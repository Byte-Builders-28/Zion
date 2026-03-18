import React from 'react';

const Policies = () => {
    return (
        <div className="p-6">
            <h2 className="text-xl mb-4 text-green-500">// SECURITY POLICIES</h2>
            <div className="grid grid-cols-2 gap-6">
                <div className="border border-green-800 p-4 bg-black">
                    <h3 className="text-green-400 mb-2">RATE LIMITING</h3>
                    <div className="space-y-4">
                        <div className="flex justify-between items-center text-sm text-green-700">
                            <span>MAX_REQUESTS_PER_MIN</span>
                            <input type="text" value="60" className="bg-black border border-green-800 text-green-500 w-16 text-center" readOnly />
                        </div>
                        <div className="flex justify-between items-center text-sm text-green-700">
                            <span>BURST_TOLERANCE</span>
                            <div className="w-24 h-2 bg-green-900 rounded">
                                <div className="h-full bg-green-500 w-1/2"></div>
                            </div>
                        </div>
                    </div>
                </div>
                 <div className="border border-green-800 p-4 bg-black">
                    <h3 className="text-green-400 mb-2">BLOCKING RULES</h3>
                     <div className="space-y-2 text-sm text-green-600">
                        <div>[x] Block Tor Exit Nodes</div>
                        <div>[x] Block Known Malicious IPs</div>
                        <div>[ ] Block Non-Domestic Traffic</div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Policies;
