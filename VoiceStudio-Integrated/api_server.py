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
from core_engine import VoiceStudioEngine, Language, AudioConfig, OptimizedVoiceStudio, VoiceModel, VoiceFeatures
from database import VoiceStudioDB
import asyncio
import json
import os
from pathlib import Path
import shutil
from datetime import datetime
from typing import List, Optional

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

# تهيئة قاعدة البيانات
db = VoiceStudioDB("./voices/voicestudio.db")

# تهيئة مجلدات التخزين للملفات الصوتية
VOICES_DIR = Path("./voices")
AUDIO_DIR = VOICES_DIR / "audio"
BACKUP_DIR = VOICES_DIR / "backups"

for directory in [AUDIO_DIR, BACKUP_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


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


@app.post("/synthesis/voice")
async def synthesize_with_voice(
    text: str = Query(..., min_length=1, max_length=1000),
    voice_id: str = Query(...),
    language: str = Query("ar")
):
    """
    تحويل النص إلى صوت باستخدام نموذج صوتي محدد
    Convert text to speech using a specific voice model

    - text: النص المراد تحويله (Text to synthesize)
    - voice_id: معرف النموذج الصوتي (Voice model ID)
    - language: اللغة (ar/en/fr/es)
    """
    try:
        # البحث عن النموذج الصوتي من قاعدة البيانات
        voice = db.get_voice_model(voice_id)
        if not voice:
            raise HTTPException(status_code=404, detail=f"النموذج الصوتي {voice_id} غير موجود - Voice model not found")

        # اختيار اللغة
        lang = Language[language.upper()] if language.upper() in Language.__members__ else Language.ARABIC

        # التحقق من تطابق اللغة (اختياري)
        if voice.language != lang:
            print(f"⚠️ تحذير: لغة النموذج ({voice.language.value}) لا تطابق لغة المدخل ({lang.value})")

        # الحصول على خصائص الصوت من قاعدة البيانات
        features = db.get_voice_features(voice_id)
        if not features:
            # إعادة بناء VoiceFeatures من الجودة كبديل
            features = VoiceFeatures(
                mfcc=np.zeros((13, 1)),
                spectral_centroid=2000.0 + (voice.quality_score * 10),
                spectral_rolloff=4000.0 + (voice.quality_score * 5),
                zero_crossing_rate=0.1,
                pitch_mean=100.0 + (voice.quality_score * 2),
                pitch_variance=50.0,
                energy=voice.quality_score / 100.0
            )

        # توليد الصوت باستخدام خصائص النموذج
        result = await engine.synthesize_with_voice(text, features, lang)

        # حفظ سجل التخليق
        db.save_synthesis_history(voice_id, text, lang.value, result.duration)

        # حفظ الصوت في ذاكرة
        audio_bytes = io.BytesIO()
        sf.write(audio_bytes, result.audio_output, engine.bark_sr, format='WAV')
        audio_bytes.seek(0)

        return FileResponse(
            audio_bytes,
            media_type="audio/wav",
            filename=f"synthesis_{voice_id[:8]}.wav",
            headers={
                "X-Voice-ID": voice_id,
                "X-Voice-Quality": str(voice.quality_score),
                "X-Voice-Type": voice.voice_type
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"خطأ في التخليق الصوتي: {str(e)}")


@app.get("/synthesis/preview")
async def synthesis_preview(
    text: str = Query(..., min_length=1, max_length=500),
    voice_id: str = Query(...),
    language: str = Query("ar")
):
    """
    معاينة التخليق الصوتي بدون تنزيل الملف
    Preview synthesis metadata without generating audio

    Returns synthesis details:
    - duration estimate
    - quality metrics
    - voice characteristics
    - language compatibility
    """
    try:
        # الحصول على البيانات من قاعدة البيانات
        voice = db.get_voice_model(voice_id)
        if not voice:
            raise HTTPException(status_code=404, detail="النموذج الصوتي غير موجود - Voice model not found")

        # تقدير المدة بناءً على طول النص
        # Estimate duration: ~150 words per minute in speech
        estimated_duration = (len(text.split()) / 150) * 60

        lang = Language[language.upper()] if language.upper() in Language.__members__ else Language.ARABIC

        return {
            "voice_id": voice_id,
            "voice_name": voice.name,
            "voice_type": voice.voice_type,
            "voice_quality": voice.quality_score,
            "text_length": len(text),
            "word_count": len(text.split()),
            "estimated_duration_seconds": round(estimated_duration, 2),
            "language": lang.value,
            "language_match": voice.language == lang,
            "can_synthesize": True,
            "message": "✅ جاهز للتخليق الصوتي - Ready for synthesis"
        }
    except HTTPException:
        raise
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

        # حفظ الملف الصوتي
        audio_path = AUDIO_DIR / f"{voice_model.id}.wav"
        sf.write(str(audio_path), audio_data, 16000)

        # حفظ في قاعدة البيانات
        db.save_voice_model(voice_model, str(audio_path), voice_model.features)

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
        # استعلام قاعدة البيانات
        voices = db.list_voice_models(language=language, voice_type=voice_type, skip=skip, limit=limit)
        total = db.count_voice_models(language=language, voice_type=voice_type)

        # تحويل إلى قاموس للإرجاع
        voices_data = [
            {
                "id": v.id,
                "name": v.name,
                "description": v.description,
                "language": v.language.value,
                "duration": v.duration,
                "quality_score": v.quality_score,
                "voice_type": v.voice_type,
                "tags": v.tags,
                "created_at": v.created_at,
                "updated_at": v.updated_at
            }
            for v in voices
        ]

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "voices": voices_data
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
        # استعلام قاعدة البيانات
        voice = db.get_voice_model(voice_id)

        if not voice:
            raise HTTPException(status_code=404, detail="النموذج الصوتي غير موجود - Voice model not found")

        # التحقق من وجود الملف الصوتي
        audio_path = db.get_voice_audio_path(voice_id)
        audio_exists = Path(audio_path).exists() if audio_path else False

        return {
            "id": voice.id,
            "name": voice.name,
            "description": voice.description,
            "language": voice.language.value,
            "sample_rate": voice.sample_rate,
            "duration": voice.duration,
            "file_size": voice.file_size,
            "quality_score": voice.quality_score,
            "voice_type": voice.voice_type,
            "tags": voice.tags,
            "created_at": voice.created_at,
            "updated_at": voice.updated_at,
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
        # التحقق من وجود النموذج
        voice = db.get_voice_model(voice_id)
        if not voice:
            raise HTTPException(status_code=404, detail="النموذج الصوتي غير موجود - Voice model not found")

        # حذف الملف الصوتي
        audio_path = db.get_voice_audio_path(voice_id)
        if audio_path and Path(audio_path).exists():
            Path(audio_path).unlink()

        # حذف من قاعدة البيانات
        db.delete_voice_model(voice_id)

        return {
            "message": "✅ تم حذف النموذج الصوتي بنجاح - Voice model deleted successfully",
            "id": voice_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/voices/merge")
async def merge_voice_models(
    voice_ids: List[str] = Query(..., min_items=2, max_items=5),
    weights: Optional[List[float]] = Query(None),
    name: str = Query(..., min_length=1, max_length=100),
    description: str = Query("", max_length=500),
    language: str = Query("ar")
):
    """
    دمج عدة نماذج صوتية في نموذج واحد
    Merge multiple voice models into one

    - voice_ids: قائمة معرفات الأصوات (List of voice IDs to merge, 2-5 voices)
    - weights: أوزان اختيارية لكل صوت (Optional weights for each voice)
    - name: اسم النموذج الجديد (Name for merged voice)
    - description: وصف اختياري (Optional description)
    - language: اللغة (ar/en/fr/es)
    """
    try:
        # التحقق من وجود جميع الأصوات
        audio_data_dict = {}
        for voice_id in voice_ids:
            # استعلام قاعدة البيانات
            voice = db.get_voice_model(voice_id)
            if not voice:
                raise HTTPException(status_code=404, detail=f"النموذج الصوتي {voice_id} غير موجود - Voice model {voice_id} not found")

            # قراءة الملف الصوتي
            audio_path = db.get_voice_audio_path(voice_id)
            if not audio_path or not Path(audio_path).exists():
                raise HTTPException(status_code=404, detail=f"ملف الصوت لـ {voice_id} غير موجود - Audio file not found")

            audio_data, sr = sf.read(audio_path)
            if sr != 16000:
                num_samples = int(len(audio_data) * 16000 / sr)
                audio_data = np.interp(
                    np.linspace(0, len(audio_data), num_samples),
                    np.arange(len(audio_data)),
                    audio_data
                )
            audio_data_dict[voice_id] = audio_data

        # اختيار اللغة
        lang = Language[language.upper()] if language.upper() in Language.__members__ else Language.ARABIC

        # دمج الأصوات
        merged_model = await engine.merge_voice_models(
            voice_ids=voice_ids,
            audio_data_dict=audio_data_dict,
            weights=weights,
            name=name,
            description=description,
            language=lang
        )

        # حفظ الملف الصوتي
        merged_audio = audio_data_dict[voice_ids[0]]  # Get one as reference
        if weights:
            # Blend audio manually here
            blended = np.zeros(max(len(audio_data_dict[vid]) for vid in voice_ids))
            for voice_id, weight in zip(voice_ids, (weights if weights else [1.0/len(voice_ids)]*len(voice_ids))):
                audio = audio_data_dict[voice_id]
                if len(audio) < len(blended):
                    audio = np.pad(audio, (0, len(blended) - len(audio)), mode='constant')
                blended += audio * weight
            max_val = np.max(np.abs(blended))
            if max_val > 0:
                merged_audio = blended / max_val * 0.95
            else:
                merged_audio = blended
        else:
            merged_audio = np.mean([audio_data_dict[vid] for vid in voice_ids], axis=0)

        audio_path = AUDIO_DIR / f"{merged_model.id}.wav"
        sf.write(str(audio_path), merged_audio, 16000)

        # حفظ في قاعدة البيانات
        db.save_voice_model(merged_model, str(audio_path), merged_model.features)

        # حفظ سجل الدمج
        db.save_merge_history(merged_model.id, voice_ids, weights)

        return {
            "id": merged_model.id,
            "name": merged_model.name,
            "language": merged_model.language.value,
            "voice_type": merged_model.voice_type,
            "duration": merged_model.duration,
            "quality_score": merged_model.quality_score,
            "merged_from": voice_ids,
            "created_at": merged_model.created_at,
            "message": "✅ تم دمج الأصوات بنجاح - Voices merged successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"خطأ في دمج الأصوات: {str(e)}")


@app.get("/voices/{voice_id}/merge-history")
async def get_merge_history(voice_id: str):
    """
    الحصول على سجل دمج النموذج الصوتي
    Get merge history for a voice model
    """
    try:
        voice = db.get_voice_model(voice_id)
        if not voice:
            raise HTTPException(status_code=404, detail="النموذج الصوتي غير موجود - Voice model not found")

        history = db.get_merge_history(voice_id)
        if not history:
            return {
                "voice_id": voice_id,
                "is_merged": False,
                "message": "هذا النموذج ليس نتيجة دمج - This voice is not a merged model"
            }

        return {
            "voice_id": voice_id,
            "is_merged": True,
            "source_voices": history['source_voice_ids'],
            "weights": history['weights'],
            "merged_at": history['created_at']
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/voices/{voice_id}/synthesis-history")
async def get_synthesis_history(voice_id: str, limit: int = Query(10, ge=1, le=100)):
    """
    الحصول على سجل التخليق الصوتي للنموذج
    Get synthesis history for a voice model
    """
    try:
        voice = db.get_voice_model(voice_id)
        if not voice:
            raise HTTPException(status_code=404, detail="النموذج الصوتي غير موجود - Voice model not found")

        history = db.get_synthesis_history(voice_id, limit=limit)

        return {
            "voice_id": voice_id,
            "voice_name": voice.name,
            "total_syntheses": len(history),
            "syntheses": history
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/database/backup")
async def backup_database(backup_name: str = Query(None)):
    """
    إنشاء نسخة احتياطية من قاعدة البيانات
    Create a database backup
    """
    try:
        if not backup_name:
            backup_name = f"backup_{datetime.utcnow().isoformat().replace(':', '-')}"

        backup_path = BACKUP_DIR / f"{backup_name}.db"
        success = db.export_backup(str(backup_path))

        if success:
            return {
                "status": "success",
                "message": f"✅ تم إنشاء النسخة الاحتياطية - Backup created successfully",
                "backup_name": backup_name,
                "backup_path": str(backup_path),
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="فشل في إنشاء النسخة الاحتياطية - Backup creation failed")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/database/verify")
async def verify_database():
    """
    التحقق من سلامة قاعدة البيانات
    Verify database integrity
    """
    try:
        is_valid = db.verify_database()

        return {
            "status": "valid" if is_valid else "corrupted",
            "message": "✅ قاعدة البيانات سليمة - Database is valid" if is_valid else "❌ قاعدة البيانات تالفة - Database is corrupted",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/database/stats")
async def get_database_stats():
    """
    الحصول على إحصائيات قاعدة البيانات
    Get database statistics
    """
    try:
        total_voices = db.count_voice_models()
        merged_voices = db.count_voice_models(voice_type="merged")
        original_voices = db.count_voice_models(voice_type="original")

        return {
            "total_voices": total_voices,
            "original_voices": original_voices,
            "merged_voices": merged_voices,
            "cloned_voices": db.count_voice_models(voice_type="cloned"),
            "database_path": str(db.db_path),
            "database_size_mb": db.db_path.stat().st_size / (1024 * 1024) if db.db_path.exists() else 0
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ===== صوت الاستنساخ - Voice Cloning Endpoints =====

@app.post("/voices/{voice_id}/clone")
async def clone_voice_model(
    voice_id: str,
    text: str = Query(..., min_length=1, max_length=1000),
    clone_name: str = Query(..., min_length=1, max_length=100),
    language: str = Query("ar"),
    cloning_method: str = Query("basic"),
    intensity: float = Query(0.8, ge=0.0, le=1.0),
    pitch_shift: float = Query(0.0, ge=-12.0, le=12.0),
    tempo_factor: float = Query(1.0, ge=0.5, le=2.0),
    formant_shift: float = Query(0.0, ge=-1.0, le=1.0),
    breathiness: float = Query(0.5, ge=0.0, le=1.0),
    robustness: float = Query(0.8, ge=0.0, le=1.0)
):
    """
    استنساخ نموذج صوتي باستخدام تقنيات متقدمة
    Clone a voice model with advanced parameters

    - voice_id: معرف الصوت المراد استنساخه (Source voice ID)
    - text: النص المراد تخليقه بالصوت المستنسخ (Text to synthesize)
    - clone_name: اسم الصوت المستنسخ (Cloned voice name)
    - language: اللغة (ar/en/fr/es)
    - cloning_method: 'basic' أو 'advanced'
    - intensity: شدة الاستنساخ (0.0-1.0)
    - pitch_shift: تحويل الطبقة الصوتية بالنصف نبرة (-12 إلى +12)
    - tempo_factor: عامل السرعة (0.5 إلى 2.0)
    - formant_shift: تحويل الرنين (-1.0 إلى 1.0)
    - breathiness: مستوى التنفس (0.0-1.0)
    - robustness: المتانة (0.0-1.0)
    """
    try:
        # الحصول على النموذج الأصلي
        source_voice = db.get_voice_model(voice_id)
        if not source_voice:
            raise HTTPException(status_code=404, detail=f"النموذج الصوتي {voice_id} غير موجود - Voice model not found")

        # الحصول على خصائص الصوت المصدر
        source_features = db.get_voice_features(voice_id)
        if not source_features:
            source_features = VoiceFeatures(
                mfcc=np.zeros((13, 1)),
                spectral_centroid=2000.0 + (source_voice.quality_score * 10),
                spectral_rolloff=4000.0 + (source_voice.quality_score * 5),
                zero_crossing_rate=0.1,
                pitch_mean=100.0 + (source_voice.quality_score * 2),
                pitch_variance=50.0,
                energy=source_voice.quality_score / 100.0
            )

        # اختيار اللغة
        lang = Language[language.upper()] if language.upper() in Language.__members__ else Language.ARABIC

        # استنساخ الصوت
        result = await engine.clone_voice(
            source_voice_features=source_features,
            target_text=text,
            language=lang,
            cloning_method=cloning_method,
            intensity=intensity,
            pitch_shift=pitch_shift,
            tempo_factor=tempo_factor,
            formant_shift=formant_shift,
            breathiness=breathiness,
            robustness=robustness
        )

        # إنشاء نموذج صوتي جديد للصوت المستنسخ
        cloned_voice_model = VoiceModel(
            name=clone_name,
            description=f"Cloned from {source_voice.name}",
            language=lang,
            sample_rate=engine.config.sample_rate,
            duration=result.duration,
            file_size=len(result.audio_output) * 2,
            quality_score=source_voice.quality_score * (intensity * 0.8 + 0.2),
            voice_type="cloned",
            tags=[f"cloned_from_{voice_id[:8]}", cloning_method]
        )

        # حفظ الملف الصوتي
        audio_path = AUDIO_DIR / f"{cloned_voice_model.id}.wav"
        sf.write(str(audio_path), result.audio_output, engine.bark_sr)

        # حفظ في قاعدة البيانات
        cloned_features = engine._extract_voice_features(result.audio_output, lang)
        db.save_voice_model(cloned_voice_model, str(audio_path), cloned_features)

        # حفظ سجل الاستنساخ
        db.save_cloning_history(cloned_voice_model.id, voice_id, cloning_method, intensity)

        # حفظ معاملات الاستنساخ
        db.save_cloning_parameters(
            cloned_voice_model.id,
            pitch_shift=pitch_shift,
            tempo_factor=tempo_factor,
            formant_shift=formant_shift,
            breathiness=breathiness,
            robustness=robustness
        )

        return {
            "cloned_voice_id": cloned_voice_model.id,
            "cloned_voice_name": cloned_voice_model.name,
            "source_voice_id": voice_id,
            "source_voice_name": source_voice.name,
            "cloning_method": cloning_method,
            "intensity": intensity,
            "duration": cloned_voice_model.duration,
            "quality_score": cloned_voice_model.quality_score,
            "message": "✅ تم استنساخ الصوت بنجاح - Voice cloned successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"خطأ في استنساخ الصوت: {str(e)}")


@app.get("/voices/{voice_id}/clone-history")
async def get_clone_history(voice_id: str):
    """
    الحصول على سجل استنساخ النموذج الصوتي
    Get cloning history for a voice model
    """
    try:
        voice = db.get_voice_model(voice_id)
        if not voice:
            raise HTTPException(status_code=404, detail="النموذج الصوتي غير موجود - Voice model not found")

        history = db.get_cloning_history(voice_id)
        if not history:
            return {
                "voice_id": voice_id,
                "is_cloned": False,
                "message": "هذا النموذج ليس مستنسخاً - This voice is not a cloned model"
            }

        # الحصول على معاملات الاستنساخ
        params = db.get_cloning_parameters(voice_id)

        return {
            "voice_id": voice_id,
            "voice_name": voice.name,
            "is_cloned": True,
            "source_voice_id": history['source_voice_id'],
            "cloning_method": history['cloning_method'],
            "intensity": history['intensity'],
            "cloning_parameters": params or {},
            "cloned_at": history['created_at']
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/voices/{voice_id}/cloned-from")
async def get_cloned_voices(voice_id: str, limit: int = Query(10, ge=1, le=100)):
    """
    الحصول على جميع الأصوات المستنسخة من صوت مصدر
    Get all cloned voices created from a source voice

    - voice_id: معرف الصوت المصدر (Source voice ID)
    """
    try:
        voice = db.get_voice_model(voice_id)
        if not voice:
            raise HTTPException(status_code=404, detail="النموذج الصوتي غير موجود - Voice model not found")

        cloned_list = db.get_cloned_voices_from_source(voice_id, limit=limit)

        return {
            "source_voice_id": voice_id,
            "source_voice_name": voice.name,
            "total_cloned": len(cloned_list),
            "cloned_voices": cloned_list
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/voices/transfer")
async def transfer_voice_characteristics(
    source_voice_id: str = Query(...),
    target_voice_id: str = Query(...),
    transfer_intensity: float = Query(0.7, ge=0.0, le=1.0),
    preserve_target_pitch: bool = Query(True)
):
    """
    نقل خصائص الصوت من صوت إلى آخر
    Transfer voice characteristics from one voice to another

    - source_voice_id: معرف الصوت المصدر (Source voice ID)
    - target_voice_id: معرف الصوت الهدف (Target voice ID)
    - transfer_intensity: شدة النقل (0.0-1.0)
    - preserve_target_pitch: الحفاظ على نبرة الصوت الهدف
    """
    try:
        # الحصول على الأصوات
        source_voice = db.get_voice_model(source_voice_id)
        if not source_voice:
            raise HTTPException(status_code=404, detail="الصوت المصدر غير موجود - Source voice not found")

        target_voice = db.get_voice_model(target_voice_id)
        if not target_voice:
            raise HTTPException(status_code=404, detail="الصوت الهدف غير موجود - Target voice not found")

        # الحصول على خصائص الأصوات
        source_features = db.get_voice_features(source_voice_id)
        target_features = db.get_voice_features(target_voice_id)

        if not source_features or not target_features:
            raise HTTPException(status_code=400, detail="غير قادر على الحصول على خصائص الصوت - Cannot extract voice features")

        # نقل الخصائص
        transferred_features = VoiceFeatures(
            mfcc=source_features.mfcc * transfer_intensity + target_features.mfcc * (1.0 - transfer_intensity),
            spectral_centroid=source_features.spectral_centroid * transfer_intensity + target_features.spectral_centroid * (1.0 - transfer_intensity),
            spectral_rolloff=source_features.spectral_rolloff * transfer_intensity + target_features.spectral_rolloff * (1.0 - transfer_intensity),
            zero_crossing_rate=source_features.zero_crossing_rate * transfer_intensity + target_features.zero_crossing_rate * (1.0 - transfer_intensity),
            pitch_mean=target_features.pitch_mean if preserve_target_pitch else (source_features.pitch_mean * transfer_intensity + target_features.pitch_mean * (1.0 - transfer_intensity)),
            pitch_variance=source_features.pitch_variance * transfer_intensity + target_features.pitch_variance * (1.0 - transfer_intensity),
            energy=source_features.energy * transfer_intensity + target_features.energy * (1.0 - transfer_intensity)
        )

        return {
            "source_voice_id": source_voice_id,
            "source_voice_name": source_voice.name,
            "target_voice_id": target_voice_id,
            "target_voice_name": target_voice.name,
            "transfer_intensity": transfer_intensity,
            "preserve_target_pitch": preserve_target_pitch,
            "transferred_features": {
                "spectral_centroid": float(transferred_features.spectral_centroid),
                "spectral_rolloff": float(transferred_features.spectral_rolloff),
                "pitch_mean": float(transferred_features.pitch_mean),
                "energy": float(transferred_features.energy)
            },
            "message": "✅ تم نقل الخصائص الصوتية بنجاح - Voice characteristics transferred successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
