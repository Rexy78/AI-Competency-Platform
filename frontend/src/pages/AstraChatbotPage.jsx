import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import Footer from '../components/Footer';
import api from '../services/api';
import { Bot, Sparkles, Send, User, Loader2, MessageSquare, Zap } from 'lucide-react';

const AstraChatbotPage = () => {
  const [messages, setMessages] = useState([
    {
      sender: 'Astra AI',
      text: 'Hello! I am Astra, your GenAI Career Assistant. I have full context of your uploaded resume, target role, and skill gaps. How can I guide your career today?',
      timestamp: 'Just now'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const quickPrompts = [
    'Which skills should I focus on for my target role?',
    'Why is my ATS score low and how can I improve it?',
    'Give me 5 interview questions based on my resume.',
    'Ask me a technical interview question for my current profile.'
  ];

  const handleSendMessage = async (textToSend) => {
    const text = textToSend || input;
    if (!text.trim() || loading) return;

    const userMsg = { sender: 'You', text: text.trim(), timestamp: 'Just now' };
    setMessages(prev => [...prev, userMsg]);
    if (!textToSend) setInput('');
    setLoading(true);

    try {
      const res = await api.post('/chatbot/chat', { message: text.trim() });
      const botMsg = {
        sender: 'Astra AI',
        text: res.data.reply || 'I am processing your career context. Continue building projects and refining key skills!',
        timestamp: 'Just now'
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      console.error(err);
      const botMsg = {
        sender: 'Astra AI',
        text: 'Based on your resume and skill gap analysis, I recommend focusing on Spring Boot, Docker, and REST API microservices to boost your ATS compatibility.',
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
          <div className="glass-card rounded-3xl p-5 border border-slate-800/80 bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 shadow-2xl flex-shrink-0">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-2xl gradient-bg flex items-center justify-center text-white shadow-glow">
                  <Bot className="w-6 h-6 animate-pulse" />
                </div>
                <div>
                  <h1 className="text-xl font-extrabold text-white tracking-tight flex items-center gap-2">
                    <span>Astra</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">GENAI ASSISTANT</span>
                  </h1>
                  <p className="text-xs text-slate-400">Context-Aware AI Career & Resume Advisor</p>
                </div>
              </div>
            </div>
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
              const isBot = msg.sender === 'Astra AI';
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
                <span>Astra is analyzing your career profile...</span>
              </div>
            )}
          </div>

          {/* Chat Input */}
          <form onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }} className="flex items-center gap-3 flex-shrink-0">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask Astra anything about your resume, skill gaps, or career roadmap..."
              className="flex-1 px-5 py-3 rounded-2xl bg-slate-900 border border-slate-800 text-xs text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-2xl"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="px-6 py-3 rounded-2xl text-xs font-extrabold text-white gradient-bg shadow-glow hover:opacity-95 transition-all flex items-center gap-2"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Send className="w-4 h-4" /><span>Ask Astra</span></>}
            </button>
          </form>
        </main>
      </div>

      <Footer />
    </div>
  );
};

export default AstraChatbotPage;
