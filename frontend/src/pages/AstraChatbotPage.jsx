import React, { useEffect, useState } from 'react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import Footer from '../components/Footer';
import api from '../services/api';
import { Bot, Send, User, Loader2, Zap } from 'lucide-react';

const AstraChatbotPage = () => {
  const [messages, setMessages] = useState([
    {
      sender: 'AI Chatbot',
      text: 'Hello! I can compare skills detected in your latest analyzed resume with a target role and suggest next steps. Choose a target role below, then ask me to identify your skill gaps.',
      timestamp: 'Just now'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [targetRole, setTargetRole] = useState('Java Backend Developer');
  const [targetRoles, setTargetRoles] = useState([]);
  const [roleError, setRoleError] = useState('');

  useEffect(() => {
    let active = true;

    const loadTargetRoles = async () => {
      try {
        const rolesResponse = await api.get('/chatbot/roles');
        const roles = rolesResponse.data;
        if (!Array.isArray(roles) || roles.length === 0) {
          throw new Error('The chatbot did not return any target roles.');
        }
        if (!active) return;

        setTargetRoles(roles);
        if (!roles.includes(targetRole)) {
          setTargetRole(roles[0]);
        }

        try {
          const latestResponse = await api.get('/resume/latest');
          const savedRole = latestResponse.data?.target_role;
          if (active && roles.includes(savedRole)) {
            setTargetRole(savedRole);
          }
        } catch (error) {
          console.warn('Could not load the latest analyzed target role:', error);
        }
      } catch (error) {
        console.error('Could not load chatbot target roles:', error);
        if (active) {
          setRoleError('Target roles could not be loaded. Refresh the page to retry.');
        }
      }
    };

    loadTargetRoles();
    return () => {
      active = false;
    };
  }, []);

  const quickPrompts = [
    'Which skills should I focus on for my target role?',
    'How can I tailor my resume to a job description?',
    'Give me 5 interview questions based on my resume.',
    'Explain REST APIs for my target role.'
  ];

  const handleSendMessage = async (textToSend) => {
    const text = textToSend || input;
    if (!text.trim() || loading) return;

    const userMsg = { sender: 'You', text: text.trim(), timestamp: 'Just now' };
    setMessages(prev => [...prev, userMsg]);
    if (!textToSend) setInput('');
    setLoading(true);

    try {
      const history = messages.slice(-10).map((message) => ({
        role: message.sender === 'You' ? 'user' : 'assistant',
        content: message.text.slice(-2000),
      }));
      const res = await api.post('/chatbot/chat', {
        message: text.trim(),
        target_role: targetRole,
        history,
      });
      const botMsg = {
        sender: 'AI Chatbot',
        text: res.data.reply || 'The assistant returned an empty response. Please try asking in a different way.',
        timestamp: 'Just now'
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      console.error(err);
      const botMsg = {
        sender: 'AI Chatbot',
        text: 'I could not reach the chatbot service. Please check your connection and try again.',
        timestamp: 'Just now'
      };
      setMessages(prev => [...prev, botMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between selection:bg-indigo-500 selection:text-white">
      <Navbar />

      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        <Sidebar />

        <main className="flex-1 p-6 md:p-8 space-y-6 flex flex-col h-[calc(100vh-80px)] overflow-hidden">
          {/* Header */}
          <div className="chatbot-header glass-card rounded-3xl p-5 border border-slate-800/80 bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 shadow-2xl flex-shrink-0">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-2xl gradient-bg flex items-center justify-center text-white shadow-glow">
                  <Bot className="w-6 h-6 animate-pulse" />
                </div>
                <div>
                  <h1 className="text-xl font-extrabold text-white tracking-tight flex items-center gap-2">
                    <span>AI Chatbot</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">CAREER ASSISTANT</span>
                  </h1>
                  <p className="text-xs text-slate-400">Context-Aware AI Career & Resume Advisor</p>
                </div>
              </div>
            </div>
          </div>

          <div className="glass-card rounded-2xl p-4 border border-slate-800/80 flex flex-col sm:flex-row sm:items-center gap-3 flex-shrink-0">
            <div className="flex-1">
              <label htmlFor="chatbot-target-role" className="block text-xs font-bold text-slate-200 mb-1">
                Analyze skill gaps for
              </label>
              <p className="text-[11px] text-slate-400">
                Results use your latest analyzed resume and this role's requirements.
              </p>
            </div>
            <select
              id="chatbot-target-role"
              value={targetRole}
              onChange={(event) => setTargetRole(event.target.value)}
              disabled={targetRoles.length === 0}
              className="w-full sm:w-72 px-3 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-60"
            >
              {targetRoles.map((role) => <option key={role} value={role}>{role}</option>)}
            </select>
            {roleError && <p role="alert" className="text-xs text-rose-400">{roleError}</p>}
          </div>

          {/* Quick Suggestions */}
          <div className="flex items-center gap-2 overflow-x-auto pb-1 flex-shrink-0 custom-scrollbar">
            <span className="text-[11px] font-bold text-slate-400 whitespace-nowrap flex items-center gap-1">
              <Zap className="w-3.5 h-3.5 text-amber-400" /> Suggestions:
            </span>
            {quickPrompts.map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => handleSendMessage(prompt)}
                className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 text-xs font-semibold hover:border-indigo-500 hover:text-white whitespace-nowrap transition-all"
              >
                {prompt}
              </button>
            ))}
          </div>

          {/* Chat Conversation Scroll Area */}
          <div className="flex-1 glass-card rounded-3xl p-6 border border-slate-800/80 overflow-y-auto space-y-4 custom-scrollbar">
            {messages.map((msg, idx) => {
              const isBot = msg.sender === 'AI Chatbot';
              return (
                <div key={idx} className={`flex items-start gap-3 ${isBot ? '' : 'flex-row-reverse'}`}>
                  <div className={`w-8 h-8 rounded-xl flex items-center justify-center text-white text-xs font-bold flex-shrink-0 ${
                    isBot ? 'gradient-bg shadow-glow' : 'bg-slate-800 border border-slate-700'
                  }`}>
                    {isBot ? <Bot className="w-4 h-4" /> : <User className="w-4 h-4" />}
                  </div>

                  <div className={`max-w-xl p-4 rounded-2xl text-xs leading-relaxed space-y-1 ${
                    isBot
                      ? 'bg-slate-900/90 border border-slate-800 text-slate-200'
                      : 'bg-indigo-600 text-white shadow-glow'
                  }`}>
                    <div className="flex items-center justify-between text-[10px] opacity-75 font-semibold">
                      <span>{msg.sender}</span>
                      <span>{msg.timestamp}</span>
                    </div>
                    <p className="whitespace-pre-line">{msg.text}</p>
                  </div>
                </div>
              );
            })}
            {loading && (
              <div className="flex items-center gap-2 text-xs text-indigo-400 p-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>AI Chatbot is analyzing your career profile...</span>
              </div>
            )}
          </div>

          {/* Chat Input */}
          <form onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }} className="flex items-center gap-3 flex-shrink-0">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask the AI chatbot about your resume, skill gaps, or career roadmap..."
              className="flex-1 px-5 py-3 rounded-2xl bg-slate-900 border border-slate-800 text-xs text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-2xl"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="px-6 py-3 rounded-2xl text-xs font-extrabold text-white gradient-bg shadow-glow hover:opacity-95 transition-all flex items-center gap-2"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Send className="w-4 h-4" /><span>Send</span></>}
            </button>
          </form>
        </main>
      </div>

      <Footer />
    </div>
  );
};

export default AstraChatbotPage;
