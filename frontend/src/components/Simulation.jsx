import React from 'react';

const Simulation = () => {
    return (
        <div className="p-6">
            <h2 className="text-xl mb-4 text-green-500">// ATTACK SIMULATION</h2>
            <div className="border border-green-800 p-6 bg-black">
                <p className="text-green-600 mb-4">Select attack vector to simulate:</p>
                <div className="space-x-4">
                    <button className="border border-green-600 text-green-500 px-4 py-2 hover:bg-green-900">RATE FLOOD</button>
                    <button className="border border-green-600 text-green-500 px-4 py-2 hover:bg-green-900">TOKEN REPLAY</button>
                    <button className="border border-green-600 text-green-500 px-4 py-2 hover:bg-green-900">CREDENTIAL STUFFING</button>
                </div>
            </div>
        </div>
    );
};

export default Simulation;
