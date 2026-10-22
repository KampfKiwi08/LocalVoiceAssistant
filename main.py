from modules import audio, wake, llm, tts, stt

try:
    while True:
        wake.wait_for_wake_word()
        audio.beep()
        recording = audio.record_until_silence()

        if len(recording) == 0:
            print("No speech heard")
            continue

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