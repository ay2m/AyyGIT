# 📦 AyyGIT Projects Overview

A curated collection of enhanced and extended versions of open-source projects, with a focus on voice processing and audio technology.

## 🌟 Featured Project

### [VoiceStudio-Integrated](./VoiceStudio-Integrated)
**Status:** ✅ Production Ready | **Commits:** 25+ | **Lines of Code:** 4,400+

A comprehensive voice processing platform with advanced features:

| Feature | Status | Details |
|---------|--------|---------|
| Voice Recording | ✅ | Upload, validation, metadata extraction |
| Voice Merging | ✅ | Weighted blending, feature interpolation |
| Text-to-Speech | ✅ | Multi-language synthesis |
| Voice Cloning | ✅ | **NEW** - Basic & advanced algorithms |
| React Frontend | ✅ | Modern UI with Tailwind CSS |
| SQLite Database | ✅ | Optimized schema with full query support |

**Tech Stack:** Python 3.11, FastAPI, React 18, SQLite, Librosa

**Quick Start:**
```bash
cd VoiceStudio-Integrated
./start-dev.sh
# Access: http://localhost:5173
```

**Documentation:**
- [VoiceStudio README](./VoiceStudio-Integrated/README.md)
- [Voice Cloning Guide](./VoiceStudio-Integrated/STEP6_VOICE_CLONING.md)
- [Local Setup Guide](./VoiceStudio-Integrated/LOCAL_SETUP.md)
- [Architecture](./VoiceStudio-Integrated/ARCHITECTURE.md)

---

## 🎵 Audio & Voice Processing

### [VoiceStudio](./VoiceStudio)
Original voice studio implementation with basic voice management features.

### [bark](./bark)
High-quality text-to-speech system with multilingual support.

### [TTS](./TTS)
Text-to-speech synthesis engine with multiple backends.

### [whisper](./whisper)
OpenAI's automatic speech recognition (ASR) system.

### [speech_recognition](./speech_recognition)
Speech recognition library with multiple backends.

### [demucs](./demucs)
Music source separation using deep learning.

---

## 🧠 ML Frameworks & Tools

### [llama.cpp](./llama.cpp)
Lightweight C++ inference engine for LLMs - **Status:** Complete implementation

### [onnxruntime](./onnxruntime)
High-performance inference engine for ONNX models.

### [onnx](./onnx)
Open Neural Network Exchange format tools.

### [tflite-micro](./tflite-micro)
TensorFlow Lite Micro for embedded machine learning.

### [NeMo](./NeMo)
NVIDIA's open-source conversational AI toolkit.

---

## 🎼 Audio Processing Libraries

### [librosa](./librosa)
Python library for audio analysis and processing.

### [julius](./julius)
Digital signal processing library for PyTorch.

### [VITS-fast-fine-tuning](./VITS-fast-fine-tuning)
Fast fine-tuning implementation for VITS (Variational Inference with adversarial learning for end-to-end Text-to-Speech).

### [espnet](./espnet)
End-to-end speech processing toolkit.

### [rasa](./rasa)
Open-source conversational AI framework.

---

## 🛠️ Utilities

### [DNS-Challenge](./DNS-Challenge)
DNS challenge implementation utilities.

### [text-generation-webui](./text-generation-webui)
Web interface for text generation models.

---

## 📊 Project Statistics

| Category | Count | Focus |
|----------|-------|-------|
| Production Ready | 1 | VoiceStudio-Integrated |
| Audio Processing | 7 | Voice, TTS, ASR, Source Separation |
| ML Frameworks | 5 | Inference, Model Optimization |
| Libraries | 4 | DSP, Audio Analysis, AI |
| Utilities | 3 | Tools & Web UIs |
| **Total** | **20** | Enhanced Implementations |

---

## 🚀 Getting Started

### For VoiceStudio (Recommended)
```bash
cd VoiceStudio-Integrated
./start-dev.sh
```

### For Other Projects
Each project includes its own README with specific setup instructions. Check the project directory for:
- `README.md` - Project overview
- `requirements.txt` - Python dependencies
- `package.json` - Node dependencies (if applicable)

---

## 📁 Repository Structure

```
AyyGIT/
├── VoiceStudio-Integrated/    ⭐ Main project - Production ready
│   ├── api_server.py          FastAPI backend
│   ├── core_engine.py         Voice processing engine
│   ├── database.py            SQLite layer
│   ├── frontend/              React application
│   ├── requirements.txt        Python dependencies
│   ├── LOCAL_SETUP.md         Local development guide
│   └── README.md              Full documentation
│
├── Audio & Voice Processing/
│   ├── VoiceStudio/
│   ├── bark/
│   ├── TTS/
│   ├── whisper/
│   ├── speech_recognition/
│   └── demucs/
│
├── ML Frameworks/
│   ├── llama.cpp/
│   ├── onnxruntime/
│   ├── onnx/
│   ├── tflite-micro/
│   └── NeMo/
│
├── Audio Libraries/
│   ├── librosa/
│   ├── julius/
│   ├── VITS-fast-fine-tuning/
│   ├── espnet/
│   └── rasa/
│
└── Documentation/
    ├── README.md              Main overview
    ├── PROJECTS.md            This file
    ├── SETUP.md               Quick setup reference
    ├── .gitignore             Git ignore rules
    └── CONTRIBUTING.md        Contribution guidelines
```

---

## 🔄 Workflow

1. **Explore** - Browse projects in their respective directories
2. **Setup** - Follow project-specific README instructions
3. **Develop** - Make changes and test locally
4. **Document** - Update relevant documentation
5. **Commit** - Use clear, descriptive commit messages
6. **Push** - Push to your feature branch

---

## 📝 Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on:
- Code style and standards
- Commit message format
- Pull request process
- Documentation requirements

---

## 📄 License

Each project may have its own licensing terms. Check individual project directories for license files.

---

## 🎯 Key Takeaways

- **VoiceStudio-Integrated** is the main production-ready project
- All projects are enhanced versions of original repositories
- Documentation is comprehensive and organized
- Setup is streamlined for quick development start
- Contribution guidelines ensure code quality

Happy coding! 🚀
