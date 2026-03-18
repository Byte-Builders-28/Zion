import React from 'react';
import MatrixRain from './components/MatrixRain';
import Card from './components/Card';
import './LandingPage.css';

const LandingPage = () => {
  const cards = [
    {
      title: 'Dashboard',
      description: 'System overview and core metrics.'
    },
    {
      title: 'Privacy Policy',
      description: 'Data protection and security protocols.'
    },
    {
      title: 'Incident Log',
      description: 'Real-time threat detection history.'
    },
    {
      title: 'Attack simulation',
      description: 'Vulnerability assessment and stress testing.'
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
