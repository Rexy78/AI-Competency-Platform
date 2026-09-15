import React, { useEffect, useState } from 'react';
import SidebarLayout from '../components/SidebarLayout';
import api from '../services/api';
import { Briefcase, Sparkles, CheckCircle2, AlertTriangle, ArrowRight } from 'lucide-react';

const JobRecommendationsPage = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/jobs/recommendations')
      .then(res => {
        setJobs(res.data || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <SidebarLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="glass-card rounded-3xl p-8 border border-slate-800/80 shadow-2xl space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-semibold uppercase tracking-wider">
            <Briefcase className="w-3.5 h-3.5" />
            <span>Target Role Intelligence</span>
          </div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">Recommended Technical Job Roles</h1>
          <p className="text-xs text-slate-400">
            Matching percentage calculated by comparing your resume skill taxonomy against high-demand software engineering benchmarks.
          </p>
        </div>

        {/* Job Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {jobs.map((job, idx) => (
            <div key={idx} className="glass-card p-6 rounded-3xl border border-slate-800/80 shadow-2xl space-y-4 glass-card-hover">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-base font-extrabold text-white">{job.role}</h3>
                  <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">{job.category || 'Software Engineering'}</span>
                </div>

                <div className="px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 text-xs font-extrabold">
                  {Math.round(job.match_percentage)}% Match
                </div>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed font-medium">{job.description}</p>

              {/* Matching Skills */}
              <div className="space-y-1.5 pt-2 border-t border-slate-800">
                <span className="text-[11px] font-bold text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Matching Skills
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {(job.matching_skills || []).map((sk, i) => (
                    <span key={i} className="px-2.5 py-1 rounded-lg bg-emerald-950/60 text-emerald-300 text-xs font-semibold border border-emerald-800/40">
                      {sk}
                    </span>
                  ))}
                </div>
              </div>

              {/* Missing Skills */}
              {(job.missing_skills || []).length > 0 && (
                <div className="space-y-1.5 pt-2">
                  <span className="text-[11px] font-bold text-rose-400 flex items-center gap-1">
                    <AlertTriangle className="w-3.5 h-3.5" /> Missing Requirements
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {job.missing_skills.map((sk, i) => (
                      <span key={i} className="px-2.5 py-1 rounded-lg bg-rose-950/60 text-rose-300 text-xs font-semibold border border-rose-800/40">
                        {sk}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </SidebarLayout>
  );
};

export default JobRecommendationsPage;
