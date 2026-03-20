import React from 'react';
import './Dashboard.css';

const Dashboard = () => {
  const stats = [
    { value: '1,284', label: 'THREATS DETECTED', color: '#0f0' },
    { value: '12', label: 'CRITICAL ACTIVE', color: '#f00' },
    { value: '0.14', label: 'AVG RISK SCORE', color: '#ff0' },
    { value: '42', label: 'IPs BLOCKED', color: '#0af' }
  ];

  return (
    <div className="p-6">
      <h2 className="dashboard-section-title">// ZION COMMAND CENTER -- REAL-TIME THREAT OVERVIEW</h2>
      
      {/* Stats Row */}
      <div className="dashboard-stat-grid">
        {stats.map((stat, index) => (
          <div key={index} className="dashboard-stat-card">
            <div className="stat-value" style={{ color: stat.color }}>{stat.value}</div>
            <div className="stat-label" style={{ color: stat.color }}>{stat.label}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="space-y-6">
          <div className="dashboard-panel h-64">
             <h3 className="panel-header">LIVE TRAFFIC -- REQUESTS/MIN</h3>
             <div className="h-full flex items-center justify-center">
                 <div className="text-green-900 text-xs font-mono animate-pulse">
                   [ SYSTEM ANALYZING TRAFFIC DATA ... ]
                 </div>
             </div>
          </div>
          
          <div className="dashboard-panel h-48">
              <h3 className="panel-header">ATTACK TYPE BREAKDOWN</h3>
              <div className="space-y-4 pt-2">
                {['SQL Injection', 'Cross-Site Scripting', 'DDoS Attempt'].map((type, i) => (
                  <div key={i} className="space-y-1">
                    <div className="flex justify-between text-[10px] font-mono">
                      <span>{type}</span>
                      <span>{65 - i * 15}%</span>
                    </div>
                    <div className="h-1 bg-green-900/30 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-green-500 shadow-[0_0_10px_#0f0]" 
                        style={{ width: `${65 - i * 15}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          <div className="dashboard-panel h-64">
            <h3 className="panel-header">ACTIVE THREAT FEED</h3>
             <div className="text-xs font-mono space-y-3 overflow-y-auto h-48 pr-2">
                {[
                  { type: 'token_replay', path: '/login', risk: '0.96', level: 'CRITICAL' },
                  { type: 'rate_limit', path: '/api/v1/user', risk: '0.72', level: 'HIGH' },
                  { type: 'brute_force', path: '/auth', risk: '0.88', level: 'CRITICAL' },
                  { type: 'unusual_geo', path: '/dashboard', risk: '0.45', level: 'MED' }
                ].map((threat, i) => (
                  <div key={i} className="flex justify-between items-center border-b border-green-900/20 pb-2">
                      <span className="text-green-400 w-24">{threat.type}</span>
                      <span className="text-green-600 flex-1 px-2">{threat.path}</span>
                      <span className={`px-2 py-0.5 border text-[9px] ${
                        threat.level === 'CRITICAL' ? 'text-red-500 border-red-900' : 
                        threat.level === 'HIGH' ? 'text-orange-500 border-orange-900' : 'text-yellow-500 border-yellow-900'
                      }`}>
                        {threat.level} {threat.risk}
                      </span>
                  </div>
                ))}
             </div>
          </div>

          <div className="dashboard-panel h-48">
             <h3 className="panel-header">SYSTEM LOG</h3>
             <div className="text-[10px] font-mono space-y-1 text-green-600/80 max-h-32 overflow-y-auto">
                <div>[00:00:01] INITIALIZING ZION CORE...</div>
                <div>[00:00:02] DEFENSE LAYERS ARMED</div>
                <div>[00:00:04] ML-MODEL: ISOLATION FOREST LOADED</div>
                <div>[00:00:05] MONITORING TRAFFIC ON PORT 80/443</div>
                <div className="animate-pulse text-green-400">_ SYSTEM STANDBY...</div>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
