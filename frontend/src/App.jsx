import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './LandingPage';
import Dashboard from './components/Dashboard';
import Simulation from './components/Simulation';
import Threats from './components/Threats';
import Policies from './components/Policies';
import ConsoleLayout from './components/layout/ConsoleLayout';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route element={<ConsoleLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/simulation" element={<Simulation />} />
          <Route path="/threats" element={<Threats />} />
          <Route path="/policies" element={<Policies />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
