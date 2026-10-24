import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { BarChart3, BookOpen, BrainCircuit, Loader2, TrendingUp, Trophy } from 'lucide-react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import Footer from '../components/Footer';
import api from '../services/api';

const InterviewResultPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const res = await api.get(`/interview/${id}/report`);
        setReport(res.data);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };
    fetchReport();
  }, [id]);

  const handleWeaknessPractice = async () => {
    try {
      const res = await api.post('/interview/weakness-practice');
      navigate(`/interview/session/${res.data.session_id}`);
    } catch (error) {
      console.error(error);
    }
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center bg-slate-950 text-white"><Loader2 className="w-8 h-8 animate-spin" /></div>;
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <Navbar />
      <div className="flex max-w-7xl mx-auto">
        <Sidebar />
        <main className="flex-1 p-6 md:p-8">
          <div className="glass-card rounded-3xl p-6 border border-slate-800 bg-gradient-to-r from-slate-900 via-emerald-950/30 to-slate-900">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-2xl gradient-bg flex items-center justify-center text-white"><Trophy className="w-6 h-6" /></div>
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-emerald-400 font-bold">Practice Test Performance</p>
                <h1 className="text-2xl md:text-3xl font-extrabold text-white">Final Candidate Review</h1>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 mt-6">
            {[
              { label: 'Overall Score', value: `${report?.overall_score || 0} / 100`, icon: Trophy },
              { label: 'Role Readiness', value: `${report?.role_readiness || 0}%`, icon: TrendingUp },
              { label: 'Technical', value: `${report?.technical_score || 0}%`, icon: BrainCircuit },
              { label: 'Communication', value: `${report?.communication_score || 0}%`, icon: BarChart3 },
            ].map(({ label, value, icon: Icon }) => (
              <div key={label} className="glass-card rounded-2xl p-4 border border-slate-800/80">
                <div className="flex items-center justify-between">
                  <span className="text-xs uppercase text-slate-400 tracking-[0.2em]">{label}</span>
                  <Icon className="w-4 h-4 text-indigo-400" />
                </div>
                <div className="mt-3 text-2xl font-extrabold text-white">{value}</div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mt-6">
            <div className="glass-card rounded-3xl p-6 border border-slate-800/80">
              <h3 className="text-sm font-bold uppercase tracking-[0.18em] text-slate-300">Topic Performance</h3>
              <div className="mt-4 space-y-3">
                {(report?.topic_scores && Object.entries(report.topic_scores).length > 0) ? Object.entries(report.topic_scores).map(([topic, value]) => (
                  <div key={topic}>
                    <div className="flex justify-between text-xs text-slate-300 mb-2"><span>{topic}</span><span>{value}%</span></div>
                    <div className="h-2 rounded-full bg-slate-800 overflow-hidden"><div className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-emerald-400" style={{ width: `${Math.min(100, value)}%` }} /></div>
                  </div>
                )) : <p className="text-sm text-slate-400">No topic data available yet.</p>}
              </div>
            </div>

            <div className="glass-card rounded-3xl p-6 border border-slate-800/80">
              <h3 className="text-sm font-bold uppercase tracking-[0.18em] text-slate-300">Strong Areas</h3>
              <div className="mt-4 space-y-3 text-sm text-slate-200">
                {(report?.strengths || []).length ? report.strengths.map((item) => <div key={item} className="px-3 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-200">✓ {item}</div>) : <p className="text-slate-400">No strong topic data available.</p>}
              </div>

              <h3 className="text-sm font-bold uppercase tracking-[0.18em] text-slate-300 mt-6">Needs Improvement</h3>
              <div className="mt-4 space-y-3 text-sm text-slate-200">
                {(report?.weaknesses || []).length ? report.weaknesses.map((item) => <div key={item} className="px-3 py-2 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-200">⚠ {item}</div>) : <p className="text-slate-400">No weak topics identified yet.</p>}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mt-6">
            <div className="glass-card rounded-3xl p-6 border border-slate-800/80">
              <h3 className="text-sm font-bold uppercase tracking-[0.18em] text-slate-300">AI Recommendation</h3>
              <div className="mt-4 text-sm text-slate-200 leading-relaxed">
                {(report?.recommendations || []).length ? report.recommendations.map((item) => <p key={item} className="mb-2">• {item}</p>) : <p>No recommendation available yet.</p>}
              </div>
            </div>

            <div className="glass-card rounded-3xl p-6 border border-slate-800/80">
              <h3 className="text-sm font-bold uppercase tracking-[0.18em] text-slate-300">Learning Plan</h3>
              <div className="mt-4 space-y-3 text-sm text-slate-200">
                {(report?.learning_plan || []).length ? report.learning_plan.map((item) => (
                  <div key={item.day} className="p-3 rounded-xl bg-slate-900 border border-slate-700">
                    <div className="font-bold text-white">Day {item.day}: {item.topic}</div>
                    <div className="text-xs text-slate-400 mt-1">{item.focus}</div>
                  </div>
                )) : <p className="text-slate-400">No learning plan generated yet.</p>}
              </div>
            </div>
          </div>

          <div className="mt-6 flex flex-wrap gap-3">
            <button onClick={() => navigate('/interview/history')} className="px-4 py-2 rounded-xl bg-slate-800 text-white text-xs font-bold">View Detailed Analysis</button>
            <button onClick={handleWeaknessPractice} className="px-4 py-2 rounded-xl gradient-bg text-white text-xs font-bold">Start Weakness Practice</button>
            <button onClick={() => navigate('/interview/performance')} className="px-4 py-2 rounded-xl bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 text-xs font-bold">Generate Learning Plan</button>
          </div>
        </main>
      </div>
      <Footer />
    </div>
  );
};

export default InterviewResultPage;
