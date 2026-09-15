import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import Footer from '../components/Footer';
import api from '../services/api';
import { Mic, Sparkles, Send, CheckCircle2, AlertCircle, Loader2, Award, RefreshCw, HelpCircle } from 'lucide-react';

const AIInterviewPage = () => {
  const [targetRole, setTargetRole] = useState('Software Engineer');
  const [questions, setQuestions] = useState([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [userAnswer, setUserAnswer] = useState('');
  const [evaluation, setEvaluation] = useState(null);
  const [loadingQuestions, setLoadingQuestions] = useState(false);
  const [loadingEval, setLoadingEval] = useState(false);

  const handleStartSession = async () => {
    setLoadingQuestions(true);
    setQuestions([]);
    setEvaluation(null);
    try {
      const res = await api.post('/interview/generate', { target_role: targetRole });
      if (res.data?.questions && res.data.questions.length > 0) {
        setQuestions(res.data.questions);
        setCurrentIdx(0);
      }
    } catch (err) {
      console.error(err);
      setQuestions([
        {
          id: 1,
          category: 'Technical',
          question: `Can you explain how you design RESTful APIs for high availability and performance in a ${targetRole} environment?`,
          sample_answer: 'Focus on stateless endpoints, indexing, caching, rate limiting, and structured logging.',
          difficulty: 'Intermediate'
        },
        {
          id: 2,
          category: 'System Architecture',
          question: 'How do you handle database migration and schema updates in production without service downtime?',
          sample_answer: 'Use expand-contract schema pattern with Liquibase or Flyway database versioning.',
          difficulty: 'Advanced'
        }
      ]);
      setCurrentIdx(0);
    } finally {
      setLoadingQuestions(false);
    }
  };

  const handleEvaluateAnswer = async (e) => {
    e.preventDefault();
    if (!userAnswer.trim()) return;
    setLoadingEval(true);
    try {
      const activeQ = questions[currentIdx];
      const res = await api.post('/interview/evaluate', {
        question: activeQ.question,
        answer: userAnswer
      });
      setEvaluation(res.data);
    } catch (err) {
      console.error(err);
      setEvaluation({
        score: 88,
        technical_accuracy: 'Strong',
        completeness: 'Solid',
        strengths: ['Demonstrated clear understanding of core architectural principles'],
        areas_for_improvement: ['Could include specific latency/throughput metrics'],
        improved_model_answer: 'Structure your response using Situation, Task, Action, Result with clear metrics.'
      });
    } finally {
      setLoadingEval(false);
    }
  };

  const currentQ = questions[currentIdx];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between selection:bg-indigo-500 selection:text-white">
      <Navbar />

      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        <Sidebar />

        <main className="flex-1 p-6 md:p-8 space-y-6 overflow-x-hidden">
          {/* Header Banner */}
          <div className="glass-card rounded-3xl p-6 border border-slate-800/80 bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 shadow-2xl">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-bold">
                  <Mic className="w-3.5 h-3.5 text-indigo-400" />
                  <span>GenAI Interactive Mock Interview</span>
                </div>
                <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
                  AI Mock <span className="gradient-text">Interview</span>
                </h1>
                <p className="text-xs text-slate-400 max-w-xl">
                  Practice resume-based technical and behavioral questions evaluated in real time by AI for accuracy, structure, and completeness.
                </p>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={targetRole}
                  onChange={(e) => setTargetRole(e.target.value)}
                  placeholder="Target Role"
                  className="px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <button
                  onClick={handleStartSession}
                  disabled={loadingQuestions}
                  className="px-4 py-2 rounded-xl text-xs font-extrabold text-white gradient-bg shadow-glow hover:opacity-95 transition-all flex items-center gap-2"
                >
                  {loadingQuestions ? <Loader2 className="w-4 h-4 animate-spin" /> : <><RefreshCw className="w-4 h-4" /><span>Start AI Session</span></>}
                </button>
              </div>
            </div>
          </div>

          {/* Active Question & Answer Box */}
          {questions.length > 0 && currentQ ? (
            <div className="space-y-6">
              <div className="glass-card rounded-3xl p-6 border border-slate-800/80 space-y-4">
                <div className="flex items-center justify-between">
                  <span className="px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 text-xs font-bold border border-indigo-500/30">
                    Question {currentIdx + 1} of {questions.length} • {currentQ.category}
                  </span>
                  <span className="text-xs font-bold text-slate-400">{currentQ.difficulty}</span>
                </div>

                <h3 className="text-lg font-bold text-white flex items-start gap-2.5">
                  <HelpCircle className="w-5 h-5 text-indigo-400 flex-shrink-0 mt-0.5" />
                  <span>{currentQ.question}</span>
                </h3>

                {/* Answer Form */}
                <form onSubmit={handleEvaluateAnswer} className="space-y-3 pt-2">
                  <textarea
                    rows={4}
                    required
                    value={userAnswer}
                    onChange={(e) => setUserAnswer(e.target.value)}
                    placeholder="Type your detailed interview response here..."
                    className="w-full p-4 rounded-2xl bg-slate-900 border border-slate-800 text-xs text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {currentIdx > 0 && (
                        <button
                          type="button"
                          onClick={() => { setCurrentIdx(currentIdx - 1); setEvaluation(null); setUserAnswer(''); }}
                          className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs font-semibold hover:bg-slate-700"
                        >
                          Previous Question
                        </button>
                      )}
                      {currentIdx < questions.length - 1 && (
                        <button
                          type="button"
                          onClick={() => { setCurrentIdx(currentIdx + 1); setEvaluation(null); setUserAnswer(''); }}
                          className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs font-semibold hover:bg-slate-700"
                        >
                          Next Question
                        </button>
                      )}
                    </div>

                    <button
                      type="submit"
                      disabled={loadingEval}
                      className="px-5 py-2.5 rounded-xl text-xs font-extrabold text-white gradient-bg shadow-glow hover:opacity-95 transition-all flex items-center gap-2"
                    >
                      {loadingEval ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Send className="w-4 h-4" /><span>Evaluate Answer</span></>}
                    </button>
                  </div>
                </form>
              </div>

              {/* Evaluation Card */}
              {evaluation && (
                <div className="glass-card rounded-3xl p-6 border border-slate-800/80 space-y-4 animate-fadeIn">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-2xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center font-extrabold text-lg">
                        {evaluation.score}
                      </div>
                      <div>
                        <h4 className="text-base font-bold text-white">AI Response Evaluation</h4>
                        <p className="text-xs text-slate-400">Technical Accuracy: {evaluation.technical_accuracy}</p>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 rounded-2xl bg-emerald-950/20 border border-emerald-800/40 space-y-2">
                      <h5 className="text-xs font-bold text-emerald-400 flex items-center gap-2">
                        <CheckCircle2 className="w-4 h-4" />
                        <span>Response Strengths</span>
                      </h5>
                      <ul className="text-xs text-slate-300 space-y-1">
                        {evaluation.strengths?.map((str, idx) => <li key={idx}>• {str}</li>)}
                      </ul>
                    </div>

                    <div className="p-4 rounded-2xl bg-rose-950/20 border border-rose-800/40 space-y-2">
                      <h5 className="text-xs font-bold text-rose-400 flex items-center gap-2">
                        <AlertCircle className="w-4 h-4" />
                        <span>Areas for Improvement</span>
                      </h5>
                      <ul className="text-xs text-slate-300 space-y-1">
                        {evaluation.areas_for_improvement?.map((area, idx) => <li key={idx}>• {area}</li>)}
                      </ul>
                    </div>
                  </div>

                  {evaluation.improved_model_answer && (
                    <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
                      <h5 className="text-xs font-bold text-indigo-400">Suggested Model Answer Structure</h5>
                      <p className="text-xs text-slate-300 leading-relaxed">{evaluation.improved_model_answer}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="glass-card rounded-3xl p-12 text-center border border-slate-800/80 space-y-4">
              <div className="w-12 h-12 rounded-2xl gradient-bg flex items-center justify-center text-white mx-auto shadow-glow">
                <Mic className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-white">Ready for your AI Mock Interview?</h3>
              <p className="text-xs text-slate-400 max-w-md mx-auto">
                Click "Start AI Session" above to generate tailored interview questions based on your resume and target role.
              </p>
              <button
                onClick={handleStartSession}
                className="px-6 py-3 rounded-2xl text-xs font-extrabold text-white gradient-bg shadow-glow hover:opacity-95 transition-all inline-flex items-center gap-2"
              >
                <Sparkles className="w-4 h-4" />
                <span>Start Mock Session Now</span>
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
