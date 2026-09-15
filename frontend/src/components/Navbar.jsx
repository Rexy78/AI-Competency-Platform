import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Sparkles, LayoutDashboard, FileText, Target, Map, Briefcase, 
  SearchCode, Wand2, FileCode, LogOut, User, ShieldCheck, ChevronDown, Menu, X 
} from 'lucide-react';

const Navbar = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="sticky top-0 z-50 glass-card border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl gradient-bg flex items-center justify-center text-white shadow-glow group-hover:scale-105 transition-all">
              <Sparkles className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold text-lg tracking-tight text-white">Resume<span className="gradient-text">AI</span></span>
                <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">PRO</span>
              </div>
              <p className="text-[10px] text-slate-400 hidden sm:block">AI Resume & Career Assistant</p>
            </div>
          </Link>

          {/* Desktop Auth Links */}
          {isAuthenticated ? (
            <div className="hidden md:flex items-center gap-4">
              <Link
                to="/dashboard"
                className={`px-3.5 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all ${
                  location.pathname === '/dashboard'
                    ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/30'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                }`}
              >
                <LayoutDashboard className="w-4 h-4" />
                <span>Dashboard</span>
              </Link>

              <Link
                to="/upload"
                className={`px-3.5 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all ${
                  location.pathname === '/upload'
                    ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/30'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                }`}
              >
                <FileText className="w-4 h-4" />
                <span>Analyze Resume</span>
              </Link>

              <Link
                to="/builder"
                className={`px-3.5 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all ${
                  location.pathname === '/builder'
                    ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/30'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                }`}
              >
                <FileCode className="w-4 h-4" />
                <span>Resume Builder</span>
              </Link>

              {/* User Dropdown */}
              <div className="relative">
                <button
                  onClick={() => setDropdownOpen(!dropdownOpen)}
                  className="flex items-center gap-2.5 px-3 py-1.5 rounded-xl bg-slate-800/80 border border-slate-700/80 text-white text-xs font-semibold hover:border-slate-600 transition-all"
                >
                  <div className="w-7 h-7 rounded-lg bg-indigo-600 text-white flex items-center justify-center font-bold text-xs uppercase">
                    {user?.full_name?.charAt(0) || 'U'}
                  </div>
                  <span className="max-w-[120px] truncate">{user?.full_name || 'Account'}</span>
                  <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                </button>

                {dropdownOpen && (
                  <div className="absolute right-0 mt-2 w-56 rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl p-2 z-50 space-y-1">
                    <div className="px-3 py-2 border-b border-slate-800">
                      <p className="text-xs font-bold text-white truncate">{user?.full_name}</p>
                      <p className="text-[11px] text-slate-400 truncate">{user?.email}</p>
                    </div>

                    <Link
                      to="/dashboard"
                      onClick={() => setDropdownOpen(false)}
                      className="w-full text-left px-3 py-2 rounded-xl text-xs text-slate-300 hover:bg-slate-800 flex items-center gap-2"
                    >
                      <LayoutDashboard className="w-4 h-4 text-indigo-400" />
                      <span>My Dashboard</span>
                    </Link>

                    {user?.is_admin && (
                      <Link
                        to="/admin"
                        onClick={() => setDropdownOpen(false)}
                        className="w-full text-left px-3 py-2 rounded-xl text-xs text-amber-400 hover:bg-slate-800 flex items-center gap-2"
                      >
                        <ShieldCheck className="w-4 h-4 text-amber-400" />
                        <span>Admin Console</span>
                      </Link>
                    )}

                    <button
                      onClick={handleLogout}
                      className="w-full text-left px-3 py-2 rounded-xl text-xs text-rose-400 hover:bg-rose-500/10 flex items-center gap-2"
                    >
                      <LogOut className="w-4 h-4 text-rose-400" />
                      <span>Sign Out</span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="hidden md:flex items-center gap-3">
              <Link
                to="/login"
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-300 hover:text-white transition-colors"
              >
                Sign In
              </Link>
              <Link
                to="/signup"
                className="px-5 py-2.5 rounded-xl text-xs font-bold text-white gradient-bg shadow-glow hover:opacity-95 transition-all"
              >
                Get Started Free
              </Link>
            </div>
          )}

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-slate-900 border-b border-slate-800 px-4 pt-2 pb-6 space-y-3">
          {isAuthenticated ? (
            <>
              <div className="px-3 py-2 bg-slate-800/60 rounded-xl border border-slate-700/60 mb-2">
                <p className="text-xs font-bold text-white">{user?.full_name}</p>
                <p className="text-[11px] text-slate-400">{user?.email}</p>
              </div>
              <Link to="/dashboard" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2 rounded-xl text-sm font-semibold text-slate-300 hover:bg-slate-800">Dashboard</Link>
              <Link to="/upload" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2 rounded-xl text-sm font-semibold text-slate-300 hover:bg-slate-800">Analyze Resume</Link>
              <Link to="/skill-gap" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2 rounded-xl text-sm font-semibold text-slate-300 hover:bg-slate-800">Skill Gap Radar</Link>
              <Link to="/roadmap" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2 rounded-xl text-sm font-semibold text-slate-300 hover:bg-slate-800">Career Roadmap</Link>
              <Link to="/builder" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2 rounded-xl text-sm font-semibold text-slate-300 hover:bg-slate-800">Resume Builder</Link>
              <button onClick={handleLogout} className="w-full text-left px-3 py-2 rounded-xl text-sm font-semibold text-rose-400 hover:bg-rose-500/10">Sign Out</button>
            </>
          ) : (
            <div className="space-y-2 pt-2">
              <Link to="/login" onClick={() => setMobileMenuOpen(false)} className="block w-full py-2.5 text-center rounded-xl text-sm font-semibold text-slate-300 bg-slate-800">Sign In</Link>
              <Link to="/signup" onClick={() => setMobileMenuOpen(false)} className="block w-full py-2.5 text-center rounded-xl text-sm font-bold text-white gradient-bg">Get Started Free</Link>
            </div>
          )}
        </div>
      )}
    </nav>
  );
};

export default Navbar;
