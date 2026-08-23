import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useVoiceStore } from '../store/voiceStore';
import { FiArrowLeft, FiDownload, FiCheck, FiAlertCircle } from 'react-icons/fi';
import '../styles/Settings.css';

export default function Settings() {
  const navigate = useNavigate();
  const {
    databaseStats,
    getDatabaseStats,
    backupDatabase,
    verifyDatabase,
    loading,
    error
  } = useVoiceStore();

  const [backupStatus, setBackupStatus] = React.useState(null);
  const [verifyStatus, setVerifyStatus] = React.useState(null);

  useEffect(() => {
    getDatabaseStats();
  }, []);

  const handleBackup = async () => {
    try {
      const result = await backupDatabase();
      setBackupStatus(result);
    } catch (err) {
      console.error('Backup failed:', err);
    }
  };

  const handleVerify = async () => {
    try {
      const result = await verifyDatabase();
      setVerifyStatus(result);
    } catch (err) {
      console.error('Verification failed:', err);
    }
  };

  return (
    <div className="settings">
      <div className="settings-header">
        <button className="btn btn-ghost" onClick={() => navigate('/')}>
          <FiArrowLeft /> Back
        </button>
        <h1>Settings</h1>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="settings-container">
        <section className="settings-section">
          <h2>Database Statistics</h2>
          {databaseStats ? (
            <div className="stats-grid">
              <div className="stat-box">
                <p className="stat-label">Total Voices</p>
                <p className="stat-value">{databaseStats.total_voices}</p>
              </div>
              <div className="stat-box">
                <p className="stat-label">Original Voices</p>
                <p className="stat-value">{databaseStats.original_voices}</p>
              </div>
              <div className="stat-box">
                <p className="stat-label">Merged Voices</p>
                <p className="stat-value">{databaseStats.merged_voices}</p>
              </div>
              <div className="stat-box">
                <p className="stat-label">Cloned Voices</p>
                <p className="stat-value">{databaseStats.cloned_voices}</p>
              </div>
              <div className="stat-box">
                <p className="stat-label">Database Size</p>
                <p className="stat-value">
                  {databaseStats.database_size_mb.toFixed(2)} MB
                </p>
              </div>
            </div>
          ) : (
            <p>Loading statistics...</p>
          )}
        </section>

        <section className="settings-section">
          <h2>Database Management</h2>

          <div className="settings-option">
            <div className="option-content">
              <h3>Create Backup</h3>
              <p>Create a timestamped backup of the database</p>
            </div>
            <button
              className="btn btn-primary"
              onClick={handleBackup}
              disabled={loading}
            >
              <FiDownload /> Backup
            </button>
          </div>

          {backupStatus && (
            <div className="status-message success">
              <FiCheck className="status-icon" />
              <div>
                <p className="status-title">Backup Created</p>
                <p className="status-detail">{backupStatus.backup_name}</p>
              </div>
            </div>
          )}

          <div className="settings-option">
            <div className="option-content">
              <h3>Verify Database</h3>
              <p>Check database integrity and consistency</p>
            </div>
            <button
              className="btn btn-secondary"
              onClick={handleVerify}
              disabled={loading}
            >
              Check
            </button>
          </div>

          {verifyStatus && (
            <div
              className={`status-message ${
                verifyStatus.status === 'valid' ? 'success' : 'error'
              }`}
            >
              {verifyStatus.status === 'valid' ? (
                <FiCheck className="status-icon" />
              ) : (
                <FiAlertCircle className="status-icon" />
              )}
              <div>
                <p className="status-title">{verifyStatus.message}</p>
                <p className="status-detail">
                  {new Date(verifyStatus.timestamp).toLocaleString()}
                </p>
              </div>
            </div>
          )}
        </section>

        <section className="settings-section">
          <h2>API Configuration</h2>
          <div className="api-config">
            <div className="config-item">
              <label>API Base URL</label>
              <code>http://localhost:8000</code>
            </div>
            <div className="config-item">
              <label>WebSocket Endpoint</label>
              <code>ws://localhost:8000/ws</code>
            </div>
          </div>
          <p className="hint">
            Update these settings in your environment if using a remote server
          </p>
        </section>

        <section className="settings-section">
          <h2>About</h2>
          <div className="about-content">
            <h3>VoiceStudio</h3>
            <p>Advanced AI Voice Management Platform</p>
            <p className="version">Version 1.0.0</p>
            <ul className="features-list">
              <li>✅ Voice Creation & Analysis</li>
              <li>✅ Voice Merging Algorithm</li>
              <li>✅ Text-to-Speech Synthesis</li>
              <li>✅ SQLite Database Backend</li>
              <li>✅ Real-time Audio Processing</li>
            </ul>
          </div>
        </section>
      </div>
    </div>
  );
}
