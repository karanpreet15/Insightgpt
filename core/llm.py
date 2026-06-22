import ollama

MODEL = "qwen2.5-coder:7b"

def ask_llm(prompt):

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]
