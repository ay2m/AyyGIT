# VoiceStudio Integrated - دليل البدء السريع

## التثبيت والتشغيل الفوري

### الطريقة 1️⃣: Docker (الأسهل)

```bash
# بناء الـ image
docker build -t voicestudio .

# تشغيل الحاوية
docker run -p 8000:8000 voicestudio

# أو باستخدام Docker Compose
docker-compose up
```

زيارة: `http://localhost:8000/docs` (Swagger API)

---

### الطريقة 2️⃣: التثبيت المحلي

```bash
# 1. إنشاء بيئة افتراضية
python -m venv venv
source venv/bin/activate  # Linux/Mac
# أو
venv\Scripts\activate  # Windows

# 2. تثبيت المكتبات
pip install -r requirements.txt

# 3. تشغيل الخادم
python api_server.py

# 4. اختبار الـ API
curl http://localhost:8000/health
```

---

## الاستخدام السريع

### 1️⃣ تحويل صوت إلى نص
```python
import requests

with open("audio.wav", "rb") as f:
    response = requests.post(
        "http://localhost:8000/transcribe",
        files={"file": f},
        params={"language": "ar"}
    )
    print(response.json())
```

### 2️⃣ تحويل نص إلى صوت
```bash
curl -X POST "http://localhost:8000/synthesize?text=السلام عليكم&language=ar" \
     --output output.wav
```

### 3️⃣ محادثة كاملة
```python
import requests

with open("audio.wav", "rb") as f:
    response = requests.post(
        "http://localhost:8000/conversation",
        files={"file": f}
    )
    result = response.json()
    print(f"User: {result['user_input']}")
    print(f"Bot: {result['bot_response']}")
```

### 4️⃣ الاستخدام من Python
```python
from client_example import VoiceStudioClient

client = VoiceStudioClient()

# تحويل صوت
result = client.transcribe_file("audio.wav", language="ar")
print(result["text"])

# تحويل نص
client.text_to_speech("السلام عليكم", language="ar")

# الحصول على اللغات المدعومة
langs = client.get_supported_languages()
print(langs)
```

---

## الميزات الرئيسية

| الميزة | الوصف | الحالة |
|--------|-------|-------|
| 🎤 الاستماع | تحويل صوت لنص (Whisper) | ✅ جاهز |
| 🔊 التحدث | تحويل نص لصوت (Bark/TTS) | ✅ جاهز |
| 💬 المحادثة | محادثة كاملة ذكية | ✅ جاهز |
| 🌍 اللغات | العربية + 3 لغات أخرى | ✅ جاهز |
| ⚡ الوقت الفعلي | WebSocket للمحادثة الفورية | ✅ جاهز |
| 📊 الأداء | تحسين بـ ONNX Runtime | ✅ جاهز |
| 🔄 الدفعات | معالجة عدة ملفات | ✅ جاهز |
| 📱 الأجهزة | دعم الهاتف والكمبيوتر | ✅ جاهز |

---

## API Endpoints

### Health Check
```
GET /health
```

### Transcribe Audio
```
POST /transcribe
- file: audio file
- language: ar/en/fr/es
```

### Synthesize Speech
```
POST /synthesize
- text: النص المراد تحويله
- language: ar/en/fr/es
```

### Full Conversation
```
POST /conversation
- file: audio file
- language: ar/en/fr/es
```

### WebSocket Real-time
```
WS /ws/conversation
```

### Languages
```
GET /languages
```

### Stats
```
GET /stats
```

---

## الإعدادات المتقدمة

### تغيير جودة الصوت
```python
from core_engine import AudioConfig, OptimizedVoiceStudio

config = AudioConfig(quality="high", sample_rate=16000)
engine = OptimizedVoiceStudio(config)
```

### تفعيل GPU
في `.env`:
```
USE_GPU=true
DEVICE=cuda
```

### استخدام Rasa للحوار المتقدم
```bash
# تشغيل Rasa
rasa run --enable-api

# تعديل .env
USE_RASA=true
RASA_SERVER_URL=http://localhost:5005
```

---

## استكشاف الأخطاء

### المشكلة: "Models not loaded"
```bash
# الحل: تثبيت المكتبات مجدداً
pip install --upgrade torch torchvision torchaudio
pip install faster-whisper bark-huggingface
```

### المشكلة: "CUDA out of memory"
```bash
# الحل: تقليل الجودة
# في .env: AUDIO_QUALITY=low
```

### المشكلة: بطء في الأداء
```bash
# الحل: استخدام النسخة المحسّنة
engine = OptimizedVoiceStudio()
result = await engine.transcribe_fast(audio_data)
```

---

## الملفات المهمة

| الملف | الوصف |
|------|-------|
| `core_engine.py` | محرك VoiceStudio الأساسي |
| `api_server.py` | خادم FastAPI |
| `client_example.py` | أمثلة على الاستخدام |
| `requirements.txt` | المكتبات المطلوبة |
| `Dockerfile` | حاوية Docker |

---

## المراجع السريعة

- 📖 [FastAPI Documentation](https://fastapi.tiangolo.com/)
- 🎤 [Faster Whisper](https://github.com/guillaumekln/faster-whisper)
- 🔊 [Bark TTS](https://github.com/suno-ai/bark)
- 💬 [Rasa Framework](https://rasa.com/)

---

## الدعم

للمساعدة والدعم:
- 📧 البريد الإلكتروني: support@voicestudio.local
- 🐛 البلاغ عن الأخطاء: GitHub Issues
- 💬 المنتدى: Community Forum

---

## الترخيص

MIT License - استخدام حر للأغراض التجارية والشخصية

---

**نسخة**: 1.0.0  
**آخر تحديث**: 2024  
**الحالة**: ✅ جاهز للإنتاج
