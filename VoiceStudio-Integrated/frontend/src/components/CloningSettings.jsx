import React from 'react';
import '../styles/CloningSettings.css';

export default function CloningSettings({ params, onParamsChange }) {
  const handleParamChange = (key, value) => {
    onParamsChange({
      ...params,
      [key]: parseFloat(value) || value
    });
  };

  return (
    <div className="cloning-panel settings-panel">
      <h2>⚙️ Advanced Settings</h2>
      <p className="panel-description">
        Fine-tune the voice cloning parameters to achieve the desired result.
      </p>

      <div className="settings-tabs">
        <div className="settings-section">
          <h3>Cloning Method</h3>
          <div className="form-group">
            <label>Method</label>
            <select
              value={params.method}
              onChange={(e) => handleParamChange('method', e.target.value)}
              className="settings-select"
            >
              <option value="basic">Basic - Feature Interpolation</option>
              <option value="advanced">Advanced - Speaker Embedding</option>
            </select>
            <p className="setting-hint">
              {params.method === 'basic'
                ? 'Uses simple feature blending for faster processing'
                : 'Uses advanced speaker embeddings for higher quality clones'}
            </p>
          </div>
        </div>

        <div className="settings-section">
          <h3>Cloning Parameters</h3>

          <div className="form-group">
            <label>
              Clone Intensity: <span className="value">{params.intensity.toFixed(2)}</span>
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={params.intensity}
              onChange={(e) => handleParamChange('intensity', e.target.value)}
              className="slider"
            />
            <p className="setting-hint">
              Lower values (0.5) = more variation from original | Higher values (1.0) = closer to original
            </p>
          </div>

          <div className="form-group">
            <label>
              Pitch Shift: <span className="value">{params.pitch_shift > 0 ? '+' : ''}{params.pitch_shift}</span> semitones
            </label>
            <input
              type="range"
              min="-12"
              max="12"
              step="1"
              value={params.pitch_shift}
              onChange={(e) => handleParamChange('pitch_shift', e.target.value)}
              className="slider"
            />
            <p className="setting-hint">
              -12 (lower) to +12 (higher) semitones
            </p>
          </div>

          <div className="form-group">
            <label>
              Tempo Factor: <span className="value">{params.tempo_factor.toFixed(2)}x</span>
            </label>
            <input
              type="range"
              min="0.5"
              max="2.0"
              step="0.1"
              value={params.tempo_factor}
              onChange={(e) => handleParamChange('tempo_factor', e.target.value)}
              className="slider"
            />
            <p className="setting-hint">
              0.5x (slower) to 2.0x (faster) playback speed
            </p>
          </div>

          <div className="form-group">
            <label>
              Formant Shift: <span className="value">{params.formant_shift > 0 ? '+' : ''}{params.formant_shift.toFixed(2)}</span>
            </label>
            <input
              type="range"
              min="-1"
              max="1"
              step="0.1"
              value={params.formant_shift}
              onChange={(e) => handleParamChange('formant_shift', e.target.value)}
              className="slider"
            />
            <p className="setting-hint">
              Shifts formant frequencies for different voice characteristics
            </p>
          </div>
        </div>

        <div className="settings-section">
          <h3>Voice Characteristics</h3>

          <div className="form-group">
            <label>
              Breathiness: <span className="value">{params.breathiness.toFixed(2)}</span>
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={params.breathiness}
              onChange={(e) => handleParamChange('breathiness', e.target.value)}
              className="slider"
            />
            <p className="setting-hint">
              0 (no breath) to 1 (very breathy) - adds air and subtle details
            </p>
          </div>

          {params.method === 'advanced' && (
            <div className="form-group">
              <label>
                Robustness: <span className="value">{params.robustness.toFixed(2)}</span>
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={params.robustness}
                onChange={(e) => handleParamChange('robustness', e.target.value)}
                className="slider"
              />
              <p className="setting-hint">
                Higher values provide more stable, consistent clones (advanced method only)
              </p>
            </div>
          )}
        </div>

        <div className="settings-section preset-section">
          <h3>Quick Presets</h3>
          <div className="preset-buttons">
            <button
              className="preset-btn"
              onClick={() => {
                onParamsChange({
                  method: 'basic',
                  intensity: 0.9,
                  pitch_shift: 0,
                  tempo_factor: 1.0,
                  formant_shift: 0,
                  breathiness: 0.2,
                  robustness: 0.5
                });
              }}
            >
              🎯 Exact Clone
            </button>
            <button
              className="preset-btn"
              onClick={() => {
                onParamsChange({
                  method: 'advanced',
                  intensity: 0.6,
                  pitch_shift: 3,
                  tempo_factor: 1.1,
                  formant_shift: 0.2,
                  breathiness: 0.4,
                  robustness: 0.7
                });
              }}
            >
              ✨ Variation
            </button>
            <button
              className="preset-btn"
              onClick={() => {
                onParamsChange({
                  method: 'basic',
                  intensity: 0.5,
                  pitch_shift: 5,
                  tempo_factor: 1.2,
                  formant_shift: 0.3,
                  breathiness: 0.5,
                  robustness: 0.4
                });
              }}
            >
              🎨 Creative
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
