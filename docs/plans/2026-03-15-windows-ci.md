# Windows CI Workflow Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a GitHub Actions workflow that verifies `setup.bat` succeeds and the server responds to `/api/health` on a real Windows runner.

**Architecture:** Single workflow file, single job on `windows-latest`, two phases delivered as one commit each. Phase 1 verifies the install + build. Phase 2 adds server start, health poll, assert, and teardown.

**Tech Stack:** GitHub Actions, `actions/checkout@v4`, `actions/setup-python@v5`, `actions/setup-node@v4`, PowerShell, cmd

---

### Task 1: Phase 1 — Setup verify workflow

**Files:**
- Create: `.github/workflows/windows.yml`

**Step 1: Create the workflow directory**

```bash
mkdir -p .github/workflows
```

**Step 2: Write the workflow file**

Create `.github/workflows/windows.yml` with this exact content:

```yaml
name: Windows setup

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  windows-setup:
    runs-on: windows-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Set up Node.js LTS
        uses: actions/setup-node@v4
        with:
          node-version: 'lts/*'

      - name: Run setup.bat
        shell: cmd
        run: setup.bat
```

**Step 3: Verify the file is well-formed YAML**

```bash
python -c "import yaml; yaml.safe_load(open('.github/workflows/windows.yml')); print('OK')"
```

Expected output: `OK`

**Step 4: Commit**

```bash
git add .github/workflows/windows.yml
git commit -m "ci(windows): add setup verify workflow"
```

**Step 5: Push and confirm the workflow appears in GitHub Actions**

```bash
git push
```

Open the repository on GitHub → Actions tab → confirm a `Windows setup` workflow run is triggered and the `windows-setup` job appears. Wait for it to go green before proceeding to Task 2.

---

### Task 2: Phase 2 — Add smoke test steps

**Files:**
- Modify: `.github/workflows/windows.yml`

**Context:** The venv created by `setup.bat` is not activated across steps. Use `.venv\Scripts\python.exe` directly instead of `python`. Pass the server PID across steps via `$env:GITHUB_ENV`.

**Step 1: Append the four smoke-test steps to the workflow**

Replace the contents of `.github/workflows/windows.yml` with:

```yaml
name: Windows setup

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  windows-setup:
    runs-on: windows-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Set up Node.js LTS
        uses: actions/setup-node@v4
        with:
          node-version: 'lts/*'

      - name: Run setup.bat
        shell: cmd
        run: setup.bat

      - name: Start server
        shell: pwsh
        run: |
          $proc = Start-Process .venv\Scripts\python.exe -ArgumentList main.py -PassThru
          "SERVER_PID=$($proc.Id)" | Out-File -FilePath $env:GITHUB_ENV -Append

      - name: Wait for server
        shell: pwsh
        run: |
          $url = "http://localhost:8000/api/health"
          $retries = 30
          for ($i = 1; $i -le $retries; $i++) {
            try {
              $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2
              Write-Host "Server responded after $i second(s)"
              exit 0
            } catch {
              Write-Host "Attempt $i/$retries — not ready yet"
              Start-Sleep -Seconds 1
            }
          }
          Write-Error "Server did not respond after $retries seconds"
          exit 1

      - name: Assert health endpoint
        shell: pwsh
        run: |
          $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing
          $body = $response.Content
          Write-Host "Response: $body"
          if ($body -notmatch '"status":\s*"ok"') {
            Write-Error "Health check failed: unexpected response body: $body"
            exit 1
          }
          Write-Host "Health check passed"

      - name: Stop server
        if: always()
        shell: pwsh
        run: |
          if ($env:SERVER_PID) {
            Stop-Process -Id $env:SERVER_PID -Force -ErrorAction SilentlyContinue
            Write-Host "Stopped server process $env:SERVER_PID"
          }
```

Key details:
- `Stop server` uses `if: always()` so it runs even if the assert step fails — prevents orphan processes
- `Stop-Process` uses `-ErrorAction SilentlyContinue` in case the process already exited naturally

**Step 2: Verify the file is well-formed YAML**

```bash
python -c "import yaml; yaml.safe_load(open('.github/workflows/windows.yml')); print('OK')"
```

Expected output: `OK`

**Step 3: Commit**

```bash
git add .github/workflows/windows.yml
git commit -m "ci(windows): add server smoke test to Windows workflow"
```

**Step 4: Push and confirm smoke test passes**

```bash
git push
```

Open the repository on GitHub → Actions tab → confirm the new run shows all steps green including `Wait for server`, `Assert health endpoint`, and `Stop server`.
