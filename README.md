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

## Hardware acceleration

Claudescribe detects your hardware automatically and picks the best settings. No configuration needed.

### Apple Silicon (M1 / M2 / M3 / M4)

By default, Claudescribe runs on CPU using CTranslate2's ARM64-optimised build (Apple Accelerate framework). This is already faster than Intel, and requires no extra steps.

**Optional: enable Metal GPU acceleration (experimental)**

This branch includes experimental support for [mlx-whisper](https://github.com/ml-explore/mlx-examples/tree/main/whisper), which runs inference on the GPU cores built into Apple Silicon via Apple's MLX framework. To try it:

```bash
pip install mlx-whisper
make run
```

That's it — Claudescribe detects `mlx-whisper` automatically and uses the Metal GPU. No other config needed.

**What to expect:**
- Faster transcription, especially on `large-v3` and `turbo` models
- The progress bar jumps from 0% to 100% on completion instead of filling gradually — mlx-whisper processes the whole file at once, so there is no incremental progress to report
- Models are downloaded from Hugging Face (`mlx-community/whisper-*`) on first use, separately from the faster-whisper model cache

**To go back to CPU**, uninstall it:

```bash
pip uninstall mlx-whisper
```

> **Note:** `mlx-whisper` is Apple-only. Do not install it on Windows or Linux.

### NVIDIA GPU (Windows or Linux)

If you have an NVIDIA GPU, Claudescribe will use it automatically — but you need the CUDA runtime and cuDNN installed first.

**Requirements:**
- NVIDIA driver 525 or later (check: `nvidia-smi`)
- CUDA 12.3 or later
- cuDNN 9.x

**Step-by-step on Windows:**

1. Check your driver version:
   ```powershell
   nvidia-smi
   ```
   The top-right corner shows the maximum CUDA version your driver supports. It must be **12.3 or higher**. If it's lower, update your driver from [nvidia.com/drivers](https://www.nvidia.com/drivers/).

2. Install the **CUDA Toolkit 12.x** from [developer.nvidia.com/cuda-downloads](https://developer.nvidia.com/cuda-downloads). Select: Windows → x86_64 → your Windows version → exe (local).

3. Install **cuDNN 9.x** from [developer.nvidia.com/cudnn](https://developer.nvidia.com/cudnn) (free NVIDIA account required). Download the zip for CUDA 12.x, then copy its `bin/`, `include/`, and `lib/` folders into your CUDA installation directory (typically `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.x\`).

4. Restart your terminal, then verify:
   ```powershell
   nvcc --version   # should show 12.x
   ```

5. Install Claudescribe as normal. When you start transcribing, the GPU is picked up automatically. You can confirm in the terminal output — faster-whisper will log the device it's using.

**Expected speedup:** 5–10× faster than CPU for large models, depending on your GPU.

> **Not sure it's working?** Run a transcription and watch the GPU usage in Task Manager → Performance → GPU. It should spike while transcription runs.

### Intel / AMD CPU (no GPU)

The app runs on CPU by default using optimised BLAS libraries. On modern multi-core CPUs this is perfectly usable for the `tiny`, `base`, and `turbo` models.

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

## Configuration

### Port

By default the server runs on port **8000**. Override it with the `PORT` environment variable:

```bash
# macOS / Linux — with make
PORT=9000 make run

# macOS / Linux — without make
PORT=9000 python main.py

# Windows (PowerShell)
$env:PORT = "9000"; python main.py

# Windows (Command Prompt)
set PORT=9000 && python main.py
```

You can also export it for the whole shell session so you don't have to repeat it:

```bash
export PORT=9000   # macOS / Linux
make run
```

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

If you changed the port, pass `PORT` to both:

```bash
PORT=9000 uvicorn backend.app:app --reload --port 9000
PORT=9000 npm run dev   # (inside frontend/)
```

Frontend dev server runs at `http://localhost:5173` and proxies `/api` to the backend.

Run tests:

```bash
python -m pytest tests/ -v
```

## Built with Claude Code

This project was designed and implemented entirely through [Claude Code](https://claude.ai/code) using **Claude Sonnet 4.6**, Anthropic's CLI coding agent.

### How it was built

The implementation followed a structured, plan-driven workflow:

1. **Brainstorming session** — requirements, architecture, and key technical decisions were explored interactively before any code was written. Decisions like using `faster-whisper` over the official Whisper library (4× faster, lazy segment generator for real-time progress, native word timestamps), persistent JSON storage, and the binary-search word-sync approach were all arrived at collaboratively.

2. **Written implementation plan** — the outcome of the brainstorm was a detailed 9-step plan covering every file, data format, API endpoint, and frontend component, before a single line of code was touched.

3. **Subagent-driven development** — each of the 9 steps was handed to a fresh Claude subagent with full context from the plan. A separate spec-compliance reviewer and code quality reviewer subagent ran after each step, catching issues (missing `fsync` before atomic rename, stale closure in polling hook, etc.) before moving on.

4. **Git worktree isolation** — all implementation work happened in an isolated `.worktrees/main` branch, keeping `main` clean until the full feature was reviewed and merged.

5. **TDD throughout** — tests were written alongside each backend module. The 27-test suite covers storage, transcription service bookkeeping, and all API endpoints including edge cases.

The full implementation — 38 files, ~3900 lines of Python, TypeScript, CSS, and config — was produced across a single Claude Code session, with the human role limited to reviewing decisions, answering clarifying questions, and verifying the running app.
