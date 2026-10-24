import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import Navbar from './Navbar';
import Footer from './Footer';
import { 
  LayoutDashboard, FileText, Target, Map, Briefcase, 
  SearchCode, Wand2, FileCode, ShieldCheck, History, Sparkles, ClipboardCheck, Gauge
} from 'lucide-react';

const SidebarLayout = ({ children }) => {
  const location = useLocation();

  const navItems = [
    { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { label: 'Upload & Analyze', path: '/upload', icon: FileText },
    { label: 'Analysis Report', path: '/analysis', icon: History },
    { label: 'Skill Gap Radar', path: '/skill-gap', icon: Target },
    { label: 'Career Roadmap', path: '/roadmap', icon: Map },
    { label: 'Job Recommendations', path: '/jobs', icon: Briefcase },
    { label: 'JD Matcher', path: '/jd-analyzer', icon: SearchCode },
    { label: 'AI Bullet Enhancer', path: '/improve', icon: Wand2 },
    { label: 'ATS Resume Builder', path: '/builder', icon: FileCode },
    { label: 'AI Chatbot', path: '/chatbot', icon: Sparkles },
    { label: 'Practice Test', path: '/interview', icon: ClipboardCheck },
    { label: 'Practice Performance', path: '/interview/performance', icon: Gauge },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between">
      <Navbar />

      <div className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Left Navigation Sidebar */}
          <aside className="w-full lg:w-64 flex-shrink-0">
            <div className="glass-card rounded-3xl p-4 sticky top-24 space-y-1.5 border border-slate-800/80 shadow-2xl">
              <span className="block px-3 py-2 text-[10px] font-extrabold uppercase tracking-wider text-slate-400">
                Career Intelligence Platform
              </span>

              {navItems.map((item) => {
                const Icon = item.icon;
                const active = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-xs font-semibold transition-all ${
                      active
                        ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 shadow-glow'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                    }`}
                  >
                    <Icon className={`w-4 h-4 ${active ? 'text-indigo-400' : 'text-slate-400'}`} />
                    <span>{item.label}</span>
                  </Link>
                );
              })}

              <div className="pt-4 mt-4 border-t border-slate-800/80 px-3">
                <div className="p-3 rounded-2xl bg-indigo-950/40 border border-indigo-800/30 text-indigo-300 text-[11px] space-y-1">
                  <span className="font-bold block">💡 Pro Tip</span>
                  <p className="text-[10px] text-slate-400 leading-normal">
                    Re-analyze your resume after learning missing skills to increase your ATS score fit!
                  </p>
                </div>
              </div>
            </div>
          </aside>

          {/* Main Content View */}
          <main className="flex-1 min-w-0">
            {children}
          </main>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default SidebarLayout;
