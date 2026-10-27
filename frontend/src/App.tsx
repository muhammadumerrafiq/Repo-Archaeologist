import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { StyleguidePage } from './pages/StyleguidePage';
import { LandingPage } from './pages/LandingPage';
import { ResultsDashboard } from './pages/ResultsDashboard';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/styleguide" element={<StyleguidePage />} />
        <Route path="/analyze" element={<ResultsDashboard />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
