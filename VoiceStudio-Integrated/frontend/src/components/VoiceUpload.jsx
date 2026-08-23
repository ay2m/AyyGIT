import React, { useState } from 'react';
import { useVoiceStore } from '../store/voiceStore';
import { FiUpload, FiX } from 'react-icons/fi';
import '../styles/VoiceUpload.css';

export default function VoiceUpload({ onSuccess }) {
  const { createVoice, loading, error } = useVoiceStore();
  const [file, setFile] = useState(null);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [language, setLanguage] = useState('ar');
  const [uploadError, setUploadError] = useState(null);

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (selectedFile.type.startsWith('audio/')) {
        setFile(selectedFile);
        setUploadError(null);
        if (!name) {
          setName(selectedFile.name.replace(/\.[^/.]+$/, ''));
        }
      } else {
        setUploadError('Please select an audio file (MP3, WAV, etc.)');
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file || !name.trim()) {
      setUploadError('Please select a file and enter a name');
      return;
    }

    try {
      await createVoice(file, name, description, language);
      setFile(null);
      setName('');
      setDescription('');
      setLanguage('ar');
      setUploadError(null);
      onSuccess?.();
    } catch (err) {
      setUploadError(err.message || 'Upload failed');
    }
  };

  return (
    <div className="voice-upload">
      <h2>Upload Voice</h2>
      <form onSubmit={handleSubmit} className="upload-form">
        <div className="form-group">
          <label>Audio File</label>
          <div className="file-input-wrapper">
            <input
              type="file"
              accept="audio/*"
              onChange={handleFileSelect}
              disabled={loading}
              className="file-input"
            />
            <div className="file-input-label">
              <FiUpload />
              <span>{file ? file.name : 'Select an audio file'}</span>
            </div>
          </div>
        </div>

        <div className="form-group">
          <label>Voice Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g., My Voice 1"
            disabled={loading}
          />
        </div>

        <div className="form-group">
          <label>Description (optional)</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe this voice..."
            disabled={loading}
            rows="3"
          />
        </div>

        <div className="form-group">
          <label>Language</label>
          <select value={language} onChange={(e) => setLanguage(e.target.value)} disabled={loading}>
            <option value="ar">العربية (Arabic)</option>
            <option value="en">English</option>
            <option value="fr">Français (French)</option>
            <option value="es">Español (Spanish)</option>
          </select>
        </div>

        {(uploadError || error) && (
          <div className="error-message">
            <FiX /> {uploadError || error}
          </div>
        )}

        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={loading || !file}>
            {loading ? 'Uploading...' : 'Upload Voice'}
          </button>
        </div>
      </form>
    </div>
  );
}
