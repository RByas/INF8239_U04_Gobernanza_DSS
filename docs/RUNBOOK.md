# Incident Runbook — Territorial Review DSS

**Señales monitoreadas** (cálculo mensual sobre casos ya revisados, o ante una alerta):

| Señal | Umbral | Severidad |
|---|---|---|
| Recall global | < 0.68 | Alta |
| Brecha de recall o de FPR entre G1 y G2 | > 0.16 | Alta |
| Recall de cualquier grupo con n ≥ 30 | < 0.68 | Media |
| Identificador directo en los datos | cualquier aparición | Crítica |
| Uso fuera de alcance (elegibilidad, intervención, emergencia) | cualquier caso | Crítica |
| Apelación confirmada con daño atribuible al ranking | 1 | Alta |
| Latencia / tamaño del modelo | > 500 ms / > 1024 KB | Baja |

1. **Detection and classification:** la alerta sale de `scripts/lab13_governance.py`
   (`deployment_decision.json` con `status: REVIEW`), de un reporte del operador o de una apelación.
   El ML Engineer la clasifica según la tabla en menos de 24 h y abre un registro de incidente con ID,
   hora y señal.
2. **Containment authority:** el **Institutional Owner** (A de "Incident response" en `raci.csv`)
   decide la contención. Si la severidad es crítica o alta, el ML Engineer puede suspender el ranking de
   inmediato y avisar en menos de 4 h. Durante la contención, la cola vuelve al baseline de reglas o FIFO.
3. **Evidence preservation:** se congelan la versión del modelo (`models/*.joblib` y el hash del commit),
   los `reports/lab12` y `reports/lab13` vigentes, el lote de datos afectado y los logs de decisión. Todo
   se guarda en solo lectura, con acceso restringido a Legal y Data Scientist.
4. **Internal and affected-party communication:** el Product Owner informa a operadores y supervisores
   el mismo día. Las personas afectadas cuyos casos se revisaron tarde reciben aviso y ofrecimiento de
   revisión prioritaria. Los representantes de afectados reciben un resumen en menos de 10 días hábiles.
   Legal revisa cualquier comunicación externa.
5. **Rollback or safe baseline:** se desactiva el modelo y la cola pasa a reglas transparentes
   (`previous_incidents >= 5` o `exposure >= 0.7`) más orden de llegada. Solo se vuelve al modelo con la
   auditoría LAB12 repetida y la aprobación firmada del Product Owner.
6. **Postmortem, owner and due date:** el Data Scientist (R) y el Product Owner (A) entregan el
   postmortem sin culpables en un plazo de 10 días hábiles. Debe incluir causa raíz, daño, acciones
   correctivas con responsable y fecha, y actualización del registro de riesgos. El simulacro está en
   `reports/lab13/INCIDENT_POSTMORTEM.md`.
