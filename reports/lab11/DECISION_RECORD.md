# Registro de decisión · LAB11

**Sistema:** Territorial Review DSS (sintético) · **Propietario (A):** Product Owner institucional · **Fecha:** 2026-10-15

> **Nota de versión.** La evaluación de impacto (propósito, interesados, riesgos, alternativa, apelación y condición de retiro) se definió antes de entrenar el modelo. Las cifras de recall y FPR citadas abajo se incorporaron después, con la evidencia de la auditoría de LAB12 (`reports/lab12/`), para actualizar la interpretación de los riesgos. Los controles de R06 y R07 que dependen del runbook y del monitoreo quedan **pendientes de LAB13**.

## Decisión
**REVISAR (REVIEW).** Se puede continuar con la auditoría de equidad (LAB12) y con un piloto limitado, siempre con revisión humana de todos los casos. **No** se autoriza ningún despliegue con acciones automáticas.

## Riesgos prioritarios (`risk_register_scored.csv`)
| Riesgo | Prioridad | Observación | Evidencia | Interpretación |
|---|---|---|---|---|
| R02 · Brecha de falsos positivos (FPR) en G2 | 9 | El modelo logístico tiene FPR de 0.375 en G2 frente a 0.250 en G1 (brecha de 0.125). | `reports/lab12/logistic/fairness_by_group.csv` | Está por debajo del límite de 0.16, pero G2 recibe más revisiones innecesarias. El árbol de decisión supera el límite (0.168). |
| R01 · Falsos negativos en G1 | 8 | El recall de G1 es 0.653, frente a 0.791 en G2 y 0.717 a nivel global. | `reports/lab12/logistic/global_metrics.json` | G1 queda por debajo del recall mínimo de 0.68 aunque el promedio global lo cumple. Esto significa que se pierden casos reales de G1. |
| R07 · Deriva temporal | 8 | La evaluación usa una partición temporal: entrenamiento hasta el 2026-09-24 y prueba desde el 2026-09-25 (160 casos). | `src/inf8239_u04/data.py`, `scripts/describe_dataset.py` | El periodo de prueba es corto y no permite saber cómo se comportará el modelo en meses posteriores. Hace falta monitoreo. |

## Incertidumbre
- La muestra de prueba es pequeña: 101 casos de G1 y 59 de G2. Algunos subgrupos interseccionales tienen menos de 30 casos (por ejemplo, G2 | 45-59 tiene solo 8), así que sus métricas son inestables (R03).
- Los datos son sintéticos. Este análisis no permite concluir nada sobre la población real de República Dominicana.
- La puntuación de prioridad (probabilidad × impacto) sirve para ordenar la atención. No mide el daño humano real, y los escenarios fueron revisados uno por uno.

## Proporcionalidad y alternativa
La alternativa no predictiva (cola FIFO con reglas públicas de umbral) sigue disponible como línea base segura. El modelo solo se justifica si mejora el recall de **ambos** grupos frente a esa línea base sin superar las brechas permitidas.

## Condición de retiro
Se vuelve a la alternativa FIFO si ocurre cualquiera de estas situaciones:
- El recall global baja de 0.68.
- La brecha de recall o de FPR entre grupos supera 0.16.
- Se detecta un uso fuera de alcance.
- Se confirma un incidente con daño.

## Responsables y próximos pasos
- **Data Scientist:** completar la auditoría de equidad (LAB12) y evaluar si un umbral distinto por grupo o una mitigación reduce la brecha de recall de G1.
- **Product Owner:** aprobar o rechazar el piloto con la evidencia de LAB12.
- **ML Engineer:** definir el monitoreo de la deriva temporal (LAB13).
