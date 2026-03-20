import React, { useState } from 'react';
import './pages.css';

const Policies = () => {
  const [rules, setRules] = useState([
    { id: 1, name: 'MAX_REQUESTS_PER_MIN', value: '60',   category: 'RATE LIMITING' },
    { id: 2, name: 'BURST_WINDOW_SECONDS', value: '10',   category: 'RATE LIMITING' },
    { id: 3, name: 'IP_BLOCK_DURATION_MIN', value: '30',  category: 'RATE LIMITING' },
  ]);

  const [toggles, setToggles] = useState([
    { id: 1, name: 'Block Tor Exit Nodes',        desc: 'Deny requests from Tor network IPs',            on: true  },
    { id: 2, name: 'Block Known Malicious IPs',   desc: 'Match against threat intelligence feed',       on: true  },
    { id: 3, name: 'Block Non-Domestic Traffic',  desc: 'Restrict to domestic IP ranges only',          on: false },
    { id: 4, name: 'Force HTTPS Redirect',        desc: 'Redirect all HTTP traffic to HTTPS',           on: true  },
    { id: 5, name: 'Enable HSTS Headers',         desc: 'Strict-Transport-Security enforcement',        on: true  },
    { id: 6, name: 'Mutable Request Logging',     desc: 'Log full request body for forensic analysis',  on: false },
  ]);

  const flip = (id) => setToggles(t => t.map(r => r.id === id ? { ...r, on: !r.on } : r));

  return (
    <div className="pop-in" style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <h2 className="page-title">// SECURITY POLICIES — DATA PROTECTION PROTOCOLS</h2>

      {/* Summary */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '2rem' }}>
        {[
          { label: 'ACTIVE RULES',    value: toggles.filter(t => t.on).length.toString(),  color: '#0f0' },
          { label: 'DISABLED RULES',  value: toggles.filter(t => !t.on).length.toString(), color: '#f55' },
          { label: 'RATE CONFIGS',    value: rules.length.toString(),                       color: '#0af' },
        ].map((s, i) => (
          <div key={i} className="mini-stat" style={{ color: s.color }}>
            <div className="mini-stat-value">{s.value}</div>
            <div className="mini-stat-label">{s.label}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>

        {/* Blocking Rules */}
        <div className="glass-panel">
          <div className="panel-title">BLOCKING & SECURITY RULES</div>
          <div>
            {toggles.map(t => (
              <div key={t.id} className="policy-row">
                <div style={{ flex: 1 }}>
                  <div>{t.name}</div>
                  <div className="policy-desc">{t.desc}</div>
                </div>
                <div
                  className={`toggle ${t.on ? 'toggle-on' : 'toggle-off'}`}
                  onClick={() => flip(t.id)}
                  title={t.on ? 'ENABLED – click to disable' : 'DISABLED – click to enable'}
                />
              </div>
            ))}
          </div>
        </div>

        {/* Rate Limiting + Log */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

          <div className="glass-panel">
            <div className="panel-title">RATE LIMITING CONFIGURATION</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {rules.map(r => (
                <div key={r.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontFamily: 'Share Tech Mono', fontSize: '0.75rem', color: 'rgba(0,255,0,0.75)' }}>
                  <span>{r.name}</span>
                  <span style={{
                    background: 'rgba(0,255,0,0.08)',
                    border: '1px solid rgba(0,255,0,0.25)',
                    borderRadius: '4px',
                    padding: '3px 14px',
                    color: '#0f0',
                    fontFamily: 'Orbitron, sans-serif',
                    fontSize: '0.85rem'
                  }}>{r.value}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="glass-panel">
            <div className="panel-title">POLICY AUDIT LOG</div>
            <div style={{ fontFamily: 'Share Tech Mono', fontSize: '0.68rem', display: 'flex', flexDirection: 'column', gap: '0.35rem', color: 'rgba(0,255,0,0.5)' }}>
              <div>[18:42] Policy update: Tor block ENABLED</div>
              <div>[18:30] Policy update: HSTS ACTIVATED</div>
              <div>[17:55] Rate limit changed: 100 → 60 req/min</div>
              <div>[17:22] New IP blocked: 104.21.1.1</div>
              <div style={{ color: '#0f0', marginTop: '4px' }}>▌ NO UNAUTHORIZED CHANGES DETECTED</div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default Policies;
