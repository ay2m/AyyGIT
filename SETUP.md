# 🚀 Setup Guide - AyyGIT Repository

Quick reference for setting up projects in the AyyGIT collection.

## ⭐ VoiceStudio-Integrated (Recommended)

The main production-ready project with complete voice processing capabilities.

### Prerequisites
- Python 3.11+
- Node.js 16+ and npm
- 2GB+ free disk space (for ML models)

### Quick Setup (Recommended)
```bash
cd VoiceStudio-Integrated

# Automatic setup
./start-dev.sh
```

**Access:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Manual Setup

**Terminal 1 - Backend:**
```bash
cd VoiceStudio-Integrated
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python api_server.py
```

**Terminal 2 - Frontend:**
```bash
cd VoiceStudio-Integrated/frontend
npm install
npm run dev
```

### First Run
- Backend will download ML models on first startup (~1-2GB)
- This is a one-time process
- Ensure you have internet connection

### Troubleshooting
- **Port in use:** Change port in `api_server.py` or use `npm run dev -- --port 5174`
- **Module not found:** Ensure virtual environment is activated
- **Database errors:** Delete `voicestudio.db` and restart backend

**Full Documentation:** [LOCAL_SETUP.md](./VoiceStudio-Integrated/LOCAL_SETUP.md)

---

## 🎵 Other Projects

### Generic Python Project Setup

```bash
cd <project-directory>
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py  # or relevant entry point
```

### Generic Node Project Setup

```bash
cd <project-directory>
npm install
npm start  # or npm run dev
```

### Mixed Projects (Python + Node)

1. Follow Python setup for backend
2. Follow Node setup for frontend in separate terminal

---

## 🛠️ Common Commands

### Virtual Environment
```bash
# Create
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Deactivate
deactivate
```

### Package Management
```bash
# Python
pip install -r requirements.txt
pip freeze > requirements.txt

# Node
npm install
npm update
npm list
```

### Development
```bash
# Python linting
black .
flake8 .
pytest

# Node linting
npm run lint
npm run format
```

---

## 🔧 Environment Configuration

### Python
Create `.env` file in project root:
```env
DEBUG=true
PYTHONUNBUFFERED=1
DATABASE_URL=sqlite:///voicestudio.db
```

### Node
Create `.env.local` in frontend directory:
```env
VITE_API_URL=http://localhost:8000
VITE_DEBUG=true
```

---

## 📋 Project-Specific Setup

### [llama.cpp](./llama.cpp)
```bash
cd llama.cpp
make
./main -m model.gguf -p "Your prompt"
```

### [whisper](./whisper)
```bash
cd whisper
pip install -e .
whisper audio.mp3 --model base
```

### [TTS](./TTS)
```bash
cd TTS
pip install -e .
tts --text "Hello" --model_name "tts_models/en/ljspeech/glow-tts"
```

### [demucs](./demucs)
```bash
cd demucs
pip install -e .
demucs song.mp3
```

---

## 📊 System Requirements

| Project | CPU | RAM | Storage | Python |
|---------|-----|-----|---------|--------|
| VoiceStudio-Integrated | Dual-core | 4GB | 2GB | 3.11+ |
| llama.cpp | Quad-core | 8GB | 5GB+ | 3.8+ |
| whisper | Dual-core | 2GB | 1GB+ | 3.7+ |
| TTS | Quad-core | 4GB | 2GB+ | 3.6+ |
| demucs | Quad-core | 4GB | 2GB+ | 3.7+ |

---

## 🐛 Debugging

### Enable Debug Mode
```bash
# Python
export DEBUG=true
export PYTHONUNBUFFERED=1

# Node
export VITE_DEBUG=true
export DEBUG=*
```

### Check Logs
```bash
# Backend logs
tail -f backend.log

# Frontend logs
# Check browser console (F12)
```

### Clear Caches
```bash
# Python
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Node
rm -rf node_modules
npm cache clean --force
npm install
```

---

## 🔒 Security Best Practices

1. **Environment Variables**
   - Never commit `.env` files
   - Use `.env.example` for templates
   - Always keep secrets out of version control

2. **Dependencies**
   - Regularly update packages: `pip install --upgrade -r requirements.txt`
   - Run security audits: `pip-audit`, `npm audit`
   - Pin versions in production

3. **Database**
   - Use strong passwords for database credentials
   - Don't use default SQLite in production
   - Backup databases regularly

---

## 📚 Additional Resources

- [VoiceStudio Documentation](./VoiceStudio-Integrated/README.md)
- [Projects Overview](./PROJECTS.md)
- [Contributing Guidelines](./CONTRIBUTING.md)
- Individual project READMEs

---

## 🆘 Getting Help

1. Check project-specific README
2. Review [PROJECTS.md](./PROJECTS.md) for project details
3. See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines
4. Check individual project documentation

---

## ✅ Setup Checklist

- [ ] Python 3.11+ installed
- [ ] Node.js 16+ installed
- [ ] Git configured
- [ ] Clone repository: `git clone <repo-url>`
- [ ] Choose project to work on
- [ ] Follow project-specific setup
- [ ] Verify running (access URLs, test endpoints)
- [ ] Read project documentation
- [ ] Create feature branch for changes

Happy coding! 🚀
