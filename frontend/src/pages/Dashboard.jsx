import React, { useState, useEffect } from 'react';
import { getCases } from '../services/api';

const Dashboard = () => {
    const [stats, setStats] = useState({ total: 0, open: 0, closed: 0 });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const data = await getCases();
                const cases = Array.isArray(data) ? data : [];

                const open = cases.filter(c => c.status === 'open').length;
                const closed = cases.filter(c => c.status === 'closed').length;

                setStats({
                    total: cases.length,
                    open,
                    closed
                });
            } catch (err) {
                console.error('Failed to fetch dashboard stats:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
    }, []);

    return (
        <div>
            <h2 className="text-2xl font-bold mb-6">Dashboard</h2>

            {loading ? (
                <div className="flex justify-center items-center h-32">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 flex flex-col items-center">
                        <h3 className="text-gray-500 text-sm font-medium">Total Cases</h3>
                        <p className="text-4xl font-bold text-gray-900 mt-2">{stats.total}</p>
                    </div>
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 flex flex-col items-center">
                        <h3 className="text-gray-500 text-sm font-medium">Open Cases</h3>
                        <p className="text-4xl font-bold text-green-600 mt-2">{stats.open}</p>
                    </div>
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 flex flex-col items-center">
                        <h3 className="text-gray-500 text-sm font-medium">Closed Cases</h3>
                        <p className="text-4xl font-bold text-red-600 mt-2">{stats.closed}</p>
                    </div>
                </div>
            )}

            <div className="mt-8 bg-white p-6 rounded-lg shadow-sm border border-gray-100">
                <h3 className="text-lg font-semibold mb-4">Welcome to LegalCMS</h3>
                <p className="text-gray-600">
                    Select an option from the sidebar to manage your cases. You can view existing cases or create new ones.
                </p>
            </div>
        </div>
    );
};

export default Dashboard;
