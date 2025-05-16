
// -- session.js !!! --


document.addEventListener("DOMContentLoaded", () => {
  let startTime = null, timerInterval;
  let sessionID = null;
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

  // Gets time from server and resyncs timer
  async function resyncTime(){
    const payload = {
      type: "time",
      id: sessionID
    };

    try {
      const res = await fetch("/api/sessions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error(await res.text());
      const session_json = await res.json();
      startTime = new Date(Date.parse(session_json["start_time"]));
    } catch (err) {
      console.error("Session time-sync failed:", err);
    }
  }

  // Pick up an old session
  if (typeof oldSession !== 'undefined'){
    sessionID = oldSession;
    
    // Copied from below - transition page to timer started
    timerInterval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      timerEl.textContent = fmt(elapsed);
      if (focusTimer) focusTimer.textContent = fmt(elapsed);
    }, 500);

    startBtn.disabled = true;
    endBtn.disabled = false;
    
    // Hide original content original content
    sessionWrapper.classList.add("fade-out"); // Kept to prevent an error down the line - doesn't actually do anything
    sessionWrapper.classList.add("hidden");
    focusMode.classList.remove("hidden");

    resyncTime() // Time isn't synced - call and resync time
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

    // Send POST req to server to get ID
    startSession()
  });

  // Set a request to the server to start a session
  async function startSession(){
    const payload = {
      type: "start"
    };

    try {
      const res = await fetch("/api/sessions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error(await res.text());
      const session_json = await res.json();
      sessionID = session_json["session"]["id"];
    } catch (err) {
      console.error("Session Start failed:", err);
    }
  }

  // Attempt a session abort (cancel entirely)
  async function abortSession(){
    try {
      const res = await fetch("/api/sessions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({id: sessionID, type:"abort"}),
      });
      if (!res.ok) throw new Error(await res.text());
      const session_json = await res.json();
      sessionID = session_json["session"]["id"];
    } catch (err) {
      console.error("Session Start failed:", err);
    }
  }

  async function endSessionAndShowSummary() {
    clearInterval(timerInterval);
    const endTime = Date.now();
    if (sessionID == null){
      throw new Error("Session ID not set, but session end called on client.");
    }
    const payload = {
      type: "end",
      id: sessionID
    };

    try {
      const res = await fetch("/api/sessions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error(await res.text());
      await res.json();
      sessionID = null;
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
      abortSession()
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


  // Adds dynamic label to the productivity slider
  const prod_desc = document.getElementById("prod_desc");
  document.getElementById("prod_slider").oninput = function () {
    if (this.value < 5){
      prod_desc.textContent = "Nothing Done 😭"
    } else if(this.value < 30){
      prod_desc.textContent = "Did a little. 🫤"
    } else if(this.value < 50){
      prod_desc.textContent = "Did some."
    } else if(this.value < 75){
      prod_desc.textContent = "Did a fair bit."
    } else if(this.value < 95){
      prod_desc.textContent = "Did almost everything. 😎"
    } else{
      prod_desc.textContent = "Did everything!! 🥳"
    }
  };
  document.getElementById("prod_slider").oninput()
});


// -- Made with the assistance of Copilot --
