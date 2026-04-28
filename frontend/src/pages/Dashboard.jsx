import React, { useState, useEffect } from 'react';
import { getCases } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { Briefcase, CheckCircle, XCircle, TrendingUp, PlusCircle, ArrowRight, Clock } from 'lucide-react';

const StatCard = ({ icon: Icon, label, value, color, gradient, delay }) => (
    <div
        className="bg-white rounded-xl p-6 shadow-sm border border-slate-200/60 hover:shadow-lg hover:border-slate-300/80 transition-all duration-300 group animate-slide-up"
        style={{ animationDelay: `${delay}ms` }}
    >
        <div className="flex items-center justify-between mb-4">
            <div className={`h-11 w-11 rounded-xl ${gradient} flex items-center justify-center shadow-lg`}>
                <Icon size={20} className="text-white" />
            </div>
            <TrendingUp size={16} className="text-slate-300 group-hover:text-emerald-400 transition-colors" />
        </div>
        <p className={`text-3xl font-bold ${color} animate-count-up`}>{value}</p>
        <p className="text-sm text-slate-500 mt-1 font-medium">{label}</p>
    </div>
);

const Dashboard = () => {
    const navigate = useNavigate();
    const [stats, setStats] = useState({ total: 0, open: 0, closed: 0 });
    const [recentCases, setRecentCases] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const data = await getCases();
                const cases = Array.isArray(data) ? data : [];

                const open = cases.filter(c => c.status === 'open').length;
                const closed = cases.filter(c => c.status === 'closed').length;

                setStats({ total: cases.length, open, closed });
                setRecentCases(cases.slice(-5).reverse());
            } catch (err) {
                console.error('Failed to fetch dashboard stats:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
    }, []);

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="flex flex-col items-center gap-3">
                    <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center animate-pulse">
                        <Briefcase size={20} className="text-white" />
                    </div>
                    <p className="text-sm text-slate-400">Loading dashboard...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Welcome Section */}
            <div className="bg-gradient-to-r from-indigo-600 via-violet-600 to-purple-600 rounded-2xl p-6 md:p-8 text-white shadow-xl shadow-indigo-600/20 animate-slide-up relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2" />
                <div className="absolute bottom-0 left-1/3 w-40 h-40 bg-white/5 rounded-full translate-y-1/2" />
                <div className="relative z-10">
                    <h2 className="text-2xl md:text-3xl font-bold">Welcome back, Admin 👋</h2>
                    <p className="text-indigo-100 mt-2 max-w-lg text-sm md:text-base">
                        Here's an overview of your legal case management. Track progress, manage cases, and stay organized.
                    </p>
                    <button
                        id="dashboard-create-case"
                        onClick={() => navigate('/create-case')}
                        className="mt-5 inline-flex items-center gap-2 px-5 py-2.5 bg-white/15 hover:bg-white/25 backdrop-blur-sm rounded-xl text-sm font-medium transition-all duration-200 border border-white/20"
                    >
                        <PlusCircle size={16} />
                        Create New Case
                        <ArrowRight size={14} />
                    </button>
                </div>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                <StatCard
                    icon={Briefcase}
                    label="Total Cases"
                    value={stats.total}
                    color="text-slate-800"
                    gradient="bg-gradient-to-br from-indigo-500 to-indigo-600 shadow-indigo-200"
                    delay={0}
                />
                <StatCard
                    icon={CheckCircle}
                    label="Open Cases"
                    value={stats.open}
                    color="text-emerald-600"
                    gradient="bg-gradient-to-br from-emerald-500 to-emerald-600 shadow-emerald-200"
                    delay={100}
                />
                <StatCard
                    icon={XCircle}
                    label="Closed Cases"
                    value={stats.closed}
                    color="text-slate-500"
                    gradient="bg-gradient-to-br from-slate-500 to-slate-600 shadow-slate-200"
                    delay={200}
                />
            </div>

            {/* Recent Cases */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200/60 animate-slide-up" style={{ animationDelay: '300ms' }}>
                <div className="flex items-center justify-between p-5 border-b border-slate-100">
                    <div>
                        <h3 className="text-base font-semibold text-slate-800">Recent Cases</h3>
                        <p className="text-xs text-slate-400 mt-0.5">Latest activity across your cases</p>
                    </div>
                    <button
                        id="dashboard-view-all-cases"
                        onClick={() => navigate('/cases')}
                        className="text-xs font-medium text-indigo-600 hover:text-indigo-700 flex items-center gap-1 transition-colors"
                    >
                        View All
                        <ArrowRight size={13} />
                    </button>
                </div>

                {recentCases.length === 0 ? (
                    <div className="p-10 text-center">
                        <Briefcase size={36} className="text-slate-200 mx-auto mb-3" />
                        <p className="text-sm text-slate-500">No cases yet. Create your first case to get started.</p>
                        <button
                            onClick={() => navigate('/create-case')}
                            className="mt-4 text-sm text-indigo-600 font-medium hover:text-indigo-700"
                        >
                            + Create Case
                        </button>
                    </div>
                ) : (
                    <div className="divide-y divide-slate-50">
                        {recentCases.map((c, i) => (
                            <div
                                key={c.id}
                                className="flex items-center justify-between px-5 py-3.5 hover:bg-slate-50/80 transition-colors group cursor-pointer"
                                onClick={() => navigate('/cases')}
                            >
                                <div className="flex items-center gap-3 min-w-0">
                                    <div className={`h-8 w-8 rounded-lg flex items-center justify-center flex-shrink-0 ${c.status === 'open' ? 'bg-emerald-50 text-emerald-600' : 'bg-slate-100 text-slate-400'
                                        }`}>
                                        {c.status === 'open' ? <CheckCircle size={15} /> : <XCircle size={15} />}
                                    </div>
                                    <div className="min-w-0">
                                        <p className="text-sm font-medium text-slate-700 truncate group-hover:text-indigo-600 transition-colors">{c.title}</p>
                                        <p className="text-xs text-slate-400 truncate">{c.client_name}</p>
                                    </div>
                                </div>
                                <div className="flex items-center gap-3 flex-shrink-0">
                                    <span className={`text-xs font-medium px-2 py-0.5 rounded-md ${c.status === 'open' ? 'text-emerald-700 bg-emerald-50' : 'text-slate-500 bg-slate-100'
                                        }`}>
                                        {c.status}
                                    </span>
                                    <ArrowRight size={14} className="text-slate-300 group-hover:text-indigo-400 transition-colors" />
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default Dashboard;
