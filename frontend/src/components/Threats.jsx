import React from 'react';

const Threats = () => {
    return (
        <div className="p-6">
            <h2 className="text-xl mb-4 text-green-500">// INCIDENT LOG & THREATS</h2>
            <div className="border border-green-800 p-4 bg-black h-96 overflow-y-auto">
                <table className="w-full text-left text-sm text-green-600">
                    <thead>
                        <tr className="border-b border-green-800">
                            <th className="p-2">TIMESTAMP</th>
                            <th className="p-2">TYPE</th>
                            <th className="p-2">SOURCE IP</th>
                            <th className="p-2">TARGET</th>
                            <th className="p-2">RISK</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr className="border-b border-green-900">
                            <td className="p-2">2026-03-19 10:42:01</td>
                            <td className="p-2">token_replay</td>
                            <td className="p-2">192.168.1.45</td>
                            <td className="p-2">/api/v1/login</td>
                            <td className="p-2 text-red-500">HIGH</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default Threats;
