# MVP Roadmap

The goal of the MVP: **say a wake word, ask a question, hear a spoken answer, all offline, on a PC first.**
Raspberry Pi porting comes after the MVP works.

Rule of thumb: get each stage working **alone** before connecting it to the next one. Commit after every working step.

---

## MVP Requirements (what "done" means)

- [ ] Captures audio from a microphone
- [ ] Detects a wake word without sending audio anywhere
- [ ] Records the user's request after the wake word and stops when they stop speaking
- [ ] Transcribes speech to text locally (Whisper)
- [ ] Generates a reply with a local LLM
- [ ] Speaks the reply with a local TTS voice (Piper)
- [ ] Runs as one continuous loop (wake -> listen -> think -> speak -> back to idle)
- [ ] Settings live in `config.json`, not hardcoded
- [ ] Works fully offline after models are downloaded
- [ ] Setup is reproducible from the README (`pip install -r requirements.txt`)

Not part of the MVP (do later): noise cancellation, custom wake words, function calling and skills (weather, music), LEDs and display, web interface, Raspberry Pi hardware.

---

## Step-by-step order

### Phase 0: Setup
1. Install Python 3.11 or 3.12, VS Code, Git.
2. Create the project folder, `.venv`, and select the interpreter in VS Code.
3. `git init`, add `.gitignore`, make the first commit.
4. Create empty files: `main.py`, `audio.py`, `wake.py`, `stt.py`, `llm.py`, `tts.py`, `config.json`.

### Phase 1: Audio in/out
5. `pip install sounddevice numpy`, run `python -m sounddevice` and note your mic and speaker indices.
6. In `audio.py`: record 5 seconds from the mic and save to a `.wav`.
7. Play that `.wav` back through the speakers.
   - Milestone: you hear your own voice.

### Phase 2: Speech to text
8. `pip install faster-whisper`.
9. In `stt.py`: transcribe the recorded `.wav` with the `tiny.en` or `base.en` model.
10. Record from the mic straight into `stt.py` and print the text.
    - Milestone: you speak, text appears.

### Phase 3: Language model
11. Install a local runtime: either Ollama (easiest) or `llama-cpp-python`.
12. Download a small quantized model (1B-3B, e.g. Llama 3.2 1B or 3B, Q4).
13. In `llm.py`: send a text prompt, get a text reply, with a short system prompt (e.g. "Answer in one or two short sentences").
    - Milestone: typed question in, answer out.

### Phase 4: Text to speech
14. `pip install piper-tts`, download one voice model (`.onnx` + `.json`).
15. In `tts.py`: turn a sentence into audio and play it.
    - Milestone: the computer speaks a text you give it.

### Phase 5: Connect the pipeline (no wake word yet)
16. In `main.py`: press Enter -> record until silence -> STT -> LLM -> TTS -> play.
17. Add simple silence detection (e.g. `webrtcvad` or an energy threshold) so recording stops automatically.
    - Milestone: a full voice conversation, triggered by a key press.

### Phase 6: Wake word
18. `pip install openwakeword`, test a built-in wake word on its own (e.g. "hey jarvis").
19. In `wake.py`: run the detector continuously on the mic stream.
20. Replace the Enter key in `main.py` with the wake word trigger.
    - Milestone: hands-free, fully local loop. **This is the MVP.**

### Phase 7: Make it solid
21. Move all settings (model names, mic index, thresholds, wake word, voice) into `config.json`.
22. Add basic error handling and logging (mic missing, model missing, empty transcript).
23. Add a short "listening" sound so you know when it heard the wake word.
24. Stream LLM output into TTS sentence by sentence to cut perceived delay.
25. Update the README with real setup steps and tick the checkboxes above.

---

## After the MVP

1. Noise suppression (RNNoise or WebRTC audio processing)
2. Conversation memory (keep the last few turns)
3. Function calling and skills (time, weather, timers, music)
4. Custom wake word
5. Port to Raspberry Pi: install on Pi OS, tune model sizes, measure latency
6. Hardware extras: mic array, LEDs, speaker, case
