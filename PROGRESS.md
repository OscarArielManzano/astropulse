# PROGRESS
## Hecho (probado por Oscar)
- analysis.py: baseline, z-scores, persistencia 3 días (mismo signo), semáforo por dominio, explain, summarize
- simulate.py: demo.csv y cohort.csv
- reaction_test.py: test de reacción (el resultado se copia a mano al CSV)
- app.py: pestañas Dashboard, Reaction test, Experiment
- experiment.py: umbral fijo vs línea base personal (data/experiment_level1.csv y 2)
## Pendiente
- Formulario de registro diario; dose_mSv acumulado (límite de Gabo); exportar resumen
- Diseño (style.py, config.toml, paleta de gráficas); README; video; presentación
## Decisiones
- Variables actualizadas: sin mood; se agregan temp_c, hrv_rmssd, grip_kg
- Persistencia: 3 días seguidos con el mismo signo de z
- Interfaz y textos en inglés
## Parámetros sin fuente (Gabo)
- Piso de sigma = 1 % de la media; BETWEEN = 2.0 y tamaños de deterioro en simulate.py