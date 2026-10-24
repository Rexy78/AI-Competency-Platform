import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { BarChart3, CalendarRange, Clock3, Mic } from 'lucide-react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import Footer from '../components/Footer';
import api from '../services/api';

const InterviewHistoryPage = () => {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await api.get('/interview/history');
        setHistory(Array.isArray(res.data) ? res.data : []);
      } catch (error) {
        console.error(error);
      }
    };
    fetchHistory();
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <Navbar />
      <div className="flex max-w-7xl mx-auto">
        <Sidebar />
        <main className="flex-1 p-6 md:p-8">
          <div className="glass-card rounded-3xl p-6 border border-slate-800 bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-2xl gradient-bg flex items-center justify-center text-white"><Mic className="w-6 h-6" /></div>
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-indigo-400 font-bold">Practice Test History</p>
                <h1 className="text-2xl md:text-3xl font-extrabold text-white">Performance Timeline</h1>
              </div>
            </div>
          </div>

          <div className="mt-6 glass-card rounded-3xl p-6 border border-slate-800/80">
            <div className="space-y-4">
              {history.length ? history.map((item) => (
                <div key={item.id} className="flex flex-col md:flex-row md:items-center md:justify-between p-4 rounded-2xl border border-slate-800 bg-slate-900/80 gap-4">
                  <div>
                    <div className="text-sm font-bold text-white">{item.target_role}</div>
                    <div className="text-xs text-slate-400 mt-1">{item.interview_type} • {item.difficulty}</div>
                  </div>
                  <div className="flex flex-wrap gap-3 text-xs text-slate-300">
                    <span className="flex items-center gap-1"><CalendarRange className="w-3.5 h-3.5" /> {new Date(item.started_at).toLocaleDateString()}</span>
                    <span className="flex items-center gap-1"><Clock3 className="w-3.5 h-3.5" /> {item.status}</span>
                    <span className="flex items-center gap-1"><BarChart3 className="w-3.5 h-3.5" /> {item.score || 0}%</span>
                  </div>
                  <Link to={`/interview/result/${item.id}`} className="px-3 py-2 rounded-xl bg-indigo-500/15 text-indigo-300 text-xs font-bold border border-indigo-500/30">View Details</Link>
                </div>
              )) : <p className="text-slate-400 text-sm">No interview sessions yet. Start your first adaptive interview.</p>}
            </div>
          </div>
        </main>
      </div>
      <Footer />
    </div>
  );
};

export default InterviewHistoryPage;
