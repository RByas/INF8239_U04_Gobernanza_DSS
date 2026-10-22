# Postmortem del simulacro (sin culpables)

**ID:** INC-2026-001 (simulacro) · **Severidad:** Alta · **Accountable:** Institutional Owner · **Fecha:** 2026-10-22
**Evidencia generada:** `reports/lab13/incident_drill.json`, producido por `uv run python scripts/simulate_incident.py`.

## Escenario
Tras una actualización, entra a producción el **árbol de decisión** en lugar del modelo logístico revisado. Para
que la señal sea real y no solo declarada, el simulacro pasa ese modelo por las mismas puertas de
`configs/governance.yml`.

**Resultado:** `status: REVIEW`, con tres puertas fallidas.

| Puerta | Valor | Umbral |
|---|---|---|
| `recall_gap` | 0.181 | ≤ 0.16 |
| `fpr_gap` | 0.168 | ≤ 0.16 |
| `group_recall` | 0.633 en G1 | ≥ 0.68 |

**La puerta fallida produjo REVIEW y no se ocultó.**

## Línea de tiempo
| Paso del runbook | Acción | Rol |
|---|---|---|
| 1. Detección | La decisión del pipeline pasa a REVIEW con tres puertas fallidas. Se clasifica como severidad alta (brecha > 0.16 y recall de G1 < 0.68) y se abre el registro INC-2026-001. | ML Engineer |
| 2. Contención | Se suspende el ranking y la cola vuelve a la alternativa FIFO con reglas públicas. | ML Engineer (R), Institutional Owner (A) |
| 3. Evidencia | Se congela el bloque `trace` del simulacro (commit, hash de la política, modelo `tree`), junto con `reports/lab12/tree/` y `deployment_decision.json`. | ML Engineer |
| 4. Comunicación | El Product Owner avisa a operadores y supervisores el mismo día. Las personas de G1 cuyos casos se revisaron tarde reciben un aviso y una revisión prioritaria. Los representantes de los afectados reciben un resumen en un máximo de 10 días hábiles, revisado por Legal. | Product Owner (R), Institutional Owner (A) |
| 5. Rollback | **No se vuelve al modelo logístico:** al pasarlo por las puertas también da REVIEW (`group_recall`, G1 = 0.653). La cola se mantiene en FIFO hasta que el Product Owner elija una mitigación (B2 o D) y una nueva auditoría devuelva GO. | ML Engineer (R), Institutional Owner (A) |
| 6. Postmortem | Este documento. | Data Scientist (R), Product Owner (A) |

## Causa raíz (simulada)
1. **Las puertas no bloqueaban el despliegue.** El pipeline emite una recomendación, pero nada impide publicar otro modelo.
2. **Hasta este laboratorio, las puertas solo revisaban el recall global y las brechas.** El modelo logístico obtenía GO aunque el recall de G1 (0.653) quedara por debajo de 0.68. El simulacro confirmó que hacía falta la puerta `group_recall`, que ya está activa.

## Daño
Es un simulacro con datos sintéticos, así que no hubo daño real. En un caso real, el daño serían los casos de G1 con riesgo real que quedaron sin revisión oportuna durante el periodo con el árbol en producción.

## Acciones correctivas
| Acción | Responsable | Fecha | Estado |
|---|---|---|---|
| Añadir la puerta de recall mínimo por grupo (≥ 0.68, grupos con n ≥ 30) | Data Scientist | 2026-10-22 | Hecho (`src/inf8239_u04/governance.py`, `tests/test_governance.py`) |
| Añadir la puerta de privacidad (STOP si `protected_group` o un identificador directo entra al modelo) | Data Scientist | 2026-10-22 | Hecho |
| Registrar commit, política y evidencia en cada recomendación (`trace`) | ML Engineer | 2026-10-22 | Hecho |
| Exigir `status: GO` **y** la firma del Product Owner antes de publicar un modelo (bloqueo en CI) | ML Engineer | 2026-11-05 | Pendiente |
| Incluir en `deployment_decision.json` los intervalos de confianza de las brechas | Data Scientist | 2026-11-05 | Pendiente |
| Elegir la mitigación (B2 o D) con revisión legal para D | Product Owner | 2026-11-12 | Pendiente |
| Repetir el simulacro con el procedimiento corregido | Product Owner | 2026-11-19 | Pendiente |
| Actualizar R01 y R07 en el registro de riesgos con lo aprendido | Data Scientist | 2026-11-05 | Pendiente |

## Lecciones
- Un archivo de control no es un control eficaz: la puerta protege solo si alguien con autoridad la aplica.
- Un GO automático basado en promedios no reemplaza la revisión humana de la evidencia desagregada.
- El rollback debe ir a una alternativa que **sí** cumpla la política. El modelo anterior también puede estar fuera de tolerancia.
