# Contrato del CSV (Foundation Document, sección 7, actualizado)
COLUMNS = ["sleep_h", "hr_rest", "exercise_min", "stress",
           "pvt_lapses_pct", "dose_mSv", "temp_c", "hrv_rmssd", "grip_kg"]

DOMAINS = {
    "Behavioral & cognitive": ["sleep_h", "stress", "pvt_lapses_pct"],
    "Cardiovascular": ["hr_rest", "hrv_rmssd"],
    "Bone & muscle": ["exercise_min", "grip_kg"],
    "Immunity & radiation": ["dose_mSv", "temp_c"],
}



"""Línea base y z-scores. Ayuda a la decisión, no diagnóstico. Datos sintéticos."""
import numpy as np
import pandas as pd

BASELINE_DAYS = 10    # Foundation Document, sección 8
SIGMA_FLOOR_PCT = 0.01  # PROVISIONAL, SIN FUENTE: piso de σ = 1 % de |μ|. Gabo debe validarlo.


def compute_baseline(df, n_days=BASELINE_DAYS):
    """Media (mu) y desviación estándar (sigma) de cada variable en los primeros n_days."""
    window = df[COLUMNS].iloc[:n_days]
    mu = window.mean()
    sigma = window.std(ddof=1)  # muestral (n-1)
    floor = (mu.abs() * SIGMA_FLOOR_PCT).clip(lower=1e-6)  # evita dividir entre ~0
    sigma = np.maximum(sigma, floor)
    return pd.DataFrame({"mu": mu, "sigma": sigma})


def compute_zscores(df, baseline):
    """z = (valor de hoy - mu) / sigma, para cada día y variable."""
    z = (df[COLUMNS] - baseline["mu"]) / baseline["sigma"]
    z.insert(0, "day", df["day"].values)
    return z

PERSIST_DAYS = 3  # Foundation Document, sección 8
LEVELS = {0: "green", 1: "yellow", 2: "red"}


def level_from_z(z):
    """|z|<1 verde (0), 1<=|z|<2 amarillo (1), |z|>=2 rojo (2). Acepta Series o DataFrame."""
    a = z.abs()
    return (a >= 1).astype(int) + (a >= 2).astype(int)


def compute_levels(z, n=PERSIST_DAYS):
    """Nivel con persistencia: n días seguidos en la MISMA dirección (mismo signo de z)."""
    zc = z[COLUMNS]
    signed = level_from_z(zc) * np.sign(zc)           # nivel con signo: +alto, -bajo
    pos = signed.clip(lower=0).rolling(n, min_periods=n).min()
    neg = (-signed).clip(lower=0).rolling(n, min_periods=n).min()
    return np.maximum(pos, neg).fillna(0).astype(int)


def domain_levels(levels):
    """Cada dominio toma el peor nivel de sus variables, por día."""
    out = pd.DataFrame({"day": z_days(levels)})
    for name, cols in DOMAINS.items():
        out[name] = levels[cols].max(axis=1).values
    return out


def z_days(levels):
    return levels.index + 1  # solo para alinear con la columna day (1..N)

NAMES = {"sleep_h": "Sleep hours", "hr_rest": "Resting heart rate", "exercise_min": "Exercise minutes",
         "stress": "Stress", "pvt_lapses_pct": "Reaction lapses", "dose_mSv": "Radiation dose",
         "temp_c": "Body temperature", "hrv_rmssd": "Heart rate variability (HRV)", "grip_kg": "Grip strength"}
ACTIONS = {1: "Watch: repeat the measurement tomorrow and note how you feel.",
           2: "Review: consider informing the crew medical officer or mission control."}


def explain(z, levels, idx):
    """Messages for day idx (0 = day 1): which variable deviated, by how much, and for how many days."""
    msgs = []
    for dom, cols in DOMAINS.items():
        for c in cols:
            lvl = int(levels[c].iloc[idx])
            if lvl == 0:
                continue
            sign = np.sign(z[c].iloc[idx])
            n = 0  # consecutive days with |z|>=1 and the same sign
            while idx - n >= 0 and np.sign(z[c].iloc[idx - n]) == sign and abs(z[c].iloc[idx - n]) >= 1:
                n += 1
            word = "above" if sign > 0 else "below"
            text = (f"{NAMES[c]}: {abs(z[c].iloc[idx]):.1f} SD {word} your baseline, "
                    f"{n} consecutive day(s). {ACTIONS[lvl]}")
            msgs.append({"domain": dom, "variable": c, "level": lvl, "text": text})
    return msgs


def summarize(z, levels, dom):
    """Overall text summary of the whole log (up to the last documented day). Rule-based, no ML."""
    n = len(dom)
    day = dom["day"]
    lines = [f"**Days documented:** {n} (baseline = days 1-{BASELINE_DAYS})."]
    ever = False
    for name in DOMAINS:
        s = dom[name]
        alert = s >= 1
        if not alert.any():
            lines.append(f"- **{name}:** no sustained deviations.")
            continue
        ever = True
        d1, d2 = int(day[alert].iloc[0]), int(day[alert].iloc[-1])
        peak = LEVELS[int(s.max())]
        now = LEVELS[int(s.iloc[-1])]
        lines.append(f"- **{name}:** alerts between day {d1} and day {d2}, "
                     f"peak level {peak} ({int((s == 2).sum())} red day(s)); status on day {n}: {now}.")
    # Variables with the largest sustained deviation
    rows = []
    for c in COLUMNS:
        if (levels[c] > 0).any():
            i = z[c].abs().idxmax()
            rows.append((abs(z[c][i]), c, int(day[i]), "above" if z[c][i] > 0 else "below"))
    if rows:
        lines.append("")
        lines.append("**Largest deviations (peak |z|):**")
        for peak_z, c, d, w in sorted(rows, reverse=True)[:4]:
            lines.append(f"- {NAMES[c]}: {peak_z:.1f} SD {w} baseline on day {d}.")
    lines.append("")
    active = [name for name in DOMAINS if int(dom[name].iloc[-1]) > 0]
    if not ever:
        lines.append("**Conclusion:** no sustained deviations from your personal baseline in this log.")
    elif active:
        lines.append(f"**Conclusion:** deviations are still active on day {n} in: {', '.join(active)}. "
                     "Consider a review with the crew medical officer.")
    else:
        lines.append(f"**Conclusion:** deviations were detected but all domains are green on day {n}. "
                     "Keep monitoring.")
    lines.append("_Decision-support aid, not a diagnosis. Synthetic data._")
    return "\n".join(lines)