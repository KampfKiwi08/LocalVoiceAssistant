# Roadmap

**Stage 1 (MVP, done):** say a wake word, ask a question, hear a spoken answer, all offline, on a PC.

**Stage 2 (now):** the assistant can *do* things, not just talk. It tells the time, answers with live data and controls the home through Home Assistant, using **skills that each live in their own repository**.

**Stage 3 (later):** noise suppression, custom wake word, Raspberry Pi port.

Rule of thumb: get each stage working **alone** before connecting it to the next one. Commit after every working step.

---

## MVP Requirements (done)

- [x] Captures audio from a microphone
- [x] Detects a wake word without sending audio anywhere
- [x] Records the user's request after the wake word and stops when they stop speaking
- [x] Transcribes speech to text locally (Whisper)
- [x] Generates a reply with a local LLM
- [x] Speaks the reply with a local TTS voice (Piper)
- [x] Runs as one continuous loop (wake -> listen -> think -> speak -> back to idle)
- [x] Settings live in `config.json`, not hardcoded
- [x] The core pipeline works fully offline after models are downloaded
- [ ] Setup is reproducible from the README (`requirements.txt` is still a full `pip freeze` and needs cleaning up)

---

## Stage 1: Phases 0 to 7

### Phases 0 to 6 (done)
Setup, audio in and out, speech to text, local language model, text to speech, connecting the pipeline, wake word. Milestone reached: hands-free, fully local loop.

### Phase 7: Make it solid
- [x] 21. Move all settings into `config.json`
- [x] 22. Error handling: the main loop survives errors, empty transcripts are handled, startup checks report problems clearly (config, voice files, audio devices, Ollama)
- [ ] 22b. Replace `print` calls with the `logging` module
- [x] 23. Short beep so you know the wake word was heard
- [x] 24. Stream LLM output into TTS sentence by sentence
- [x] 25. Update the README
- [x] Warm-up of Whisper, Piper and the LLM at startup
- [x] Timing output behind a debug flag, including Ollama statistics
- [x] Output device taken from the config
- [x] Recording tuned (`max_seconds`, `silence_seconds`)

---

## Stage 2: Skills and tool calling

### Design decisions (so far)

- **Tool calling.** The LLM gets a list of tools (name, description, parameters). If it wants one, the reply contains a tool call instead of text. The code runs the tool, hands the result back, and the model writes the final answer. The first pass is not streamed (nothing is spoken yet), only the final answer is streamed into the voice.
- **One repository per skill.** Users choose what their assistant can do.
- **Skills are folders in `skills/`.** Cloned from their repository, listed in `config.json` under `skills.enabled`. Installed does not mean enabled.
- **Manifest.** Each skill has a `skill.json` describing it: name, version, description, and what it needs (network, settings, environment variables). This lets the loader and the startup checks verify a skill before using it.
- **Honest about the network.** The core stays offline. A skill that needs the internet or another service says so in its manifest, and the README lists it.
- **The skill has the last word.** Models make mistakes: wrong tool, wrong arguments, invented names. Skills validate every argument, use allowlists, and can refuse or ask for a spoken confirmation.
- **Secrets stay out of Git.** Tokens come from environment variables or a git-ignored secrets file, never from `config.json`.
- **Possible later:** packaging skills as pip packages with entry points. Folders are simpler to start with.

### Phase 8: Skill layer (core)

- [x] 26. **Conversation memory.** Keeps the last few turns (`memory_turns`), forgets after `memory_timeout_seconds` of silence, kept in RAM only. Needed for follow-ups like "and in the kitchen?".
- [ ] 27. **Tool-calling loop with one built-in tool.** Add `get_time` directly inside the project to learn how Ollama's tool calls work: send the tools, detect a tool call, run it, return the result, stream the final answer. Limit the number of rounds, and handle unknown tools, bad arguments and errors by returning a short error text to the model. Decide what goes into the conversation memory for tool turns (suggestion: only the final question and answer, not the tool messages).
    - Milestone: "What time is it?" is answered from the real clock.
- [ ] 28. **Test phrase list.** About 30 phrases with the expected tool call (and phrases that must *not* trigger a tool). Run it whenever the model or the prompt changes, and write down the accuracy. Try other small models that support tools.
- [ ] 29. **Define the skill format.** Manifest fields, how a skill declares its tools, how it receives its settings, how it reports problems to the startup checks. Write it down in `SKILLS.md`.
- [ ] 30. **Skill loader (`modules/skills.py`).** Scan `skills/`, read manifests, load only enabled skills, collect their tools, detect duplicate tool names, give each skill its settings. Add the skill checks to the startup checks.
- [ ] 31. **Move `get_time` into its own repository** (`LocalVoiceAssistant-skill-time`) and load it through the loader.
    - Milestone: the assistant gets a new ability by cloning a repo and adding one line to the config.
- [ ] 32. **Skill template repository** with the manifest, an example tool, a test and a README, so anyone can start a new skill.
- [ ] 33. **Timing for tool turns.** Add milestones for "tool call received" and "tool finished" to the debug output.
- [ ] 34. **Optional router for trivial requests** (time, date) that skips the model entirely, if tool turns turn out to be too slow, especially on the Pi.

### Phase 9: Home Assistant skill (own repository)

- [ ] 35. **Connection.** Base URL and token from the environment or a secrets file. Startup check: Home Assistant is reachable and the token works.
- [ ] 36. **Read-only first.** A tool to read the state of an allowlisted entity ("how warm is it in the bedroom?").
- [ ] 37. **Allowlist file.** Which entities can be used, with spoken names, aliases and areas. Only these names are shown to the model. Start with a handful of entities.
- [ ] 38. **Control tools, domain by domain**, testing each before the next:
    - [ ] lights (on/off, brightness, color, color temperature)
    - [ ] switches and fans
    - [ ] climate (temperature, mode)
    - [ ] covers (blinds, shutters)
    - [ ] media players (play, pause, volume)
    - [ ] scenes and scripts
- [ ] 39. **Argument validation.** Unknown names, out-of-range values and domains that do not match the action are rejected with a short, speakable error.
- [ ] 40. **Sensitive domains** (locks, alarms, garage doors): disabled by default. When enabled, require a spoken confirmation before acting.
- [ ] 41. **Action log.** Record every executed action with the transcript that caused it.
- [ ] 42. **Test phrases for the home** added to the phrase list, including ambiguous and dangerous ones that must be refused or confirmed.

### Phase 10: More skills (each its own repository)

- [ ] Weather (declares that it needs the network, or reads a Home Assistant weather entity)
- [ ] Timers and reminders
- [ ] Music or media control beyond Home Assistant
- [ ] Anything else the community writes

---

## Stage 3: Later

1. Noise suppression (RNNoise or WebRTC audio processing)
2. Custom wake word
3. Port to Raspberry Pi
   - smaller models (`base.en` or `tiny.en` for Whisper, a 1B LLM, a lighter Piper voice)
   - choose audio devices by name instead of by number
   - a cleaned and pinned `requirements.txt`
   - run as a `systemd` service with restart on failure
   - cooling for sustained load
   - measure latency with the timing output and recheck tool-calling accuracy with the smaller model
4. Hardware extras: mic array, LEDs, speaker, case

## Housekeeping

- [ ] Add the `LICENSE` file mentioned in the README
- [ ] Clean up `requirements.txt` (direct dependencies only, Pi-specific ones separate)
- [ ] `SKILLS.md` once the skill format is stable