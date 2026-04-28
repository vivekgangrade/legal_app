import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import CaseCard from '../components/CaseCard';
import { getCases } from '../services/api';
import { Search, Filter, PlusCircle, Briefcase, RefreshCw } from 'lucide-react';

const CaseList = () => {
    const navigate = useNavigate();
    const [cases, setCases] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filter, setFilter] = useState('all');
    const [search, setSearch] = useState('');

    const fetchCases = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await getCases();
            setCases(Array.isArray(data) ? data : []);
        } catch (err) {
            console.error('Failed to fetch cases:', err);
            setError('Failed to load cases. Please try again later.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCases();
    }, []);

    const handleStatusChange = (caseId, newStatus) => {
        setCases(prev =>
            prev.map(c => c.id === caseId ? { ...c, status: newStatus } : c)
        );
    };

    const handleDelete = (caseId) => {
        setCases(prev => prev.filter(c => c.id !== caseId));
    };

    const filteredCases = cases.filter(c => {
        const matchesFilter = filter === 'all' || (c.status && c.status.toLowerCase() === filter);
        const matchesSearch = c.title.toLowerCase().includes(search.toLowerCase()) ||
            (c.description && c.description.toLowerCase().includes(search.toLowerCase())) ||
            (c.client_name && c.client_name.toLowerCase().includes(search.toLowerCase()));
        return matchesFilter && matchesSearch;
    });

    const openCount = cases.filter(c => c.status === 'open').length;
    const closedCount = cases.filter(c => c.status === 'closed').length;

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Cases</h2>
                    <p className="text-slate-500 text-sm mt-0.5">
                        {cases.length} total &middot; {openCount} open &middot; {closedCount} closed
                    </p>
                </div>
                <div className="flex gap-2">
                    <button
                        id="case-list-refresh"
                        onClick={fetchCases}
                        className="h-10 w-10 rounded-xl border border-slate-200 flex items-center justify-center text-slate-400 hover:text-indigo-600 hover:border-indigo-200 hover:bg-indigo-50 transition-all duration-200"
                        title="Refresh"
                    >
                        <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
                    </button>
                    <button
                        id="case-list-create"
                        onClick={() => navigate('/create-case')}
                        className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-indigo-600 to-violet-600 text-white text-sm font-medium rounded-xl hover:from-indigo-500 hover:to-violet-500 transition-all duration-200 shadow-lg shadow-indigo-200"
                    >
                        <PlusCircle size={16} />
                        New Case
                    </button>
                </div>
            </div>

            {/* Search & Filter Bar */}
            <div className="bg-white rounded-xl border border-slate-200/60 p-3 flex flex-col sm:flex-row gap-3 shadow-sm">
                <div className="relative flex-1">
                    <Search className="absolute left-3.5 top-1/2 transform -translate-y-1/2 text-slate-400" size={16} />
                    <input
                        id="case-search"
                        type="text"
                        placeholder="Search by title, description, or client..."
                        className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/30 focus:border-indigo-300 text-sm text-slate-700 placeholder-slate-400 transition-all"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                </div>

                <div className="flex gap-1.5 p-1 bg-slate-50 rounded-lg border border-slate-200">
                    {[
                        { value: 'all', label: 'All' },
                        { value: 'open', label: 'Open' },
                        { value: 'closed', label: 'Closed' },
                    ].map(opt => (
                        <button
                            key={opt.value}
                            id={`case-filter-${opt.value}`}
                            onClick={() => setFilter(opt.value)}
                            className={`px-4 py-2 text-xs font-semibold rounded-md transition-all duration-200 ${filter === opt.value
                                ? 'bg-white text-indigo-600 shadow-sm border border-slate-200'
                                : 'text-slate-500 hover:text-slate-700'
                                }`}
                        >
                            {opt.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Case Grid */}
            {loading ? (
                <div className="flex justify-center items-center h-64">
                    <div className="flex flex-col items-center gap-3">
                        <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center animate-pulse">
                            <Briefcase size={20} className="text-white" />
                        </div>
                        <p className="text-sm text-slate-400">Loading cases...</p>
                    </div>
                </div>
            ) : error ? (
                <div className="text-center py-12 bg-red-50/50 rounded-xl border border-red-200/50 animate-scale-in">
                    <p className="text-red-500 font-medium">{error}</p>
                    <button
                        onClick={fetchCases}
                        className="mt-3 text-sm text-red-600 underline hover:no-underline"
                    >
                        Try again
                    </button>
                </div>
            ) : filteredCases.length === 0 ? (
                <div className="text-center py-16 bg-white rounded-xl border border-dashed border-slate-300 animate-fade-in">
                    <Briefcase size={40} className="text-slate-200 mx-auto mb-3" />
                    <p className="text-slate-500 font-medium">No cases found</p>
                    <p className="text-slate-400 text-sm mt-1">
                        {search || filter !== 'all' ? 'Try adjusting your search or filters.' : 'Create your first case to get started.'}
                    </p>
                    {!search && filter === 'all' && (
                        <button
                            onClick={() => navigate('/create-case')}
                            className="mt-4 inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
                        >
                            <PlusCircle size={16} />
                            Create Case
                        </button>
                    )}
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
                    {filteredCases.map(caseItem => (
                        <CaseCard
                            key={caseItem.id}
                            caseItem={caseItem}
                            onStatusChange={handleStatusChange}
                            onDelete={handleDelete}
                        />
                    ))}
                </div>
            )}
        </div>
    );
};

export default CaseList;
