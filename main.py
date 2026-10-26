from modules import checks
import time
import traceback

checks.run_checks()

from modules import audio, wake, speaker, stt, llm, debug, tts

try:
    llm.warm_up()
    print("Loading LLM...")
except Exception as e:
    print(e)

try:
    stt.warm_up()
    print("Loading STT Model...")
except Exception as e:
    print(e)

try:
    tts.warm_up("Hello im Loading")
    print("Loading TTS Model...")
except Exception as e:
    print(e)

print("Loading finished, listening for wake word...")

try:
    while True:
        try:
            wake.wait_for_wake_word()
            audio.beep()
            recording = audio.record_until_silence()
            debug.start()

            if len(recording) == 0:
                print("No speech heard")
                continue

            transcribed = stt.transcribe(recording)
            debug.milestone("transcribed")
            print("You: '", transcribed, "'")

            if not transcribed.strip():
                print("I didn't understand")
                continue

            full_response = speaker.speak_reply(transcribed)

            print("AI: '", full_response, "'")
        except Exception as e:
            print(e)
            traceback.print_exc()
            time.sleep(1)


except KeyboardInterrupt:
    print("\nBye")