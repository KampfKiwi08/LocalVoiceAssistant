import openwakeword
import sounddevice as sd
import numpy as np


THRESHOLD = 0.1
WAKE_WORD_NAME = "hey_jarvis"
DEVICE_IN = 1
INPUT_GAIN = 3.0  # tune this


model = openwakeword.Model(wakeword_models=[WAKE_WORD_NAME], inference_framework="onnx")

def wait_for_wake_word():
    stream = sd.InputStream(samplerate=16000, channels=1, dtype="int16", blocksize=1280, device=DEVICE_IN)

    with stream:
        while True:
            block, overflowed = stream.read(1280)
            block = block.flatten()
            block = np.clip(block.astype(np.float32) * INPUT_GAIN, -32768, 32767).astype(np.int16)
            if model.predict(block)[WAKE_WORD_NAME] > THRESHOLD:
                model.reset()
                print("Wake Word Detected!")
                return


if __name__ == "__main__":
    wait_for_wake_word()