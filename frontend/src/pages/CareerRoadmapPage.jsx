import React, { useState } from 'react';
import SidebarLayout from '../components/SidebarLayout';
import { Map, Sparkles, CheckCircle2, Clock, BookOpen, ChevronRight } from 'lucide-react';

const CareerRoadmapPage = () => {
  const [steps, setSteps] = useState([
    {
      id: 1,
      title: 'Master Docker & Containerization',
      category: 'Cloud & DevOps',
      time: '2 Weeks',
      priority: 'High',
      status: 'Completed',
      description: 'Learn Dockerfiles, multi-stage builds, container networking, and docker-compose deployment.',
      resources: ['Official Docker Docs', 'FreeCodeCamp Docker Course']
    },
    {
      id: 2,
      title: 'Implement Microservices with Spring Cloud',
      category: 'Backend Architecture',
      time: '3 Weeks',
      priority: 'High',
      status: 'Learning',
      description: 'Build REST APIs with Eureka Service Discovery, Spring Cloud Gateway, and Circuit Breakers.',
      resources: ['Baeldung Spring Cloud', 'Spring Microservices in Action']
    },
    {
      id: 3,
      title: 'Setup Automated CI/CD Pipelines',
      category: 'DevOps Automation',
      time: '1 Week',
      priority: 'Medium',
      status: 'Not Started',
      description: 'Configure GitHub Actions workflows for automated testing, linting, and cloud staging deployment.',
      resources: ['GitHub Actions Documentation']
    },
    {
      id: 4,
      title: 'Integrate Redis In-Memory Caching',
      category: 'Database Optimization',
      time: '1 Week',
      priority: 'Medium',
      status: 'Not Started',
      description: 'Implement distributed session management and query caching using Redis & Spring Data Redis.',
      resources: ['Redis Developer Guide']
    }
  ]);

  const toggleStatus = (id) => {
    setSteps(prev => prev.map(s => {
      if (s.id === id) {
        const nextStatus = s.status === 'Completed' ? 'Not Started' : s.status === 'Learning' ? 'Completed' : 'Learning';
        return { ...s, status: nextStatus };
      }
      return s;
    }));
  };

  return (
    <SidebarLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="glass-card rounded-3xl p-8 border border-slate-800/80 shadow-2xl space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold uppercase tracking-wider">
            <Map className="w-3.5 h-3.5" />
            <span>Structured Upskilling Progression</span>
          </div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">Personalized Career Roadmap</h1>
          <p className="text-xs text-slate-400">
            Step-by-step learning path generated from your skill gap analysis to reach 95%+ ATS qualification.
          </p>
        </div>

        {/* Roadmap Step Timeline */}
        <div className="space-y-4">
          {steps.map((step, idx) => (
            <div
              key={step.id}
              className={`glass-card p-6 rounded-3xl border transition-all space-y-3 ${
                step.status === 'Completed'
                  ? 'border-emerald-500/40 bg-emerald-950/10'
                  : step.status === 'Learning'
                  ? 'border-indigo-500/40 bg-indigo-950/10'
                  : 'border-slate-800/80'
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <span className="w-8 h-8 rounded-xl bg-slate-800 text-slate-300 font-extrabold text-xs flex items-center justify-center flex-shrink-0">
                    0{idx + 1}
                  </span>
                  <div>
                    <h3 className="text-sm font-extrabold text-white">{step.title}</h3>
                    <p className="text-[10px] text-slate-400 font-semibold">{step.category} • Estimated Time: {step.time}</p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <button
                    onClick={() => toggleStatus(step.id)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all border ${
                      step.status === 'Completed'
                        ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40'
                        : step.status === 'Learning'
                        ? 'bg-indigo-500/20 text-indigo-400 border-indigo-500/40'
                        : 'bg-slate-800 text-slate-400 border-slate-700'
                    }`}
                  >
                    {step.status}
                  </button>
                </div>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed pl-11">{step.description}</p>

              <div className="pl-11 pt-2 flex flex-wrap items-center gap-2 text-[11px] text-slate-400 font-medium">
                <BookOpen className="w-3.5 h-3.5 text-indigo-400" />
                <span>Recommended Resources:</span>
                {step.resources.map((res, i) => (
                  <span key={i} className="px-2 py-0.5 rounded bg-slate-800 text-indigo-300 font-semibold">
                    {res}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </SidebarLayout>
  );
};

export default CareerRoadmapPage;
