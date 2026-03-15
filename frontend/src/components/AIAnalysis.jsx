export default function AIAnalysis({ explanation, loading }) {
  if (loading) {
    return (
      <div className="card">
        <div className="card-header">
          <div className="icon" style={{ background: "rgba(6,182,212,0.15)", color: "var(--accent-cyan)" }}>🤖</div>
          <h2>AI Clinical Analysis</h2>
          <span className="badge" style={{ background: "rgba(6,182,212,0.15)", color: "var(--accent-cyan)" }}>Gemini AI</span>
        </div>
        <div className="ai-panel" style={{ textAlign: "center", padding: 40 }}>
          <div style={{ fontSize: 32, marginBottom: 16 }}>🧠</div>
          <p style={{ marginBottom: 12 }}>Analyzing vitals with Gemini AI...</p>
          <div className="ai-typing">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>
    );
  }

  if (!explanation) {
    return (
      <div className="card">
        <div className="card-header">
          <div className="icon" style={{ background: "rgba(6,182,212,0.15)", color: "var(--accent-cyan)" }}>🤖</div>
          <h2>AI Clinical Analysis</h2>
          <span className="badge" style={{ background: "rgba(6,182,212,0.15)", color: "var(--accent-cyan)" }}>Gemini AI</span>
        </div>
        <div className="empty-state">
          <div className="icon">🧠</div>
          <h3>Waiting for Vitals</h3>
          <p>Submit vitals to get an AI-powered clinical explanation</p>
        </div>
      </div>
    );
  }

  // Simple markdown-like renderer for Gemini output
  function renderMarkdown(text) {
    const lines = text.split("\n");
    const elements = [];
    let inList = false;
    let listItems = [];

    function flushList() {
      if (listItems.length > 0) {
        elements.push(<ul key={`list-${elements.length}`}>{listItems}</ul>);
        listItems = [];
        inList = false;
      }
    }

    lines.forEach((line, i) => {
      const trimmed = line.trim();

      if (trimmed.startsWith("### ")) {
        flushList();
        elements.push(<h3 key={i}>{trimmed.slice(4)}</h3>);
      } else if (trimmed.startsWith("## ")) {
        flushList();
        elements.push(<h3 key={i}>{trimmed.slice(3)}</h3>);
      } else if (trimmed.startsWith("# ")) {
        flushList();
        elements.push(<h3 key={i}>{trimmed.slice(2)}</h3>);
      } else if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
        inList = true;
        const content = trimmed.slice(2).replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
        listItems.push(<li key={i} dangerouslySetInnerHTML={{ __html: content }} />);
      } else if (trimmed === "") {
        flushList();
      } else {
        flushList();
        const content = trimmed.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
        elements.push(<p key={i} dangerouslySetInnerHTML={{ __html: content }} />);
      }
    });
    flushList();

    return elements;
  }

  return (
    <div className="card">
      <div className="card-header">
        <div className="icon" style={{ background: "rgba(6,182,212,0.15)", color: "var(--accent-cyan)" }}>🤖</div>
        <h2>AI Clinical Analysis</h2>
        <span className="badge" style={{ background: "rgba(16,185,129,0.15)", color: "var(--accent-green)" }}>✓ Complete</span>
      </div>
      <div className="ai-panel" style={{ animation: "fadeIn 0.5s ease" }}>
        {renderMarkdown(explanation)}
      </div>
    </div>
  );
}
