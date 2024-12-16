from flask import Flask, request, jsonify, send_from_directory, render_template, url_for
from flask_cors import CORS
from ai_model import generate_response, suggest_topics, generate_response_with_context
import os

app = Flask(__name__)  # Specifică locația frontend-ului
CORS(app)
# Istoric conversație
messages = []


@app.route("/", methods=["GET"])
def serve_frontend():
    """
    Servește pagina principală a aplicației (index.html).
    """
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def chat():
    """
    Endpoint pentru generarea răspunsurilor AI cu păstrarea contextului.
    """

    data = request.get_json()
    user_message = data.get("message")
    corrected_message = generate_response(
        f"Correct the following sentence for grammar errors and give me the only the corrected sentence, If it's already correct, repeat it as is:\n{user_message}"
    )
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    messages.append({"role": "user", "content": corrected_message})
    # Generare răspuns cu context
    ai_response = generate_response_with_context(messages=messages)

    # Actualizează istoricul conversației
    messages.append({"role": "assistant", "content": ai_response})

    response_text = ai_response
    if corrected_message != user_message:
        response_text = f"The correct sentence is: {corrected_message}\n\n{ai_response}"
    return jsonify({"response": response_text, "user_message": user_message})

  
@app.route("/history", methods=["GET"])
def history():
    """
    Returnează istoricul conversației.
    """
    return jsonify(messages)


@app.route("/topics", methods=["GET"])
def topics():
    """
    Returnează sugestii de subiecte generate de AI.
    """
    data = request.get_json()
    context = data.get("context", "")
    topics = suggest_topics()
    return jsonify({"topics": topics})


@app.route("/static/<path:filename>")
def serve_static(filename):
    """
    Servește fișierele statice (CSS, JS, imagini).
    """
    return send_from_directory(os.path.join("..", "frontend"), filename)


if __name__ == "__main__":
    app.run(debug=True)
