import { useEffect, useRef } from 'react';

const MatrixRain = ({ opacity = 0.45, colors = ['#0F0', '#F00', '#0AF', '#FF0'] }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    // Make canvas full screen
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Matrix characters (Alphabets only)
    const text = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const matrix = text.split('');

    const fontSize = 16;
    const columns = canvas.width / fontSize;



    // Array of drops and their colors
    const drops = [];
    const dropColors = [];
    for (let x = 0; x < columns; x++) {
      drops[x] = Math.random() * -100;
      dropColors[x] = colors[Math.floor(Math.random() * colors.length)];
    }

    // Drawing the characters
    const draw = () => {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.08)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.font = fontSize + 'px monospace';

      for (let i = 0; i < drops.length; i++) {
        const charHead = matrix[Math.floor(Math.random() * matrix.length)];
        const charTail = matrix[Math.floor(Math.random() * matrix.length)];
        
        // Draw the tail character in its assigned color
        ctx.fillStyle = dropColors[i];
        ctx.fillText(charTail, i * fontSize, (drops[i] - 1) * fontSize);

        // Draw the head character in white for the glowing effect
        ctx.fillStyle = '#FFF';
        ctx.fillText(charHead, i * fontSize, drops[i] * fontSize);

        if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
          drops[i] = 0;
          // Assign a new random color when the drop resets
          dropColors[i] = colors[Math.floor(Math.random() * colors.length)];
        }

        drops[i]++;
      }
    };

    const intervalId = setInterval(draw, 33); // ~30fps

    return () => {
      clearInterval(intervalId);
      window.removeEventListener('resize', resizeCanvas);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        zIndex: -1, // Keep it behind everything
        backgroundColor: 'black',
        opacity: opacity // Customizable background effect
      }}
    />
  );
};

export default MatrixRain;
