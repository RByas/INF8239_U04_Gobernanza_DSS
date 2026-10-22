# Traspaso entre roles (handoff)

Cada traspaso tiene un **criterio de aceptación verificable**. Quien recibe puede rechazar la entrega si el criterio
no se cumple, y la responsabilidad no se transfiere hasta que acepta. Los roles son los de `student_inputs/raci.csv`.

| # | De → A | Qué se entrega | Criterio de aceptación (verificable) | Si falla |
|---|---|---|---|---|
| 1 | Data Engineer → Data Scientist | Lote de datos y Dataset Card | `uv run pytest -q tests/test_data.py tests/test_privacy.py` en verde; `check_environment.py` → `dataset_status: valid`; sin identificadores directos | Se devuelve el lote y no se entrena |
| 2 | Data Scientist → Product Owner | Evaluación de impacto y auditoría de equidad | `lab11_impact.py` y `validate_lab12_decision.py` sin errores; `AUDIT_REPORT.md` con el n de cada subgrupo, IC 95 % y mitigación | El PO no firma y el estado queda en REVIEW |
| 3 | Product Owner → ML Engineer | Decisión firmada (`DECISION_RECORD.md`, `lab12_decision.yml`) y modelo elegido | Decisión explícita (GO / LIMITAR / STOP) con condiciones; `lab13_governance.py` sin puertas ocultas y con `trace` | No se despliega |
| 4 | ML Engineer → Operadores | Tablero Streamlit, Model Card y runbook | `pytest -q` en verde (incluye AppTest); el tablero muestra el aviso sintético, los límites, la puerta fallida, la cola priorizada y la acción humana; capacitación registrada | Se mantiene la cola FIFO |
| 5 | Operador → Supervisor | Casos en desacuerdo y apelaciones | Registro con ID del caso, motivo y fecha; respuesta escrita en ≤ 10 días hábiles | Se escala al Institutional Owner |
| 6 | ML Engineer → Institutional Owner | Alerta de monitoreo o incidente | `lab13_monitor.py` o `lab13_governance.py` con alerta; clasificación según `RUNBOOK.md` en < 24 h; evidencia congelada (`trace`) | Contención inmediata a la cola FIFO |
| 7 | Data Scientist → Product Owner | Postmortem | Causa raíz y acciones con responsable y fecha; registro de riesgos actualizado (≤ 10 días hábiles) | El incidente sigue abierto y no se vuelve al modelo |

**Regla de continuidad:** si alguien con un rol R o A deja el proyecto, entrega este documento, el historial Git
(`git log` y el tag vigente) y la lista de incidentes abiertos a su sucesor. El Product Owner confirma el traspaso
por escrito.

**Estado actual (2026-10-22):** el traspaso 3 está **detenido**. La decisión es LIMITAR y `lab13_governance.py`
devuelve REVIEW (`group_recall`), así que el ML Engineer no recibe un modelo para desplegar hasta que el Product
Owner elija una mitigación y una nueva auditoría devuelva GO.
