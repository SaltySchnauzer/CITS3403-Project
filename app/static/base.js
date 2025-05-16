// -- base.js  --


// -- Re-usable Function to check if there is a session running --

async function checkIfSession(payload){
    try {
    const res = await fetch("/api/sessions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({type: "check"}),
    });
    if (!res.ok) throw new Error(await res.text());
    payload(await res.json());
    } catch (err) {
    console.error("Session check failed:", err);
    }
}



document.addEventListener("DOMContentLoaded", () => {
    // Check if session is running
    if (window.location.pathname != "/session"){
        checkIfSession(
            (json) => {
                if (json["status"] == "active"){
                    document.getElementById("session_active").classList.remove("hidden");
                }
            }
        );
    }
    
});