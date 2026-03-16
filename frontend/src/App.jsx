import { useState, useCallback } from "react";
import PatientManager from "./components/PatientManager";
import VitalsForm from "./components/VitalsForm";
import VitalsDashboard from "./components/VitalsDashboard";
import AIAnalysis from "./components/AIAnalysis";
import AlertStatus from "./components/AlertStatus";
import { createPatient, listPatients, submitVitals } from "./api";
import "./App.css";

function App() {
  const [patients, setPatients] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [activeTab, setActiveTab] = useState("register");
  const [lastVitals, setLastVitals] = useState(null);
  const [lastQsofa, setLastQsofa] = useState(null);
  const [mlScore, setMlScore] = useState(null);
  const [mlRiskLevel, setMlRiskLevel] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [aiExplanation, setAiExplanation] = useState("");
  const [alertSent, setAlertSent] = useState(false);
  const [alertDetails, setAlertDetails] = useState([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [notification, setNotification] = useState(null);

  const showNotification = useCallback((type, message) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 5000);
  }, []);

  async function handlePatientCreated(data) {
    try {
      const patient = await createPatient(data);
      const updated = await listPatients();
      setPatients(updated);
      setSelectedPatient(patient);
      setActiveTab("monitor");
      showNotification("success", `Patient "${patient.name}" registered successfully!`);
    } catch (err) {
      showNotification("danger", `Error: ${err.message}`);
    }
  }

  async function handleVitalsSubmit(vitals) {
    if (!selectedPatient) {
      showNotification("danger", "Please select a patient first");
      return;
    }

    setAnalyzing(true);
    setAiExplanation("");
    setAlertSent(false);
    setAlertDetails([]);

    try {
      const result = await submitVitals(selectedPatient.id, vitals);
      setLastVitals(vitals);
      setLastQsofa(result.qsofa);
      setMlScore(result.ml_score);
      setMlRiskLevel(result.ml_risk_level);
      setRecommendation(result.recommendation);
      setAiExplanation(result.explanation);
      setAlertSent(result.alert_sent);
      if (result.alert_details) setAlertDetails(result.alert_details);

      if (result.ml_risk_level === "high") {
        showNotification("danger", `⚠️ HIGH RISK! ML Score: ${(result.ml_score * 100).toFixed(1)}% | qSOFA: ${result.qsofa.score}/3`);
      } else {
        showNotification("success", `Vitals analyzed — Risk Level: ${result.ml_risk_level}`);
      }
    } catch (err) {
      showNotification("danger", `Error: ${err.message}`);
    }

    setAnalyzing(false);
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="logo">
          <div className="logo-icon">🛡️</div>
          <div>
            <h1>SepsisGuard AI</h1>
            <div className="subtitle">Early Warning System · Powered by Gemini AI</div>
          </div>
        </div>
      </header>

      <main className="app-main">
        {/* Notification */}
        {notification && (
          <div className={`alert-banner ${notification.type}`}>
            <span>{notification.type === "danger" ? "⚠️" : notification.type === "success" ? "✅" : "ℹ️"}</span>
            {notification.message}
          </div>
        )}

        {/* Tabs */}
        <div className="tabs">
          <button className={`tab ${activeTab === "register" ? "active" : ""}`} onClick={() => setActiveTab("register")}>
            👤 Register Patient
          </button>
          <button className={`tab ${activeTab === "monitor" ? "active" : ""}`} onClick={() => setActiveTab("monitor")}>
            📊 Monitor Vitals
          </button>
        </div>

        {/* Registration Tab */}
        {activeTab === "register" && (
          <div style={{ maxWidth: 640 }}>
            <PatientManager onPatientCreated={handlePatientCreated} />
          </div>
        )}

        {/* Monitor Tab */}
        {activeTab === "monitor" && (
          <>
            {/* Patient Selector */}
            <div className="patient-selector">
              <span style={{ fontSize: 14, color: "var(--text-secondary)" }}>Patient:</span>
              <select
                id="patient-selector"
                value={selectedPatient?.id || ""}
                onChange={e => {
                  const p = patients.find(p => p.id === e.target.value);
                  setSelectedPatient(p || null);
                  setLastVitals(null);
                  setLastQsofa(null);
                  setMlScore(null);
                  setMlRiskLevel(null);
                  setRecommendation(null);
                  setAiExplanation("");
                  setAlertSent(false);
                  setAlertDetails([]);
                }}
              >
                <option value="">— Select a patient —</option>
                {patients.map(p => (
                  <option key={p.id} value={p.id}>{p.name}{p.age ? ` (${p.age}y)` : ""}</option>
                ))}
              </select>
              {selectedPatient?.emergency_contacts?.length > 0 && (
                <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
                  📧 {selectedPatient.emergency_contacts.length} emergency contact(s)
                </span>
              )}
            </div>

            {!selectedPatient ? (
              <div className="card">
                <div className="empty-state">
                  <div className="icon">👤</div>
                  <h3>No Patient Selected</h3>
                  <p>Register a patient first, or select one from the dropdown</p>
                  <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={() => setActiveTab("register")}>
                    Register Patient
                  </button>
                </div>
              </div>
            ) : (
              <div className="grid-2">
                {/* Left Column: Input + Dashboard */}
                <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
                  <VitalsForm onSubmit={handleVitalsSubmit} loading={analyzing} />
                  <VitalsDashboard 
                    vitals={lastVitals} 
                    qsofa={lastQsofa} 
                    mlScore={mlScore} 
                    mlRiskLevel={mlRiskLevel} 
                    recommendation={recommendation} 
                  />
                </div>

                {/* Right Column: AI + Alerts */}
                <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
                  <AlertStatus alertSent={alertSent} alertDetails={alertDetails} />
                  <AIAnalysis explanation={aiExplanation} loading={analyzing} />
                </div>
              </div>
            )}
          </>
        )}
      </main>

      {/* Footer */}
      <footer style={{
        textAlign: "center",
        padding: "16px 32px",
        borderTop: "1px solid var(--border-color)",
        fontSize: 12,
        color: "var(--text-muted)",
      }}>
        ⚕️ For informational purposes only — not a substitute for professional medical advice.
      </footer>
    </div>
  );
}

export default App;
