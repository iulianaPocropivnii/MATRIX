import g4f


def generate_response(user_message):
    """
    Generează un răspuns AI folosind ChatGLM.
    """
    # Obține răspunsul de la model
    response = g4f.ChatCompletion.create(
        model=g4f.models.gpt_4o,
        messages=[{"role": "user", "content": user_message}],
    )

    # Verifică formatul răspunsului
    if isinstance(response, str):
        # Dacă este șir simplu
        return response
    elif isinstance(response, dict) and "choices" in response:
        # Dacă este obiect JSON complex
        return response["choices"][0]["message"]["content"]
    else:
        raise ValueError(f"Formatul răspunsului nu este suportat: {response}")


def generate_response_with_context(messages: list):

    response = g4f.ChatCompletion.create(model=g4f.models.gpt_4, messages=messages)

    # Dacă răspunsul este doar text
    if isinstance(response, str):
        return response.strip()  # Înlătură spațiile suplimentare, dacă există
    else:
        raise ValueError("Unexpected response type from g4f.ChatCompletion.create")


def suggest_topics(conversation_context=""):
    """
    Sugerează teme de discuție dinamice, bazate pe contextul conversației.
    """
    if conversation_context:
        prompt = f"Based on the following conversation context, suggest 5 topics:\n{conversation_context}"
    else:
        prompt = "Suggest 5 interesting topics for an English conversation."
    topics_response = generate_response(prompt)
    return topics_response.split("\n")[:5]
  