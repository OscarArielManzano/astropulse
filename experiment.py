"""Experiment: fixed population threshold vs personal baseline. Synthetic data, not clinical validation."""
import numpy as np
import pandas as pd

import plotly.graph_objects as go

LABELS = {"fixed": "Fixed population threshold", "personal": "Personal baseline"}


def figures(res):
    """Three plotly figures from an experiment_level*.csv. Synthetic data."""
    s = summarize_results(res)
    x = [LABELS[m] for m in s.index]
    f1 = go.Figure(go.Bar(x=x, y=s["false_pos_days_per_astronaut"]))
    f1.update_layout(title="False-alarm days per astronaut (before the deterioration)", yaxis_title="Days")
    f2 = go.Figure([go.Bar(name="Detected (new)", x=x, y=s["detected_pct"]),
                    go.Bar(name="Already in false alert", x=x, y=s["already_alert_pct"])])
    f2.update_layout(title="Detection and false alert at onset (%)", barmode="group", yaxis_title="% of astronauts")
    f3 = go.Figure()
    for m in ("fixed", "personal"):
        f3.add_trace(go.Box(y=res[res["method"] == m]["delay"].dropna(), name=LABELS[m]))
    f3.update_layout(title="Detection delay (days, detected cases only)", yaxis_title="Days")
    return [f1, f2, f3]

from analysis import (COLUMNS, BASELINE_DAYS, PERSIST_DAYS,
                      compute_baseline, compute_zscores, compute_levels)
from simulate import generate_cohort


def population_baseline(cohort):
    """Fixed 'population norm': pooled mean/SD of the baseline days of ALL astronauts."""
    w = cohort[cohort["day"] <= BASELINE_DAYS][COLUMNS]
    return pd.DataFrame({"mu": w.mean(), "sigma": w.std(ddof=1)})


def alert_series(a, baseline, level):
    """True on days where any variable reaches `level` (1 = yellow, 2 = red) after persistence."""
    z = compute_zscores(a, baseline)
    return (compute_levels(z).max(axis=1) >= level).to_numpy()


def evaluate(cohort, level):
    pop = population_baseline(cohort)
    rows = []
    for aid, a in cohort.groupby("astronaut_id"):
        a = a.reset_index(drop=True)
        truth = a["anomaly_day"].to_numpy() == 1
        start = int(np.argmax(truth))                      # first anomaly day (0-based)
        end = len(truth) - 1 - int(np.argmax(truth[::-1]))  # last anomaly day
        for method, base in (("fixed", pop), ("personal", compute_baseline(a))):
            alert = alert_series(a, base, level)
            already = bool(alert[start - 1])   # ya estaba en alerta antes del deterioro
            window = alert[start:end + 1 + PERSIST_DAYS]  # permite el retraso de persistencia
            delay = int(np.argmax(window)) if (window.any() and not already) else np.nan
            rows.append({"astronaut_id": aid, "method": method, "delay": delay,
                         "already_alert": int(already),
                         "false_pos": int(alert[:start].sum())})
    return pd.DataFrame(rows)


def summarize_results(res):
    return res.groupby("method").agg(
        detected_pct=("delay", lambda s: 100 * s.notna().mean()),
        mean_delay_days=("delay", "mean"),
        already_alert_pct=("already_alert", lambda s: 100 * s.mean()),
        false_pos_days_per_astronaut=("false_pos", "mean")).round(2)


if __name__ == "__main__":
    cohort = generate_cohort(100, seed=42)
    for level, name in ((1, "yellow or worse"), (2, "red only")):
        res = evaluate(cohort, level)
        print(f"\n=== Alert = {name} ===")
        print(summarize_results(res))
        res.to_csv(f"data/experiment_level{level}.csv", index=False)
    print("\nSynthetic data: not clinical validation.")