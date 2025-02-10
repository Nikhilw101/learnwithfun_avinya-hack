import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';

// Import your page components (you can create these components in separate files)
import SignupPage from './components/signup';
import LoginPage from './components/login';
import Dashboard from './components/Dashboardd';
import BaseLevel from './components/BaseLevel'; // Add this import for Base Level page
import AdvancedLevel from './components/AdvancedLevel'; // Add this import for Advanced Level page
import ModerateLevel from './components/ModerateLevel';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<SignupPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/base-level" element={<BaseLevel />} /> {/* Route for Base Level */}
        <Route path="/ModerateLevel" element={<ModerateLevel />} />
        <Route path="/advanced-level" element={<AdvancedLevel />} /> {/* Route for Advanced Level */}
      </Routes>
    </Router>
  );
}

export default App;
