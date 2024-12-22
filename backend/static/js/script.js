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
fileInput.accept = ".txt"; // Limităm fișierele la .txt

let conversations = [];
let currentConversation = [];

/** Add message */
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

/** response */
inputForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const userMessage = userInput.value.trim();
  if (userMessage) {
    // Afișează mesajul utilizatorului
    addMessage(userMessage);
    userInput.value = "";

    try {
      // Trimite cererea către backend
      const response = await fetch("http://127.0.0.1:5000/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage }),
      });

      const data = await response.json();

      // Afișează răspunsul AI (corectarea propoziției + răspuns)
      addMessage(data.response, true);
    } catch (error) {
      console.error("Error:", error);
      addMessage("An error occurred. Please try again.", true);
    }
  }
});

/** save new conversation */
document
  .querySelector(".new-chat-button")
  .addEventListener("click", saveConversation);

/** Save the current conversation */
function saveConversation() {
  if (currentConversation.length > 0) {
    conversations.push([...currentConversation]); // Save the current conversation
    currentConversation = []; // Reset the current conversation
    console.log("Conversation saved:", conversations);

    // Optionally update the UI
    const chatItem = document.createElement("div");
    chatItem.className = "chat-item";
    chatItem.textContent = `Conversation ${conversations.length}`;
    chatItem.addEventListener("click", () => {
      // Load the saved conversation
      messagesDiv.innerHTML = ""; // Clear messages
      conversations[conversations.length - 1].forEach(({ content, isBot }) => {
        addMessage(content, isBot);
      });
    });
    chatList.appendChild(chatItem);
  } else {
    console.warn("No conversation to save!");
  }
}
/** Sidebar */
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

/** height input */
userInput.addEventListener("input", () => {
  userInput.style.height = "20px";
  userInput.style.height = `${Math.min(userInput.scrollHeight, 40)}px`;
});

/** file */
// Eveniment pentru încărcarea fișierului
paperclipIcon.addEventListener("click", () => {
  fileInput.click(); // Deschide dialogul de alegere fișier
});

fileInput.addEventListener("change", async () => {
  const file = fileInput.files[0]; // Obține fișierul selectat
  if (file) {
    const formData = new FormData();
    formData.append("file", file); // Adaugă fișierul la FormData

    try {
      // Trimite fișierul la backend
      const response = await fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      // Afișează toate întrebările generate ca un singur mesaj
      if (data.questions) {
        addMessage(data.questions, true); // Afișează toate întrebările concatenate
      } else {
        addMessage("No questions generated.", true); // Mesaj dacă nu sunt întrebări
      }
    } catch (error) {
      console.error("Error:", error); // Verifică erorile în consola de dezvoltare
      addMessage("An error occurred while uploading the file.", true);
    }
  }
});

/** camera */
cameraIcon.addEventListener("click", () => {
  alert("Open the camera!");
});

// Preia teme de discuție
async function fetchTopics() {
  const response = await fetch("http://127.0.0.1:5000/topics");
  const data = await response.json();
  console.log("Suggested topics:", data.topics);
}
fetchTopics();
