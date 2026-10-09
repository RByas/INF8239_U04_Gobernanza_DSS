# Incident simulation

- detected_at: 2026-10-09T01:44:42.994300+00:00
- signal: recall gap exceeded
- containment: REVIEW and safe baseline
- evidence: preserved report and model version
- communication: Product Owner notifica a operadores y supervisores el mismo día; aviso y revisión prioritaria a personas de G1 cuyos casos se revisaron tarde; resumen a representantes de afectados en ≤ 10 días hábiles (revisado por Legal)
- corrective actions, owners and dates: ver tabla "Acciones correctivas"

## Postmortem del simulacro (sin culpables)

**ID:** INC-2026-001 (simulacro) · **Severidad:** Alta · **Accountable:** Institutional Owner

### Escenario

Se simula que, tras una actualización, entra a producción el modelo *tree* en lugar del *logistic*
aprobado. Para que la señal sea real y no solo declarada, el drill pasa ese modelo por las mismas puertas:

```bash
uv run python -c "from inf8239_u04.data import load_data; from inf8239_u04.governance import load_config; from inf8239_u04.pipeline import run; print(run(load_data(),load_config()['gates'],kind='tree')['decision'])"
```

Resultado: `status: REVIEW`, `failed: ['recall_gap', 'fpr_gap']` (brecha de recall 0.181 > 0.16 y de
FPR 0.168 > 0.16). **La puerta fallida produjo REVIEW y no se ocultó.**

### Línea de tiempo

| Paso del runbook | Acción | Rol |
|---|---|---|
| 1. Detección | La alerta de gate pasa a REVIEW. Se clasifica como severidad alta (brecha > 0.16). | ML Engineer |
| 2. Contención | Se suspende el ranking y la cola vuelve al baseline de reglas + FIFO. | ML Engineer (R), Institutional Owner (A) |
| 3. Evidencia | Se congelan el modelo, el hash de commit, `reports/lab12/tree` y `deployment_decision.json`. | ML Engineer |
| 4. Comunicación | Avisos según la sección anterior. | Product Owner |
| 5. Rollback | Se restaura logistic: `uv run python scripts/lab13_governance.py`, que vuelve a dar GO en las puertas. Se mantiene la decisión humana LIMITAR. | ML Engineer |
| 6. Postmortem | Este documento. | Data Scientist (R), Product Owner (A) |

### Causa raíz (simulada)

Las puertas existían, pero **no bloqueaban el despliegue**: el pipeline genera una recomendación y nada
impide publicar otro modelo. A eso se suma una debilidad descubierta en el simulacro: las puertas solo
miran brechas y recall global, de modo que el GO del modelo logistic oculta que el recall de G1
(0.653) está por debajo de 0.68.

### Acciones correctivas

| Acción | Responsable | Fecha |
|---|---|---|
| Hacer que el despliegue requiera `status: GO` **y** la firma del Product Owner (bloqueo en CI) | ML Engineer | 2026-10-22 |
| Añadir un gate de recall mínimo por grupo (≥ 0.68) para grupos con n ≥ 30 | Data Scientist | 2026-10-22 |
| Reportar los IC95 de las brechas en `deployment_decision.json` | Data Scientist | 2026-10-29 |
| Repetir el simulacro con el procedimiento corregido | Product Owner | 2026-11-05 |
| Actualizar R01 y R07 en el registro de riesgos con lo aprendido | Data Scientist | 2026-10-15 |

### Lecciones

Un archivo de control no es un control eficaz. La puerta solo protege si alguien con autoridad la
aplica, y un GO automático no reemplaza la revisión humana de la evidencia desagregada.
