import React, { useRef, useState, useEffect } from 'react';
import { FiPlay, FiPause, FiVolume2, FiDownload } from 'react-icons/fi';
import { useVoiceStore } from '../store/voiceStore';
import '../styles/VoicePlayer.css';

export default function VoicePlayer({ voiceId }) {
  const { selectedVoice, downloadVoiceAudio, loading } = useVoiceStore();
  const audioRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const updateTime = () => setCurrentTime(audio.currentTime);
    const updateDuration = () => setDuration(audio.duration);
    const handleEnded = () => setIsPlaying(false);

    audio.addEventListener('timeupdate', updateTime);
    audio.addEventListener('loadedmetadata', updateDuration);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('timeupdate', updateTime);
      audio.removeEventListener('loadedmetadata', updateDuration);
      audio.removeEventListener('ended', handleEnded);
    };
  }, []);

  const handlePlayPause = () => {
    const audio = audioRef.current;
    if (isPlaying) {
      audio.pause();
    } else {
      audio.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleVolumeChange = (e) => {
    const value = parseFloat(e.target.value);
    setVolume(value);
    if (audioRef.current) {
      audioRef.current.volume = value;
    }
  };

  const handleProgressChange = (e) => {
    const time = parseFloat(e.target.value);
    setCurrentTime(time);
    if (audioRef.current) {
      audioRef.current.currentTime = time;
    }
  };

  const handleDownload = async () => {
    try {
      await downloadVoiceAudio(voiceId);
    } catch (err) {
      console.error('Download failed:', err);
    }
  };

  const formatTime = (time) => {
    if (!time || isNaN(time)) return '0:00';
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  if (!selectedVoice) {
    return <div className="voice-player loading">Loading audio player...</div>;
  }

  const audioUrl = selectedVoice.audio_file_path
    ? `http://localhost:8000/voices/${voiceId}/audio`
    : null;

  return (
    <div className="voice-player">
      {audioUrl ? (
        <>
          <audio
            ref={audioRef}
            src={audioUrl}
            onLoadedMetadata={() => setDuration(audioRef.current.duration)}
          />

          <div className="player-controls">
            <button
              className="play-btn"
              onClick={handlePlayPause}
              title={isPlaying ? 'Pause' : 'Play'}
            >
              {isPlaying ? <FiPause /> : <FiPlay />}
            </button>

            <div className="progress-container">
              <span className="time">{formatTime(currentTime)}</span>
              <input
                type="range"
                className="progress-bar"
                min="0"
                max={duration || 0}
                value={currentTime}
                onChange={handleProgressChange}
              />
              <span className="time">{formatTime(duration)}</span>
            </div>

            <div className="volume-container">
              <FiVolume2 />
              <input
                type="range"
                className="volume-slider"
                min="0"
                max="1"
                step="0.1"
                value={volume}
                onChange={handleVolumeChange}
                title="Volume"
              />
            </div>

            <button
              className="download-btn"
              onClick={handleDownload}
              disabled={loading}
              title="Download audio"
            >
              <FiDownload />
            </button>
          </div>

          <div className="player-info">
            <p>
              <strong>Sample Rate:</strong> {selectedVoice.sample_rate} Hz
            </p>
            <p>
              <strong>Duration:</strong> {selectedVoice.duration.toFixed(2)}s
            </p>
            <p>
              <strong>File Size:</strong> {(selectedVoice.file_size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>
        </>
      ) : (
        <div className="player-empty">No audio file available</div>
      )}
    </div>
  );
}
