import React, { useState, useEffect } from 'react';
import CaseCard from '../components/CaseCard';
import { getCases } from '../services/api';
import { Search, Filter } from 'lucide-react';

const CaseList = () => {
    const [cases, setCases] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filter, setFilter] = useState('all');
    const [search, setSearch] = useState('');

    useEffect(() => {
        const fetchCases = async () => {
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

        fetchCases();
    }, []);

    const filteredCases = cases.filter(c => {
        const matchesFilter = filter === 'all' || (c.status && c.status.toLowerCase() === filter);
        const matchesSearch = c.title.toLowerCase().includes(search.toLowerCase()) ||
            (c.description && c.description.toLowerCase().includes(search.toLowerCase()));
        return matchesFilter && matchesSearch;
    });

    return (
        <div>
            <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-gray-900">Cases</h2>
                    <p className="text-gray-500">Manage and view all legal cases</p>
                </div>

                <div className="flex gap-2">
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                        <input
                            type="text"
                            placeholder="Search cases..."
                            className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm w-full md:w-64"
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                        />
                    </div>

                    <div className="relative">
                        <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                        <select
                            className="pl-10 pr-8 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm appearance-none bg-white"
                            value={filter}
                            onChange={(e) => setFilter(e.target.value)}
                        >
                            <option value="all">All Status</option>
                            <option value="open">Open</option>
                            <option value="closed">Closed</option>
                        </select>
                    </div>
                </div>
            </div>

            {loading ? (
                <div className="flex justify-center items-center h-64">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
                </div>
            ) : error ? (
                <div className="text-center py-12 bg-red-50 rounded-lg border border-red-200">
                    <p className="text-red-600">{error}</p>
                </div>
            ) : filteredCases.length === 0 ? (
                <div className="text-center py-12 bg-white rounded-lg border border-dashed border-gray-300">
                    <p className="text-gray-500">No cases found matching your criteria.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filteredCases.map(caseItem => (
                        <CaseCard key={caseItem.id} caseItem={caseItem} />
                    ))}
                </div>
            )}
        </div>
    );
};

export default CaseList;
