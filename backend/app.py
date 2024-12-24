from flask import Flask, request, jsonify, send_from_directory, render_template, url_for
from flask_cors import CORS
from ai_model import generate_response, generate_response_with_context
from transformers import (
    T5Tokenizer,
    T5ForConditionalGeneration,
    Trainer,
    TrainingArguments,
)
from werkzeug.utils import secure_filename
from datasets import load_dataset
import os
import base64
from io import BytesIO
import cv2
from keras.models import model_from_json
import numpy as np
from PIL import Image

# Initialize the Flask app
app = Flask(__name__)
CORS(app)

messages = []

# Store conversation history
UPLOAD_FOLDER = "backend/uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
ALLOWED_EXTENSIONS = {"txt"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Load the trained model (or train it only once)
model_path = "backend/fine_tuned_model"
if os.path.exists(model_path):
    qa_model = T5ForConditionalGeneration.from_pretrained(model_path)
    qa_tokenizer = T5Tokenizer.from_pretrained(model_path)
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

    # Select a subset for speed
    train_dataset = train_dataset.shuffle(seed=42).select(range(20000))
    val_dataset = val_dataset.shuffle(seed=42).select(range(4000))

    # Training setup
    training_args = TrainingArguments(
        output_dir="./results",
        num_train_epochs=3,
        per_device_train_batch_size=16,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        logging_dir="./logs",
        logging_steps=10,
        learning_rate=5e-5,
        fp16=True,
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

    # Save model
    model.save_pretrained(model_path)
    tokenizer.save_pretrained(model_path)


# Check if the uploaded file is allowed based on its extension
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Handle file uploads, validate them, and generate questions based on the file content
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Reed file
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        # Generate questions
        input_text = (
            f"Generate five diverse and unique questions from the following text. "
            f"Ensure the questions focus on different aspects of the context provided. Text: {text}"
        )
        input_ids = qa_tokenizer(
            input_text[:512], return_tensors="pt", truncation=True
        ).input_ids
        generated_ids = qa_model.generate(
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
            qa_tokenizer.decode(g, skip_special_tokens=True) for g in generated_ids
        ]
        concatenated_questions = "\n".join(questions)
        message = f"give me some questions based on the given text: {text}"
        messages.append({"role": "user", "content": message})
        messages.append({"role": "assistant", "content": concatenated_questions})
        return jsonify({"questions": concatenated_questions}), 200
    else:
        return jsonify({"error": "File type not allowed"}), 400


# Serve the frontend of the application by rendering the main HTML file
@app.route("/", methods=["GET"])
def serve_frontend():
    return render_template("index.html")


# Handle chat interactions by processing user messages and generating AI responses
@app.route("/generate", methods=["POST"])
def chat():
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


# Provide the message history of the conversation
@app.route("/history", methods=["GET"])
def history():
    return jsonify(messages)


# Serve static files, such as CSS and JavaScript, from the frontend directory
@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory(os.path.join("..", "frontend"), filename)


# Load the emotion detection model and weights
json_file = open("../MATRIX/backend/camera_models/emotiondetector.json", "r")
model_json = json_file.read()
json_file.close()
model = model_from_json(model_json)
model.load_weights("../MATRIX/backend/camera_models/emotiondetector.h5")

# Load the Haar Cascade for face detection
haar_file = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(haar_file)

labels = {
    0: "angry",
    1: "disgust",
    2: "fear",
    3: "happy",
    4: "neutral",
    5: "sad",
    6: "surprise",
}


# Preprocess the image to extract features for emotion detection
def extract_features(image):
    feature = np.array(image)
    feature = feature.reshape(1, 48, 48, 1)
    return feature / 255.0


# Route to detect emotions from the uploaded image
@app.route("/detect_emotion", methods=["POST"])
def detect_emotion():
    data = request.get_json()
    image_data = data["image"]

    img_data = base64.b64decode(image_data.split(",")[1])
    img = Image.open(BytesIO(img_data))
    img = np.array(img)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    # Process the first detected face
    if len(faces) > 0:
        for x, y, w, h in faces:
            face = gray[y : y + h, x : x + w]
            face_resized = cv2.resize(face, (48, 48))
            face_preprocessed = extract_features(face_resized)

            # Predict the emotion
            pred = model.predict(face_preprocessed)
            emotion = labels[pred.argmax()]
            return jsonify({"emotion": emotion})
    else:
        return jsonify({"error": "No face detected"})


if __name__ == "__main__":
    app.run(debug=True)
