import sounddevice as sd
import numpy as np
from modules.config import cfg


BLOCK_SIZE = 480  # samples per read: 30 ms at 16 kHz

sd.default.device = cfg["audio"]["device_in"], cfg["audio"]["device_out"]


def record(seconds) -> np.ndarray:
    recording = sd.rec(int(seconds * cfg["audio"]["sample_rate"]), samplerate=cfg["audio"]["sample_rate"], channels=1, dtype='float32')
    sd.wait()

    return recording.flatten()

def record_until_silence() -> np.ndarray:
    """Record one spoken request.

    Waits for speech to start, then stops after a pause. Sounds shorter than
    min_speech_seconds (clicks, echoes, the tail of the wake word) are
    discarded and listening continues. Returns an empty array if nobody
    speaks within start_timeout_seconds. Never records more than
    max_seconds of audio.
    """
    sample_rate = cfg["audio"]["sample_rate"]
    recording_config = cfg["record"]
    max_silent_blocks = max(1, int(recording_config["silence_seconds"] * sample_rate / BLOCK_SIZE))
    max_blocks = int(recording_config["max_seconds"] * sample_rate / BLOCK_SIZE)
    max_start_timeout_blocks = int(recording_config["start_timeout_seconds"] * sample_rate / BLOCK_SIZE)
    min_speech_blocks = int(recording_config["min_speech_seconds"] * sample_rate / BLOCK_SIZE)

    recording = []
    silent_blocks = 0   # consecutive quiet blocks after speech started
    start_timeout_blocks = 0 # counter for the start timeout
    speech_started = False

    with sd.InputStream(samplerate=sample_rate, channels=1, dtype='float32') as stream:
        while True:
            block, overflowed = stream.read(BLOCK_SIZE)
            is_silent = np.sqrt(np.mean(block ** 2)) < recording_config["silence_threshold"]

            if speech_started:
                recording.append(block)
                if is_silent:
                    silent_blocks += 1
                else:
                    silent_blocks = 0

                if silent_blocks >= max_silent_blocks:
                    speech_len = len(recording) - silent_blocks

                    #discard any speach shorter than min_speech_blocks and reset
                    if speech_len < min_speech_blocks:
                        recording.clear()
                        speech_started = False
                        silent_blocks = 0
                        continue

                    del recording[-silent_blocks:]
                    break

                if len(recording) >= max_blocks:
                    break

            else:
                start_timeout_blocks += 1
                if not is_silent:
                    silent_blocks = 0
                    speech_started = True
                    recording.append(block)

                if start_timeout_blocks >= max_start_timeout_blocks:
                    return np.array([], dtype='float32')


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