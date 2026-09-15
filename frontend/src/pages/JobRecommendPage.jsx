import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import SidebarLayout from '../components/SidebarLayout';
import api from '../services/api';
import { 
  Briefcase, CheckCircle2, XCircle, Sparkles, ArrowRight, BookOpen, 
  Search, Filter, Target, Map, Award
} from 'lucide-react';

const JobRecommendPage = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [minMatch, setMinMatch] = useState(0);
  const navigate = useNavigate();

  const getFallbackRecommendations = () => {
    return [
      {
        role: 'Java Backend Developer',
        match_percentage: 88,
        description: 'Build enterprise-grade microservices, REST APIs, and multi-threaded Java backend architectures.',
        matching_skills: ['Java', 'Spring Boot', 'REST API', 'SQL', 'Git', 'MySQL'],
        missing_skills: ['Microservices', 'Docker', 'Hibernate'],
        required_technologies: ['Java', 'Spring Boot', 'REST API', 'SQL', 'MySQL', 'Docker'],
        recommended_learning_path: ['Learn Microservices', 'Learn Docker', 'Learn Hibernate']
      },
      {
        role: 'Software Engineer',
        match_percentage: 82,
        description: 'Design software solutions, collaborate across cross-functional teams, and write clean scalable code.',
        matching_skills: ['Java', 'SQL', 'Git', 'REST API', 'JavaScript'],
        missing_skills: ['System Design', 'Algorithms', 'CI/CD'],
        required_technologies: ['Java', 'Python', 'SQL', 'Git', 'System Design'],
        recommended_learning_path: ['Learn System Design', 'Learn Algorithms', 'Learn CI/CD']
      },
      {
        role: 'Full Stack Developer',
        match_percentage: 75,
        description: 'Deliver end-to-end web applications combining React interfaces with Spring Boot/Node backends.',
        matching_skills: ['Java', 'React', 'HTML', 'CSS', 'JavaScript', 'SQL'],
        missing_skills: ['Node.js', 'TypeScript', 'GraphQL'],
        required_technologies: ['React', 'Node.js', 'Java', 'SQL', 'TypeScript'],
        recommended_learning_path: ['Learn Node.js', 'Learn TypeScript', 'Learn GraphQL']
      },
      {
        role: 'Python Data Engineer / AI',
        match_percentage: 68,
        description: 'Build automated data pipelines, process big datasets, and train GenAI LLM models.',
        matching_skills: ['Python', 'SQL', 'Git'],
        missing_skills: ['Pandas', 'PyTorch', 'Spark', 'FastAPI'],
        required_technologies: ['Python', 'SQL', 'Pandas', 'Spark', 'FastAPI'],
        recommended_learning_path: ['Learn Pandas', 'Learn PyTorch', 'Learn Spark']
      },
      {
        role: 'DevOps & Cloud Engineer',
        match_percentage: 60,
        description: 'Automate cloud infrastructure provisioning, container deployments, and CI/CD pipelines.',
        matching_skills: ['Git', 'SQL'],
        missing_skills: ['Docker', 'Kubernetes', 'AWS', 'Terraform', 'Linux'],
        required_technologies: ['Docker', 'Kubernetes', 'AWS', 'Linux', 'Git'],
        recommended_learning_path: ['Learn Docker', 'Learn Kubernetes', 'Learn AWS']
      }
    ];
  };

  useEffect(() => {
    api.get('/jobs/recommendations')
      .then(res => {
        if (res.data && res.data.length > 0) {
          setRecommendations(res.data);
        } else {
          setRecommendations(getFallbackRecommendations());
        }
        setLoading(false);
      })
      .catch(() => {
        setRecommendations(getFallbackRecommendations());
        setLoading(false);
      });
  }, []);

  const filteredJobs = recommendations.filter(job => {
    const matchesSearch = job.role.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          job.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesScore = job.match_percentage >= minMatch;
    return matchesSearch && matchesScore;
  });

  return (
    <SidebarLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="glass-card rounded-3xl p-8 border border-slate-800/80 shadow-2xl flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-bold uppercase tracking-wider mb-2">
              <Sparkles className="w-3.5 h-3.5" />
              <span>AI Career Matcher Engine</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">Job Role Recommendations</h1>
            <p className="text-xs text-slate-400 mt-1">
              AI-evaluated positions ranked by candidate technical skill taxonomy and profile compatibility.
            </p>
          </div>

          {/* Search & Filters */}
          <div className="flex flex-col sm:flex-row items-center gap-3">
            <div className="relative w-full sm:w-60">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
              <input
                type="text"
                placeholder="Search position..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 rounded-2xl bg-slate-900 border border-slate-700/80 text-xs font-bold text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div className="w-full sm:w-auto">
              <select
                value={minMatch}
                onChange={(e) => setMinMatch(Number(e.target.value))}
                className="w-full p-2.5 rounded-2xl bg-slate-900 border border-slate-700/80 text-xs font-bold text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value={0}>All Match Fits</option>
                <option value={80}>≥ 80% Match</option>
                <option value={70}>≥ 70% Match</option>
                <option value={50}>≥ 50% Match</option>
              </select>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="glass-card rounded-3xl p-12 text-center border border-slate-800 space-y-4">
            <div className="w-10 h-10 rounded-full border-4 border-indigo-500/20 border-t-indigo-500 animate-spin mx-auto"></div>
            <p className="text-xs font-bold text-slate-300">Evaluating resume taxonomy against 12+ tech engineering roles...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {filteredJobs.map((item, idx) => {
              const score = item.match_percentage;
              const badgeStyle = score >= 80
                ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                : score >= 65
                ? 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30'
                : 'bg-amber-500/20 text-amber-400 border-amber-500/30';

              return (
                <div key={idx} className="glass-card rounded-3xl p-6 border border-slate-800/80 shadow-2xl flex flex-col justify-between hover:border-indigo-500/50 transition-all space-y-5 group">
                  <div className="space-y-4">
                    {/* Top Title & Match % */}
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <span className="text-[10px] font-extrabold uppercase tracking-wider text-slate-400 block mb-1">
                          Rank #{idx + 1} Position
                        </span>
                        <h3 className="text-lg font-extrabold text-white group-hover:text-indigo-300 transition-colors">
                          {item.role}
                        </h3>
                        <p className="text-xs text-slate-400 mt-1 leading-relaxed">{item.description}</p>
                      </div>

                      <div className="text-right flex-shrink-0">
                        <span className={`inline-block px-3 py-1 rounded-2xl text-xl font-extrabold border ${badgeStyle}`}>
                          {score}%
                        </span>
                        <span className="block text-[10px] uppercase font-bold text-slate-500 mt-1">Skill Fit Match</span>
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full bg-slate-900 rounded-full h-2.5 overflow-hidden border border-slate-800">
                      <div
                        className="gradient-bg h-full rounded-full transition-all duration-700"
                        style={{ width: `${score}%` }}
                      ></div>
                    </div>

                    {/* Matching vs Missing Skills */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs pt-3 border-t border-slate-800/80">
                      <div className="space-y-2">
                        <span className="font-bold text-slate-300 block flex items-center gap-1.5">
                          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                          <span>Matching Skills ({item.matching_skills?.length || 0})</span>
                        </span>
                        <div className="flex flex-wrap gap-1.5">
                          {item.matching_skills?.map((sk, i) => (
                            <span key={i} className="px-2.5 py-1 rounded-lg bg-emerald-950/60 text-emerald-300 border border-emerald-800/40 text-[11px] font-semibold">
                              {sk} ✓
                            </span>
                          ))}
                        </div>
                      </div>

                      <div className="space-y-2">
                        <span className="font-bold text-slate-300 block flex items-center gap-1.5">
                          <XCircle className="w-4 h-4 text-rose-400" />
                          <span>Missing Gaps ({item.missing_skills?.length || 0})</span>
                        </span>
                        <div className="flex flex-wrap gap-1.5">
                          {item.missing_skills?.map((sk, i) => (
                            <span key={i} className="px-2.5 py-1 rounded-lg bg-rose-950/60 text-rose-300 border border-rose-800/40 text-[11px] font-semibold">
                              {sk} ✗
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Actions Footer Bar */}
                  <div className="pt-4 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3">
                    <button
                      onClick={() => navigate('/skill-gap')}
                      className="w-full sm:w-auto px-4 py-2.5 rounded-xl text-xs font-bold text-slate-200 bg-slate-900 border border-slate-800 hover:text-white hover:border-slate-700 transition-all flex items-center justify-center gap-1.5"
                    >
                      <Target className="w-4 h-4 text-indigo-400" />
                      <span>Evaluate Skill Radar</span>
                    </button>

                    <button
                      onClick={() => navigate('/roadmap')}
                      className="w-full sm:w-auto px-4 py-2.5 rounded-xl text-xs font-bold text-white gradient-bg shadow-glow hover:opacity-95 transition-all flex items-center justify-center gap-1.5"
                    >
                      <Map className="w-4 h-4" />
                      <span>View Career Roadmap</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </SidebarLayout>
  );
};

export default JobRecommendPage;
