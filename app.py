

"""AstroPulse: tablero de línea base personal. Ayuda a la decisión, no diagnóstico. Datos sintéticos."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from analysis import (COLUMNS, DOMAINS, NAMES, LEVELS, compute_baseline,
                      compute_zscores, compute_levels, domain_levels, explain)
from reaction_test import render_reaction_test

st.set_page_config(page_title="AstroPulse", layout="wide")
st.title("AstroPulse")
st.caption("Ayuda a la decisión, no es un diagnóstico. Datos simulados.")

tab_dash, tab_pvt = st.tabs(["Tablero", "Test de reacción"])

with tab_pvt:
    render_reaction_test()
    st.number_input("Lapsos % (copia el resultado)", 0.0, 100.0, step=5.0)

with tab_dash:
    file = st.file_uploader("Carga tu CSV (opcional)", type="csv")
    df = pd.read_csv(file) if file else pd.read_csv("data/demo.csv")

    missing = [c for c in ["day"] + COLUMNS if c not in df.columns]
    if missing:
        st.error(f"Faltan columnas en el CSV: {missing}")
        st.stop()

    base = compute_baseline(df)
    z = compute_zscores(df, base)
    lv = compute_levels(z)
    dom = domain_levels(lv)

    day = st.slider("Día", 1, len(df), len(df))
    idx = day - 1

    # Semáforo por dominio
    ICON = {0: "🟢", 1: "🟡", 2: "🔴"}
    cols = st.columns(len(DOMAINS))
    for col, name in zip(cols, DOMAINS):
        col.metric(name, f"{ICON[int(dom[name].iloc[idx])]} {LEVELS[int(dom[name].iloc[idx])]}")

    # Mensajes explicativos
    st.subheader("Qué cambió")
    msgs = explain(z, lv, idx)
    if not msgs:
        st.success("Sin desviaciones sostenidas respecto a tu línea base.")
    for m in sorted(msgs, key=lambda m: -m["nivel"]):
        st.write(f"{ICON[m['nivel']]} {m['texto']}")
    if msgs:
        st.caption("El nivel se basa en los últimos 3 días, no solo en el valor de hoy.")

    # Tendencia con banda ±2 DE
    st.subheader("Tendencias")
    var = st.selectbox("Variable", COLUMNS, format_func=lambda c: NAMES[c])
    mu, sd = base.loc[var, "mu"], base.loc[var, "sigma"]
    fig = go.Figure()
    fig.add_hrect(y0=mu - 2 * sd, y1=mu + 2 * sd, fillcolor="green", opacity=0.12, line_width=0)
    fig.add_hline(y=mu, line_dash="dash")
    fig.add_vrect(x0=0.5, x1=10.5, fillcolor="gray", opacity=0.10, line_width=0)  # ventana de línea base
    fig.add_trace(go.Scatter(x=df["day"], y=df[var], mode="lines+markers", name=NAMES[var]))
    fig.update_layout(xaxis_title="Día", yaxis_title=NAMES[var], height=380)
    st.plotly_chart(fig, use_container_width=True)