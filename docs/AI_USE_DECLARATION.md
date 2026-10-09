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

La IA no decidió los valores del análisis. El estudiante revisó, ajustó y asume la responsabilidad de
las puntuaciones de riesgo, la interpretación normativa y la decisión final.
