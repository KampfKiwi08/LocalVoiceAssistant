import llm
import tts
import stt
import audio

try:
    while True:
        input("Press Enter and speak")
        recording = audio.record(seconds=3)
        transcribed = stt.transcribe(recording)
        print("You: ", transcribed)

        if not transcribed.strip():
            print("I didn't understand")
            continue

        response = llm.ask(transcribed)
        print("LLM: ", response)
        tts.speak(response)
except KeyboardInterrupt:
    print("\nBye")