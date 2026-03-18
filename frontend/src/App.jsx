import React, { useState } from 'react';
import LandingPage from './LandingPage';
import Dashboard from './components/Dashboard';
import Simulation from './components/Simulation';
import Threats from './components/Threats';
import Policies from './components/Policies';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('landing');

  if (currentPage === 'landing') {
    return <LandingPage onNavigate={setCurrentPage} />;
  }

  return (
    <div className="zion-app bg-black min-h-screen text-green-500 font-mono">
      <header className="border-b border-green-800 p-4 flex justify-between items-center bg-black">
        <div className="text-2xl font-bold tracking-wider glitch cursor-pointer" 
             data-text="ZION // API DEFENSE SYSTEM"
             onClick={() => setCurrentPage('landing')}>
          ZION // API DEFENSE SYSTEM
        </div>
        <nav className="flex space-x-4">
          <button 
            className={`px-4 py-2 border ${currentPage === 'dashboard' ? 'bg-green-900 border-green-500 text-green-100' : 'border-transparent text-green-700 hover:text-green-500'}`}
            onClick={() => setCurrentPage('dashboard')}
          >
            [_DASHBOARD]
          </button>
          <button 
            className={`px-4 py-2 border ${currentPage === 'simulation' ? 'bg-green-900 border-green-500 text-green-100' : 'border-transparent text-green-700 hover:text-green-500'}`}
            onClick={() => setCurrentPage('simulation')}
          >
            [_SIMULATION]
          </button>
          <button 
            className={`px-4 py-2 border ${currentPage === 'threats' ? 'bg-green-900 border-green-500 text-green-100' : 'border-transparent text-green-700 hover:text-green-500'}`}
            onClick={() => setCurrentPage('threats')}
          >
            [_THREATS]
          </button>
          <button 
            className={`px-4 py-2 border ${currentPage === 'policies' ? 'bg-green-900 border-green-500 text-green-100' : 'border-transparent text-green-700 hover:text-green-500'}`}
            onClick={() => setCurrentPage('policies')}
          >
             [_POLICIES]
          </button>
        </nav>
      </header>


      <main className="p-4">
        {currentPage === 'dashboard' && <Dashboard />}
        {currentPage === 'simulation' && <Simulation />}
        {currentPage === 'threats' && <Threats />}
        {currentPage === 'policies' && <Policies />}
      </main>
    </div>
  );
}

export default App;
