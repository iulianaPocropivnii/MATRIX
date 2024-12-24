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
```
brew install git-lfs
```
- On Windows, download and install Git LFS from [Git LFS website](https://git-lfs.com/).

**You will need to pull those large files by running**
```
git lfs pull
```

## Setup Instructions

### 1. Clone the Repository

Start by cloning the project repository from GitHub:

```
git clone https://github.com/iulianaPocropivnii/MATRIX.git
cd your-repository
```

### 2. Create a Virtual Environment

# On Windows:

```
python -m venv venv
venv\Scripts\activate
```

# On macOS/Linux:

```
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```
pip install -r backend\requirements.txt
```

## Running the Application

# 1. Navigate to the Backend Directory

Move into the directory where app.py is located (e.g., backend):

```
cd backend
```

# 2. Run the Application

Start the application by running the following command:

```
python app.py
```

## Running the Application

After running the application, open your browser and navigate to:

```
http://127.0.0.1:5000
```
