import React, { useEffect, useState } from 'react';
import { BarChart3, TrendingUp, Zap } from 'lucide-react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import Footer from '../components/Footer';
import api from '../services/api';

const InterviewPerformancePage = () => {
  const [history, setHistory] = useState([]);
  const [latest, setLatest] = useState(null);

  useEffect(() => {
    const fetchLatest = async () => {
      try {
        const res = await api.get('/interview/history');
        const items = Array.isArray(res.data) ? res.data : [];
        setHistory(items);
        setLatest(items[0] || null);
      } catch (error) {
        console.error(error);
      }
    };
    fetchLatest();
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <Navbar />
      <div className="flex max-w-7xl mx-auto">
        <Sidebar />
        <main className="flex-1 p-6 md:p-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[
              { label: 'Total Practice Tests', value: history.length, icon: BarChart3 },
              { label: 'Average Score', value: `${Math.round(history.reduce((sum, item) => sum + (Number(item.score) || 0), 0) / Math.max(1, history.length))}%`, icon: TrendingUp },
              { label: 'Best Score', value: `${Math.max(...history.map((item) => Number(item.score) || 0), 0)}%`, icon: Zap },
              { label: 'Current Readiness', value: `${latest?.score || 0}%`, icon: TrendingUp },
            ].map(({ label, value, icon: Icon }) => (
              <div key={label} className="glass-card rounded-2xl p-5 border border-slate-800/80">
                <div className="flex items-center justify-between text-xs uppercase tracking-[0.2em] text-slate-400"><span>{label}</span><Icon className="w-4 h-4 text-indigo-400" /></div>
                <div className="mt-4 text-2xl font-extrabold text-white">{value}</div>
              </div>
            ))}
          </div>

          <div className="mt-6 glass-card rounded-3xl p-6 border border-slate-800/80">
            <h3 className="text-sm font-bold uppercase tracking-[0.18em] text-slate-300">Performance Over Time</h3>
            <div className="mt-6 space-y-3">
              {history.length ? history.slice(0, 5).map((item, idx) => (
                <div key={item.id}>
                  <div className="flex justify-between text-xs text-slate-300 mb-2"><span>Attempt {idx + 1}</span><span>{item.score || 0}%</span></div>
                  <div className="h-2 rounded-full bg-slate-800 overflow-hidden"><div className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-indigo-500" style={{ width: `${Math.min(100, Number(item.score) || 0)}%` }} /></div>
                </div>
              )) : <p className="text-sm text-slate-400">No performance data available yet.</p>}
            </div>
          </div>
        </main>
      </div>
      <Footer />
    </div>
  );
};

export default InterviewPerformancePage;
