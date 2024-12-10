const chatList = document.getElementById("chat-list");
const messagesDiv = document.getElementById("messages");
const userInput = document.getElementById("user-input");
const sidebar = document.querySelector(".sidebar");
const inputForm = document.querySelector(".input-form");
const toggleSidebarButton = document.querySelector(".toggle-sidebar");
const paperclipIcon = document.querySelector(".fa-paperclip");
const cameraIcon = document.querySelector(".fa-camera");

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
    addMessage(userMessage);
    userInput.value = "";

    // Trimite cerere către backend
    const response = await fetch("http://127.0.0.1:5000/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userMessage }),
    });

    const data = await response.json();
    addMessage(data.response, true);
  }
});

/** save new conversation */
document
  .querySelector(".new-chat-button")
  .addEventListener("click", saveConversation);

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
paperclipIcon.addEventListener("click", () => {
  alert("Attach a file!");
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
