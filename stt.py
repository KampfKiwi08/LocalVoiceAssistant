import numpy as np
from faster_whisper import WhisperModel

model = WhisperModel("small.en", device="cpu", compute_type="int8")

def transcribe(audio: np.ndarray) -> str:
    # audio: float32 mono, 16 kHz, values between -1 and 1
    segments, _ = model.transcribe(audio, beam_size=1, vad_filter=True)
    return " ".join(s.text.strip() for s in segments)