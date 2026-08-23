import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useVoiceStore } from '../store/voiceStore';
import { FiArrowLeft } from 'react-icons/fi';
import CloningSettings from '../components/CloningSettings';
import CloningResult from '../components/CloningResult';
import CloningHistory from '../components/CloningHistory';
import '../styles/VoiceCloning.css';

export default function VoiceCloning() {
  const navigate = useNavigate();
  const {
    voices,
    fetchVoices,
    cloneVoice,
    getCloningHistory,
    getClonedVoices,
    cloningResult,
    cloningHistory,
    clonedVoices,
    loading,
    error,
    clearCloningResult
  } = useVoiceStore();

  const [selectedVoiceId, setSelectedVoiceId] = useState('');
  const [cloneName, setCloneName] = useState('');
  const [text, setText] = useState('');
  const [language, setLanguage] = useState('ar');
  const [cloningParams, setCloningParams] = useState({
    method: 'basic',
    intensity: 0.7,
    pitch_shift: 0,
    tempo_factor: 1.0,
    formant_shift: 0,
    breathiness: 0.3,
    robustness: 0.5
  });
  const [activeTab, setActiveTab] = useState('clone');
  const [showHistory, setShowHistory] = useState(false);

  useEffect(() => {
    fetchVoices();
  }, []);

  useEffect(() => {
    if (showHistory && selectedVoiceId) {
      getCloningHistory(selectedVoiceId);
      getClonedVoices(selectedVoiceId);
    }
  }, [showHistory, selectedVoiceId]);

  const handleClone = async () => {
    if (!selectedVoiceId || !text.trim() || !cloneName.trim()) {
      alert('Please select a voice, enter text, and provide a clone name');
      return;
    }

    try {
      await cloneVoice(selectedVoiceId, text, cloneName, language, cloningParams);
    } catch (err) {
      console.error('Cloning failed:', err);
    }
  };

  const selectedVoice = voices.find((v) => v.id === selectedVoiceId);

  return (
    <div className="voice-cloning">
      <div className="cloning-header">
        <button className="btn btn-ghost" onClick={() => navigate('/')}>
          <FiArrowLeft /> Back
        </button>
        <h1>Voice Cloning Studio</h1>
        <div className="header-actions">
          <button
            className={`btn ${showHistory ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setShowHistory(!showHistory)}
          >
            {showHistory ? '🎯 Clone' : '📋 History'}
          </button>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {!showHistory ? (
        <div className="cloning-container">
          <div className="cloning-panel config-panel">
            <h2>Configuration</h2>

            <div className="form-group">
              <label>Select Source Voice</label>
              <select
                value={selectedVoiceId}
                onChange={(e) => setSelectedVoiceId(e.target.value)}
                className="voice-select"
              >
                <option value="">Choose a voice to clone...</option>
                {voices.map((voice) => (
                  <option key={voice.id} value={voice.id}>
                    {voice.name} ({voice.voice_type}) - {voice.language.toUpperCase()}
                  </option>
                ))}
              </select>
            </div>

            {selectedVoice && (
              <div className="voice-info-card">
                <h3>{selectedVoice.name}</h3>
                <div className="info-row">
                  <span>Quality:</span>
                  <span className="quality-badge">
                    {Math.round(selectedVoice.quality_score)}/100
                  </span>
                </div>
                <div className="info-row">
                  <span>Type:</span>
                  <span>{selectedVoice.voice_type}</span>
                </div>
                <div className="info-row">
                  <span>Duration:</span>
                  <span>{selectedVoice.duration.toFixed(2)}s</span>
                </div>
              </div>
            )}

            <div className="form-group">
              <label>Clone Name</label>
              <input
                type="text"
                value={cloneName}
                onChange={(e) => setCloneName(e.target.value)}
                placeholder="Enter a name for your cloned voice..."
                className="text-input"
                maxLength="100"
              />
            </div>

            <div className="form-group">
              <label>Language</label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
              >
                <option value="ar">العربية (Arabic)</option>
                <option value="en">English</option>
                <option value="fr">Français (French)</option>
                <option value="es">Español (Spanish)</option>
              </select>
            </div>
          </div>

          <div className="cloning-panel text-panel">
            <h2>Reference Text</h2>
            <p className="panel-description">
              Provide text to guide the cloning process. This helps establish the vocal characteristics.
            </p>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Enter reference text for cloning..."
              className="text-input"
              maxLength="1000"
            />
            <div className="text-stats">
              <span>{text.length}/1000 characters</span>
              <span>{text.split(/\s+/).filter(Boolean).length} words</span>
            </div>

            <button
              className="btn btn-primary btn-large"
              onClick={handleClone}
              disabled={loading || !selectedVoiceId || !text.trim() || !cloneName.trim()}
            >
              {loading ? 'Creating Clone...' : '✨ Clone Voice'}
            </button>
          </div>

          <CloningSettings params={cloningParams} onParamsChange={setCloningParams} />

          {cloningResult && <CloningResult result={cloningResult} />}
        </div>
      ) : (
        <CloningHistory
          selectedVoiceId={selectedVoiceId}
          voices={voices}
          history={cloningHistory}
          clonedVoices={clonedVoices}
          loading={loading}
        />
      )}
    </div>
  );
}
