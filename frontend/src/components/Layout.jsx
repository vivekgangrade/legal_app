import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import { Bell, Search } from 'lucide-react';

const pageTitles = {
    '/dashboard': 'Dashboard',
    '/cases': 'Case Management',
    '/create-case': 'Create New Case',
};

const Layout = () => {
    const location = useLocation();
    const currentPath = location.pathname;
    const pageTitle = Object.entries(pageTitles).find(([path]) => currentPath.startsWith(path))?.[1] || 'LegalCMS';

    return (
        <div className="flex h-screen bg-slate-50">
            <Sidebar />
            <div className="flex-1 flex flex-col overflow-hidden">
                <header className="h-16 bg-white/80 backdrop-blur-md border-b border-slate-200/60 flex items-center justify-between px-6 md:px-8 sticky top-0 z-20">
                    <div className="flex items-center gap-4 md:ml-0 ml-12">
                        <h1 className="text-lg font-semibold text-slate-800 tracking-tight">{pageTitle}</h1>
                    </div>
                    <div className="flex items-center gap-3">
                        <button
                            id="header-notifications"
                            className="relative h-9 w-9 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-indigo-600 hover:border-indigo-200 hover:bg-indigo-50 transition-all duration-200"
                        >
                            <Bell size={17} />
                            <span className="absolute -top-1 -right-1 h-4 w-4 rounded-full bg-red-500 text-white text-[10px] font-bold flex items-center justify-center">3</span>
                        </button>
                        <div className="h-6 w-px bg-slate-200" />
                        <div className="flex items-center gap-2">
                            <span className="text-sm text-slate-600 font-medium hidden sm:block">Admin</span>
                            <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center text-white font-bold text-sm shadow-md shadow-indigo-200">
                                A
                            </div>
                        </div>
                    </div>
                </header>
                <main className="flex-1 overflow-x-hidden overflow-y-auto bg-slate-50 p-4 md:p-6">
                    <div className="animate-fade-in">
                        <Outlet />
                    </div>
                </main>
            </div>
        </div>
    );
};

export default Layout;
