import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { CheckCircle2, Loader2, Send, Sparkles, Target } from 'lucide-react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import Footer from '../components/Footer';
import api from '../services/api';

const InterviewSessionPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [question, setQuestion] = useState(null);
  const [answer, setAnswer] = useState('');
  const [evaluation, setEvaluation] = useState(null);
  const [progress, setProgress] = useState(0);
  const [sessionStatus, setSessionStatus] = useState('active');
  const [runResult, setRunResult] = useState(null);
  const [testQuestions, setTestQuestions] = useState([]);
  const [savedAnswers, setSavedAnswers] = useState({});
  const [draftAnswers, setDraftAnswers] = useState({});

  const fetchQuestionOverview = async () => {
    try {
      const res = await api.get(`/interview/${id}/questions`);
      setTestQuestions(res.data.questions || []);
      setSavedAnswers(Object.fromEntries(
        (res.data.questions || [])
          .filter((item) => item.answered)
          .map((item) => [item.question_number, item.answer])
      ));
      setSessionStatus(res.data.status || 'active');
    } catch (error) {
      console.error('Unable to load test questions:', error);
      alert(error?.response?.data?.detail || 'Unable to load the test overview.');
    }
  };

  const fetchQuestion = async (questionNumber) => {
    setLoading(true);
    try {
      const query = questionNumber ? `?question_number=${questionNumber}` : '';
      const res = await api.get(`/interview/${id}/current-question${query}`);
      const payload = res.data;
      if (payload.status === 'completed' && !payload.question) {
        navigate(`/interview/result/${id}`);
        return;
      }
      setQuestion(payload);
      setAnswer(payload.saved_answer ?? draftAnswers[payload.question_number] ?? (payload.question_type === 'coding' ? (payload.starter_code || '') : ''));
      setRunResult(null);
      setEvaluation(null);
      setProgress(payload.progress || 0);
      setSessionStatus(payload.status || 'active');
    } catch (error) {
      console.error('Unable to load test question:', error);
      alert(error?.response?.data?.detail || 'Unable to load this question.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const initialize = async () => {
      await fetchQuestionOverview();
      await fetchQuestion();
    };
    initialize();
  }, [id]);

  const isCodingQuestion = question?.question_type === 'coding' || question?.category === 'Coding' || (question?.topic || '').toLowerCase().includes('coding');
  const sectionGroups = testQuestions.reduce((groups, item) => {
    const section = item.section || 'General';
    if (!groups[section]) groups[section] = [];
    groups[section].push(item);
    return groups;
  }, {});
  const answeredCount = Object.keys(savedAnswers).length;

  const handleDraftChange = (value) => {
    setAnswer(value);
    if (question) {
      setDraftAnswers((current) => ({ ...current, [question.question_number]: value }));
    }
  };

  const saveAnswer = async (questionNumber, answerValue) => {
    const res = await api.post(`/interview/${id}/answer`, {
      answer: answerValue,
      question_number: questionNumber,
    });
    setSavedAnswers((current) => ({ ...current, [questionNumber]: answerValue }));
    setDraftAnswers((current) => {
      const updated = { ...current };
      delete updated[questionNumber];
      return updated;
    });
    setTestQuestions((current) => current.map((item) => (
      item.question_number === questionNumber ? { ...item, answered: true, answer: answerValue } : item
    )));
    setProgress(res.data.progress || 0);
    return res.data;
  };

  const finishTest = async () => {
    const unanswered = testQuestions.length - answeredCount;
    const initialAnswer = question?.saved_answer ?? question?.starter_code ?? '';
    const pendingAnswer = question && answer.trim() && answer !== initialAnswer;
    const unansweredAfterSave = Math.max(0, unanswered - (pendingAnswer && !savedAnswers[question?.question_number] ? 1 : 0));
    const confirmation = unansweredAfterSave
      ? `You have ${unansweredAfterSave} unanswered question${unansweredAfterSave === 1 ? '' : 's'}. Submit the test anyway?`
      : 'Submit your test and view your results?';
    if (!window.confirm(confirmation)) return;

    setLoading(true);
    try {
      if (pendingAnswer) {
        await saveAnswer(question.question_number, answer);
      }
      await api.post(`/interview/${id}/finish`);
      setSessionStatus('completed');
      navigate(`/interview/result/${id}`);
    } catch (error) {
      console.error('Unable to submit test:', error);
      alert(error?.response?.data?.detail || 'Unable to submit the test. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRunCode = async () => {
    if (!isCodingQuestion || !answer || !answer.trim()) {
      alert('Write code before running it.');
      return;
    }
    setLoading(true);
    try {
      const res = await api.post(`/interview/${id}/run-code`, {
        question_number: question?.question_number || 1,
        code: answer,
      });
      setRunResult(res.data);
    } catch (error) {
      console.error(error);
      alert(error?.response?.data?.detail || 'Unable to run this coding challenge.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    const selectedAnswer = question?.options?.length ? answer : answer.trim();
    if (!selectedAnswer || (question?.options?.length && !selectedAnswer)) return;
    setLoading(true);
    try {
      const res = await saveAnswer(question?.question_number || 1, selectedAnswer);
      setEvaluation(res.evaluation);
      if (res.status === 'completed') {
        await api.post(`/interview/${id}/finish`);
        setTimeout(() => navigate(`/interview/result/${id}`), 500);
      } else if (res.next_question && res.next_question.question) {
        await fetchQuestion(res.next_question.question_number);
      } else {
        await api.post(`/interview/${id}/finish`);
        setTimeout(() => navigate(`/interview/result/${id}`), 500);
      }
    } catch (error) {
      console.error(error);
      alert(error?.response?.data?.detail || 'Unable to submit answer. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading && !question) {
    return <div className="min-h-screen flex items-center justify-center bg-slate-950 text-white"><Loader2 className="w-8 h-8 animate-spin" /></div>;
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <Navbar />
      <div className="flex max-w-7xl mx-auto">
        <Sidebar />
        <main className="flex-1 p-6 md:p-8">
          <div className="glass-card rounded-3xl p-6 border border-slate-800 bg-gradient-to-r from-slate-900 via-violet-950/40 to-slate-900">
            <div className="flex items-center justify-between gap-3 flex-wrap">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-violet-400 font-bold">AI Practice Test</p>
                <h1 className="text-2xl font-extrabold text-white">Adaptive Practice Test Session</h1>
              </div>
              <div className="flex items-center gap-3">
                <div className="text-xs text-slate-300">Question {question?.question_number || 1} of {question?.total_questions || 10}</div>
                <button
                  onClick={finishTest}
                  disabled={loading || sessionStatus === 'completed'}
                  className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-extrabold text-xs flex items-center gap-2 disabled:opacity-50"
                >
                  <Send className="w-4 h-4" /> Submit Test
                </button>
              </div>
            </div>

            <section className="mt-6 rounded-2xl border border-slate-800 bg-slate-900/80 p-5" aria-label="Test question navigator">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h2 className="text-sm font-extrabold text-white">Test Overview</h2>
                  <p className="mt-1 text-xs text-slate-400">{answeredCount} of {testQuestions.length} questions answered</p>
                </div>
                <div className="flex flex-wrap gap-3 text-[11px] text-slate-300">
                  <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-emerald-500" /> Answered</span>
                  <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-amber-500" /> Draft</span>
                  <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-indigo-500" /> Current</span>
                  <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-slate-700" /> Not answered</span>
                </div>
              </div>
              <div className="mt-4 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
                {Object.entries(sectionGroups).map(([section, items], sectionIndex) => {
                  const sectionAnswered = items.filter((item) => savedAnswers[item.question_number] !== undefined).length;
                  return (
                    <div key={section} className="rounded-xl border border-slate-800 bg-slate-950/70 p-3">
                      <div className="flex items-center justify-between gap-2 mb-3">
                        <h3 className="text-xs font-extrabold text-white">
                          Section {sectionIndex + 1}: {section.replace(/-/g, ' ').replace(/\b\w/g, (letter) => letter.toUpperCase())}
                        </h3>
                        <span className="text-[10px] text-slate-400">{items.length} questions · {sectionAnswered}/{items.length} answered</span>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {items.map((item) => {
                          const isCurrent = question?.question_number === item.question_number;
                          const isAnswered = savedAnswers[item.question_number] !== undefined;
                          const draft = draftAnswers[item.question_number];
                          const isDraft = draft !== undefined && draft.trim() !== '' && draft !== savedAnswers[item.question_number];
                          const color = isCurrent
                            ? 'border-indigo-300 bg-indigo-600 text-white ring-2 ring-indigo-400/40'
                            : isDraft
                              ? 'border-amber-400 bg-amber-500 text-slate-950'
                              : isAnswered
                                ? 'border-emerald-400 bg-emerald-600 text-white'
                                : 'border-slate-700 bg-slate-800 text-slate-300 hover:border-slate-500';
                          return (
                            <button
                              key={item.question_number}
                              type="button"
                              onClick={() => fetchQuestion(item.question_number)}
                              disabled={loading}
                              aria-label={`Go to question ${item.question_number}${isAnswered ? ', answered' : isDraft ? ', draft' : ', unanswered'}`}
                              aria-current={isCurrent ? 'step' : undefined}
                              className={`w-9 h-9 rounded-lg border text-xs font-extrabold transition-colors disabled:opacity-60 ${color}`}
                            >
                              {item.question_number}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>
            </section>

            <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900/80 p-5">
              <div className="flex flex-wrap gap-3 text-xs text-slate-300">
                <span className="px-2 py-1 rounded-full bg-indigo-950">Section: <span className="text-white font-bold">{question?.section || question?.category || 'General'}</span></span>
                <span className="px-2 py-1 rounded-full bg-slate-800">Category: <span className="text-white font-bold">{question?.category || 'General'}</span></span>
                <span className="px-2 py-1 rounded-full bg-slate-800">Difficulty: <span className="text-white font-bold">{question?.difficulty || 'Intermediate'}</span></span>
                <span className="px-2 py-1 rounded-full bg-slate-800">Topic: <span className="text-white font-bold">{question?.topic || 'General'}</span></span>
              </div>

              <div className="mt-6 text-xl md:text-2xl font-bold leading-relaxed text-white">{question?.question}</div>

              {isCodingQuestion && (
                <div className="mt-4 rounded-2xl border border-indigo-500/30 bg-indigo-500/5 p-4 text-xs text-indigo-200">
                  <div className="font-bold uppercase tracking-[0.18em] text-indigo-300">Coding Section</div>
                  <div className="mt-2">Language: <span className="font-bold text-white">{question?.language || 'Python'}</span></div>
                  <div className="mt-1 text-slate-300">Run your code locally to validate it against the listed test cases before final submission.</div>
                </div>
              )}

              {isCodingQuestion && (
                <>
                  {question?.explanation && (
                    <div className="mt-4 rounded-2xl border border-violet-500/30 bg-violet-500/5 p-4">
                      <div className="text-xs font-bold uppercase tracking-[0.18em] text-violet-300 mb-2">Question Explanation</div>
                      <p className="text-sm leading-relaxed text-slate-200">{question.explanation}</p>
                    </div>
                  )}
                  <div className="mt-4 rounded-2xl border border-slate-700 bg-slate-950/60 p-4">
                    <div className="text-xs font-bold uppercase tracking-[0.18em] text-slate-300 mb-3">Sample Test Cases</div>
                    {question?.test_cases?.length > 0 ? (
                      <div className="space-y-3">
                        {question.test_cases.map((testCase, idx) => (
                          <div key={idx} className="rounded-xl border border-slate-700 bg-slate-900 p-3 text-xs text-slate-300">
                            <div className="font-bold text-white mb-2">Case {idx + 1}</div>
                            <div><span className="text-slate-400">Function arguments:</span> <span className="font-mono text-slate-200">{JSON.stringify(testCase.args)}</span></div>
                            <div className="mt-1"><span className="text-slate-400">Expected result:</span> <span className="font-mono text-emerald-300">{JSON.stringify(testCase.expected)}</span></div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-xs text-slate-400">No sample test cases are available for this question.</p>
                    )}
                  </div>
                </>
              )}

              <div className="mt-6">
                <label className="block text-xs font-bold text-slate-300 mb-2">{isCodingQuestion ? 'Your Code' : 'Your Answer'}</label>
                {question?.options?.length ? (
                  <div className="space-y-3">
                    {question.options.map((option, idx) => (
                      <label key={idx} className="flex items-start gap-3 p-3 rounded-2xl border border-slate-700 bg-slate-950 text-sm text-slate-200 cursor-pointer hover:border-indigo-500/50">
                        <input
                          type="radio"
                          name="practice-option"
                          value={String.fromCharCode(65 + idx)}
                          checked={answer === String.fromCharCode(65 + idx)}
                          onChange={(e) => handleDraftChange(e.target.value)}
                          className="mt-1 h-4 w-4 accent-indigo-500"
                        />
                        <span><span className="font-bold text-white">{String.fromCharCode(65 + idx)}.</span> {option}</span>
                      </label>
                    ))}
                  </div>
                ) : (
                  <textarea
                    value={answer}
                    onChange={(e) => handleDraftChange(e.target.value)}
                    rows={isCodingQuestion ? 16 : 8}
                    spellCheck={false}
                    className="w-full px-4 py-3 rounded-2xl bg-slate-950 border border-slate-700 text-white text-sm font-mono"
                    placeholder={isCodingQuestion ? (question?.starter_code || 'Write your solution here...') : 'Provide a clear, structured answer to the practice question...'}
                  />
                )}
              </div>

              <div className="mt-6 flex items-center justify-between gap-3">
                <div className="text-xs text-slate-400">Progress</div>
                <div className="text-xs text-slate-300">{Math.round(progress)}%</div>
              </div>
              <div className="mt-2 h-2 rounded-full bg-slate-800 overflow-hidden">
                <div className="h-full rounded-full bg-gradient-to-r from-indigo-500 via-violet-500 to-emerald-400" style={{ width: `${Math.min(100, progress)}%` }} />
              </div>

              <div className="mt-6 flex flex-wrap justify-end gap-3">
                {isCodingQuestion && (
                  <button onClick={handleRunCode} disabled={loading || !answer || !answer.trim()} className="px-5 py-3 rounded-2xl border border-emerald-500/40 bg-emerald-500/10 text-emerald-300 font-extrabold text-xs shadow-glow disabled:opacity-50 flex items-center gap-2">
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Target className="w-4 h-4" /> Run Code</>}
                  </button>
                )}
                <button onClick={handleSubmit} disabled={loading || !answer || (question?.options?.length ? !answer : !answer.trim())} className="px-5 py-3 rounded-2xl bg-gradient-to-r from-indigo-600 to-violet-600 text-white font-extrabold text-xs shadow-glow disabled:opacity-50 flex items-center gap-2">
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Sparkles className="w-4 h-4" /> Submit Answer</>}
                </button>
              </div>
            </div>

            {runResult && (
              <div className="mt-6 rounded-2xl border border-emerald-500/30 bg-emerald-500/5 p-5">
                <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm"><CheckCircle2 className="w-4 h-4" /> Code Run Result</div>
                <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-slate-200">
                  <div><span className="text-slate-400">Status:</span> <span className="font-extrabold text-white">{runResult.passed ? 'Passed' : 'Failed'}</span></div>
                  <div><span className="text-slate-400">Test Cases:</span> <span className="font-extrabold text-white">{runResult.passed_cases || 0}/{runResult.total_cases || 0}</span></div>
                  <div><span className="text-slate-400">Score:</span> <span className="font-extrabold text-white">{runResult.score || 0}/10</span></div>
                </div>
                <div className="mt-4 text-xs text-slate-300 leading-relaxed whitespace-pre-wrap"><span className="font-bold text-white">Feedback:</span> {runResult.feedback}</div>
                {runResult.output && (
                  <div className="mt-4 rounded-xl border border-slate-700 bg-slate-950 p-3 text-xs text-slate-200 whitespace-pre-wrap font-mono">
                    {runResult.output}
                  </div>
                )}
              </div>
            )}

            {evaluation && (
              <div className="mt-6 rounded-2xl border border-emerald-500/30 bg-emerald-500/5 p-5">
                <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm"><CheckCircle2 className="w-4 h-4" /> Evaluation</div>
                <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-slate-200">
                  <div><span className="text-slate-400">Score:</span> <span className="font-extrabold text-white">{evaluation.score}/{evaluation.max_score || 10}</span></div>
                  <div><span className="text-slate-400">Technical correctness:</span> <span className="font-bold text-white">{evaluation.technical_correctness}</span></div>
                  <div><span className="text-slate-400">Completeness:</span> <span className="font-bold text-white">{evaluation.completeness}</span></div>
                  <div><span className="text-slate-400">Clarity:</span> <span className="font-bold text-white">{evaluation.clarity}</span></div>
                </div>
                <div className="mt-4 text-xs text-slate-300 leading-relaxed"><span className="font-bold text-white">Feedback:</span> {evaluation.feedback}</div>
                <div className="mt-3 text-xs text-slate-300"><span className="font-bold text-white">Strengths:</span> {Array.isArray(evaluation.strengths) ? evaluation.strengths.join(', ') : evaluation.strengths}</div>
                <div className="mt-3 text-xs text-slate-300"><span className="font-bold text-white">Missing points:</span> {Array.isArray(evaluation.missing_points) ? evaluation.missing_points.join(', ') : evaluation.missing_points}</div>
              </div>
            )}
          </div>
        </main>
      </div>
      <Footer />
    </div>
  );
};

export default InterviewSessionPage;
