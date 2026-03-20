import React, { useState } from 'react';
import './pages.css';

const incidents = [
  { ts: '2026-03-20 18:42:01', type: 'token_replay',   ip: '192.168.1.45', target: '/api/v1/login',  risk: 'CRITICAL' },
  { ts: '2026-03-20 18:40:17', type: 'rate_flood',      ip: '10.0.0.82',    target: '/api/v1/user',   risk: 'HIGH' },
  { ts: '2026-03-20 18:38:53', type: 'sql_injection',   ip: '203.0.113.7',  target: '/api/products',  risk: 'HIGH' },
  { ts: '2026-03-20 18:35:22', type: 'cred_stuffing',   ip: '198.51.100.1', target: '/api/v1/auth',   risk: 'CRITICAL' },
  { ts: '2026-03-20 18:31:05', type: 'unusual_geo',     ip: '91.108.4.20',  target: '/dashboard',     risk: 'MED' },
  { ts: '2026-03-20 18:28:49', type: 'xss_probe',       ip: '172.16.0.3',   target: '/api/search',    risk: 'MED' },
  { ts: '2026-03-20 18:22:14', type: 'ddos_attempt',    ip: '104.21.1.1',   target: '/*',             risk: 'CRITICAL' },
  { ts: '2026-03-20 18:18:01', type: 'token_replay',    ip: '192.168.5.11', target: '/api/v1/session', risk: 'HIGH' },
];

const riskClass = r =>
  r === 'CRITICAL' ? 'badge-red' : r === 'HIGH' ? 'badge-yellow' : 'badge-blue';

const Threats = () => {
  const [filter, setFilter] = useState('ALL');

  const filters = ['ALL', 'CRITICAL', 'HIGH', 'MED'];
  const shown = filter === 'ALL' ? incidents : incidents.filter(i => i.risk === filter);

  return (
    <div className="pop-in" style={{ padding: '2rem', maxWidth: '1300px', margin: '0 auto' }}>
      <h2 className="page-title">// INCIDENT LOG & THREAT INTELLIGENCE</h2>

      {/* Summary mini stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '2rem' }}>
        {[
          { label: 'TOTAL INCIDENTS', value: incidents.length.toString(), color: '#0f0' },
          { label: 'CRITICAL',  value: incidents.filter(i => i.risk === 'CRITICAL').length.toString(), color: '#f55' },
          { label: 'HIGH',      value: incidents.filter(i => i.risk === 'HIGH').length.toString(),     color: '#ff0' },
          { label: 'MEDIUM',    value: incidents.filter(i => i.risk === 'MED').length.toString(),      color: '#0af' },
        ].map((s, i) => (
          <div key={i} className="mini-stat" style={{ color: s.color }}>
            <div className="mini-stat-value">{s.value}</div>
            <div className="mini-stat-label">{s.label}</div>
          </div>
        ))}
      </div>

      {/* Filter tabs */}
      <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.25rem' }}>
        {filters.map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            style={{
              background: filter === f ? 'rgba(0,255,0,0.12)' : 'transparent',
              border: `1px solid ${filter === f ? 'rgba(0,255,0,0.6)' : 'rgba(0,255,0,0.2)'}`,
              color: filter === f ? '#0f0' : 'rgba(0,255,0,0.5)',
              fontFamily: 'Share Tech Mono',
              fontSize: '0.7rem',
              letterSpacing: '2px',
              padding: '0.4rem 1rem',
              borderRadius: '6px',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Incident table */}
      <div className="glass-panel">
        <div className="panel-title">INCIDENT LOG — {shown.length} RECORDS</div>
        <div style={{ overflowX: 'auto' }}>
          <table className="cyber-table">
            <thead>
              <tr>
                <th>TIMESTAMP</th>
                <th>TYPE</th>
                <th>SOURCE IP</th>
                <th>TARGET</th>
                <th>RISK</th>
              </tr>
            </thead>
            <tbody>
              {shown.map((inc, i) => (
                <tr key={i}>
                  <td style={{ color: 'rgba(0,255,0,0.45)', whiteSpace: 'nowrap' }}>{inc.ts}</td>
                  <td style={{ color: '#0f0' }}>{inc.type}</td>
                  <td style={{ color: 'rgba(0,255,0,0.65)' }}>{inc.ip}</td>
                  <td style={{ color: 'rgba(0,255,0,0.55)' }}>{inc.target}</td>
                  <td><span className={`badge ${riskClass(inc.risk)}`}>{inc.risk}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Threats;
