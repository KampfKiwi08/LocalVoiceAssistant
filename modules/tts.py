import numpy as np
import sounddevice as sd
from piper import PiperVoice
from pathlib import Path

from modules import debug
from modules.config import cfg

VOICE_PATH = Path(__file__).resolve().parent.parent / "models" / cfg["tts"]["voice_model"]

voice = PiperVoice.load(VOICE_PATH)

def speak(text: str) -> None:
    """Turn text into speech with Piper and play it. Blocks until finished."""
    text = text.strip()
    if not text:
        return

    parts = []
    samplerate = 22050
    for chunk in voice.synthesize(text):
        samplerate = chunk.sample_rate
        parts.append(np.frombuffer(chunk.audio_int16_bytes, dtype=np.int16))

    if not parts:
        return

    audio = np.concatenate(parts)
    debug.milestone("first audio starts")
    sd.play(audio, samplerate=samplerate)
    sd.wait()

def warm_up(text_for_warm_up ="Hello"):
    """Synthesize a short text with Piper without playing it, to warm up model."""
    text = text_for_warm_up.strip()
    if not text:
        return

    for chunk in voice.synthesize(text):
        pass