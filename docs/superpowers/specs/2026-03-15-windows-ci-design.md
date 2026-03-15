# Windows CI Workflow — Design Spec

**Date:** 2026-03-15
**Status:** Approved

---

## Goal

Add a GitHub Actions workflow that verifies the Windows onboarding experience works end-to-end, without requiring a Windows machine. The workflow runs on every push and pull request to `main`.

---

## Scope

Two phases, delivered incrementally in the same workflow file:

1. **Phase 1 — Setup verify:** confirm `setup.bat` completes without error (dependencies install, frontend builds)
2. **Phase 2 — Smoke test:** confirm the server starts and responds correctly on `http://localhost:8000/api/health`

---

## File

`.github/workflows/windows.yml`

---

## Trigger

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
```

---

## Job: `windows-setup`

Runner: `windows-latest`

### Steps

#### Phase 1 — Setup verify

| Step | Action / Command | Failure means |
|------|-----------------|---------------|
| Checkout | `actions/checkout@v4` | — |
| Setup Python 3.12 | `actions/setup-python@v5` with `python-version: '3.12'` | — |
| Setup Node.js LTS | `actions/setup-node@v4` with `node-version: 'lts/*'` | — |
| Run setup.bat | `shell: cmd`, `run: setup.bat` | Install or build step failed |

#### Phase 2 — Smoke test

| Step | Action / Command | Failure means |
|------|-----------------|---------------|
| Start server | PowerShell: `$proc = Start-Process .venv\Scripts\python.exe -ArgumentList main.py -PassThru`; persist PID across steps via `"SERVER_PID=$($proc.Id)" \| Out-File -FilePath $env:GITHUB_ENV -Append` | — |
| Wait for server | Poll `http://localhost:8000/api/health` every 1s, up to 30 retries; fail with clear message on timeout | Server failed to start |
| Assert health | Check response body contains `"status": "ok"` | API returned unexpected response |
| Stop server | `Stop-Process -Id $env:SERVER_PID -Force` | — |

---

## Key Decisions

**Pre-install Python and Node via Actions:**
`setup.bat` assumes Python and Node are already on PATH (it does not call `winget`). The GitHub Actions setup steps fulfil this assumption without modification to the script, keeping the script identical to what a real user runs.

**Venv activation does not persist across steps:**
`setup.bat` calls `.venv\Scripts\activate.bat` internally, but each GitHub Actions step runs in a fresh shell — that activation is lost. All subsequent steps that need venv packages must therefore invoke `.venv\Scripts\python.exe` directly rather than the system `python`. This applies to starting the server in Phase 2.

**`/api/health` as smoke target:**
The endpoint exists in `backend/app.py` and returns `{"status": "ok"}`. It exercises server startup, the lifespan hook, and the FastAPI routing layer without requiring an audio file or GPU.

**`webbrowser.open()` on headless runner:**
`main.py` calls `webbrowser.open()` via a timer thread. On a headless runner this call fails silently — the server continues to start normally. No changes to `main.py` are needed.

**30-retry poll budget:**
Cold `windows-latest` runners can be slow to start uvicorn due to heavy import chains (pydantic-core, fastapi). 15 retries has been observed to be flaky in similar stacks. 30 retries (30s maximum wait) is used instead. On timeout the step explicitly fails with a clear message before reaching the assert step, avoiding confusing "connection refused" errors.

**Single job (not two jobs):**
A second job would spin up a fresh runner, requiring `setup.bat` to run again with no benefit. All steps run sequentially in one job, making Phase 2 trivially addable later.

---

## Out of Scope

- Testing on `windows-2019` (matrix can be added later if needed)
- End-to-end transcription test (requires audio file + Whisper model download)
- Linux / macOS CI (separate concern)
