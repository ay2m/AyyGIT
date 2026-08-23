"""
VoiceStudio REST API
API الواجهة البرمجية
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import io
import soundfile as sf
from core_engine import VoiceStudioEngine, Language, AudioConfig, OptimizedVoiceStudio
import asyncio
import json

app = FastAPI(
    title="VoiceStudio API",
    description="محرك صوتي ذكي متقدم - Advanced AI Voice Engine",
    version="1.0.0"
)

# CORS للتطبيقات الخارجية
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# تهيئة المحرك
engine = OptimizedVoiceStudio()


@app.get("/health")
async def health_check():
    """فحص صحة الخادم - Health check"""
    return {
        "status": "online",
        "models_loaded": engine.models_loaded,
        "version": "1.0.0"
    }


@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...), language: str = "ar"):
    """
    تحويل الملف الصوتي إلى نص
    Convert audio file to text

    - العربية: ar
    - الإنجليزية: en
    - الفرنسية: fr
    - الإسبانية: es
    """
    try:
        contents = await file.read()
        audio_data, sr = sf.read(io.BytesIO(contents))

        # تحويل إلى mono إذا لزم
        if len(audio_data.shape) > 1:
            audio_data = audio_data.mean(axis=1)

        # إعادة العينات
        if sr != 16000:
            audio_data = np.interp(
                np.linspace(0, len(audio_data), int(len(audio_data) * 16000 / sr)),
                np.arange(len(audio_data)),
                audio_data
            )

        lang = Language[language.upper()] if language.upper() in Language.__members__ else Language.ARABIC
        result = await engine.transcribe(audio_data, lang)

        return {
            "text": result.text,
            "confidence": result.confidence,
            "language": result.language.value,
            "duration": result.duration
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/synthesize")
async def synthesize_speech(text: str, language: str = "ar"):
    """
    تحويل النص إلى صوت طبيعي
    Convert text to natural speech
    """
    try:
        lang = Language[language.upper()] if language.upper() in Language.__members__ else Language.ARABIC
        result = await engine.synthesize(text, lang)

        # حفظ الصوت في ذاكرة
        audio_bytes = io.BytesIO()
        sf.write(audio_bytes, result.audio_output, engine.bark_sr, format='WAV')
        audio_bytes.seek(0)

        return FileResponse(
            audio_bytes,
            media_type="audio/wav",
            filename="output.wav"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/conversation")
async def full_conversation(file: UploadFile = File(...), language: str = "ar"):
    """
    محادثة كاملة: استماع → فهم → رد
    Full conversation flow
    """
    try:
        contents = await file.read()
        audio_data, sr = sf.read(io.BytesIO(contents))

        if len(audio_data.shape) > 1:
            audio_data = audio_data.mean(axis=1)

        if sr != 16000:
            audio_data = np.interp(
                np.linspace(0, len(audio_data), int(len(audio_data) * 16000 / sr)),
                np.arange(len(audio_data)),
                audio_data
            )

        result = await engine.process_conversation(audio_data)

        # تحويل الصوت إلى bytes
        audio_bytes = io.BytesIO()
        sf.write(audio_bytes, result["audio"], engine.bark_sr, format='WAV')
        audio_bytes.seek(0)

        return {
            "user_input": result["user_input"],
            "intent": result["intent"],
            "bot_response": result["bot_response"],
            "duration": result["duration"],
            "audio_url": "/get-response-audio"  # يمكن تحسينها
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.websocket("/ws/conversation")
async def websocket_conversation(websocket: WebSocket):
    """
    اتصال WebSocket للمحادثة الفورية
    WebSocket connection for real-time conversation
    """
    await websocket.accept()
    try:
        while True:
            # استقبال الصوت
            data = await websocket.receive_bytes()
            audio_array = np.frombuffer(data, dtype=np.float32)

            # معالجة
            result = await engine.process_conversation(audio_array)

            # إرسال النتيجة
            await websocket.send_json({
                "user_text": result["user_input"],
                "intent": result["intent"],
                "bot_response": result["bot_response"]
            })

            # إرسال الصوت
            await websocket.send_bytes(result["audio"].tobytes())

    except Exception as e:
        await websocket.close(code=1011, reason=str(e))


@app.get("/languages")
async def get_supported_languages():
    """الحصول على اللغات المدعومة - Get supported languages"""
    return {
        "supported": [
            {"code": "ar", "name": "العربية"},
            {"code": "en", "name": "English"},
            {"code": "fr", "name": "Français"},
            {"code": "es", "name": "Español"},
        ]
    }


@app.get("/stats")
async def get_stats():
    """احصائيات الاستخدام - Usage statistics"""
    return {
        "models_loaded": engine.models_loaded,
        "quality_mode": engine.config.quality,
        "sample_rate": engine.config.sample_rate,
        "supported_languages": len(Language)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
