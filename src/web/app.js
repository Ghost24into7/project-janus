const healthBadge = document.getElementById("healthBadge");
const backendName = document.getElementById("backendName");
const jobIdValue = document.getElementById("jobIdValue");
const jobStatusValue = document.getElementById("jobStatusValue");
const progressBar = document.getElementById("progressBar");
const progressPercent = document.getElementById("progressPercent");
const statusMessage = document.getElementById("statusMessage");
const resultPreview = document.getElementById("resultPreview");
const refreshResultBtn = document.getElementById("refreshResultBtn");
const downloadResultBtn = document.getElementById("downloadResultBtn");
const clearFileBtn = document.getElementById("clearFileBtn");
const clearTextBtn = document.getElementById("clearTextBtn");
const fileForm = document.getElementById("fileForm");
const textForm = document.getElementById("textForm");
const fileInput = document.getElementById("fileInput");
const textInput = document.getElementById("textInput");
const textLabel = document.getElementById("textLabel");

let currentJobId = null;
let pollTimer = null;

function setHealth(state, label) {
  healthBadge.className = `badge rounded-pill ${state}`;
  healthBadge.textContent = label;
}

function setStatus(message, tone = "muted") {
  statusMessage.className = `status-message text-${tone}`;
  statusMessage.textContent = message;
}

function setProgress(value) {
  const clamped = Math.max(0, Math.min(100, value || 0));
  progressBar.style.width = `${clamped}%`;
  progressBar.textContent = `${Math.round(clamped)}%`;
  if (progressPercent) {
    progressPercent.textContent = `${Math.round(clamped)}%`;
  }
}

function setResult(text) {
  resultPreview.textContent = text || "No result yet.";
}

function setJob(jobId, status) {
  currentJobId = jobId;
  jobIdValue.textContent = jobId || "No job running";
  jobStatusValue.textContent = status || "Idle";
  downloadResultBtn.disabled = !jobId;
}

async function fetchHealth() {
  try {
    const response = await fetch("/health");
    if (!response.ok) throw new Error("health check failed");
    const data = await response.json();
    backendName.textContent = data.service || "OCR Intelligence Engine";
    setHealth("text-bg-success", "Healthy");
  } catch (error) {
    setHealth("text-bg-danger", "Offline");
  }
}

async function pollJob(jobId) {
  try {
    const response = await fetch(`/jobs/${jobId}`);
    if (!response.ok) {
      throw new Error("job not found");
    }

    const job = await response.json();
    setJob(job.job_id, job.status);
    setProgress(job.progress || 0);

    if (job.status === "completed") {
      setStatus("Processing complete.", "success");
      setProgress(100);
      await loadResult(jobId);
      stopPolling();
      return;
    }

    if (job.status === "failed") {
      setStatus(job.error || "Job failed.", "danger");
      stopPolling();
      return;
    }

    setStatus(`Processing ${job.status}...`, "warning");
  } catch (error) {
    setStatus("Unable to fetch job status.", "danger");
    stopPolling();
  }
}

async function loadResult(jobId = currentJobId) {
  if (!jobId) return;

  try {
    const response = await fetch(`/jobs/${jobId}/result`);
    if (!response.ok) {
      throw new Error("result not ready");
    }

    const markdown = await response.text();
    setResult(markdown);
    downloadResultBtn.disabled = false;
  } catch (error) {
    setResult("Result not ready yet.");
  }
}

function startPolling(jobId) {
  stopPolling();
  pollTimer = window.setInterval(() => pollJob(jobId), 2000);
  pollJob(jobId);
}

function stopPolling() {
  if (pollTimer) {
    window.clearInterval(pollTimer);
    pollTimer = null;
  }
}

fileForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const file = fileInput.files && fileInput.files[0];
  if (!file) {
    setStatus("Choose a file first.", "warning");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  setStatus("Uploading file...", "info");
  setResult("Processing started. Waiting for output...");
  setProgress(5);

  try {
    const response = await fetch("/documents/process", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Upload failed");
    }

    setJob(data.job_id, data.status);
    setStatus(`Queued ${data.source}.`, "info");
    startPolling(data.job_id);
  } catch (error) {
    setStatus(error.message || "Upload failed.", "danger");
  }
});

textForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const content = textInput.value.trim();
  if (!content) {
    setStatus("Paste legacy data or text first.", "warning");
    return;
  }

  const payload = {
    label: textLabel.value.trim() || "legacy_data",
    content,
  };

  setStatus("Submitting text payload...", "info");
  setResult("Processing started. Waiting for output...");
  setProgress(5);

  try {
    const response = await fetch("/documents/text", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Text processing failed");
    }

    setJob(data.job_id, data.status);
    setStatus(`Queued ${data.source}.`, "info");
    startPolling(data.job_id);
  } catch (error) {
    setStatus(error.message || "Text processing failed.", "danger");
  }
});

refreshResultBtn.addEventListener("click", () => loadResult());

clearFileBtn.addEventListener("click", () => {
  fileInput.value = "";
  setStatus("File selection cleared.", "secondary");
});

clearTextBtn.addEventListener("click", () => {
  textInput.value = "";
  textLabel.value = "legacy_data";
  setStatus("Text input cleared.", "secondary");
});

downloadResultBtn.addEventListener("click", async () => {
  if (!currentJobId) return;
  window.location.href = `/jobs/${currentJobId}/result`;
});

fetchHealth();
setJob(null, "Idle");
setProgress(0);
setResult("No result yet.");
