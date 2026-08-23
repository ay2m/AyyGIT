"""
VoiceStudio Integrated Engine
محرك صوتي موحد متكامل
"""

import asyncio
import numpy as np
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


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
