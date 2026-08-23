import React from 'react';
import { FiPlay } from 'react-icons/fi';
import '../styles/VoiceCard.css';

export default function VoiceCard({ voice, onSelect }) {
  const getVoiceTypeIcon = (type) => {
    switch (type) {
      case 'original':
        return '🎙️';
      case 'merged':
        return '🔀';
      case 'cloned':
        return '👥';
      default:
        return '🎤';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="voice-card" onClick={onSelect}>
      <div className="voice-card-header">
        <div className="voice-card-title">
          <span className="voice-type-icon">{getVoiceTypeIcon(voice.voice_type)}</span>
          <h3>{voice.name}</h3>
        </div>
        <button className="play-btn" title="View details">
          <FiPlay />
        </button>
      </div>

      <div className="voice-card-meta">
        <span className="language-badge">{voice.language.toUpperCase()}</span>
        <span className="type-badge">{voice.voice_type}</span>
      </div>

      <div className="voice-card-stats">
        <div className="stat">
          <span className="label">Quality</span>
          <div className="quality-indicator">
            <div className="quality-bar">
              <div className="quality-fill" style={{ width: `${voice.quality_score}%` }} />
            </div>
            <span className="value">{Math.round(voice.quality_score)}/100</span>
          </div>
        </div>

        <div className="stat">
          <span className="label">Duration</span>
          <span className="value">{voice.duration.toFixed(2)}s</span>
        </div>

        <div className="stat">
          <span className="label">Size</span>
          <span className="value">{(voice.file_size / 1024).toFixed(1)} KB</span>
        </div>
      </div>

      {voice.description && (
        <p className="voice-card-description">{voice.description}</p>
      )}

      <div className="voice-card-footer">
        <span className="date">{formatDate(voice.created_at)}</span>
      </div>
    </div>
  );
}
