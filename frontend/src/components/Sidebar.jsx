import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  LayoutDashboard, FileText, BarChart3, Target, Briefcase, 
  SearchCode, Wand2, FileCode, Map, ClipboardCheck, User, LogOut, Sparkles, Gauge
} from 'lucide-react';

const Sidebar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Resume Analyzer', path: '/upload', icon: FileText },
    { name: 'ATS Analysis', path: '/analysis', icon: BarChart3 },
    { name: 'Skill Gap', path: '/skill-gap', icon: Target },
    { name: 'Job Roles', path: '/job-recommendations', icon: Briefcase },
    { name: 'Career Roadmap', path: '/roadmap', icon: Map },
    { name: 'Job Description', path: '/jd-analyzer', icon: SearchCode },
    { name: 'Resume Builder', path: '/builder', icon: FileCode },
    { name: 'AI Resume Improver', path: '/improver', icon: Wand2 },
    { name: 'AI Chatbot', path: '/chatbot', icon: Sparkles },
    { name: 'Practice Test', path: '/interview', icon: ClipboardCheck },
    { name: 'Practice Test Performance', path: '/interview/performance', icon: Gauge },
    { name: 'Profile & Settings', path: '/profile', icon: User },
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <aside className="w-64 bg-slate-900/90 border-r border-slate-800/80 flex flex-col justify-between hidden md:flex min-h-screen sticky top-0 backdrop-blur-xl z-40 selection:bg-indigo-500 selection:text-white">
      <div>
        {/* Brand Header */}
        <div className="p-5 border-b border-slate-800/80 flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl gradient-bg flex items-center justify-center text-white shadow-glow">
            <Sparkles className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-extrabold text-base tracking-tight text-white">Resume<span className="gradient-text">Analyzer</span></span>
            </div>
            <p className="text-[10px] text-slate-400">Career Intelligence Platform</p>
          </div>
        </div>

        {/* Navigation Items */}
        <div className="p-3 space-y-1 overflow-y-auto max-h-[calc(100vh-140px)] custom-scrollbar">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                  isActive
                    ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/40 shadow-glow font-bold'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-400' : 'text-slate-500'}`} />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <span className={`px-1.5 py-0.5 rounded text-[9px] font-extrabold uppercase ${
                    item.badge === 'NEW' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                    item.badge === 'PRO' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                    'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30'
                  }`}>
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </div>
      </div>

      {/* Footer Profile Box */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/40">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="w-8 h-8 rounded-xl bg-indigo-600 text-white flex items-center justify-center font-bold text-xs flex-shrink-0">
              {user?.full_name?.charAt(0) || 'U'}
            </div>
            <div className="truncate">
              <p className="text-xs font-bold text-white truncate">{user?.full_name || 'Candidate User'}</p>
              <p className="text-[10px] text-slate-400 truncate">{user?.email || 'user@resumeai.com'}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            title="Sign Out"
            className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
