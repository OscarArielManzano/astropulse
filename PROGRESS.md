# PROGRESS
## Hecho (probado por Oscar, salvo lo marcado)
- analysis.py: baseline, z-scores, persistencia 3 días (mismo signo), semáforo por dominio, explain, summarize
- analysis.py: dose_summary (límite 600 mSv, NASA-STD-3001; Gabo debe confirmar revisión) y build_report (SIN PROBAR)
- simulate.py: demo.csv y cohort.csv
- reaction_test.py: test de reacción (el resultado se copia a mano al formulario)
- experiment.py: umbral fijo vs línea base personal (data/experiment_level1.csv y 2)
- app.py: pestañas Dashboard, Reaction test, Experiment; guía del CSV; formulario diario; dosis acumulada (SIN PROBAR); exportar resumen .md (SIN PROBAR)
## Pendiente
- Diseño de Krissia: style.py, .streamlit/config.toml, paleta de gráficas Plotly (hoy son azules por defecto)
- Foundation Document: variables nuevas (sin mood), persistencia con mismo signo, idioma inglés, dosis
- Gabo: sensibilidad del experimento a BETWEEN (0.5, 1, 2), fuentes de parámetros, diapositiva de costos
- README, video, presentación
## Decisiones
- Variables: sin mood; se agregan temp_c, hrv_rmssd, grip_kg. Columna day en el CSV.
- Persistencia: 3 días seguidos con el mismo signo de z
- Interfaz y textos en inglés
- Dosis: solo registro y acumulado, no cambia el semáforo
## Parámetros sin fuente (Gabo)
- Piso de sigma = 1 % de la media; BETWEEN = 2.0 y tamaños de deterioro en simulate.py
- Rangos de los campos del formulario; norma poblacional del experimento (sale de los datos simulados)
## Recortado
- Fatiga circadiana, CUSUM