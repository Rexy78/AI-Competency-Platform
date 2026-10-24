import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, Heart } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-slate-900 text-slate-400 py-12 border-t border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div className="md:col-span-1 space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg gradient-bg flex items-center justify-center text-white">
                <Sparkles className="w-4 h-4" />
              </div>
              <span className="font-extrabold text-lg tracking-tight text-white">Resume<span className="gradient-text">AI</span></span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Empowering engineers and tech candidates with AI resume optimization, ATS scoring, and personalized skill development roadmaps.
            </p>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-3">Resume Tools</h4>
            <ul className="space-y-2 text-xs">
              <li><Link to="/upload" className="hover:text-indigo-400 transition-colors">AI Resume Analyzer</Link></li>
              <li><Link to="/builder" className="hover:text-indigo-400 transition-colors">ATS Resume Builder</Link></li>
              <li><Link to="/improve" className="hover:text-indigo-400 transition-colors">AI Bullet Point Enhancer</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-3">Career Intelligence</h4>
            <ul className="space-y-2 text-xs">
              <li><Link to="/skill-gap" className="hover:text-indigo-400 transition-colors">Skill Gap Analyzer</Link></li>
              <li><Link to="/roadmap" className="hover:text-indigo-400 transition-colors">Career Learning Roadmap</Link></li>
              <li><Link to="/jobs" className="hover:text-indigo-400 transition-colors">Job Role Matcher</Link></li>
              <li><Link to="/jd-analyzer" className="hover:text-indigo-400 transition-colors">Job Description Matcher</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-3">Platform</h4>
            <ul className="space-y-2 text-xs">
              <li><Link to="/dashboard" className="hover:text-indigo-400 transition-colors">User Dashboard</Link></li>
              <li><Link to="/login" className="hover:text-indigo-400 transition-colors">Account Sign In</Link></li>
              <li><Link to="/signup" className="hover:text-indigo-400 transition-colors">Create Account</Link></li>
            </ul>
          </div>
        </div>

        <div className="pt-8 border-t border-slate-800 text-xs flex flex-col sm:flex-row items-center justify-between gap-4">
          <p>© {new Date().getFullYear()} ResumeAnalyzer. All rights reserved.</p>
          <p className="flex items-center gap-1 text-slate-500">
            Built with <Heart className="w-3.5 h-3.5 text-rose-500 fill-rose-500" /> for Final-Year CSE & Career Success.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
