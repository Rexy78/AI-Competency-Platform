import React, { useEffect, useState } from 'react';
import SidebarLayout from '../components/SidebarLayout';
import api from '../services/api';
import { 
  Map, CheckCircle2, Clock, Award, Sparkles, BookOpen, 
  ArrowDown, Check, ExternalLink, RefreshCw, Target, PlayCircle 
} from 'lucide-react';

const RoadmapPage = () => {
  const [targetRole, setTargetRole] = useState('Java Backend Developer');
  const [steps, setSteps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  const targetRolesList = [
    'Java Backend Developer',
    'Full Stack Developer',
    'Frontend Developer (React)',
    'Backend Developer',
    'Python Data Engineer / AI',
    'Data Analyst',
    'Data Scientist',
    'Machine Learning Engineer',
    'AI Engineer',
    'DevOps & Cloud Engineer',
    'Cloud Engineer',
    'Software Engineer (General)'
  ];

  const getPlatformUrl = (platform, title, skill) => {
    const query = encodeURIComponent(title || skill || 'programming tutorial');
    const platLower = (platform || '').toLowerCase();

    if (platLower.includes('coursera')) {
      return `https://www.coursera.org/search?query=${query}`;
    } else if (platLower.includes('udemy')) {
      return `https://www.udemy.com/courses/search/?q=${query}`;
    } else if (platLower.includes('youtube') || platLower.includes('freecodecamp')) {
      return `https://www.youtube.com/results?search_query=${query}`;
    } else if (platLower.includes('leetcode') || platLower.includes('hackerrank')) {
      return `https://leetcode.com/problemset/all/?search=${query}`;
    } else if (platLower.includes('github')) {
      return `https://github.com/search?q=${query}`;
    } else if (platLower.includes('edx')) {
      return `https://www.edx.org/search?q=${query}`;
    } else if (platLower.includes('aws')) {
      return `https://aws.amazon.com/training/`;
    } else if (platLower.includes('postman')) {
      return `https://learning.postman.com/`;
    } else {
      return `https://www.google.com/search?q=${query}+official+documentation`;
    }
  };

  const getFallbackRoadmap = (role) => {
    return [
      {
        id: 1,
        skill: `${role} Core Fundamentals`,
        category: 'Core Engineering',
        difficulty: 'Beginner',
        estimated_time: '2 Weeks',
        priority: 'High',
        status: 'Completed',
        description: 'Master core syntax, data structures, OOP design patterns, and version control fundamentals.',
        prerequisites: ['Computer Science Basics'],
        online_platforms: [
          { platform: 'Coursera', title: `${role} Specialization (Duke University)`, url: `https://www.coursera.org/search?query=${encodeURIComponent(role)}`, type: 'Interactive Course' },
          { platform: 'YouTube / freeCodeCamp', title: `${role} Full Beginner Tutorial`, url: `https://www.youtube.com/results?search_query=${encodeURIComponent(role + " tutorial freecodecamp")}`, type: 'Video Tutorial' },
          { platform: 'Official Documentation', title: 'Official Language Docs & Standard Manual', url: `https://developer.mozilla.org`, type: 'Documentation' }
        ]
      },
      {
        id: 2,
        skill: 'Backend Framework & REST API Architecture',
        category: 'Backend',
        difficulty: 'Intermediate',
        estimated_time: '3 Weeks',
        priority: 'High',
        status: 'Learning',
        description: 'Build high-throughput RESTful web microservices, DTO validation, and JSON data mapping.',
        prerequisites: ['Core Fundamentals', 'Git'],
        online_platforms: [
          { platform: 'Udemy', title: 'Mastering Spring Boot & REST APIs', url: `https://www.udemy.com/courses/search/?q=spring+boot+rest+api`, type: 'Paid Video Course' },
          { platform: 'GitHub Repositories', title: 'Awesome-Backend Microservice Boilerplate', url: `https://github.com/search?q=spring+boot+microservices+template`, type: 'Code Architecture' },
          { platform: 'Postman Academy', title: 'REST API Design & Testing Certification', url: `https://learning.postman.com/`, type: 'Interactive Testing' }
        ]
      },
      {
        id: 3,
        skill: 'Database Systems & ORM Persistence',
        category: 'Database',
        difficulty: 'Intermediate',
        estimated_time: '2 Weeks',
        priority: 'High',
        status: 'Not Started',
        description: 'Design relational database schemas, write complex SQL joins, and optimize query indexing.',
        prerequisites: ['REST APIs', 'SQL Basics'],
        online_platforms: [
          { platform: 'LeetCode / HackerRank', title: 'Top SQL Interview Database Challenges', url: `https://leetcode.com/problemset/all/?search=sql`, type: 'Coding Practice' },
          { platform: 'Coursera', title: 'Database Management Essentials (University of Colorado)', url: `https://www.coursera.org/search?query=database+management`, type: 'University Course' },
          { platform: 'PostgreSQL Official', title: 'PostgreSQL Tutorial & Indexing Manual', url: `https://www.postgresql.org/docs/`, type: 'Documentation' }
        ]
      },
      {
        id: 4,
        skill: 'Docker Containerization & Microservices',
        category: 'DevOps',
        difficulty: 'Intermediate',
        estimated_time: '2 Weeks',
        priority: 'Medium',
        status: 'Not Started',
        description: 'Package applications with Dockerfiles and orchestrate multi-container services via Docker Compose.',
        prerequisites: ['Linux CLI', 'REST APIs'],
        online_platforms: [
          { platform: 'Docker Official Docs', title: 'Docker Getting Started Guide & CLI Reference', url: `https://docs.docker.com/get-started/`, type: 'Official Manual' },
          { platform: 'freeCodeCamp', title: 'Docker for Beginners - Full Course', url: `https://www.youtube.com/results?search_query=docker+for+beginners+freecodecamp`, type: 'Free Video Course' },
          { platform: 'Udemy', title: 'Docker & Kubernetes: The Practical Guide', url: `https://www.udemy.com/courses/search/?q=docker+kubernetes`, type: 'Certification Course' }
        ]
      },
      {
        id: 5,
        skill: 'Cloud Infrastructure & CI/CD Deployment',
        category: 'Cloud',
        difficulty: 'Advanced',
        estimated_time: '3 Weeks',
        priority: 'Medium',
        status: 'Not Started',
        description: 'Automate build and deployment pipelines using GitHub Actions onto AWS cloud infrastructure.',
        prerequisites: ['Docker', 'Git'],
        online_platforms: [
          { platform: 'AWS Skill Builder', title: 'AWS Cloud Practitioner & Solutions Architect Essentials', url: `https://aws.amazon.com/training/`, type: 'Cloud Training' },
          { platform: 'GitHub Skills', title: 'Automate workflows with GitHub Actions', url: `https://skills.github.com/`, type: 'Hands-on Lab' },
          { platform: 'edX', title: 'Cloud Computing Fundamentals (MIT / IEEE)', url: `https://www.edx.org/search?q=cloud+computing`, type: 'Academic Course' }
        ]
      }
    ];
  };

  const fetchRoadmap = (role) => {
    setLoading(true);
    api.get(`/roadmap?target_role=${encodeURIComponent(role)}`)
      .then(res => {
        if (res.data && res.data.steps && res.data.steps.length > 0) {
          setSteps(res.data.steps);
        } else {
          setSteps(getFallbackRoadmap(role));
        }
        setLoading(false);
      })
      .catch(() => {
        setSteps(getFallbackRoadmap(role));
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchRoadmap(targetRole);
  }, [targetRole]);

  const handleRegenerate = async () => {
    setGenerating(true);
    try {
      const res = await api.post('/roadmap/generate', { target_role: targetRole });
      if (res.data && res.data.steps && res.data.steps.length > 0) {
        setSteps(res.data.steps);
      } else {
        setSteps(getFallbackRoadmap(targetRole));
      }
      setGenerating(false);
    } catch (err) {
      console.error(err);
      setSteps(getFallbackRoadmap(targetRole));
      setGenerating(false);
    }
  };

  const handleStatusChange = async (stepId, newStatus) => {
    setSteps(prev => prev.map(s => s.id === stepId ? { ...s, status: newStatus } : s));

    try {
      await api.post('/roadmap/update', {
        step_id: stepId,
        status: newStatus,
        target_role: targetRole
      });
    } catch (err) {
      console.error('Failed to update status', err);
    }
  };

  const completedCount = steps.filter(s => s.status === 'Completed').length;
  const progressPct = steps.length > 0 ? Math.round((completedCount / steps.length) * 100) : 0;

  return (
    <SidebarLayout>
      <div className="space-y-6">
        {/* Header Bar */}
        <div className="glass-card rounded-3xl p-8 border border-slate-800/80 shadow-2xl flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-bold uppercase tracking-wider mb-2">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Gemini GenAI Career Roadmap</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">AI Skill Acquisition Roadmap</h1>
            <p className="text-xs text-slate-400 mt-1">
              Personalized sequential learning path with clickable online platforms (Coursera, Udemy, YouTube, freeCodeCamp, edX, Docs & LeetCode).
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
            <div>
              <label className="block text-[11px] font-extrabold uppercase tracking-wider text-slate-400 mb-1 flex items-center gap-1.5">
                <Target className="w-3.5 h-3.5 text-indigo-400" />
                <span>Target Role</span>
              </label>
              <select
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
                className="p-3 rounded-2xl bg-slate-900 border border-slate-700/80 text-xs font-bold text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                {targetRolesList.map((role) => (
                  <option key={role} value={role}>{role}</option>
                ))}
              </select>
            </div>

            <button
              onClick={handleRegenerate}
              disabled={generating}
              className="px-4 py-3 rounded-2xl text-xs font-extrabold text-white gradient-bg shadow-glow hover:opacity-95 flex items-center justify-center gap-2 transition-all self-end"
            >
              <RefreshCw className={`w-4 h-4 ${generating ? 'animate-spin' : ''}`} />
              <span>{generating ? 'Gemini AI Generating...' : 'Generate New Path'}</span>
            </button>
          </div>
        </div>

        {/* Progress Gauge */}
        <div className="glass-card rounded-3xl p-6 border border-slate-800/80 shadow-2xl flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="space-y-1 text-center sm:text-left">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Roadmap Execution Progress</h3>
            <p className="text-xs text-slate-400">Track your completed milestone steps as you acquire skills.</p>
          </div>

          <div className="flex items-center gap-4">
            <div className="w-48 bg-slate-900 rounded-full h-3 overflow-hidden border border-slate-800 p-0.5">
              <div
                className="gradient-bg h-full rounded-full transition-all duration-700"
                style={{ width: `${progressPct}%` }}
              ></div>
            </div>
            <span className="text-sm font-extrabold text-indigo-400">{progressPct}% ({completedCount}/{steps.length})</span>
          </div>
        </div>

        {loading ? (
          <div className="glass-card rounded-3xl p-12 text-center border border-slate-800 space-y-4">
            <div className="w-10 h-10 rounded-full border-4 border-indigo-500/20 border-t-indigo-500 animate-spin mx-auto"></div>
            <p className="text-xs font-bold text-slate-300">Generating Gemini AI career roadmap for {targetRole}...</p>
          </div>
        ) : (
          <div className="space-y-6 max-w-4xl mx-auto">
            {steps.map((step, idx) => (
              <div key={step.id} className="relative">
                {/* Vertical Line Connector */}
                {idx < steps.length - 1 && (
                  <div className="absolute left-8 top-16 bottom-0 w-0.5 bg-slate-800 -z-0 translate-y-2"></div>
                )}

                <div className={`relative z-10 glass-card rounded-3xl p-6 border transition-all space-y-4 ${
                  step.status === 'Completed'
                    ? 'border-emerald-500/40 bg-emerald-950/20'
                    : step.status === 'Learning'
                    ? 'border-indigo-500/60 shadow-glow'
                    : 'border-slate-800/80 shadow-2xl'
                }`}>
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
                    <div className="flex items-center gap-4">
                      {/* Step Status Badge Circle */}
                      <div className={`w-12 h-12 rounded-2xl flex items-center justify-center font-extrabold text-base flex-shrink-0 ${
                        step.status === 'Completed'
                          ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/30'
                          : step.status === 'Learning'
                          ? 'gradient-bg text-white shadow-glow'
                          : 'bg-slate-900 border border-slate-800 text-slate-400'
                      }`}>
                        {step.status === 'Completed' ? <Check className="w-6 h-6" /> : idx + 1}
                      </div>

                      <div>
                        <div className="flex items-center gap-2 flex-wrap">
                          <h3 className="text-base font-extrabold text-white">{step.skill}</h3>
                          <span className="px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 text-[10px] font-bold border border-indigo-500/30">
                            {step.category}
                          </span>
                        </div>
                        <p className="text-xs text-slate-400 mt-1">
                          Estimated Time: <span className="text-slate-200 font-semibold">{step.estimated_time || '2 Weeks'}</span> • Difficulty: <span className="text-slate-200 font-semibold">{step.difficulty || 'Intermediate'}</span>
                        </p>
                      </div>
                    </div>

                    {/* Step Status Buttons */}
                    <div className="flex items-center gap-1.5 bg-slate-900 p-1 rounded-2xl border border-slate-800">
                      <button
                        onClick={() => handleStatusChange(step.id, 'Not Started')}
                        className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                          step.status === 'Not Started'
                            ? 'bg-slate-800 text-white shadow'
                            : 'text-slate-500 hover:text-slate-300'
                        }`}
                      >
                        Not Started
                      </button>

                      <button
                        onClick={() => handleStatusChange(step.id, 'Learning')}
                        className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                          step.status === 'Learning'
                            ? 'gradient-bg text-white shadow-glow'
                            : 'text-slate-500 hover:text-slate-300'
                        }`}
                      >
                        Learning
                      </button>

                      <button
                        onClick={() => handleStatusChange(step.id, 'Completed')}
                        className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                          step.status === 'Completed'
                            ? 'bg-emerald-600 text-white shadow'
                            : 'text-slate-500 hover:text-slate-300'
                        }`}
                      >
                        Completed
                      </button>
                    </div>
                  </div>

                  {step.description && (
                    <p className="text-xs text-slate-300 leading-relaxed font-medium">
                      {step.description}
                    </p>
                  )}

                  {/* Online Platform Recommendations Section */}
                  <div className="space-y-3 pt-2">
                    <span className="text-xs font-extrabold uppercase tracking-wider text-indigo-400 flex items-center gap-2">
                      <BookOpen className="w-4 h-4" />
                      <span>Suggested Online Platform Recommendations (Click to Open)</span>
                    </span>

                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                      {(step.online_platforms || step.online_platform_recommendations || [
                        { platform: 'Coursera', title: `${step.skill} Specialization`, type: 'Interactive Course' },
                        { platform: 'YouTube / freeCodeCamp', title: `${step.skill} Full Beginner Tutorial`, type: 'Video Tutorial' },
                        { platform: 'Official Docs & LeetCode', title: `${step.skill} Reference & Practice`, type: 'Documentation & Hands-on' }
                      ]).map((item, pIdx) => {
                        const targetUrl = item.url || getPlatformUrl(item.platform, item.title || item.course_name, step.skill);

                        return (
                          <a
                            key={pIdx}
                            href={targetUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-indigo-500 hover:bg-slate-800/90 transition-all space-y-1.5 group block shadow-lg hover:shadow-indigo-500/20"
                          >
                            <div className="flex items-center justify-between">
                              <span className="text-[11px] font-extrabold text-indigo-300 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">
                                {item.platform || 'Online Platform'}
                              </span>
                              <ExternalLink className="w-3.5 h-3.5 text-slate-500 group-hover:text-indigo-400 group-hover:scale-110 transition-all" />
                            </div>
                            <p className="text-xs font-bold text-white truncate group-hover:text-indigo-300 transition-colors pt-1">
                              {item.title || item.course_name}
                            </p>
                            <span className="text-[10px] text-slate-400 font-medium block flex items-center justify-between">
                              <span>{item.type || 'Course / Tutorial'}</span>
                              <span className="text-indigo-400 font-bold group-hover:underline">Open Site ↗</span>
                            </span>
                          </a>
                        );
                      })}
                    </div>
                  </div>
                </div>

                {/* Downward Arrow Icon */}
                {idx < steps.length - 1 && (
                  <div className="flex justify-center my-3">
                    <ArrowDown className="w-5 h-5 text-slate-600 animate-bounce" />
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </SidebarLayout>
  );
};

export default RoadmapPage;
