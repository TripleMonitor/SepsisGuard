import { useState } from "react";

export default function PatientManager({ onPatientCreated }) {
  const [name, setName] = useState("");
  const [age, setAge] = useState("");
  const [contactName, setContactName] = useState("");
  const [contactEmail, setContactEmail] = useState("");
  const [contactRelation, setContactRelation] = useState("Family");
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(false);

  function addContact() {
    if (!contactName || !contactEmail) return;
    setContacts([...contacts, { name: contactName, email: contactEmail, relationship: contactRelation }]);
    setContactName("");
    setContactEmail("");
    setContactRelation("Family");
  }

  function removeContact(idx) {
    setContacts(contacts.filter((_, i) => i !== idx));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!name) return;
    setLoading(true);
    try {
      await onPatientCreated({
        name,
        age: age ? parseInt(age) : null,
        emergency_contacts: contacts,
      });
      setName("");
      setAge("");
      setContacts([]);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  }

  return (
    <div className="card">
      <div className="card-header">
        <div className="icon" style={{ background: "rgba(139,92,246,0.15)", color: "var(--accent-purple)" }}>👤</div>
        <h2>Register Patient</h2>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label>Patient Name</label>
            <input
              id="patient-name"
              type="text"
              placeholder="Full name"
              value={name}
              onChange={e => setName(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label>Age</label>
            <input
              id="patient-age"
              type="number"
              placeholder="Age"
              value={age}
              onChange={e => setAge(e.target.value)}
              min="0"
              max="150"
            />
          </div>
        </div>

        <div style={{ marginTop: 12, marginBottom: 12 }}>
          <label style={{ fontSize: 12, fontWeight: 600, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: 0.5 }}>
            Emergency Contacts (Email)
          </label>
          <div style={{ display: "flex", gap: 8, marginTop: 6, flexWrap: "wrap" }}>
            <input
              id="contact-name"
              type="text"
              placeholder="Contact name"
              value={contactName}
              onChange={e => setContactName(e.target.value)}
              style={{ flex: 1, minWidth: 120, padding: "8px 12px", background: "var(--bg-input)", border: "1px solid var(--border-color)", borderRadius: "var(--radius-sm)", color: "var(--text-primary)", fontFamily: "inherit", fontSize: 13, outline: "none" }}
            />
            <input
              id="contact-email"
              type="email"
              placeholder="email@example.com"
              value={contactEmail}
              onChange={e => setContactEmail(e.target.value)}
              style={{ flex: 1.5, minWidth: 160, padding: "8px 12px", background: "var(--bg-input)", border: "1px solid var(--border-color)", borderRadius: "var(--radius-sm)", color: "var(--text-primary)", fontFamily: "inherit", fontSize: 13, outline: "none" }}
            />
            <select
              id="contact-relation"
              value={contactRelation}
              onChange={e => setContactRelation(e.target.value)}
              style={{ padding: "8px 12px", background: "var(--bg-input)", border: "1px solid var(--border-color)", borderRadius: "var(--radius-sm)", color: "var(--text-primary)", fontFamily: "inherit", fontSize: 13, outline: "none" }}
            >
              <option value="Family">Family</option>
              <option value="Spouse">Spouse</option>
              <option value="Parent">Parent</option>
              <option value="Sibling">Sibling</option>
              <option value="Friend">Friend</option>
            </select>
            <button type="button" className="btn btn-ghost" onClick={addContact} style={{ padding: "8px 14px" }}>+ Add</button>
          </div>
        </div>

        {contacts.length > 0 && (
          <div style={{ marginBottom: 16 }}>
            {contacts.map((c, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, padding: "6px 10px", background: "var(--bg-glass)", borderRadius: "var(--radius-sm)", marginBottom: 4, fontSize: 13 }}>
                <span>📧</span>
                <span style={{ flex: 1 }}>{c.name} — {c.email} ({c.relationship})</span>
                <button type="button" onClick={() => removeContact(i)} style={{ background: "none", border: "none", color: "var(--accent-red)", cursor: "pointer", fontSize: 16 }}>×</button>
              </div>
            ))}
          </div>
        )}

        <button id="register-patient-btn" type="submit" className="btn btn-primary btn-full" disabled={loading || !name}>
          {loading ? <><span className="spinner"></span>Registering...</> : "🩺 Register Patient"}
        </button>
      </form>
    </div>
  );
}
