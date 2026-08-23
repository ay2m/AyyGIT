import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { FiHome, FiMusic, FiSettings } from 'react-icons/fi';
import '../styles/Navbar.css';

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();

  const isActive = (path) => {
    if (path === '/' && location.pathname === '/') return true;
    if (path !== '/' && location.pathname.startsWith(path)) return true;
    return false;
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-brand">
          <h1>🎤 VoiceStudio</h1>
        </div>
        <div className="navbar-menu">
          <button
            className={`nav-link ${isActive('/') ? 'active' : ''}`}
            onClick={() => navigate('/')}
          >
            <FiHome /> Dashboard
          </button>
          <button
            className={`nav-link ${isActive('/voices') ? 'active' : ''}`}
            onClick={() => navigate('/voices')}
          >
            <FiMusic /> Voices
          </button>
          <button
            className={`nav-link ${isActive('/merge') ? 'active' : ''}`}
            onClick={() => navigate('/merge')}
          >
            🔀 Merge
          </button>
          <button
            className={`nav-link ${isActive('/synthesize') ? 'active' : ''}`}
            onClick={() => navigate('/synthesize')}
          >
            🎤 Synthesize
          </button>
          <button
            className={`nav-link ${isActive('/settings') ? 'active' : ''}`}
            onClick={() => navigate('/settings')}
          >
            <FiSettings /> Settings
          </button>
        </div>
      </div>
    </nav>
  );
}
