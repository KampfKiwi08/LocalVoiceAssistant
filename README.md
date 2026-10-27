# Local Voice Assistant

### A privacy-first voice assistant that runs on your own hardware, built on a PC first and designed to run on a Raspberry Pi

![Status](https://img.shields.io/badge/status-early%20development-orange)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![Core](https://img.shields.io/badge/core-runs%20offline-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

> **Status:** The core voice loop works: wake word, speech to text, local LLM, spoken reply (streamed sentence by sentence). The **skill layer** (tool calling, Home Assistant, weather, ...) is in development. See [ROADMAP.md](ROADMAP.md) for the plan and progress.

---

## Overview

A voice assistant that listens for a wake word, understands what you say, thinks with a local language model, and answers out loud. **The core pipeline runs entirely on your own device.** No cloud, no accounts, no audio leaving your machine.

What the assistant can *do* beyond talking comes from **skills**: small add-ons that give the language model tools, for example "tell the time", "get the weather" or "turn on the living room light through Home Assistant". Every skill lives in **its own Git repository**, so you install only what you want. A skill that needs the internet says so up front (see [Skills](#skills)).

The project is developed on a regular PC and designed so it can later move to a Raspberry Pi with little change, which is why it favors small, quantized models and cross-platform libraries.

## Why this project

Commercial smart speakers send your voice to the cloud, work in closed ecosystems, and handle only simple commands. This project aims to be:

| Private | Smart | Customizable | Open |
|---|---|---|---|
| Voice never leaves your device | Local LLM understands natural phrasing and can use tools | Swap models, voices, wake words and skills | Every line is readable and changeable |

## Pipeline

```
Voice Input -> Wake Word -> Whisper STT -> LLM <-> Skills (tools) -> Piper TTS -> Audio Output
```

| Stage | Tool | Purpose |
|---|---|---|
| Audio capture and playback | `sounddevice` | Microphone input and speaker output |
| Noise cancellation (later) | RNNoise / WebRTC | Clean up the microphone signal |
| Wake word | `openWakeWord` | Always-on, lightweight trigger |
| Speech to text | `faster-whisper` | Transcribe what you said |
| Language model | Ollama (`llama.cpp` underneath) | Understand the request and write the reply |
| Skills (tool calling) | Ollama tool calling + skill repos | Let the model act: time, weather, Home Assistant, ... |
| Text to speech | `Piper` | Speak the reply naturally |

### How skills fit in

```
you speak
    |
Whisper turns it into text
    |
LLM receives: your text + the tools of all enabled skills
    |
    +---------------------------+
    |                           |
plain answer              tool call (name + arguments)
    |                           |
    |                     the skill runs and returns a short result
    |                           |
    |                     LLM turns the result into a sentence
    +---------------------------+
    |
Piper speaks it (streamed sentence by sentence)
```

The model only *chooses* a tool and its arguments. The actual work happens in plain Python inside the skill, which can check, limit or refuse the action.

## Features

**Working now**
- Wake word detection (openWakeWord)
- Local speech recognition (faster-whisper)
- Local LLM replies through Ollama, streamed sentence by sentence into the voice
- Local neural voice (Piper)
- A short beep when the wake word was heard
- Single config file for all settings
- Startup checks with clear messages (config, voice files, audio devices, Ollama)
- Model warm-up at startup, so the first question is not slower than the rest
- Conversation memory: remembers the last few turns and forgets after a pause (kept in RAM only, never written to disk)
- Optional timing output to find out where the time goes

**In development: the skill layer**
- Tool calling in the LLM loop
- A skill loader and a documented skill format
- Skills, each in its own repository: time, Home Assistant, weather, and more

**Planned after that**
- Noise suppression
- Custom wake words
- Raspberry Pi port, then optional hardware (mic array, LEDs, speaker)

## Getting started

### Requirements
- Python 3.12 or newer (developed on 3.14)
- A working microphone and speakers
- [Ollama](https://ollama.com) installed and running
- Git
- A few GB of disk space for models

### Installation

```bash
# Clone the repository
git clone https://github.com/KampfKiwi08/LocalVoiceAssistant.git
cd LocalVoiceAssistant

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

Models are not stored in the repository.

1. **Whisper**: downloaded automatically by `faster-whisper` on first run (the model is set in `config.json`, for example `small.en`).
2. **LLM**: pull a small model with Ollama, for example `ollama pull llama3.2:3b`. The name must match `llm.model` in `config.json`.
3. **Piper voice**: put one `.onnx` voice file and its `.onnx.json` config into the `models/` folder, and set `tts.voice_model` to the file name.

### Configuration

Everything is set in `config.json`:

| Section | What it controls |
|---|---|
| `audio` | Input and output device numbers (find them with `python -m sounddevice`), sample rate, input gain |
| `wake` | Wake word model and detection threshold |
| `record` | Silence detection, maximum length of a request, start timeout |
| `stt` | Whisper model and beam size |
| `llm` | Ollama model, reply length limit, system prompt, how long the model stays loaded (`keep_alive`), conversation memory (`memory_turns`: how many question-and-answer pairs to remember, `memory_timeout_seconds`: forget after this much silence) |
| `tts` | Piper voice file |
| `beep` | The sound played after the wake word |
| `debug` | `timings`: print how long each stage takes (optional) |

### Run

```bash
python main.py
```

On start, the assistant checks its configuration and prints every problem it finds (wrong device number, missing voice file, Ollama not running, ...) instead of crashing with a long error. After the warm-up it prints that it is ready, and you can say the wake word.

## Skills

The core assistant listens, thinks and speaks. Everything it can *do* comes from skills.

**Principles**
- **One repository per skill.** Choose exactly what your assistant can do.
- **Installed is not enabled.** A skill only runs if you list it in `config.json`.
- **Honest about the network.** Each skill declares in its manifest whether it needs the internet or other services. The core stays offline either way.
- **The skill, not the model, has the last word.** Skills validate arguments and can refuse or ask for confirmation.

> **Security:** a skill is Python code that runs with the same permissions as the assistant. Only install skills whose code you have read or whose author you trust.

### Installing a skill (planned format)

```bash
cd skills
git clone https://github.com/<author>/<skill-repository> <skill-name>
pip install -r <skill-name>/requirements.txt   # only if the skill has one
```

Then enable it in `config.json`:

```json
"skills": {
  "enabled": ["time", "homeassistant"]
}
```

At the next start, the startup checks verify that each enabled skill is complete (its settings are present, its services are reachable).

### What a skill repository contains (sketch)

```
my-skill/
├── skill.json         # manifest: name, version, description, needs (network, settings, environment variables)
├── skill.py           # the tools: name, description, parameters, and the function that runs
├── requirements.txt   # optional extra Python dependencies
└── README.md          # what it does, how to configure it, what it is allowed to touch
```

The exact format is still being designed. It will be documented in `SKILLS.md` once the first skill works. Proposed repository naming: `LocalVoiceAssistant-skill-<name>`.

### Planned skills

| Skill | What it does | Network |
|---|---|---|
| `time` | Current time and date | No |
| `homeassistant` | Control and query your home (see below) | Your own Home Assistant, on your network |
| `weather` | Current weather and forecast | Yes (or through Home Assistant) |
| `timers` | Timers and reminders | No |

### Home Assistant skill

The main goal of the skill layer. It talks to your own Home Assistant instance through its API and is meant to cover much more than switches:

- Lights (on/off, brightness, color, color temperature)
- Switches and fans
- Climate (temperature, mode)
- Covers (blinds, shutters, garage doors)
- Media players (play, pause, volume)
- Scenes and scripts
- Reading sensor values ("how warm is it in the bedroom?")

Safety rules for this skill:
- The access token is **never** stored in the repository. It is read from an environment variable or a git-ignored secrets file.
- Only entities you list in an **allowlist** can be controlled, using the spoken names and areas you choose.
- Sensitive domains (locks, alarms, garage doors) are **off by default** and, once enabled, ask for a spoken confirmation first.
- Every executed action is logged together with what the assistant heard.

## Project structure

```
.
├── main.py             # Connects all stages into one loop
├── config.json         # Settings (models, devices, thresholds, enabled skills)
├── requirements.txt    # Python dependencies
├── modules/
│   ├── audio.py        # Microphone capture, silence detection, beep
│   ├── checks.py       # Startup checks with clear messages
│   ├── config.py       # Loads config.json
│   ├── debug.py        # Optional timing output
│   ├── llm.py          # Language model (Ollama), streamed replies
│   ├── speaker.py      # Speaks the reply while it is still being generated
│   ├── stt.py          # Speech to text (Whisper)
│   ├── tts.py          # Text to speech (Piper)
│   ├── wake.py         # Wake word detection
│   └── skills.py       # (planned) loads skills and runs tool calls
├── skills/             # (planned) installed skills, one folder and one repo each, not tracked by this repo
├── models/             # Piper voices (not tracked)
├── ROADMAP.md          # Checklist and build order
└── README.md
```

## Roadmap

The full build order is in [ROADMAP.md](ROADMAP.md). Short version:

- [x] Phase 0 to 6: Setup, audio, speech to text, LLM, text to speech, pipeline, wake word (**MVP complete**)
- [x] Phase 7: Config, error handling, startup checks, streaming, warm-up, timing
- [ ] Phase 8: Skill layer (conversation memory is done; tool calling and the skill loader are next)
- [ ] Phase 9: Home Assistant skill
- [ ] Phase 10: More skills (weather, timers, ...)
- [ ] Later: noise cancellation, custom wake word, Raspberry Pi port

## Design goals

- **Offline-first core**: speech recognition, language model and voice need no network after setup. Skills declare when they do.
- **Modular**: skills are separate repositories. Install only what you need.
- **Small models**: everything should be able to run on a Raspberry Pi 4/5
- **Simple code**: one small module per pipeline stage
- **Configurable**: behavior changes through `config.json`, not code edits
- **Safe by default**: skills can only do what they declare, and risky actions need confirmation

## Contributing

Ideas, issues and pull requests are welcome. Please open an issue first for larger changes. Once the skill format is documented, new skills are welcome as their own repositories.

## License

MIT License. See `LICENSE` for details.

## Acknowledgements

- [OpenAI Whisper](https://github.com/openai/whisper) and [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- [llama.cpp](https://github.com/ggerganov/llama.cpp) and [Ollama](https://ollama.com)
- [Piper TTS](https://github.com/rhasspy/piper)
- [openWakeWord](https://github.com/dscripka/openWakeWord)
- [Home Assistant](https://www.home-assistant.io)