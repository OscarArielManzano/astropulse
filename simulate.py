"""Generador de astronautas sintéticos. Datos simulados: no es validación clínica."""
import argparse
import numpy as np
import pandas as pd

# variable: (media poblacional, DE intra-persona, mín, máx, dirección del deterioro, desviación en DE durante anomalía)
VARS = {
    "sleep_h":        (7.0, 0.5, 0, 12, -1, 3.0),
    "hr_rest":        (62.0, 3.0, 30, 150, +1, 2.5),
    "exercise_min":   (60.0, 10.0, 0, 240, -1, 1.5),
    "stress":         (2.0, 0.4, 1, 5, +1, 2.5),
    "pvt_lapses_pct": (5.0, 2.0, 0, 100, +1, 3.0),
    "dose_mSv":       (0.6, 0.05, 0, 10, +1, 0.0),   # sin anomalía; el acumulado se calcula aparte
    "temp_c":         (36.6, 0.2, 34, 41, +1, 0.0),
    "hrv_rmssd":      (45.0, 6.0, 5, 150, -1, 2.5),
    "grip_kg":        (40.0, 2.0, 5, 80, -1, 1.5),
}
BETWEEN = 2.0  # la normalidad entre personas varía BETWEEN veces la DE intra-persona


def generate_astronaut(rng, days=30, anomaly_start=15, anomaly_len=7, with_truth=False):
    """Un astronauta: normalidad propia + ruido + una semana de deterioro con rampa de 3 días."""
    df = pd.DataFrame({"day": np.arange(1, days + 1)})
    ramp = np.zeros(days)
    for i in range(days):
        d = i + 1 - anomaly_start  # días desde el inicio de la anomalía
        if 0 <= d < anomaly_len:
            ramp[i] = min(1.0, (d + 1) / 3)
    for col, (mu, sd, lo, hi, sign, shift) in VARS.items():
        personal_mu = mu + rng.normal(0, BETWEEN * sd)
        values = personal_mu + rng.normal(0, sd, days) + sign * shift * sd * ramp
        df[col] = np.clip(values, lo, hi).round(2)
    if with_truth:
        df["anomaly_day"] = (ramp > 0).astype(int)  # solo para experiment.py, no es parte del contrato
    return df


def generate_cohort(n=100, days=30, seed=0):
    """n astronautas con inicio y duración de anomalía distintos (para experiment.py)."""
    rng = np.random.default_rng(seed)
    parts = []
    for i in range(n):
        start = int(rng.integers(12, days - 8))
        length = int(rng.integers(5, 9))
        a = generate_astronaut(rng, days, start, length, with_truth=True)
        a.insert(0, "astronaut_id", i + 1)
        parts.append(a)
    return pd.concat(parts, ignore_index=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--demo", action="store_true", help="escribe data/demo.csv (1 astronauta, 30 días)")
    p.add_argument("--cohort", type=int, default=0, help="N astronautas -> data/cohort.csv")
    p.add_argument("--seed", type=int, default=42)
    a = p.parse_args()
    if a.demo:
        generate_astronaut(np.random.default_rng(a.seed)).to_csv("data/demo.csv", index=False)
        print("data/demo.csv listo")
    if a.cohort:
        generate_cohort(a.cohort, seed=a.seed).to_csv("data/cohort.csv", index=False)
        print("data/cohort.csv listo")