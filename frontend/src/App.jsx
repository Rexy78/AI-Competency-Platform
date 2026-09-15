import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';

import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import DashboardPage from './pages/DashboardPage';
import ResumeUploadPage from './pages/ResumeUploadPage';
import ResumeAnalysisPage from './pages/ResumeAnalysisPage';
import SkillGapPage from './pages/SkillGapPage';
import RoadmapPage from './pages/RoadmapPage';
import JobRecommendPage from './pages/JobRecommendPage';
import JDAnalyzerPage from './pages/JDAnalyzerPage';
import ResumeImprovementPage from './pages/ResumeImprovementPage';
import ResumeBuilderPage from './pages/ResumeBuilderPage';
import AdminDashboardPage from './pages/AdminDashboardPage';
import AIInterviewPage from './pages/AIInterviewPage';
import AstraChatbotPage from './pages/AstraChatbotPage';
import ProfilePage from './pages/ProfilePage';
import AstraButton from './components/AstraButton';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />

      {/* 13 Core GenAI Platform Routes */}
      <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
      <Route path="/upload" element={<ProtectedRoute><ResumeUploadPage /></ProtectedRoute>} />
      <Route path="/analysis" element={<ProtectedRoute><ResumeAnalysisPage /></ProtectedRoute>} />
      <Route path="/ats-analysis" element={<ProtectedRoute><ResumeAnalysisPage /></ProtectedRoute>} />
      <Route path="/skill-gap" element={<ProtectedRoute><SkillGapPage /></ProtectedRoute>} />
      <Route path="/jobs" element={<ProtectedRoute><JobRecommendPage /></ProtectedRoute>} />
      <Route path="/job-recommendations" element={<ProtectedRoute><JobRecommendPage /></ProtectedRoute>} />
      <Route path="/jd-analyzer" element={<ProtectedRoute><JDAnalyzerPage /></ProtectedRoute>} />
      <Route path="/builder" element={<ProtectedRoute><ResumeBuilderPage /></ProtectedRoute>} />
      <Route path="/roadmap" element={<ProtectedRoute><RoadmapPage /></ProtectedRoute>} />
      <Route path="/improve" element={<ProtectedRoute><ResumeImprovementPage /></ProtectedRoute>} />
      <Route path="/improver" element={<ProtectedRoute><ResumeImprovementPage /></ProtectedRoute>} />
      <Route path="/interview" element={<ProtectedRoute><AIInterviewPage /></ProtectedRoute>} />
      <Route path="/astra" element={<ProtectedRoute><AstraChatbotPage /></ProtectedRoute>} />
      <Route path="/chatbot" element={<ProtectedRoute><AstraChatbotPage /></ProtectedRoute>} />
      <Route path="/profile text" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
      <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
      <Route path="/admin" element={<ProtectedRoute><AdminDashboardPage /></ProtectedRoute>} />

      {/* Catch-all fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <AppRoutes />
        <AstraButton />
      </Router>
    </AuthProvider>
  );
}
