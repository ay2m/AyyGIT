import React, { useState, useEffect } from 'react';
import { useVoiceStore } from '../store/voiceStore';
import { FiPlay, FiDownload } from 'react-icons/fi';
import '../styles/SynthesisPanel.css';

export default function SynthesisPanel({ voiceId, voiceName }) {
  const { synthesizeVoice, getSynthesisPreview, synthesisResult, loading, error } = useVoiceStore();
  const [text, setText] = useState('');
  const [language, setLanguage] = useState('ar');
  const [preview, setPreview] = useState(null);

  useEffect(() => {
    if (voiceId && text) {
      const timer = setTimeout(() => {
        handlePreview();
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [text, language, voiceId]);

  const handlePreview = async () => {
    try {
      const result = await getSynthesisPreview(text, voiceId, language);
      setPreview(result);
    } catch (err) {
      console.error('Preview failed:', err);
    }
  };

  const handleSynthesize = async () => {
    if (!text.trim()) {
      alert('Please enter text to synthesize');
      return;
    }

    try {
      await synthesizeVoice(text, voiceId, language);
    } catch (err) {
      console.error('Synthesis failed:', err);
    }
  };

  return (
    <div className="synthesis-panel">
      <h3>Synthesize with {voiceName}</h3>

      <div className="synthesis-controls">
        <div className="form-group">
          <label>Text to Synthesize</label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter text to synthesize..."
            maxLength="1000"
            rows="4"
            disabled={loading}
          />
          <div className="text-stats">
            <span>{text.length}/1000 characters</span>
            <span>{text.split(/\s+/).filter(Boolean).length} words</span>
          </div>
        </div>

        <div className="form-group">
          <label>Language</label>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            disabled={loading}
          >
            <option value="ar">العربية (Arabic)</option>
            <option value="en">English</option>
            <option value="fr">Français (French)</option>
            <option value="es">Español (Spanish)</option>
          </select>
        </div>

        <button
          className="btn btn-primary"
          onClick={handleSynthesize}
          disabled={loading || !text.trim()}
        >
          {loading ? 'Synthesizing...' : '🎤 Synthesize'}
        </button>
      </div>

      {preview && (
        <div className="preview-info">
          <h4>Preview</h4>
          <div className="preview-grid">
            <div className="preview-item">
              <label>Estimated Duration</label>
              <p>{preview.estimated_duration_seconds?.toFixed(2) || 'N/A'}s</p>
            </div>
            <div className="preview-item">
              <label>Word Count</label>
              <p>{preview.word_count || 0}</p>
            </div>
            <div className="preview-item">
              <label>Voice Quality</label>
              <p>{preview.voice_quality?.toFixed(0) || 'N/A'}/100</p>
            </div>
            <div className="preview-item">
              <label>Language Match</label>
              <p className={preview.language_match ? 'match' : 'no-match'}>
                {preview.language_match ? '✅ Matched' : '⚠️ Mismatch'}
              </p>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="error-message">
          <p>Error: {error}</p>
        </div>
      )}

      {synthesisResult && (
        <div className="synthesis-result">
          <h4>Generated Audio</h4>
          <audio
            src={synthesisResult.audioUrl}
            controls
            className="audio-player"
          />
          <p className="generated-text">"{synthesisResult.text}"</p>
          <a
            href={synthesisResult.audioUrl}
            download={`synthesis_${voiceId}_${Date.now()}.wav`}
            className="btn btn-secondary"
          >
            <FiDownload /> Download
          </a>
        </div>
      )}
    </div>
  );
}
