import React from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { 
  Sparkles, CheckCircle2, ArrowRight, FileText, Target, Map, 
  Briefcase, SearchCode, Wand2, ShieldCheck, Award, Zap, Layers 
} from 'lucide-react';

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between selection:bg-indigo-500 selection:text-white">
      <Navbar />

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-16 pb-24 border-b border-slate-800/80">
        <div className="absolute inset-0 bg-mesh opacity-80 pointer-events-none"></div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center space-y-8">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-bold uppercase tracking-wider shadow-glow">
            <Sparkles className="w-4 h-4 animate-pulse text-indigo-400" />
            <span>Next-Gen AI Resume & Skill Intelligence</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold text-white tracking-tight max-w-4xl mx-auto leading-tight">
            Optimize Your Resume for ATS & Accelerate Your <span className="gradient-text">Tech Career</span>
          </h1>

          <p className="text-sm sm:text-base text-slate-300 max-w-2xl mx-auto font-medium leading-relaxed">
            Upload your resume to calculate instant ATS match scores, discover canonical skill gap radar charts, build personalized learning roadmaps, and generate targeted resume improvements.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <Link
              to="/signup"
              className="w-full sm:w-auto px-8 py-4 rounded-2xl font-extrabold text-sm text-white gradient-bg shadow-glow hover:opacity-95 hover:scale-[1.02] transition-all flex items-center justify-center gap-3"
            >
              <span>Analyze Your Resume Free</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              to="/login"
              className="w-full sm:w-auto px-8 py-4 rounded-2xl font-extrabold text-sm text-slate-300 bg-slate-900 border border-slate-800 hover:border-slate-700 hover:text-white transition-all flex items-center justify-center gap-2"
            >
              <span>Explore Demo Account</span>
            </Link>
          </div>

          {/* Quick Metrics Banner */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto pt-12">
            {[
              { label: 'Canonical Skills', value: '7+ Categories' },
              { label: 'ATS Parsing Engine', value: 'PyMuPDF + spaCy' },
              { label: 'Resume Templates', value: '4 Clean Layouts' },
              { label: 'Skill Gap Radar', value: 'Automated Match' },
            ].map((m, i) => (
              <div key={i} className="glass-card p-4 rounded-2xl border border-slate-800/80 text-center">
                <span className="text-lg font-extrabold text-white block">{m.value}</span>
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">{m.label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Feature Showcase Grid */}
      <section className="py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        <div className="text-center space-y-3">
          <h2 className="text-3xl font-extrabold text-white tracking-tight">Everything You Need for Career Success</h2>
          <p className="text-xs text-slate-400 max-w-lg mx-auto">Complete full-stack AI career platform designed to help software engineers pass ATS filters.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            {
              icon: FileText,
              title: 'ATS Resume Scoring',
              desc: 'Instant 0-100 ATS match scoring evaluating keyword density, formatting, section completeness, and skill taxonomy.',
              color: 'text-indigo-400 bg-indigo-500/20'
            },
            {
              icon: Target,
              title: 'Skill Gap Radar Charts',
              desc: 'Interactive canonical skill radar comparisons highlighting missing high-priority tech stacks for targeted roles.',
              color: 'text-purple-400 bg-purple-500/20'
            },
            {
              icon: Map,
              title: 'Personalized Career Roadmaps',
              desc: 'Step-by-step learning progression paths with time estimates, prerequisites, and resource links.',
              color: 'text-emerald-400 bg-emerald-500/20'
            },
            {
              icon: Briefcase,
              title: 'Targeted Job Role Matcher',
              desc: 'Matches your current resume skills against top technical roles like Full Stack, Backend, Data Engineer, & DevOps.',
              color: 'text-cyan-400 bg-cyan-500/20'
            },
            {
              icon: SearchCode,
              title: 'Job Description Matcher',
              desc: 'Paste any target job description to compute exact missing skill keywords and tailor your application.',
              color: 'text-amber-400 bg-amber-500/20'
            },
            {
              icon: Wand2,
              title: 'ATS Resume Builder',
              desc: 'Build clean, high-scoring resumes with 4 professional ATS templates and 1-click PDF export.',
              color: 'text-rose-400 bg-rose-500/20'
            },
          ].map((f, idx) => {
            const Icon = f.icon;
            return (
              <div key={idx} className="glass-card p-8 rounded-3xl border border-slate-800/80 shadow-2xl glass-card-hover space-y-4">
                <div className={`w-12 h-12 rounded-2xl ${f.color} flex items-center justify-center font-bold`}>
                  <Icon className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-bold text-white">{f.title}</h3>
                <p className="text-xs text-slate-400 leading-relaxed font-medium">{f.desc}</p>
              </div>
            );
          })}
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default LandingPage;
