"""
VoiceStudio Integrated Engine
محرك صوتي موحد متكامل
"""

import asyncio
import numpy as np
import librosa
import json
import uuid
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
from pathlib import Path
import pickle


class Language(str, Enum):
    ARABIC = "ar"
    ENGLISH = "en"
    FRENCH = "fr"
    SPANISH = "es"


@dataclass
class AudioConfig:
    sample_rate: int = 16000
    chunk_size: int = 2048
    channels: int = 1
    quality: str = "high"  # high/medium/low


@dataclass
class VoiceResponse:
    text: str
    confidence: float
    language: Language
    duration: float
    audio_output: Optional[np.ndarray] = None
    intent: Optional[str] = None
    emotion: Optional[str] = None


@dataclass
class VoiceFeatures:
    """Voice model features extracted from audio"""
    mfcc: np.ndarray
    spectral_centroid: float
    spectral_rolloff: float
    zero_crossing_rate: float
    pitch_mean: float
    pitch_variance: float
    energy: float


@dataclass
class VoiceModel:
    """Voice model metadata and features"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    language: Language = Language.ARABIC
    sample_rate: int = 16000
    duration: float = 0.0
    file_size: int = 0
    features: Optional[VoiceFeatures] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    voice_type: str = "original"  # original/merged/cloned
    quality_score: float = 0.0
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding numpy arrays"""
        data = asdict(self)
        data['features'] = None
        return data

    def to_json(self) -> str:
        """Convert to JSON"""
        return json.dumps(self.to_dict())


class VoiceStudioEngine:
    """
    نواة VoiceStudio - تجمع كل المكونات
    Core engine combining all components
    """

    def __init__(self, config: AudioConfig = None):
        self.config = config or AudioConfig()
        self.models_loaded = False
        self._init_models()

    def _init_models(self):
        """تحميل النماذج بكفاءة - Load models efficiently"""
        try:
            # Whisper - STT سريع
            from faster_whisper import WhisperModel
            self.whisper = WhisperModel("base", device="auto", compute_type="int8")

            # Bark - TTS حقيقي سريع
            from bark import SAMPLE_RATE as bark_sr, generate_audio, preload_models
            preload_models()
            self.bark_sr = bark_sr
            self.bark_generate = generate_audio

            # ONNX Runtime - للأداء الأمثل
            import onnxruntime as ort
            self.ort_session = ort

            self.models_loaded = True
            print("✅ All models loaded successfully")
        except ImportError as e:
            print(f"⚠️ Warning: {e}")
            self.models_loaded = False

    async def transcribe(self, audio_data: np.ndarray, lang: Language = Language.ARABIC) -> VoiceResponse:
        """
        تحويل الصوت إلى نص
        Convert speech to text with enhancement
        """
        if not self.models_loaded:
            raise RuntimeError("Models not loaded")

        try:
            # معالجة الصوت
            segments, info = self.whisper.transcribe(
                audio_data,
                language=lang.value,
                condition_on_previous_text=False,
                without_timestamps=False
            )

            text = " ".join([seg.text for seg in segments])
            confidence = info.get("language_probability", 0.95)

            return VoiceResponse(
                text=text,
                confidence=confidence,
                language=lang,
                duration=len(audio_data) / self.config.sample_rate
            )
        except Exception as e:
            raise RuntimeError(f"Transcription error: {e}")

    async def synthesize(self, text: str, language: Language = Language.ARABIC,
                        speaker: str = "default") -> VoiceResponse:
        """
        تحويل النص إلى صوت بشري طبيعي
        Convert text to natural speech
        """
        if not self.models_loaded:
            raise RuntimeError("Models not loaded")

        try:
            # Bark prompt engineering للتحكم بالنبرة
            language_prompt = {
                Language.ARABIC: "[SPEAKER] [LAUGH]",
                Language.ENGLISH: "[SPEAKER] [CLEAR]",
            }.get(language, "[SPEAKER]")

            audio_array = self.bark_generate(
                text,
                history_prompt=language_prompt,
                text_temp=0.7,
                waveform_temp=0.8
            )

            return VoiceResponse(
                text=text,
                confidence=0.99,
                language=language,
                duration=len(audio_array) / self.bark_sr,
                audio_output=audio_array
            )
        except Exception as e:
            raise RuntimeError(f"Synthesis error: {e}")

    async def synthesize_with_voice(self, text: str, voice_features: VoiceFeatures,
                                   language: Language = Language.ARABIC) -> VoiceResponse:
        """
        تحويل النص إلى صوت باستخدام خصائص صوتية محددة
        Convert text to speech using specific voice characteristics

        Args:
            text: Text to synthesize
            voice_features: VoiceFeatures from a voice model
            language: Language of the text

        Returns:
            VoiceResponse with synthesized audio
        """
        if not self.models_loaded:
            raise RuntimeError("Models not loaded")

        try:
            # استخراج خصائص الصوت للتأثير على التخليق
            # Extract voice characteristics for synthesis control
            pitch_factor = voice_features.pitch_mean / 200.0  # Normalize pitch
            energy_factor = voice_features.energy * 0.5  # Scale energy
            spectral_brightness = voice_features.spectral_centroid / 4000.0  # 0-1 range

            # ضبط معاملات Bark بناءً على خصائص الصوت
            # Adjust Bark parameters based on voice features
            text_temp = 0.6 + (spectral_brightness * 0.2)  # Range: 0.6-0.8
            waveform_temp = 0.7 + (energy_factor * 0.2)  # Range: 0.7-0.9

            # اختيار prompt اللغة
            language_prompt = {
                Language.ARABIC: "[SPEAKER] [LAUGH]",
                Language.ENGLISH: "[SPEAKER] [CLEAR]",
                Language.FRENCH: "[SPEAKER]",
                Language.SPANISH: "[SPEAKER]",
            }.get(language, "[SPEAKER]")

            # توليد الصوت
            audio_array = self.bark_generate(
                text,
                history_prompt=language_prompt,
                text_temp=text_temp,
                waveform_temp=waveform_temp
            )

            # تطبيق تأثيرات الصوت (اختياري - بسيط)
            # Apply voice characteristics (optional)
            audio_array = audio_array * (0.8 + energy_factor)

            # منع القطع
            max_val = np.max(np.abs(audio_array))
            if max_val > 1.0:
                audio_array = audio_array / max_val * 0.95

            return VoiceResponse(
                text=text,
                confidence=0.95 + (voice_features.energy * 0.04),
                language=language,
                duration=len(audio_array) / self.bark_sr,
                audio_output=audio_array
            )
        except Exception as e:
            raise RuntimeError(f"Voice-based synthesis error: {e}")

    async def process_conversation(self, audio_input: np.ndarray) -> Dict[str, Any]:
        """
        معالجة محادثة كاملة: استماع → فهم → رد
        Full conversation: listen → understand → respond
        """
        # 1. استماع وتحويل
        user_text = await self.transcribe(audio_input)

        # 2. معالجة اللغة الطبيعية (يمكن ربطها مع Rasa)
        intent = self._extract_intent(user_text.text)

        # 3. توليد الرد
        response_text = self._generate_response(intent, user_text.text)

        # 4. تحويل الرد إلى صوت
        audio_response = await self.synthesize(response_text, user_text.language)

        return {
            "user_input": user_text.text,
            "intent": intent,
            "bot_response": response_text,
            "audio": audio_response.audio_output,
            "duration": audio_response.duration
        }

    async def create_voice_model(self, audio_data: np.ndarray, name: str,
                                 description: str = "", language: Language = Language.ARABIC) -> VoiceModel:
        """
        Create a new voice model from audio recording
        تحويل تسجيل صوتي إلى نموذج صوتي
        """
        try:
            # Extract voice features
            features = self._extract_voice_features(audio_data, language)

            # Calculate quality score
            quality_score = self._calculate_quality_score(audio_data, features)

            # Create voice model
            voice_model = VoiceModel(
                name=name,
                description=description,
                language=language,
                sample_rate=self.config.sample_rate,
                duration=len(audio_data) / self.config.sample_rate,
                file_size=len(audio_data) * 2,  # 16-bit audio
                features=features,
                quality_score=quality_score,
                voice_type="original"
            )

            return voice_model
        except Exception as e:
            raise RuntimeError(f"Voice model creation error: {e}")

    def _extract_voice_features(self, audio_data: np.ndarray, language: Language) -> VoiceFeatures:
        """Extract acoustic features from audio"""
        # Normalize audio
        audio_normalized = audio_data / (np.max(np.abs(audio_data)) + 1e-9)

        # MFCC - Mel-frequency cepstral coefficients
        mfcc = librosa.feature.mfcc(y=audio_normalized, sr=self.config.sample_rate, n_mfcc=13)

        # Spectral features
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio_normalized, sr=self.config.sample_rate))
        spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=audio_normalized, sr=self.config.sample_rate))

        # Zero crossing rate
        zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(audio_normalized))

        # Pitch estimation (simplified)
        S = librosa.magphase(librosa.stft(audio_normalized))[0]
        pitch_mean = np.mean(librosa.feature.spectral_centroid(S=S, sr=self.config.sample_rate))
        pitch_variance = np.var(librosa.feature.spectral_centroid(S=S, sr=self.config.sample_rate))

        # Energy
        energy = np.mean(np.sqrt(np.sum(mfcc**2, axis=0)))

        return VoiceFeatures(
            mfcc=mfcc,
            spectral_centroid=float(spectral_centroid),
            spectral_rolloff=float(spectral_rolloff),
            zero_crossing_rate=float(zero_crossing_rate),
            pitch_mean=float(pitch_mean),
            pitch_variance=float(pitch_variance),
            energy=float(energy)
        )

    def _calculate_quality_score(self, audio_data: np.ndarray, features: VoiceFeatures) -> float:
        """
        Calculate voice quality score (0-100)
        Based on clarity, energy, and spectral characteristics
        """
        # Normalize audio
        audio_normalized = audio_data / (np.max(np.abs(audio_data)) + 1e-9)

        # Signal-to-noise ratio estimate
        noise_profile = np.std(audio_normalized[:self.config.sample_rate // 2])  # First 0.5s
        snr = 20 * np.log10(np.mean(np.abs(audio_normalized)) / (noise_profile + 1e-9))
        snr_score = min(100, max(0, snr * 5))

        # Energy uniformity
        energy_score = min(100, features.energy * 100)

        # Spectral balance
        spectral_balance = features.spectral_centroid / (features.spectral_rolloff + 1e-9)
        spectral_score = min(100, spectral_balance * 50)

        # Combined score
        quality_score = (snr_score * 0.3 + energy_score * 0.3 + spectral_score * 0.4)
        return float(min(100, max(0, quality_score)))

    def _extract_intent(self, text: str) -> str:
        """استخراج النية من النص - Extract intent"""
        intents = {
            "السلام": "greeting",
            "شكرا": "thanks",
            "كيف": "question",
            "ماذا": "question",
            "اسمك": "identity",
            "hello": "greeting",
            "thanks": "thanks",
            "what": "question",
            "how": "question",
        }

        for key, intent in intents.items():
            if key in text.lower():
                return intent
        return "general"

    def _generate_response(self, intent: str, text: str) -> str:
        """توليد رد ذكي - Generate smart response"""
        responses = {
            "greeting": "مرحبا! أنا مساعدك الصوتي الذكي. كيف يمكنني مساعدتك؟",
            "thanks": "أنت مرحبا! سعيد بمساعدتك.",
            "question": "سؤال جيد! دعني أساعدك بالإجابة.",
            "identity": "أنا VoiceStudio، مساعدك الصوتي الذكي المتقدم.",
            "general": f"فهمت: '{text}'. كيف يمكنني المساعدة؟"
        }
        return responses.get(intent, responses["general"])

    async def merge_voice_models(self, voice_ids: List[str], audio_data_dict: Dict[str, np.ndarray],
                                weights: Optional[List[float]] = None, name: str = "",
                                description: str = "", language: Language = Language.ARABIC) -> VoiceModel:
        """
        دمج عدة نماذج صوتية - Merge multiple voice models
        Creates a new voice model by blending acoustic features and audio from multiple voices

        Args:
            voice_ids: List of voice model IDs to merge
            audio_data_dict: Dictionary mapping voice_id to audio_data (numpy arrays)
            weights: Optional list of weights for each voice (normalized to sum=1)
            name: Name for the merged voice model
            description: Description of the merged voice
            language: Language of the merged voice

        Returns:
            VoiceModel: New merged voice model
        """
        try:
            if not voice_ids or len(voice_ids) < 2:
                raise ValueError("يجب توفير صوتين على الأقل للدمج - At least 2 voices required for merging")

            if weights is None:
                weights = [1.0 / len(voice_ids)] * len(voice_ids)
            else:
                weights = list(weights)
                if len(weights) != len(voice_ids):
                    raise ValueError("عدد الأوزان يجب أن يطابق عدد الأصوات - Number of weights must match number of voices")
                # Normalize weights
                total = sum(weights)
                weights = [w / total for w in weights]

            # Blend audio data
            merged_audio = self._blend_audio_arrays(audio_data_dict, voice_ids, weights)

            # Extract features from merged audio
            merged_features = self._extract_voice_features(merged_audio, language)

            # Calculate quality score
            quality_score = self._calculate_quality_score(merged_audio, merged_features)

            # Create merged voice model
            voice_model = VoiceModel(
                name=name,
                description=description,
                language=language,
                sample_rate=self.config.sample_rate,
                duration=len(merged_audio) / self.config.sample_rate,
                file_size=len(merged_audio) * 2,
                features=merged_features,
                quality_score=quality_score,
                voice_type="merged",
                tags=[f"merged_from_{vid[:8]}" for vid in voice_ids]
            )

            return voice_model
        except Exception as e:
            raise RuntimeError(f"Voice merging error: {e}")

    def _blend_audio_arrays(self, audio_data_dict: Dict[str, np.ndarray],
                           voice_ids: List[str], weights: List[float]) -> np.ndarray:
        """
        Blend multiple audio arrays using weighted averaging
        Handles different audio lengths by padding shorter ones
        """
        # Find max length
        max_length = max(len(audio_data_dict[vid]) for vid in voice_ids)

        # Pad and blend
        blended = np.zeros(max_length)
        for voice_id, weight in zip(voice_ids, weights):
            audio = audio_data_dict[voice_id]
            # Pad if necessary
            if len(audio) < max_length:
                audio = np.pad(audio, (0, max_length - len(audio)), mode='constant')
            blended += audio * weight

        # Normalize to prevent clipping
        max_val = np.max(np.abs(blended))
        if max_val > 0:
            blended = blended / max_val * 0.95

        return blended

    def _blend_voice_features(self, features_dict: Dict[str, VoiceFeatures],
                             voice_ids: List[str], weights: List[float]) -> VoiceFeatures:
        """
        Blend acoustic features from multiple voice models
        Creates interpolated features that represent the merged voice
        """
        blended_mfcc = np.zeros_like(list(features_dict.values())[0].mfcc)
        blended_spectral_centroid = 0.0
        blended_spectral_rolloff = 0.0
        blended_zero_crossing = 0.0
        blended_pitch_mean = 0.0
        blended_pitch_variance = 0.0
        blended_energy = 0.0

        for voice_id, weight in zip(voice_ids, weights):
            features = features_dict[voice_id]
            blended_mfcc += features.mfcc * weight
            blended_spectral_centroid += features.spectral_centroid * weight
            blended_spectral_rolloff += features.spectral_rolloff * weight
            blended_zero_crossing += features.zero_crossing_rate * weight
            blended_pitch_mean += features.pitch_mean * weight
            blended_pitch_variance += features.pitch_variance * weight
            blended_energy += features.energy * weight

        return VoiceFeatures(
            mfcc=blended_mfcc,
            spectral_centroid=float(blended_spectral_centroid),
            spectral_rolloff=float(blended_spectral_rolloff),
            zero_crossing_rate=float(blended_zero_crossing),
            pitch_mean=float(blended_pitch_mean),
            pitch_variance=float(blended_pitch_variance),
            energy=float(blended_energy)
        )


class OptimizedVoiceStudio(VoiceStudioEngine):
    """
    نسخة محسّنة للأداء العالي
    Optimized version for high performance
    """

    def __init__(self, config: AudioConfig = None):
        super().__init__(config or AudioConfig(quality="medium"))
        self.cache = {}

    async def transcribe_fast(self, audio_data: np.ndarray) -> VoiceResponse:
        """نسخة سريعة من التحويل - Fast transcription version"""
        # تقليل معدل العينات للسرعة
        if self.config.sample_rate > 8000:
            audio_data = audio_data[::2]

        return await self.transcribe(audio_data)

    async def synthesize_stream(self, text: str) -> np.ndarray:
        """
        بث الصوت مباشرة بدون انتظار الانتهاء
        Stream audio directly
        """
        chunks = text.split('.')
        audio_chunks = []

        for chunk in chunks:
            if chunk.strip():
                response = await self.synthesize(chunk.strip())
                audio_chunks.append(response.audio_output)

        return np.concatenate(audio_chunks) if audio_chunks else np.array([])


# مثال على الاستخدام - Usage Example
async def main():
    engine = OptimizedVoiceStudio()

    # اختبار تحويل النص إلى صوت
    print("🎤 Testing Text-to-Speech...")
    response = await engine.synthesize("السلام عليكم ورحمة الله وبركاته")
    print(f"✅ Generated audio: {response.duration:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())
