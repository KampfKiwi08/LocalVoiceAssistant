import llm
import tts
import stt
import wake
import audio

try:
    while True:
        wake.wait_for_wake_word()
        audio.beep(volume=1)
        recording = audio.record_until_silence()
        transcribed = stt.transcribe(recording)
        print("You: '", transcribed, "'")

        if not transcribed.strip():
            print("I didn't understand")
            continue

        response = llm.ask(transcribed)
        print("LLM: '", response, "'")
        tts.speak(response)
except KeyboardInterrupt:
    print("\nBye")