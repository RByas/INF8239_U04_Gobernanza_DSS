# Decision record — LAB11 · Evaluación de impacto ético

**Sistema:** Territorial Review DSS - Synthetic (prioriza casos sintéticos para revisión humana)
**Responsable de la decisión (accountable):** Product Owner institucional
**Autoridad de retiro:** Institutional Owner
**Fecha:** 2026-10-08 · **Próxima revisión:** al cerrar LAB12 (auditoría de equidad)

## Decisión

**REVIEW** — continuar el desarrollo **sin desplegar**. El sistema solo puede pasar a GO cuando la
auditoría de LAB12 demuestre que se cumplen los gates de `configs/governance.yml`
(recall ≥ 0.68; brecha de recall y de FPR entre G1 y G2 ≤ 0.16). Mientras tanto la cola se
ordena con la alternativa no predictiva (FIFO + reglas transparentes).

## Evidencia disponible

| Evidencia | Qué muestra | Qué NO demuestra |
|---|---|---|
| `uv run python scripts/check_environment.py` → `dataset_status: valid`, 640 filas | El dataset cumple el contrato técnico | Que sea adecuado para decidir sobre personas reales |
| Tasa base del target: G1 = 0.497, G2 = 0.639; Sur = 0.616 | Las clases están desbalanceadas por grupo y zona | Si la diferencia es real o se debe a cómo se registran los incidentes (R10) |
| Medias por grupo: infrastructure_score G1 0.566 / G2 0.444; exposure G1 0.469 / G2 0.559 | Hay features correlacionadas con el grupo protegido | Cuánto contribuyen a la disparidad del modelo (pendiente en LAB12) |
| Test temporal: 160 casos (G1 101, G2 59); G2 \| 45-59 = 8 | Hay subgrupos interseccionales muy pequeños | Métricas confiables para esos subgrupos |
| `risk_register_scored.csv` (10 riesgos) | Orden de atención según probabilidad × impacto | Una medida "objetiva" del daño humano |
| `tests/test_impact.py`, `tests/test_privacy.py` → 3 passed | Se rechazan los placeholders y los identificadores directos | La eficacia de los controles organizacionales |

## Los tres riesgos prioritarios (interpretados, no solo ordenados)

El script ordena por prioridad = probabilidad × impacto. Con ese criterio los tres primeros son
**R02 (9), R09 (9) y R01 (8)**. Revisé los escenarios antes de aceptar ese orden:

1. **R01 — Recall menor en G2 (falsos negativos desiguales).** Es el riesgo con **impacto 4 y riesgo
   residual alto**. Aunque su puntaje (8) es menor que el de R02, lo trato como el **principal**, porque
   el daño que produce es el que el propósito del sistema busca evitar: un caso con riesgo real que no
   se revisa a tiempo. G2 tiene la tasa base más alta, así que un recall bajo en G2 afecta justamente
   a quien más lo necesita.
   *Control:* gate `max_recall_gap` y auditoría por grupo en LAB12. *Responsable:* Data Scientist.
2. **R02 — Variables proxy (`infrastructure_score`, `exposure`).** Excluir `protected_group` del modelo
   no garantiza equidad, porque estas variables difieren entre grupos y pueden reproducir la
   disparidad. Es la causa probable de R01.
   *Control:* análisis de proxies y comparación del modelo con y sin cada variable.
   *Responsable:* Data Scientist.
3. **R09 — Subgrupos interseccionales pequeños.** Con n = 8 no se puede afirmar ni negar que haya
   daño. Es un riesgo **epistémico**: si no se reconoce, una métrica inestable puede dar falsa
   seguridad.
   *Control:* reportar n, no concluir con n < 30, usar bootstrap. *Responsable:* Data Scientist.

**R07 (deriva temporal, impacto 4, residual alto)** queda empatado con R01 en puntaje. Lo mantengo en
vigilancia activa porque el split de prueba cubre pocas semanas.

**Observación de gobernanza:** los tres riesgos principales recaen en el mismo rol (Data Scientist).
Es una concentración de responsabilidad. El Product Owner debe validar las mitigaciones para que quien
construye el modelo no sea también quien lo audita.

## Incertidumbre

- MEASURE sigue **pendiente**: todavía no hay métricas por grupo del modelo entrenado
  (`rmf_summary.json`).
- Los datos son sintéticos: las conclusiones no se trasladan a poblaciones reales (DATASET_CARD).
- La escala 1-4 de probabilidad e impacto es un juicio del equipo, no una medición.

## Resumen NIST AI RMF

| Función | Estado | Evidencia |
|---|---|---|
| GOVERN | Parcial | Owner, autoridad de retiro, RACI y usos prohibidos definidos |
| MAP | Completo para LAB11 | Propósito, interesados (5) y 10 riesgos con responsable y evidencia |
| MEASURE | Pendiente | Auditoría global, por grupo e interseccional en LAB12 |
| MANAGE | Parcial | Condición de retiro, apelación y baseline FIFO documentados; falta runbook (LAB13) |

## Condición de retiro / STOP

Se pasa a **STOP** y se vuelve al baseline FIFO si: recall global < 0.68; brecha de recall o FPR
entre G1 y G2 > 0.16; se detecta un uso fuera de alcance (elegibilidad, intervención automática,
emergencia); aparecen identificadores directos; o una apelación confirmada demuestra daño atribuible
al ranking.

## Condiciones para pasar a GO

1. LAB12 cumple todos los gates con el modelo elegido.
2. El análisis de proxies (R02) está documentado y la mitigación tiene justificación.
3. Las métricas interseccionales se reportan con n e incertidumbre (R09).
4. Hay mecanismo de apelación operativo y operadores capacitados (R06, R08).
5. El Product Owner firma este registro.

## Adenda tras LAB12 (2026-10-08)

- **R01 corregido con evidencia:** la hipótesis original (recall menor en G2) era falsa. LAB12 muestra
  recall G1 0.653 frente a G2 0.791, y FPR G1 0.250 frente a G2 0.375 (logistic). El escenario y los
  afectados de R01 se actualizaron en `risk_register.csv`. Es un ejemplo de por qué el registro debe
  revisarse con datos y no quedarse en suposiciones.
- **MEASURE:** completado en `reports/lab12/AUDIT_REPORT.md`. La logística cumple los gates en la
  estimación puntual, pero los IC95 de las brechas superan 0.16.
- **Decisión actualizada:** de REVIEW a **LIMITAR**, es decir, piloto en modo sombra con revisión
  humana total y baseline de reglas como rollback. Se mantienen las condiciones para GO indicadas arriba.
