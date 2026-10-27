import re
import time

import ollama

from modules import debug
from modules.config import cfg

chat_history = []
time_since_last_interaction = None


def ask_stream(prompt: str):
    """Send one text prompt to the local LLM and yield each sentence."""
    global time_since_last_interaction
    full_response = ""
    current_sentence = ""

    if time_since_last_interaction is not None and time.monotonic() - time_since_last_interaction > cfg["llm"]["memory_timeout_seconds"]:
        chat_history.clear()


    response = ollama.chat(
        model=cfg["llm"]["model"],
        messages=[
            {"role": "system", "content": cfg["llm"]["system_prompt"]},
            *chat_history,
            {"role": "user", "content": prompt},
        ],
        options={"num_predict": cfg["llm"]["max_tokens"]},  # hard cap on reply length (in tokens)
        keep_alive=cfg["llm"]["keep_alive"],
        stream=True
    )
    for streamChunk in response:

        current_sentence += streamChunk['message']['content']
        full_response += streamChunk['message']['content']

        while re.search(r"[.!?]\s", current_sentence):
            sentence_end = re.search(r"[.!?]\s", current_sentence).end()
            yield current_sentence[0:sentence_end].strip()

            current_sentence = current_sentence[sentence_end:]
        if streamChunk.get('done'):
            #Debug Ollama statistics
            load_time = round((streamChunk.get('load_duration') or 0)/1000000000, 4)
            prompt_time = round((streamChunk.get('prompt_eval_duration') or 0)/1000000000,2)
            eval_count = streamChunk.get('eval_count') or 0
            eval_duration = (streamChunk.get('eval_duration') or 0)/1000000000 or 1
            token_speed = round(eval_count/eval_duration, 2)

            debug.info("Ollama", "load " + str(load_time) + "s, " + "prompt " + str(prompt_time) + "s, " + str(token_speed) + " tokens/s")
    if current_sentence.strip() != "":
        yield current_sentence.strip()

    if full_response.strip() != "":
        chat_history.append({"role":"user", "content": prompt})
        chat_history.append({"role":"assistant", "content": full_response.strip()})

    chat_history[:] = chat_history[-cfg["llm"]["memory_turns"] * 2:]
    time_since_last_interaction = time.monotonic()


def warm_up():
    response = ollama.chat(
        model=cfg["llm"]["model"],
        messages=[
            {"role": "system", "content": cfg["llm"]["system_prompt"]},
            {"role": "user", "content": "Hi"},
        ],
        options={"num_predict": 1},
        keep_alive=cfg["llm"]["keep_alive"],
    )
