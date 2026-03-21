import React, { useState, useEffect, useRef } from 'react';
import './ScrambledText.css';

const ScrambledText = ({ 
  children, 
  className = '', 
  radius = 100, 
  duration = 1.2, 
  speed = 0.5, 
  scrambleChars = '.:' 
}) => {
  const [displayText, setDisplayText] = useState('');
  const [isScrambling, setIsScrambling] = useState(false);
  const textRef = useRef(null);
  const originalText = typeof children === 'string' ? children : '';

  useEffect(() => {
    setDisplayText(originalText);
  }, [originalText]);

  const scramble = async () => {
    if (isScrambling) return;
    setIsScrambling(true);

    const text = originalText;
    const chars = scrambleChars.split('');
    const iterations = radius;
    
    for (let i = 0; i <= iterations; i++) {
      let scrambled = '';
      
      for (let j = 0; j < text.length; j++) {
        if (text[j] === ' ') {
          scrambled += ' ';
        } else if (i < iterations) {
          const progress = i / iterations;
          const charProgress = j / text.length;
          
          if (charProgress < progress) {
            scrambled += text[j];
          } else {
            scrambled += chars[Math.floor(Math.random() * chars.length)];
          }
        } else {
          scrambled += text[j];
        }
      }
      
      setDisplayText(scrambled);
      await new Promise(resolve => setTimeout(resolve, speed * 1000 / iterations));
    }
    
    setIsScrambling(false);
  };

  useEffect(() => {
    const element = textRef.current;
    if (!element) return;

    const handleMouseEnter = () => scramble();
    
    element.addEventListener('mouseenter', handleMouseEnter);
    
    return () => {
      element.removeEventListener('mouseenter', handleMouseEnter);
    };
  }, [originalText, radius, duration, speed, scrambleChars]);

  return (
    <span 
      ref={textRef}
      className={`scrambled-text ${className}`}
      style={{ '--duration': duration }}
    >
      {displayText}
    </span>
  );
};

export default ScrambledText;
