import re
import ollama
from modules.config import cfg



def ask(prompt: str) -> str:
    """Send one text prompt to the local LLM and return the reply as text."""
    response = ollama.chat(
        model=cfg["llm"]["model"],
        messages=[
            {"role": "system", "content": cfg["llm"]["system_prompt"]},
            {"role": "user", "content": prompt},
        ],
        options={"num_predict": cfg["llm"]["max_tokens"]},  # hard cap on reply length (in tokens)
    )
    return response["message"]["content"].strip()

def ask_stream(prompt: str):
    """Send one text prompt to the local LLM and yield each sentence."""
    current_sentence = ""
    response = ollama.chat(
        model=cfg["llm"]["model"],
        messages=[
            {"role": "system", "content": cfg["llm"]["system_prompt"]},
            {"role": "user", "content": prompt},
        ],
        options={"num_predict": cfg["llm"]["max_tokens"]},  # hard cap on reply length (in tokens)
        stream=True
    )
    for streamChunk in response:
        current_sentence += streamChunk['message']['content']

        while re.search(r"[.!?]\s", current_sentence):
            sentence_end = re.search(r"[.!?]\s", current_sentence).end()
            yield current_sentence[0:sentence_end].strip()
            current_sentence = current_sentence[sentence_end:]

    if current_sentence.strip() != "":
        yield current_sentence.strip()


