import sounddevice as sd
import numpy as np
from modules.config import cfg


BLOCK_SIZE = 480  # samples per read: 30 ms at 16 kHz

def record(seconds) -> np.ndarray:
    recording = sd.rec(int(seconds * cfg["audio"]["sample_rate"]), samplerate=cfg["audio"]["sample_rate"], channels=1, dtype='float32', device=cfg["audio"]["device_in"])
    sd.wait()

    return recording.flatten()

def record_until_silence() -> np.ndarray:
    """Record one spoken request.

    Waits for speech to start, then stops after a pause. Returns an empty
    array if nobody starts speaking within start_timeout_seconds. Never
    records more than max_seconds of audio.
    """
    sr = cfg["audio"]["sample_rate"]
    rec = cfg["record"]
    max_silent_blocks = int(rec["silence_seconds"] * sr / BLOCK_SIZE)
    max_blocks = int(rec["max_seconds"] * sr / BLOCK_SIZE)
    start_timeout_blocks = int(rec["start_timeout_seconds"] * sr / BLOCK_SIZE)

    recording = []
    silent_blocks = 0   # consecutive quiet blocks after speech started
    waited_blocks = 0   # blocks spent waiting for speech to start
    speech_started = False

    with sd.InputStream(samplerate=sr, channels=1, dtype='float32', device=cfg["audio"]["device_in"]) as stream:
        while True:
            block, overflowed = stream.read(BLOCK_SIZE)
            rms = np.sqrt(np.mean(block ** 2))
            is_silent = rms < rec["silence_threshold"]
            print(f"{rms:.5f}", "quiet" if is_silent else "LOUD")

            if speech_started:
                recording.append(block)
                silent_blocks = silent_blocks + 1 if is_silent else 0

                if silent_blocks > max_silent_blocks:
                    del recording[len(recording) - silent_blocks:]  # trim the trailing pause
                    break
                if len(recording) >= max_blocks:  # maximum length reached
                    break
            elif not is_silent:
                speech_started = True
                recording.append(block)
            else:
                waited_blocks += 1
                if waited_blocks > start_timeout_blocks:  # nobody spoke
                    return np.zeros(0, dtype=np.float32)

    return np.concatenate(recording).flatten()

def beep(freq=cfg["beep"]["freq"], duration=cfg["beep"]["duration"], volume=cfg["beep"]["volume"]):
    t = np.linspace(0, duration, int(cfg["audio"]["sample_rate"] * duration), endpoint=False)
    tone = np.sin(2 * np.pi * freq * t)

    # short fade in/out so it doesn't click
    fade = int(cfg["audio"]["sample_rate"] * 0.01)
    tone[:fade] *= np.linspace(0, 1, fade)
    tone[-fade:] *= np.linspace(1, 0, fade)

    sd.play((tone * volume).astype(np.float32), samplerate=cfg["audio"]["sample_rate"])
    sd.wait()