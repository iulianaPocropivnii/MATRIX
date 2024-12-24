# MATRIX

## Description

This project is a web application built with Flask that integrates several AI-powered features for generating questions, correcting grammar in sentences, and detecting emotions from images. The application uses a T5 model for question generation from user-uploaded texts, an AI model for grammar correction in messages, and an emotion detection model for facial expressions in images.

### Key features include:

- **_Question Generation:_** Users can upload text files, and the application will generate relevant questions based on the content.
- **_Grammar Correction:_** Users can submit messages, and the application will correct any grammatical mistakes and respond based on the conversation context.
- **_Emotion Detection:_** Users can upload images to detect facial emotions using a deep learning model.
- **_Conversation History:_** The application maintains a history of messages exchanged between the user and the AI assistant.

**Project is to demonstrate the integration and use of various natural language processing and computer vision techniques to create an interactive and useful application.**

## Prerequisites

Before running this project, ensure you have the following installed:

- Python 3.7 or later
- pip (Python package manager)
- Visual Studio Code (VS Code) (optional, but recommended for development)

### Install Git LFS

If you are working with large files in this repository, ensure you have Git LFS installed:

- On macOS:

```bash
brew install git-lfs
```

- On Windows, download and install Git LFS from [Git LFS website](https://git-lfs.com/).

**You will need to pull those large files by running**

```bash
git lfs pull
```

## Setup Instructions

### 1. Clone the Repository

Start by cloning the project repository from GitHub:

```bash
git clone https://github.com/iulianaPocropivnii/MATRIX.git
cd your-repository
```

### 2. Create a Virtual Environment

#### On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

#### On macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r backend\requirements.txt
```

## Running the Application

### 1. Navigate to the Backend Directory

Move into the directory where app.py is located (e.g., backend):

```bash
cd backend
```

### 2. Run the Application

Start the application by running the following command:

```bash
python app.py
```

### 3. Running the Application

After running the application, open your browser and navigate to:

```bash
http://127.0.0.1:5000
```

---

# Emotion detection model

### Model Training Process

The **facial expression recognition model** was trained using a dataset sourced from [Kaggle's Face Expression Recognition Dataset](https://www.kaggle.com/datasets/jonathanoheix/face-expression-recognition-dataset). The process involved several steps, which are detailed below:

#### 1. **Dataset Preparation**

The dataset was divided into training and testing directories, each containing images categorized into seven facial expression classes (e.g., happy, sad, angry, etc.). A Python script was used to:

- Read the images from the directories.
- Assign labels to the images based on their respective class folders.
- Store the image paths and labels in a structured `pandas.DataFrame`.

#### 2. **Feature Extraction**

Each image was processed as follows:

- The images were converted to grayscale to reduce complexity.
- Resized to dimensions of 48x48 pixels to maintain uniformity.
- Transformed into NumPy arrays for compatibility with the model.
- Normalized by scaling pixel values to the range [0, 1].

#### 3. **Label Encoding**

The labels were encoded using `LabelEncoder` to convert categorical labels into numerical format. The encoded labels were further converted to one-hot encoding using `to_categorical`, enabling the model to classify images into one of the seven categories.

#### 4. **Model Architecture**

The model was built using the **Keras Sequential API** and comprised:

- **Convolutional Layers**: Four Conv2D layers with ReLU activation to extract spatial features from images.
- **MaxPooling Layers**: To reduce dimensionality and retain key features.
- **Dropout Layers**: Introduced after each convolutional block to prevent overfitting.
- **Flatten Layer**: To prepare the feature maps for the fully connected layers.
- **Dense Layers**: Two dense layers with ReLU activation for learning complex patterns.
- **Output Layer**: A final dense layer with a softmax activation function for multiclass classification.

#### 5. **Model Compilation**

The model was compiled using:

- **Optimizer**: Adam, for efficient gradient descent.
- **Loss Function**: Categorical cross-entropy, as it is suited for multiclass classification.
- **Metrics**: Accuracy, to evaluate the model's performance.

#### 6. **Model Training**

The model was trained with the following parameters:

- **Batch Size**: 128
- **Epochs**: 100
- **Validation Data**: A separate test set to monitor the model's performance.

#### 7. **Evaluation**

After training, the model's performance was evaluated on the test set. The loss and accuracy were calculated, demonstrating the effectiveness of the model in recognizing facial expressions.

#### 8. **Results**

The model achieved an accuracy of approximately **63.46** on the test set, indicating its ability to classify facial expressions effectively.

Here’s the refined version of the text for your README:

---

# Question Generation and Conversational AI System

## 1. Question Generation

### Model Used

The system utilizes a fine-tuned **T5 (Text-to-Text Transfer Transformer)** model. T5 treats all NLP tasks as text-to-text problems, enabling seamless encoding of question generation tasks as input-output pairs.

### Training Details

- **Pretrained Model**: The `t5-small` variant, pretrained by Google on the C4 dataset, serves as the foundation.
- **Fine-Tuning Dataset**: The model is fine-tuned using the **SQuAD (Stanford Question Answering Dataset)**, which contains context-answer pairs ideal for question generation tasks.
- **Preprocessing**:
  - Input texts are prefixed with `"context:"` followed by the relevant text.
  - Target texts are the questions corresponding to the provided context.
- **Tokenization**: Both inputs and outputs are tokenized using T5’s tokenizer. Special tokens ensure proper handling of sequence lengths.
- **Training Configuration**: Parameters such as batch size, learning rate, and number of epochs are specified in the `TrainingArguments`. The fine-tuned model is saved locally for inference.

### Inference Process

1. A text file containing the input is uploaded and processed.
2. The model generates questions based on the content using sampling-based methods with parameters like `top_k`, `top_p`, and `temperature`, ensuring diversity in the output.

### Output

- The system generates **five unique questions**, addressing different aspects of the input text.
- These questions are concatenated and returned as a **JSON response**.

---

## 2. Conversational AI

### Functionality

The conversational flow is implemented as follows:

1. **Chat Handling**: User messages are appended to a conversation history list.
2. **AI Response**: Responses are generated using the `generate_response_with_context` method from the `ai_model.py` module.

### Model Used

The system employs a **ChatGPT-like model** (e.g., `gpt-4o` or `gpt-4`) provided via a `g4f` API wrapper for LLMs. This model supports context retention, enabling coherent and meaningful multi-turn conversations.

### Process

1. **Message Preprocessing**: User messages are corrected for grammar using a dedicated prompt.
2. **Contextual Conversation**:
   - The original or corrected message is added to the conversation history.
   - The conversation history is used as input to generate a context-aware response.
3. **Adaptive Responses**: The system adapts its replies based on the prior exchange, maintaining coherence throughout the conversation.

---

This system provides a robust solution for question generation and conversational AI, leveraging state-of-the-art models for diverse NLP applications.
