import React from 'react';
import { useNavigate } from 'react-router-dom';
import MatrixRain from './components/MatrixRain';
import TiltCard from './components/TiltCard';
import ScrambledText from './components/ScrambledText';
import './LandingPage.css';

const LandingPage = () => {
  const navigate = useNavigate();
  const cards = [
    {
      title: 'Dashboard',
      description: 'System overview and core metrics.',
      page: '/dashboard'
    },
    {
      title: 'Privacy Policy',
      description: 'Data protection and security protocols.',
      page: '/policies'
    },
    {
      title: 'Incident Log',
      description: 'Real-time threat detection history.',
      page: '/threats'
    },
    {
      title: 'Attack simulation',
      description: 'Vulnerability assessment and stress testing.',
      page: '/simulation'
    }
  ];

  const features = [
    {
      title: 'AI-Driven Simulation',
      description: 'Advanced digital twin technology to model and optimize complex supply chain scenarios.',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 18a8 8 0 1 1 8-8 8 8 0 0 1-8 8z" />
          <path d="M12 6v6l4 2" />
        </svg>
      )
    },
    {
      title: 'Edge Intelligence',
      description: 'Real-time processing at the source for maximum speed and reduced latency.',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M17.5 19c.7-1.3 1.1-2.8 1.1-4.5 0-4.4-3.6-8-8-8S2.6 10.1 2.6 14.5c0 1.7.4 3.2 1.1 4.5" />
          <path d="M12 11v9" />
          <path d="M10 20h4" />
        </svg>
      )
    },
    {
      title: 'API Integration',
      description: 'Seamless connectivity with existing logistics, ERP, and data ecosystem platforms.',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
          <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
        </svg>
      )
    },
    {
      title: 'Algorand Tracking',
      description: 'Blockchain-powered immutable, real-time micro-transaction visibility and trust.',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="2" y="7" width="20" height="14" rx="2" ry="2" />
          <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
        </svg>
      )
    }
  ];

  const capabilities = [
    { label: 'Monitoring & Tracking', value: 'Traffic rate, Request payloads, Unique IPs, Endpoint spread, Token usage, Failed login streaks' },
    { label: 'Threats Defeated', value: 'Rate Floods, Credential Stuffing, Token Replays, Automated Scraping, DDoS Probes' },
    { label: 'Automated Response', value: 'Real-time ML scoring -> Dynamic Policy Generation -> Smart IP Blocking' },
    { label: 'Incident Integrity', value: 'Decentralized evidence logging via Algorand Testnet for secure, tamper-proof audits' }
  ];

  const flowSteps = [
    { step: '01', title: 'TRAFFIC INTERCEPTION', desc: 'FastAPI middleware intercepts every HTTP request, extracting core features (IP, token, payload, endpoint).' },
    { step: '02', title: 'ML DETECTION', desc: 'Sliding windows track metrics in memory. An Isolation Forest model identifies statistical anomalies dynamically.' },
    { step: '03', title: 'THREAT CLASSIFICATION', desc: 'Heuristics label high-risk clusters (e.g. Rate Flood, Credential Stuffing, Token Replay).' },
    { step: '04', title: 'BLOCKCHAIN AUDIT', desc: 'Critical incidents trigger smart policies via Smolify and get permanently logged to the Algorand blockchain.' }
  ];

  return (
    <div className="landing-container">
      <MatrixRain colors={['#0F0']} />
      
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
        <p className="subtitle">Secure connection established.</p>
        <button className="get-started-btn" onClick={() => navigate('/dashboard')}>
          GET STARTED
          <span className="btn-glow"></span>
        </button>
      </header>

      <div className="nav-wrapper">
        <nav className="bottom-nav">
          {cards.map((card, index) => (
            <TiltCard 
              key={index}
              title={card.title}
              onClick={() => navigate(card.page)}
            />
          ))}
        </nav>
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

        <h2 className="section-title" style={{ marginTop: '4rem' }}>CORE COMPONENTS</h2>
        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-box">
              <div className="feature-icon">{feature.icon}</div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-desc">{feature.description}</p>
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
