import sounddevice as sd
import numpy as np

FS = 16000
DEVICE_IN = 1
DEVICE_OUT = 10

STREAM_SAMPLERATE = 480

SILENCE_THRESHOLD = 0.00003
SILENCE_LENGTH_THRESHOLD = 0.5 #seconds

MAX_DURATION = 15 #seconds


def record(seconds) -> np.ndarray:
    recording = sd.rec(int(seconds * FS), samplerate=FS, channels=1, dtype='float32', device=DEVICE_IN)
    sd.wait()

    return recording.flatten()

def record_until_silence() -> np.ndarray:
    recording = []
    silent_blocks = 0
    speech_started = False
    max_silent_blocks = FS / STREAM_SAMPLERATE * SILENCE_LENGTH_THRESHOLD

    with sd.InputStream(samplerate=FS, channels=1, dtype='float32', device=DEVICE_IN) as stream:
        while True:
            block, overflowed = stream.read(STREAM_SAMPLERATE)
            if np.sqrt(np.mean(block ** 2)) < SILENCE_THRESHOLD:
                if speech_started:
                    silent_blocks += 1
                    recording.append(block)
            else:
                speech_started = True
                silent_blocks = 0
                recording.append(block)

            if speech_started and silent_blocks > max_silent_blocks:
                del recording[len(recording) - silent_blocks:]
                break

    return np.concatenate(recording).flatten()

def beep(freq=880, duration=0.15, volume=0.3):
    t = np.linspace(0, duration, int(FS * duration), endpoint=False)
    tone = np.sin(2 * np.pi * freq * t)

    # short fade in/out so it doesn't click
    fade = int(FS * 0.01)
    tone[:fade] *= np.linspace(0, 1, fade)
    tone[-fade:] *= np.linspace(1, 0, fade)

    sd.play((tone * volume).astype(np.float32), samplerate=FS)
    sd.wait()
