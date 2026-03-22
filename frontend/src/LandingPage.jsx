import React from 'react';
import { useNavigate } from 'react-router-dom';
import MatrixRain from './components/MatrixRain';
import ScrambledText from './components/ScrambledText';
import config from './config';
import './LandingPage.css';

const LandingPage = () => {
  const navigate = useNavigate();

  const pills = [
    {
      title: 'Dashboard',
      description: 'Enter the command center',
      page: '/dashboard',
      color: 'blue',
      side: 'right'
    },
    {
      title: 'Simulation',
      description: 'Begin attack simulation',
      page: '/simulation',
      color: 'red',
      side: 'left'
    }
  ];

  const flowSteps = [
    { step: '01', title: 'TRAFFIC INTERCEPTION', desc: 'FastAPI middleware intercepts every HTTP request, extracting core features (IP, token, payload, endpoint).' },
    { step: '02', title: 'ML DETECTION', desc: 'Sliding windows track metrics in memory. An Isolation Forest model identifies statistical anomalies dynamically.' },
    { step: '03', title: 'THREAT CLASSIFICATION', desc: 'Heuristics label high-risk clusters (e.g. Rate Flood, Credential Stuffing, Token Replay).' },
    { step: '04', title: 'BLOCKCHAIN AUDIT', desc: 'Critical incidents trigger smart policies and get permanently logged to Algorand blockchain.' }
  ];

  const capabilities = [
    { label: 'Monitoring & Tracking', value: 'Traffic rate, Request payloads, Unique IPs, Endpoint spread, Token usage, Failed login streaks' },
    { label: 'Threats Defeated', value: 'Rate Floods, Credential Stuffing, Token Replays, Automated Scraping, DDoS Probes' },
    { label: 'Automated Response', value: 'Real-time ML scoring -> Dynamic Policy Generation -> Smart IP Blocking' },
    { label: 'Incident Integrity', value: 'Decentralized evidence logging via Algorand Testnet for secure, tamper-proof audits' }
  ];

  return (
    <div className="landing-container">
      <div className="background-image"></div>
      <MatrixRain colors={config.MATRIX_RAIN.COLORS} opacity={0.25} />
      
      <header className="landing-header">
        <ScrambledText
          className="glitch scrambled-text-zion"
          radius={100}
          duration={1.2}
          speed={0.5}
          scrambleChars=".:"
        >
          ZION
        </ScrambledText>
      </header>

      <div className="matrix-choice-container">
        <div className="matrix-scene">
          {/* Left Pill - Positioned over background hand */}
          <div className="pill-side left">
            <div 
              className="matrix-pill red"
              onClick={() => navigate('/dashboard')}
            >
              <div className="pill-content">
                <div className="pill-title">Dashboard</div>
                <div className="pill-description">Enter the command center</div>
              </div>
            </div>
          </div>

          {/* Center Text */}
          <div className="center-text">
            <div className="choice-title">THE CHOICE</div>
            <div className="choice-subtitle">Take the blue pill... or take the red pill</div>
          </div>

          {/* Right Pill - Positioned over background hand */}
          <div className="pill-side right">
            <div 
              className="matrix-pill blue"
              onClick={() => navigate('/simulation')}
            >
              <div className="pill-content">
                <div className="pill-title">Simulation</div>
                <div className="pill-description">Begin attack simulation</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="features-section">
        <h2 className="section-title">SYSTEM ARCHITECTURE</h2>
        <div className="flow-grid">
          {flowSteps.map((f, i) => (
            <div key={i} className="flow-step">
              <span className="step-num">{f.step}</span>
              <h4>{f.title}</h4>
              <p>{f.desc}</p>
            </div>
          ))}
        </div>

        <h2 className="section-title" style={{ marginTop: '4rem' }}>CAPABILITIES & TRACKING</h2>
        <div className="capabilities-grid">
          {capabilities.map((c, i) => (
            <div key={i} className="capability-row">
              <div className="capability-label">[{c.label}]</div>
              <div className="capability-value">{c.value}</div>
            </div>
          ))}
        </div>
      </div>

      <footer className="landing-footer">
        <p>V 1.0.0 // MATRIX PROTOCOL // ZION CYBERSECURITY</p>
      </footer>
    </div>
  );
};

export default LandingPage;
