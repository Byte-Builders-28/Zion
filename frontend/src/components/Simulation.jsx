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
  const [terminalLogs, setTerminalLogs] = useState([]);
  const [dashboardData, setDashboardData] = useState({
    total_threats: 0,
    rate_limited_ips: 0,
    ips_blocked: 0,
    revoked_tokens_count: 0
  });
  const [overallRisk, setOverallRisk] = useState(0);
  const wsRef = useRef(null);

  // HTTP GET to dashboard/stats as default method
  useEffect(() => {
    const fetchDashboardStats = async () => {
      try {
        const backendUrl = config.BACKEND_BASE_URL;
        const response = await fetch(`${backendUrl}/dashboard/stats`);
        if (response.ok) {
          const data = await response.json();
          setDashboardData(data);
          
          // Calculate overall risk based on received data
          const riskScore = calculateRiskScore(data);
          setOverallRisk(riskScore);
        }
      } catch (error) {
        console.error('Failed to fetch dashboard stats:', error);
      }
    };

    fetchDashboardStats();
    // Refresh every 5 seconds
    const interval = setInterval(fetchDashboardStats, 5000);
    return () => clearInterval(interval);
  }, []);

  // Terminal WebSocket connection
  const connectTerminalWebSocket = (attackType) => {
    try {
      const backendUrl = config.BACKEND_BASE_URL;
      const wsUrl = backendUrl.replace('http://', 'ws://').replace('https://', 'wss://') + '/dashboard/logs';
      wsRef.current = new WebSocket(wsUrl);
      
      wsRef.current.onopen = () => {
        console.log('Terminal WebSocket connected');
        setTerminalLogs([`[${new Date().toLocaleTimeString()}] CONNECTED TO TERMINAL - DOING ${attackType.toUpperCase()} SIMULATION`]);
      };
      
      wsRef.current.onmessage = (event) => {
        try {
          const logEntry = JSON.parse(event.data);
          
          // Format log entry for terminal display (same as dashboard)
          const formattedLog = `${logEntry.method}    ${logEntry.ip}    ${logEntry.status}    [${logEntry.score_result?.threat_type || 'normal'}]`;
          setTerminalLogs(prevLogs => [formattedLog, ...prevLogs].slice(0, 50));
          
        } catch (error) {
          console.error('Error parsing terminal WebSocket message:', error);
        }
      };
      
      wsRef.current.onclose = () => {
        console.log('Terminal WebSocket disconnected');
        setTerminalLogs(prevLogs => [...prevLogs, `[${new Date().toLocaleTimeString()}] TERMINAL DISCONNECTED`]);
      };
      
      wsRef.current.onerror = (error) => {
        console.error('Terminal WebSocket error:', error);
        setTerminalLogs(prevLogs => [...prevLogs, `[${new Date().toLocaleTimeString()}] TERMINAL ERROR`]);
      };
    } catch (error) {
      console.error('Failed to connect terminal WebSocket:', error);
      setTerminalLogs([`[${new Date().toLocaleTimeString()}] FAILED TO CONNECT TO TERMINAL`]);
    }
  };

  // Call simulation API endpoints
  const callSimulationAPI = async (vectorId) => {
    try {
      const backendUrl = config.BACKEND_BASE_URL;
      let endpoint = '';
      
      // Map vector IDs to API endpoints
      switch (vectorId) {
        case 'ddos':
          endpoint = '/simulate/ddos';
          break;
        case 'cred_stuff':
          endpoint = '/simulate/credit';
          break;
        case 'token_replay':
          endpoint = '/simulate/token';
          break;
        case 'sql_inject':
          endpoint = '/simulate/param';
          break;
        case 'xpath':
          endpoint = '/simulate/endpoint';
          break;
        default:
          endpoint = '/simulate/ddos';
      }
      
      const response = await fetch(`${backendUrl}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          target: 'http://127.0.0.1:8000/test'
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        setTerminalLogs(prevLogs => [...prevLogs, `[${new Date().toLocaleTimeString()}] ✓ SIMULATION EXECUTED: ${result.msg}`]);
      } else {
        setTerminalLogs(prevLogs => [...prevLogs, `[${new Date().toLocaleTimeString()}] ⚠️ SIMULATION FAILED: HTTP ${response.status}`]);
      }
    } catch (error) {
      console.error('Failed to call simulation API:', error);
      setTerminalLogs(prevLogs => [...prevLogs, `[${new Date().toLocaleTimeString()}] ⛔ API ERROR: ${error.message}`]);
    }
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
    
    // Connect to WebSocket for real-time logs
    connectTerminalWebSocket(v.id);
    
    // Call the simulation API to trigger the attack
    callSimulationAPI(v.id);
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

        {/* Simulation console */}
        <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', marginTop: '1.5rem' }}>
          <div className="panel-title">SIMULATION CONSOLE</div>
          <div style={{ fontFamily: 'Share Tech Mono', fontSize: '0.72rem', display: 'flex', flexDirection: 'column', gap: '0.3rem', overflowY: 'auto', flex: 1, maxHeight: '320px' }}>
            {terminalLogs.length === 0 ? (
              <span style={{ color: 'rgba(0,255,0,0.3)', marginTop: '1rem' }}>{'>'} SELECT A VECTOR TO BEGIN SIMULATION...</span>
            ) : (
              terminalLogs.map((log, i) => {
                let color = 'rgba(0, 255, 0, 0.6)'; // default green
                if (log.includes('CONNECTED')) color = '#0f0';
                if (log.includes('DISCONNECTED')) color = '#fa0';
                if (log.includes('ERROR')) color = '#f55';
                if (log.includes('POST') || log.includes('GET')) color = 'rgba(255, 255, 255, 0.7)';
                return <div key={i} style={{ color }}>{log}</div>;
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
