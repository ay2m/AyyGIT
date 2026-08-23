import React from 'react';
import '../styles/CloningResult.css';

export default function CloningResult({ result }) {
  if (!result) return null;

  const handleDownload = async () => {
    try {
      const response = await fetch(`http://localhost:8000/voices/${result.cloned_voice_id}/audio`, {
        responseType: 'blob'
      });

      if (!response.ok) {
        throw new Error('Failed to download audio');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${result.clone_name || 'cloned_voice'}.wav`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch (error) {
      console.error('Download failed:', error);
      alert('Failed to download audio');
    }
  };

  return (
    <div className="cloning-result">
      <div className="result-container">
        <h2>✅ Voice Successfully Cloned!</h2>

        <div className="result-card">
          <div className="result-header">
            <div className="result-title">
              <h3>{result.clone_name}</h3>
              <span className="result-type">Cloned Voice</span>
            </div>
            <div className="result-quality">
              <div className="quality-score">
                <span className="label">Quality</span>
                <span className="value">{Math.round(result.quality_score)}/100</span>
              </div>
            </div>
          </div>

          <div className="result-details">
            <div className="detail-item">
              <span className="label">Clone ID:</span>
              <span className="value">{result.cloned_voice_id}</span>
            </div>
            <div className="detail-item">
              <span className="label">Status:</span>
              <span className="value success">✅ Ready</span>
            </div>
            {result.created_at && (
              <div className="detail-item">
                <span className="label">Created:</span>
                <span className="value">{new Date(result.created_at).toLocaleString()}</span>
              </div>
            )}
          </div>

          {result.audio_url && (
            <div className="audio-preview">
              <h4>Preview Cloned Voice</h4>
              <audio controls className="audio-player">
                <source src={result.audio_url} type="audio/wav" />
                Your browser does not support the audio element.
              </audio>
            </div>
          )}

          <div className="result-actions">
            <button className="btn btn-primary" onClick={handleDownload}>
              📥 Download Audio
            </button>
            <button className="btn btn-secondary" onClick={() => {
              const link = `/voice/${result.cloned_voice_id}`;
              window.location.href = link;
            }}>
              👁️ View Details
            </button>
          </div>
        </div>

        <div className="result-info-box">
          <h4>💡 Next Steps</h4>
          <ul>
            <li>Use the cloned voice for synthesis tasks</li>
            <li>Further refine with additional parameters</li>
            <li>Create variations with different settings</li>
            <li>Export and save your cloned voice</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
