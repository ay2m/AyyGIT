import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useVoiceStore } from '../store/voiceStore';
import VoiceUpload from '../components/VoiceUpload';
import VoiceCard from '../components/VoiceCard';
import { FiFilter, FiRefreshCw } from 'react-icons/fi';
import '../styles/VoiceLibrary.css';

export default function VoiceLibrary() {
  const navigate = useNavigate();
  const { voices, loading, fetchVoices, error } = useVoiceStore();
  const [language, setLanguage] = useState(null);
  const [voiceType, setVoiceType] = useState(null);
  const [skip, setSkip] = useState(0);
  const [showUpload, setShowUpload] = useState(false);

  useEffect(() => {
    fetchVoices(language, voiceType, skip);
  }, [language, voiceType, skip]);

  const handleRefresh = () => {
    fetchVoices(language, voiceType, skip);
  };

  const languages = ['ar', 'en', 'fr', 'es'];
  const voiceTypes = ['original', 'merged', 'cloned'];

  return (
    <div className="voice-library">
      <div className="library-header">
        <h1>Voice Library</h1>
        <button
          className="btn btn-primary"
          onClick={() => setShowUpload(true)}
        >
          + Upload Voice
        </button>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="filters-section">
        <div className="filter-group">
          <select
            value={language || ''}
            onChange={(e) => {
              setLanguage(e.target.value || null);
              setSkip(0);
            }}
            className="filter-select"
          >
            <option value="">All Languages</option>
            {languages.map((lang) => (
              <option key={lang} value={lang}>
                {lang.toUpperCase()}
              </option>
            ))}
          </select>

          <select
            value={voiceType || ''}
            onChange={(e) => {
              setVoiceType(e.target.value || null);
              setSkip(0);
            }}
            className="filter-select"
          >
            <option value="">All Types</option>
            {voiceTypes.map((type) => (
              <option key={type} value={type}>
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </option>
            ))}
          </select>

          <button
            className="btn btn-secondary"
            onClick={handleRefresh}
            disabled={loading}
          >
            <FiRefreshCw /> Refresh
          </button>
        </div>
      </div>

      {showUpload && (
        <div className="upload-modal-overlay">
          <div className="upload-modal">
            <button
              className="close-btn"
              onClick={() => setShowUpload(false)}
            >
              ✕
            </button>
            <VoiceUpload
              onSuccess={() => {
                setShowUpload(false);
                handleRefresh();
              }}
            />
          </div>
        </div>
      )}

      {loading && <div className="loading">Loading voices...</div>}

      {voices.length > 0 ? (
        <>
          <div className="voices-grid">
            {voices.map((voice) => (
              <VoiceCard
                key={voice.id}
                voice={voice}
                onSelect={() => navigate(`/voices/${voice.id}`)}
              />
            ))}
          </div>

          <div className="pagination">
            <button
              disabled={skip === 0}
              onClick={() => setSkip(Math.max(0, skip - 10))}
              className="btn btn-secondary"
            >
              Previous
            </button>
            <span>Page {Math.floor(skip / 10) + 1}</span>
            <button
              disabled={voices.length < 10}
              onClick={() => setSkip(skip + 10)}
              className="btn btn-secondary"
            >
              Next
            </button>
          </div>
        </>
      ) : (
        <div className="empty-state">
          <p>No voices yet. Upload your first voice to get started!</p>
          <button
            className="btn btn-primary"
            onClick={() => setShowUpload(true)}
          >
            Upload Voice
          </button>
        </div>
      )}
    </div>
  );
}
