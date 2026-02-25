const API_BASE = "https://financial-calculations-api.onrender.com";

// Wait for DOM to be ready
document.addEventListener("DOMContentLoaded", () => {
  const out = document.getElementById("out");
  const btnHealth = document.getElementById("btnHealth");
  const btnEcho = document.getElementById("btnEcho");

  const show = (obj) => {
    out.textContent = JSON.stringify(obj, null, 2);
  };

  const showError = (error) => {
    out.textContent = `Error: ${error.message || error}`;
  };

  btnHealth.onclick = async () => {
    try {
      out.textContent = "Loading...";
      const r = await fetch(`${API_BASE}/v1/health`);
      const data = await r.json();
      show(data);
    } catch (error) {
      showError(error);
    }
  };

  btnEcho.onclick = async () => {
    try {
      out.textContent = "Loading...";
      const r = await fetch(`${API_BASE}/v1/echo`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: "hello", number: 42 }),
      });
      const data = await r.json();
      show(data);
    } catch (error) {
      showError(error);
    }
  };
});
