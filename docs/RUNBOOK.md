# Incident Runbook — Territorial Review DSS

**Señales monitoreadas.** Se calculan cada mes sobre los casos ya revisados con `uv run python scripts/lab13_monitor.py`, que escribe `reports/lab13/monitoring_monthly.csv` y `monitoring_summary.json`. Ante una alerta se usa además `uv run python scripts/lab13_governance.py`.

En el monitoreo mensual, un mes queda en `ALERT` si un grupo con n ≥ 30 baja de 0.68 de recall; en `REVIEW` si solo se supera una brecha; y en `LOW_SUPPORT` si ningún grupo alcanza n ≥ 30, caso en que se revisa sin concluir. Los traspasos y sus criterios de aceptación están en `docs/HANDOFF.md`.

**Último monitoreo (prueba temporal, de septiembre a diciembre de 2026):**
- **Octubre, noviembre y diciembre:** en `ALERT`, porque el recall de G1 fue de 0.643, 0.625 y 0.667.
- **Septiembre:** en `LOW_SUPPORT`, con 6 casos.

La falla de G1 es **persistente**, no un accidente de un solo corte, y respalda la decisión LIMITAR.

| Señal | Umbral | Puerta | Severidad |
|---|---|---|---|
| Identificador directo o `protected_group` entre las variables del modelo | Cualquier aparición | `privacy` → STOP | Crítica |
| Uso fuera de alcance (elegibilidad, intervención o emergencia) | Cualquier caso | — | Crítica |
| Recall global | < 0.68 | `recall` → REVIEW | Alta |
| Recall de cualquier grupo con n ≥ 30 | < 0.68 | `group_recall` → REVIEW | Alta |
| Brecha de recall o de FPR entre G1 y G2 | > 0.16 | `recall_gap` / `fpr_gap` → REVIEW | Alta |
| Apelación confirmada con daño atribuible al ranking | 1 | — | Alta |
| Latencia o tamaño del modelo | > 500 ms / > 1024 KB | `latency` / `model_size` → REVIEW | Baja |

1. **Detección y clasificación.** La alerta puede llegar de tres fuentes:
   - `reports/lab13/deployment_decision.json`, cuando `status` es REVIEW o STOP;
   - un reporte del operador;
   - una apelación.

   El ML Engineer clasifica la alerta según la tabla en menos de 24 h. Luego abre un registro de incidente con su ID, la hora y la señal.
2. **Autoridad de contención.** Decide el **Institutional Owner**, que es el A de "Incident response" en `student_inputs/raci.csv`. Si la severidad es crítica o alta, el ML Engineer suspende el ranking de inmediato y avisa en menos de 4 h. Mientras dura la contención, la cola vuelve a la alternativa segura (paso 5).
3. **Preservación de evidencia.** Se congela, en solo lectura:
   - el modelo (`models/*.joblib`) y el bloque `trace` de `deployment_decision.json` (commit, hash de la política y versión);
   - los reportes vigentes de `reports/lab12/` y `reports/lab13/`;
   - el lote de datos afectado y los logs de decisión.

   Solo Legal y el Data Scientist tienen acceso.
4. **Comunicación interna y a las personas afectadas.**
   - El Product Owner informa a operadores y supervisores el mismo día.
   - Las personas cuyos casos se revisaron tarde reciben un aviso y la oferta de una revisión prioritaria.
   - Los representantes de las personas afectadas reciben un resumen en un máximo de 10 días hábiles.

   Legal revisa toda comunicación externa (responsable: Institutional Owner, actividad "External communication").
5. **Rollback o alternativa segura.** Se desactiva el modelo y la cola vuelve a la alternativa no predictiva de LAB11: orden de llegada (FIFO) con las reglas públicas sobre incidentes previos y exposición. La responsable es la actividad "Rollback to baseline", con el ML Engineer como R y el Institutional Owner como A. Para volver al modelo hacen falta tres condiciones:
   - repetir la auditoría de LAB12;
   - que `lab13_governance.py` devuelva GO;
   - que el Product Owner firme la aprobación.
6. **Postmortem, responsable y plazo.** El Data Scientist (R) y el Product Owner (A) entregan un postmortem sin culpables en un máximo de 10 días hábiles. Debe incluir la causa raíz, el daño, las acciones correctivas con su responsable y fecha, y la actualización del registro de riesgos. El simulacro de referencia está en `reports/lab13/INCIDENT_POSTMORTEM.md`.
