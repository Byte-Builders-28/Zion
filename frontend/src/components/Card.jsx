import React from 'react';
import './Card.css';

const Card = ({ title, description, icon, onClick }) => {
  return (
    <div className="matrix-card" onClick={onClick} role="button" tabIndex={0}>
      <div className="card-content">
        {icon && <div className="card-icon">{icon}</div>}
        <h2 className="card-title">{title}</h2>
        {description && <p className="card-desc">{description}</p>}
      </div>
    </div>
  );
};

export default Card;
