# Claudescribe

Local lecture transcription with karaoke-style word highlighting. Upload an audio file, transcribe it locally with [faster-whisper](https://github.com/SYSTRAN/faster-whisper), then play it back with every word highlighted in sync.

No cloud. No API keys. Runs entirely on your machine.

---

## Requirements

- Python 3.10 or later
- Node.js 18 or later
- ~500 MB disk space (for the `turbo` Whisper model, downloaded on first use)

---

## Installation — macOS

### 1. Install Python

Check if Python 3.10+ is already installed:

```bash
python3 --version
```

If not, install it via [Homebrew](https://brew.sh):

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python
```

### 2. Install Node.js

```bash
brew install node
```

Verify:

```bash
node --version   # should be 18+
npm --version
```

### 3. Clone the repository

```bash
git clone https://github.com/xpepper/claudescribe.git
cd claudescribe
```

### 4. Create a Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

> You'll need to run `source .venv/bin/activate` each time you open a new terminal before starting the app.

### 5. Install all dependencies

```bash
make install
```

This runs `pip install -r requirements.txt` and `npm install` inside `frontend/`.

### 6. Run the app

```bash
make run
```

This builds the frontend and starts the server. Your browser will open automatically at `http://localhost:8000`.

---

## Installation — Windows

### 1. Install Python

Download the **Python 3.12** installer from [python.org/downloads](https://www.python.org/downloads/).

During installation:
- **Check "Add python.exe to PATH"** on the first screen
- Click "Install Now"

Verify in a new Command Prompt or PowerShell window:

```powershell
python --version
```

### 2. Install Node.js

Download the **LTS** installer from [nodejs.org](https://nodejs.org/).

Run the installer with all defaults. Verify:

```powershell
node --version
npm --version
```

### 3. Clone the repository

If you have Git installed:

```powershell
git clone https://github.com/xpepper/claudescribe.git
cd claudescribe
```

Or download the ZIP from GitHub and extract it.

### 4. Create a Python virtual environment

```powershell
python -m venv .venv
.venv\Scripts\activate
```

> You'll need to run `.venv\Scripts\activate` each time you open a new terminal before starting the app.
>
> If you get an error about script execution policy, run this first:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

### 5. Install Python dependencies

```powershell
pip install -r requirements.txt
```

### 6. Install frontend dependencies

```powershell
cd frontend
npm install
cd ..
```

### 7. Build the frontend

```powershell
cd frontend
npm run build
cd ..
```

### 8. Run the app

```powershell
python main.py
```

Your browser will open automatically at `http://localhost:8000`.

> **Note:** Windows does not have `make`, so you run the steps manually. If you install [Make for Windows](https://gnuwin32.sourceforge.net/packages/make.htm) or use [WSL](https://learn.microsoft.com/en-us/windows/wsl/), `make run` works the same as on macOS.

---

## Usage

1. **Upload** an audio file (MP3, M4A, WAV, MP4, OGG, FLAC, WEBM)
2. **Select a model** — `tiny` is fastest, `turbo` gives the best accuracy/speed balance
3. **Watch the progress bar** fill as transcription runs locally
4. **Click the title** to open the transcript
5. **Press play** — words highlight in sync with the audio
6. **Click any word** to jump the audio to that point
7. **Double-click the title** to rename
8. **Export** as `.txt` or `.srt` (subtitles) from the detail page

---

## Model sizes

| Model | Speed | Accuracy | Download size |
|-------|-------|----------|---------------|
| tiny | fastest | lowest | ~75 MB |
| base | fast | decent | ~145 MB |
| small | moderate | good | ~465 MB |
| medium | slow | better | ~1.5 GB |
| large-v3 | slowest | best | ~3 GB |
| turbo | fast | near-large | ~800 MB |

Models are downloaded automatically on first use and cached locally.

---

## Development

Run backend and frontend separately for hot reload:

```bash
# Terminal 1 — backend
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
uvicorn backend.app:app --reload --port 8000

# Terminal 2 — frontend
cd frontend
npm run dev
```

Frontend dev server runs at `http://localhost:5173` and proxies `/api` to the backend.

Run tests:

```bash
python -m pytest tests/ -v
```
