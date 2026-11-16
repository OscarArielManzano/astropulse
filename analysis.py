# Contrato del CSV (Foundation Document, sección 7, actualizado)
COLUMNS = ["sleep_h", "hr_rest", "exercise_min", "stress",
           "pvt_lapses_pct", "dose_mSv", "temp_c", "hrv_rmssd", "grip_kg"]

DOMAINS = {
    "Conductual y cognitivo": ["sleep_h", "stress", "pvt_lapses_pct"],
    "Cardiovascular": ["hr_rest", "hrv_rmssd"],
    "Hueso y músculo": ["exercise_min", "grip_kg"],
    "Inmunidad y radiación": ["dose_mSv", "temp_c"],
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
LEVELS = {0: "verde", 1: "amarillo", 2: "rojo"}


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

NAMES = {"sleep_h": "Horas de sueño", "hr_rest": "Pulso en reposo", "exercise_min": "Minutos de ejercicio",
         "stress": "Estrés", "pvt_lapses_pct": "Lapsos de reacción", "dose_mSv": "Dosis de radiación",
         "temp_c": "Temperatura corporal", "hrv_rmssd": "Variabilidad cardiaca (HRV)", "grip_kg": "Fuerza de agarre"}
ACTIONS = {1: "Vigilar: repite la medición mañana y revisa cómo te sientes.",
           2: "Revisar: considera informar al oficial médico o a control de misión."}


def explain(z, levels, idx):
    """Mensajes del día idx (0 = día 1): qué variable se desvió, cuánto y por cuántos días seguidos."""
    msgs = []
    for dom, cols in DOMAINS.items():
        for c in cols:
            lvl = int(levels[c].iloc[idx])
            if lvl == 0:
                continue
            sign = np.sign(z[c].iloc[idx])
            n = 0  # días consecutivos con |z|>=1 y el mismo signo
            while idx - n >= 0 and np.sign(z[c].iloc[idx - n]) == sign and abs(z[c].iloc[idx - n]) >= 1:
                n += 1
            word = "por encima" if sign > 0 else "por debajo"
            text = (f"{NAMES[c]}: {abs(z[c].iloc[idx]):.1f} desviaciones {word} de tu línea base, "
                    f"{n} día(s) seguidos. {ACTIONS[lvl]}")
            msgs.append({"dominio": dom, "variable": c, "nivel": lvl, "texto": text})
    return msgs