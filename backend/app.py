from flask import Flask, request, jsonify, send_from_directory, render_template, url_for
from flask_cors import CORS
from ai_model import generate_response, suggest_topics, generate_response_with_context
from transformers import (
    T5Tokenizer,
    T5ForConditionalGeneration,
    Trainer,
    TrainingArguments,
)
from werkzeug.utils import secure_filename
from datasets import load_dataset
import os

app = Flask(__name__)  # Specifică locația frontend-ului
CORS(app)

messages = []

# Configurare directoare încărcare fișiere
UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = {"txt"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Încarcă modelul antrenat (sau îl antrenează doar o dată)
model_path = "./fine_tuned_model"
if os.path.exists(model_path):
    model = T5ForConditionalGeneration.from_pretrained(model_path)
    tokenizer = T5Tokenizer.from_pretrained(model_path)
else:
    model = T5ForConditionalGeneration.from_pretrained("t5-small")
    tokenizer = T5Tokenizer.from_pretrained("t5-small")
    dataset = load_dataset("squad")

    def preprocess_function(examples):
        inputs = ["context: " + context for context in examples["context"]]
        targets = examples["question"]
        model_inputs = tokenizer(
            inputs, max_length=256, truncation=True, padding="max_length"
        )
        labels = tokenizer(
            targets, max_length=32, truncation=True, padding="max_length"
        )
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    train_dataset = dataset["train"].map(preprocess_function, batched=True)
    val_dataset = dataset["validation"].map(preprocess_function, batched=True)

    # Selectăm un subset pentru rapiditate
    train_dataset = train_dataset.shuffle(seed=42).select(range(20000))
    val_dataset = val_dataset.shuffle(seed=42).select(range(4000))

    # Configurare antrenare
    training_args = TrainingArguments(
        output_dir="./results",
        num_train_epochs=3,
        per_device_train_batch_size=16,  # Creștere batch size
        evaluation_strategy="epoch",
        save_strategy="epoch",
        logging_dir="./logs",
        logging_steps=10,
        learning_rate=5e-5,
        fp16=True,  # Mixed precision pentru GPU
        save_total_limit=2,
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
    )

    trainer.train()

    # Salvează modelul
    model.save_pretrained(model_path)
    tokenizer.save_pretrained(model_path)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload", methods=["POST"])
def upload_file():
    """
    Endpoint pentru încărcarea fișierului și generarea întrebărilor.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Citește conținutul fișierului
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        # Generează întrebări
        input_text = (
            f"Generate five diverse and unique questions from the following text. "
            f"Ensure the questions focus on different aspects of the context provided. Text: {text}"
        )
        input_ids = tokenizer(input_text, return_tensors="pt").input_ids
        generated_ids = model.generate(
            input_ids,
            max_length=50,
            num_return_sequences=5,
            do_sample=True,
            top_k=50,
            temperature=0.8,
            top_p=0.95,
            repetition_penalty=2.0,
        )
        questions = [
            tokenizer.decode(g, skip_special_tokens=True) for g in generated_ids
        ]
        concatenated_questions = "\n".join(questions)
        message = f"give me some questions based on the given text: {text}"
        messages.append({"role": "user", "content": message})
        messages.append({"role": "assistant", "content": concatenated_questions})
        return jsonify({"questions": concatenated_questions}), 200
    else:
        return jsonify({"error": "File type not allowed"}), 400


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
    messages.append({"role": "user", "content": user_message})
    ai_response = generate_response_with_context(messages=messages)
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
