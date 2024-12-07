from flask import Flask, request, jsonify, send_from_directory, render_template,url_for
from flask_cors import CORS
from ai_model import generate_response, suggest_topics,correct_grammar, generate_response_with_context
import os
from database import init_db, save_to_db, get_history
app = Flask(__name__)  # Specifică locația frontend-ului
CORS(app)
init_db()
# Istoric conversație
conversation_history = []

@app.route("/", methods=["GET"])
def serve_frontend():
    """
    Servește pagina principală a aplicației (index.html).
    """
    return render_template( "index.html")

@app.route("/generate", methods=["POST"])
def chat():
    """
    Endpoint pentru generarea răspunsurilor AI cu păstrarea contextului.
    """
    data = request.get_json()
    user_message = data.get("message")
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Corectarea mesajului
    corrected_message = correct_grammar(user_message)
    
    # Generare răspuns cu context
    ai_response = generate_response_with_context(conversation_history, corrected_message)
    
    # Actualizează istoricul conversației
    conversation_history.append({"user": corrected_message, "ai": ai_response})
    
    return jsonify({
        "response": ai_response,
        "corrected_message": corrected_message
    })
@app.route("/history", methods=["GET"])
def history():
    """
    Returnează istoricul conversației.
    """
    return jsonify(conversation_history)

@app.route("/topics", methods=["GET"])
def topics():
    """
    Returnează sugestii de subiecte generate de AI.
    """
    data = request.get_json()
    context = data.get("context", "")
    topics = suggest_topics()
    return jsonify({"topics": topics})

@app.route('/static/<path:filename>')
def serve_static(filename):
    """
    Servește fișierele statice (CSS, JS, imagini).
    """
    return send_from_directory(os.path.join("..", "frontend"), filename)

if __name__ == "__main__":
    app.run(debug=True)