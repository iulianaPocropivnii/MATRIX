const chatList = document.getElementById("chat-list");
const messagesDiv = document.getElementById("messages");
const userInput = document.getElementById("user-input");
const sidebar = document.querySelector(".sidebar");
const inputForm = document.querySelector(".input-form");
const toggleSidebarButton = document.querySelector(".toggle-sidebar");
const paperclipIcon = document.querySelector(".fa-paperclip");
const cameraIcon = document.querySelector(".fa-camera");

const fileInput = document.createElement("input");
fileInput.type = "file";
fileInput.accept = ".txt";

let conversations = [];
let currentConversation = [];

// Add message
function addMessage(content, isBot = false) {
  const messageDiv = document.createElement("div");
  messageDiv.className = isBot ? "message ai-message" : "message user-message";

  if (isBot) {
    const avatar = document.createElement("img");
    avatar.src = "static/img/logo.png";
    avatar.alt = "AI Avatar";
    avatar.className = "ai-avatar";
    messageDiv.appendChild(avatar);
  }

  const messageText = document.createElement("p");
  messageText.textContent = content;
  messageDiv.appendChild(messageText);

  messagesDiv.appendChild(messageDiv);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;

  currentConversation.push({ content, isBot });
}

// Submitting a user message
inputForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const userMessage = userInput.value.trim();
  if (userMessage) {
    addMessage(userMessage);
    userInput.value = "";

    try {
      const response = await fetch("http://127.0.0.1:5000/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage }),
      });

      const data = await response.json();

      addMessage(data.response, true);
    } catch (error) {
      console.error("Error:", error);
      addMessage("An error occurred. Please try again.", true);
    }
  }
});

// Save new conversation
document
  .querySelector(".new-chat-button")
  .addEventListener("click", saveConversation);

// Save the current conversation 
function saveConversation() {
  if (currentConversation.length > 0) {
    conversations.push([...currentConversation]); 
    currentConversation = [];
    console.log("Conversation saved:", conversations);

    const chatItem = document.createElement("div");
    chatItem.className = "chat-item";
    chatItem.textContent = `Conversation ${conversations.length}`;
    chatItem.addEventListener("click", () => {
      messagesDiv.innerHTML = "";
      conversations[conversations.length - 1].forEach(({ content, isBot }) => {
        addMessage(content, isBot);
      });
    });
    chatList.appendChild(chatItem);
  } else {
    console.warn("No conversation to save!");
  }
}

// Sidebar
toggleSidebarButton.addEventListener("click", () => {
  sidebar.classList.toggle("hidden");
  const isSidebarHidden = sidebar.classList.contains("hidden");
  document.querySelector(".chat").style.marginLeft = isSidebarHidden
    ? "0"
    : "30px";
  document.querySelector(".chat").style.marginRight = isSidebarHidden
    ? "120px"
    : "0px";
});

// Height input 
userInput.addEventListener("input", () => {
  userInput.style.height = "20px";
  userInput.style.height = `${Math.min(userInput.scrollHeight, 40)}px`;
});

// File attachment
paperclipIcon.addEventListener("click", () => {
  fileInput.click();
});

fileInput.addEventListener("change", async () => {
  const file = fileInput.files[0]; 
  if (file) {
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      // Display all generated questions as a single message
      if (data.questions) {
        addMessage(data.questions, true); 
      } else {
        addMessage("No questions generated.", true);
      }
    } catch (error) {
      console.error("Error:", error); 
      addMessage("An error occurred while uploading the file.", true);
    }
  }
});

// Retrieve discussion topics
async function fetchTopics() {
  const response = await fetch("http://127.0.0.1:5000/topics");
  const data = await response.json();
  console.log("Suggested topics:", data.topics);
}
fetchTopics();

//------------------CAMERA----------------//
const startCameraButton = document.getElementById("start-camera");
const cameraContainer = document.getElementById("input-camera");
const webcam = document.getElementById("webcam");
const emotionText = document.getElementById("emotion");

let mediaStream;
let emotionDetectionInterval;

// Camera button (start and stop camera)
startCameraButton.addEventListener("click", async () => {
  if (webcam.style.display === "none") {
    // Show camera
    cameraContainer.style.display = "block";
    startCameraButton.innerHTML =
      '<i class="fas fa-video-slash" title="Turn off Camera"></i>';
    webcam.style.display = "block";
    await setupCamera();
    // Start detecting emotion in real-time
    startEmotionDetection();
  } else {
    // Hide camera
    cameraContainer.style.display = "none";
    startCameraButton.innerHTML =
      '<i class="fas fa-video" title="Turn on Camera"></i>';
    webcam.style.display = "none";
    stopCamera();
    // Stop emotion detection
    stopEmotionDetection();
  }
});

// Activate the camera
async function setupCamera() {
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
    webcam.srcObject = mediaStream;
    webcam.style.display = "block";
    console.log("Camera activată");
  } catch (err) {
    console.error("Eroare la accesarea camerei:", err);
  }
}

// Stop the camera
function stopCamera() {
  if (mediaStream) {
    const tracks = mediaStream.getTracks();
    tracks.forEach((track) => track.stop());
    mediaStream = null;
    console.log("Camera oprită");
  }
}

// Capture the frame and send it to the backend for emotion detection
async function captureFrameAndDetectEmotion() {
  const canvas = document.createElement("canvas");
  canvas.width = webcam.videoWidth;
  canvas.height = webcam.videoHeight;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(webcam, 0, 0, canvas.width, canvas.height);

  // Convert canvas to base64 image
  const imageBase64 = canvas.toDataURL("image/jpeg");

  // Send the image to the backend for emotion detection
  try {
    const response = await fetch("http://127.0.0.1:5000/detect_emotion", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ image: imageBase64 }),
    });
    const data = await response.json();
    console.log("Răspuns backend:", data);
    displayEmotion(data.emotion);
  } catch (error) {
    console.error("Error during emotion detection:", error);
  }
}

// Display the detected emotion
function displayEmotion(emotion) {
  const emotionIcons = {
    angry: "😡",
    disgust: "🤢",
    fear: "😨",
    happy: "😊",
    neutral: "😐",
    sad: "😢",
    surprise: "😲",
  };

  emotionText.innerHTML = `Detected Emotion: ${emotion} ${
    emotionIcons[emotion] || "❓"
  }`;
}

// Start detecting emotions
function startEmotionDetection() {
  emotionDetectionInterval = setInterval(captureFrameAndDetectEmotion, 1000);
}

// Stop detecting emotions
function stopEmotionDetection() {
  if (emotionDetectionInterval) {
    clearInterval(emotionDetectionInterval);
    console.log("Emotion detection stopped");
  }

  // Clear the text area displaying the detected emotion
  const emotionText = document.getElementById("emotion");
  if (emotionText) {
    emotionText.innerHTML = "";
  }
}

