import React from 'react';
import { Clock, CheckCircle, XCircle } from 'lucide-react';

const CaseCard = ({ caseItem }) => {
    const getStatusColor = (status) => {
        switch (status.toLowerCase()) {
            case 'open':
                return 'text-green-600 bg-green-50';
            case 'closed':
                return 'text-red-600 bg-red-50';
            default:
                return 'text-gray-600 bg-gray-50';
        }
    };

    const getStatusIcon = (status) => {
        switch (status.toLowerCase()) {
            case 'open':
                return <CheckCircle size={16} className="mr-1" />;
            case 'closed':
                return <XCircle size={16} className="mr-1" />;
            default:
                return <Clock size={16} className="mr-1" />;
        }
    };

    return (
        <div className="bg-white rounded-lg p-5 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-3">
                <h3 className="text-lg font-semibold text-gray-800">{caseItem.title}</h3>
                <span className={`flex items-center text-xs font-medium px-2.5 py-0.5 rounded ${getStatusColor(caseItem.status)}`}>
                    {getStatusIcon(caseItem.status)}
                    {caseItem.status.toUpperCase()}
                </span>
            </div>
            <p className="text-gray-600 text-sm mb-4 line-clamp-2">{caseItem.description}</p>
            <div className="flex justify-between items-center text-xs text-gray-500 border-t pt-3">
                <span>ID: #{caseItem.id}</span>
                <span>{new Date().toLocaleDateString()}</span>
            </div>
        </div>
    );
};

export default CaseCard;
