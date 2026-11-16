from reaction_test import render_reaction_test

"""AstroPulse: personal-baseline dashboard. Decision-support aid, not a diagnosis. Synthetic data."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from analysis import (COLUMNS, DOMAINS, NAMES, LEVELS, BASELINE_DAYS, compute_baseline,
                      compute_zscores, compute_levels, domain_levels, explain, summarize)

tab_dash, tab_pvt, tab_exp = st.tabs(["Dashboard", "Reaction test", "Experiment"])

import os
from experiment import figures

with tab_exp:
    level = st.radio("Alert level", [1, 2], horizontal=True,
                     format_func=lambda l: {1: "Yellow or worse", 2: "Red only"}[l])
    path = f"data/experiment_level{level}.csv"
    if not os.path.exists(path):
        st.warning("Run `python experiment.py` first.")
    else:
        for f in figures(pd.read_csv(path)):
            st.plotly_chart(f, use_container_width=True)
        st.caption("Synthetic data, not clinical validation. Results depend on unsourced simulation assumptions.")

with tab_pvt:
    st.write("Click the box to start. When it turns red, click as fast as you can (20 trials).")
    render_reaction_test()
    st.caption("Copy the 'Lapses' % into the pvt_lapses_pct column of your CSV.")

REQUIRED = ["day"] + COLUMNS
UNITS = {"day": ("Day number, 1, 2, 3... (consecutive, no gaps)", "integer"),
         "sleep_h": ("Hours slept", "decimal"),
         "hr_rest": ("Resting heart rate, bpm", "decimal"),
         "exercise_min": ("Exercise minutes, including resistive", "decimal"),
         "stress": ("Stress, scale 1 to 5", "integer"),
         "pvt_lapses_pct": ("Reaction lapses > 500 ms, % (from the reaction test)", "decimal"),
         "dose_mSv": ("Radiation dose of the day, mSv (simulated)", "decimal"),
         "temp_c": ("Body temperature, °C", "decimal"),
         "hrv_rmssd": ("Heart rate variability RMSSD, ms", "decimal"),
         "grip_kg": ("Grip strength, kg", "decimal")}

# ---- CSV guide ----
with st.expander("CSV format guide (what the astronaut must upload)", expanded=False):
    st.markdown(f"""
- One row per day, **{len(REQUIRED)} columns with exactly these names** (CSV, comma separated, `.` as decimal point).
- At least **{BASELINE_DAYS} days**: the first {BASELINE_DAYS} rows define your personal baseline.
  Ideally 14+ days so the 3-day persistence rule can work.
- Days must be consecutive and sorted (1, 2, 3...). No empty cells.
""")
    st.table(pd.DataFrame([(c, *UNITS[c]) for c in REQUIRED], columns=["Column", "Meaning", "Type"]))
    template = pd.DataFrame([[1, 7.2, 60, 60, 2, 5.0, 0.6, 36.6, 45, 40],
                             [2, 7.0, 61, 55, 2, 5.0, 0.6, 36.7, 44, 40]], columns=REQUIRED)
    st.download_button("Download CSV template", template.to_csv(index=False),
                       file_name="astropulse_template.csv", mime="text/csv")

file = st.file_uploader("Upload your CSV (optional; the demo is used if empty)", type="csv")
df = pd.read_csv(file) if file else pd.read_csv("data/demo.csv")

# ---- Validation ----
missing = [c for c in REQUIRED if c not in df.columns]
if missing:
    st.error(f"Missing columns in the CSV: {missing}. See the format guide above.")
    st.stop()
df[REQUIRED] = df[REQUIRED].apply(pd.to_numeric, errors="coerce")
bad = [c for c in REQUIRED if df[c].isna().any()]
if bad:
    st.error(f"Empty or non-numeric values in: {bad}.")
    st.stop()
if len(df) < BASELINE_DAYS:
    st.error(f"At least {BASELINE_DAYS} days are needed for the baseline (you uploaded {len(df)}).")
    st.stop()
if list(df["day"]) != list(range(1, len(df) + 1)):
    st.warning("Days are not 1..N consecutive; they are treated as consecutive in file order.")

base = compute_baseline(df)
z = compute_zscores(df, base)
lv = compute_levels(z)
dom = domain_levels(lv)
ICON = {0: "🟢", 1: "🟡", 2: "🔴"}

# ---- Overall analysis (whole log) ----
st.subheader(f"Analysis summary (days 1-{len(df)})")
st.info(summarize(z, lv, dom))

# ---- Day view ----
st.subheader("Day view")
day = st.slider("Day", 1, len(df), len(df))
idx = day - 1
cols = st.columns(len(DOMAINS))
for col, name in zip(cols, DOMAINS):
    lvl = int(dom[name].iloc[idx])
    col.metric(name, f"{ICON[lvl]} {LEVELS[lvl].capitalize()}")

st.markdown("**What changed**")
msgs = explain(z, lv, idx)
if not msgs:
    st.success("No sustained deviations from your baseline.")
for m in sorted(msgs, key=lambda m: -m["level"]):
    st.write(f"{ICON[m['level']]} {m['text']}")
if msgs:
    st.caption("The level is based on the last 3 days, not only today's value.")

# ---- Trends ----
st.subheader("Trends")
var = st.selectbox("Variable", COLUMNS, format_func=lambda c: NAMES[c])
mu, sd = base.loc[var, "mu"], base.loc[var, "sigma"]
fig = go.Figure()
fig.add_hrect(y0=mu - 2 * sd, y1=mu + 2 * sd, fillcolor="green", opacity=0.12, line_width=0)
fig.add_hline(y=mu, line_dash="dash")
fig.add_vrect(x0=0.5, x1=BASELINE_DAYS + 0.5, fillcolor="gray", opacity=0.10, line_width=0)  # baseline window
fig.add_trace(go.Scatter(x=df["day"], y=df[var], mode="lines+markers", name=NAMES[var]))
fig.update_layout(xaxis_title="Day", yaxis_title=NAMES[var], height=380)
st.plotly_chart(fig, use_container_width=True)
st.caption("Green band = baseline mean ± 2 SD. Gray zone = baseline window.")