const API_BASE = "http://localhost:3001/api";

export async function createPatient(data) {
  const res = await fetch(`${API_BASE}/patients`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function listPatients() {
  const res = await fetch(`${API_BASE}/patients`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getPatient(id) {
  const res = await fetch(`${API_BASE}/patients/${id}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function submitVitals(patientId, vitals) {
  const res = await fetch(`${API_BASE}/patients/${patientId}/vitals`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(vitals),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function analyzeVitals(vitals, patientName = "Patient") {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ vitals, patient_name: patientName }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getVitalsHistory(patientId) {
  const res = await fetch(`${API_BASE}/patients/${patientId}/vitals`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getAlertHistory() {
  const res = await fetch(`${API_BASE}/alerts`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
