import React, { useEffect, useState } from 'react';
import SidebarLayout from '../components/SidebarLayout';
import api from '../services/api';
import { 
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer 
} from 'recharts';
import { Target, Sparkles, AlertCircle, CheckCircle2, Award } from 'lucide-react';

const SkillGapRadarPage = () => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/resume/latest')
      .then(res => {
        setAnalysis(res.data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const radarData = analysis?.radar_data || [
    { subject: 'Languages', CandidateScore: 85, RequiredScore: 90 },
    { subject: 'Frontend', CandidateScore: 70, RequiredScore: 80 },
    { subject: 'Backend', CandidateScore: 90, RequiredScore: 95 },
    { subject: 'Database', CandidateScore: 80, RequiredScore: 85 },
    { subject: 'Cloud/DevOps', CandidateScore: 50, RequiredScore: 85 },
    { subject: 'Data/AI', CandidateScore: 40, RequiredScore: 70 },
  ];

  return (
    <SidebarLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="glass-card rounded-3xl p-8 border border-slate-800/80 shadow-2xl space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-400 text-xs font-semibold uppercase tracking-wider">
            <Target className="w-3.5 h-3.5" />
            <span>Canonical Skill Taxonomy Intelligence</span>
          </div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">Skill Gap Radar Analysis</h1>
          <p className="text-xs text-slate-400">
            Compare your extracted skill proficiency against benchmark target role requirements (<span className="text-purple-400 font-bold">{analysis?.target_role || 'Java Backend Developer'}</span>).
          </p>
        </div>

        {/* Radar Chart & Key Missing Gaps */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recharts Radar Graphic */}
          <div className="glass-card rounded-3xl p-6 border border-slate-800/80 shadow-2xl space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider border-b border-slate-800 pb-3">
              Radar Proficiency Comparison
            </h3>

            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                  <PolarGrid stroke="#334155" />
                  <PolarAngleAxis dataKey="subject" tick={{ fill: '#cbd5e1', fontSize: 11, fontWeight: 700 }} />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 10 }} />
                  <Radar name="Your Resume Skills" dataKey="CandidateScore" stroke="#818cf8" fill="#6366f1" fillOpacity={0.4} />
                  <Radar name="Target Benchmark" dataKey="RequiredScore" stroke="#10b981" fill="#10b981" fillOpacity={0.2} />
                </RadarChart>
              </ResponsiveContainer>
            </div>

            <div className="flex justify-center gap-6 text-xs font-semibold pt-2">
              <span className="flex items-center gap-2 text-indigo-400">
                <span className="w-3 h-3 rounded-full bg-indigo-500"></span> Your Resume Proficiency
              </span>
              <span className="flex items-center gap-2 text-emerald-400">
                <span className="w-3 h-3 rounded-full bg-emerald-500"></span> Benchmark Requirements
              </span>
            </div>
          </div>

          {/* Missing Priority Skills Matrix */}
          <div className="glass-card rounded-3xl p-6 border border-slate-800/80 shadow-2xl space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider border-b border-slate-800 pb-3">
              Detected High-Priority Skill Gaps
            </h3>

            <div className="space-y-3">
              {[
                { skill: 'Docker / Containerization', category: 'Cloud/DevOps', priority: 'High', status: 'Missing' },
                { skill: 'CI/CD Pipelines (GitHub Actions)', category: 'Cloud/DevOps', priority: 'High', status: 'Missing' },
                { skill: 'System Architecture & Microservices', category: 'Backend', priority: 'Medium', status: 'Missing' },
                { skill: 'Redis Caching', category: 'Database', priority: 'Medium', status: 'Missing' },
              ].map((gap, i) => (
                <div key={i} className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 flex items-center justify-between">
                  <div className="space-y-1">
                    <p className="text-xs font-extrabold text-white">{gap.skill}</p>
                    <span className="text-[10px] text-slate-400 font-semibold">{gap.category}</span>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="px-2.5 py-0.5 rounded-full bg-rose-500/20 text-rose-400 text-[10px] font-extrabold border border-rose-500/30">
                      {gap.priority} Priority
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </SidebarLayout>
  );
};

export default SkillGapRadarPage;
