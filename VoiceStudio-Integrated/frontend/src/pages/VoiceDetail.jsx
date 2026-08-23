import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useVoiceStore } from '../store/voiceStore';
import VoicePlayer from '../components/VoicePlayer';
import SynthesisPanel from '../components/SynthesisPanel';
import {
  FiDownload,
  FiTrash2,
  FiArrowLeft,
  FiInfo,
  FiHistory,
  FiMerge2
} from 'react-icons/fi';
import '../styles/VoiceDetail.css';

export default function VoiceDetail() {
  const { voiceId } = useParams();
  const navigate = useNavigate();
  const {
    selectedVoice,
    getVoiceDetails,
    deleteVoice,
    downloadVoiceAudio,
    getSynthesisHistory,
    synthesisHistory,
    loading,
    error
  } = useVoiceStore();

  const [activeTab, setActiveTab] = useState('info');
  const [deleteConfirm, setDeleteConfirm] = useState(false);

  useEffect(() => {
    getVoiceDetails(voiceId);
    getSynthesisHistory(voiceId);
  }, [voiceId]);

  const handleDelete = async () => {
    try {
      await deleteVoice(voiceId);
      navigate('/voices');
    } catch (err) {
      console.error('Delete failed:', err);
    }
  };

  const handleDownload = async () => {
    try {
      await downloadVoiceAudio(voiceId);
    } catch (err) {
      console.error('Download failed:', err);
    }
  };

  if (loading) return <div className="loading">Loading voice details...</div>;
  if (!selectedVoice) return <div className="error">Voice not found</div>;

  return (
    <div className="voice-detail">
      <div className="detail-header">
        <button
          className="btn btn-ghost"
          onClick={() => navigate('/voices')}
        >
          <FiArrowLeft /> Back
        </button>
        <h1>{selectedVoice.name}</h1>
        <div className="header-actions">
          <button
            className="btn btn-secondary"
            onClick={handleDownload}
            title="Download audio"
          >
            <FiDownload />
          </button>
          <button
            className="btn btn-secondary"
            onClick={() => navigate('/merge', { state: { preSelected: voiceId } })}
            title="Merge with other voices"
          >
            <FiMerge2 />
          </button>
          <button
            className="btn btn-danger"
            onClick={() => setDeleteConfirm(true)}
            title="Delete voice"
          >
            <FiTrash2 />
          </button>
        </div>
      </div>

      {deleteConfirm && (
        <div className="confirmation-modal">
          <div className="modal-content">
            <p>Are you sure you want to delete "{selectedVoice.name}"?</p>
            <div className="modal-actions">
              <button
                className="btn btn-secondary"
                onClick={() => setDeleteConfirm(false)}
              >
                Cancel
              </button>
              <button
                className="btn btn-danger"
                onClick={handleDelete}
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'info' ? 'active' : ''}`}
          onClick={() => setActiveTab('info')}
        >
          <FiInfo /> Information
        </button>
        <button
          className={`tab ${activeTab === 'player' ? 'active' : ''}`}
          onClick={() => setActiveTab('player')}
        >
          🎵 Player
        </button>
        <button
          className={`tab ${activeTab === 'synthesis' ? 'active' : ''}`}
          onClick={() => setActiveTab('synthesis')}
        >
          🎤 Synthesize
        </button>
        <button
          className={`tab ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          <FiHistory /> History
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'info' && (
          <div className="info-panel">
            <div className="info-grid">
              <div className="info-item">
                <label>Language</label>
                <p>{selectedVoice.language.toUpperCase()}</p>
              </div>
              <div className="info-item">
                <label>Voice Type</label>
                <p>{selectedVoice.voice_type}</p>
              </div>
              <div className="info-item">
                <label>Quality Score</label>
                <div className="quality-bar">
                  <div
                    className="quality-fill"
                    style={{ width: `${selectedVoice.quality_score}%` }}
                  />
                </div>
                <p>{Math.round(selectedVoice.quality_score)}/100</p>
              </div>
              <div className="info-item">
                <label>Duration</label>
                <p>{selectedVoice.duration.toFixed(2)}s</p>
              </div>
              <div className="info-item">
                <label>Sample Rate</label>
                <p>{selectedVoice.sample_rate} Hz</p>
              </div>
              <div className="info-item">
                <label>Created</label>
                <p>{new Date(selectedVoice.created_at).toLocaleDateString()}</p>
              </div>
            </div>
            {selectedVoice.description && (
              <div className="description">
                <h3>Description</h3>
                <p>{selectedVoice.description}</p>
              </div>
            )}
            {selectedVoice.tags?.length > 0 && (
              <div className="tags">
                <h3>Tags</h3>
                <div className="tag-list">
                  {selectedVoice.tags.map((tag) => (
                    <span key={tag} className="tag">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'player' && (
          <div className="player-panel">
            <VoicePlayer voiceId={voiceId} />
          </div>
        )}

        {activeTab === 'synthesis' && (
          <div className="synthesis-panel">
            <SynthesisPanel voiceId={voiceId} voiceName={selectedVoice.name} />
          </div>
        )}

        {activeTab === 'history' && (
          <div className="history-panel">
            <h3>Synthesis History</h3>
            {synthesisHistory.length > 0 ? (
              <div className="history-list">
                {synthesisHistory.map((item, idx) => (
                  <div key={idx} className="history-item">
                    <div className="history-text">
                      <p className="text-content">"{item.text}"</p>
                      <p className="text-meta">
                        {item.language.toUpperCase()} • {item.duration?.toFixed(2)}s
                      </p>
                    </div>
                    <p className="text-date">
                      {new Date(item.generated_at).toLocaleDateString()}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="empty">No synthesis history yet</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
