import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import VoiceLibrary from './pages/VoiceLibrary';
import VoiceDetail from './pages/VoiceDetail';
import VoiceMerge from './pages/VoiceMerge';
import TextToSpeech from './pages/TextToSpeech';
import VoiceCloning from './pages/VoiceCloning';
import Settings from './pages/Settings';
import './styles/App.css';

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-container">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/voices" element={<VoiceLibrary />} />
            <Route path="/voices/:voiceId" element={<VoiceDetail />} />
            <Route path="/merge" element={<VoiceMerge />} />
            <Route path="/synthesize" element={<TextToSpeech />} />
            <Route path="/clone" element={<VoiceCloning />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
