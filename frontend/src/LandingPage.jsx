import React from 'react';
import { useNavigate } from 'react-router-dom';
import MatrixRain from './components/MatrixRain';
import Card from './components/Card';
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
        <h1 className="glitch" data-text="SYSTEM TERMINAL">SYSTEM TERMINAL</h1>
        <p className="subtitle">Secure connection established.</p>
      </header>

      <main className="cards-grid">
        {cards.map((card, index) => (
          <Card 
            key={index}
            title={card.title}
            description={card.description}
            onClick={() => navigate(card.page)}
          />
        ))}
      </main>

      <footer className="landing-footer">
        <p>V 1.0.0 // MATRIX PROTOCOL</p>
      </footer>
    </div>
  );
};

export default LandingPage;
