AstroPulse(Nombre a Decidir): Foundation Document
Tablero offline de líneas base personalizadas para la salud de astronautas en misiones de larga duración
NASA Space Apps Challenge 2026 · Reto: software de monitoreo de salud para misiones de larga duración
Equipo: Oscar (programación), Krissia (diseño y comunicación), Gabo (estadística y costos)
Versión 1.0 · 15 de noviembre de 2026
1. Resumen ejecutivo
AstroPulse es una aplicación en Python que permite a un astronauta registrar sus indicadores de salud diarios y detectar cambios respecto a su propia normalidad, no respecto a un promedio poblacional. El sistema calcula una línea base personal, compara cada día nuevo contra ella mediante z-scores, agrupa las desviaciones en los cuatro riesgos del reto (inmunidad y radiación, hueso y músculo, cardiovascular, conductual) y muestra un semáforo explicable con acciones sugeridas.
Funciona completamente offline, sin servidor ni conexión con la Tierra, lo que responde al problema central del reto: en misiones largas el retraso de comunicación obliga a la tripulación a evaluarse y actuar de forma autónoma.
AstroPulse es una ayuda a la decisión, no un dispositivo médico: marca desviaciones y sugiere revisar, nunca diagnostica ni prescribe tratamiento.
2. Problema y contexto
Las misiones de larga duración exponen a los astronautas a radiación espacial, aislamiento y confinamiento, gravedad alterada y un entorno cerrado y hostil. Esto puede producir cambios inmunes, pérdida ósea, eventos cardiovasculares y problemas de salud conductual. En misiones lejanas, buena parte de la responsabilidad de notar estos cambios recae en el propio astronauta.
El reto pide construir un software que reúna indicadores de salud y permita al astronauta evaluar su estado y actuar.
3. Brecha identificada en la literatura
La búsqueda bibliográfica del equipo señala los siguientes hallazgos:
El monitoreo actual (por ejemplo, el sistema CHeCS de la ISS) está fragmentado en subsistemas independientes y su procesamiento es retrospectivo, lo que produce una gestión reactiva y no proactiva.
Las tecnologías actuales se limitan sobre todo a monitorear, no a predecir.
Las líneas base personalizadas (zonas de confort de ±2 desviaciones estándar) redujeron falsos positivos y negativos frente a normas poblacionales en datos simulados.
El déficit de sueño en vuelo está documentado objetivamente, y hay datos de rendimiento cognitivo reducido en vuelo.
Persisten obstáculos: muestras pequeñas y líneas base cambiantes.
Las brechas más claras para software pequeño son: líneas base personalizadas, alertas de anomalías y soporte de decisiones offline.
Conclusión del equipo: el mayor valor para un prototipo de pocas horas es un tablero de anomalías con línea base personal, transparente y offline.
4. Objetivo y alcance
Objetivo general. Desarrollar un prototipo funcional que detecte de forma temprana y explicable desviaciones en los indicadores de salud de un astronauta respecto a su propia línea base, y que oriente su siguiente acción.
Objetivos específicos
Calcular una línea base individual a partir de los primeros días de registro.
Generar alertas por variable y por dominio de riesgo con reglas transparentes.
Mostrar tendencias y explicar en lenguaje claro qué se desvió, cuánto y durante cuántos días.
Evaluar cuantitativamente, con datos simulados, si la línea base personal supera al umbral fijo poblacional.
Dentro del alcance: registro y carga de datos, línea base, z-scores, semáforos, tendencias, plan de acción por reglas, exportación de resumen, datos sintéticos y experimento comparativo.
Fuera del alcance: diagnóstico clínico, modelado de biofísica de radiación, conexión con sensores reales, aprendizaje automático, validación con datos de vuelo.
5. Usuarios y escenario de uso
Usuario principal: un tripulante en una misión de larga duración, sin comunicación inmediata con Tierra.
Usuario secundario: el oficial médico de la tripulación o control de misión, que recibe un resumen exportado.
Escenario de demostración. Un astronauta simulado de 30 días mantiene valores estables durante los primeros 10 días, que fijan su línea base. Hacia el día 15 comienza una semana de déficit de sueño, con pulso en reposo ligeramente elevado y ánimo en descenso. AstroPulse emite alerta amarilla en el dominio conductual a los pocos días, la eleva a roja si la desviación persiste y explica qué variables cambiaron y cuánto.
6. Descripción funcional
Registro diario. El astronauta ingresa sus datos en un formulario o carga un archivo CSV con su historial.
Línea base. El sistema calcula media y desviación estándar de cada variable en la ventana inicial (por defecto, los primeros 10 días).
Comparación diaria. Cada nuevo valor se convierte en un z-score respecto a la línea base.
Semáforos. Las variables se agrupan en cuatro dominios y cada dominio recibe un color.
Plan de acción explicable. Reglas simples de tipo si-entonces traducen las desviaciones en recomendaciones de revisión.
Tendencias. Gráficas con la banda de ±2 desviaciones estándar muestran la evolución de cada variable.
Resumen exportable. Un reporte breve para control de misión.
7. Variables medidas
Variable (columna CSV)
Dominio del reto
Propósito
sleep_h horas de sueño
Conductual y cognitivo
Detectar déficit de sueño
hr_rest pulso en reposo
Cardiovascular
Detectar desviaciones de carga cardiovascular
exercise_min minutos de ejercicio, incluido el resistivo
Hueso y músculo
Seguir el cumplimiento de contramedidas
mood ánimo (1 a 5)
Conductual
Detectar efectos del aislamiento
stress estrés (1 a 5)
Conductual
Detectar efectos del confinamiento
pvt_lapses_pct lapsos de reacción mayores a 500 ms (opcional)
Cognitivo
Estimar rendimiento y fatiga
dose_mSv dosis de radiación (simulada)
Inmunidad y radiación
Registro y acumulado frente a un límite configurable

La radiación se trata solo como registro y acumulado; no se modela su biofísica.
8. Metodología analítica
Línea base. Para cada variable se calcula la media μ y la desviación estándar σ sobre la ventana inicial.
Z-score diario. z = (valor de hoy − μ) / σ.
Niveles de alerta
Verde: |z| menor que 1.
Amarillo: |z| entre 1 y 2.
Rojo: |z| mayor o igual que 2.
Persistencia. Para reducir falsas alarmas, el nivel solo sube si la desviación se mantiene durante al menos 3 días consecutivos.
Semáforo por dominio. Cada dominio toma el peor estado de sus variables.
Opcionales si el tiempo lo permite
Detección de deriva lenta con suma acumulada (CUSUM).
Estimador de fatiga circadiana con el modelo de dos procesos de Borbély (Proceso S de presión de sueño y Proceso C circadiano). Los parámetros deben verificarse en la literatura antes de usarse.
Todo el cálculo se hace con pandas y numpy; no se usa aprendizaje automático, de modo que cada alerta es explicable.
9. Arquitectura técnica
Lenguaje: Python. Interfaz: Streamlit. Librerías: pandas, numpy, plotly.
astropulse/
├── app.py            # interfaz (Streamlit)
├── analysis.py       # línea base, z-scores, semáforos, reglas
├── style.py          # paleta, fuentes y CSS (diseño de Krissia)
├── simulate.py       # generador de astronautas sintéticos
├── experiment.py     # umbral fijo vs. línea base personal
├── data/demo.csv     # 30 días de ejemplo con anomalía
├── assets/           # logo e íconos exportados
├── .streamlit/config.toml   # tema visual
└── requirements.txt
El contrato entre integrantes es el esquema del CSV de la sección 7: si todos respetan esos nombres de columna, el trabajo puede avanzar en paralelo.
10. Resultados esperados y evaluación
En la demostración. Se espera que todos los dominios permanezcan en verde durante la línea base, y que la anomalía de sueño produzca alerta amarilla pocos días después de iniciar y alerta roja si persiste, con un mensaje que explique qué se desvió.
Experimento comparativo. Se simulan unos 100 astronautas con distintas normalidades y un periodo de deterioro. Se comparan dos métodos:
Umbral fijo poblacional.
Línea base personal con z-score.
Métricas: retraso de detección (días hasta la alerta) y falsos positivos por astronauta.
Hipótesis: la línea base personal detecta antes y con menos falsas alarmas. Si el resultado fuera distinto, se reportará tal cual, porque es un hallazgo válido.
Los resultados provienen de datos sintéticos y no constituyen validación clínica.
11. Impacto y análisis de costos
La detección temprana busca reducir la probabilidad de que un problema evolucione hasta requerir una intervención mayor o una comunicación urgente con la Tierra. El análisis de costos, a cargo de Gabo, se presentará como una estimación con supuestos explícitos, comparando:
Costo de operar un sistema liviano, offline y de bajo consumo.
Costo potencial de un evento de salud detectado tarde.
Dependencia de la comunicación en tiempo real con Tierra.
No se afirmarán cifras sin fuente.
12. Limitaciones y consideraciones éticas
Los datos son sintéticos; no hay validación clínica ni de vuelo.
Es una herramienta de apoyo a la decisión, no de diagnóstico; sugiere revisión, no tratamiento.
No reemplaza biosensores ni revierte la pérdida ósea o el daño por radiación.
Con muestras pequeñas y líneas base cambiantes, el método requiere recalibración periódica.
Los umbrales son referenciales y deben ajustarse con asesoría médica real.
13. Roles y responsabilidades
Integrante
Rol
Tareas principales
Oscar
Programación
app.py, analysis.py, integración del diseño, exportación, video de demostración
Krissia
Diseño y comunicación
Identidad visual, kit de diseño de la interfaz, textos de alertas, guion del video, presentación
Gabo
Estadística y costos
Umbrales y parámetros con fuentes, simulate.py y demo.csv, experiment.py, diapositiva de costos y limitaciones

14. Cronograma (5 horas)
Hora
Hito
0:00
Acordar alcance, esquema CSV y kit de diseño
0:45
Primer kit de diseño de Krissia; entorno y estructura listos
1:45
demo.csv de Gabo; primera versión de la interfaz
3:00
Congelar funciones; solo corrección de errores
3:30
Experimento y gráficas listos; video grabado
4:30
Presentación terminada
5:00
Entrega con margen

Orden de recorte si falta tiempo: fatiga circadiana, CUSUM, exportar resumen. No se recorta: línea base, semáforo y demostración.
15. Entregables
Aplicación AstroPulse funcionando (repositorio o carpeta con instrucciones de ejecución).
Video de demostración de 1 a 2 minutos.
Presentación de 6 a 7 diapositivas.
Resultados del experimento comparativo con sus gráficas.
Este documento como descripción del proyecto.
16. Trabajo futuro
Conexión con datos de wearables reales.
Ajuste de la línea base de forma continua (ventana móvil).
Integración de más fuentes de datos y de un módulo de fatiga circadiana validado.
Evaluación con conjuntos de datos públicos de NASA y asesoría de profesionales de medicina espacial.
17. Referencias base
Citas tal como aparecen en la búsqueda bibliográfica del equipo; verificar autores y títulos completos antes de la entrega.
Jarboui 2026: líneas base personalizadas con zonas de ±2 DE.
Altwajre 2025: detección de anomalías con autoencoders LSTM sobre datos de wearables.
Prysyazhnyuk 2021: limitaciones del sistema CHeCS y procesamiento retrospectivo.
Scott 2021: Precision Space Health y monitoreo más allá de la órbita baja.
Barger 2014: déficit de sueño en vuelo.
Dev 2024: rendimiento cognitivo en vuelo.
Popov 2023: arquitectura PHM/HeSS.
Schmidt 2026: obstáculos de muestras pequeñas y líneas base cambiantes.
Roda 2018: restricciones de biosensores en vuelo.

