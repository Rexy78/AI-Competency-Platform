import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import SidebarLayout from '../components/SidebarLayout';
import api from '../services/api';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell 
} from 'recharts';
import { 
  Sparkles, Award, Target, CheckCircle2, Briefcase, FileText, 
  SearchCode, FileCode, ArrowRight, Trash2, Clock, Wand2 
} from 'lucide-react';

const DashboardPage = () => {
  const [data, setData] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
    fetchHistory();
  }, []);

  const fetchDashboardData = () => {
    api.get('/dashboard')
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  const fetchHistory = () => {
    api.get('/resume/history')
      .then(res => {
        setHistory(res.data || []);
      })
      .catch(err => console.error(err));
  };

  const handleDeleteHistory = (id, e) => {
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this analysis record?")) return;

    api.delete(`/resume/analysis/${id}`)
      .then(() => {
        fetchHistory();
        fetchDashboardData();
      })
      .catch(err => console.error(err));
  };

  const COLORS = ['#6366f1', '#818cf8', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6'];

  return (
    <SidebarLayout>
      <div className="space-y-6">
        {/* Welcome Header */}
        <div className="glass-card rounded-3xl p-8 border border-slate-800/80 shadow-2xl flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-2">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Career Dashboard</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Welcome back, <span className="gradient-text">{data?.user_name || 'Candidate'}</span> 👋
            </h1>
            <p className="text-xs text-slate-400 mt-1">Here is your resume ATS evaluation score and career skill matrix overview.</p>
          </div>

          <div className="flex gap-3">
            <Link
              to="/upload"
              className="px-6 py-3 rounded-2xl font-bold text-xs text-white gradient-bg shadow-glow hover:opacity-95 transition-all flex items-center gap-2"
            >
              <FileText className="w-4 h-4" />
              <span>Analyze New Resume</span>
            </Link>
          </div>
        </div>

        {/* 4 Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="glass-card p-6 rounded-3xl border border-slate-800/80 shadow-2xl space-y-2 glass-card-hover">
            <div className="flex justify-between items-center text-slate-400">
              <span className="text-xs font-extrabold uppercase tracking-wider">ATS Score</span>
              <div className="w-8 h-8 rounded-xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold">
                <Award className="w-4 h-4" />
              </div>
            </div>
            <p className="text-3xl font-extrabold text-white">{data?.ats_score || 82}<span className="text-sm text-slate-500 font-bold">/100</span></p>
            <p className="text-[11px] text-emerald-400 font-semibold flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" /> High keyword match
            </p>
          </div>

          <div className="glass-card p-6 rounded-3xl border border-slate-800/80 shadow-2xl space-y-2 glass-card-hover">
            <div className="flex justify-between items-center text-slate-400">
              <span className="text-xs font-extrabold uppercase tracking-wider">Skill Match</span>
              <div className="w-8 h-8 rounded-xl bg-purple-500/20 text-purple-400 flex items-center justify-center font-bold">
                <Target className="w-4 h-4" />
              </div>
            </div>
            <p className="text-3xl font-extrabold text-white">{data?.skill_match_pct || 68}%</p>
            <p className="text-[11px] text-indigo-400 font-semibold">Target: {data?.target_role || 'Java Backend'}</p>
          </div>

          <div className="glass-card p-6 rounded-3xl border border-slate-800/80 shadow-2xl space-y-2 glass-card-hover">
            <div className="flex justify-between items-center text-slate-400">
              <span className="text-xs font-extrabold uppercase tracking-wider">Completeness</span>
              <div className="w-8 h-8 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold">
                <CheckCircle2 className="w-4 h-4" />
              </div>
            </div>
            <p className="text-3xl font-extrabold text-white">{data?.resume_completeness || 92}%</p>
            <p className="text-[11px] text-slate-400 font-medium">All major sections present</p>
          </div>

          <div className="glass-card p-6 rounded-3xl border border-slate-800/80 shadow-2xl space-y-2 glass-card-hover">
            <div className="flex justify-between items-center text-slate-400">
              <span className="text-xs font-extrabold uppercase tracking-wider">Job Fit</span>
              <div className="w-8 h-8 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center font-bold">
                <Briefcase className="w-4 h-4" />
              </div>
            </div>
            <p className="text-3xl font-extrabold text-white">{data?.job_match_pct || 87}%</p>
            <p className="text-[11px] text-slate-400 font-medium">Matching 4 recommended roles</p>
          </div>
        </div>

        {/* Quick Actions Grid */}
        <div className="glass-card rounded-3xl p-8 border border-slate-800/80 shadow-2xl space-y-4">
          <h3 className="text-base font-bold text-white">Quick Platform Actions</h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
            <Link to="/upload" className="p-4 rounded-2xl bg-indigo-950/40 border border-indigo-800/40 hover:bg-indigo-900/50 transition-all text-center space-y-2 group">
              <div className="w-10 h-10 rounded-xl gradient-bg text-white flex items-center justify-center mx-auto group-hover:scale-105 transition-transform shadow-glow">
                <FileText className="w-5 h-5" />
              </div>
              <span className="block text-xs font-bold text-white">Analyze Resume</span>
            </Link>

            <Link to="/skill-gap" className="p-4 rounded-2xl bg-purple-950/40 border border-purple-800/40 hover:bg-purple-900/50 transition-all text-center space-y-2 group">
              <div className="w-10 h-10 rounded-xl bg-purple-600 text-white flex items-center justify-center mx-auto group-hover:scale-105 transition-transform">
                <Target className="w-5 h-5" />
              </div>
              <span className="block text-xs font-bold text-white">Check Skill Gap</span>
            </Link>

            <Link to="/jobs" className="p-4 rounded-2xl bg-cyan-950/40 border border-cyan-800/40 hover:bg-cyan-900/50 transition-all text-center space-y-2 group">
              <div className="w-10 h-10 rounded-xl bg-cyan-600 text-white flex items-center justify-center mx-auto group-hover:scale-105 transition-transform">
                <Briefcase className="w-5 h-5" />
              </div>
              <span className="block text-xs font-bold text-white">Find Job Roles</span>
            </Link>

            <Link to="/builder" className="p-4 rounded-2xl bg-emerald-950/40 border border-emerald-800/40 hover:bg-emerald-900/50 transition-all text-center space-y-2 group">
              <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center mx-auto group-hover:scale-105 transition-transform">
                <FileCode className="w-5 h-5" />
              </div>
              <span className="block text-xs font-bold text-white">Build Resume</span>
            </Link>

            <Link to="/jd-analyzer" className="p-4 rounded-2xl bg-amber-950/40 border border-amber-800/40 hover:bg-amber-900/50 transition-all text-center space-y-2 group">
              <div className="w-10 h-10 rounded-xl bg-amber-600 text-white flex items-center justify-center mx-auto group-hover:scale-105 transition-transform">
                <SearchCode className="w-5 h-5" />
              </div>
              <span className="block text-xs font-bold text-white">Match Job Description</span>
            </Link>
          </div>
        </div>

        {/* Recharts Analytics Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Skill Distribution Chart */}
          <div className="glass-card rounded-3xl p-6 border border-slate-800/80 shadow-2xl space-y-3">
            <h3 className="text-sm font-bold text-white">Extracted Skill Distribution by Category</h3>
            <div className="h-60 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data?.skill_distribution || []}>
                  <XAxis dataKey="category" tick={{ fill: '#94a3b8', fontSize: 11, fontWeight: 600 }} />
                  <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', color: '#fff' }} />
                  <Bar dataKey="count" radius={[8, 8, 0, 0]}>
                    {(data?.skill_distribution || []).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* ATS Score Evaluation Breakdown */}
          <div className="glass-card rounded-3xl p-6 border border-slate-800/80 shadow-2xl space-y-3">
            <h3 className="text-sm font-bold text-white">ATS Evaluation Breakdown (%)</h3>
            <div className="h-60 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data?.score_breakdown || []} layout="vertical">
                  <XAxis type="number" domain={[0, 100]} tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <YAxis dataKey="category" type="category" width={130} tick={{ fill: '#cbd5e1', fontSize: 11, fontWeight: 600 }} />
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', color: '#fff' }} />
                  <Bar dataKey="score" fill="#818cf8" radius={[0, 8, 8, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Recent Resume Analyses History Table */}
        <div className="glass-card rounded-3xl p-8 border border-slate-800/80 shadow-2xl space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white">Saved Resume Analysis History</h3>
            <span className="text-xs text-slate-400 font-semibold">{history.length} Saved Reports</span>
          </div>

          {history && history.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-slate-800 text-xs font-bold text-slate-400 uppercase tracking-wider">
                    <th className="py-3 px-4">Date</th>
                    <th className="py-3 px-4">Filename</th>
                    <th className="py-3 px-4">Target Role</th>
                    <th className="py-3 px-4">ATS Score</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-xs font-semibold">
                  {history.map((item, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-3.5 px-4 text-slate-400 flex items-center gap-1.5">
                        <Clock className="w-3.5 h-3.5 text-slate-500" />
                        <span>{new Date(item.created_at).toLocaleDateString()}</span>
                      </td>
                      <td className="py-3.5 px-4 font-bold text-white">{item.filename}</td>
                      <td className="py-3.5 px-4 text-slate-300">{item.target_role}</td>
                      <td className="py-3.5 px-4">
                        <span className="px-2.5 py-1 rounded-full bg-indigo-500/20 text-indigo-400 font-extrabold border border-indigo-500/30">
                          {Math.round(item.ats_score)}/100
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-right space-x-3">
                        <Link to="/analysis" className="text-indigo-400 font-bold hover:underline inline-flex items-center gap-1">
                          <span>View Report</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </Link>
                        <button
                          onClick={(e) => handleDeleteHistory(item.analysis_id, e)}
                          className="text-slate-500 hover:text-rose-400 transition-colors p-1"
                          title="Delete Analysis"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8 bg-slate-900/60 rounded-2xl border border-slate-800">
              <p className="text-xs text-slate-400 font-medium">No previous resume uploads found. Upload your first resume to get started!</p>
              <Link to="/upload" className="mt-3 inline-block px-5 py-2.5 rounded-xl text-xs font-bold text-white gradient-bg shadow-glow">
                Upload Resume Now
              </Link>
            </div>
          )}
        </div>
      </div>
    </SidebarLayout>
  );
};

export default DashboardPage;
