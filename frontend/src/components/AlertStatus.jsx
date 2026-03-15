export default function AlertStatus({ alertSent, alertDetails }) {
  if (!alertSent && (!alertDetails || alertDetails.length === 0)) {
    return null;
  }

  return (
    <div>
      {alertSent && (
        <div className="alert-banner danger">
          <span style={{ fontSize: 20 }}>📧</span>
          <div>
            <strong>Emergency Alert Sent!</strong>
            <span style={{ opacity: 0.8, marginLeft: 8 }}>
              Email notifications sent to {alertDetails?.length || 0} emergency contact(s)
            </span>
          </div>
        </div>
      )}

      {alertDetails && alertDetails.length > 0 && (
        <div className="card" style={{ marginTop: 12 }}>
          <div className="card-header">
            <div className="icon" style={{ background: "rgba(239,68,68,0.15)", color: "var(--accent-red)" }}>🚨</div>
            <h2>Alert History</h2>
          </div>
          {alertDetails.map((alert, i) => (
            <div key={alert.id || i} className="alert-item">
              <span className="alert-icon">{alert.success ? "✅" : "❌"}</span>
              <div className="alert-info">
                <div>
                  <strong>{alert.contact_name}</strong> — {alert.contact_email}
                </div>
                <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 2 }}>
                  {alert.message}
                </div>
              </div>
              <div className="alert-time">
                {new Date(alert.sent_at).toLocaleTimeString()}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
