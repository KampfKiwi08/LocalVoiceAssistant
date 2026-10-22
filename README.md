# Local Voice Assistant

### An offline, privacy-first voice assistant, built on a PC first and designed to run on a Raspberry Pi

![Status](https://img.shields.io/badge/status-early%20development-orange)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Offline](https://img.shields.io/badge/runs-100%25%20offline-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

> **Status:** Early development. Nothing here is finished yet. See [ROADMAP.md](ROADMAP.md) for the current plan and progress.

---

## Overview

A voice assistant that listens for a wake word, understands what you say, thinks with a local language model, and answers out loud. **All processing happens on your own device.** No cloud, no accounts, no audio leaving your machine.

The project is developed on a regular PC and designed so it can later move to a Raspberry Pi with little change, which is why it favors small, quantized models and cross-platform libraries.

## Why this project

Commercial smart speakers send your voice to the cloud, work in closed ecosystems, and handle only simple commands. This project aims to be:

| Private | Smart | Customizable | Open |
|---|---|---|---|
| Voice never leaves your device | Local LLM understands natural phrasing | Swap models, voices, wake words | Every line is readable and changeable |

## Pipeline

```
Voice Input -> Noise Cancellation -> Wake Word -> Whisper STT -> LLaMA -> Piper TTS -> Audio Output
```

| Stage | Tool | Purpose |
|---|---|---|
| Audio capture and playback | `sounddevice` | Microphone input and speaker output |
| Noise cancellation (later) | RNNoise / WebRTC | Clean up the microphone signal |
| Wake word | `openWakeWord` | Always-on, lightweight trigger |
| Speech to text | `faster-whisper` | Transcribe what you said |
| Language model | `llama.cpp` / Ollama | Generate the reply |
| Text to speech | `Piper` | Speak the reply naturally |

## Features

**Planned for the MVP**
- Wake word detection
- Local speech recognition (Whisper `tiny.en` / `base.en`)
- Local LLM replies (1B-3B quantized model)
- Local neural voice (Piper)
- Single config file for all settings

**Planned after the MVP**
- Noise suppression
- Conversation memory
- Skills via function calling (time, weather, timers, music)
- Custom wake words
- Raspberry Pi port, then optional hardware (mic array, LEDs, speaker)

## Getting started

### Requirements
- Python 3.11 or 3.12
- A working microphone and speakers
- Git
- A few GB of disk space for models

### Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

# Create and activate a virtual environment
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Linux / macOS
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Models

Models are not stored in the repository. Download them into the `models/` folder:

1. **Whisper**: downloaded automatically by `faster-whisper` on first run (`tiny.en` or `base.en`).
2. **LLM**: a small quantized model (e.g. Llama 3.2 1B or 3B, Q4) via Ollama or as a `.gguf` file.
3. **Piper voice**: one `.onnx` voice file and its `.json` config.

### Run

```bash
python main.py
```

> Not functional yet. This section will be updated as the MVP comes together.

## Project structure

```
.
├── main.py            # Connects all stages into one loop
├── audio.py           # Microphone capture and playback
├── wake.py            # Wake word detection
├── stt.py             # Speech to text (Whisper)
├── llm.py             # Language model replies
├── tts.py             # Text to speech (Piper)
├── config.json        # Settings (models, devices, thresholds)
├── requirements.txt   # Python dependencies
├── ROADMAP.md         # MVP checklist and build order
└── README.md
```

## Roadmap

The full build order is in [ROADMAP.md](ROADMAP.md). Short version:

- [x] Phase 0: Project setup
- [x] Phase 1: Audio in and out
- [x] Phase 2: Speech to text
- [x] Phase 3: Local language model
- [x] Phase 4: Text to speech
- [ ] Phase 5: Connect the pipeline (push-to-talk)
- [ ] Phase 6: Wake word (**MVP complete**)
- [ ] Phase 7: Config, error handling, streaming
- [ ] Later: noise cancellation, skills, Raspberry Pi port

## Design goals

- **Offline first**: no network needed after setup
- **Small models**: everything should be able to run on a Raspberry Pi 4/5
- **Simple code**: one small module per pipeline stage
- **Configurable**: behavior changes through `config.json`, not code edits

## Contributing

Ideas, issues and pull requests are welcome. Please open an issue first for larger changes.

## License

MIT License. See `LICENSE` for details.

## Acknowledgements

- [OpenAI Whisper](https://github.com/openai/whisper) and [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- [llama.cpp](https://github.com/ggerganov/llama.cpp) and [Ollama](https://ollama.com)
- [Piper TTS](https://github.com/rhasspy/piper)
- [openWakeWord](https://github.com/dscripka/openWakeWord)
