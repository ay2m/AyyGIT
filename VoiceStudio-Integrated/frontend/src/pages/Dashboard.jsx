import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useVoiceStore } from '../store/voiceStore';
import { FiUpload, FiMerge2, FiVolume2, FiSettings, FiBarChart2 } from 'react-icons/fi';
import '../styles/Dashboard.css';

export default function Dashboard() {
  const navigate = useNavigate();
  const { databaseStats, getDatabaseStats, voices, fetchVoices } = useVoiceStore();

  useEffect(() => {
    getDatabaseStats();
    fetchVoices(null, null, 0, 5);
  }, []);

  const features = [
    {
      icon: FiUpload,
      title: 'Create Voice',
      description: 'Upload audio and create new voice models',
      action: () => navigate('/voices')
    },
    {
      icon: FiMerge2,
      title: 'Merge Voices',
      description: 'Blend multiple voices into one',
      action: () => navigate('/merge')
    },
    {
      icon: FiVolume2,
      title: 'Text to Speech',
      description: 'Synthesize text with voice models',
      action: () => navigate('/synthesize')
    },
    {
      icon: FiSettings,
      title: 'Manage Voices',
      description: 'View and manage all voice models',
      action: () => navigate('/voices')
    }
  ];

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>🎤 VoiceStudio</h1>
        <p>Advanced AI Voice Management Platform</p>
      </header>

      {databaseStats && (
        <section className="stats-grid">
          <div className="stat-card">
            <FiBarChart2 className="stat-icon" />
            <h3>Total Voices</h3>
            <p className="stat-value">{databaseStats.total_voices}</p>
          </div>
          <div className="stat-card">
            <span className="stat-icon">📝</span>
            <h3>Original</h3>
            <p className="stat-value">{databaseStats.original_voices}</p>
          </div>
          <div className="stat-card">
            <span className="stat-icon">🔀</span>
            <h3>Merged</h3>
            <p className="stat-value">{databaseStats.merged_voices}</p>
          </div>
          <div className="stat-card">
            <span className="stat-icon">🎭</span>
            <h3>Cloned</h3>
            <p className="stat-value">{databaseStats.cloned_voices}</p>
          </div>
        </section>
      )}

      <section className="features-grid">
        <h2>Quick Actions</h2>
        <div className="features">
          {features.map((feature, idx) => {
            const Icon = feature.icon;
            return (
              <button
                key={idx}
                className="feature-card"
                onClick={feature.action}
              >
                <Icon className="feature-icon" />
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </button>
            );
          })}
        </div>
      </section>

      {voices.length > 0 && (
        <section className="recent-voices">
          <h2>Recent Voices</h2>
          <div className="voices-preview">
            {voices.slice(0, 3).map((voice) => (
              <div
                key={voice.id}
                className="voice-preview-card"
                onClick={() => navigate(`/voices/${voice.id}`)}
              >
                <div className="voice-info">
                  <h4>{voice.name}</h4>
                  <p className="voice-lang">
                    {voice.language.toUpperCase()} • {voice.voice_type}
                  </p>
                  <p className="voice-quality">
                    Quality: {Math.round(voice.quality_score)}/100
                  </p>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
