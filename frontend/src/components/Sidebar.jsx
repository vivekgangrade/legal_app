import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Briefcase, PlusCircle, LogOut, Scale, Menu, X } from 'lucide-react';

const navItems = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/cases', label: 'Cases', icon: Briefcase, end: true },
    { to: '/create-case', label: 'Create Case', icon: PlusCircle },
];

const Sidebar = () => {
    const navigate = useNavigate();
    const [mobileOpen, setMobileOpen] = useState(false);

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    const sidebarContent = (
        <>
            {/* Logo */}
            <div className="h-16 flex items-center gap-3 px-5 border-b border-slate-800/50">
                <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
                    <Scale size={18} className="text-white" />
                </div>
                <span className="text-lg font-bold bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent tracking-tight">LegalCMS</span>
            </div>

            {/* Navigation */}
            <nav className="flex-1 overflow-y-auto py-5 px-3">
                <p className="text-xs uppercase tracking-wider text-slate-500 font-semibold px-3 mb-3">Menu</p>
                <ul className="space-y-1">
                    {navItems.map(item => (
                        <li key={item.to}>
                            <NavLink
                                to={item.to}
                                end={item.end}
                                onClick={() => setMobileOpen(false)}
                                className={({ isActive }) =>
                                    `group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 ${isActive
                                        ? 'bg-gradient-to-r from-indigo-600/20 to-violet-600/10 text-indigo-400 shadow-sm'
                                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                                    }`
                                }
                            >
                                {({ isActive }) => (
                                    <>
                                        <item.icon
                                            size={19}
                                            className={`mr-3 transition-colors ${isActive ? 'text-indigo-400' : 'text-slate-500 group-hover:text-slate-300'}`}
                                        />
                                        {item.label}
                                        {isActive && (
                                            <div className="ml-auto w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse" />
                                        )}
                                    </>
                                )}
                            </NavLink>
                        </li>
                    ))}
                </ul>
            </nav>

            {/* Footer */}
            <div className="p-3 border-t border-slate-800/50">
                <button
                    onClick={handleLogout}
                    className="flex items-center w-full px-3 py-2.5 text-sm font-medium text-slate-400 rounded-lg hover:bg-red-500/10 hover:text-red-400 transition-all duration-200 group"
                >
                    <LogOut size={19} className="mr-3 text-slate-500 group-hover:text-red-400 transition-colors" />
                    Logout
                </button>
            </div>
        </>
    );

    return (
        <>
            {/* Mobile toggle */}
            <button
                id="sidebar-mobile-toggle"
                onClick={() => setMobileOpen(!mobileOpen)}
                className="md:hidden fixed top-4 left-4 z-50 h-10 w-10 rounded-lg bg-slate-900 text-slate-300 flex items-center justify-center shadow-lg border border-slate-700"
            >
                {mobileOpen ? <X size={20} /> : <Menu size={20} />}
            </button>

            {/* Mobile overlay */}
            {mobileOpen && (
                <div
                    className="md:hidden fixed inset-0 bg-black/50 z-30 animate-fade-in"
                    onClick={() => setMobileOpen(false)}
                />
            )}

            {/* Mobile sidebar */}
            <aside className={`md:hidden fixed inset-y-0 left-0 z-40 w-64 bg-slate-900 flex flex-col transform transition-transform duration-300 ${mobileOpen ? 'translate-x-0' : '-translate-x-full'}`}>
                {sidebarContent}
            </aside>

            {/* Desktop sidebar */}
            <aside className="w-64 bg-slate-900 hidden md:flex flex-col flex-shrink-0 animate-slide-right">
                {sidebarContent}
            </aside>
        </>
    );
};

export default Sidebar;
