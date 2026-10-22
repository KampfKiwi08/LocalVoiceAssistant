import sounddevice as sd
import numpy as np

fs = 16000
device_in = 1
device_out = 10

stream_samplerate = 480

silence_threshold = 0.00003
silence_length_threshold = 0.5 #seconds

max_duration = 15 #seconds


def record(seconds) -> np.ndarray:
    recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='float32', device=device_in)
    sd.wait()

    return recording.flatten()

def record_until_silence() -> np.ndarray:
    recording = []
    silent_blocks = 0
    speech_started = False
    max_silent_blocks = fs / stream_samplerate * silence_length_threshold

    with sd.InputStream(samplerate=fs, channels=1, dtype='float32', device=device_in) as stream:
        while True:
            block, overflowed = stream.read(stream_samplerate)
            if np.sqrt(np.mean(block ** 2)) < silence_threshold:
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
