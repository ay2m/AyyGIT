"""
VoiceStudio REST API
API الواجهة البرمجية
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import io
import soundfile as sf
from core_engine import VoiceStudioEngine, Language, AudioConfig, OptimizedVoiceStudio, VoiceModel
import asyncio
import json
import os
from pathlib import Path
import shutil

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

# تهيئة مجلدات التخزين
VOICES_DIR = Path("./voices")
MODELS_DIR = VOICES_DIR / "models"
METADATA_DIR = VOICES_DIR / "metadata"
AUDIO_DIR = VOICES_DIR / "audio"

for directory in [MODELS_DIR, METADATA_DIR, AUDIO_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# قاموس لتخزين النماذج في الذاكرة (للتطوير - استخدم قاعدة بيانات في الإنتاج)
voice_models_cache = {}


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


# ===== صوت النماذج - Voice Models Endpoints =====

@app.post("/voices/create")
async def create_voice_model(
    file: UploadFile = File(...),
    name: str = Query(..., min_length=1, max_length=100),
    description: str = Query("", max_length=500),
    language: str = Query("ar")
):
    """
    إنشاء نموذج صوتي جديد من ملف صوتي
    Create a new voice model from an audio file

    - name: اسم النموذج الصوتي (Voice model name)
    - description: وصف اختياري (Optional description)
    - language: اللغة (ar/en/fr/es)
    """
    try:
        # قراءة الملف الصوتي
        contents = await file.read()
        audio_data, sr = sf.read(io.BytesIO(contents))

        # تحويل إلى mono إذا لزم
        if len(audio_data.shape) > 1:
            audio_data = audio_data.mean(axis=1)

        # إعادة العينات إلى 16kHz
        if sr != 16000:
            num_samples = int(len(audio_data) * 16000 / sr)
            audio_data = np.interp(
                np.linspace(0, len(audio_data), num_samples),
                np.arange(len(audio_data)),
                audio_data
            )

        # اختيار اللغة
        lang = Language[language.upper()] if language.upper() in Language.__members__ else Language.ARABIC

        # إنشاء نموذج الصوت
        voice_model = await engine.create_voice_model(
            audio_data=audio_data,
            name=name,
            description=description,
            language=lang
        )

        # حفظ البيانات الوصفية
        metadata_path = METADATA_DIR / f"{voice_model.id}.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(voice_model.to_dict(), f, ensure_ascii=False, indent=2)

        # حفظ الملف الصوتي
        audio_path = AUDIO_DIR / f"{voice_model.id}.wav"
        sf.write(str(audio_path), audio_data, 16000)

        # تخزين في الذاكرة المؤقتة
        voice_models_cache[voice_model.id] = voice_model

        return {
            "id": voice_model.id,
            "name": voice_model.name,
            "language": voice_model.language.value,
            "duration": voice_model.duration,
            "quality_score": voice_model.quality_score,
            "voice_type": voice_model.voice_type,
            "created_at": voice_model.created_at,
            "message": "✅ تم إنشاء النموذج الصوتي بنجاح - Voice model created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"خطأ في إنشاء النموذج: {str(e)}")


@app.get("/voices")
async def list_voice_models(
    language: str = Query(None),
    voice_type: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """
    قائمة بجميع نماذج الصوت
    List all voice models with optional filters
    """
    try:
        # جمع جميع نماذج الصوت من المجلد
        all_models = []
        for metadata_file in METADATA_DIR.glob("*.json"):
            with open(metadata_file, "r", encoding="utf-8") as f:
                model_data = json.load(f)
                all_models.append(model_data)

        # تطبيق المرشحات
        filtered_models = all_models
        if language:
            filtered_models = [m for m in filtered_models if m["language"] == language]
        if voice_type:
            filtered_models = [m for m in filtered_models if m["voice_type"] == voice_type]

        # ترتيب حسب تاريخ الإنشاء (الأحدث أولاً)
        filtered_models.sort(key=lambda x: x["created_at"], reverse=True)

        # تطبيق التصفح
        paginated = filtered_models[skip : skip + limit]

        return {
            "total": len(filtered_models),
            "skip": skip,
            "limit": limit,
            "voices": paginated
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/voices/{voice_id}")
async def get_voice_model(voice_id: str):
    """
    الحصول على تفاصيل نموذج صوتي محدد
    Get details of a specific voice model
    """
    try:
        metadata_path = METADATA_DIR / f"{voice_id}.json"

        if not metadata_path.exists():
            raise HTTPException(status_code=404, detail="النموذج الصوتي غير موجود - Voice model not found")

        with open(metadata_path, "r", encoding="utf-8") as f:
            model_data = json.load(f)

        # التحقق من وجود الملف الصوتي
        audio_path = AUDIO_DIR / f"{voice_id}.wav"
        audio_exists = audio_path.exists()

        return {
            **model_data,
            "audio_exists": audio_exists
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/voices/{voice_id}/audio")
async def download_voice_audio(voice_id: str):
    """
    تنزيل ملف الصوت لنموذج محدد
    Download the audio file for a specific voice model
    """
    try:
        audio_path = AUDIO_DIR / f"{voice_id}.wav"

        if not audio_path.exists():
            raise HTTPException(status_code=404, detail="ملف الصوت غير موجود - Audio file not found")

        return FileResponse(
            str(audio_path),
            media_type="audio/wav",
            filename=f"voice_{voice_id}.wav"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/voices/{voice_id}")
async def delete_voice_model(voice_id: str):
    """
    حذف نموذج صوتي
    Delete a voice model
    """
    try:
        metadata_path = METADATA_DIR / f"{voice_id}.json"
        audio_path = AUDIO_DIR / f"{voice_id}.wav"

        if not metadata_path.exists():
            raise HTTPException(status_code=404, detail="النموذج الصوتي غير موجود - Voice model not found")

        # حذف الملفات
        metadata_path.unlink()
        if audio_path.exists():
            audio_path.unlink()

        # حذف من الذاكرة المؤقتة
        if voice_id in voice_models_cache:
            del voice_models_cache[voice_id]

        return {
            "message": "✅ تم حذف النموذج الصوتي بنجاح - Voice model deleted successfully",
            "id": voice_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
