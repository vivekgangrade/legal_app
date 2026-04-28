import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../services/api';
import { Lock, User, Scale, ArrowRight } from 'lucide-react';

const Login = () => {
    const navigate = useNavigate();
    const [isLoading, setIsLoading] = useState(false);
    const [credentials, setCredentials] = useState({ username: '', password: '' });
    const [error, setError] = useState('');

    const handleChange = (e) => {
        setCredentials(prev => ({ ...prev, [e.target.name]: e.target.value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        try {
            const data = await login(credentials.username, credentials.password);
            localStorage.setItem('token', data.access_token);
            navigate('/dashboard');
        } catch (err) {
            console.error('Login failed:', err);
            if (!err.response) {
                setError('Cannot connect to server. Is the backend running?');
            } else if (err.response.status === 401 || err.response.status === 400) {
                setError('Invalid username or password.');
            } else {
                setError(`Login failed: ${err.response.data?.detail || 'Unknown error'}`);
            }
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex bg-slate-900 relative overflow-hidden">
            {/* Animated background */}
            <div className="absolute inset-0">
                <div className="absolute top-0 -left-40 w-96 h-96 bg-indigo-600/20 rounded-full blur-3xl animate-pulse" />
                <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-violet-600/15 rounded-full blur-3xl" style={{ animation: 'pulse 4s ease-in-out infinite' }} />
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-72 h-72 bg-indigo-500/10 rounded-full blur-3xl" />
            </div>

            {/* Left panel - Branding */}
            <div className="hidden lg:flex flex-1 items-center justify-center relative z-10 p-12">
                <div className="max-w-md animate-slide-right">
                    <div className="h-14 w-14 rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-2xl shadow-indigo-500/40 mb-8">
                        <Scale size={28} className="text-white" />
                    </div>
                    <h1 className="text-4xl font-bold text-white mb-4 leading-tight">
                        Legal Case
                        <span className="block bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
                            Management System
                        </span>
                    </h1>
                    <p className="text-slate-400 text-lg leading-relaxed">
                        Streamline your legal workflow with powerful case tracking, client management, and real-time analytics.
                    </p>
                    <div className="mt-10 grid grid-cols-3 gap-6">
                        {[
                            { value: '99.9%', label: 'Uptime' },
                            { value: '500+', label: 'Cases' },
                            { value: '24/7', label: 'Support' },
                        ].map((stat) => (
                            <div key={stat.label} className="text-center">
                                <p className="text-2xl font-bold text-white">{stat.value}</p>
                                <p className="text-xs text-slate-500 mt-1 uppercase tracking-wider">{stat.label}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Right panel - Login form */}
            <div className="flex-1 flex items-center justify-center relative z-10 px-4 sm:px-6 lg:px-12">
                <div className="w-full max-w-md animate-slide-up">
                    {/* Mobile logo */}
                    <div className="lg:hidden flex items-center gap-3 mb-10 justify-center">
                        <div className="h-11 w-11 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
                            <Scale size={22} className="text-white" />
                        </div>
                        <span className="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">LegalCMS</span>
                    </div>

                    <div className="bg-white/[0.07] backdrop-blur-xl rounded-2xl p-8 border border-white/10 shadow-2xl">
                        <div className="mb-8">
                            <h2 className="text-2xl font-bold text-white">Welcome back</h2>
                            <p className="text-slate-400 mt-1.5 text-sm">Sign in to continue to your dashboard</p>
                        </div>

                        <form onSubmit={handleSubmit} className="space-y-5">
                            <div>
                                <label htmlFor="username" className="block text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">
                                    Username
                                </label>
                                <div className="relative">
                                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                                        <User className="h-4 w-4 text-slate-500" />
                                    </div>
                                    <input
                                        id="username"
                                        name="username"
                                        type="text"
                                        required
                                        className="w-full pl-10 pr-4 py-3 bg-white/[0.06] border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition-all text-sm"
                                        placeholder="Enter your username"
                                        value={credentials.username}
                                        onChange={handleChange}
                                    />
                                </div>
                            </div>

                            <div>
                                <label htmlFor="password" className="block text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">
                                    Password
                                </label>
                                <div className="relative">
                                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                                        <Lock className="h-4 w-4 text-slate-500" />
                                    </div>
                                    <input
                                        id="password"
                                        name="password"
                                        type="password"
                                        required
                                        className="w-full pl-10 pr-4 py-3 bg-white/[0.06] border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition-all text-sm"
                                        placeholder="Enter your password"
                                        value={credentials.password}
                                        onChange={handleChange}
                                    />
                                </div>
                            </div>

                            {error && (
                                <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl animate-scale-in">
                                    <p className="text-red-400 text-sm text-center">{error}</p>
                                </div>
                            )}

                            <button
                                id="login-submit"
                                type="submit"
                                disabled={isLoading}
                                className="w-full flex items-center justify-center gap-2 py-3 px-4 bg-gradient-to-r from-indigo-600 to-violet-600 text-white font-medium rounded-xl hover:from-indigo-500 hover:to-violet-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 focus:ring-indigo-500 disabled:opacity-60 disabled:cursor-not-allowed transition-all duration-200 shadow-lg shadow-indigo-600/25 text-sm"
                            >
                                {isLoading ? (
                                    <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                ) : (
                                    <>
                                        Sign in
                                        <ArrowRight size={16} />
                                    </>
                                )}
                            </button>
                        </form>

                        <p className="mt-6 text-center text-xs text-slate-500">
                            Default credentials: <span className="text-slate-400 font-medium">admin</span> / <span className="text-slate-400 font-medium">password</span>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;
