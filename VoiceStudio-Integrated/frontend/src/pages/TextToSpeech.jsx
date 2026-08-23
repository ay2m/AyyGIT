import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useVoiceStore } from '../store/voiceStore';
import { FiArrowLeft } from 'react-icons/fi';
import '../styles/TextToSpeech.css';

export default function TextToSpeech() {
  const navigate = useNavigate();
  const {
    voices,
    fetchVoices,
    synthesizeVoice,
    getSynthesisPreview,
    synthesisResult,
    loading,
    error
  } = useVoiceStore();

  const [selectedVoiceId, setSelectedVoiceId] = useState('');
  const [text, setText] = useState('');
  const [language, setLanguage] = useState('ar');
  const [preview, setPreview] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    fetchVoices();
  }, []);

  useEffect(() => {
    if (selectedVoiceId && text) {
      const timer = setTimeout(() => {
        handlePreview();
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [text, selectedVoiceId, language]);

  const handlePreview = async () => {
    try {
      const result = await getSynthesisPreview(text, selectedVoiceId, language);
      setPreview(result);
    } catch (err) {
      console.error('Preview failed:', err);
    }
  };

  const handleSynthesize = async () => {
    if (!selectedVoiceId || !text.trim()) {
      alert('Please select a voice and enter text');
      return;
    }

    try {
      await synthesizeVoice(text, selectedVoiceId, language);
    } catch (err) {
      console.error('Synthesis failed:', err);
    }
  };

  const selectedVoice = voices.find((v) => v.id === selectedVoiceId);

  return (
    <div className="text-to-speech">
      <div className="tts-header">
        <button className="btn btn-ghost" onClick={() => navigate('/')}>
          <FiArrowLeft /> Back
        </button>
        <h1>Text to Speech</h1>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="tts-container">
        <div className="tts-panel">
          <h2>Configuration</h2>

          <div className="form-group">
            <label>Select Voice</label>
            <select
              value={selectedVoiceId}
              onChange={(e) => setSelectedVoiceId(e.target.value)}
              className="voice-select"
            >
              <option value="">Choose a voice...</option>
              {voices.map((voice) => (
                <option key={voice.id} value={voice.id}>
                  {voice.name} ({voice.language.toUpperCase()})
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

        <div className="tts-panel text-panel">
          <h2>Text Input</h2>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter text to synthesize..."
            className="text-input"
            maxLength="1000"
          />
          <div className="text-stats">
            <span>{text.length}/1000 characters</span>
            <span>{text.split(/\s+/).filter(Boolean).length} words</span>
          </div>

          <button
            className="btn btn-primary btn-large"
            onClick={handleSynthesize}
            disabled={
              loading || !selectedVoiceId || !text.trim()
            }
          >
            {loading ? 'Synthesizing...' : '🎤 Synthesize'}
          </button>
        </div>

        <div className="tts-panel preview-panel">
          <h2>Preview</h2>

          {preview && (
            <div className="preview-info">
              <div className="preview-item">
                <label>Estimated Duration</label>
                <p>{preview.estimated_duration_seconds.toFixed(2)}s</p>
              </div>
              <div className="preview-item">
                <label>Word Count</label>
                <p>{preview.word_count}</p>
              </div>
              <div className="preview-item">
                <label>Voice Quality</label>
                <p>{preview.voice_quality.toFixed(0)}/100</p>
              </div>
              <div className="preview-item">
                <label>Language Match</label>
                <p className={preview.language_match ? 'match' : 'no-match'}>
                  {preview.language_match ? '✅ Matched' : '⚠️ Mismatch'}
                </p>
              </div>
            </div>
          )}

          {synthesisResult && (
            <div className="synthesis-result">
              <h3>Generated Audio</h3>
              <audio
                src={synthesisResult.audioUrl}
                controls
                className="audio-player"
              />
              <p className="generated-text">"{synthesisResult.text}"</p>
              <a
                href={synthesisResult.audioUrl}
                download={`synthesis_${Date.now()}.wav`}
                className="btn btn-secondary"
              >
                📥 Download
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
