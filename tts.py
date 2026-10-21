import numpy as np
import sounddevice as sd
from piper import PiperVoice

VOICE_PATH = "models/en_US-lessac-medium.onnx"

voice = PiperVoice.load(VOICE_PATH)


def speak(text: str) -> None:
    """Turn text into speech with Piper and play it. Blocks until finished."""
    text = text.strip()
    if not text:
        return

    parts = []
    sample_rate = 22050
    for chunk in voice.synthesize(text):
        sample_rate = chunk.sample_rate
        parts.append(np.frombuffer(chunk.audio_int16_bytes, dtype=np.int16))

    if not parts:
        return

    audio = np.concatenate(parts)
    sd.play(audio, samplerate=sample_rate)
    sd.wait()