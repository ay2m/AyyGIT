import React, { useState } from 'react';
import '../styles/CloningHistory.css';

export default function CloningHistory({ selectedVoiceId, voices, history, clonedVoices, loading }) {
  const [selectedTab, setSelectedTab] = useState('lineage');
  const selectedVoice = voices.find((v) => v.id === selectedVoiceId);

  if (!selectedVoiceId) {
    return (
      <div className="cloning-history">
        <div className="empty-state">
          <p>Select a voice to view its cloning history and lineage.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="cloning-history">
        <div className="loading-state">
          <p>Loading cloning history...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="cloning-history">
      <div className="history-header">
        <h2>Cloning History & Lineage</h2>
        {selectedVoice && (
          <div className="voice-summary">
            <span className="voice-name">{selectedVoice.name}</span>
            <span className="voice-type">({selectedVoice.voice_type})</span>
          </div>
        )}
      </div>

      <div className="history-tabs">
        <button
          className={`tab-btn ${selectedTab === 'lineage' ? 'active' : ''}`}
          onClick={() => setSelectedTab('lineage')}
        >
          📊 Cloning Lineage
        </button>
        <button
          className={`tab-btn ${selectedTab === 'clones' ? 'active' : ''}`}
          onClick={() => setSelectedTab('clones')}
        >
          🎯 Cloned Voices
        </button>
      </div>

      {selectedTab === 'lineage' && (
        <div className="lineage-section">
          {history ? (
            <div className="lineage-card">
              <h3>Cloning Information</h3>
              <div className="lineage-content">
                <div className="lineage-item">
                  <span className="label">Current Voice:</span>
                  <span className="value">{selectedVoice?.name}</span>
                </div>
                <div className="lineage-item">
                  <span className="label">Cloning Method:</span>
                  <span className="value badge">{history.cloning_method}</span>
                </div>
                <div className="lineage-item">
                  <span className="label">Intensity:</span>
                  <span className="value">{history.intensity.toFixed(2)}</span>
                </div>

                {history.cloning_parameters && (
                  <>
                    <h4>Voice Modifications</h4>
                    <div className="parameters-grid">
                      <div className="param-item">
                        <span className="param-label">Pitch Shift:</span>
                        <span className="param-value">
                          {history.cloning_parameters.pitch_shift > 0 ? '+' : ''}
                          {history.cloning_parameters.pitch_shift} semitones
                        </span>
                      </div>
                      <div className="param-item">
                        <span className="param-label">Tempo Factor:</span>
                        <span className="param-value">
                          {history.cloning_parameters.tempo_factor.toFixed(2)}x
                        </span>
                      </div>
                      <div className="param-item">
                        <span className="param-label">Formant Shift:</span>
                        <span className="param-value">
                          {history.cloning_parameters.formant_shift > 0 ? '+' : ''}
                          {history.cloning_parameters.formant_shift.toFixed(2)}
                        </span>
                      </div>
                      <div className="param-item">
                        <span className="param-label">Breathiness:</span>
                        <span className="param-value">
                          {history.cloning_parameters.breathiness.toFixed(2)}
                        </span>
                      </div>
                      <div className="param-item">
                        <span className="param-label">Robustness:</span>
                        <span className="param-value">
                          {history.cloning_parameters.robustness.toFixed(2)}
                        </span>
                      </div>
                    </div>
                  </>
                )}

                {history.created_at && (
                  <div className="lineage-item">
                    <span className="label">Cloned On:</span>
                    <span className="value">{new Date(history.created_at).toLocaleString()}</span>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="no-data">
              <p>No cloning history found for this voice.</p>
              <p>This voice hasn't been cloned yet or is an original voice.</p>
            </div>
          )}
        </div>
      )}

      {selectedTab === 'clones' && (
        <div className="clones-section">
          {clonedVoices && clonedVoices.length > 0 ? (
            <div className="clones-list">
              <p className="clones-count">
                {clonedVoices.length} voice{clonedVoices.length !== 1 ? 's' : ''} cloned from this voice
              </p>
              <div className="clones-grid">
                {clonedVoices.map((clone) => (
                  <div key={clone.id} className="clone-card">
                    <div className="clone-header">
                      <h4>{clone.name}</h4>
                      <span className="quality-badge">
                        {Math.round(clone.quality_score)}/100
                      </span>
                    </div>
                    <div className="clone-info">
                      <div className="info-row">
                        <span className="label">Type:</span>
                        <span>{clone.voice_type}</span>
                      </div>
                      <div className="info-row">
                        <span className="label">Language:</span>
                        <span>{clone.language.toUpperCase()}</span>
                      </div>
                      {clone.created_at && (
                        <div className="info-row">
                          <span className="label">Created:</span>
                          <span>{new Date(clone.created_at).toLocaleDateString()}</span>
                        </div>
                      )}
                    </div>
                    <div className="clone-actions">
                      <button className="btn btn-small">
                        👁️ View
                      </button>
                      <button className="btn btn-small">
                        🎵 Listen
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="no-data">
              <p>No voices have been cloned from this voice yet.</p>
              <p>Start cloning to create variations and new voices.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
