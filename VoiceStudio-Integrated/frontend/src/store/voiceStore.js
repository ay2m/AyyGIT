import { create } from 'zustand';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const useVoiceStore = create((set, get) => ({
  // State
  voices: [],
  selectedVoice: null,
  loading: false,
  error: null,
  synthesisResult: null,
  mergeHistory: null,
  synthesisHistory: [],
  databaseStats: null,
  cloningResult: null,
  cloningHistory: null,
  clonedVoices: [],

  // Voice Operations
  fetchVoices: async (language = null, voiceType = null, skip = 0, limit = 10) => {
    set({ loading: true, error: null });
    try {
      const params = new URLSearchParams();
      if (language) params.append('language', language);
      if (voiceType) params.append('voice_type', voiceType);
      params.append('skip', skip);
      params.append('limit', limit);

      const response = await axios.get(`${API_BASE_URL}/voices?${params}`);
      set({ voices: response.data.voices, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  getVoiceDetails: async (voiceId) => {
    set({ loading: true, error: null });
    try {
      const response = await axios.get(`${API_BASE_URL}/voices/${voiceId}`);
      set({ selectedVoice: response.data, loading: false });
      return response.data;
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  createVoice: async (file, name, description, language = 'ar') => {
    set({ loading: true, error: null });
    try {
      const formData = new FormData();
      formData.append('file', file);

      const params = new URLSearchParams({
        name,
        description,
        language
      });

      const response = await axios.post(
        `${API_BASE_URL}/voices/create?${params}`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );

      set((state) => ({
        voices: [response.data, ...state.voices],
        loading: false
      }));

      return response.data;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  deleteVoice: async (voiceId) => {
    set({ loading: true, error: null });
    try {
      await axios.delete(`${API_BASE_URL}/voices/${voiceId}`);

      set((state) => ({
        voices: state.voices.filter((v) => v.id !== voiceId),
        selectedVoice: state.selectedVoice?.id === voiceId ? null : state.selectedVoice,
        loading: false
      }));
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  downloadVoiceAudio: async (voiceId) => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/voices/${voiceId}/audio`,
        { responseType: 'blob' }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `voice_${voiceId}.wav`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },

  // Voice Merging
  mergeVoices: async (voiceIds, weights, name, description, language = 'ar') => {
    set({ loading: true, error: null });
    try {
      const params = new URLSearchParams({
        name,
        description,
        language
      });

      voiceIds.forEach((id) => params.append('voice_ids', id));
      if (weights) weights.forEach((w) => params.append('weights', w));

      const response = await axios.post(
        `${API_BASE_URL}/voices/merge?${params}`
      );

      set((state) => ({
        voices: [response.data, ...state.voices],
        loading: false
      }));

      return response.data;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  getMergeHistory: async (voiceId) => {
    set({ loading: true, error: null });
    try {
      const response = await axios.get(
        `${API_BASE_URL}/voices/${voiceId}/merge-history`
      );
      set({ mergeHistory: response.data, loading: false });
      return response.data;
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  // Text-to-Speech
  synthesizeVoice: async (text, voiceId, language = 'ar') => {
    set({ loading: true, error: null });
    try {
      const params = new URLSearchParams({
        text,
        voice_id: voiceId,
        language
      });

      const response = await axios.get(
        `${API_BASE_URL}/synthesis/voice?${params}`,
        { responseType: 'blob' }
      );

      const audioUrl = window.URL.createObjectURL(new Blob([response.data]));
      set({ synthesisResult: { audioUrl, text, voiceId }, loading: false });

      return audioUrl;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  getSynthesisPreview: async (text, voiceId, language = 'ar') => {
    try {
      const params = new URLSearchParams({
        text,
        voice_id: voiceId,
        language
      });

      const response = await axios.get(
        `${API_BASE_URL}/synthesis/preview?${params}`
      );

      return response.data;
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },

  getSynthesisHistory: async (voiceId, limit = 10) => {
    set({ loading: true, error: null });
    try {
      const params = new URLSearchParams({ limit });
      const response = await axios.get(
        `${API_BASE_URL}/voices/${voiceId}/synthesis-history?${params}`
      );
      set({ synthesisHistory: response.data.syntheses, loading: false });
      return response.data;
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  // Database Management
  backupDatabase: async (backupName = null) => {
    set({ loading: true, error: null });
    try {
      const params = new URLSearchParams();
      if (backupName) params.append('backup_name', backupName);

      const response = await axios.post(`${API_BASE_URL}/database/backup?${params}`);
      set({ loading: false });
      return response.data;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  verifyDatabase: async () => {
    set({ loading: true, error: null });
    try {
      const response = await axios.get(`${API_BASE_URL}/database/verify`);
      set({ loading: false });
      return response.data;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  getDatabaseStats: async () => {
    set({ loading: true, error: null });
    try {
      const response = await axios.get(`${API_BASE_URL}/database/stats`);
      set({ databaseStats: response.data, loading: false });
      return response.data;
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  // Voice Cloning
  cloneVoice: async (voiceId, text, cloneName, language = 'ar', cloningParams = {}) => {
    set({ loading: true, error: null });
    try {
      const params = new URLSearchParams({
        text,
        clone_name: cloneName,
        language,
        cloning_method: cloningParams.method || 'basic',
        intensity: cloningParams.intensity || 0.7,
        pitch_shift: cloningParams.pitch_shift || 0,
        tempo_factor: cloningParams.tempo_factor || 1.0,
        formant_shift: cloningParams.formant_shift || 0,
        breathiness: cloningParams.breathiness || 0.3,
        robustness: cloningParams.robustness || 0.5
      });

      const response = await axios.post(
        `${API_BASE_URL}/voices/${voiceId}/clone?${params}`
      );

      set((state) => ({
        cloningResult: response.data,
        voices: [response.data, ...state.voices],
        loading: false
      }));

      return response.data;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  getCloningHistory: async (voiceId) => {
    set({ loading: true, error: null });
    try {
      const response = await axios.get(
        `${API_BASE_URL}/voices/${voiceId}/clone-history`
      );
      set({ cloningHistory: response.data, loading: false });
      return response.data;
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  getClonedVoices: async (voiceId, limit = 10) => {
    set({ loading: true, error: null });
    try {
      const params = new URLSearchParams({ limit });
      const response = await axios.get(
        `${API_BASE_URL}/voices/${voiceId}/cloned-from?${params}`
      );
      set({ clonedVoices: response.data.cloned_voices, loading: false });
      return response.data;
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  transferVoiceCharacteristics: async (sourceVoiceId, targetVoiceId, intensity = 0.7, preservePitch = false) => {
    set({ loading: true, error: null });
    try {
      const params = new URLSearchParams({
        source_voice_id: sourceVoiceId,
        target_voice_id: targetVoiceId,
        transfer_intensity: intensity,
        preserve_target_pitch: preservePitch
      });

      const response = await axios.post(
        `${API_BASE_URL}/voices/transfer?${params}`
      );

      set({ loading: false });
      return response.data;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  // Utilities
  clearError: () => set({ error: null }),
  clearSynthesisResult: () => set({ synthesisResult: null }),
  clearCloningResult: () => set({ cloningResult: null })
}));
