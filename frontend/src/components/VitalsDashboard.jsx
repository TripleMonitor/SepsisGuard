export default function VitalsDashboard({ vitals, qsofa, mlScore, mlRiskLevel, recommendation }) {
  if (!vitals) {
    return (
      <div className="card">
        <div className="empty-state">
          <div className="icon">📋</div>
          <h3>No Vitals Recorded</h3>
          <p>Submit patient vitals to see the dashboard</p>
        </div>
      </div>
    );
  }

  function getVitalStatus(key, value) {
    const rules = {
      heart_rate: v => v < 60 ? "danger" : v > 100 ? "danger" : "normal",
      spo2: v => v < 90 ? "danger" : v < 94 ? "warning" : "normal",
      temperature_f: v => v > 100.4 ? "danger" : v < 96.8 ? "warning" : "normal",
      respiratory_rate: v => v >= 22 ? "danger" : v < 12 ? "warning" : "normal",
      systolic_bp: v => v <= 100 ? "danger" : v > 180 ? "danger" : "normal",
      gcs_score: v => v < 15 ? "danger" : "normal",
    };
    return (rules[key] || (() => "normal"))(value);
  }

  function getStatusLabel(key, value) {
    const labels = {
      heart_rate: v => v < 60 ? "Bradycardia" : v > 100 ? "Tachycardia" : "Normal",
      spo2: v => v < 90 ? "Critical" : v < 94 ? "Low" : "Normal",
      temperature_f: v => v > 100.4 ? "Fever" : v < 96.8 ? "Hypothermia" : "Normal",
      respiratory_rate: v => v >= 22 ? "Elevated" : v < 12 ? "Low" : "Normal",
      systolic_bp: v => v <= 100 ? "Hypotension" : v > 180 ? "Crisis" : "Normal",
      gcs_score: v => v < 15 ? "Altered" : "Normal",
    };
    return (labels[key] || (() => "Normal"))(value);
  }

  const vitalCards = [
    { key: "heart_rate", label: "Heart Rate", value: vitals.heart_rate, unit: "bpm", icon: "❤️" },
    { key: "spo2", label: "Blood Oxygen", value: vitals.spo2, unit: "%", icon: "💨" },
    { key: "temperature_f", label: "Temperature", value: vitals.temperature_f, unit: "°F", icon: "🌡️" },
    { key: "respiratory_rate", label: "Breathing Rate", value: vitals.respiratory_rate, unit: "br/min", icon: "🫁" },
    { key: "systolic_bp", label: "Systolic BP", value: vitals.systolic_bp, unit: "mmHg", icon: "🩸" },
    { key: "gcs_score", label: "GCS Score", value: vitals.gcs_score, unit: "/ 15", icon: "🧠" },
  ];

  return (
    <div>
      {/* Vital Cards Grid */}
      <div className="grid-vitals" style={{ marginBottom: 20 }}>
        {vitalCards.map(vc => {
          const status = getVitalStatus(vc.key, vc.value);
          const label = getStatusLabel(vc.key, vc.value);
          return (
            <div key={vc.key} className={`vital-card ${status}`}>
              <div className="vital-label">{vc.icon} {vc.label}</div>
              <div className="vital-value" style={{ color: status === "danger" ? "var(--accent-red)" : status === "warning" ? "var(--accent-yellow)" : "var(--text-primary)" }}>
                {vc.value}
              </div>
              <div className="vital-unit">{vc.unit}</div>
              <div className={`vital-status ${status}`}>{label}</div>
            </div>
          );
        })}
      </div>

      {/* qSOFA Score */}
      {qsofa && (
        <div className="card">
          <div className="qsofa-display">
            <div className="vital-label" style={{ marginBottom: 8 }}>qSOFA SEPSIS SCORE</div>
            <div className={`qsofa-score ${qsofa.risk_level}`}>
              {qsofa.score}<span style={{ fontSize: 24, opacity: 0.5 }}>/3</span>
            </div>
            <div className="qsofa-label">Quick Sequential Organ Failure Assessment</div>
            <div className={`qsofa-risk ${qsofa.risk_level}`}>
              {qsofa.risk_level === "high" ? "🚨 " : qsofa.risk_level === "moderate" ? "⚠️ " : "✅ "}
              {qsofa.risk_level} risk
            </div>

            <div className="qsofa-criteria">
              <div className={`criteria-item ${qsofa.criteria.respiratory_rate_elevated ? "met" : "not-met"}`}>
                <span>{qsofa.criteria.respiratory_rate_elevated ? "🔴" : "⚪"}</span>
                Respiratory Rate ≥ 22
              </div>
              <div className={`criteria-item ${qsofa.criteria.systolic_bp_low ? "met" : "not-met"}`}>
                <span>{qsofa.criteria.systolic_bp_low ? "🔴" : "⚪"}</span>
                Systolic BP ≤ 100 mmHg
              </div>
              <div className={`criteria-item ${qsofa.criteria.altered_mental_status ? "met" : "not-met"}`}>
                <span>{qsofa.criteria.altered_mental_status ? "🔴" : "⚪"}</span>
                Altered Mental Status (GCS &lt; 15)
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ML Score */}
      {mlScore !== null && mlScore !== undefined && (
        <div className="card" style={{ marginTop: 20 }}>
          <div className="qsofa-display">
            <div className="vital-label" style={{ marginBottom: 8 }}>AI HYBRID RISK SCORE</div>
            <div className={`qsofa-score ${mlRiskLevel}`}>
              {(mlScore * 100).toFixed(1)}<span style={{ fontSize: 24, opacity: 0.5 }}>%</span>
            </div>
            <div className="qsofa-label">Machine Learning Sepsis Probability</div>
            <div className={`qsofa-risk ${mlRiskLevel}`}>
              {mlRiskLevel === "high" ? "🚨 " : mlRiskLevel === "moderate" ? "⚠️ " : "✅ "}
              {mlRiskLevel} risk
            </div>
            {recommendation && (
              <div style={{ marginTop: 15, padding: 10, background: 'var(--surface-color)', borderRadius: 8, fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                <strong>Recommendation:</strong> {recommendation}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
