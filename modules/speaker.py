import threading
from queue import Queue
from modules import llm, tts


def speak_reply(transcribed: str) -> str:
    full_response = ""

    response_queue = Queue()
    speaker_thread = threading.Thread(target=speak_sentence,args=(response_queue,), daemon=True)
    speaker_thread.start()

    try:
        for sentence in llm.ask_stream(transcribed):
            response_queue.put(sentence)
            full_response = full_response + sentence + " "
    finally:
        response_queue.put(None)

    speaker_thread.join()

    return full_response.strip()
def speak_sentence(sentence_queue: Queue):
    while True:
        sentence = sentence_queue.get()
        if sentence is None:
            break

        try:
            tts.speak(sentence)
        except Exception as e:
            print(e)

