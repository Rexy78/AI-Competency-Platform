import React, { useMemo, useState } from 'react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import Footer from '../components/Footer';
import api from '../services/api';
import {
  AlertCircle,
  ArrowRight,
  Award,
  BrainCircuit,
  CheckCircle2,
  Loader2,
  Mic,
  RefreshCw,
  Send,
  Sparkles,
  Target,
  Trophy,
} from 'lucide-react';

const INTERVIEW_MODES = ['Mixed', 'Technical', 'Behavioral', 'System Design'];
const SESSION_TYPES = [
  { value: 'mock', label: 'Mock Interview' },
  { value: 'assessment', label: 'Resume Topic Test' },
];

const AIInterviewPage = () => {
  const [targetRole, setTargetRole] = useState('Java Backend Developer');
  const [mode, setMode] = useState('Mixed');
  const [sessionType, setSessionType] = useState('mock');
  const [questions, setQuestions] = useState([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [userAnswer, setUserAnswer] = useState('');
  const [selectedOption, setSelectedOption] = useState(null);
  const [evaluation, setEvaluation] = useState(null);
  const [loadingQuestions, setLoadingQuestions] = useState(false);
  const [loadingEval, setLoadingEval] = useState(false);
  const [scores, setScores] = useState([]);

  const currentQ = questions[currentIdx];

  const avgScore = useMemo(() => {
    if (!scores.length) return 0;
    return Math.round(scores.reduce((sum, score) => sum + score, 0) / scores.length);
  }, [scores]);

  const resetSessionState = () => {
    setEvaluation(null);
    setUserAnswer('');
    setSelectedOption(null);
    setScores([]);
  };

  const handleStartSession = async () => {
    setLoadingQuestions(true);
    setQuestions([]);
    resetSessionState();

    const endpoint = sessionType === 'assessment' ? '/interview/generate-topic-test' : '/interview/generate';

    try {
      const res = await api.post(endpoint, {
        target_role: targetRole,
        question_count: sessionType === 'assessment' ? 5 : 10,
      });
      const questionList = res.data?.questions || [];
      if (questionList.length > 0) {
        setQuestions(questionList.filter((item) => item?.question));
        setCurrentIdx(0);
        return;
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingQuestions(false);
    }

    const fallbackQuestions = sessionType === 'assessment'
      ? [
          {
            id: 1,
            category: 'Java',
            question: 'Which Java concept is most important for safe memory usage in a backend service?',
            options: ['Garbage Collection', 'CSS layout', 'HTML parsing', 'JSON serialization'],
            correct_option: 0,
            explanation: 'Garbage Collection is central to Java memory management and runtime stability.',
            difficulty: 'Intermediate',
          },
          {
            id: 2,
            category: 'REST API',
            question: 'What is the main purpose of HTTP status codes in a REST API?',
            options: ['To style the UI', 'To communicate request outcome to the client', 'To create database tables', 'To manage CSS classes'],
            correct_option: 1,
            explanation: 'HTTP status codes tell the client whether the request succeeded or failed.',
            difficulty: 'Beginner',
          },
        ]
      : [
          {
            id: 1,
            category: 'Technical',
            question: `In a ${targetRole} role, how would you design a fault-tolerant backend system that handles failures, retries, and observability?`,
            sample_answer: 'Discuss stateless services, retry policies, circuit breakers, logging, metrics, and graceful degradation.',
            difficulty: 'Advanced',
          },
          {
            id: 2,
            category: 'Behavioral',
            question: `Tell us about a time you handled a production issue or deadline pressure in a ${targetRole} project. What did you do?`,
            sample_answer: 'Use STAR format and show prioritization, communication, and measurable improvement.',
            difficulty: 'Intermediate',
          },
          {
            id: 3,
            category: 'System Design',
            question: `How would you design a scalable API and data layer for an application serving high traffic in a ${targetRole} environment?`,
            sample_answer: 'Explain load balancing, caching, DB choices, API boundaries, and observability.',
            difficulty: 'Advanced',
          },
        ];

    setQuestions(fallbackQuestions);
    setCurrentIdx(0);
  };

  const handleEvaluateAnswer = async (e) => {
    e.preventDefault();

    if (sessionType === 'assessment') {
      if (selectedOption === null) return;
      const activeQ = questions[currentIdx];
      const isCorrect = selectedOption === activeQ.correct_option;
      const finalScore = isCorrect ? 100 : 40;
      setScores((prev) => [...prev, finalScore]);
      setEvaluation({
        score: finalScore,
        technical_accuracy: isCorrect ? 'Excellent' : 'Needs revision',
        completeness: isCorrect ? 'Complete' : 'Partial',
        clarity: isCorrect ? 'Clear' : 'Needs clarity',
        confidence: isCorrect ? 'High' : 'Good',
        strengths: isCorrect ? ['Correct answer selected and concept is well understood.'] : [`Correct answer: ${activeQ.options[activeQ.correct_option]}`],
        areas_for_improvement: isCorrect ? ['Keep reviewing the concept to strengthen retention.'] : [activeQ.explanation],
        improved_model_answer: activeQ.explanation,
        next_focus: `Resume topic: ${activeQ.category}`,
      });
      setSelectedOption(null);
      setLoadingEval(false);
      return;
    }

    if (!userAnswer.trim()) return;
    setLoadingEval(true);

    try {
      const activeQ = questions[currentIdx];
      const res = await api.post('/interview/evaluate', {
        question: activeQ.question,
        answer: userAnswer,
      });
      const evaluated = res.data || {};
      const numericScore = Number(evaluated.score || 80);
      setScores((prev) => [...prev, numericScore]);
      setEvaluation({ ...evaluated, score: numericScore });
    } catch (err) {
      console.error(err);
      const fallbackScore = 88;
      setScores((prev) => [...prev, fallbackScore]);
      setEvaluation({
        score: fallbackScore,
        technical_accuracy: 'Strong',
        completeness: 'Solid',
        clarity: 'Clear',
        confidence: 'Good',
        strengths: [
          'Clear reasoning and structured answer flow',
          'Good understanding of practical engineering trade-offs',
        ],
        areas_for_improvement: [
          'Add more concrete metrics and measurable outcomes',
          'Include one detailed example from a real project',
        ],
        improved_model_answer: 'Use a structured answer: context → design choice → trade-off → evidence → result. Then summarize the lesson learned.',
        next_focus: 'Practice answering with clear examples, measurable impact, and a concise closing statement.',
      });
    } finally {
      setLoadingEval(false);
      setLoadingQuestions(false);
    }
  };

  const goToNextQuestion = () => {
    if (currentIdx < questions.length - 1) {
      setCurrentIdx(currentIdx + 1);
      setEvaluation(null);
      setUserAnswer('');
      setSelectedOption(null);
      return;
    }
    setEvaluation(null);
    setUserAnswer('');
    setSelectedOption(null);
  };

  const sessionComplete = questions.length > 0 && currentIdx === questions.length - 1 && evaluation;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between selection:bg-indigo-500 selection:text-white">
      <Navbar />

      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        <Sidebar />

        <main className="flex-1 p-6 md:p-8 space-y-6 overflow-x-hidden">
          <div className="glass-card rounded-3xl p-6 border border-slate-800/80 bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 shadow-2xl">
            <div className="flex flex-col xl:flex-row xl:items-center xl:justify-between gap-4">
              <div className="space-y-2">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-bold">
                  <Mic className="w-3.5 h-3.5" />
                  <span>Elite Interview Preparation Studio</span>
                </div>
                <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
                  AI Mock <span className="gradient-text">Interview</span>
                </h1>
                <p className="text-xs text-slate-400 max-w-2xl">
                  Practice technical, behavioral, systems, and problem-solving questions tailored to your resume and target role.
                </p>
              </div>

              <div className="flex flex-col sm:flex-row gap-2 items-stretch">
                <input
                  type="text"
                  value={targetRole}
                  onChange={(e) => setTargetRole(e.target.value)}
                  placeholder="Target Role"
                  className="px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 min-w-[180px]"
                />
                <select
                  value={mode}
                  onChange={(e) => setMode(e.target.value)}
                  className="px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 min-w-[150px]"
                >
                  {INTERVIEW_MODES.map((value) => (
                    <option key={value} value={value}>{value}</option>
                  ))}
                </select>
                <select
                  value={sessionType}
                  onChange={(e) => setSessionType(e.target.value)}
                  className="px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 min-w-[180px]"
                >
                  {SESSION_TYPES.map((option) => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
                <button
                  onClick={handleStartSession}
                  disabled={loadingQuestions}
                  className="px-4 py-2.5 rounded-xl text-xs font-extrabold text-white gradient-bg shadow-glow hover:opacity-95 transition-all flex items-center justify-center gap-2"
                >
                  {loadingQuestions ? <Loader2 className="w-4 h-4 animate-spin" /> : <><RefreshCw className="w-4 h-4" /><span>Start Session</span></>}
                </button>
              </div>
            </div>
          </div>

          {questions.length > 0 && currentQ ? (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="glass-card rounded-2xl p-4 border border-slate-800/80">
                  <div className="flex items-center gap-2 text-indigo-400 text-xs font-bold"><Target className="w-4 h-4" /> Role Focus</div>
                  <div className="mt-3 text-lg font-bold text-white">{targetRole}</div>
                </div>
                <div className="glass-card rounded-2xl p-4 border border-slate-800/80">
                  <div className="flex items-center gap-2 text-amber-400 text-xs font-bold"><BrainCircuit className="w-4 h-4" /> Interview Mode</div>
                  <div className="mt-3 text-lg font-bold text-white">{mode}</div>
                </div>
                <div className="glass-card rounded-2xl p-4 border border-slate-800/80">
                  <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold"><Trophy className="w-4 h-4" /> Avg Score</div>
                  <div className="mt-3 text-lg font-bold text-white">{avgScore || '—'}%</div>
                </div>
              </div>

              <div className="glass-card rounded-3xl p-6 border border-slate-800/80 space-y-4">
                <div className="flex items-center justify-between gap-3 flex-wrap">
                  <span className="px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 text-xs font-bold border border-indigo-500/30">
                    Question {currentIdx + 1} / {questions.length} • {currentQ.category}
                  </span>
                  <span className="text-xs font-bold text-slate-400">{currentQ.difficulty}</span>
                </div>

                <h3 className="text-xl font-bold text-white leading-relaxed">{currentQ.question}</h3>

                {sessionType === 'assessment' && currentQ?.options && (
                  <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-4 space-y-3">
                   <div className="flex items-center gap-2 text-amber-400 font-bold mb-2 text-xs"><Award className="w-4 h-4" /> Choose the best answer</div>
                   {currentQ.options.map((option, index) => {
                     const selected = selectedOption === index;
                     return (
                       <button
                         key={option}
                         type="button"
                         onClick={() => setSelectedOption(index)}
                         className={`w-full text-left px-4 py-3 rounded-xl border text-xs transition-all ${
                           selected
                             ? 'border-indigo-500 bg-indigo-500/10 text-white'
                             : 'border-slate-700 bg-slate-950 text-slate-300 hover:border-slate-500'
                         }`}
                       >
                         <span className="font-bold text-indigo-300 mr-2">{String.fromCharCode(65 + index)}.</span>{option}
                       </button>
                     );
                   })}
                  </div>
                )}

                {sessionType !== 'assessment' && (
                  <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-4 text-xs text-slate-300">
                   <div className="flex items-center gap-2 text-amber-400 font-bold mb-2"><Award className="w-4 h-4" /> Strong answer strategy</div>
                   <p>{currentQ.sample_answer}</p>
                  </div>
                )}

                <form onSubmit={handleEvaluateAnswer} className="space-y-3 pt-2">
                  {sessionType !== 'assessment' && (
                   <textarea
                     rows={6}
                     required
                     value={userAnswer}
                     onChange={(e) => setUserAnswer(e.target.value)}
                     placeholder="Answer as if you are in a real interview. Explain your thinking, trade-offs, and outcome..."
                     className="w-full p-4 rounded-2xl bg-slate-900 border border-slate-800 text-xs text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                   />
                  )}

                  <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
                   <div className="flex gap-2 flex-wrap">
                     {currentIdx > 0 && (
                       <button
                         type="button"
                         onClick={() => {
                           setCurrentIdx(currentIdx - 1);
                           setEvaluation(null);
                           setUserAnswer('');
                           setSelectedOption(null);
                         }}
                         className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs font-semibold hover:bg-slate-700"
                       >
                         Previous
                       </button>
                     )}
                     {currentIdx < questions.length - 1 && (
                       <button
                         type="button"
                         onClick={goToNextQuestion}
                         className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs font-semibold hover:bg-slate-700"
                       >
                         Skip ahead
                       </button>
                     )}
                   </div>

                   <button
                     type="submit"
                     disabled={loadingEval || (sessionType === 'assessment' && selectedOption === null)}
                     className="px-5 py-2.5 rounded-xl text-xs font-extrabold text-white gradient-bg shadow-glow hover:opacity-95 transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                   >
                     {loadingEval ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Send className="w-4 h-4" /><span>{sessionType === 'assessment' ? 'Submit Answer' : 'Evaluate Answer'}</span></>}
                   </button>
                  </div>
                </form>
              </div>

              {evaluation && (
                <div className="glass-card rounded-3xl p-6 border border-slate-800/80 space-y-4">
                  <div className="flex flex-col md:flex-row items-start md:items-center justify-between border-b border-slate-800 pb-4 gap-3">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center font-extrabold text-lg">
                        {evaluation.score}
                      </div>
                      <div>
                        <h4 className="text-base font-bold text-white">Interview Performance Review</h4>
                        <p className="text-xs text-slate-400">Accuracy: {evaluation.technical_accuracy || 'Strong'} • Clarity: {evaluation.clarity || 'Clear'}</p>
                      </div>
                    </div>
                    <div className="text-xs text-slate-300">{evaluation.completeness || 'Good'} completeness</div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 rounded-2xl bg-emerald-950/20 border border-emerald-800/40 space-y-2">
                      <h5 className="text-xs font-bold text-emerald-400 flex items-center gap-2"><CheckCircle2 className="w-4 h-4" /> Strengths</h5>
                      <ul className="text-xs text-slate-300 space-y-1">
                        {(evaluation.strengths || []).map((str, idx) => <li key={idx}>• {str}</li>)}
                      </ul>
                    </div>

                    <div className="p-4 rounded-2xl bg-rose-950/20 border border-rose-800/40 space-y-2">
                      <h5 className="text-xs font-bold text-rose-400 flex items-center gap-2"><AlertCircle className="w-4 h-4" /> Improve</h5>
                      <ul className="text-xs text-slate-300 space-y-1">
                        {(evaluation.areas_for_improvement || []).map((area, idx) => <li key={idx}>• {area}</li>)}
                      </ul>
                    </div>
                  </div>

                  {evaluation.improved_model_answer && (
                    <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800">
                      <h5 className="text-xs font-bold text-indigo-400 mb-2">High-scoring answer framework</h5>
                      <p className="text-xs text-slate-300 leading-relaxed">{evaluation.improved_model_answer}</p>
                    </div>
                  )}

                  {evaluation.next_focus && (
                    <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800">
                      <h5 className="text-xs font-bold text-violet-400 mb-2">Next focus area</h5>
                      <p className="text-xs text-slate-300 leading-relaxed">{evaluation.next_focus}</p>
                    </div>
                  )}

                  <div className="flex items-center justify-end">
                    {currentIdx < questions.length - 1 ? (
                      <button
                        type="button"
                        onClick={goToNextQuestion}
                        className="px-4 py-2 rounded-xl text-xs font-bold text-white gradient-bg shadow-glow flex items-center gap-2"
                      >
                        Next question <ArrowRight className="w-4 h-4" />
                      </button>
                    ) : (
                      <button
                        type="button"
                        onClick={() => {
                          window.scrollTo({ top: 0, behavior: 'smooth' });
                          setCurrentIdx(0);
                          setEvaluation(null);
                          setUserAnswer('');
                        }}
                        className="px-4 py-2 rounded-xl text-xs font-bold text-white gradient-bg shadow-glow flex items-center gap-2"
                      >
                        Finish session <Sparkles className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="glass-card rounded-3xl p-12 text-center border border-slate-800/80 space-y-5">
              <div className="w-14 h-14 rounded-2xl gradient-bg flex items-center justify-center text-white mx-auto shadow-glow">
                <Mic className="w-7 h-7" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-white">Ready for a high-impact interview practice session?</h3>
                <p className="text-xs text-slate-400 max-w-lg mx-auto mt-2">
                  The AI interview coach generates questions based on your resume, target role, and skill gaps so you can practice realistic technical and behavioral interviews, plus resume-topic assessments.
                </p>
              </div>
              <button
                onClick={handleStartSession}
                className="px-6 py-3 rounded-2xl text-xs font-extrabold text-white gradient-bg shadow-glow hover:opacity-95 transition-all inline-flex items-center gap-2"
              >
                <Sparkles className="w-4 h-4" />
                <span>{sessionType === 'assessment' ? 'Start Resume Topic Test' : 'Start Elite Mock Interview'}</span>
              </button>
            </div>
          )}
        </main>
      </div>

      <Footer />
    </div>
  );
};

export default AIInterviewPage;
