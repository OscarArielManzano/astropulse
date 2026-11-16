"""AstroPulse: personal-baseline dashboard. Decision-support aid, not a diagnosis. Synthetic data."""
import os
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from analysis import (COLUMNS, DOMAINS, NAMES, LEVELS, BASELINE_DAYS, DOSE_LIMIT_MSV, compute_baseline,
                      compute_zscores, compute_levels, domain_levels, explain, summarize, dose_summary,
                      build_report)
from experiment import figures
from reaction_test import render_reaction_test
from style import COLORS, PLOTLY_COLORWAY, apply_style

st.set_page_config(page_title="AstroPulse", layout="wide")
apply_style()
st.title("AstroPulse")
st.caption("Decision-support aid, not a diagnosis. Simulated data.")

tab_dash, tab_pvt, tab_exp = st.tabs(["Dashboard", "Reaction test", "Experiment"])

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
ICON = {0: ":green[●]", 1: ":yellow[●]", 2: ":red[●]"}

# ---------------- Reaction test tab ----------------
with tab_pvt:
    st.write("Click the box to start. When it turns red, click as fast as you can (20 trials).")
    render_reaction_test()
    st.caption("Copy the 'Lapses' % into the pvt_lapses_pct field of your daily entry.")

# ---------------- Experiment tab ----------------
with tab_exp:
    level = st.radio("Alert level", [1, 2], horizontal=True,
                     format_func=lambda l: {1: "Yellow or worse", 2: "Red only"}[l])
    path = f"data/experiment_level{level}.csv"
    if not os.path.exists(path):
        st.warning("Run `python experiment.py` first.")
    else:
        for f in figures(pd.read_csv(path)):
            f.update_layout(colorway=PLOTLY_COLORWAY,
                            font=dict(family="Courier New, Courier, monospace", color=COLORS["text"]),
                            paper_bgcolor=COLORS["surface"], plot_bgcolor=COLORS["surface"])
            st.plotly_chart(f, use_container_width=True)
        st.caption("Synthetic data, not clinical validation. Results depend on unsourced simulation assumptions.")

# ---------------- Dashboard tab ----------------
with tab_dash:
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
    base_df = pd.read_csv(file) if file else pd.read_csv("data/demo.csv")

    # ---- Daily entry form ----
    if "added" not in st.session_state:
        st.session_state["added"] = []
    added = st.session_state["added"]
    next_day = len(base_df) + len(added) + 1

    with st.expander(f"Add today's entry (day {next_day})"):
        with st.form("daily_entry"):
            c = st.columns(3)
            v = {
                "sleep_h": c[0].number_input("Sleep hours", 0.0, 24.0, 7.0, 0.1),
                "hr_rest": c[1].number_input("Resting heart rate (bpm)", 30.0, 200.0, 60.0, 1.0),
                "exercise_min": c[2].number_input("Exercise minutes", 0.0, 480.0, 60.0, 5.0),
                "stress": c[0].number_input("Stress (1-5)", 1, 5, 2),
                "pvt_lapses_pct": c[1].number_input("Reaction lapses % (from the test)", 0.0, 100.0, 5.0, 5.0),
                "dose_mSv": c[2].number_input("Radiation dose (mSv, simulated)", 0.0, 20.0, 0.6, 0.01),
                "temp_c": c[0].number_input("Body temperature (°C)", 34.0, 42.0, 36.6, 0.1),
                "hrv_rmssd": c[1].number_input("HRV RMSSD (ms)", 1.0, 200.0, 45.0, 1.0),
                "grip_kg": c[2].number_input("Grip strength (kg)", 5.0, 100.0, 40.0, 0.5),
            }
            if st.form_submit_button("Add entry"):
                added.append({"day": next_day, **v})
                st.rerun()
        if added:
            b1, b2 = st.columns(2)
            if b1.button("Remove last entry"):
                added.pop()
                st.rerun()
            if b2.button("Clear all added entries"):
                added.clear()
                st.rerun()

    df = pd.concat([base_df, pd.DataFrame(added)], ignore_index=True) if added else base_df
    st.download_button("Download full log (CSV)", df.to_csv(index=False),
                       file_name="astropulse_log.csv", mime="text/csv")

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

    # ---- Overall analysis (whole log) ----
    st.subheader(f"Analysis summary (days 1-{len(df)})")
    st.info(summarize(z, lv, dom))

    # ---- Cumulative radiation dose ----
    st.subheader("Cumulative radiation dose")
    with st.expander("Dose settings"):
        limit = st.number_input("Limit (mSv)", 1.0, 5000.0, DOSE_LIMIT_MSV, 10.0)
        prior = st.number_input("Dose from earlier flights (mSv)", 0.0, 5000.0, 0.0, 1.0)
    ds = dose_summary(df, limit, prior)
    d1, d2, d3 = st.columns(3)
    d1.metric("Cumulative dose", f"{ds['total']:.1f} mSv")
    d2.metric("% of limit", f"{ds['pct']:.1f} %")
    d3.metric("Estimated days left", "n/a" if ds["days_left"] is None else f"{max(ds['days_left'], 0):.0f}")
    st.progress(min(ds["pct"] / 100, 1.0))
    st.caption("Default limit: NASA career limit (NASA-STD-3001). Simulated dose values. "
               "Days left = linear estimate at the average daily dose; not a prediction.")

    # ---- Export report ----
    st.download_button("Download summary report (.md)", build_report(df, z, lv, dom, ds),
                       file_name="astropulse_report.md", mime="text/markdown")

    # ---- Day view ----
    st.subheader("Day view")
    day = st.slider("Day", 1, len(df), len(df))
    idx = day - 1
    with st.container(key="domain_statuses"):
        cols = st.columns(len(DOMAINS))
        for col, name in zip(cols, DOMAINS):
            lvl = int(dom[name].iloc[idx])
            with col.container(key=f"domain_level_{lvl}_{name}"):
                st.metric(name, LEVELS[lvl].capitalize())

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
    fig.add_hrect(y0=mu - 2 * sd, y1=mu + 2 * sd, fillcolor=COLORS["green"], opacity=0.12, line_width=0)
    fig.add_hline(y=mu, line_dash="dash")
    fig.add_vrect(x0=0.5, x1=BASELINE_DAYS + 0.5, fillcolor=COLORS["baseline"], opacity=0.10, line_width=0)
    fig.add_trace(go.Scatter(x=df["day"], y=df[var], mode="lines+markers", name=NAMES[var]))
    fig.update_layout(xaxis_title="Day", yaxis_title=NAMES[var], height=380)
    fig.update_layout(colorway=PLOTLY_COLORWAY,
                      font=dict(family="Courier New, Courier, monospace", color=COLORS["text"]),
                      paper_bgcolor=COLORS["surface"], plot_bgcolor=COLORS["surface"])
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Green band = baseline mean ± 2 SD. Gray zone = baseline window.")
