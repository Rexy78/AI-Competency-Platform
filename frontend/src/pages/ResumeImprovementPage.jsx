import React, { useEffect, useState } from 'react';
import SidebarLayout from '../components/SidebarLayout';
import api from '../services/api';
import { Wand2, Sparkles, CheckCircle2, Copy, Check } from 'lucide-react';

const ResumeImprovementPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copiedIdx, setCopiedIdx] = useState(null);

  useEffect(() => {
    api.post('/resume/improve', { target_role: 'Software Engineer' })
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const handleCopy = (text, idx) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  return (
    <SidebarLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="glass-card rounded-3xl p-8 border border-slate-800/80 shadow-2xl space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-semibold uppercase tracking-wider">
            <Wand2 className="w-3.5 h-3.5" />
            <span>AI Action Bullet Point Generator</span>
          </div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">AI Resume Enhancements</h1>
          <p className="text-xs text-slate-400">
            Action-verb bullet point suggestions engineered to maximize ATS impact and quantify achievements.
          </p>
        </div>

        {/* Enhanced Bullet Suggestions */}
        <div className="glass-card rounded-3xl p-8 border border-slate-800/80 shadow-2xl space-y-4">
          <h3 className="text-base font-bold text-white">Recommended High-Impact Experience Bullets</h3>

          <div className="space-y-3">
            {[
              "Engineered scalable microservices architecture using Java 17 and Spring Boot, reducing database query latency by 35% across 200k+ daily transactions.",
              "Containerized core application suite using Docker & Kubernetes, standardizing deployment environments and decreasing deployment downtime to zero.",
              "Implemented Redis distributed caching layer to streamline high-frequency session lookups, improving API throughput by 45%.",
              "Architected automated CI/CD deployment pipelines using GitHub Actions, cutting release deployment cycles from 2 hours to 15 minutes."
            ].map((bullet, idx) => (
              <div key={idx} className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 flex items-center justify-between gap-4">
                <p className="text-xs text-slate-300 font-medium leading-relaxed">• {bullet}</p>

                <button
                  onClick={() => handleCopy(bullet, idx)}
                  className="px-3 py-1.5 rounded-xl bg-slate-800 text-indigo-400 hover:text-white hover:bg-slate-700 text-xs font-bold flex items-center gap-1.5 flex-shrink-0 transition-all"
                >
                  {copiedIdx === idx ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copiedIdx === idx ? 'Copied' : 'Copy'}</span>
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </SidebarLayout>
  );
};

export default ResumeImprovementPage;
