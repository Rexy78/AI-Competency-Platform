import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BarChart3, BrainCircuit, ClipboardCheck, Gauge, Loader2, Sparkles } from 'lucide-react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import Footer from '../components/Footer';
import api from '../services/api';

const roleOptions = ['Java Developer', 'Java Backend Developer', 'Full Stack Developer', 'Data Scientist', 'Backend Engineer'];
const interviewTypes = [
  { value: 'full-practice', label: 'Full Placement Practice Test' },
  { value: 'technical', label: 'Technical MCQ' },
  { value: 'aptitude', label: 'Aptitude MCQ' },
  { value: 'communication', label: 'Communication MCQ' },
  { value: 'logical', label: 'Logical Ability' },
  { value: 'reasoning', label: 'Reasoning' },
  { value: 'coding', label: 'Coding Practice' },
];
const defaultSections = ['communication', 'aptitude', 'logical', 'reasoning', 'technical', 'coding'];
const difficultyLevels = ['Beginner', 'Intermediate', 'Advanced'];

const InterviewSetupPage = () => {
  const navigate = useNavigate();
  const [targetRole, setTargetRole] = useState('Java Backend Developer');
  const [interviewType, setInterviewType] = useState('full-practice');
  const [selectedSections, setSelectedSections] = useState(defaultSections);
  const [difficulty, setDifficulty] = useState('Intermediate');
  const [questionCount, setQuestionCount] = useState(62);
  const [codingLanguage, setCodingLanguage] = useState('Java');
  const [jobDescription, setJobDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await api.get('/interview/history');
        setHistory(Array.isArray(res.data) ? res.data : []);
      } catch (error) {
        console.error('History fetch failed', error);
      }
    };
    fetchHistory();
  }, []);

  const previousStats = useMemo(() => {
    if (!history.length) {
      return { average: 0, interviews: 0, strongest: 'N/A', weakest: 'N/A' };
    }
    const avg = Math.round(history.reduce((sum, item) => sum + (Number(item.score) || 0), 0) / history.length);
    const strongest = history.reduce((best, current) => (Number(current.score) || 0) > (Number(best.score) || 0) ? current : best, history[0]);
    const weakest = history.reduce((lowest, current) => (Number(current.score) || 0) < (Number(lowest.score) || 0) ? current : lowest, history[0]);
    return {
      average: avg,
      interviews: history.length,
      strongest: strongest?.target_role || 'N/A',
      weakest: weakest?.target_role || 'N/A',
    };
  }, [history]);

  const sectionOptions = [
    { value: 'communication', label: 'Communication', badge: 'Grammar + Soft Skills' },
    { value: 'aptitude', label: 'Quantitative Aptitude', badge: 'Math + Arithmetic' },
    { value: 'logical', label: 'Logical Ability', badge: 'Series + Puzzles' },
    { value: 'reasoning', label: 'Reasoning', badge: 'Patterns + Deductions' },
    { value: 'technical', label: 'Technical MCQ', badge: 'Core skills' },
    { value: 'coding', label: 'Coding Practice', badge: 'Java / Python' },
  ];

  const toggleSection = (section) => {
    setInterviewType('full-practice');
    setSelectedSections((current) => {
      if (section === 'coding') {
        return current.includes('coding') ? current : [...current, 'coding'];
      }
      if (current.includes(section)) {
        return current.filter((item) => item !== section);
      }
      return [...current, section];
    });
  };

  const handleInterviewTypeChange = (type) => {
    setInterviewType(type);
    setSelectedSections(type === 'full-practice' ? defaultSections : [type]);
  };

  const handleStart = async () => {
    setLoading(true);
    try {
      const finalSections = interviewType === 'full-practice'
        ? [...selectedSections.filter((section) => section !== 'coding'), 'coding']
        : (selectedSections.length ? selectedSections : [interviewType]);
      const finalType = interviewType === 'full-practice' ? 'full-practice' : (finalSections.length > 1 ? 'mixed-practice' : finalSections[0]);
      const balancedCount = finalSections.includes('coding') ? 62 : 60;
      const payload = {
        target_role: targetRole,
        interview_type: finalType,
        difficulty,
        question_count: Number(questionCount) || balancedCount,
        job_description: jobDescription || null,
        coding_language: finalSections.includes('coding') ? codingLanguage : null,
        sections: finalSections,
      };

      const res = await api.post('/interview/start', payload);
      navigate(`/interview/session/${res.data.session_id}`);
    } catch (error) {
      console.error('Practice-test start failed:', error);
      const message = error?.response?.data?.detail
        || (error?.response
          ? `The practice-test API returned HTTP ${error.response.status}. Please try again or contact support.`
          : `Unable to reach the API at ${api.defaults.baseURL}. Start the backend and try again.`);
      alert(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <Navbar />
      <div className="flex max-w-7xl mx-auto">
        <Sidebar />
        <main className="flex-1 p-6 md:p-8">
          <div className="glass-card rounded-3xl p-6 border border-slate-800 bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-2xl gradient-bg flex items-center justify-center text-white">
                <ClipboardCheck className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-indigo-400 font-bold">AI Practice Test</p>
                <h1 className="text-2xl md:text-3xl font-extrabold text-white">Adaptive Candidate Practice Test</h1>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-[1.3fr_0.7fr] gap-6 mt-6">
            <div className="glass-card rounded-3xl p-6 border border-slate-800/80">
              <div className="space-y-5">
                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-2">Choose Target Role</label>
                  <select value={targetRole} onChange={(e) => setTargetRole(e.target.value)} className="w-full px-3 py-3 rounded-xl bg-slate-900 border border-slate-700 text-white text-sm">
                    {roleOptions.map((role) => <option key={role} value={role}>{role}</option>)}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-2">Practice Test Type</label>
                  <select value={interviewType} onChange={(e) => handleInterviewTypeChange(e.target.value)} className="w-full px-3 py-3 rounded-xl bg-slate-900 border border-slate-700 text-white text-sm">
                    {interviewTypes.map((type) => <option key={type.value} value={type.value}>{type.label}</option>)}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-2">Practice Sections</label>
                  <p className="mb-3 text-xs text-slate-400">Every selected section contains MCQs. The final section is always a coding test.</p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {sectionOptions.map((option) => {
                      const isSelected = selectedSections.includes(option.value);
                      return (
                        <button
                          key={option.value}
                          type="button"
                          onClick={() => toggleSection(option.value)}
                          aria-pressed={isSelected}
                          className={`rounded-2xl border p-3 text-left transition-all ${
                            isSelected
                              ? 'border-indigo-500/60 bg-indigo-500/10 text-white shadow-glow'
                              : 'border-slate-700 bg-slate-900 text-slate-300 hover:border-slate-500'
                          }`}
                        >
                          <div className="flex items-center justify-between gap-2">
                            <span className="text-sm font-bold">{option.label}</span>
                            <span className={`w-3 h-3 rounded-full ${isSelected ? 'bg-emerald-400' : 'bg-slate-600'}`} />
                          </div>
                          <div className="mt-2 text-[10px] uppercase tracking-[0.15em] text-slate-400">{option.badge}</div>
                        </button>
                      );
                    })}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-300 mb-2">Difficulty</label>
                    <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)} className="w-full px-3 py-3 rounded-xl bg-slate-900 border border-slate-700 text-white text-sm">
                      {difficultyLevels.map((level) => <option key={level} value={level}>{level}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-300 mb-2">Number of Questions</label>
                    <select value={questionCount} onChange={(e) => setQuestionCount(Number(e.target.value))} className="w-full px-3 py-3 rounded-xl bg-slate-900 border border-slate-700 text-white text-sm">
                      {[20, 40, 62, 80].map((count) => <option key={count} value={count}>{count}</option>)}
                    </select>
                  </div>
                </div>

                {(interviewType === 'coding' || selectedSections.includes('coding')) && (
                  <div>
                    <label className="block text-xs font-bold text-slate-300 mb-2">Coding Language</label>
                    <select value={codingLanguage} onChange={(e) => setCodingLanguage(e.target.value)} className="w-full px-3 py-3 rounded-xl bg-slate-900 border border-slate-700 text-white text-sm">
                      <option value="Java">Java</option>
                      <option value="Python">Python</option>
                    </select>
                  </div>
                )}

                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-2">Optional Job Description</label>
                  <textarea value={jobDescription} onChange={(e) => setJobDescription(e.target.value)} rows={5} placeholder="Paste job description to align the adaptively generated interview with role-specific requirements..." className="w-full px-3 py-3 rounded-xl bg-slate-900 border border-slate-700 text-white text-sm" />
                </div>

                <button onClick={handleStart} disabled={loading} className="w-full py-3 rounded-2xl gradient-bg text-white font-extrabold text-sm shadow-glow flex items-center justify-center gap-2">
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Sparkles className="w-4 h-4" /> Start Practice Test</>}
                </button>
              </div>
            </div>

            <div className="space-y-5">
              <div className="glass-card rounded-3xl p-5 border border-slate-800/80">
                <h3 className="text-sm font-bold uppercase tracking-[0.18em] text-slate-300">Previous Performance</h3>
                <div className="mt-4 space-y-4">
                  <div className="flex items-center justify-between text-sm"><span>Average Score</span><span className="font-extrabold text-emerald-400">{previousStats.average}%</span></div>
                  <div className="flex items-center justify-between text-sm"><span>Interviews Completed</span><span className="font-extrabold text-white">{previousStats.interviews}</span></div>
                  <div className="flex items-center justify-between text-sm"><span>Strongest Topic</span><span className="font-extrabold text-indigo-400">{previousStats.strongest}</span></div>
                  <div className="flex items-center justify-between text-sm"><span>Weakest Topic</span><span className="font-extrabold text-rose-400">{previousStats.weakest}</span></div>
                </div>
              </div>

              <div className="glass-card rounded-3xl p-5 border border-slate-800/80">
                <div className="flex items-center gap-2 text-indigo-400 text-xs font-bold uppercase tracking-[0.15em]"><BrainCircuit className="w-4 h-4" /> AI Strategy</div>
                <ul className="mt-4 space-y-2 text-xs text-slate-300">
                  <li>• Resume-aware question generation</li>
                  <li>• Adaptive difficulty escalation</li>
                  <li>• Weak-topic reinforcement</li>
                  <li>• Final role-readiness analysis</li>
                </ul>
              </div>

              <div className="glass-card rounded-3xl p-5 border border-slate-800/80">
                <div className="flex items-center gap-2 text-amber-400 text-xs font-bold uppercase tracking-[0.15em]"><Gauge className="w-4 h-4" /> Readiness</div>
                <div className="mt-4 flex items-end gap-2">
                  <span className="text-3xl font-extrabold text-white">{previousStats.average || 72}</span>
                  <span className="text-xs text-slate-400 mb-1">/ 100</span>
                </div>
                <div className="mt-4 h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-2 rounded-full bg-gradient-to-r from-emerald-400 to-indigo-500" style={{ width: `${Math.min(100, previousStats.average || 72)}%` }} />
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
      <Footer />
    </div>
  );
};

export default InterviewSetupPage;
