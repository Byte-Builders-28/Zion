import React from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';

const navLinks = [
  { label: '_DASHBOARD', path: '/dashboard' },
  { label: '_SIMULATION', path: '/simulation' },
  { label: '_THREATS', path: '/threats' },
  { label: '_POLICIES', path: '/policies' }
];

const sectionClassMap = {
  '/dashboard': 'page-dashboard',
  '/simulation': 'page-simulation',
  '/threats': 'page-threats',
  '/policies': 'page-policies'
};

import MatrixRain from '../MatrixRain';

const ConsoleLayout = () => {
  const location = useLocation();
  const sectionClass = sectionClassMap[location.pathname] || 'page-generic';

  return (
    <div className="zion-shell font-mono text-green-500">
      <MatrixRain opacity={0.45} colors={['#0F0', '#F00', '#0AF', '#FF0']} />
      <header className="zion-header">
        <NavLink to="/" className="zion-brand glitch" data-text="ZION // API DEFENSE SYSTEM">
          ZION // API DEFENSE SYSTEM
        </NavLink>
        <nav className="zion-nav">
          {navLinks.map(({ label, path }) => (
            <NavLink
              key={path}
              to={path}
              className={({ isActive }) => `nav-link${isActive ? ' is-active' : ''}`}
            >
              [{label}]
            </NavLink>
          ))}
        </nav>
      </header>

      <main className={`page-section ${sectionClass}`}>
        <Outlet />
      </main>
    </div>
  );
};

export default ConsoleLayout;
