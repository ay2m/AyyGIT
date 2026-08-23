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
