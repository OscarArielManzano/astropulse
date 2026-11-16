import streamlit as st
from reaction_test import render_reaction_test

render_reaction_test()
pvt = st.number_input("Lapsos % (copia el resultado del test)", 0.0, 100.0, step=5.0)
