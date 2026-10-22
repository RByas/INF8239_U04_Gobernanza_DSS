# Model Card — Territorial Review DSS (regresión logística)

*Estructura basada en Mitchell et al., Model Cards for Model Reporting (DOI 10.1145/3287560.3287596).*

## Intended use
Ordenar casos territoriales **sintéticos** para que un analista humano decida cuáles revisar primero. El sistema
solo aporta una puntuación y su explicación. El operador decide sobre cada caso y puede reordenar o ignorar el
ranking. Lo usan operadores técnicos capacitados y su supervisor (`student_inputs/lab11_impact.yml`).

## Out-of-scope use
Quedan fuera de alcance:
- Intervención automática, decisiones de elegibilidad y declaración de emergencias (prohibidas en `configs/governance.yml`).
- Perfilado de personas o poblaciones reales.
- Uso con datos reales sin una nueva evaluación de impacto.
- Cualquier uso de `protected_group` como criterio de decisión.

## Data and split
- **Datos:** `data/territorial_risk_synthetic.csv` (ver `docs/DATASET_CARD.md`).
- **Corte temporal 75/25:** el entrenamiento cubre del 2026-01-01 al 2026-09-24 (480 casos). La prueba empieza el 2026-09-25 (160 casos: 101 de G1 y 59 de G2).
- **Variables:** `zone`, `age_band`, `previous_incidents`, `infrastructure_score` y `exposure`. `protected_group` queda fuera del modelo; lo verifica la puerta `privacy`.
- **Pipeline:** OneHotEncoder + StandardScaler + `LogisticRegression(class_weight="balanced", max_iter=1200, random_state=42)`, con umbral 0.5.
- **Versión:** paquete `inf8239-u04-governance-dss` 0.1.0. El commit Git y el hash de la política se registran en `reports/lab13/deployment_decision.json` (`trace`).

## Global and subgroup evaluation
| Métrica | Global | G1 (n = 101) | G2 (n = 59) | Brecha (IC 95 % bootstrap) |
|---|---|---|---|---|
| Accuracy | 0.719 | 0.703 | 0.746 | 0.043 |
| Recall | 0.717 | **0.653** | 0.791 | 0.138 [0.010, 0.318] |
| FPR | 0.279 | 0.250 | **0.375** | 0.125 [0.006, 0.398] |
| Tasa de selección | 0.531 | 0.446 | 0.678 | 0.232 |

**Puertas (`reports/lab13/deployment_decision.json`): estado `REVIEW`.** Falla `group_recall`, porque el recall de G1 (0.653) queda bajo el mínimo por grupo de 0.68. Las demás puertas se cumplen: recall global, brechas, latencia, tamaño y privacidad.

La evaluación tiene además dos límites:
- Los intervalos de confianza de las brechas superan 0.16. Por eso, cumplir la tolerancia en la estimación puntual no prueba equidad.
- Solo un subgrupo interseccional (G1 | 45-59, n = 35) tiene soporte ≥ 30, y en él el recall es 0.588.

El detalle está en `reports/lab12/AUDIT_REPORT.md`.

## Green AI evidence
| Modelo | Recall | Entrenamiento | Tamaño | Latencia por caso | Puertas |
|---|---|---|---|---|---|
| Logístico (elegido) | 0.717 | 0.10–0.35 s | 3.6 KB | ≈ 0.05 ms | REVIEW (`group_recall`) |
| Árbol de profundidad 5 | 0.717 | 0.09–0.20 s | 7.9 KB | — | REVIEW (`recall_gap`, `fpr_gap` y `group_recall`) |

El árbol no aporta utilidad y empeora las brechas, así que se elige el modelo suficiente y más pequeño. El costo
es despreciable frente a los límites de 500 ms y 1024 KB.

## Limitations, human oversight and appeal
- **Datos y prueba:** los datos son sintéticos y la prueba es pequeña (160 casos; G2 tiene solo 16 negativos). `target` refleja incidentes *registrados*, no daño real.
- **Posibles *proxies* de grupo:** `infrastructure_score` y `exposure` difieren por grupo. Una brecha observada no prueba discriminación causal, pero exige investigarla.
- **Deriva temporal (R07):** en validación (agosto–septiembre), el recall de G1 era 0.778, y en la prueba baja a 0.653. Por eso un umbral fijo elegido con el pasado no protege a G1 (`reports/lab12/AUDIT_REPORT.md`, sección 6).
- **`age_band`:** figura como atributo sensible en la política y aun así se usa como predictor. Se audita por subgrupo, y su uso queda en revisión del Product Owner.
- **Supervisión:** el operador revisa toda la cola y registra sus desacuerdos, el supervisor puede anular cualquier orden y el Institutional Owner puede detener el sistema (`student_inputs/raci.csv`).
- **Apelación:** cualquier persona puede pedir que un analista distinto revise su caso sin ver la puntuación. Recibe respuesta escrita en 10 días hábiles.
- **Decisión humana: LIMITAR.** El modelo solo ordena la cola, con revisión humana total, y la puerta REVIEW lo confirma. Antes de cualquier despliegue, el Product Owner elige una mitigación (`reports/lab12/mitigation/threshold_strategies.csv`):
  - **B2:** umbral global de 0.30, sin usar el grupo. Lleva el recall de G1 a 0.939, con un 45 % más de carga de revisión.
  - **D:** la paridad de recall de Fairlearn. Usa el grupo, es aleatoria y necesita revisión legal (`docs/MARCO_NORMATIVO.md`).

  Si ninguna es admisible, se mantiene la alternativa FIFO.

## Owner and review date
- **Accountable:** Product Owner institucional.
- **Mantenimiento técnico:** Data Scientist y ML Engineer (`student_inputs/raci.csv`).
- **Última revisión:** 2026-10-22.
- **Próxima revisión:** 2026-11-22, o antes si hay un incidente o se alcanza una condición de retiro.
