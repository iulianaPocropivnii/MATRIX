import g4f


# Generates an AI response based on a single user message.
def generate_response(user_message):
    response = g4f.ChatCompletion.create(
        model=g4f.models.gpt_4o,
        messages=[{"role": "user", "content": user_message}],
    )

    if isinstance(response, str):
        return response
    elif isinstance(response, dict) and "choices" in response:
        return response["choices"][0]["message"]["content"]
    else:
        raise ValueError(f"Unsupported response format: {response}")


# Generates an AI response using context from a conversation.
def generate_response_with_context(messages: list):
    response = g4f.ChatCompletion.create(model=g4f.models.gpt_4, messages=messages)
    if isinstance(response, str):
        return response.strip()
    else:
        raise ValueError("Unexpected response type from g4f.ChatCompletion.create")
