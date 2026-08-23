import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useVoiceStore } from '../store/voiceStore';
import { FiArrowLeft, FiPlus, FiX } from 'react-icons/fi';
import '../styles/VoiceMerge.css';

export default function VoiceMerge() {
  const navigate = useNavigate();
  const { voices, fetchVoices, mergeVoices, loading, error } = useVoiceStore();
  const [selectedVoices, setSelectedVoices] = useState([]);
  const [weights, setWeights] = useState([]);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [language, setLanguage] = useState('ar');

  useEffect(() => {
    fetchVoices();
  }, []);

  const handleSelectVoice = (voiceId) => {
    if (selectedVoices.includes(voiceId)) {
      const idx = selectedVoices.indexOf(voiceId);
      setSelectedVoices(selectedVoices.filter((_, i) => i !== idx));
      setWeights(weights.filter((_, i) => i !== idx));
    } else if (selectedVoices.length < 5) {
      setSelectedVoices([...selectedVoices, voiceId]);
      setWeights([...weights, 1.0 / (selectedVoices.length + 1)]);
    }
  };

  const handleWeightChange = (idx, value) => {
    const newWeights = [...weights];
    newWeights[idx] = parseFloat(value) || 0;
    setWeights(newWeights);
  };

  const normalizeWeights = () => {
    const sum = weights.reduce((a, b) => a + b, 0);
    if (sum > 0) {
      setWeights(weights.map((w) => w / sum));
    }
  };

  const handleMerge = async () => {
    if (!name.trim()) {
      alert('Please enter a name for the merged voice');
      return;
    }

    if (selectedVoices.length < 2) {
      alert('Select at least 2 voices to merge');
      return;
    }

    try {
      normalizeWeights();
      await mergeVoices(selectedVoices, weights, name, description, language);
      navigate('/voices');
    } catch (err) {
      console.error('Merge failed:', err);
    }
  };

  const getSelectedVoiceDetails = () => {
    return selectedVoices.map((id) =>
      voices.find((v) => v.id === id)
    ).filter(Boolean);
  };

  return (
    <div className="voice-merge">
      <div className="merge-header">
        <button className="btn btn-ghost" onClick={() => navigate('/voices')}>
          <FiArrowLeft /> Back
        </button>
        <h1>Merge Voices</h1>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="merge-container">
        <div className="merge-panel">
          <h2>Available Voices</h2>
          <div className="voices-list">
            {voices.map((voice) => (
              <div
                key={voice.id}
                className={`voice-item ${
                  selectedVoices.includes(voice.id) ? 'selected' : ''
                }`}
                onClick={() => handleSelectVoice(voice.id)}
              >
                <div className="voice-name">{voice.name}</div>
                <div className="voice-meta">
                  {voice.language.toUpperCase()} • Quality: {Math.round(voice.quality_score)}/100
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="merge-panel config-panel">
          <h2>Merge Configuration</h2>

          <div className="selected-voices">
            <h3>Selected Voices ({selectedVoices.length}/5)</h3>
            {selectedVoices.length > 0 ? (
              <div className="selected-list">
                {getSelectedVoiceDetails().map((voice, idx) => (
                  <div key={voice.id} className="selected-item">
                    <div className="selected-info">
                      <p className="selected-name">{voice.name}</p>
                    </div>
                    <div className="weight-control">
                      <label>Weight</label>
                      <input
                        type="number"
                        min="0"
                        max="1"
                        step="0.1"
                        value={weights[idx]?.toFixed(2) || 0}
                        onChange={(e) => handleWeightChange(idx, e.target.value)}
                      />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="empty">No voices selected</p>
            )}
          </div>

          <div className="merge-form">
            <div className="form-group">
              <label>Merged Voice Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g., Mixed Voice 1"
              />
            </div>

            <div className="form-group">
              <label>Description (optional)</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe the merged voice..."
              />
            </div>

            <div className="form-group">
              <label>Language</label>
              <select value={language} onChange={(e) => setLanguage(e.target.value)}>
                <option value="ar">Arabic</option>
                <option value="en">English</option>
                <option value="fr">French</option>
                <option value="es">Spanish</option>
              </select>
            </div>

            <div className="form-actions">
              <button
                className="btn btn-primary"
                onClick={handleMerge}
                disabled={loading || selectedVoices.length < 2}
              >
                {loading ? 'Merging...' : 'Merge Voices'}
              </button>
              <button
                className="btn btn-secondary"
                onClick={() => {
                  setSelectedVoices([]);
                  setWeights([]);
                }}
              >
                Clear
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
