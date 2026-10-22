import openwakeword
import sounddevice as sd
import numpy as np
from modules.config import cfg


model = openwakeword.Model(wakeword_models=[cfg["wake"]["model"]], inference_framework="onnx")

def wait_for_wake_word():
    stream = sd.InputStream(samplerate=16000, channels=1, dtype="int16", blocksize=1280, device=cfg["audio"]["device_in"])

    with stream:
        while True:
            block, overflowed = stream.read(1280)
            block = block.flatten()
            block = np.clip(block.astype(np.float32) * cfg["audio"]["input_gain"], -32768, 32767).astype(np.int16)
            if model.predict(block)[cfg["wake"]["model"]] > cfg["wake"]["threshold"]:
                model.reset()
                print("Wake Word Detected!")
                return


if __name__ == "__main__":
    wait_for_wake_word()