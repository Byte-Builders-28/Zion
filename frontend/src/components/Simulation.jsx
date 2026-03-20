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

  const run = (v) => {
    setActive(v.id);
    setLogs(prev => [
      `[${new Date().toLocaleTimeString()}] INITIATING ${v.label}...`,
      `[${new Date().toLocaleTimeString()}] TARGET: /api/v1/  THREADS: 32`,
      `[${new Date().toLocaleTimeString()}] SIMULATION RUNNING — MONITORING RESPONSE`,
      ...prev
    ].slice(0, 20));
    setTimeout(() => {
      setLogs(prev => [
        `[${new Date().toLocaleTimeString()}] ✓ ${v.label} COMPLETE — 0 BYPASSES DETECTED`,
        ...prev
      ].slice(0, 20));
      setActive(null);
    }, 2000);
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
              logs.map((l, i) => (
                <div key={i} style={{ color: l.includes('✓') ? '#0f0' : 'rgba(0,255,0,0.6)' }}>{l}</div>
              ))
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
