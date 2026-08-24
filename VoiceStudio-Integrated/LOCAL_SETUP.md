# VoiceStudio Local Setup Guide

## ✅ Setup Complete!

Both backend and frontend dependencies have been installed and are ready to run.

## Starting the Project

### Terminal 1: Start FastAPI Backend Server

```bash
cd /home/user/AyyGIT/VoiceStudio-Integrated
source venv/bin/activate
python api_server.py
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

The backend will be available at: **http://localhost:8000**

### Terminal 2: Start React Frontend Dev Server

```bash
cd /home/user/AyyGIT/VoiceStudio-Integrated/frontend
npm run dev
```

**Expected output:**
```
  VITE v5.x.x  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

The frontend will be available at: **http://localhost:5173**

## First Run Notes

On first run, the backend will download required ML models (Whisper speech recognition model). This is a one-time download (~1-2GB) and may take a few minutes.

## API Endpoints

The backend provides these voice cloning endpoints:

- `POST /api/voices/{id}/clone` - Clone a voice with parameters
- `GET /api/voices/{id}/clone-history` - Get cloning history for a voice
- `GET /api/voices/{id}/cloned-from` - Get the source voice a clone was derived from
- `POST /api/voices/transfer` - Transfer voice characteristics between voices

## Frontend Features

- **Voice Library**: Browse and manage voice samples
- **Voice Cloning**: Clone voices with adjustable parameters (pitch, speed, intensity)
- **Cloning History**: View the complete history of clones for each voice
- **Audio Playback**: Play original and cloned audio samples

## Testing Voice Cloning

1. Open http://localhost:5173 in your browser
2. Navigate to "Voice Cloning" section
3. Select a voice from the library
4. Adjust cloning parameters (Basic or Advanced mode)
5. Click "Start Cloning" to clone the voice
6. View results and cloning history

## Troubleshooting

### Port Already in Use
If port 8000 or 5173 is already in use:

**Backend:** Modify `api_server.py` line (change port in uvicorn.run)
**Frontend:** `npm run dev -- --port 5174`

### Module Not Found Errors
Ensure virtual environment is activated:
```bash
source venv/bin/activate
```

### Network/Model Download Issues
The backend needs internet access to download ML models on first run. If you get connection errors, ensure your internet connection is working.

### Database Errors
The database is automatically initialized when the backend starts. If you encounter issues:
```bash
# Delete and recreate the database
rm voicestudio.db
# Restart the backend
python api_server.py
```

## Project Structure

```
VoiceStudio-Integrated/
├── api_server.py          # FastAPI backend server
├── core_engine.py         # Voice processing and cloning engine
├── database.py            # SQLite database layer
├── requirements.txt       # Python dependencies
├── venv/                  # Virtual environment (installed)
└── frontend/
    ├── src/
    │   ├── components/    # React components
    │   ├── pages/         # Page components
    │   └── App.jsx
    ├── package.json       # Node dependencies (installed)
    └── vite.config.js
```

## Development Notes

- **Python**: 3.11.15
- **FastAPI**: 0.104.1
- **React**: 18.2.0
- **Vite**: 5.0+
- **Database**: SQLite (voicestudio.db)

Happy voice cloning! 🎤
