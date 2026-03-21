import React, { useState } from 'react';
import './pages.css';

const vectors = [
  { id: 'rate_flood',   label: 'RATE FLOOD',         icon: '🌊', desc: 'Flood API endpoints with high-speed repeated requests', cls: 'blue' },
  { id: 'token_replay', label: 'TOKEN REPLAY',        icon: '🔁', desc: 'Reuse captured JWT/session tokens to hijack sessions', cls: '' },
  { id: 'cred_stuff',  label: 'CREDENTIAL STUFFING', icon: '🔑', desc: 'Use leaked credential lists to attempt account takeover', cls: 'red' },
  { id: 'sql_inject',  label: 'SQL INJECTION',        icon: '💉', desc: 'Probe endpoints for SQL injection vulnerabilities', cls: 'yellow' },
  { id: 'ddos',        label: 'DDoS SIM',             icon: '💥', desc: 'Distributed denial-of-service attack simulation', cls: 'red' },
  { id: 'xpath',       label: 'XPATH PROBE',          icon: '🔍', desc: 'Test for XPath injection via query parameters', cls: 'blue' },
];

const Simulation = () => {
  const [active, setActive] = useState(null);
  const [logs, setLogs] = useState([]);

  const generateDynamicSequence = (vectorId) => {
    const time = () => new Date().toLocaleTimeString();
    let seq = [
      { text: `[${time()}] INITIATING ${vectorId.toUpperCase()}...`, delay: 100 },
      { text: `[${time()}] TARGET: /api/v1/ | THREADS: 32 | ALGORITHM: ISOLATION_FOREST`, delay: 600 },
      { text: `[${time()}] SIMULATION CONNECTED — MONITORING REAL-TIME RESPONSE`, delay: 1200 },
    ];

    if (vectorId === 'rate_flood') {
      for (let i = 0; i < 5; i++) {
        seq.push({ text: `[${time()}] > GET /api/v1/test HTTP/1.1 200 OK`, delay: 1300 + (i * 100) });
      }
      seq.push({ text: `[${time()}] ⚠️ ML DETECT: requests_per_min = 180 -> rate_flood`, delay: 1900 });
      seq.push({ text: `[${time()}] ⛔ POLICY ENGINE: IP BLOCKED (Rule: Block_Rate_Flood)`, delay: 2200 });
      seq.push({ text: `[${time()}] > GET /api/v1/test HTTP/1.1 403 FORBIDDEN`, delay: 2500 });
      seq.push({ text: `[${time()}] ⛓️ LOGGING TO ALGORAND BLOCKCHAIN -> TX: ABC...`, delay: 3000 });
    } else if (vectorId === 'cred_stuff') {
      seq.push({ text: `[${time()}] > POST /api/v1/login (admin/admin) 401 UNAUTHORIZED`, delay: 1400 });
      seq.push({ text: `[${time()}] > POST /api/v1/login (admin/1234) 401 UNAUTHORIZED`, delay: 1600 });
      seq.push({ text: `[${time()}] > POST /api/v1/login (admin/pass) 401 UNAUTHORIZED`, delay: 1800 });
      seq.push({ text: `[${time()}] ⚠️ ML DETECT: failed_logins > 5 -> credential_stuffing`, delay: 2100 });
      seq.push({ text: `[${time()}] ⛔ POLICY ENGINE: IP BLOCKED (Rule: Halt_Cred_Stuffing)`, delay: 2400 });
      seq.push({ text: `[${time()}] > POST /api/v1/login (admin/qwerty) 403 FORBIDDEN`, delay: 2600 });
      seq.push({ text: `[${time()}] ⛓️ LOGGING INCIDENT TO ALGORAND SMART CONTRACT`, delay: 3200 });
    } else if (vectorId === 'token_replay') {
      seq.push({ text: `[${time()}] > GET /api/v1/data (Token: eyJhb...) [IP: 104.12.x] 200 OK`, delay: 1400 });
      seq.push({ text: `[${time()}] > GET /api/v1/data (Token: eyJhb...) [IP: 44.55.x] 200 OK`, delay: 1700 });
      seq.push({ text: `[${time()}] > GET /api/v1/data (Token: eyJhb...) [IP: 12.8.x] 200 OK`, delay: 2000 });
      seq.push({ text: `[${time()}] ⚠️ ML DETECT: token_reuse_count = 3 -> token_replay`, delay: 2400 });
      seq.push({ text: `[${time()}] ⛔ POLICY ENGINE: TOKEN REVOKED GLOBALLY`, delay: 2700 });
      seq.push({ text: `[${time()}] > GET /api/v1/data (Token: eyJhb...) [IP: 88.2.x] 401 UNAUTHORIZED`, delay: 3000 });
    } else {
      seq.push({ text: `[${time()}] > PROBING VULNERABILITY VECTORS...`, delay: 1400 });
      seq.push({ text: `[${time()}] ⚠️ ML DETECT: anomaly detected (risk_score = 0.85)`, delay: 2200 });
      seq.push({ text: `[${time()}] ⛔ IP FLAGGED FOR REVIEW`, delay: 2600 });
    }

    seq.push({ text: `[${time()}] ✓ SIMULATION COMPLETE — ZERO BYPASSES DETECTED`, delay: 4000 });
    return seq;
  };

  const run = (v) => {
    if (active) return;
    setActive(v.id);
    setLogs([]); // Clear logs for new run

    const sequence = generateDynamicSequence(v.id);
    
    sequence.forEach((item) => {
      setTimeout(() => {
        setLogs((prev) => {
          // Keep last 50 logs instead of 20 to prevent cutting off the simulation mid-way
          const next = [item.text, ...prev];
          return next.slice(0, 50);
        });
        
        // Finish condition
        if (item.text.includes('✓')) {
          setActive(null);
        }
      }, item.delay);
    });
  };

  return (
    <div className="pop-in" style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <h2 className="page-title">// ATTACK SIMULATION — VULNERABILITY ASSESSMENT</h2>

      {/* Mini stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '2rem' }}>
        {[
          { label: 'SIMULATIONS RUN', value: '847', color: '#0f0' },
          { label: 'BYPASSES FOUND',  value: '0',   color: '#0af' },
          { label: 'LAST RUN',        value: '2m AGO', color: '#ff0' }
        ].map((s, i) => (
          <div key={i} className="mini-stat" style={{ color: s.color }}>
            <div className="mini-stat-value">{s.value}</div>
            <div className="mini-stat-label">{s.label}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>

        {/* Attack vector grid */}
        <div className="glass-panel">
          <div className="panel-title">SELECT ATTACK VECTOR</div>
          <div className="sim-grid">
            {vectors.map(v => (
              <button
                key={v.id}
                className={`sim-btn ${v.cls}`}
                onClick={() => run(v)}
                disabled={active !== null}
                style={{ opacity: active && active !== v.id ? 0.5 : 1 }}
              >
                <span className="sim-icon">{active === v.id ? '⚡' : v.icon}</span>
                {v.label}
                <span className="sim-label">{active === v.id ? 'RUNNING...' : v.desc.slice(0, 30) + '…'}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Live log */}
        <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column' }}>
          <div className="panel-title">SIMULATION CONSOLE</div>
          <div style={{ fontFamily: 'Share Tech Mono', fontSize: '0.72rem', display: 'flex', flexDirection: 'column', gap: '0.3rem', overflowY: 'auto', flex: 1, maxHeight: '320px' }}>
            {logs.length === 0 ? (
              <span style={{ color: 'rgba(0,255,0,0.3)', marginTop: '1rem' }}>{'>'} SELECT A VECTOR TO BEGIN SIMULATION...</span>
            ) : (
              logs.map((l, i) => {
                let color = 'rgba(0, 255, 0, 0.6)'; // default green
                if (l.includes('✓')) color = '#0f0';
                if (l.includes('⚠️')) color = '#ffeb3b';
                if (l.includes('⛔')) color = '#f44336';
                if (l.includes('⛓️')) color = '#00bcd4';
                if (l.includes('>')) color = 'rgba(255, 255, 255, 0.7)';
                return <div key={i} style={{ color }}>{l}</div>;
              })
            )}
          </div>
          {active && (
            <div style={{ marginTop: '1rem', height: '3px', background: 'rgba(0,255,0,0.1)', borderRadius: '2px', overflow: 'hidden' }}>
              <div style={{ height: '100%', background: 'linear-gradient(90deg, #0f0, #0af)', animation: 'scanEdge 1.5s linear infinite', width: '40%' }} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Simulation;
