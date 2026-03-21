import { useEffect, useRef } from 'react';

/**
 * MatrixRain — enhanced with:
 *  1. Depth-of-field tunnel: radial depth from screen center drives
 *     font size (22→7px), fall speed (3.5→0.3), and brightness (1→0.15)
 *  2. Cursor physics — 3 zones:
 *     • Clear  (< 80px)  : no rendering, dark hole
 *     • Scatter(< 180px) : horizontal repulsion impulse
 *     • Accel  (< 260px) : fall speed multiplied up to 6×
 */
const MatrixRain = ({ opacity = 0.45, colors = ['#0F0', '#F00', '#0AF', '#FF0'] }) => {
  const canvasRef = useRef(null);
  const mouseRef  = useRef({ x: -9999, y: -9999 });

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx    = canvas.getContext('2d');

    /* ── mouse tracking ── */
    const onMove  = (e) => { mouseRef.current = { x: e.clientX, y: e.clientY }; };
    const onLeave = ()  => { mouseRef.current = { x: -9999,     y: -9999     }; };
    window.addEventListener('mousemove',  onMove);
    window.addEventListener('mouseleave', onLeave);

    /* ── constants ── */
    const FONT_MAX     = 22;   // center font size
    const FONT_MIN     = 7;    // edge font size
    const SPEED_MAX    = 3.5;  // center fall speed (px/frame)
    const SPEED_MIN    = 0.3;  // edge fall speed
    const BRIGHT_MAX   = 1.0;  // center brightness
    const BRIGHT_MIN   = 0.4; // edge brightness
    const CLEAR_R      = 80;   // cursor clear radius
    const SCATTER_R    = 180;  // cursor scatter radius
    const ACCEL_R      = 260;  // cursor accel radius
    const TRAIL_ALPHA  = 0.03; // lower = longer trails

    const CHARS = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
    const rChar = () => CHARS[Math.floor(Math.random() * CHARS.length)];

    /* parse "#RRGGBB" or "#RGB" → [r,g,b] */
    const hexRgb = (hex) => {
      let h = hex.replace('#', '');
      if (h.length === 3) h = h.split('').map(c => c + c).join('');
      const n = parseInt(h, 16);
      return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
    };

    let cols = [];

    const init = () => {
      canvas.width  = window.innerWidth;
      canvas.height = window.innerHeight;
      ctx.fillStyle = '#000';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const cx      = canvas.width  / 2;
      const cy      = canvas.height / 2;
      /* diagonal = max possible distance from center */
      const maxDist = Math.sqrt(cx * cx + cy * cy);

      cols = [];
      /* columns spaced by FONT_MAX so they don't overlap at center */
      for (let x = 0; x < canvas.width; x += FONT_MAX) {
        const colCX  = x + FONT_MAX / 2;
        const colCY  = cy; // use vertical center for depth calc
        const dx     = colCX - cx;
        const dy     = colCY - cy; // 0 — purely horizontal tunnel
        /* radial distance 0..1 from center */
        const t      = Math.min(Math.sqrt(dx * dx + dy * dy) / (canvas.width / 2), 1);
        /* depth 1 at center, 0 at edge — cosine curve for smooth falloff */
        const depth  = Math.cos(t * Math.PI * 0.5);

        cols.push({
          x,
          y:        Math.random() * -canvas.height * 1.5,
          fontSize: Math.round(FONT_MIN  + (FONT_MAX   - FONT_MIN)   * depth),
          speed:    SPEED_MIN  + (SPEED_MAX  - SPEED_MIN)  * depth,
          bright:   BRIGHT_MIN + (BRIGHT_MAX - BRIGHT_MIN) * depth,
          color:    colors[Math.floor(Math.random() * colors.length)],
          offsetX:  0,
          velX:     0,
        });
      }
    };

    init();
    window.addEventListener('resize', init);

    /* ── draw loop ── */
    let animId;
    const draw = () => {
      /* fade previous frame */
      ctx.fillStyle = `rgba(0,0,0,${TRAIL_ALPHA})`;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const mx = mouseRef.current.x;
      const my = mouseRef.current.y;

      for (const col of cols) {
        const drawX = col.x + col.offsetX;

        /* distance from cursor to this column's current head */
        const dx   = drawX + col.fontSize / 2 - mx;
        const dy   = col.y - my;
        const dist = Math.sqrt(dx * dx + dy * dy);

        /* ── zone 1: clear — invisible hole ── */
        if (dist < CLEAR_R) {
          col.y    += col.speed * 2;
          col.velX += -col.offsetX * 0.2;
          col.velX *= 0.75;
          col.offsetX += col.velX;
          if (col.y > canvas.height) col.y = Math.random() * -300;
          continue; // skip drawing
        }

        /* ── zone 2: scatter — horizontal repulsion ── */
        if (dist < SCATTER_R) {
          const strength = (1 - (dist - CLEAR_R) / (SCATTER_R - CLEAR_R));
          col.velX += (dx / dist) * strength * 5;
        }

        /* ── zone 3: accelerate ── */
        let speedMult = 1;
        if (dist < ACCEL_R) {
          speedMult = 1 + (1 - (dist - CLEAR_R) / (ACCEL_R - CLEAR_R)) * 5;
        }

        /* spring back to home column */
        col.velX    += -col.offsetX * 0.06;
        col.velX    *= 0.88;
        col.offsetX += col.velX;

        /* ── render ── */
        const [r, g, b] = hexRgb(col.color);
        ctx.font = `${col.fontSize}px monospace`;

        /* trail char — colored, brighter */
        ctx.fillStyle = `rgba(${r},${g},${b},${col.bright * 0.9})`;
        ctx.fillText(rChar(), drawX, col.y - col.fontSize);

        /* head char — white hot */
        ctx.fillStyle = `rgba(255,255,255,${col.bright})`;
        ctx.fillText(rChar(), drawX, col.y);

        /* advance */
        col.y += col.speed * speedMult;
        if (col.y > canvas.height + col.fontSize * 2) {
          col.y     = Math.random() * -300;
          col.color = colors[Math.floor(Math.random() * colors.length)];
        }
      }

      animId = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize',    init);
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('mouseleave',onLeave);
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
        backgroundColor: '#000',
        opacity,
      }}
    />
  );
};

export default MatrixRain;
