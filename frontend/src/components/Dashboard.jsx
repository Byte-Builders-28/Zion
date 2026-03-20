import React from 'react';
import './pages.css';

const Dashboard = () => {
  const stats = [
    { value: '1,284', label: 'THREATS DETECTED', color: '#0f0' },
    { value: '12',    label: 'CRITICAL ACTIVE',  color: '#f55' },
    { value: '0.14',  label: 'AVG RISK SCORE',   color: '#ff0' },
    { value: '42',    label: 'IPs BLOCKED',       color: '#0af' }
  ];

  const threats = [
    { type: 'token_replay',  path: '/login',       risk: '0.96', level: 'CRITICAL' },
    { type: 'rate_limit',    path: '/api/v1/user', risk: '0.72', level: 'HIGH' },
    { type: 'brute_force',   path: '/auth',        risk: '0.88', level: 'CRITICAL' },
    { type: 'unusual_geo',   path: '/dashboard',   risk: '0.45', level: 'MED' }
  ];

  const attacks = [
    { name: 'SQL Injection',        pct: 65, cls: '' },
    { name: 'Cross-Site Scripting', pct: 48, cls: '' },
    { name: 'DDoS Attempt',         pct: 33, cls: 'prog-fill-red' },
    { name: 'Brute Force',          pct: 24, cls: 'prog-fill-blue' }
  ];

  const levelClass = l =>
    l === 'CRITICAL' ? 'badge-red' : l === 'HIGH' ? 'badge-yellow' : 'badge-blue';

  return (
    <div className="pop-in" style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
      <h2 className="page-title">// ZION COMMAND CENTER — REAL-TIME THREAT OVERVIEW</h2>

      {/* ── Stat Cards ── */}
      <div className="dashboard-stat-grid">
        {stats.map((s, i) => (
          <div key={i} className="dashboard-stat-card scan-edge">
            <div className="stat-value" style={{ color: s.color }}>{s.value}</div>
            <div className="stat-label"  style={{ color: s.color }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* ── Main two-column grid ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>

        {/* Left */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

          <div className="glass-panel" style={{ minHeight: '210px' }}>
            <div className="panel-title">LIVE TRAFFIC — REQUESTS / MIN</div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '130px' }}>
              <span style={{ fontFamily: 'Share Tech Mono', fontSize: '0.78rem', color: 'rgba(0,255,0,0.35)', letterSpacing: '2px' }}>
                [ SYSTEM ANALYZING TRAFFIC DATA... ]
              </span>
            </div>
          </div>

          <div className="glass-panel">
            <div className="panel-title">ATTACK TYPE BREAKDOWN</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {attacks.map((a, i) => (
                <div key={i}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontFamily: 'Share Tech Mono', fontSize: '0.72rem', color: 'rgba(0,255,0,0.7)', marginBottom: '4px' }}>
                    <span>{a.name}</span><span>{a.pct}%</span>
                  </div>
                  <div className="prog-track">
                    <div className={`prog-fill ${a.cls}`} style={{ width: `${a.pct}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

          <div className="glass-panel" style={{ minHeight: '210px' }}>
            <div className="panel-title">ACTIVE THREAT FEED</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.55rem', overflowY: 'auto', maxHeight: '150px' }}>
              {threats.map((t, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(0,255,0,0.06)', paddingBottom: '0.45rem', fontFamily: 'Share Tech Mono', fontSize: '0.73rem' }}>
                  <span style={{ color: '#0f0', width: '110px', flexShrink: 0 }}>{t.type}</span>
                  <span style={{ color: 'rgba(0,255,0,0.45)', flex: 1, padding: '0 0.5rem' }}>{t.path}</span>
                  <span className={`badge ${levelClass(t.level)}`}>{t.level} {t.risk}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="glass-panel">
            <div className="panel-title">SYSTEM LOG</div>
            <div style={{ fontFamily: 'Share Tech Mono', fontSize: '0.7rem', display: 'flex', flexDirection: 'column', gap: '0.35rem', color: 'rgba(0,255,0,0.55)' }}>
              {[
                '[00:00:01] INITIALIZING ZION CORE...',
                '[00:00:02] DEFENSE LAYERS ARMED',
                '[00:00:04] ML-MODEL: ISOLATION FOREST LOADED',
                '[00:00:05] MONITORING TRAFFIC ON PORT 80/443',
              ].map((l, i) => <div key={i}>{l}</div>)}
              <div style={{ color: '#0f0', marginTop: '4px' }}>▌ SYSTEM STANDBY...</div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default Dashboard;
