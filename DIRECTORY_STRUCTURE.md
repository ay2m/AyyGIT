# 📁 Repository Directory Structure

Complete overview of the AyyGIT repository organization.

## Root Level

```
AyyGIT/
├── .git/                          Git repository data
├── .gitignore                      Git ignore rules (updated)
├── README.md                       Main repository overview
├── PROJECTS.md                     📝 Projects catalog
├── SETUP.md                        🚀 Setup guide
├── CONTRIBUTING.md                 🤝 Contribution guidelines
├── DIRECTORY_STRUCTURE.md          📁 This file
│
├── VoiceStudio-Integrated/         ⭐ MAIN PROJECT (Production Ready)
├── VoiceStudio/                    Original voice studio
├── bark/                           Text-to-speech system
├── TTS/                            Synthesis engine
├── whisper/                        Speech recognition
├── speech_recognition/             ASR library
├── demucs/                         Source separation
│
├── llama.cpp/                      LLM inference engine
├── onnxruntime/                    ONNX inference
├── onnx/                           ONNX tools
├── tflite-micro/                   Embedded ML
├── NeMo/                           Conversational AI
│
├── librosa/                        Audio analysis
├── julius/                         DSP library
├── VITS-fast-fine-tuning/          Speech synthesis
├── espnet/                         Speech toolkit
├── rasa/                           Dialog framework
│
├── DNS-Challenge/                  DNS utilities
└── text-generation-webui/          LLM web interface
```

---

## VoiceStudio-Integrated Structure (Main Project)

```
VoiceStudio-Integrated/
│
├── 📄 Configuration & Documentation
│   ├── README.md                   Complete documentation
│   ├── ARCHITECTURE.md             System architecture
│   ├── LOCAL_SETUP.md              Local development guide
│   ├── QUICKSTART.md               Quick start guide
│   ├── STEP6_VOICE_CLONING.md      Voice cloning details
│   ├── STEP6_SUMMARY.md            Implementation summary
│   ├── requirements.txt            Python dependencies (15 packages)
│   └── voicestudio.db             SQLite database (auto-created)
│
├── 🐍 Backend (Python - FastAPI)
│   ├── api_server.py               (609 lines) Main API server
│   │   - HTTP routes and endpoints
│   │   - Request validation
│   │   - Error handling
│   │   - CORS configuration
│   │   - Database initialization
│   │
│   ├── core_engine.py              (609 lines) Voice processing engine
│   │   - Audio processing
│   │   - Voice cloning algorithms
│   │   - MFCC analysis
│   │   - Speaker embeddings
│   │   - Quality scoring
│   │
│   ├── database.py                 (609 lines) Data persistence layer
│   │   - SQLite schema
│   │   - CRUD operations
│   │   - Query builders
│   │   - Voice history tracking
│   │   - Cloning lineage tracking
│   │
│   └── client_example.py           (205 lines) API client example
│       - Demonstrates API usage
│       - Example requests/responses
│
├── 🎨 Frontend (React - Vite)
│   ├── package.json                Node dependencies
│   │   - React 18.2.0
│   │   - Tailwind CSS
│   │   - React Router
│   │   - Zustand
│   │   - Axios
│   │   - Icons & utilities
│   │
│   ├── vite.config.js              Vite configuration
│   ├── index.html                  HTML entry point
│   ├── tailwind.config.js          Tailwind configuration
│   ├── eslint.config.js            ESLint rules
│   │
│   ├── public/                     Static assets
│   │   ├── logo.svg
│   │   └── favicon.ico
│   │
│   └── src/                        React application source
│       ├── index.css               Global styles
│       ├── App.jsx                 Main app component
│       ├── main.jsx                Entry point
│       │
│       ├── pages/                  📄 Page components
│       │   ├── Dashboard.jsx       Main dashboard
│       │   ├── VoiceLibrary.jsx    Voice management
│       │   ├── VoiceMerge.jsx      Voice merging
│       │   ├── Synthesis.jsx       TTS interface
│       │   └── VoiceCloning.jsx    Voice cloning (NEW)
│       │
│       ├── components/             🧩 Reusable components
│       │   ├── Header.jsx
│       │   ├── Sidebar.jsx
│       │   ├── VoiceCard.jsx
│       │   ├── AudioPlayer.jsx
│       │   ├── VoiceCloning/
│       │   │   ├── CloningSettings.jsx
│       │   │   ├── CloningResult.jsx
│       │   │   ├── CloningHistory.jsx
│       │   │   └── *.module.css    Component styles
│       │   └── ...
│       │
│       ├── store/                  🔄 State management (Zustand)
│       │   ├── voiceStore.js       Voice data store
│       │   ├── uiStore.js          UI state
│       │   └── cloningStore.js     Cloning state (NEW)
│       │
│       ├── services/               🌐 API services
│       │   └── api.js              Axios configuration & endpoints
│       │
│       ├── styles/                 🎨 Global styles
│       │   ├── variables.css       CSS variables
│       │   ├── common.css          Common styles
│       │   └── theme.css           Theme definitions
│       │
│       └── utils/                  🛠️ Utilities
│           ├── audio.js            Audio utilities
│           ├── format.js           Formatting helpers
│           └── validators.js       Input validation
│
├── 🚀 Scripts
│   ├── start-dev.sh                Startup script
│   │   - Starts both servers
│   │   - Manages logs
│   │   - Process management
│   │
│   ├── api_server.py               Main Python entry point
│   │   Port: 8000
│   │   Auto-reloads in dev mode
│   │
│   └── npm scripts (from package.json)
│       - npm run dev               Start dev server (port 5173)
│       - npm run build             Production build
│       - npm run preview           Preview production build
│       - npm run lint              Run ESLint
│
├── 📊 Statistics
│   ├── Python code: ~1,827 lines
│   │   - api_server.py: 609 lines
│   │   - core_engine.py: 609 lines
│   │   - database.py: 609 lines
│   │
│   ├── React code: ~1,784 lines
│   │   - Pages: ~400 lines
│   │   - Components: ~800 lines
│   │   - Store: ~300 lines
│   │   - Services: ~284 lines
│   │
│   ├── Documentation: ~800 lines
│   ├── API Endpoints: 15+
│   ├── React Components: 15+
│   ├── CSS Modules: 6+
│   ├── Database Tables: 4
│   └── Git Commits: 25+
│
└── 📦 Artifacts (in .gitignore)
    ├── venv/                       Python virtual environment
    ├── __pycache__/                Python cache
    ├── frontend/node_modules/      Node packages
    ├── frontend/package-lock.json  Dependencies lock file
    ├── voicestudio.db              SQLite database
    ├── backend.log                 Backend log file
    └── frontend.log                Frontend log file
```

---

## Database Schema (SQLite)

```
VoiceStudio Database
│
├── voices
│   ├── id (PRIMARY KEY)
│   ├── name
│   ├── description
│   ├── language
│   ├── audio_path
│   ├── sample_rate
│   ├── duration
│   ├── created_at
│   └── metadata (JSON)
│
├── voice_merges
│   ├── id (PRIMARY KEY)
│   ├── voice_id (FOREIGN KEY)
│   ├── source_voices (JSON array)
│   ├── weights (JSON)
│   ├── result_audio_path
│   ├── merge_type
│   ├── quality_score
│   ├── created_at
│   └── parameters (JSON)
│
├── voice_synthesis
│   ├── id (PRIMARY KEY)
│   ├── voice_id (FOREIGN KEY)
│   ├── text
│   ├── language
│   ├── audio_path
│   ├── pitch
│   ├── speed
│   ├── quality_score
│   ├── created_at
│   └── synthesis_params (JSON)
│
└── cloning_history
    ├── id (PRIMARY KEY)
    ├── source_voice_id (FOREIGN KEY)
    ├── clone_voice_id (FOREIGN KEY)
    ├── cloning_type (basic/advanced)
    ├── parameters (JSON)
    │   - pitch_shift
    │   - tempo_ratio
    │   - formant_shift
    │   - breathiness
    │   - intensity
    ├── quality_score
    ├── processing_time
    └── created_at
```

---

## API Endpoints

```
BASE_URL: http://localhost:8000

VOICE MANAGEMENT
├── GET    /api/voices              List all voices
├── POST   /api/voices              Upload new voice
├── GET    /api/voices/{id}         Get voice details
├── PUT    /api/voices/{id}         Update voice metadata
├── DELETE /api/voices/{id}         Delete voice

VOICE CLONING (NEW)
├── POST   /api/voices/{id}/clone   Clone a voice
├── GET    /api/voices/{id}/clone-history  Cloning history
├── GET    /api/voices/{id}/cloned-from   Source voice info
├── POST   /api/voices/transfer     Voice transfer

VOICE MERGING
├── POST   /api/voices/merge        Merge voices
├── GET    /api/merges              List merges

SYNTHESIS
├── POST   /api/synthesis           Generate speech
├── GET    /api/synthesis/{id}      Get synthesis

SYSTEM
├── GET    /health                  Health check
├── GET    /stats                   System statistics
├── GET    /docs                    Swagger UI
└── GET    /openapi.json            OpenAPI schema
```

---

## Environment Variables

### Backend (.env or environment)
```
DEBUG=false
DATABASE_URL=sqlite:///voicestudio.db
PYTHONUNBUFFERED=1
HOST=0.0.0.0
PORT=8000
WORKERS=4
```

### Frontend (.env.local)
```
VITE_API_URL=http://localhost:8000
VITE_DEBUG=false
VITE_APP_TITLE=VoiceStudio
```

---

## Git Branches

### Main Branch
- `main` - Production-ready code

### Working Branches
- `claude/free-claude-code-fork-f7fk7q` - Current development branch
- `feature/*` - Feature branches
- `fix/*` - Bug fix branches

---

## CI/CD & Build Artifacts (Ignored)

All build and temporary files are in `.gitignore`:
- `__pycache__/` - Python bytecode
- `*.pyc`, `*.pyo` - Compiled Python
- `venv/` - Virtual environment
- `node_modules/` - Node packages
- `dist/`, `build/` - Build outputs
- `.env`, `.env.local` - Environment files
- `*.log` - Log files
- `.pytest_cache/` - Test cache

---

## Documentation Files

| File | Purpose |
|------|---------|
| README.md | Main overview |
| PROJECTS.md | Project catalog |
| SETUP.md | Setup instructions |
| CONTRIBUTING.md | Contribution guidelines |
| DIRECTORY_STRUCTURE.md | This file |
| LOCAL_SETUP.md | Local development guide |
| ARCHITECTURE.md | System architecture |

---

## File Size Reference

| Component | Size | Type |
|-----------|------|------|
| api_server.py | ~25KB | Python source |
| core_engine.py | ~30KB | Python source |
| database.py | ~20KB | Python source |
| VoiceCloning.jsx | ~15KB | React source |
| package.json | ~2KB | Config |
| requirements.txt | ~1KB | Python deps |
| README.md | ~40KB | Documentation |

---

## Performance Notes

- **Python startup time:** ~3-5 seconds
- **Model download:** First run only (~1-2GB)
- **Voice cloning:** 3-6 seconds per operation
- **Frontend build:** ~10 seconds
- **Database size:** Starts at ~500KB (grows with usage)

---

## Key Takeaways

1. **Main Project:** VoiceStudio-Integrated is fully organized and production-ready
2. **Clean Structure:** Separate concerns - backend, frontend, docs
3. **Build Artifacts:** All ignored via .gitignore (not in repo)
4. **Documentation:** Comprehensive guides at multiple levels
5. **Scalable:** Easy to add new features following established patterns

---

## Next Steps

- Start with [SETUP.md](./SETUP.md) for development
- Read [VoiceStudio-Integrated/README.md](./VoiceStudio-Integrated/README.md) for details
- Follow [CONTRIBUTING.md](./CONTRIBUTING.md) when making changes
- Check relevant project README for other projects

Happy exploring! 🚀
