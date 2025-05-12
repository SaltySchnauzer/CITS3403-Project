// JS for dynamically rendering sessions and posting data via JSON


document.addEventListener("DOMContentLoaded", () => {
  let startTime = null, timerInterval;
  const timerEl   = document.getElementById("timer");
  const startBtn  = document.getElementById("start-session");
  const endBtn    = document.getElementById("end-session");

  function fmt(ms) {
    const s = Math.floor(ms/1000)%60, m = Math.floor(ms/60000);
    return `${m.toString().padStart(2,"0")}:${s.toString().padStart(2,"0")}`;
  }

  startBtn.addEventListener("click", () => {
    startTime = Date.now();
    startBtn.disabled = true;
    endBtn.disabled   = false;
    timerInterval = setInterval(() => {
      timerEl.textContent = fmt(Date.now() - startTime);
    }, 500);
  });

  endBtn.addEventListener("click", async () => {
    clearInterval(timerInterval);
    const endTime  = Date.now();
    const payload  = {
      started_at: new Date(startTime).toISOString(),
      ended_at:   new Date(endTime).toISOString(),
      duration:   endTime - startTime
    };

    try {
      const res = await fetch("/api/sessions", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify(payload)
      });
      if (!res.ok) throw new Error(await res.text());
      await res.json();
    } catch (err) {
      console.error("Save failed:", err);
    }

    // reset UI
    timerEl.textContent = "00:00";
    startBtn.disabled = false;
    endBtn.disabled   = true;
  });
});