# Declaración de uso de IA

## LAB11 · Evaluación de impacto ético

| Campo | Detalle |
|---|---|
| Herramienta | Claude (Anthropic), modelo Claude Opus 5.5, mediante Claude Code |
| Finalidad | Configurar el proyecto, corregir un error de sintaxis en los scripts base, explorar los datos y redactar un **borrador** de `lab11_impact.yml`, `stakeholders.csv`, `risk_register.csv` y `DECISION_RECORD.md` |
| Prompts relevantes | "aydame" con el manual LAB11 y el enunciado del Ejercicio 07 adjuntos; luego el zip del proyecto base |
| Fragmentos afectados | `scripts/lab11_impact.py` y `scripts/simulate_incident.py` (strings sin cerrar → `SyntaxError`); los tres archivos de `student_inputs/`; `reports/lab11/DECISION_RECORD.md` |
| Verificaciones automáticas | `uv run pytest -q` (10 passed); `tests/test_impact.py` y `tests/test_privacy.py` (3 passed); `scripts/lab11_impact.py` sin errores |
| Errores detectados | El script base no compilaba; `DECISION_RECORD.md` se sobrescribía en cada ejecución (ahora se crea solo si no existe) |
| Verificación humana | REPLACE — qué revisó el estudiante: cifras de los datos, escala de probabilidad e impacto, responsables, decisión REVIEW |
| Correcciones del estudiante | REPLACE — cambios hechos al borrador de la IA y por qué |

## LAB12 · Auditoría de equidad

| Campo | Detalle |
|---|---|
| Prompt relevante | "continuar si falta algo me indica" con los manuales LAB12/LAB13 y el enunciado del Ejercicio 08 |
| Finalidad | Ejecutar las auditorías logistic/tree, escribir `scripts/lab12_compare.py` (baseline de reglas + IC95 bootstrap + soporte interseccional), redactar `lab12_decision.yml` y `reports/lab12/AUDIT_REPORT.md` |
| Fragmentos afectados | `scripts/lab12_compare.py` (nuevo), `configs/governance.yml` (`min_group_size: 30`), `student_inputs/lab12_decision.yml`, R01 de `risk_register.csv`, adenda de `DECISION_RECORD.md` |
| Verificaciones automáticas | `validate_lab12_decision.py` → documented; `tests/test_fairness.py`, `tests/test_model.py` (2 passed) |
| Errores detectados | La hipótesis de LAB11 (recall menor en G2) era falsa según los datos; se corrigió R01. El commit incluyó por error una copia anidada del proyecto, que se retiró del índice |
| Verificación humana | REPLACE — p. ej. recalcular a mano una métrica de `fairness_by_group.csv`; decidir si `min_group_size` = 30 es razonable |
| Correcciones del estudiante | REPLACE |

## LAB13 · Gobernanza y DSS

| Campo | Detalle |
|---|---|
| Finalidad | Ampliar la RACI, redactar Dataset Card, Model Card y Runbook, ejecutar el simulacro (drill con el modelo tree), escribir el postmortem, añadir trazabilidad y alerta de recall por grupo a `app.py`, exportar `requirements.txt` |
| Verificaciones automáticas | `uv run pytest -q` (10 passed, incluye AppTest de Streamlit); revisión del tablero en el navegador; `lab13_governance.py` → GO; drill tree → REVIEW con `recall_gap` y `fpr_gap` fallidos |
| Advertencias | Los plazos de retención y la mención a la Ley 172-13 son propuestas que el estudiante debe verificar en la fuente legal; la IA no hizo interpretación jurídica |
| Verificación humana | REPLACE |
| Correcciones del estudiante | REPLACE |

La IA no decidió los valores del análisis. El estudiante revisó, ajustó y asume la responsabilidad de
las puntuaciones de riesgo, la interpretación normativa y la decisión final.
