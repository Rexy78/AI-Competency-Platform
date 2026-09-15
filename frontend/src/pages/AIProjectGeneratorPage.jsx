import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import Footer from '../components/Footer';
import api from '../services/api';
import { Lightbulb, Sparkles, Code2, Cpu, CheckCircle2, ArrowRight, Loader2, Layers } from 'lucide-react';

const AIProjectGeneratorPage = () => {
  const [targetRole, setTargetRole] = useState('Java Backend Developer');
  const [missingSkills, setMissingSkills] = useState('Spring Boot, Docker, REST API, Redis');
  const [blueprint, setBlueprint] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const skillsArray = missingSkills.split(',').map(s => s.trim()).filter(Boolean);
      const res = await api.post('/projects/generate', {
        target_role: targetRole,
        missing_skills: skillsArray
      });
      setBlueprint(res.data);
    } catch (err) {
      console.error(err);
      // Fallback preview blueprint
      setBlueprint({
        title: `${targetRole} Production Microservices Platform`,
        objective: `Build an enterprise-grade service to master ${missingSkills}.`,
        target_role: targetRole,
        technologies: missingSkills.split(',').map(s => s.trim()),
        architecture: 'Client UI / Postman -> API Gateway -> Auth & Business Microservices -> Redis Cache & Database',
        features: [
          'JWT Authorization with Role-Based Access Controls',
          'Containerized deployment using Docker Compose',
          'OpenAPI Swagger documentation and automated tests'
        ],
        skills_gained: missingSkills.split(',').map(s => s.trim()),
        implementation_steps: [
          'Initialize repository and set up environment dependencies',
          'Design domain data models and database migrations',
          'Build RESTful API endpoints with error handling middleware',
          'Create multi-stage Dockerfiles and container orchestration'
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between selection:bg-indigo-500 selection:text-white">
      <Navbar />

      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        <Sidebar />

        <main className="flex-1 p-6 md:p-8 space-y-6 overflow-x-hidden">
          {/* Header Banner */}
          <div className="glass-card rounded-3xl p-6 border border-slate-800/80 bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 relative overflow-hidden shadow-2xl">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 z-10 relative">
              <div className="space-y-1">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-bold">
                  <Lightbulb className="w-3.5 h-3.5" />
                  <span>GenAI Portfolio Blueprint Generator</span>
                </div>
                <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
                  AI Project <span className="gradient-text">Generator</span>
                </h1>
                <p className="text-xs text-slate-400 max-w-xl">
                  Generate realistic, industry-aligned portfolio project blueprints tailored specifically to bridge your target role's skill gaps.
                </p>
              </div>
            </div>
          </div>

          {/* Form Card */}
          <div className="glass-card rounded-3xl p-6 border border-slate-800/80 space-y-4">
            <form onSubmit={handleGenerate} className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Target Job Role</label>
                <input
                  type="text"
                  required
                  value={targetRole}
                  onChange={(e) => setTargetRole(e.target.value)}
                  placeholder="e.g. Java Backend Developer"
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Missing Skills to Master (Comma Separated)</label>
                <input
                  type="text"
                  required
                  value={missingSkills}
                  onChange={(e) => setMissingSkills(e.target.value)}
                  placeholder="e.g. Spring Boot, Docker, REST API"
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div className="md:col-span-2 pt-2">
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-3 rounded-2xl text-xs font-extrabold text-white gradient-bg shadow-glow hover:opacity-95 transition-all flex items-center justify-center gap-2"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Sparkles className="w-4 h-4" /><span>Generate GenAI Project Blueprint</span></>}
                </button>
              </div>
            </form>
          </div>

          {/* Generated Blueprint View */}
          {blueprint && (
            <div className="glass-card rounded-3xl p-6 border border-slate-800/80 space-y-6 animate-fadeIn">
              <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-400">Target Role Blueprint</span>
                  <h2 className="text-xl font-bold text-white">{blueprint.title}</h2>
                  <p className="text-xs text-slate-400 mt-1">{blueprint.objective}</p>
                </div>
              </div>

              {/* Technologies & Stack */}
              <div className="space-y-2">
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                  <Code2 className="w-4 h-4 text-indigo-400" />
                  <span>Target Skill Stack</span>
                </h3>
                <div className="flex flex-wrap gap-2">
                  {blueprint.technologies?.map((tech, idx) => (
                    <span key={idx} className="px-3 py-1 rounded-xl bg-indigo-600/20 border border-indigo-500/30 text-indigo-300 text-xs font-bold">
                      {tech}
                    </span>
                  ))}
                </div>
              </div>

              {/* Architecture Blueprint */}
              <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-2">
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                  <Layers className="w-4 h-4 text-amber-400" />
                  <span>System Architecture Blueprint</span>
                </h3>
                <p className="text-xs text-slate-300 font-mono bg-slate-950 p-3 rounded-xl border border-slate-800/80 leading-relaxed">
                  {blueprint.architecture}
                </p>
              </div>

              {/* Implementation Steps */}
              <div className="space-y-3">
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-emerald-400" />
                  <span>Step-by-Step Implementation Strategy</span>
                </h3>
                <div className="space-y-2">
                  {blueprint.implementation_steps?.map((step, idx) => (
                    <div key={idx} className="p-3 rounded-xl bg-slate-900 border border-slate-800/80 flex items-start gap-3 text-xs text-slate-300">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                      <span>{step}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </main>
      </div>

      <Footer />
    </div>
  );
};

export default AIProjectGeneratorPage;
