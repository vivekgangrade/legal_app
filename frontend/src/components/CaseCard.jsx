import React, { useState } from 'react';
import { Clock, CheckCircle, XCircle, ChevronRight, User, Trash2, X as XIcon } from 'lucide-react';
import { updateCase, deleteCase } from '../services/api';

const CaseCard = ({ caseItem, onStatusChange, onDelete }) => {
    const [showConfirmDelete, setShowConfirmDelete] = useState(false);
    const [isClosing, setIsClosing] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);

    const statusConfig = {
        open: {
            color: 'text-emerald-700 bg-emerald-50 border-emerald-200',
            icon: <CheckCircle size={14} className="mr-1.5" />,
            dot: 'bg-emerald-500',
        },
        closed: {
            color: 'text-slate-500 bg-slate-100 border-slate-200',
            icon: <XCircle size={14} className="mr-1.5" />,
            dot: 'bg-slate-400',
        },
        pending: {
            color: 'text-amber-700 bg-amber-50 border-amber-200',
            icon: <Clock size={14} className="mr-1.5" />,
            dot: 'bg-amber-500',
        },
    };

    const status = caseItem.status?.toLowerCase() || 'open';
    const config = statusConfig[status] || statusConfig.open;

    const handleCloseCase = async () => {
        setIsClosing(true);
        try {
            await updateCase(caseItem.id, { status: 'closed' });
            if (onStatusChange) onStatusChange(caseItem.id, 'closed');
        } catch (err) {
            console.error('Failed to close case:', err);
        } finally {
            setIsClosing(false);
        }
    };

    const handleReopenCase = async () => {
        setIsClosing(true);
        try {
            await updateCase(caseItem.id, { status: 'open' });
            if (onStatusChange) onStatusChange(caseItem.id, 'open');
        } catch (err) {
            console.error('Failed to reopen case:', err);
        } finally {
            setIsClosing(false);
        }
    };

    const handleDelete = async () => {
        setIsDeleting(true);
        try {
            await deleteCase(caseItem.id);
            if (onDelete) onDelete(caseItem.id);
        } catch (err) {
            console.error('Failed to delete case:', err);
        } finally {
            setIsDeleting(false);
            setShowConfirmDelete(false);
        }
    };

    const formattedDate = caseItem.created_at
        ? new Date(caseItem.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
        : new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });

    return (
        <div className="group bg-white rounded-xl p-5 shadow-sm border border-slate-200/80 hover:shadow-lg hover:border-indigo-200/60 transition-all duration-300 animate-slide-up relative">
            {/* Delete Confirmation Overlay */}
            {showConfirmDelete && (
                <div className="absolute inset-0 bg-white/95 backdrop-blur-sm rounded-xl flex flex-col items-center justify-center z-10 animate-fade-in p-4">
                    <Trash2 size={28} className="text-red-400 mb-3" />
                    <p className="text-sm font-medium text-slate-700 text-center mb-1">Delete this case?</p>
                    <p className="text-xs text-slate-500 text-center mb-4">This action cannot be undone.</p>
                    <div className="flex gap-2">
                        <button
                            onClick={() => setShowConfirmDelete(false)}
                            className="px-4 py-1.5 text-xs font-medium rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            onClick={handleDelete}
                            disabled={isDeleting}
                            className="px-4 py-1.5 text-xs font-medium rounded-lg bg-red-500 text-white hover:bg-red-600 transition-colors disabled:opacity-50"
                        >
                            {isDeleting ? 'Deleting...' : 'Delete'}
                        </button>
                    </div>
                </div>
            )}

            {/* Header */}
            <div className="flex justify-between items-start mb-3">
                <div className="flex-1 min-w-0 mr-3">
                    <h3 className="text-base font-semibold text-slate-800 truncate group-hover:text-indigo-700 transition-colors">
                        {caseItem.title}
                    </h3>
                    <div className="flex items-center gap-1.5 mt-1 text-xs text-slate-400">
                        <User size={12} />
                        <span>{caseItem.client_name || 'Unknown Client'}</span>
                    </div>
                </div>
                <span className={`flex items-center text-xs font-medium px-2.5 py-1 rounded-lg border ${config.color} flex-shrink-0`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${config.dot} mr-1.5`} />
                    {status.charAt(0).toUpperCase() + status.slice(1)}
                </span>
            </div>

            {/* Description */}
            <p className="text-slate-600 text-sm mb-4 line-clamp-2 leading-relaxed">
                {caseItem.description || 'No description provided.'}
            </p>

            {/* Footer */}
            <div className="flex justify-between items-center text-xs text-slate-400 border-t border-slate-100 pt-3">
                <span className="font-mono">#{String(caseItem.id).padStart(4, '0')}</span>
                <span>{formattedDate}</span>
            </div>

            {/* Actions */}
            <div className="mt-3 flex gap-2">
                {status === 'open' && (
                    <button
                        onClick={handleCloseCase}
                        disabled={isClosing}
                        className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-medium rounded-lg border border-slate-200 text-slate-600 hover:bg-amber-50 hover:text-amber-700 hover:border-amber-200 transition-all duration-200 disabled:opacity-50"
                    >
                        <XCircle size={14} />
                        {isClosing ? 'Closing...' : 'Close Case'}
                    </button>
                )}
                {status === 'closed' && (
                    <button
                        onClick={handleReopenCase}
                        disabled={isClosing}
                        className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-medium rounded-lg border border-slate-200 text-slate-600 hover:bg-emerald-50 hover:text-emerald-700 hover:border-emerald-200 transition-all duration-200 disabled:opacity-50"
                    >
                        <CheckCircle size={14} />
                        {isClosing ? 'Reopening...' : 'Reopen Case'}
                    </button>
                )}
                <button
                    onClick={() => setShowConfirmDelete(true)}
                    className="flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-medium rounded-lg border border-slate-200 text-slate-400 hover:bg-red-50 hover:text-red-600 hover:border-red-200 transition-all duration-200"
                >
                    <Trash2 size={14} />
                </button>
            </div>
        </div>
    );
};

export default CaseCard;
