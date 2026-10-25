from modules import audio, wake, speaker, stt


try:
    while True:
        wake.wait_for_wake_word()
        recording = audio.record_until_silence()

        if len(recording) == 0:
            print("No speech heard")
            continue

        transcribed = stt.transcribe(recording)
        print("You: '", transcribed, "'")

        if not transcribed.strip():
            print("I didn't understand")
            continue

        full_response = speaker.speak_reply(transcribed)

        print("AI: '", full_response, "'")

except KeyboardInterrupt:
    print("\nBye")