import { useState } from "react";

const VITAL_FIELDS = [
  { key: "heart_rate",       label: "Heart Rate",       unit: "bpm",         min: 20,  max: 250, step: 1,   defaultVal: 80  },
  { key: "spo2",             label: "Blood Oxygen",     unit: "%",           min: 50,  max: 100, step: 1,   defaultVal: 98  },
  { key: "temperature_f",    label: "Temperature",      unit: "°F",          min: 90,  max: 110, step: 0.1, defaultVal: 98.6 },
  { key: "respiratory_rate", label: "Respiratory Rate",  unit: "breaths/min", min: 4,   max: 50,  step: 1,   defaultVal: 16  },
  { key: "systolic_bp",      label: "Systolic BP",      unit: "mmHg",        min: 40,  max: 300, step: 1,   defaultVal: 120 },
  { key: "gcs_score",        label: "GCS Score",        unit: "/ 15",        min: 3,   max: 15,  step: 1,   defaultVal: 15  },
];

export default function VitalsForm({ onSubmit, loading }) {
  const [vitals, setVitals] = useState(
    Object.fromEntries(VITAL_FIELDS.map(f => [f.key, f.defaultVal]))
  );

  function update(key, value) {
    setVitals(prev => ({ ...prev, [key]: parseFloat(value) || 0 }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    onSubmit(vitals);
  }

  function setDangerPreset() {
    setVitals({
      heart_rate: 115,
      spo2: 88,
      temperature_f: 102.5,
      respiratory_rate: 28,
      systolic_bp: 85,
      gcs_score: 12,
    });
  }

  function setNormalPreset() {
    setVitals(Object.fromEntries(VITAL_FIELDS.map(f => [f.key, f.defaultVal])));
  }

  return (
    <div className="card">
      <div className="card-header">
        <div className="icon" style={{ background: "rgba(6,182,212,0.15)", color: "var(--accent-cyan)" }}>📊</div>
        <h2>Enter Vitals</h2>
        <div style={{ marginLeft: "auto", display: "flex", gap: 6 }}>
          <button type="button" className="btn btn-ghost" onClick={setNormalPreset} style={{ padding: "4px 10px", fontSize: 11 }}>
            ✅ Normal
          </button>
          <button type="button" className="btn btn-ghost" onClick={setDangerPreset} style={{ padding: "4px 10px", fontSize: 11, color: "var(--accent-red)", borderColor: "rgba(239,68,68,0.3)" }}>
            🚨 Danger
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="grid-vitals">
          {VITAL_FIELDS.map(f => (
            <div key={f.key} className="form-group">
              <label>{f.label}</label>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <input
                  id={`vital-${f.key}`}
                  type="number"
                  min={f.min}
                  max={f.max}
                  step={f.step}
                  value={vitals[f.key]}
                  onChange={e => update(f.key, e.target.value)}
                  required
                />
                <span style={{ fontSize: 12, color: "var(--text-muted)", whiteSpace: "nowrap" }}>{f.unit}</span>
              </div>
            </div>
          ))}
        </div>

        <button
          id="submit-vitals-btn"
          type="submit"
          className="btn btn-primary btn-full"
          disabled={loading}
          style={{ marginTop: 16 }}
        >
          {loading ? (
            <><span className="spinner"></span>Analyzing with AI...</>
          ) : (
            "🧠 Analyze Vitals"
          )}
        </button>
      </form>
    </div>
  );
}
