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

if __name__ == "__main__":
    stream = ollama.chat(
        model=cfg["llm"]["model"],
        messages=[
            {"role": "system", "content": cfg["llm"]["system_prompt"]},
            {'role': 'user', 'content': 'Why is the sky blue?'}],
        stream=True,
    )

    for chunk in stream:
        print(chunk['message']['content'])