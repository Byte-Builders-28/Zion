import { useEffect, useRef } from 'react';

const MatrixRain = ({ opacity = 0.45, colors = ['#0F0', '#F00', '#0AF', '#FF0'] }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Katakana + Latin + Numerals
    const text = 'ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍ1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const matrix = text.split('');
    const fontSize = 16;
    const columns = canvas.width / fontSize;

    const drops = [];
    const dropColors = [];
    for (let x = 0; x < columns; x++) {
      drops[x] = Math.random() * -100;
      dropColors[x] = colors[Math.floor(Math.random() * colors.length)];
    }

    const draw = () => {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.08)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.font = fontSize + 'px monospace';

      for (let i = 0; i < drops.length; i++) {
        const charHead = matrix[Math.floor(Math.random() * matrix.length)];
        const charTail = matrix[Math.floor(Math.random() * matrix.length)];

        ctx.fillStyle = dropColors[i];
        ctx.fillText(charTail, i * fontSize, (drops[i] - 1) * fontSize);

        ctx.fillStyle = '#FFF';
        ctx.fillText(charHead, i * fontSize, drops[i] * fontSize);

        if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
          drops[i] = 0;
          dropColors[i] = colors[Math.floor(Math.random() * colors.length)];
        }
        drops[i]++;
      }
    };

    const intervalId = setInterval(draw, 33);
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
        top: 0, left: 0,
        width: '100%', height: '100%',
        zIndex: -1,
        backgroundColor: 'black',
        opacity: opacity
      }}
    />
  );
};

export default MatrixRain;
