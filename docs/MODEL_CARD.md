# Model Card — Territorial Review DSS (logistic)

*Estructura basada en Mitchell et al., Model Cards for Model Reporting (DOI 10.1145/3287560.3287596).*

## Intended use
Ordenar casos territoriales **sintéticos** para revisión humana. Sirve de apoyo a la decisión: el
operador decide sobre cada caso y puede reordenar o ignorar el ranking. Lo usan analistas territoriales
capacitados y su supervisor.

## Out-of-scope use
Intervención automática, decisiones de elegibilidad, declaración de emergencia (prohibidas en
`configs/governance.yml`), perfilado de poblaciones reales, uso con datos reales sin una nueva evaluación
de impacto y cualquier uso de `protected_group` como criterio de decisión.

## Data and split
`data/territorial_risk_synthetic.csv` (ver `docs/DATASET_CARD.md`). Corte temporal 75/25: train de
2026-01-01 a 2026-09-24 (480 casos) y test desde 2026-09-25 (160 casos: G1 101, G2 59).
Features: zone, age_band, previous_incidents, infrastructure_score, exposure.
Pipeline: OneHotEncoder + StandardScaler + `LogisticRegression(class_weight="balanced", max_iter=1200,
random_state=42)`, umbral 0.5. Versión: paquete `inf8239-u04-governance-dss` 0.1.0 y commit Git del
tag `u04-lab13`.

## Global and subgroup evaluation
| | Global | G1 | G2 | Brecha (IC95 bootstrap) |
|---|---|---|---|---|
| Accuracy | 0.719 | 0.703 | 0.746 | 0.043 |
| Recall | 0.717 | **0.653** | 0.791 | 0.138 [0.007, 0.330] |
| FPR | 0.279 | 0.250 | **0.375** | 0.125 [0.005, 0.397] |
| Selection rate | 0.531 | 0.446 | 0.678 | 0.232 |

Gates (`reports/lab13/deployment_decision.json`): todos se cumplen y el estado automático es **GO**.
Hay tres límites que ese estado no refleja:
1. El recall de G1 (0.653) está por debajo del umbral global de 0.68.
2. Los IC95 de las brechas superan 0.16.
3. Solo un subgrupo interseccional (G1 | 45-59, n = 35) tiene soporte ≥ 30, y en él el recall es 0.588.
Detalle en `reports/lab12/AUDIT_REPORT.md`.

## Green AI evidence
| Modelo | Recall | Entrenamiento | Tamaño | Latencia por caso |
|---|---|---|---|---|
| Logistic (elegido) | 0.717 | ≈ 0.1-0.4 s | 3.6 KB | 0.05 ms |
| Tree depth 5 | 0.717 | 0.11 s | 7.9 KB | — |
| Baseline de reglas | 0.467 | 0 s | 0 KB | — |

El árbol no aporta utilidad y empeora las brechas, así que se elige el modelo suficiente y más pequeño.
El costo es despreciable frente a los límites (500 ms y 1024 KB).

## Limitations, human oversight and appeal
- Los datos son sintéticos, el test es pequeño, `target` refleja incidentes registrados y no daño real,
  y hay posibles proxies (R02 y R10).
- Una brecha observada no prueba discriminación causal; requiere investigación.
- **Supervisión:** el operador revisa toda la cola y registra sus desacuerdos. El supervisor puede
  anular decisiones. El Institutional Owner puede detener el sistema.
- **Apelación:** solicitud de revisión humana con respuesta de un supervisor distinto en 5 días hábiles
  (`student_inputs/lab11_impact.yml`).
- **Decisión humana: LIMITAR.** Piloto en modo sombra con baseline de reglas como rollback. Anula el GO
  automático por los tres límites anteriores.

## Owner and review date
Accountable: Product Owner institucional. Mantenimiento técnico: Data Scientist y ML Engineer
(`student_inputs/raci.csv`). Última revisión: 2026-10-08. Próxima: 2026-11-08, o antes si ocurre un
incidente o se alcanza una condición de retiro.
