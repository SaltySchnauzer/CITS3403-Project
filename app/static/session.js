document.addEventListener("DOMContentLoaded", () => {
  let startTime = null, timerInterval;
  const timerEl     = document.getElementById("timer");
  const focusTimer  = document.getElementById("focus-timer");
  const startBtn    = document.getElementById("start-session");
  const endBtn      = document.getElementById("end-session");
  const focusEndBtn = document.getElementById("focus-end");

  const sessionWrapper = document.getElementById("session-wrapper");
  const focusMode      = document.getElementById("focus-mode");

  function fmt(ms) {
    const s = Math.floor(ms / 1000) % 60,
          m = Math.floor(ms / 60000);
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  }

  startBtn.addEventListener("click", () => {
    startTime = Date.now();
    startBtn.disabled = true;
    endBtn.disabled = false;

    // Start timer update
    timerInterval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      timerEl.textContent = fmt(elapsed);
      if (focusTimer) focusTimer.textContent = fmt(elapsed);
    }, 500);

    // Fade out original content, show focus mode
    sessionWrapper.classList.add("fade-out");
    setTimeout(() => {
      sessionWrapper.classList.add("hidden");
      focusMode.classList.remove("hidden");
    }, 700); // match fade-out duration
  });

  async function endSessionAndShowSummary() {
    clearInterval(timerInterval);
    const endTime = Date.now();
    const payload = {
      started_at: new Date(startTime).toISOString(),
      ended_at: new Date(endTime).toISOString(),
      duration: endTime - startTime,
    };

    try {
      const res = await fetch("/api/sessions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error(await res.text());
      await res.json();
    } catch (err) {
      console.error("Save failed:", err);
    }

    // Reset timers and buttons
    timerEl.textContent = "00:00";
    if (focusTimer) focusTimer.textContent = "00:00";
    startBtn.disabled = false;
    endBtn.disabled = true;

    // Hide focus mode, show original layout again
    focusMode.classList.add("hidden");
    sessionWrapper.classList.remove("hidden", "fade-out");
    sessionWrapper.classList.add("fade-in");

    // Show modal
    const modal = document.getElementById("session-summary-modal");
    if (modal) modal.classList.remove("hidden");
  }

  // End button from focus layout
  if (focusEndBtn) {
    focusEndBtn.addEventListener("click", () => {
      endSessionAndShowSummary();
    });
  }

  // Cancel modal handler
  const cancelBtn = document.getElementById("cancel-modal");
  if (cancelBtn) {
    cancelBtn.addEventListener("click", () => {
      document.getElementById("session-summary-modal").classList.add("hidden");
    });
  }

  // Mood selection
  const emojiButtons = document.querySelectorAll(".emoji-btn");
  const moodInput = document.getElementById("mood-input");
  emojiButtons.forEach((button) => {
    button.addEventListener("click", () => {
      emojiButtons.forEach((b) => b.classList.remove("selected"));
      button.classList.add("selected");
      moodInput.value = button.dataset.value;
    });
  });

  // Local time rendering
  document.querySelectorAll(".session-time").forEach(el => {
    const start = new Date(el.dataset.start);
    const end = new Date(el.dataset.end);
    if (!start || !end || isNaN(start.getTime()) || isNaN(end.getTime())) {
      el.textContent = "Invalid date";
      return;
    }

    const options = { dateStyle: "medium", timeStyle: "short" };
    el.textContent = `${start.toLocaleString(undefined, options)} → ${end.toLocaleTimeString(undefined, { timeStyle: "short" })}`;
  });
});
