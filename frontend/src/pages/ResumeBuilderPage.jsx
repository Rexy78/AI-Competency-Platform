import React, { useEffect, useState } from 'react';
import SidebarLayout from '../components/SidebarLayout';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import html2pdf from 'html2pdf.js';
import { 
  FileCode, Download, Sparkles, User, FileText, Eye, RefreshCw, Plus, Trash2, Edit3, 
  Briefcase, GraduationCap, Code2, Layout, Printer, CheckCircle2, ClipboardPaste, X, FileCheck,
  Award, ShieldCheck, Palette, Zap, AlertCircle
} from 'lucide-react';

const ResumeBuilderPage = () => {
  const { user } = useAuth();
  const [template, setTemplate] = useState('overleaf'); // 'overleaf', 'canva', 'executive', 'ats', 'original'
  const [accentColor, setAccentColor] = useState('#4f46e5'); // default Indigo
  const [loadingLatest, setLoadingLatest] = useState(true);
  const [resumeFilename, setResumeFilename] = useState('');
  const [showPasteModal, setShowPasteModal] = useState(false);
  const [pastedText, setPastedText] = useState('');
  const [aiRewritingIndex, setAiRewritingIndex] = useState(null);

  const [formData, setFormData] = useState({
    personalInfo: {
      name: '',
      title: '',
      email: '',
      phone: '',
      location: '',
      linkedin: '',
      github: ''
    },
    summary: '',
    skills: [],
    experience: [],
    education: [],
    projects: [],
    certifications: [],
    achievements: [],
    rawText: ''
  });

  const parseTextIntoFormData = (text, nameFromDoc = '', filename = '') => {
    if (!text || !text.trim()) return;

    const emailMatch = text.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/);
    const phoneMatch = text.match(/\(?\+?[0-9]{1,4}\)?[-. ]?\(?[0-9]{2,4}\)?[-. ]?[0-9]{3,4}[-. ]?[0-9]{3,4}/);
    const linkedinMatch = text.match(/linkedin\.com\/in\/[a-zA-Z0-9_-]+/i);
    const githubMatch = text.match(/github\.com\/[a-zA-Z0-9_-]+/i);

    const lines = text.split('\n').map(l => l.trim()).filter(Boolean);

    let extractedName = nameFromDoc || '';
    if (!extractedName) {
      if (lines.length > 0) {
        for (let l of lines.slice(0, 5)) {
          if (!l.includes('@') && !l.match(/\d{5,}/) && l.length < 40) {
            if (!/resume|curriculum|page|profile|summary/i.test(l)) {
              extractedName = l;
              break;
            }
          }
        }
      }
    }
    if (!extractedName) extractedName = user?.full_name || '';

    let extractedTitle = '';
    for (let l of lines.slice(1, 8)) {
      if (/(engineer|developer|architect|analyst|manager|specialist|consultant|intern|student)/i.test(l)) {
        extractedTitle = l;
        break;
      }
    }

    const expItems = [];
    const eduItems = [];
    const projItems = [];
    const certItems = [];
    const skillList = new Set();

    let currentSec = 'summary';
    let summaryLines = [];

    for (let line of lines) {
      const lower = line.toLowerCase();
      if (/(experience|employment|work history|professional experience)/i.test(lower)) {
        currentSec = 'exp';
        continue;
      } else if (/(education|academic|qualification|academic background)/i.test(lower)) {
        currentSec = 'edu';
        continue;
      } else if (/(projects|portfolio|key projects)/i.test(lower)) {
        currentSec = 'proj';
        continue;
      } else if (/(certifications|certificates|licenses)/i.test(lower)) {
        currentSec = 'cert';
        continue;
      } else if (/(skills|technologies|tools|technical skills)/i.test(lower)) {
        currentSec = 'skills';
        continue;
      } else if (/(summary|profile|about|career objective)/i.test(lower)) {
        currentSec = 'summary';
        continue;
      }

      if (currentSec === 'summary' && summaryLines.length < 6) {
        summaryLines.push(line);
      } else if (currentSec === 'exp') {
        expItems.push(line);
      } else if (currentSec === 'edu') {
        eduItems.push(line);
      } else if (currentSec === 'proj') {
        projItems.push(line);
      } else if (currentSec === 'cert') {
        certItems.push(line);
      } else if (currentSec === 'skills') {
        line.split(/[,•|]/).forEach(s => {
          if (s.trim().length > 1 && s.trim().length < 35) skillList.add(s.trim());
        });
      }
    }

    const formattedExp = expItems.map((line, idx) => ({
      id: idx + 1,
      title: line,
      company: '',
      duration: '',
      description: line
    }));

    const formattedEdu = eduItems.map((line, idx) => ({
      id: idx + 1,
      degree: line,
      institution: '',
      year: ''
    }));

    const formattedProj = projItems.map((line, idx) => ({
      id: idx + 1,
      title: line,
      tech: '',
      description: line
    }));

    const formattedCert = certItems.map((line, idx) => ({
      id: idx + 1,
      name: line,
      issuer: '',
      year: ''
    }));

    setFormData({
      personalInfo: {
        name: extractedName,
        title: extractedTitle,
        email: emailMatch ? emailMatch[0] : (user?.email || ''),
        phone: phoneMatch ? phoneMatch[0] : '',
        location: '',
        linkedin: linkedinMatch ? linkedinMatch[0] : '',
        github: githubMatch ? githubMatch[0] : ''
      },
      summary: summaryLines.join(' '),
      skills: Array.from(skillList),
      experience: formattedExp,
      education: formattedEdu,
      projects: formattedProj,
      certifications: formattedCert,
      achievements: [],
      rawText: text
    });

    if (filename) setResumeFilename(filename);
  };

  const parseAndSetResumeData = (parsed, rawFilename = '') => {
    if (!parsed) return;

    if (parsed.raw_text) {
      parseTextIntoFormData(parsed.raw_text, parsed.personal_info?.name, rawFilename || 'Uploaded Resume');
      return;
    }

    const info = parsed.personal_info || {};
    const secs = parsed.sections || {};

    const name = info.name || user?.full_name || '';
    const title = info.title || '';
    const email = info.email || user?.email || '';
    const phone = info.phone || '';
    const location = info.location || '';
    const linkedin = info.linkedin || '';
    const github = info.github || '';

    const summary = secs.summary || '';
    const skills = parsed.all_skills || [];

    let expList = [];
    if (Array.isArray(secs.experience)) {
      expList = secs.experience.map((item, idx) => {
        if (typeof item === 'string') {
          return { id: idx + 1, title: item, company: '', duration: '', description: item };
        }
        return {
          id: idx + 1,
          title: item.title || item.role || '',
          company: item.company || '',
          duration: item.duration || '',
          description: item.description || item.title || ''
        };
      });
    }

    let eduList = [];
    if (Array.isArray(secs.education)) {
      eduList = secs.education.map((item, idx) => {
        if (typeof item === 'string') {
          return { id: idx + 1, degree: item, institution: '', year: '' };
        }
        return {
          id: idx + 1,
          degree: item.degree || item.qualification || '',
          institution: item.institution || '',
          year: item.year || ''
        };
      });
    }

    let projList = [];
    if (Array.isArray(secs.projects)) {
      projList = secs.projects.map((item, idx) => {
        if (typeof item === 'string') {
          return { id: idx + 1, title: item, tech: '', description: item };
        }
        return {
          id: idx + 1,
          title: item.title || item.name || '',
          tech: item.tech || '',
          description: item.description || item.title || ''
        };
      });
    }

    setFormData({
      personalInfo: { name, title, email, phone, location, linkedin, github },
      summary,
      skills,
      experience: expList,
      education: eduList,
      projects: projList,
      certifications: [],
      achievements: [],
      rawText: parsed.raw_text || ''
    });

    if (rawFilename) setResumeFilename(rawFilename);
  };

  useEffect(() => {
    setLoadingLatest(true);

    const cachedData = localStorage.getItem('latest_uploaded_resume');
    if (cachedData) {
      try {
        const parsedReport = JSON.parse(cachedData);
        if (parsedReport && parsedReport.parsed_data) {
          parseAndSetResumeData(parsedReport.parsed_data, parsedReport.filename);
          setLoadingLatest(false);
        }
      } catch (err) {
        console.warn("Cached resume error:", err);
      }
    }

    api.get('/resume/latest')
      .then(res => {
        if (res.data && res.data.parsed_data) {
          parseAndSetResumeData(res.data.parsed_data, res.data.filename || 'Uploaded Resume');
        }
        setLoadingLatest(false);
      })
      .catch(err => {
        console.error("Fetch latest uploaded resume failed:", err);
        setLoadingLatest(false);
      });
  }, [user]);

  // Live ATS Readiness Score Calculation
  const calculateLiveATSScore = () => {
    let score = 0;
    const { personalInfo, summary, skills, experience, education } = formData;

    if (personalInfo.name) score += 10;
    if (personalInfo.email) score += 10;
    if (personalInfo.phone) score += 10;
    if (personalInfo.linkedin) score += 5;
    if (summary && summary.length > 30) score += 15;
    if (skills && skills.length >= 4) score += 20;
    else if (skills && skills.length > 0) score += 10;

    if (experience && experience.length > 0) score += 20;
    if (education && education.length > 0) score += 10;

    return Math.min(score, 100);
  };

  const handleRewriteBulletWithAI = async (type, index = null) => {
    setAiRewritingIndex(type + (index !== null ? `-${index}` : ''));
    try {
      let targetText = '';
      if (type === 'summary') targetText = formData.summary;
      else if (type === 'exp' && index !== null) targetText = formData.experience[index]?.description;
      else if (type === 'proj' && index !== null) targetText = formData.projects[index]?.description;

      const body = new FormData();
      body.append('text', targetText || 'Developed backend microservices and APIs');
      body.append('target_role', formData.personalInfo.title || 'Software Engineer');

      const res = await api.post('/resume/enhance-bullet', body);
      if (res.data && res.data.enhanced) {
        if (type === 'summary') {
          setFormData(prev => ({ ...prev, summary: res.data.enhanced }));
        } else if (type === 'exp' && index !== null) {
          setFormData(prev => {
            const updated = [...prev.experience];
            updated[index] = { ...updated[index], description: res.data.enhanced };
            return { ...prev, experience: updated };
          });
        } else if (type === 'proj' && index !== null) {
          setFormData(prev => {
            const updated = [...prev.projects];
            updated[index] = { ...updated[index], description: res.data.enhanced };
            return { ...prev, projects: updated };
          });
        }
      }
    } catch (err) {
      console.error("AI Bullet Rewrite Error:", err);
    } finally {
      setAiRewritingIndex(null);
    }
  };

  const handleManualPaste = () => {
    if (!pastedText.trim()) return;
    parseTextIntoFormData(pastedText, '', 'Pasted Resume');
    setShowPasteModal(false);
    setPastedText('');
  };

  const handlePersonalInfoChange = (field, val) => {
    setFormData(prev => ({
      ...prev,
      personalInfo: { ...prev.personalInfo, [field]: val }
    }));
  };

  const handleSkillAdd = (newSkill) => {
    if (!newSkill.trim()) return;
    if (formData.skills.includes(newSkill.trim())) return;
    setFormData(prev => ({
      ...prev,
      skills: [...prev.skills, newSkill.trim()]
    }));
  };

  const handleSkillRemove = (index) => {
    setFormData(prev => ({
      ...prev,
      skills: prev.skills.filter((_, i) => i !== index)
    }));
  };

  const handleExperienceChange = (index, field, val) => {
    setFormData(prev => {
      const updated = [...prev.experience];
      updated[index] = { ...updated[index], [field]: val };
      return { ...prev, experience: updated };
    });
  };

  const handleAddExperience = () => {
    setFormData(prev => ({
      ...prev,
      experience: [
        ...prev.experience,
        { id: Date.now(), title: '', company: '', duration: '', description: '' }
      ]
    }));
  };

  const handleRemoveExperience = (index) => {
    setFormData(prev => ({
      ...prev,
      experience: prev.experience.filter((_, i) => i !== index)
    }));
  };

  const handleEducationChange = (index, field, val) => {
    setFormData(prev => {
      const updated = [...prev.education];
      updated[index] = { ...updated[index], [field]: val };
      return { ...prev, education: updated };
    });
  };

  const handleAddEducation = () => {
    setFormData(prev => ({
      ...prev,
      education: [
        ...prev.education,
        { id: Date.now(), degree: '', institution: '', year: '' }
      ]
    }));
  };

  const handleRemoveEducation = (index) => {
    setFormData(prev => ({
      ...prev,
      education: prev.education.filter((_, i) => i !== index)
    }));
  };

  const handleProjectChange = (index, field, val) => {
    setFormData(prev => {
      const updated = [...prev.projects];
      updated[index] = { ...updated[index], [field]: val };
      return { ...prev, projects: updated };
    });
  };

  const handleAddProject = () => {
    setFormData(prev => ({
      ...prev,
      projects: [
        ...prev.projects,
        { id: Date.now(), title: '', tech: '', description: '' }
      ]
    }));
  };

  const handleRemoveProject = (index) => {
    setFormData(prev => ({
      ...prev,
      projects: prev.projects.filter((_, i) => i !== index)
    }));
  };

  const handleAddCertification = () => {
    setFormData(prev => ({
      ...prev,
      certifications: [
        ...prev.certifications,
        { id: Date.now(), name: '', issuer: '', year: '' }
      ]
    }));
  };

  const handleCertificationChange = (index, field, val) => {
    setFormData(prev => {
      const updated = [...prev.certifications];
      updated[index] = { ...updated[index], [field]: val };
      return { ...prev, certifications: updated };
    });
  };

  const handleRemoveCertification = (index) => {
    setFormData(prev => ({
      ...prev,
      certifications: prev.certifications.filter((_, i) => i !== index)
    }));
  };

  const handleDownloadPDF = () => {
    const element = document.getElementById('resume-preview-canvas');
    const opt = {
      margin: 0.3,
      filename: `${(formData.personalInfo.name || 'My_Resume').replace(/\s+/g, '_')}_Resume.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2, useCORS: true },
      jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
    };
    html2pdf().set(opt).from(element).save();
  };

  if (loadingLatest) {
    return (
      <SidebarLayout>
        <div className="glass-card rounded-3xl p-12 text-center border border-slate-800 space-y-4">
          <div className="w-10 h-10 rounded-2xl bg-indigo-600/20 text-indigo-400 flex items-center justify-center mx-auto animate-spin">
            <RefreshCw className="w-5 h-5" />
          </div>
          <p className="text-xs font-semibold text-slate-300">Loading Resume Data & Initializing Custom Builder Studio...</p>
        </div>
      </SidebarLayout>
    );
  }

  const contactItems = [
    formData.personalInfo.email,
    formData.personalInfo.phone,
    formData.personalInfo.location,
    formData.personalInfo.linkedin,
    formData.personalInfo.github
  ].filter(Boolean);

  const atsScore = calculateLiveATSScore();

  return (
    <SidebarLayout>
      <div className="space-y-6">
        {/* Top Header Card */}
        <div className="glass-card rounded-3xl p-8 border border-slate-800/80 shadow-2xl flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-bold uppercase tracking-wider mb-2">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Overleaf, Canva & Original Layout ATS Builder</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">Interactive Resume Studio</h1>
            <p className="text-xs text-slate-400 mt-1 flex items-center gap-1.5">
              <FileCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>Loaded Content from: <strong className="text-white">{resumeFilename || 'Uploaded Document'}</strong></span>
            </p>
          </div>

          <div className="flex items-center gap-3 flex-wrap">
            {/* Live ATS Score Badge */}
            <div className="px-4 py-2.5 rounded-2xl bg-slate-900 border border-slate-800 flex items-center gap-3">
              <div className="text-right">
                <span className="block text-[10px] text-slate-400 uppercase font-bold tracking-wider">Live ATS Health</span>
                <span className="text-sm font-extrabold text-emerald-400">{atsScore} / 100</span>
              </div>
              <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 font-extrabold text-xs">
                {atsScore}%
              </div>
            </div>

            <button
              onClick={() => setShowPasteModal(true)}
              className="px-4 py-3 rounded-2xl font-bold text-xs text-indigo-300 bg-indigo-950/60 border border-indigo-800 hover:bg-indigo-900 transition-all flex items-center gap-2"
            >
              <ClipboardPaste className="w-4 h-4" />
              <span>Paste / Re-Import Text</span>
            </button>

            <button
              onClick={() => window.print()}
              className="px-4 py-3 rounded-2xl font-bold text-xs text-slate-200 bg-slate-900 border border-slate-800 hover:text-white hover:border-slate-700 transition-all flex items-center gap-2"
            >
              <Printer className="w-4 h-4" />
              <span>Print</span>
            </button>

            <button
              onClick={handleDownloadPDF}
              className="px-6 py-3 rounded-2xl font-bold text-xs text-white gradient-bg shadow-glow hover:opacity-95 transition-all flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              <span>Export PDF</span>
            </button>
          </div>
        </div>

        {/* Modal for Pasting Resume Text Directly */}
        {showPasteModal && (
          <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="glass-card rounded-3xl p-6 border border-slate-700 w-full max-w-2xl space-y-4 shadow-2xl">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <ClipboardPaste className="w-4 h-4 text-indigo-400" />
                  <span>Paste Your Resume Content</span>
                </h3>
                <button onClick={() => setShowPasteModal(false)} className="text-slate-400 hover:text-white">
                  <X className="w-5 h-5" />
                </button>
              </div>

              <textarea
                rows={10}
                value={pastedText}
                onChange={(e) => setPastedText(e.target.value)}
                placeholder="Paste your raw resume text here..."
                className="w-full p-4 rounded-2xl bg-slate-900 border border-slate-700 text-xs text-white leading-relaxed focus:outline-none focus:ring-2 focus:ring-indigo-500"
              ></textarea>

              <div className="flex justify-end gap-3">
                <button
                  onClick={() => setShowPasteModal(false)}
                  className="px-4 py-2.5 rounded-xl bg-slate-800 text-slate-300 text-xs font-bold hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  onClick={handleManualPaste}
                  className="px-6 py-2.5 rounded-xl gradient-bg text-white text-xs font-bold shadow-glow hover:opacity-95"
                >
                  Parse & Load Into Templates
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Template Selector & Color Customization Toolbar */}
        <div className="glass-card rounded-3xl p-4 border border-slate-800/80 shadow-2xl flex flex-col lg:flex-row lg:items-center justify-between gap-4 overflow-x-auto">
          <div className="flex items-center gap-2">
            <Layout className="w-4 h-4 text-indigo-400" />
            <span className="text-xs font-extrabold text-slate-300 uppercase tracking-wider">Select Resume Template:</span>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            {[
              { id: 'original', label: 'My Original Uploaded Layout', badge: 'Keep Original Format' },
              { id: 'overleaf', label: 'LaTeX / Overleaf Classic', badge: 'LaTeX Style' },
              { id: 'canva', label: 'Canva Modern Sidebar', badge: 'Canva Style' },
              { id: 'executive', label: 'Executive Slate', badge: 'Executive' },
              { id: 'ats', label: 'ATS Standard Clean', badge: '100% ATS' },
            ].map(t => (
              <button
                key={t.id}
                onClick={() => setTemplate(t.id)}
                className={`px-4 py-2 rounded-2xl text-xs font-bold transition-all flex items-center gap-2 ${
                  template === t.id
                    ? 'gradient-bg text-white shadow-glow'
                    : 'bg-slate-900 text-slate-400 border border-slate-800 hover:text-white hover:border-slate-700'
                }`}
              >
                <span>{t.label}</span>
                <span className="px-1.5 py-0.5 rounded text-[9px] font-extrabold bg-white/20 text-white">
                  {t.badge}
                </span>
              </button>
            ))}
          </div>

          {/* Color Customizer */}
          <div className="flex items-center gap-2 border-t lg:border-t-0 lg:border-l border-slate-800 pt-3 lg:pt-0 lg:pl-4">
            <Palette className="w-3.5 h-3.5 text-indigo-400" />
            <span className="text-[11px] font-bold text-slate-400">Accent Color:</span>
            <div className="flex items-center gap-1.5">
              {[
                { name: 'Indigo', color: '#4f46e5' },
                { name: 'Royal Navy', color: '#1e3a8a' },
                { name: 'Emerald', color: '#047857' },
                { name: 'Crimson', color: '#991b1b' },
                { name: 'Charcoal', color: '#0f172a' },
              ].map(c => (
                <button
                  key={c.color}
                  onClick={() => setAccentColor(c.color)}
                  style={{ backgroundColor: c.color }}
                  className={`w-5 h-5 rounded-full border-2 transition-transform ${
                    accentColor === c.color ? 'scale-125 border-white shadow-glow' : 'border-transparent hover:scale-110'
                  }`}
                  title={c.name}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Two-Column Editor Layout: Left Editor vs Right Live Template Canvas */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column: Interactive Form Controls */}
          <div className="space-y-6">
            {/* If Original Template Mode is Selected, Show Dedicated Raw Text Editor Option */}
            {template === 'original' && (
              <div className="glass-card rounded-3xl p-6 border border-indigo-500/40 space-y-3 bg-indigo-950/20">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <FileText className="w-4 h-4 text-indigo-400" />
                    <span>My Uploaded Resume Raw Text Editor</span>
                  </h3>
                  <span className="text-[10px] font-extrabold text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">
                    Freeform Mode
                  </span>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Edit your uploaded resume text below. Any additions, updates, or line edits will instantly update in <strong>My Original Uploaded Layout</strong> preview on the right.
                </p>
                <textarea
                  rows={14}
                  value={formData.rawText}
                  onChange={(e) => {
                    const newText = e.target.value;
                    setFormData(prev => ({ ...prev, rawText: newText }));
                    parseTextIntoFormData(newText, formData.personalInfo.name, resumeFilename);
                  }}
                  className="w-full p-4 rounded-2xl bg-slate-900 border border-slate-700 text-xs text-white leading-relaxed focus:outline-none focus:ring-2 focus:ring-indigo-500"
                ></textarea>
              </div>
            )}

            {/* Personal Details */}
            <div className="glass-card rounded-3xl p-6 border border-slate-800/80 shadow-2xl space-y-4">
              <h3 className="text-sm font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-2">
                <User className="w-4 h-4 text-indigo-400" />
                <span>Personal & Contact Info</span>
              </h3>
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="col-span-2 sm:col-span-1">
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Full Name</label>
                  <input
                    type="text"
                    value={formData.personalInfo.name}
                    onChange={(e) => handlePersonalInfoChange('name', e.target.value)}
                    className="w-full p-2.5 rounded-xl bg-slate-900 border border-slate-700/80 text-xs font-semibold text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div className="col-span-2 sm:col-span-1">
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Job Title</label>
                  <input
                    type="text"
                    value={formData.personalInfo.title}
                    onChange={(e) => handlePersonalInfoChange('title', e.target.value)}
                    className="w-full p-2.5 rounded-xl bg-slate-900 border border-slate-700/80 text-xs font-semibold text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Email</label>
                  <input
                    type="email"
                    value={formData.personalInfo.email}
                    onChange={(e) => handlePersonalInfoChange('email', e.target.value)}
                    className="w-full p-2.5 rounded-xl bg-slate-900 border border-slate-700/80 text-xs font-semibold text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Phone</label>
                  <input
                    type="text"
                    value={formData.personalInfo.phone}
                    onChange={(e) => handlePersonalInfoChange('phone', e.target.value)}
                    className="w-full p-2.5 rounded-xl bg-slate-900 border border-slate-700/80 text-xs font-semibold text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Location</label>
                  <input
                    type="text"
                    value={formData.personalInfo.location}
                    onChange={(e) => handlePersonalInfoChange('location', e.target.value)}
                    className="w-full p-2.5 rounded-xl bg-slate-900 border border-slate-700/80 text-xs font-semibold text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">LinkedIn Profile</label>
                  <input
                    type="text"
                    value={formData.personalInfo.linkedin}
                    onChange={(e) => handlePersonalInfoChange('linkedin', e.target.value)}
                    className="w-full p-2.5 rounded-xl bg-slate-900 border border-slate-700/80 text-xs font-semibold text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>
            </div>

            {/* Summary */}
            <div className="glass-card rounded-3xl p-6 border border-slate-800/80 shadow-2xl space-y-3">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <h3 className="text-sm font-bold text-white">Professional Summary</h3>
                <button
                  onClick={() => handleRewriteBulletWithAI('summary')}
                  disabled={aiRewritingIndex === 'summary'}
                  className="px-3 py-1 rounded-xl bg-indigo-600/20 border border-indigo-500/40 text-indigo-400 text-xs font-bold flex items-center gap-1.5 hover:bg-indigo-600 hover:text-white transition-all disabled:opacity-50"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>{aiRewritingIndex === 'summary' ? 'Rewriting...' : '✨ Rewrite with AI'}</span>
                </button>
              </div>
              <textarea
                rows={4}
                value={formData.summary}
                onChange={(e) => setFormData(prev => ({ ...prev, summary: e.target.value }))}
                className="w-full p-3 rounded-xl bg-slate-900 border border-slate-700/80 text-xs font-medium text-white leading-relaxed focus:outline-none focus:ring-2 focus:ring-indigo-500"
              ></textarea>
            </div>

            {/* Technical Skills */}
            <div className="glass-card rounded-3xl p-6 border border-slate-800/80 shadow-2xl space-y-3">
              <h3 className="text-sm font-bold text-white border-b border-slate-800 pb-2">Technical Skills ({formData.skills.length})</h3>
              <div className="flex flex-wrap gap-1.5">
                {formData.skills.map((sk, idx) => (
                  <span key={idx} className="px-2.5 py-1 rounded-lg bg-slate-800 text-slate-200 text-xs font-semibold flex items-center gap-1.5 border border-slate-700/80">
                    <span>{sk}</span>
                    <button onClick={() => handleSkillRemove(idx)} className="text-rose-400 hover:text-rose-300 font-bold text-sm">×</button>
                  </span>
                ))}
              </div>
              <div className="flex gap-2 pt-2">
                <input
                  type="text"
                  placeholder="Add skill..."
                  id="new-skill-input"
                  className="flex-1 p-2.5 rounded-xl bg-slate-900 border border-slate-700/80 text-xs font-semibold text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      handleSkillAdd(e.target.value);
                      e.target.value = '';
                    }
                  }}
                />
                <button
                  onClick={() => {
                    const el = document.getElementById('new-skill-input');
                    handleSkillAdd(el.value);
                    el.value = '';
                  }}
                  className="px-4 py-2.5 rounded-xl bg-indigo-600 text-white font-bold text-xs shadow-glow hover:opacity-95"
                >
                  Add Skill
                </button>
              </div>
            </div>

            {/* Work Experience */}
            <div className="glass-card rounded-3xl p-6 border border-slate-800/80 shadow-2xl space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Briefcase className="w-4 h-4 text-indigo-400" />
                  <span>Work Experience ({formData.experience.length})</span>
                </h3>
                <button
                  onClick={handleAddExperience}
                  className="px-3 py-1 rounded-xl bg-indigo-600/20 border border-indigo-500/40 text-indigo-400 text-xs font-bold flex items-center gap-1 hover:bg-indigo-600 hover:text-white transition-all"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Add Experience</span>
                </button>
              </div>

              {formData.experience.map((exp, idx) => (
                <div key={exp.id || idx} className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-3 relative">
                  <div className="flex items-center justify-between pr-8">
                    <span className="text-xs font-bold text-indigo-400">Entry #{idx + 1}</span>
                    <button
                      onClick={() => handleRewriteBulletWithAI('exp', idx)}
                      disabled={aiRewritingIndex === `exp-${idx}`}
                      className="px-2.5 py-1 rounded-lg bg-indigo-600/20 border border-indigo-500/40 text-indigo-400 text-[11px] font-bold flex items-center gap-1 hover:bg-indigo-600 hover:text-white transition-all disabled:opacity-50"
                    >
                      <Sparkles className="w-3 h-3" />
                      <span>{aiRewritingIndex === `exp-${idx}` ? 'Rewriting...' : '✨ Rewrite Bullet'}</span>
                    </button>
                  </div>
                  <button
                    onClick={() => handleRemoveExperience(idx)}
                    className="absolute top-3 right-3 text-slate-500 hover:text-rose-400"
                    title="Remove item"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                  <div className="grid grid-cols-2 gap-3 text-xs">
                    <div>
                      <label className="block text-[10px] font-semibold text-slate-400 mb-1">Job Title</label>
                      <input
                        type="text"
                        value={exp.title}
                        onChange={(e) => handleExperienceChange(idx, 'title', e.target.value)}
                        className="w-full p-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] font-semibold text-slate-400 mb-1">Company</label>
                      <input
                        type="text"
                        value={exp.company}
                        onChange={(e) => handleExperienceChange(idx, 'company', e.target.value)}
                        className="w-full p-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white"
                      />
                    </div>
                    <div className="col-span-2">
                      <label className="block text-[10px] font-semibold text-slate-400 mb-1">Duration / Dates</label>
                      <input
                        type="text"
                        value={exp.duration}
                        onChange={(e) => handleExperienceChange(idx, 'duration', e.target.value)}
                        className="w-full p-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white"
                      />
                    </div>
                    <div className="col-span-2">
                      <label className="block text-[10px] font-semibold text-slate-400 mb-1">Description / Key Accomplishments</label>
                      <textarea
                        rows={3}
                        value={exp.description}
                        onChange={(e) => handleExperienceChange(idx, 'description', e.target.value)}
                        className="w-full p-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white leading-relaxed"
                      ></textarea>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Projects */}
            <div className="glass-card rounded-3xl p-6 border border-slate-800/80 shadow-2xl space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Code2 className="w-4 h-4 text-indigo-400" />
                  <span>Projects ({formData.projects.length})</span>
                </h3>
                <button
                  onClick={handleAddProject}
                  className="px-3 py-1 rounded-xl bg-indigo-600/20 border border-indigo-500/40 text-indigo-400 text-xs font-bold flex items-center gap-1 hover:bg-indigo-600 hover:text-white transition-all"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Add Project</span>
                </button>
              </div>

              {formData.projects.map((proj, idx) => (
                <div key={proj.id || idx} className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-3 relative">
                  <div className="flex items-center justify-between pr-8">
                    <span className="text-xs font-bold text-indigo-400">Project #{idx + 1}</span>
                    <button
                      onClick={() => handleRewriteBulletWithAI('proj', idx)}
                      disabled={aiRewritingIndex === `proj-${idx}`}
                      className="px-2.5 py-1 rounded-lg bg-indigo-600/20 border border-indigo-500/40 text-indigo-400 text-[11px] font-bold flex items-center gap-1 hover:bg-indigo-600 hover:text-white transition-all disabled:opacity-50"
                    >
                      <Sparkles className="w-3 h-3" />
                      <span>{aiRewritingIndex === `proj-${idx}` ? 'Rewriting...' : '✨ Rewrite Bullet'}</span>
                    </button>
                  </div>
                  <button
                    onClick={() => handleRemoveProject(idx)}
                    className="absolute top-3 right-3 text-slate-500 hover:text-rose-400"
                    title="Remove item"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                  <div className="grid grid-cols-2 gap-3 text-xs">
                    <div>
                      <label className="block text-[10px] font-semibold text-slate-400 mb-1">Project Title</label>
                      <input
                        type="text"
                        value={proj.title}
                        onChange={(e) => handleProjectChange(idx, 'title', e.target.value)}
                        className="w-full p-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] font-semibold text-slate-400 mb-1">Technologies Used</label>
                      <input
                        type="text"
                        value={proj.tech}
                        onChange={(e) => handleProjectChange(idx, 'tech', e.target.value)}
                        className="w-full p-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white"
                      />
                    </div>
                    <div className="col-span-2">
                      <label className="block text-[10px] font-semibold text-slate-400 mb-1">Project Description</label>
                      <textarea
                        rows={2}
                        value={proj.description}
                        onChange={(e) => handleProjectChange(idx, 'description', e.target.value)}
                        className="w-full p-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white leading-relaxed"
                      ></textarea>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Education */}
            <div className="glass-card rounded-3xl p-6 border border-slate-800/80 shadow-2xl space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <GraduationCap className="w-4 h-4 text-indigo-400" />
                  <span>Education ({formData.education.length})</span>
                </h3>
                <button
                  onClick={handleAddEducation}
                  className="px-3 py-1 rounded-xl bg-indigo-600/20 border border-indigo-500/40 text-indigo-400 text-xs font-bold flex items-center gap-1 hover:bg-indigo-600 hover:text-white transition-all"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Add Education</span>
                </button>
              </div>

              {formData.education.map((edu, idx) => (
                <div key={edu.id || idx} className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-3 relative">
                  <button
                    onClick={() => handleRemoveEducation(idx)}
                    className="absolute top-3 right-3 text-slate-500 hover:text-rose-400"
                    title="Remove item"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                  <div className="grid grid-cols-2 gap-3 text-xs pr-6">
                    <div>
                      <label className="block text-[10px] font-semibold text-slate-400 mb-1">Degree / Qualification</label>
                      <input
                        type="text"
                        value={edu.degree}
                        onChange={(e) => handleEducationChange(idx, 'degree', e.target.value)}
                        className="w-full p-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] font-semibold text-slate-400 mb-1">Institution</label>
                      <input
                        type="text"
                        value={edu.institution}
                        onChange={(e) => handleEducationChange(idx, 'institution', e.target.value)}
                        className="w-full p-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white"
                      />
                    </div>
                    <div className="col-span-2">
                      <label className="block text-[10px] font-semibold text-slate-400 mb-1">Graduation Year / Dates</label>
                      <input
                        type="text"
                        value={edu.year}
                        onChange={(e) => handleEducationChange(idx, 'year', e.target.value)}
                        className="w-full p-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Certifications & Licenses */}
            <div className="glass-card rounded-3xl p-6 border border-slate-800/80 shadow-2xl space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Award className="w-4 h-4 text-indigo-400" />
                  <span>Certifications & Licenses ({formData.certifications.length})</span>
                </h3>
                <button
                  onClick={handleAddCertification}
                  className="px-3 py-1 rounded-xl bg-indigo-600/20 border border-indigo-500/40 text-indigo-400 text-xs font-bold flex items-center gap-1 hover:bg-indigo-600 hover:text-white transition-all"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Add Cert</span>
                </button>
              </div>

              {formData.certifications.map((cert, idx) => (
                <div key={cert.id || idx} className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-3 relative">
                  <button
                    onClick={() => handleRemoveCertification(idx)}
                    className="absolute top-3 right-3 text-slate-500 hover:text-rose-400"
                    title="Remove item"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                  <div className="grid grid-cols-2 gap-3 text-xs pr-6">
                    <div className="col-span-2 sm:col-span-1">
                      <label className="block text-[10px] font-semibold text-slate-400 mb-1">Certification Name</label>
                      <input
                        type="text"
                        value={cert.name}
                        onChange={(e) => handleCertificationChange(idx, 'name', e.target.value)}
                        className="w-full p-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] font-semibold text-slate-400 mb-1">Issuing Organization / Year</label>
                      <input
                        type="text"
                        value={cert.year}
                        onChange={(e) => handleCertificationChange(idx, 'year', e.target.value)}
                        className="w-full p-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right Column: Live Aligned Template Canvas */}
          <div className="glass-card p-4 rounded-3xl border border-slate-800/80 overflow-auto sticky top-4">
            <div className="flex items-center justify-between mb-3 px-2">
              <span className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <Eye className="w-4 h-4 text-indigo-400" />
                <span>Live Canvas Preview ({template.toUpperCase()})</span>
              </span>
              <span className="text-[10px] text-emerald-400 font-bold bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/20">
                Live Auto-Render
              </span>
            </div>

            {/* Renderable Canvas Document Container */}
            <div id="resume-preview-canvas" className="bg-white text-slate-900 shadow-2xl rounded-lg min-h-[900px] relative">
              {/* Single-Page Boundary Guide */}
              <div className="absolute top-[880px] left-0 right-0 border-b border-dashed border-rose-400 text-rose-500 text-[9px] font-bold px-4 py-0.5 bg-rose-50/80 flex items-center justify-between pointer-events-none z-10">
                <span>Page 1 / Page 2 Standard ATS Boundary Line</span>
                <span>Optimal 1-Page Limit</span>
              </div>

              {/* Template 0: MY ORIGINAL UPLOADED LAYOUT */}
              {template === 'original' && (
                <div className="p-10 text-xs text-slate-900 font-sans leading-relaxed space-y-4 whitespace-pre-wrap">
                  {/* Title Header */}
                  <div className="border-b-2 pb-3 mb-4" style={{ borderColor: accentColor }}>
                    <h1 className="text-2xl font-extrabold uppercase tracking-tight text-slate-900">
                      {formData.personalInfo.name || 'Uploaded Resume'}
                    </h1>
                    {contactItems.length > 0 && (
                      <p className="text-[11px] text-slate-700 mt-1 font-medium">
                        {contactItems.join('  |  ')}
                      </p>
                    )}
                  </div>
                  {/* Exact Raw Text Render */}
                  <div className="text-[11px] text-slate-800 leading-relaxed font-mono bg-slate-50/50 p-4 rounded-xl border border-slate-200">
                    {formData.rawText || 'No raw text extracted. Paste your resume text using "Paste / Re-Import Text" above.'}
                  </div>
                </div>
              )}

              {/* Template 1: OVERLEAF / LATEX CLASSIC */}
              {template === 'overleaf' && (
                <div className="p-10 text-xs text-slate-900 font-serif leading-relaxed space-y-4">
                  {/* Header */}
                  <div className="text-center border-b-2 pb-3" style={{ borderColor: accentColor }}>
                    <h1 className="text-2xl font-bold tracking-tight text-slate-900 uppercase">
                      {formData.personalInfo.name}
                    </h1>
                    {formData.personalInfo.title && (
                      <p className="text-[11px] font-sans font-semibold mt-0.5" style={{ color: accentColor }}>
                        {formData.personalInfo.title}
                      </p>
                    )}
                    {contactItems.length > 0 && (
                      <p className="text-[10px] font-sans text-slate-700 mt-1">
                        {contactItems.join('  •  ')}
                      </p>
                    )}
                  </div>

                  {/* Summary */}
                  {formData.summary && (
                    <div>
                      <h2 className="text-xs font-sans font-bold uppercase tracking-wider border-b pb-0.5 mb-1.5 text-slate-900" style={{ borderColor: accentColor }}>
                        Professional Summary
                      </h2>
                      <p className="text-[11px] text-slate-800 font-sans text-justify leading-relaxed">
                        {formData.summary}
                      </p>
                    </div>
                  )}

                  {/* Skills */}
                  {formData.skills && formData.skills.length > 0 && (
                    <div>
                      <h2 className="text-xs font-sans font-bold uppercase tracking-wider border-b pb-0.5 mb-1.5 text-slate-900" style={{ borderColor: accentColor }}>
                        Technical Skills
                      </h2>
                      <p className="text-[11px] font-sans font-medium text-slate-900">
                        <strong className="font-bold">Technologies:</strong> {formData.skills.join(', ')}
                      </p>
                    </div>
                  )}

                  {/* Work Experience */}
                  {formData.experience && formData.experience.length > 0 && (
                    <div>
                      <h2 className="text-xs font-sans font-bold uppercase tracking-wider border-b pb-0.5 mb-2 text-slate-900" style={{ borderColor: accentColor }}>
                        Work Experience
                      </h2>
                      <div className="space-y-3">
                        {formData.experience.map((exp, i) => (
                          <div key={i} className="font-sans space-y-0.5">
                            <div className="flex justify-between items-baseline text-[11px]">
                              <span className="font-bold text-slate-900">{exp.title}</span>
                              {exp.duration && <span className="font-semibold text-slate-600 text-[10px]">{exp.duration}</span>}
                            </div>
                            {exp.company && <p className="text-[10px] font-semibold text-slate-700 italic">{exp.company}</p>}
                            {exp.description && (
                              <p className="text-[11px] text-slate-800 text-justify leading-relaxed pt-0.5">
                                • {exp.description}
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Projects */}
                  {formData.projects && formData.projects.length > 0 && (
                    <div>
                      <h2 className="text-xs font-sans font-bold uppercase tracking-wider border-b pb-0.5 mb-2 text-slate-900" style={{ borderColor: accentColor }}>
                        Technical Projects
                      </h2>
                      <div className="space-y-2.5 font-sans">
                        {formData.projects.map((proj, i) => (
                          <div key={i} className="space-y-0.5">
                            <div className="flex justify-between items-baseline text-[11px]">
                              <span className="font-bold text-slate-900">{proj.title}</span>
                              {proj.tech && <span className="text-[10px] font-semibold" style={{ color: accentColor }}>[{proj.tech}]</span>}
                            </div>
                            {proj.description && (
                              <p className="text-[11px] text-slate-800 leading-relaxed text-justify">
                                • {proj.description}
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Education */}
                  {formData.education && formData.education.length > 0 && (
                    <div>
                      <h2 className="text-xs font-sans font-bold uppercase tracking-wider border-b pb-0.5 mb-1.5 text-slate-900" style={{ borderColor: accentColor }}>
                        Education
                      </h2>
                      <div className="space-y-1.5 font-sans">
                        {formData.education.map((edu, i) => (
                          <div key={i} className="flex justify-between items-baseline text-[11px]">
                            <div>
                              <span className="font-bold text-slate-900">{edu.degree}</span>
                              {edu.institution && <span className="text-slate-700 italic"> — {edu.institution}</span>}
                            </div>
                            {edu.year && <span className="font-semibold text-slate-600 text-[10px]">{edu.year}</span>}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Certifications */}
                  {formData.certifications && formData.certifications.length > 0 && (
                    <div>
                      <h2 className="text-xs font-sans font-bold uppercase tracking-wider border-b pb-0.5 mb-1.5 text-slate-900" style={{ borderColor: accentColor }}>
                        Certifications & Credentials
                      </h2>
                      <div className="space-y-1 font-sans">
                        {formData.certifications.map((c, i) => (
                          <div key={i} className="flex justify-between text-[11px]">
                            <span className="font-semibold">{c.name}</span>
                            {c.year && <span className="text-slate-600 text-[10px]">{c.year}</span>}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Template 2: CANVA MODERN SIDEBAR */}
              {template === 'canva' && (
                <div className="grid grid-cols-3 min-h-[900px] font-sans">
                  {/* Left Sidebar */}
                  <div className="bg-slate-900 text-white p-6 space-y-6 border-r border-slate-800">
                    <div>
                      <h1 className="text-lg font-extrabold tracking-tight text-white uppercase">
                        {formData.personalInfo.name}
                      </h1>
                      {formData.personalInfo.title && (
                        <p className="text-[10px] font-bold mt-0.5" style={{ color: accentColor }}>
                          {formData.personalInfo.title}
                        </p>
                      )}
                    </div>

                    {/* Contact */}
                    {contactItems.length > 0 && (
                      <div className="space-y-2 text-[10px] text-slate-300">
                        <h3 className="text-xs font-bold uppercase tracking-wider border-b border-slate-800 pb-1" style={{ color: accentColor }}>Contact</h3>
                        {formData.personalInfo.email && <p className="break-all">{formData.personalInfo.email}</p>}
                        {formData.personalInfo.phone && <p>{formData.personalInfo.phone}</p>}
                        {formData.personalInfo.location && <p>{formData.personalInfo.location}</p>}
                        {formData.personalInfo.linkedin && <p className="break-all">{formData.personalInfo.linkedin}</p>}
                      </div>
                    )}

                    {/* Skills */}
                    {formData.skills && formData.skills.length > 0 && (
                      <div className="space-y-2">
                        <h3 className="text-xs font-bold uppercase tracking-wider border-b border-slate-800 pb-1" style={{ color: accentColor }}>Skills</h3>
                        <div className="flex flex-wrap gap-1">
                          {formData.skills.map((sk, idx) => (
                            <span key={idx} className="px-2 py-0.5 rounded bg-slate-800 text-white border border-slate-700 text-[10px] font-bold">
                              {sk}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Education */}
                    {formData.education && formData.education.length > 0 && (
                      <div className="space-y-2 text-[10px]">
                        <h3 className="text-xs font-bold uppercase tracking-wider border-b border-slate-800 pb-1" style={{ color: accentColor }}>Education</h3>
                        {formData.education.map((edu, idx) => (
                          <div key={idx} className="space-y-0.5">
                            <p className="font-bold text-white">{edu.degree}</p>
                            {edu.institution && <p className="text-slate-400">{edu.institution}</p>}
                            {edu.year && <p className="font-semibold text-slate-400">{edu.year}</p>}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Right Content Column */}
                  <div className="col-span-2 p-8 space-y-6 text-xs text-slate-900 bg-white">
                    {/* Summary */}
                    {formData.summary && (
                      <div className="space-y-1.5">
                        <h2 className="text-xs font-bold uppercase tracking-wider border-b-2 pb-1" style={{ color: accentColor, borderColor: accentColor }}>
                          Professional Profile
                        </h2>
                        <p className="text-[11px] text-slate-700 leading-relaxed text-justify">
                          {formData.summary}
                        </p>
                      </div>
                    )}

                    {/* Work Experience */}
                    {formData.experience && formData.experience.length > 0 && (
                      <div className="space-y-3">
                        <h2 className="text-xs font-bold uppercase tracking-wider border-b-2 pb-1" style={{ color: accentColor, borderColor: accentColor }}>
                          Work Experience
                        </h2>
                        {formData.experience.map((exp, i) => (
                          <div key={i} className="space-y-1">
                            <div className="flex justify-between items-baseline">
                              <span className="font-bold text-slate-900 text-[11px]">{exp.title}</span>
                              {exp.duration && <span className="text-[10px] font-bold text-slate-600">{exp.duration}</span>}
                            </div>
                            {exp.company && <p className="text-[10px] font-bold text-slate-600">{exp.company}</p>}
                            {exp.description && (
                              <p className="text-[11px] text-slate-700 leading-relaxed">
                                {exp.description}
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Projects */}
                    {formData.projects && formData.projects.length > 0 && (
                      <div className="space-y-3">
                        <h2 className="text-xs font-bold uppercase tracking-wider border-b-2 pb-1" style={{ color: accentColor, borderColor: accentColor }}>
                          Key Projects
                        </h2>
                        {formData.projects.map((proj, i) => (
                          <div key={i} className="space-y-0.5">
                            <div className="flex justify-between items-baseline">
                              <span className="font-bold text-slate-900 text-[11px]">{proj.title}</span>
                            </div>
                            {proj.tech && <p className="text-[10px] font-bold text-slate-600">{proj.tech}</p>}
                            {proj.description && (
                              <p className="text-[11px] text-slate-700 leading-relaxed">
                                {proj.description}
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Template 3: EXECUTIVE SLATE */}
              {template === 'executive' && (
                <div className="p-10 text-xs text-slate-900 font-sans leading-relaxed space-y-5">
                  {/* Header Banner */}
                  <div className="bg-slate-900 text-white p-6 rounded-2xl space-y-2">
                    <h1 className="text-2xl font-extrabold tracking-tight text-white uppercase">
                      {formData.personalInfo.name}
                    </h1>
                    {formData.personalInfo.title && <p className="text-xs font-bold" style={{ color: accentColor }}>{formData.personalInfo.title}</p>}
                    {contactItems.length > 0 && (
                      <p className="text-[10px] text-slate-300 pt-1">
                        {contactItems.join('  •  ')}
                      </p>
                    )}
                  </div>

                  {/* Summary */}
                  {formData.summary && (
                    <div className="space-y-1">
                      <h2 className="text-xs font-bold uppercase tracking-wider text-slate-900 border-b-2 pb-1" style={{ borderColor: accentColor }}>
                        Executive Summary
                      </h2>
                      <p className="text-[11px] text-slate-800 leading-relaxed pt-1">
                        {formData.summary}
                      </p>
                    </div>
                  )}

                  {/* Skills */}
                  {formData.skills && formData.skills.length > 0 && (
                    <div className="space-y-2">
                      <h2 className="text-xs font-bold uppercase tracking-wider text-slate-900 border-b-2 pb-1" style={{ borderColor: accentColor }}>
                        Core Competencies
                      </h2>
                      <div className="flex flex-wrap gap-1.5 pt-1">
                        {formData.skills.map((sk, idx) => (
                          <span key={idx} className="px-2.5 py-1 rounded bg-slate-100 text-slate-900 border border-slate-300 font-bold text-[10px]">
                            {sk}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Work Experience */}
                  {formData.experience && formData.experience.length > 0 && (
                    <div className="space-y-3">
                      <h2 className="text-xs font-bold uppercase tracking-wider text-slate-900 border-b-2 pb-1" style={{ borderColor: accentColor }}>
                        Professional Experience
                      </h2>
                      {formData.experience.map((exp, i) => (
                        <div key={i} className="space-y-1">
                          <div className="flex justify-between items-baseline font-bold text-[11px]">
                            <span>{exp.title} {exp.company && <span className="text-slate-600">— {exp.company}</span>}</span>
                            {exp.duration && <span className="text-[10px] text-slate-500 font-bold">{exp.duration}</span>}
                          </div>
                          {exp.description && (
                            <p className="text-[11px] text-slate-800 leading-relaxed pl-2">
                              • {exp.description}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Education */}
                  {formData.education && formData.education.length > 0 && (
                    <div className="space-y-2">
                      <h2 className="text-xs font-bold uppercase tracking-wider text-slate-900 border-b-2 pb-1" style={{ borderColor: accentColor }}>
                        Education & Credentials
                      </h2>
                      {formData.education.map((edu, i) => (
                        <div key={i} className="flex justify-between items-baseline text-[11px]">
                          <span className="font-bold">{edu.degree} {edu.institution && <span className="font-normal text-slate-700">— {edu.institution}</span>}</span>
                          {edu.year && <span className="text-[10px] text-slate-600 font-bold">{edu.year}</span>}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Template 4: STANDARD CLEAN ATS */}
              {template === 'ats' && (
                <div className="p-10 text-xs text-slate-900 font-sans leading-relaxed space-y-4">
                  {/* Header */}
                  <div className="text-center border-b-2 pb-3" style={{ borderColor: accentColor }}>
                    <h1 className="text-2xl font-extrabold uppercase tracking-tight text-slate-900">
                      {formData.personalInfo.name}
                    </h1>
                    {contactItems.length > 0 && (
                      <p className="text-[11px] text-slate-700 mt-1 font-medium">
                        {contactItems.join('  |  ')}
                      </p>
                    )}
                  </div>

                  {/* Summary */}
                  {formData.summary && (
                    <div className="mt-3">
                      <h2 className="text-xs font-bold uppercase border-b-2 pb-0.5 mb-1.5 tracking-wider text-slate-900" style={{ borderColor: accentColor }}>
                        PROFESSIONAL SUMMARY
                      </h2>
                      <p className="text-[11px] text-slate-800 leading-relaxed">
                        {formData.summary}
                      </p>
                    </div>
                  )}

                  {/* Skills */}
                  {formData.skills && formData.skills.length > 0 && (
                    <div className="mt-3">
                      <h2 className="text-xs font-bold uppercase border-b-2 pb-0.5 mb-1.5 tracking-wider text-slate-900" style={{ borderColor: accentColor }}>
                        TECHNICAL SKILLS
                      </h2>
                      <p className="text-[11px] font-medium text-slate-900 leading-relaxed">
                        {formData.skills.join('  •  ')}
                      </p>
                    </div>
                  )}

                  {/* Work Experience */}
                  {formData.experience && formData.experience.length > 0 && (
                    <div className="mt-3">
                      <h2 className="text-xs font-bold uppercase border-b-2 pb-0.5 mb-2 tracking-wider text-slate-900" style={{ borderColor: accentColor }}>
                        WORK EXPERIENCE
                      </h2>
                      <div className="space-y-3">
                        {formData.experience.map((exp, i) => (
                          <div key={i} className="space-y-1">
                            <div className="flex justify-between items-baseline font-bold text-[11px] text-slate-900">
                              <span>
                                {exp.title} {exp.company && <span className="font-semibold text-slate-700"> — {exp.company}</span>}
                              </span>
                              {exp.duration && (
                                <span className="text-[10px] text-slate-600 font-semibold text-right">
                                  {exp.duration}
                                </span>
                              )}
                            </div>
                            {exp.description && (
                              <p className="text-[11px] text-slate-800 leading-relaxed pl-2">
                                • {exp.description}
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Projects */}
                  {formData.projects && formData.projects.length > 0 && (
                    <div className="mt-3">
                      <h2 className="text-xs font-bold uppercase border-b-2 pb-0.5 mb-2 tracking-wider text-slate-900" style={{ borderColor: accentColor }}>
                        PROJECTS
                      </h2>
                      <div className="space-y-2.5">
                        {formData.projects.map((proj, i) => (
                          <div key={i} className="space-y-0.5">
                            <div className="flex justify-between items-baseline font-bold text-[11px]">
                              <span>{proj.title}</span>
                              {proj.tech && <span className="text-[10px] text-slate-600">({proj.tech})</span>}
                            </div>
                            {proj.description && (
                              <p className="text-[11px] text-slate-800 leading-relaxed pl-2">
                                • {proj.description}
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Education */}
                  {formData.education && formData.education.length > 0 && (
                    <div className="mt-3">
                      <h2 className="text-xs font-bold uppercase border-b-2 pb-0.5 mb-1.5 tracking-wider text-slate-900" style={{ borderColor: accentColor }}>
                        EDUCATION
                      </h2>
                      <div className="space-y-2">
                        {formData.education.map((edu, i) => (
                          <div key={i} className="flex justify-between items-baseline text-[11px] font-medium text-slate-900">
                            <span className="font-bold">
                              {edu.degree} {edu.institution && <span className="font-normal text-slate-700"> — {edu.institution}</span>}
                            </span>
                            {edu.year && (
                              <span className="text-[10px] text-slate-600 font-semibold text-right">
                                {edu.year}
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </SidebarLayout>
  );
};

export default ResumeBuilderPage;
