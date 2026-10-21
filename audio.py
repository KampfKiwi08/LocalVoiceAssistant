import sounddevice as sd
from stt import transcribe

fs = 16000
duration = 3  # seconds

print("Recording...")
myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
sd.wait()

text = transcribe(myrecording)
print(repr(text))   # shows '' if empty, so you can tell blank from nothing