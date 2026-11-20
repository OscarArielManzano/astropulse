# AstroPulse

Offline personal-baseline health dashboard for long-duration space missions (NASA Space Apps Challenge 2026).
It compares each day of an astronaut's log against **their own** baseline (z-scores), groups the deviations into four risk domains and shows an explainable green/yellow/red status.

> Decision-support aid, not a medical device or a diagnosis. All data are synthetic; there is no clinical validation.

## Requirements
- Python 3.11 or newer
- Git (only to clone the repo)

## Run (Windows PowerShell)
```powershell
git clone https://github.com/TU_USUARIO/astropulse.git
cd astropulse
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```
The app opens at http://localhost:8501. Press Ctrl+C in the terminal to stop it.
If PowerShell blocks the activation, run once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

## Run (macOS / Linux)
```bash
git clone https://github.com/TU_USUARIO/astropulse.git
cd astropulse
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Optional scripts
```powershell
python simulate.py --demo        # regenerates data/demo.csv (1 astronaut, 30 days)
python simulate.py --cohort 100  # generates data/cohort.csv (100 simulated astronauts)
python experiment.py             # fixed threshold vs personal baseline (needed for the Experiment tab)
python export_db.py              # packs the synthetic data into data/astropulse.db (SQLite)
```
Run them in this order: `experiment.py` and `export_db.py` need `cohort.csv`.

## What is inside
- `app.py`: Streamlit interface (Dashboard, Reaction test, Experiment).
- `analysis.py`: baseline, z-scores, 3-day persistence, domain status, explanations, dose summary, report.
- `simulate.py`, `experiment.py`: synthetic data and the comparison experiment.
- `reaction_test.py`: reaction-time test (blue screen, click when it turns red).
- `style.py`, `.streamlit/config.toml`: visual design.
- `data/`: demo log, experiment results and the SQLite file.

## CSV format
One row per day, columns with exactly these names: `day, sleep_h, hr_rest, exercise_min, stress, pvt_lapses_pct, dose_mSv, temp_c, hrv_rmssd, grip_kg`.
The first 10 days define the baseline. A template can be downloaded inside the app.

## Future work
- Local database (for example SQLite, no server) for the astronaut's longitudinal log.
- Evaluation with public NASA data, such as the NASA Open Science Data Repository (https://osdr.nasa.gov/bio).
- Real wearable data, rolling baseline window, validated circadian-fatigue module.

## Team
Oscar (programming), Krissia (design and communication), Gabo (statistics and costs).