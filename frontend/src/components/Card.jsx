import React from 'react';
import './Card.css';

const Card = ({ title, description, icon, onClick }) => {
  const isInteractive = typeof onClick === 'function';

  const handleKeyDown = (event) => {
    if (!isInteractive) {
      return;
    }
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      onClick();
    }
  };

  return (
    <div
      className={`matrix-card${isInteractive ? ' matrix-card--interactive' : ''}`}
      onClick={isInteractive ? onClick : undefined}
      role={isInteractive ? 'button' : undefined}
      tabIndex={isInteractive ? 0 : undefined}
      onKeyDown={handleKeyDown}
    >
      <div className="card-content">
        {icon && <div className="card-icon">{icon}</div>}
        <h2 className="card-title">{title}</h2>
        {description && <p className="card-desc">{description}</p>}
      </div>
    </div>
  );
};

export default Card;
