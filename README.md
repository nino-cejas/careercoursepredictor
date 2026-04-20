# CareerLinkAI Predictor

## Project Summary
CareerLinkAI Predictor is a Flask-based web application that predicts a best-fit career and course using:

1. Academic performance (Grades 7 to 10 in Math, English, Science)
2. SHS strand (STEM, ABM, HUMSS, ICT, HE)
3. RIASEC profile (48 items)
4. SCCT factors (Self-Efficacy, Outcome Expectations, Barriers)

The app produces:

1. Top-1 prediction (best career and best course)
2. Top-3 ranked recommendations with confidence
3. Model summary metrics for Top-1 and Top-3 views

## Core Workflow
1. User opens the web UI and completes the multi-step assessment wizard.
2. Frontend sends validated payload to `/api/predict`.
3. Backend computes derived features (best subject, Holland code, SCCT averages).
4. Trained model predicts probabilities for career-course labels.
5. API returns Top-1 result, Top-3 list, and model summary metrics.

## Tech Stack
1. Backend: Flask
2. Data and modeling: pandas, scikit-learn, numpy
3. Production serving: Waitress
4. Frontend: Vanilla HTML/CSS/JavaScript (served from `public/`)

## Model Design
### Input Features
1. Categorical: `best_subject`, `shs_strand`, `holland_code`
2. Numeric: `scct_se`, `scct_oe`, `scct_b`

### Target Label
The classifier predicts a combined target label:

`best_career|||best_course`

### Training Pipeline
1. `OneHotEncoder(handle_unknown="ignore")` for categorical inputs
2. Numeric passthrough for SCCT values
3. `LogisticRegression(solver="saga", max_iter=1200, tol=5e-3)`
4. Train/test split using `test_size=0.2` and `random_state=42`

### Reported Metrics
1. Top-1 metrics: weighted Accuracy, Recall, F1-Score, Precision from exact Top-1 predictions
2. Top-3 metrics: hit-rate-based summary where a sample is counted correct if true label is in Top-3

Note: Top-3 metrics are intentionally computed from ranked hit logic and are typically higher than Top-1.

## Dataset
### File
`career_suggestion.csv`

### Columns
1. `suggestion_id`
2. `best_subject`
3. `shs_strand`
4. `holland_code`
5. `scct_se`
6. `scct_oe`
7. `scct_b`
8. `best_career`
9. `best_course`

### Generation Script
`auto_add_data.py`

The generator uses a weighted scoring rule:

1. Best subject: 10%
2. SHS strand: 10%
3. Holland code: 50%
4. SCCT-SE: 10%
5. SCCT-OE: 10%
6. SCCT-B: 10%

Run dataset generation manually:

```powershell
python auto_add_data.py --output career_suggestion.csv
```

## API Endpoints
### `GET /`
Serves `public/index.html`.

### `GET /api/questions`
Returns:

1. Randomized RIASEC questions (48 items)
2. SCCT question groups (`scct_se`, `scct_oe`, `scct_b`)

### `POST /api/predict`
Consumes payload:

1. `grades` object with 4 values each for Math/English/Science
2. `shs_strand`
3. `riasec_answers` with 48 answers (1 to 5)
4. `scct_answers` with 4 answers per SCCT category (1 to 5)

Returns:

1. Derived features (`best_subject`, `holland_code`, SCCT averages)
2. `best_career`, `best_course`, `prediction_confidence`
3. `top_predictions` (Top-3 ranked recommendations)
4. `model_summary` with nested `top1` and `top3` metrics

## Frontend Highlights
1. Wizard UI for structured data collection
2. Result view toggle:
	- Top-1 only
	- Top-3 view
3. Model summary explanation buttons for each view
4. Top-3 recommendations list with confidence values

## Local Development Setup
### 1) Create and activate virtual environment
```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& ".\.venv\Scripts\Activate.ps1"
```

### 2) Install dependencies
```powershell
pip install -r requirements.txt
```

### 3) Run development server
```powershell
python app.py
```

Default Flask app endpoint: `http://127.0.0.1:5000`

## Production-Style Run
Run with Waitress:

```powershell
waitress-serve --listen=0.0.0.0:8000 app:app
```

or, if PATH does not resolve scripts:

```powershell
& "d:/THESIS FILES/predictor/.venv/Scripts/waitress-serve.exe" --listen=0.0.0.0:8000 app:app
```

## Quick Health Checks
```powershell
(Invoke-WebRequest -Uri "http://127.0.0.1:8000/" -Method Get).StatusCode
(Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/questions" -Method Get).StatusCode
```

Expected result: both return `200`.

## Repository Layout
1. `app.py`: Backend API, feature computation, model training, prediction logic
2. `auto_add_data.py`: Dataset generation from weighted counselor-style rules
3. `career_suggestion.csv`: Training dataset
4. `requirements.txt`: Python dependencies
5. `public/index.html`: UI markup
6. `public/app.js`: Frontend logic and API integration
7. `public/style.css`: Styling and view-mode behavior

## Notes
1. The model trains on startup; ensure dataset is present before launching.
2. This is a decision-support tool and should not be used as the sole basis for life-critical decisions.

