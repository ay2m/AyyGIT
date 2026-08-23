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
        # البحث عن النموذج الصوتي
        metadata_path = METADATA_DIR / f"{voice_id}.json"

        if not metadata_path.exists():
            raise HTTPException(status_code=404, detail=f"النموذج الصوتي {voice_id} غير موجود - Voice model not found")

        # قراءة البيانات الوصفية
        with open(metadata_path, "r", encoding="utf-8") as f:
            model_data = json.load(f)

        # اختيار اللغة
        lang = Language[language.upper()] if language.upper() in Language.__members__ else Language.ARABIC

        # التحقق من تطابق اللغة (اختياري)
        if model_data.get("language") != lang.value:
            print(f"⚠️ تحذير: لغة النموذج ({model_data.get('language')}) لا تطابق لغة المدخل ({lang.value})")

        # إعادة بناء VoiceFeatures من البيانات المخزنة
        # For Step 3, we use quality_score and language as proxies
        # In a full implementation, we'd store the actual features
        from dataclasses import dataclass as dc
        dummy_features = VoiceFeatures(
            mfcc=np.zeros((13, 1)),  # Placeholder
            spectral_centroid=2000.0 + (model_data.get("quality_score", 75) * 10),
            spectral_rolloff=4000.0 + (model_data.get("quality_score", 75) * 5),
            zero_crossing_rate=0.1,
            pitch_mean=100.0 + (model_data.get("quality_score", 75) * 2),
            pitch_variance=50.0,
            energy=model_data.get("quality_score", 75) / 100.0
        )

        # توليد الصوت باستخدام خصائص النموذج
        result = await engine.synthesize_with_voice(text, dummy_features, lang)

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
                "X-Voice-Quality": str(model_data.get("quality_score", 0)),
                "X-Voice-Type": model_data.get("voice_type", "unknown")
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
        metadata_path = METADATA_DIR / f"{voice_id}.json"

        if not metadata_path.exists():
            raise HTTPException(status_code=404, detail="النموذج الصوتي غير موجود - Voice model not found")

        with open(metadata_path, "r", encoding="utf-8") as f:
            model_data = json.load(f)

        # تقدير المدة بناءً على طول النص
        # Estimate duration: ~150 words per minute in speech
        estimated_duration = (len(text.split()) / 150) * 60

        lang = Language[language.upper()] if language.upper() in Language.__members__ else Language.ARABIC

        return {
            "voice_id": voice_id,
            "voice_name": model_data.get("name", "Unknown"),
            "voice_type": model_data.get("voice_type", "unknown"),
            "voice_quality": model_data.get("quality_score", 0),
            "text_length": len(text),
            "word_count": len(text.split()),
            "estimated_duration_seconds": round(estimated_duration, 2),
            "language": lang.value,
            "language_match": model_data.get("language") == lang.value,
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
            audio_path = AUDIO_DIR / f"{voice_id}.wav"
            metadata_path = METADATA_DIR / f"{voice_id}.json"

            if not audio_path.exists() or not metadata_path.exists():
                raise HTTPException(status_code=404, detail=f"النموذج الصوتي {voice_id} غير موجود - Voice model {voice_id} not found")

            # قراءة الملف الصوتي
            audio_data, sr = sf.read(str(audio_path))
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

        # حفظ البيانات الوصفية
        metadata_path = METADATA_DIR / f"{merged_model.id}.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(merged_model.to_dict(), f, ensure_ascii=False, indent=2)

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

        # تخزين في الذاكرة المؤقتة
        voice_models_cache[merged_model.id] = merged_model

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
