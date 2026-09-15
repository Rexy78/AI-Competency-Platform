import React from 'react';
import { Link } from 'react-router-dom';
import { MessageSquare } from 'lucide-react';

export default function AstraButton() {
  return (
    <Link to="/chatbot" aria-label="Open Interview Prep" className="astra-floating" title="Open Interview Prep">
      <div className="astra-button-inner">
        <MessageSquare className="w-5 h-5 text-white" />
        <span className="sr-only">Interview Prep</span>
      </div>
    </Link>
  );
}
