import sounddevice as sd
import numpy as np

fs = 16000
device_in = 1
device_out = 10


def record(seconds) -> np.ndarray:
    recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='float32', device=device_in)
    sd.wait()

    return recording.flatten()
