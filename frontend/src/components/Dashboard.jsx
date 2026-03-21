import React, { useState, useEffect, useRef } from 'react';
import './pages.css';
import './Dashboard.css';
import config, { API_ENDPOINTS } from '../config';

const Dashboard = () => {
  // Get backend URL from environment or use default
  const backendUrl = config.BACKEND_BASE_URL;
  const [logs, setLogs] = useState([]);
  const wsRef = useRef(null);
  
  const [stats, setStats] = useState([
    { value: '1,284', label: 'THREATS DETECTED', color: '#0f0', key: 'total_threats' },
    { value: '156',    label: 'RATE LIMITED IPS',  color: '#fa0', key: 'rate_limited_ips' },
    { value: '42',     label: 'IPs BLOCKED',       color: '#0af', key: 'ips_blocked' },
    { value: '8',       label: 'REVOKED TOKEN COUNT', color: '#f55', key: 'revoked_tokens_count' }
  ]);

  const attacks = [
    { name: 'SQL Injection',        pct: 65, level: 'CRITICAL', color: '#f55' },
    { name: 'Cross-Site Scripting', pct: 48, level: 'HIGH',     color: '#fa0' },
    { name: 'DDoS Attempt',         pct: 33, level: 'MEDIUM',   color: '#ff0' },
    { name: 'Brute Force',          pct: 24, level: 'LOW',      color: '#0af' }
  ];

  // WebSocket connection for real-time logs
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        const wsUrl = backendUrl.replace('http://', 'ws://').replace('https://', 'wss://') + '/dashboard/logs';
        wsRef.current = new WebSocket(wsUrl);
        
        wsRef.current.onopen = () => {
          console.log('WebSocket connected to dashboard logs');
        };
        
        wsRef.current.onmessage = (event) => {
          try {
            const logData = JSON.parse(event.data);
            
            // Format log data for terminal display
            const formattedLog = {
              endpoint: logData.endpoint || '',
              method: logData.method || '',
              ip: logData.ip || '',
              status: logData.status_code || '',
              threat: logData.score_result?.threat_type || 'normal'
            };
            
            setLogs(prevLogs => [formattedLog, ...prevLogs].slice(0, 50)); // Keep last 50 logs
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
  }, [backendUrl]);

  // Fetch dashboard data from backend
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await fetch(`${backendUrl}${API_ENDPOINTS.DASHBOARD_STATS}`);
        if (response.ok) {
          const data = await response.json();
          
          // Map backend data to frontend stats
          const updatedStats = [
            { value: data.total_threats?.toString() || '0', label: 'THREATS DETECTED', color: '#0f0', key: 'total_threats' },
            { value: data.rate_limited_ips?.toString() || '0', label: 'RATE LIMITED IPS', color: '#fa0', key: 'rate_limited_ips' },
            { value: data.ips_blocked?.toString() || '0', label: 'IPs BLOCKED', color: '#0af', key: 'ips_blocked' },
            { value: data.revoked_tokens_count?.toString() || '0', label: 'REVOKED TOKEN COUNT', color: '#f55', key: 'revoked_tokens_count' }
          ];
          
          setStats(updatedStats);
        }
      } catch (error) {
        console.log('Backend connection failed, using default data');
      }
    };

    fetchDashboardData();
    
    // Set up polling for real-time updates
    const interval = setInterval(fetchDashboardData, 5000); // Update every 5 seconds
    
    return () => clearInterval(interval);
  }, []);

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

        {/* Left - LIVE TRAFFIC */}
        <div className="glass-panel" style={{ height: '400px' }}>
          <div className="panel-title">LIVE TRAFFIC — REQUESTS / MIN</div>
          <div style={{ 
            height: '320px', 
            overflowY: 'auto',
            padding: '1rem',
            fontFamily: 'Share Tech Mono', 
            fontSize: '0.78rem', 
            color: 'rgba(0,255,0,0.35)', 
            letterSpacing: '2px'
          }} 
          className="traffic-scrollbar">
            {logs.length === 0 ? (
              <div style={{ textAlign: 'center', marginTop: '2rem' }}>
                [ SYSTEM ANALYZING TRAFFIC DATA... ]
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
                {logs.map((log, index) => (
                  <div key={index} style={{ 
                    display: 'flex', 
                    alignItems: 'center',
                    gap: '0.5rem',
                    padding: '0.2rem 0',
                    borderBottom: index < logs.length - 1 ? '1px solid rgba(0,255,0,0.1)' : 'none'
                  }}>
                    <span style={{ color: '#0f0', minWidth: '60px' }}>
                      {log.method}
                    </span>
                    <span style={{ color: '#0af', minWidth: '120px' }}>
                      {log.ip}
                    </span>
                    <span style={{ color: '#fa0', minWidth: '200px', flex: 1 }}>
                      {log.endpoint}
                    </span>
                    <span style={{ 
                      color: log.status === 200 ? '#0f0' : log.status >= 400 ? '#f55' : '#fa0',
                      minWidth: '40px',
                      textAlign: 'right'
                    }}>
                      {log.status}
                    </span>
                    <span style={{ 
                      color: log.threat === 'normal' ? '#0f0' : '#f55',
                      minWidth: '80px',
                      textAlign: 'right',
                      fontSize: '0.7rem'
                    }}>
                      [{log.threat}]
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right - ATTACK TYPE BREAKDOWN */}
        <div className="glass-panel" style={{ height: '400px' }}>
          <div className="panel-title">ATTACK TYPE BREAKDOWN</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', padding: '1rem 0' }}>
            {attacks.map((a, i) => (
              <div key={i}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontFamily: 'Share Tech Mono', fontSize: '0.72rem', marginBottom: '4px' }}>
                  <span style={{ color: 'rgba(0,255,0,0.7)' }}>{a.name}</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ 
                      padding: '2px 6px', 
                      borderRadius: '3px', 
                      fontSize: '0.6rem', 
                      fontWeight: 'bold',
                      backgroundColor: `${a.color}20`,
                      color: a.color,
                      border: `1px solid ${a.color}50`
                    }}>
                      {a.level}
                    </span>
                    <span style={{ color: 'rgba(0,255,0,0.7)' }}>{a.pct}%</span>
                  </div>
                </div>
                <div className="prog-track">
                  <div className="prog-fill" style={{ 
                    width: `${a.pct}%`,
                    backgroundColor: a.color,
                    boxShadow: `0 0 8px ${a.color}50`
                  }} />
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
};

export default Dashboard;
