import time
import ollama

MODEL = "llama3.2:3b"  # use "llama3.2:1b" to mimic Raspberry Pi speed

SYSTEM_PROMPT = (
    "You are a voice assistant. Your answers are spoken out loud, so reply in "
    "one or two short sentences. Use plain words only: no lists, no markdown, "
    "no emojis, no special characters."
)


def ask(prompt: str) -> str:
    """Send one text prompt to the local LLM and return the reply as text."""
    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        options={"num_predict": 120},  # hard cap on reply length (in tokens)
    )
    return response["message"]["content"].strip()