const API_BASE = "https://financial-calculations-api.onrender.com";

const out = document.getElementById("out");
const show = (obj) => (out.textContent = JSON.stringify(obj, null, 2));

document.getElementById("btnHealth").onclick = async () => {
 const r = await fetch(`${API_BASE}/v1/health`);
 show(await r.json());
};

document.getElementById("btnEcho").onclick = async () => {
 const r = await fetch(`${API_BASE}/v1/echo`, {
   method: "POST",
   headers: { "Content-Type": "application/json" },
   body: JSON.stringify({ message: "hello", number: 42 }),
 });
 show(await r.json());
};
