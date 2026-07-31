const form = document.getElementById("generate-form");
const outputEl = document.getElementById("output");
const metaEl = document.getElementById("meta");
const submitBtn = document.getElementById("submit-btn");
const copyBtn = document.getElementById("copy-btn");
const clearBtn = document.getElementById("clear-btn");
const healthBadge = document.getElementById("health-badge");

let lastOutput = "";

async function checkHealth() {
  try {
    const res = await fetch("/health");
    const data = await res.json();
    if (!res.ok) throw new Error("Health check failed");

    if (data.llm_configured) {
      healthBadge.textContent = `API ready · ${data.model}`;
      healthBadge.className = "badge badge-ok";
    } else {
      healthBadge.textContent = "API up · set OPENAI_API_KEY";
      healthBadge.className = "badge badge-warn";
    }
  } catch {
    healthBadge.textContent = "API unavailable";
    healthBadge.className = "badge badge-warn";
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const userRequest = document.getElementById("user-request").value.trim();
  const mode = document.getElementById("mode").value;
  const targetModel = document.getElementById("target-model").value.trim();
  const outputFormat = document.getElementById("output-format").value;

  if (!userRequest) return;

  submitBtn.disabled = true;
  copyBtn.disabled = true;
  outputEl.classList.add("loading");
  outputEl.textContent = "Generating prompt…";
  metaEl.textContent = "";

  const payload = {
    user_request: userRequest,
    mode,
    output_format: outputFormat,
  };
  if (targetModel) payload.target_model = targetModel;

  try {
    const res = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || "Generation failed");
    }

    lastOutput = data.output;
    outputEl.textContent = data.output;
    outputEl.classList.remove("loading");
    copyBtn.disabled = false;

    const tokens = data.usage?.total_tokens;
    const tokenNote = tokens ? ` · ${tokens} tokens` : "";
    metaEl.textContent = `Mode: ${data.mode_used} · Model: ${data.model}${tokenNote}`;
  } catch (error) {
    outputEl.textContent = `Error: ${error.message}`;
    outputEl.classList.remove("loading");
  } finally {
    submitBtn.disabled = false;
  }
});

copyBtn.addEventListener("click", async () => {
  if (!lastOutput) return;
  try {
    await navigator.clipboard.writeText(lastOutput);
    copyBtn.textContent = "Copied!";
    setTimeout(() => {
      copyBtn.textContent = "Copy Output";
    }, 1500);
  } catch {
    copyBtn.textContent = "Copy failed";
  }
});

clearBtn.addEventListener("click", () => {
  document.getElementById("user-request").value = "";
  document.getElementById("target-model").value = "";
  outputEl.textContent = "Submit a request to generate a prompt.";
  metaEl.textContent = "";
  lastOutput = "";
  copyBtn.disabled = true;
});

checkHealth();
