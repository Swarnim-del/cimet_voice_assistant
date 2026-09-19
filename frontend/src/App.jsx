import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import QueuePage from './pages/QueuePage';
import WorkspacePage from './pages/WorkspacePage';
import ReviewPage from './pages/ReviewPage';
import AICallsPage from './pages/AICallsPage';
import Navigation from './components/Navigation';
import './index.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-[#F7F9FC]">
        <Navigation />
        <Routes>
          <Route path="/" element={<QueuePage />} />
          <Route path="/ai-calls" element={<AICallsPage />} />
          <Route path="/workspace/:id" element={<WorkspacePage />} />
          <Route path="/review/:id" element={<ReviewPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
