import React from 'react';
import { useNavigate } from 'react-router-dom';
import MatrixRain from './components/MatrixRain';
import TiltCard from './components/TiltCard';
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

  return (
    <div className="landing-container">
      <MatrixRain />
      
      <header className="landing-header">
        <h1 className="glitch" data-text="ZION">ZION</h1>
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

      <div className="site-summary-container">
        <p className="site-summary">
          A smart supply chain digital twin platform that combines AI-driven simulation, 
          optimized edge intelligence, seamless API integration, and Algorand-powered 
          real-time micro-transaction tracking for transparent, efficient logistics.
        </p>
      </div>

      <footer className="landing-footer">
        <p>V 1.0.0 // MATRIX PROTOCOL</p>
      </footer>
    </div>
  );
};

export default LandingPage;
