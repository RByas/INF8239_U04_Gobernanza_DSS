# Traspaso entre roles (handoff)

Cada traspaso tiene un **criterio de aceptación verificable**. Quien recibe puede rechazar la entrega si
el criterio no se cumple, y la responsabilidad no se transfiere hasta que acepta. Los roles son los de
`student_inputs/raci.csv`.

| # | De → A | Qué se entrega | Criterio de aceptación (verificable) | Si falla |
|---|---|---|---|---|
| 1 | Data Engineer → Data Scientist | Lote de datos + Dataset Card | `uv run pytest -q tests/test_data.py tests/test_privacy.py` en verde; `check_environment.py` → `dataset_status: valid`; sin identificadores directos | Se devuelve el lote; no se entrena |
| 2 | Data Scientist → Product Owner | Evaluación de impacto + auditoría | `lab11_impact.py` y `validate_lab12_decision.py` sin errores; `AUDIT_REPORT.md` con n por subgrupo e IC95 | El PO no firma; estado REVIEW |
| 3 | Product Owner → ML Engineer | Decisión firmada (`DECISION_RECORD.md`, `lab12_decision.yml`) + modelo elegido | Decisión explícita (GO / LIMITAR / STOP) con condiciones; `lab13_governance.py` sin puertas ocultas | No se despliega |
| 4 | ML Engineer → Operadores | Tablero Streamlit + Model Card + Runbook | `pytest -q` (incluye AppTest) en verde; el tablero muestra el aviso sintético, los límites, la decisión humana y la alerta por grupo; capacitación registrada | Se mantiene el baseline de reglas |
| 5 | Operador → Supervisor | Casos en desacuerdo y apelaciones | Registro con ID de caso, motivo y fecha; respuesta en ≤ 5 días hábiles | Se escala al Institutional Owner |
| 6 | ML Engineer → Institutional Owner | Alerta de monitoreo o incidente | Clasificación según la tabla de `RUNBOOK.md` en < 24 h; evidencia congelada | Contención automática al baseline |
| 7 | Data Scientist → Product Owner | Postmortem | Causa raíz, acciones con responsable y fecha, registro de riesgos actualizado (≤ 10 días hábiles) | Incidente abierto; sin vuelta al modelo |

**Regla de continuidad:** si alguien con un rol R o A deja el proyecto, entrega este documento, el
historial Git (`git log`, tag vigente) y la lista de incidentes abiertos a su sucesor. El Product Owner
confirma el traspaso por escrito.
