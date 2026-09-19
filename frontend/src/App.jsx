import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import QueuePage from './pages/QueuePage';
import WorkspacePage from './pages/WorkspacePage';
import ReviewPage from './pages/ReviewPage';
import './index.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<QueuePage />} />
        <Route path="/workspace/:id" element={<WorkspacePage />} />
        <Route path="/review/:id" element={<ReviewPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
