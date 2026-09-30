const BASE = import.meta.env.VITE_API || "http://localhost:8000";

async function j(res) {
  if (!res.ok) {
    let msg = res.statusText;
    try { msg = (await res.json()).detail || msg; } catch {}
    throw new Error(msg);
  }
  return res.json();
}

export const api = {
  lastTap: () => fetch(`${BASE}/last_tap`).then(j),
  patients: () => fetch(`${BASE}/patients`).then(j),
  patient: (uid) => fetch(`${BASE}/patient/${uid}`).then(j),
  drugs: () => fetch(`${BASE}/drugs`).then(j),
  check: (body) =>
    fetch(`${BASE}/check`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then(j),
  decision: (body) =>
    fetch(`${BASE}/decision`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then(j),
};
