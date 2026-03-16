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

> **Recommended: use WSL (Windows Subsystem for Linux)**
>
> WSL gives you a full Linux shell on Windows and lets you follow the **macOS instructions** exactly — `make install`, `make run`, GPU support, everything. It's the smoothest Windows experience and what most developers use.
>
> **One-time WSL setup** (run in PowerShell as Administrator):
> ```powershell
> wsl --install
> ```
> Restart when prompted, then open the **Ubuntu** app from the Start menu and follow the [macOS installation steps](#installation--macos) above.
>
> If you'd rather stay in native Windows (PowerShell / Command Prompt), continue with the steps below.

---

> **Tip:** Use [Windows Terminal](https://aka.ms/terminal) instead of the old `cmd.exe`. It handles virtual environment activation correctly, supports colour output, and lets you run multiple tabs side by side. Install it from the Microsoft Store or with `winget install Microsoft.WindowsTerminal`.

> **Important — PowerShell execution policy:** PowerShell blocks scripts by default. Run this once before anything else, or `npm` and the `.bat` scripts will fail with a "running scripts is disabled" error:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

### 1. Install prerequisites

**Option A — `winget` (fastest, Windows 10/11 built-in):**

```powershell
winget install Python.Python.3.12 --source winget
winget install OpenJS.NodeJS.LTS --source winget
winget install Git.Git --source winget
```

Restart your terminal after this, then verify:

```powershell
python --version
node --version
npm --version
```

**Option B — manual download:**

- Python: [python.org/downloads](https://www.python.org/downloads/) — check **"Add python.exe to PATH"** on the first screen
- Node.js: [nodejs.org](https://nodejs.org/) — run the LTS installer with all defaults
- Git: [git-scm.com](https://git-scm.com/) — run the installer with all defaults

### 2. Clone the repository

If you have Git installed:

```powershell
git clone https://github.com/xpepper/claudescribe.git
cd claudescribe
```

Or download the ZIP from GitHub and extract it.

### 3. Install dependencies and run

Two batch scripts replace the `make` commands from the macOS instructions:

```powershell
.\setup.bat
```

This installs all Python and frontend dependencies and builds the frontend. You only need to run it once (or after pulling updates that change dependencies).

```powershell
.\run.bat
```

This builds the frontend and starts the server. Your browser will open automatically at `http://localhost:8000`.

> **Note:** If you prefer the `make` workflow, install [Make for Windows](https://gnuwin32.sourceforge.net/packages/make.htm) and `make install` / `make run` work the same as on macOS.

### Troubleshooting — Windows

**"permission denied" or "failed to create virtual environment" when running `setup.bat`**

This usually means a leftover `.venv` folder from a previous attempt is locked. `setup.bat` removes it automatically before creating a new one. If it still fails, delete the `.venv` folder manually and run `setup.bat` again.

If the error persists, you may have Python installed from the **Microsoft Store**. That version has restrictions that can prevent venv creation. Uninstall it and reinstall from [python.org/downloads](https://www.python.org/downloads/) instead.

**"running scripts is disabled on this system"**

You skipped the execution policy step above. Run this once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then re-run the failed command.

**`python` not found after installation**

Close and reopen Windows Terminal (or run `refreshenv` if you have Chocolatey). The PATH update from the installer only takes effect in new shell sessions.

**`winget` not available**

`winget` ships with Windows 11 and most up-to-date Windows 10 installs. If it's missing, install the [App Installer](https://apps.microsoft.com/detail/9NBLGGH4NNS1) from the Microsoft Store, or use the manual download links in Option B above.

**`ctranslate2.dll` not found / app crashes on startup**

`ctranslate2` requires the Microsoft Visual C++ Redistributable runtime. On a fresh Windows install it is often missing. Download and run the installer:

```
https://aka.ms/vs/17/release/vc_redist.x64.exe
```

Restart your terminal and run `python main.py` again.

**Running Windows on ARM (e.g. Surface Pro X, or a UTM/Parallels VM on Apple Silicon)**

`ctranslate2` (a core dependency of faster-whisper) does not currently provide Windows ARM64 wheels. You must install the **x86-64 version of Python** instead — Windows ARM runs x86-64 applications via emulation and the x86-64 wheels will work correctly.

Download the **"Windows installer (64-bit)"** from [python.org/downloads](https://www.python.org/downloads/) — that is the x86-64 build. Do not use the ARM64 installer or the Microsoft Store version. Then re-run `setup.bat`.

You will also need the Visual C++ Redistributable — see the `ctranslate2.dll` entry above.

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
