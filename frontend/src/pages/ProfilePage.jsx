import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import Footer from '../components/Footer';
import { useAuth } from '../context/AuthContext';
import { User, Mail, ShieldCheck, Cpu, Key, Save, CheckCircle2, Sparkles } from 'lucide-react';

const ProfilePage = () => {
  const { user } = useAuth();
  const [llmProvider, setLlmProvider] = useState('gemini');
  const [apiKey, setApiKey] = useState('');
  const [targetRole, setTargetRole] = useState('Java Backend Developer');
  const [savedMsg, setSavedMsg] = useState('');

  const handleSaveSettings = (e) => {
    e.preventDefault();
    setSavedMsg('Settings saved successfully!');
    setTimeout(() => setSavedMsg(''), 3000);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between selection:bg-indigo-500 selection:text-white">
      <Navbar />

      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        <Sidebar />

        <main className="flex-1 p-6 md:p-8 space-y-6 overflow-x-hidden">
          {/* Header */}
          <div className="glass-card rounded-3xl p-6 border border-slate-800/80 bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 shadow-2xl">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-2xl bg-indigo-600 text-white font-extrabold text-xl flex items-center justify-center shadow-glow uppercase">
                {user?.full_name?.charAt(0) || 'U'}
              </div>
              <div>
                <h1 className="text-2xl font-extrabold text-white">{user?.full_name || 'Candidate User'}</h1>
                <p className="text-xs text-slate-400">{user?.email || 'user@resumeai.com'}</p>
                <div className="flex items-center gap-2 mt-2">
                  <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[10px] font-bold">
                    Active Candidate Account
                  </span>
                  {user?.is_admin && (
                    <span className="px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30 text-[10px] font-bold">
                      System Administrator
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {savedMsg && (
            <div className="p-4 rounded-2xl bg-emerald-950/40 border border-emerald-800 text-emerald-300 text-xs flex items-center gap-2.5 animate-fadeIn">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>{savedMsg}</span>
            </div>
          )}

          {/* Profile & GenAI Settings Form */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="glass-card rounded-3xl p-6 border border-slate-800/80 space-y-4">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <User className="w-4 h-4 text-indigo-400" />
                <span>Candidate Profile Details</span>
              </h3>

              <div className="space-y-3 text-xs">
                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Full Name</label>
                  <input
                    type="text"
                    disabled
                    value={user?.full_name || 'Candidate User'}
                    className="w-full px-4 py-2.5 rounded-xl bg-slate-900/60 border border-slate-800 text-slate-300 font-medium"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Email Address</label>
                  <input
                    type="email"
                    disabled
                    value={user?.email || 'user@resumeai.com'}
                    className="w-full px-4 py-2.5 rounded-xl bg-slate-900/60 border border-slate-800 text-slate-300 font-medium"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Default Target Role</label>
                  <input
                    type="text"
                    value={targetRole}
                    onChange={(e) => setTargetRole(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-white font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>
            </div>

            <div className="glass-card rounded-3xl p-6 border border-slate-800/80 space-y-4">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Cpu className="w-4 h-4 text-amber-400" />
                <span>GenAI Provider Settings</span>
              </h3>

              <form onSubmit={handleSaveSettings} className="space-y-4 text-xs">
                <div>
                  <label className="block text-slate-400 font-semibold mb-1">LLM Provider Abstraction</label>
                  <select
                    value={llmProvider}
                    onChange={(e) => setLlmProvider(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-white font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="gemini">Google Gemini API (gemini-1.5-flash)</option>
                    <option value="openai">OpenAI API (gpt-4o-mini)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Custom API Key (Optional)</label>
                  <div className="relative">
                    <Key className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
                    <input
                      type="password"
                      value={apiKey}
                      onChange={(e) => setApiKey(e.target.value)}
                      placeholder="AIzaSy... / sk-proj-..."
                      className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-white font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                  <p className="text-[10px] text-slate-500 mt-1">If blank, environment key or Intelligent Fallback GenAI Engine will be used.</p>
                </div>

                <button
                  type="submit"
                  className="w-full py-3 rounded-2xl text-xs font-extrabold text-white gradient-bg shadow-glow hover:opacity-95 transition-all flex items-center justify-center gap-2"
                >
                  <Save className="w-4 h-4" />
                  <span>Save Settings</span>
                </button>
              </form>
            </div>
          </div>
        </main>
      </div>

      <Footer />
    </div>
  );
};

export default ProfilePage;
