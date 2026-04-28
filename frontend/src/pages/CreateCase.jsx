import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createCase } from '../services/api';
import { Save, X, FileText, User, AlignLeft, CheckCircle } from 'lucide-react';

const CreateCase = () => {
    const navigate = useNavigate();
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        client_name: '',
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        if (error) setError('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        try {
            // Always create with status "open" — no user choice needed
            await createCase({ ...formData, status: 'open' });
            setSuccess(true);
            setTimeout(() => navigate('/cases'), 1500);
        } catch (err) {
            console.error('Failed to create case:', err);
            if (err.response?.data?.detail) {
                const detail = err.response.data.detail;
                if (Array.isArray(detail)) {
                    setError(detail.map(d => d.msg).join(', '));
                } else {
                    setError(String(detail));
                }
            } else {
                setError('Failed to create case. Please try again.');
            }
        } finally {
            setIsLoading(false);
        }
    };

    const isFormValid = formData.title.trim().length >= 3 && formData.client_name.trim().length > 0;

    if (success) {
        return (
            <div className="max-w-2xl mx-auto mt-12 animate-scale-in">
                <div className="bg-white rounded-2xl shadow-lg border border-emerald-200/60 p-10 text-center">
                    <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center mx-auto shadow-lg shadow-emerald-200 mb-5">
                        <CheckCircle size={32} className="text-white" />
                    </div>
                    <h3 className="text-xl font-bold text-slate-800">Case Created Successfully!</h3>
                    <p className="text-slate-500 mt-2 text-sm">Redirecting you to the cases list...</p>
                    <div className="mt-5 flex justify-center">
                        <div className="h-1 w-32 bg-slate-100 rounded-full overflow-hidden">
                            <div className="h-full bg-emerald-500 rounded-full" style={{ animation: 'expandWidth 1.5s ease-out forwards' }} />
                        </div>
                    </div>
                </div>
                <style>{`
                    @keyframes expandWidth {
                        from { width: 0%; }
                        to { width: 100%; }
                    }
                `}</style>
            </div>
        );
    }

    return (
        <div className="max-w-2xl mx-auto animate-slide-up">
            {/* Header */}
            <div className="mb-6">
                <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Create New Case</h2>
                <p className="text-slate-500 text-sm mt-1">Fill in the details below. The case will be created with <span className="text-emerald-600 font-medium">Open</span> status.</p>
            </div>

            {/* Form Card */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200/60 overflow-hidden">
                {/* Status indicator bar */}
                <div className="h-1 bg-gradient-to-r from-indigo-500 via-violet-500 to-purple-500" />

                <div className="p-6 md:p-8">
                    {error && (
                        <div className="mb-5 p-4 bg-red-50/80 border border-red-200/60 text-red-600 rounded-xl text-sm animate-scale-in flex items-start gap-2">
                            <X size={16} className="mt-0.5 flex-shrink-0" />
                            <span>{error}</span>
                        </div>
                    )}

                    <form onSubmit={handleSubmit}>
                        <div className="space-y-5">
                            {/* Title */}
                            <div>
                                <label htmlFor="title" className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                                    <FileText size={13} />
                                    Case Title
                                </label>
                                <input
                                    type="text"
                                    id="title"
                                    name="title"
                                    required
                                    minLength={3}
                                    className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/30 focus:border-indigo-300 focus:bg-white outline-none transition-all text-sm text-slate-800 placeholder-slate-400"
                                    placeholder="e.g. Smith vs. Jones — Contract Dispute"
                                    value={formData.title}
                                    onChange={handleChange}
                                />
                                <p className="mt-1.5 text-xs text-slate-400">Minimum 3 characters</p>
                            </div>

                            {/* Client Name */}
                            <div>
                                <label htmlFor="client_name" className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                                    <User size={13} />
                                    Client Name
                                </label>
                                <input
                                    type="text"
                                    id="client_name"
                                    name="client_name"
                                    required
                                    className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/30 focus:border-indigo-300 focus:bg-white outline-none transition-all text-sm text-slate-800 placeholder-slate-400"
                                    placeholder="e.g. John Doe"
                                    value={formData.client_name}
                                    onChange={handleChange}
                                />
                            </div>

                            {/* Description */}
                            <div>
                                <label htmlFor="description" className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                                    <AlignLeft size={13} />
                                    Description
                                </label>
                                <textarea
                                    id="description"
                                    name="description"
                                    rows="5"
                                    className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/30 focus:border-indigo-300 focus:bg-white outline-none transition-all resize-none text-sm text-slate-800 placeholder-slate-400 leading-relaxed"
                                    placeholder="Describe the case details, relevant facts, and any important notes..."
                                    value={formData.description}
                                    onChange={handleChange}
                                ></textarea>
                            </div>

                            {/* Status Preview */}
                            <div className="bg-slate-50 rounded-xl p-4 border border-slate-200/60">
                                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Status</p>
                                <div className="flex items-center gap-2">
                                    <span className="w-2 h-2 rounded-full bg-emerald-500" />
                                    <span className="text-sm font-medium text-emerald-700">Open</span>
                                    <span className="text-xs text-slate-400 ml-1">— You can close this case later from the Cases page</span>
                                </div>
                            </div>
                        </div>

                        {/* Actions */}
                        <div className="mt-8 flex items-center justify-end gap-3 pt-5 border-t border-slate-100">
                            <button
                                id="create-case-cancel"
                                type="button"
                                onClick={() => navigate('/cases')}
                                className="px-5 py-2.5 text-sm font-medium text-slate-600 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 hover:border-slate-300 focus:outline-none transition-all duration-200 flex items-center gap-2"
                            >
                                <X size={16} />
                                Cancel
                            </button>
                            <button
                                id="create-case-submit"
                                type="submit"
                                disabled={isLoading || !isFormValid}
                                className="px-6 py-2.5 text-sm font-medium text-white bg-gradient-to-r from-indigo-600 to-violet-600 rounded-xl hover:from-indigo-500 hover:to-violet-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg shadow-indigo-200"
                            >
                                {isLoading ? (
                                    <>
                                        <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                        Creating...
                                    </>
                                ) : (
                                    <>
                                        <Save size={16} />
                                        Create Case
                                    </>
                                )}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default CreateCase;
