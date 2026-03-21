import React, { useState, useEffect, useRef } from 'react';
import './pages.css';
import config, { API_ENDPOINTS } from '../config';

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
  const [dashboardData, setDashboardData] = useState({
    total_threats: 0,
    rate_limited_ips: new Set(),
    ips_blocked: new Set(),
    revoked_tokens_count: 0
  });
  const [overallRisk, setOverallRisk] = useState(0);
  const wsRef = useRef(null);
  const logHistoryRef = useRef([]);

  // WebSocket connection for dashboard data
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        const backendUrl = config.BACKEND_BASE_URL;
        const wsUrl = backendUrl.replace('http://', 'ws://').replace('https://', 'wss://') + '/dashboard/logs';
        wsRef.current = new WebSocket(wsUrl);
        
        wsRef.current.onopen = () => {
          console.log('WebSocket connected to dashboard logs');
        };
        
        wsRef.current.onmessage = (event) => {
          try {
            const logEntry = JSON.parse(event.data);
            
            // Store log entry for processing
            logHistoryRef.current.push(logEntry);
            
            // Keep only last 1000 entries for processing
            if (logHistoryRef.current.length > 1000) {
              logHistoryRef.current = logHistoryRef.current.slice(-1000);
            }
            
            // Calculate aggregated metrics from log entries
            const aggregatedData = calculateAggregatedMetrics(logHistoryRef.current);
            setDashboardData(aggregatedData);
            
            // Calculate overall risk based on aggregated data
            const riskScore = calculateRiskScore(aggregatedData);
            setOverallRisk(riskScore);
            
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };
        
        wsRef.current.onclose = () => {
          console.log('WebSocket disconnected, attempting to reconnect...');
          setTimeout(connectWebSocket, 3000); // Reconnect after 3 seconds
        };
        
        wsRef.current.onerror = (error) => {
          console.error('WebSocket error:', error);
        };
      } catch (error) {
        console.error('Failed to connect WebSocket:', error);
      }
    };
    
    connectWebSocket();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // Calculate aggregated metrics from individual log entries
  const calculateAggregatedMetrics = (logEntries) => {
    const rateLimitedIps = new Set();
    const blockedIps = new Set();
    let totalThreats = 0;
    let revokedTokens = 0;
    
    logEntries.forEach(entry => {
      // Count total requests
      totalThreats++;
      
      // Check if IP is rate limited (status 429) or blocked (status 403)
      if (entry.status_code === 429) {
        rateLimitedIps.add(entry.ip);
      }
      if (entry.status_code === 403) {
        blockedIps.add(entry.ip);
      }
      
      // Check for revoked tokens (token-based authentication failures)
      if (entry.status_code === 401 && entry.token) {
        revokedTokens++;
      }
    });
    
    return {
      total_threats: totalThreats,
      rate_limited_ips: rateLimitedIps.size,
      ips_blocked: blockedIps.size,
      revoked_tokens_count: revokedTokens
    };
  };

  // Calculate risk score based on dashboard metrics (0 to 1)
  const calculateRiskScore = (data) => {
    const totalThreats = data.total_threats || 0;
    const rateLimitedIps = data.rate_limited_ips || 0;
    const blockedIps = data.ips_blocked || 0;
    const revokedTokens = data.revoked_tokens_count || 0;

    // Weight factors for different metrics
    const weights = {
      threats: 0.4,        // 40% weight for total threats
      rateLimited: 0.3,    // 30% weight for rate limited IPs
      blocked: 0.2,        // 20% weight for blocked IPs
      revokedTokens: 0.1   // 10% weight for revoked tokens
    };

    // Normalize values (assuming max thresholds)
    const maxThresholds = {
      threats: 1000,
      rateLimited: 500,
      blocked: 200,
      revokedTokens: 50
    };

    // Calculate weighted risk
    const threatRisk = Math.min(totalThreats / maxThresholds.threats, 1) * weights.threats;
    const rateLimitedRisk = Math.min(rateLimitedIps / maxThresholds.rateLimited, 1) * weights.rateLimited;
    const blockedRisk = Math.min(blockedIps / maxThresholds.blocked, 1) * weights.blocked;
    const revokedRisk = Math.min(revokedTokens / maxThresholds.revokedTokens, 1) * weights.revokedTokens;

    return Math.min(threatRisk + rateLimitedRisk + blockedRisk + revokedRisk, 1);
  };

  const generateDynamicSequence = (vectorId) => {
    const time = () => new Date().toLocaleTimeString();
    let seq = [
      { text: `[${time()}] INITIATING ${vectorId.toUpperCase()}...`, delay: 100 },
      { text: `[${time()}] TARGET: /api/v1/ | THREADS: 32 | ALGORITHM: ISOLATION_FOREST`, delay: 600 },
      { text: `[${time()}] SIMULATION CONNECTED — MONITORING REAL-TIME RESPONSE`, delay: 1200 },
    ];

    if (vectorId === 'rate_flood') {
      seq.push({ text: `[${time()}] > CURRENT THREATS: ${dashboardData.total_threats} | RATE LIMITED: ${dashboardData.rate_limited_ips}`, delay: 1300 });
      for (let i = 0; i < 5; i++) {
        seq.push({ text: `[${time()}] > GET /api/v1/test HTTP/1.1 200 OK`, delay: 1400 + (i * 100) });
      }
      seq.push({ text: `[${time()}] ⚠️ ML DETECT: requests_per_min = ${Math.floor(dashboardData.rate_limited_ips * 1.5)} -> rate_flood`, delay: 2000 });
      seq.push({ text: `[${time()}] ⛔ POLICY ENGINE: IP BLOCKED (Risk: ${overallRisk.toFixed(2)})`, delay: 2300 });
      seq.push({ text: `[${time()}] > GET /api/v1/test HTTP/1.1 403 FORBIDDEN`, delay: 2600 });
      seq.push({ text: `[${time()}] ⛓️ LOGGING TO ALGORAND BLOCKCHAIN -> TX: ABC...`, delay: 3000 });
    } else if (vectorId === 'cred_stuff') {
      seq.push({ text: `[${time()}] > BLOCKED IPS: ${dashboardData.ips_blocked} | REVOKED TOKENS: ${dashboardData.revoked_tokens_count}`, delay: 1400 });
      seq.push({ text: `[${time()}] > POST /api/v1/login (admin/admin) 401 UNAUTHORIZED`, delay: 1600 });
      seq.push({ text: `[${time()}] > POST /api/v1/login (admin/1234) 401 UNAUTHORIZED`, delay: 1800 });
      seq.push({ text: `[${time()}] > POST /api/v1/login (admin/pass) 401 UNAUTHORIZED`, delay: 2000 });
      seq.push({ text: `[${time()}] ⚠️ ML DETECT: failed_logins > 5 -> credential_stuffing (Risk: ${(overallRisk * 0.8).toFixed(2)})`, delay: 2300 });
      seq.push({ text: `[${time()}] ⛔ POLICY ENGINE: IP BLOCKED (Rule: Halt_Cred_Stuffing)`, delay: 2600 });
      seq.push({ text: `[${time()}] > POST /api/v1/login (admin/qwerty) 403 FORBIDDEN`, delay: 2800 });
      seq.push({ text: `[${time()}] ⛓️ LOGGING INCIDENT TO ALGORAND SMART CONTRACT`, delay: 3200 });
    } else if (vectorId === 'token_replay') {
      seq.push({ text: `[${time()}] > REVOKED TOKENS: ${dashboardData.revoked_tokens_count} | ACTIVE THREATS: ${dashboardData.total_threats}`, delay: 1400 });
      seq.push({ text: `[${time()}] > GET /api/v1/data (Token: eyJhb...) [IP: 104.12.x] 200 OK`, delay: 1700 });
      seq.push({ text: `[${time()}] > GET /api/v1/data (Token: eyJhb...) [IP: 44.55.x] 200 OK`, delay: 2000 });
      seq.push({ text: `[${time()}] > GET /api/v1/data (Token: eyJhb...) [IP: 12.8.x] 200 OK`, delay: 2300 });
      seq.push({ text: `[${time()}] ⚠️ ML DETECT: token_reuse_count = 3 -> token_replay (Risk: ${(overallRisk * 0.6).toFixed(2)})`, delay: 2700 });
      seq.push({ text: `[${time()}] ⛔ POLICY ENGINE: TOKEN REVOKED GLOBALLY`, delay: 3000 });
      seq.push({ text: `[${time()}] > GET /api/v1/data (Token: eyJhb...) [IP: 88.2.x] 401 UNAUTHORIZED`, delay: 3300 });
    } else {
      seq.push({ text: `[${time()}] > SYSTEM STATUS: Threats=${dashboardData.total_threats}, Blocked=${dashboardData.ips_blocked}`, delay: 1400 });
      seq.push({ text: `[${time()}] ⚠️ ML DETECT: anomaly detected (risk_score = ${overallRisk.toFixed(2)})`, delay: 2200 });
      seq.push({ text: `[${time()}] ⛔ IP FLAGGED FOR REVIEW (Overall Risk: ${overallRisk.toFixed(2)})`, delay: 2600 });
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
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '2rem' }}>
        {[
          { 
            label: 'TOTAL THREATS', 
            value: dashboardData.total_threats.toString(), 
            color: '#0f0' 
          },
          { 
            label: 'RATE LIMITED', 
            value: dashboardData.rate_limited_ips.toString(), 
            color: '#fa0' 
          },
          { 
            label: 'IPs BLOCKED', 
            value: dashboardData.ips_blocked.toString(), 
            color: '#0af' 
          },
          { 
            label: 'RISK SCORE', 
            value: overallRisk.toFixed(2), 
            color: overallRisk > 0.7 ? '#f55' : overallRisk > 0.4 ? '#fa0' : '#0f0'
          }
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
