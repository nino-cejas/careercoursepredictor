# NEW DEVICE RECOVERY GUIDE (AI EXECUTION PLAYBOOK)

Use this guide when a new device clones this project and encounters missing dependencies, wrong Python interpreter, or broken virtual environment setup.

## Goal
Bring the project to a clean, runnable state and verify API endpoints.

## Scope
This guide assumes:

1. Windows + PowerShell
2. Repository already cloned
3. You need to recover from environment/dependency failures

## Step-by-Step Instructions

### Step 1: Open terminal in repository root
```powershell
cd "D:\THESIS FILES\predictor"
```

Confirm location:

```powershell
Get-Location
```

### Step 2: Confirm Python is available
```powershell
python --version
```

If this fails, install Python 3.11+ and restart terminal.

### Step 3: Remove broken virtual environment (if needed)
Only do this when imports keep failing even after install:

```powershell
if (Test-Path .venv) { Remove-Item -Recurse -Force .venv }
```

### Step 4: Create a fresh virtual environment
```powershell
python -m venv .venv
```

### Step 5: Activate the virtual environment
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& ".\.venv\Scripts\Activate.ps1"
```

Validate active interpreter path:

```powershell
python -c "import sys; print(sys.executable)"
```

Expected output should point to `.venv\Scripts\python.exe`.

### Step 6: Upgrade installer tools
```powershell
python -m pip install --upgrade pip setuptools wheel
```

### Step 7: Install project dependencies
```powershell
pip install -r requirements.txt
```

Dependencies expected:

1. flask
2. pandas
3. scikit-learn
4. numpy
5. waitress

### Step 8: Verify imports quickly
```powershell
python -c "import flask, pandas, sklearn, numpy, waitress; print('imports ok')"
```

### Step 9: Ensure dataset exists
```powershell
Test-Path .\career_suggestion.csv
```

If `False`, regenerate:

```powershell
python auto_add_data.py --output career_suggestion.csv
```

### Step 10: Run app in development mode
```powershell
python app.py
```

Expected:

1. Model summary prints in terminal
2. Flask server listens on port 5000

Stop with `Ctrl + C`.

### Step 11: Run app in deployment mode (Waitress)
```powershell
waitress-serve --listen=0.0.0.0:8000 app:app
```

If command not found:

```powershell
& ".\.venv\Scripts\waitress-serve.exe" --listen=0.0.0.0:8000 app:app
```

### Step 12: Smoke-test API in a second terminal
```powershell
(Invoke-WebRequest -Uri "http://127.0.0.1:8000/" -Method Get).StatusCode
(Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/questions" -Method Get).StatusCode
```

Expected: both return `200`.

## Common Failure Recovery Map

### Problem: `ModuleNotFoundError`
Fix:

1. Ensure venv is activated
2. Run `pip install -r requirements.txt` again
3. Re-run import check from Step 8

### Problem: Wrong interpreter in editor or terminal
Fix:

1. Activate `.venv`
2. Confirm `python -c "import sys; print(sys.executable)"`
3. In VS Code, select interpreter from `.venv\Scripts\python.exe`

### Problem: `waitress-serve` not recognized
Fix:

1. Ensure venv active
2. Use explicit path command:
	`& ".\.venv\Scripts\waitress-serve.exe" --listen=0.0.0.0:8000 app:app`

### Problem: Port already in use (5000 or 8000)
Find owner:

```powershell
Get-NetTCPConnection -State Listen | Where-Object { $_.LocalPort -in 5000,8000 } | Select-Object LocalAddress,LocalPort,OwningProcess
```

Then close the conflicting process or choose another port.

### Problem: PowerShell blocks script activation
Fix for current session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

### Problem: Dataset missing required columns
Fix:

1. Regenerate file with `auto_add_data.py`
2. Confirm file name is exactly `career_suggestion.csv`

## AI Checklist Before Declaring Success
1. venv created and activated
2. dependencies installed without errors
3. imports verified
4. dataset file exists and valid
5. app starts without traceback
6. health checks return `200`
7. `/api/predict` responds with JSON (including `model_summary` and `top_predictions`)

## Optional Full Reset (One-shot)
Run this if environment is severely broken:

```powershell
cd "D:\THESIS FILES\predictor"
if (Test-Path .venv) { Remove-Item -Recurse -Force .venv }
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& ".\.venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
if (-not (Test-Path .\career_suggestion.csv)) { python auto_add_data.py --output career_suggestion.csv }
waitress-serve --listen=0.0.0.0:8000 app:app
```

