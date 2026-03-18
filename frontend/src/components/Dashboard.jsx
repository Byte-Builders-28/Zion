import React from 'react';

const Dashboard = () => {
  return (
    <div className="p-6">
      <h2 className="text-xl mb-4 text-green-500">// ZION COMMAND CENTER -- REAL-TIME THREAT OVERVIEW</h2>
      
      {/* Stats Row */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="border border-green-800 p-4 bg-black">
          <div className="text-3xl text-green-500">0</div>
          <div className="text-xs text-green-800">THREATS DETECTED</div>
        </div>
        <div className="border border-green-800 p-4 bg-black">
          <div className="text-3xl text-red-500">0</div>
          <div className="text-xs text-green-800">CRITICAL ACTIVE</div>
        </div>
        <div className="border border-green-800 p-4 bg-black">
          <div className="text-3xl text-yellow-500">0.00</div>
          <div className="text-xs text-green-800">AVG RISK SCORE</div>
        </div>
        <div className="border border-green-800 p-4 bg-black">
          <div className="text-3xl text-blue-500">0</div>
          <div className="text-xs text-green-800">IPs BLOCKED</div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="space-y-6">
          <div className="border border-green-800 p-4 bg-black h-64">
             <h3 className="text-green-700 text-sm mb-2">LIVE TRAFFIC -- REQUESTS/MIN</h3>
             {/* Chart Placeholder */}
             <div className="h-full flex items-end justify-between px-2 pb-2">
                 <div className="w-full text-center text-green-900 text-xs">Chart Visualization Loading...</div>
             </div>
          </div>
          
          <div className="border border-green-800 p-4 bg-black h-48">
              <h3 className="text-green-700 text-sm mb-2">ATTACK TYPE BREAKDOWN</h3>
              {/* Progress bars placeholder */}
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          <div className="border border-green-800 p-4 bg-black h-64">
            <h3 className="text-green-700 text-sm mb-2">ACTIVE THREAT FEED</h3>
             <div className="text-xs font-mono space-y-2">
                <div className="flex justify-between">
                    <span className="text-green-400">token_replay</span>
                    <span className="text-green-600">/login</span>
                    <span className="text-red-500 border border-red-900 px-1">CRITICAL 0.96</span>
                </div>
                {/* More items */}
             </div>
          </div>

          <div className="border border-green-800 p-4 bg-black h-48">
             <h3 className="text-green-700 text-sm mb-2">SYSTEM LOG</h3>
             <div className="text-xs font-mono space-y-1 text-green-600">
                <div>00:00:01 [INIT] Zion defense layers armed</div>
                <div>00:00:04 [ML] Isolation Forest loaded</div>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
