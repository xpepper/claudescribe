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
| Start server | PowerShell `Start-Process python -ArgumentList main.py` | — |
| Wait for server | Poll `http://localhost:8000/api/health` every 1s, up to 15 retries | Server failed to start |
| Assert health | Check response body contains `"status": "ok"` | API returned unexpected response |
| Stop server | Kill the python process | — |

---

## Key Decisions

**Pre-install Python and Node via Actions:**
`setup.bat` assumes Python and Node are already on PATH (it does not call `winget`). The GitHub Actions setup steps fulfil this assumption without modification to the script, keeping the script identical to what a real user runs.

**`/api/health` as smoke target:**
The endpoint exists in `backend/app.py` and returns `{"status": "ok"}`. It exercises server startup, the lifespan hook, and the FastAPI routing layer without requiring an audio file or GPU.

**`webbrowser.open()` on headless runner:**
`main.py` calls `webbrowser.open()` via a timer thread. On a headless runner this call fails silently — the server continues to start normally. No changes to `main.py` are needed.

**Single job (not two jobs):**
A second job would spin up a fresh runner, requiring `setup.bat` to run again with no benefit. All steps run sequentially in one job, making Phase 2 trivially addable later.

---

## Out of Scope

- Testing on `windows-2019` (matrix can be added later if needed)
- End-to-end transcription test (requires audio file + Whisper model download)
- Linux / macOS CI (separate concern)
