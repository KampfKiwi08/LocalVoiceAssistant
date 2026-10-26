import sys
from pathlib import Path
import sounddevice as sd
import ollama

from modules.config import cfg

REQUIRED_CONFIG = {
    "audio" : ["device_in", "device_out", "samplerate", "input_gain"],
    "wake" : ["model", "threshold"],
    "record" : ["silence_threshold", "silence_seconds", "max_seconds", "start_timeout_seconds", "min_speech_seconds"],
    "stt" : ["model", "beam_size"],
    "llm" : ["model", "max_tokens", "system_prompt", "keep_alive"],
    "tts" : ["voice_model"],
    "beep": ["freq", "duration", "volume"]
}

def run_checks():
    problems = []
    problems += check_config()
    problems += check_files()
    problems += check_audio()
    problems += check_ollama()

    if not problems:
        print("No problems found")
    else:
        print("Found " + str(len(problems)) + " problems")
        for problem in problems:
            print(problem)
        sys.exit(1)


def check_config():
    problems = []
    for section_name in REQUIRED_CONFIG:
        if section_name not in cfg.keys():
            problems.append("config.json is missing section '" + section_name + "'")
            continue
        for key in REQUIRED_CONFIG[section_name]:
            if key not in cfg[section_name]:
                problems.append("config.json is missing " + section_name + "." + key)
    return problems

def check_files():
    problems = []
    file_path_model = Path(__file__).resolve().parent.parent / "models" / cfg["tts"]["voice_model"]
    file_path_config = Path(str(file_path_model) + ".json")
    if not file_path_model.exists():
        problems.append("Piper voice file not found <" + str(file_path_model) + ">")
    else:
        if file_path_model.stat().st_size <= 0:
            problems.append("Piper voice file too small/Invalid. This might be caused by a failed download <" + str(file_path_model) + ">")


    if not file_path_config.exists():
        problems.append("Piper config file not found <" + str(file_path_config) + ">")
    else:
        if file_path_config.stat().st_size <= 0:
            problems.append("Piper config file too small/Invalid. This might be caused by a failed download <" + str(file_path_config) + ">")

    return problems

def check_audio():
    problems = []
    problems += check_device("input", cfg["audio"]["device_in"], [cfg["audio"]["samplerate"]])
    problems += check_device("output", cfg["audio"]["device_out"], [cfg["audio"]["samplerate"], 22050]) #22050 is Piper's sample rate
    return problems

def check_device(device_type:str, device_number:int, samplerates):
    problems = []
    try:
        device = sd.query_devices(device_number)
    except Exception as e:
        problems.append(device_type + " device not found <" + str(
            device_number) + ">, run python -m sounddevice to see the list. \n" + str(e))
        return problems

    device_name = str(device_number) + " | " + str(device["name"])

    if device[f"max_{device_type}_channels"] == 0:
        action = "record" if device_type == "input" else "play audio"
        problems.append(f"Device <{device_name}> can't {action}, because it's not an {device_type} device")
        return problems

    for rate in samplerates:
        if device_type == "input":
            try:
                sd.check_input_settings(device_number, channels=1, samplerate=rate)
            except Exception as e:
                problems.append(f"Recording device <{device_name}> does not support specified sample rate " + str(
                    rate) + ". \n" + str(e))
        else:
            try:
                sd.check_output_settings(device_number, samplerate=rate)
            except Exception as e:
                problems.append(f"Output device <{device_name}> does not support specified sample rate " + str(
                    rate) + ". \n" + str(e))

    return problems

def check_ollama():
    problems = []
    try:
        ollama_infos = ollama.list()
    except Exception as e:
        problems.append("Ollama is not running or not reachable. Start it, then try again. \n" + str(e))
        return problems

    installed_models = []
    for entry in ollama_infos.models:
        model_name = entry.model
        if ":" not in model_name:
            model_name += ":latest"
        installed_models.append(model_name)

    configured_model = str(cfg["llm"]["model"])
    if ":" not in configured_model:
        configured_model += ":latest"

    if configured_model not in installed_models:
        problems.append(f"Model {configured_model} is not installed. Run <ollama pull {configured_model}> to install it. Installed {installed_models}")

    return problems








