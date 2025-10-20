// -------------------- USER GREETING --------------------
let userName = localStorage.getItem("user_name");
let headingElement = document.querySelector(".heading");

if (userName && userName !== "undefined") {
  headingElement.innerText = `Hello ${userName}! Welcome to Gita Bot!`;
} else {
  headingElement.innerText = "Hello, Parth! Welcome to Gita Bot!";
  localStorage.removeItem("user_name");
}

// -------------------- DOM ELEMENTS --------------------
const container = document.querySelector(".container");
const chatsContainer = document.querySelector(".chats-container");
const promptForm = document.querySelector(".prompt-form");
const promptInput = promptForm.querySelector(".prompt-input");
const fileInput = promptForm.querySelector("#file-input");
const fileUploadWrapper = promptForm.querySelector(".file-upload-wrapper");
const themeToggleBtn = document.querySelector("#theme-toggle-btn");
const logoutBtn = document.getElementById("logout-btn");
const logoutPopup = document.getElementById("logout-popup");
const confirmLogout = document.getElementById("confirm-logout");
const cancelLogout = document.getElementById("cancel-logout");

// Exit popup elements
const exitPopup = document.getElementById("exit-popup");
const confirmExit = document.getElementById("confirm-exit");
const cancelExit = document.getElementById("cancel-exit");

// -------------------- CONFIG --------------------
const API_URL = "http://127.0.0.1:8000/bot/generate/";
let controller, typingInterval;
const chatHistory = [];
const userData = { message: "", file: {} };

// -------------------- THEME --------------------
const isLightTheme = localStorage.getItem("themeColor") === "light_mode";
document.body.classList.toggle("light-theme", isLightTheme);
themeToggleBtn.textContent = isLightTheme ? "dark_mode" : "light_mode";

// -------------------- UTILITIES --------------------
const createMessageElement = (content, ...classes) => {
  const div = document.createElement("div");
  div.classList.add("message", ...classes);
  div.innerHTML = content;
  return div;
};

const scrollToBottom = () => container.scrollTo({ top: container.scrollHeight, behavior: "smooth" });

// -------------------- CHAT VIEW HANDLING --------------------

// Create a visible back button dynamically (top-left)
function createBackButton() {
  const backBtn = document.createElement("span");
  backBtn.id = "back-btn";
  backBtn.className = "material-symbols-rounded back-btn";
  backBtn.textContent = "arrow_back";
  document.body.appendChild(backBtn);
  backBtn.addEventListener("click", exitChatView);
}
createBackButton();

// History management
window.history.replaceState({ page: "home" }, "", window.location.href);

function enterChatView() {
  document.body.classList.add("chats-active");
  window.history.pushState({ page: "chat" }, "", window.location.href + "#chat");
}

function exitChatView() {
  document.body.classList.remove("chats-active");
  window.history.pushState({ page: "home" }, "", window.location.href);
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// Handle browser back button
window.addEventListener("popstate", (event) => {
  const state = event.state;
  if (document.body.classList.contains("chats-active")) {
    exitChatView(); // If in chat, go back to home
    return;
  }
  // Otherwise show exit popup
  exitPopup.style.display = "flex";
});

confirmExit.addEventListener("click", () => {
  exitPopup.style.display = "none";
  window.close(); // closes tab on mobile
});
cancelExit.addEventListener("click", () => {
  exitPopup.style.display = "none";
  history.pushState(null, "", window.location.href);
});

// -------------------- API RESPONSE --------------------
const generateResponse = async (botMsgDiv) => {
  const textElement = botMsgDiv.querySelector(".message-text");
  controller = new AbortController();

  try {
    enterChatView(); // Ensure we’re in chat view

    let userId = localStorage.getItem("user_id");
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: userData.message, user_id: userId }),
      signal: controller.signal,
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Something went wrong.");

    const responseText = data.response || "";
    const htmlContent = marked.parse(responseText); // Markdown → HTML
    textElement.innerHTML = htmlContent;
    botMsgDiv.classList.remove("loading");
    document.body.classList.remove("bot-responding");
    scrollToBottom();
  } catch (error) {
    textElement.textContent = error.message;
    textElement.style.color = "#d62939";
    botMsgDiv.classList.remove("loading");
    document.body.classList.remove("bot-responding");
  } finally {
    userData.file = {};
  }
};

// -------------------- FORM SUBMIT --------------------
const handleFormSubmit = (e) => {
  e.preventDefault();
  const userMessage = promptInput.value.trim();
  if (!userMessage || document.body.classList.contains("bot-responding")) return;

  userData.message = userMessage;
  promptInput.value = "";
  document.body.classList.add("chats-active", "bot-responding");
  fileUploadWrapper.classList.remove("file-attached", "img-attached", "active");

  // User message
  const userMsgHTML = `
    <p class="message-text"></p>
    ${
      userData.file.data
        ? userData.file.isImage
          ? `<img src="data:${userData.file.mime_type};base64,${userData.file.data}" class="img-attachment" />`
          : `<p class="file-attachment"><span class="material-symbols-rounded">description</span>${userData.file.fileName}</p>`
        : ""
    }
  `;
  const userMsgDiv = createMessageElement(userMsgHTML, "user-message");
  userMsgDiv.querySelector(".message-text").textContent = userData.message;
  chatsContainer.appendChild(userMsgDiv);
  scrollToBottom();

  setTimeout(() => {
    const botMsgHTML = `
      <img class="avatar" src="/static/krishna.png" />
      <p class="message-text">Just a sec...</p>
    `;
    const botMsgDiv = createMessageElement(botMsgHTML, "bot-message", "loading");
    chatsContainer.appendChild(botMsgDiv);
    scrollToBottom();
    generateResponse(botMsgDiv);
  }, 600);
};

// -------------------- FILE HANDLING --------------------
fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (!file) return;
  const isImage = file.type.startsWith("image/");
  const reader = new FileReader();
  reader.readAsDataURL(file);
  reader.onload = (e) => {
    fileInput.value = "";
    const base64String = e.target.result.split(",")[1];
    fileUploadWrapper.querySelector(".file-preview").src = e.target.result;
    fileUploadWrapper.classList.add("active", isImage ? "img-attached" : "file-attached");
    userData.file = { fileName: file.name, data: base64String, mime_type: file.type, isImage };
  };
});

document.querySelector("#cancel-file-btn").addEventListener("click", () => {
  userData.file = {};
  fileUploadWrapper.classList.remove("file-attached", "img-attached", "active");
});

// -------------------- STOP BOT RESPONSE --------------------
document.querySelector("#stop-response-btn").addEventListener("click", () => {
  controller?.abort();
  userData.file = {};
  clearInterval(typingInterval);
  chatsContainer.querySelector(".bot-message.loading")?.classList.remove("loading");
  document.body.classList.remove("bot-responding");
});

// -------------------- THEME TOGGLE --------------------
themeToggleBtn.addEventListener("click", () => {
  const isLightTheme = document.body.classList.toggle("light-theme");
  localStorage.setItem("themeColor", isLightTheme ? "light_mode" : "dark_mode");
  themeToggleBtn.textContent = isLightTheme ? "dark_mode" : "light_mode";
});

// -------------------- DELETE CHATS --------------------
document.querySelector("#delete-chats-btn").addEventListener("click", () => {
  chatHistory.length = 0;
  chatsContainer.innerHTML = "";
  document.body.classList.remove("chats-active", "bot-responding");
});

// -------------------- SUGGESTIONS --------------------
document.querySelectorAll(".suggestions-item").forEach((suggestion) => {
  suggestion.addEventListener("click", () => {
    promptInput.value = suggestion.querySelector(".text").textContent;
    promptForm.dispatchEvent(new Event("submit"));
  });
});

// -------------------- MOBILE INPUT BEHAVIOR --------------------
document.addEventListener("click", ({ target }) => {
  const wrapper = document.querySelector(".prompt-wrapper");
  const shouldHide =
    target.classList.contains("prompt-input") ||
    (wrapper.classList.contains("hide-controls") &&
      (target.id === "add-file-btn" || target.id === "stop-response-btn"));
  wrapper.classList.toggle("hide-controls", shouldHide);
});

promptForm.addEventListener("submit", handleFormSubmit);
promptForm.querySelector("#add-file-btn").addEventListener("click", () => fileInput.click());

// -------------------- LOGOUT FUNCTIONALITY --------------------
logoutBtn.addEventListener("click", () => {
  logoutPopup.style.display = "flex";
});

confirmLogout.addEventListener("click", () => {
  localStorage.removeItem("user_name");
  localStorage.removeItem("user_id");
  setTimeout(() => {
    window.location.href = "/static/authentication/html/login.html";
  }, 1000);
});

cancelLogout.addEventListener("click", () => {
  logoutPopup.style.display = "none";
});

window.addEventListener("click", (event) => {
  if (event.target === logoutPopup) {
    logoutPopup.style.display = "none";
  }
});
