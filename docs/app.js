// === DEFAULT PRODUCTION URL ===
const DEFAULT_API_BASE = "https://financial-calculations-api.onrender.com";

// === Read API base from query param OR localStorage ===
function resolveApiBase() {
  const params = new URLSearchParams(window.location.search);

  // 1️⃣ Check query param
  const apiFromQuery = params.get("api");
  if (apiFromQuery) {
    try {
      // Save it for future sessions
      localStorage.setItem("api_base", apiFromQuery);
    } catch {
      // Ignore storage errors (e.g. disabled cookies)
    }
    return apiFromQuery;
  }

  // 2️⃣ Check localStorage
  try {
    const apiFromStorage = localStorage.getItem("api_base");
    if (apiFromStorage) {
      return apiFromStorage;
    }
  } catch {
    // Ignore storage errors
  }

  // 3️⃣ Fallback to default production
  return DEFAULT_API_BASE;
}

// Global API base used by client
const API_BASE = resolveApiBase();

console.log("Using API base:", API_BASE);

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
