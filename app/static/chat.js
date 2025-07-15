const chatWindow = document.getElementById("chat-window");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const jobSetupModal = document.getElementById("job-setup-modal");
const jobSetupForm = document.getElementById("job-setup-form");

// Maintain conversation history and job information
let messages = [];
let jobInfo = {
  jobTitle: "",
  jobDescription: "",
  userResume: "",
};

function showJobSetupModal() {
  jobSetupModal.style.display = "block";
  document.getElementById("job-title").focus();
}

function hideJobSetupModal() {
  jobSetupModal.style.display = "none";
}

function initializeApp() {
  showJobSetupModal();
}

function appendMessage(text, sender) {
  const msgDiv = document.createElement("div");
  msgDiv.className = "message " + sender;
  msgDiv.textContent = text;
  chatWindow.appendChild(msgDiv);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  return msgDiv;
}

jobSetupForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const jobTitle = document.getElementById("job-title").value.trim();
  const jobDescription = document
    .getElementById("job-description")
    .value.trim();
  const userResume = document.getElementById("user-resume").value.trim();

  if (!jobTitle || !jobDescription || !userResume) {
    alert("Please fill in both job title and job description and user resume.");
    return;
  }

  jobInfo.jobTitle = jobTitle;
  jobInfo.jobDescription = jobDescription;
  jobInfo.userResume = userResume;
  hideJobSetupModal();

  appendMessage(
    `Welcome! You're interviewing for: ${jobTitle}, please wait for a moment, I'm preparing for your interview`,
    "agent"
  );
  chatInput.disabled = true;
  chatForm.querySelector("button").disabled = true;

  appendMessage(
    "Job Title: " + jobTitle + "\nJob Description: " + jobDescription,
    "user"
  );
  messages.push({
    role: "user",
    content:
      "This is my job description and job title, please refer to these information to ask me some questions",
  });
  chatInput.value = "";

  const assistantMsg = appendMessage("", "agent");
  let fullResponse = "";

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        messages,
        job_tile: jobTitle,
        job_description: jobDescription,
        user_resume: userResume,
      }),
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value);
      fullResponse += chunk;
      assistantMsg.textContent = fullResponse;
      chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    // Add the complete response to messages
    messages.push({ role: "assistant", content: fullResponse });
  } catch (err) {
    assistantMsg.textContent = "Error: Could not get response.";
    console.error("Error:", err);
  } finally {
    // Re-enable input
    chatInput.disabled = false;
    chatForm.querySelector("button").disabled = false;
    chatInput.focus();
  }
});

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const userMsg = chatInput.value.trim();
  if (!userMsg) return;

  // Disable input while processing
  chatInput.disabled = true;
  chatForm.querySelector("button").disabled = true;

  // Add user message
  appendMessage(userMsg, "user");
  messages.push({
    role: "user",
    content: userMsg,
  });
  chatInput.value = "";

  // Create assistant message container
  const assistantMsg = appendMessage("", "agent");
  let fullResponse = "";

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        messages,
        job_tile: jobInfo.jobTitle,
        job_description: jobInfo.jobDescription,
        user_resume: jobInfo.userResume,
      }),
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value);
      fullResponse += chunk;
      assistantMsg.textContent = fullResponse;
      chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    // Add the complete response to messages
    messages.push({ role: "assistant", content: fullResponse });
  } catch (err) {
    assistantMsg.textContent = "Error: Could not get response.";
    console.error("Error:", err);
  } finally {
    // Re-enable input
    chatInput.disabled = false;
    chatForm.querySelector("button").disabled = false;
    chatInput.focus();
  }
});

// Initialize the app when page loads
document.addEventListener("DOMContentLoaded", initializeApp);
