import numpy as np
from faster_whisper import WhisperModel
from modules.config import cfg

MODEL = WhisperModel(cfg["stt"]["model"], device="cpu", compute_type="int8")

def transcribe(audio: np.ndarray) -> str:
    audio = np.asarray(audio, dtype=np.float32).flatten()
    segments, _ = MODEL.transcribe(audio, beam_size=cfg["stt"]["beam_size"], vad_filter=True)
    return " ".join(s.text.strip() for s in segments)