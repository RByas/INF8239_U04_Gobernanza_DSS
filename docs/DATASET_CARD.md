# Dataset Card

Synthetic territorial-risk dataset generated with a fixed educational seed. It contains no real persons, locations, rates or official Dominican Republic statistics. Intended only to practice contracts, temporal evaluation, subgroup auditing and governance. Prohibited: operational profiling or inference about real populations.

*Estructura basada en Gebru et al., Datasheets for Datasets (DOI 10.1145/3458723).*

## Motivación y composición
- **Archivo:** `data/territorial_risk_synthetic.csv`, con 640 filas y 9 columnas. Hay un caso por fila, del 2026-01-01 al 2026-12-27.
- **Target:** `target` es binario (1 = incidente registrado). La prevalencia es 0.552: 0.497 en G1 y 0.639 en G2. Por zona va de 0.516 (Norte) a 0.616 (Sur).
- **Grupos:**
  - G1 = 396 casos y G2 = 244.
  - Cuatro franjas de edad, de 148 a 179 casos cada una.
  - Cuatro zonas, de 155 a 164 casos cada una.
- **Procedencia:** generado por el docente con una semilla fija. No hay un proceso de recolección real.

## Inventario de datos y minimización
| Columna | Tipo | Rol | ¿Entra al modelo? | Justificación y minimización |
|---|---|---|---|---|
| case_id | texto | Identificador técnico (seudónimo) | No | Solo para trazabilidad; no identifica personas. |
| received_date | fecha | Orden temporal | No | Solo para el corte temporal. |
| zone | categórica | Contexto territorial | Sí | Granularidad gruesa (4 zonas); no se usan direcciones. |
| protected_group | categórica | **Sensible** | **No** | Solo para la auditoría de equidad. Lo garantiza la puerta `privacy` (`excluded_from_model`). |
| age_band | categórica | **Sensible** | Sí ⚠ | Se usan franjas en vez de la edad exacta. Su uso como predictor está en revisión (`docs/MODEL_CARD.md`). |
| previous_incidents | entero | Predictor | Sí | Historial agregado. |
| infrastructure_score | real 0–1 | Predictor | Sí | Posible *proxy* de grupo (0.417 en G2 frente a 0.575 en G1 en la prueba). |
| exposure | real 0–1 | Predictor | Sí | Posible *proxy* de grupo (0.544 frente a 0.502). |
| target | binario | Etiqueta | No | Refleja incidentes *registrados*, no daño real. |

**Prohibidas por contrato:** `name`, `document_number`, `email` y `phone`. `validate_schema` las rechaza antes de
predecir. Lo verifican `tests/test_data.py` y `tests/test_privacy.py`.

## Retención y acceso (propuesta para un uso real)
| Artefacto | Retención | Acceso | Eliminación |
|---|---|---|---|
| Datos de casos | Ciclo de revisión + 12 meses para auditoría | Data Engineer y Data Scientist, por rol | Borrado seguro programado, con registro |
| Predicciones y logs de decisión | 24 meses, para atender apelaciones e incidentes | Supervisor, ML Engineer y Legal | Se agregan de forma anónima al vencer |
| Reportes de auditoría (`reports/`) | Mientras el sistema esté activo + 5 años | Equipo y responsables | Archivo institucional |
| Modelos serializados (`models/`) | Versión vigente + 2 anteriores, para rollback | ML Engineer | Se eliminan las versiones sin uso |

Estos plazos son una propuesta académica. En un despliegue real en República Dominicana, la referencia sería la
Ley 172-13 de protección de datos personales (`docs/MARCO_NORMATIVO.md`).

## Usos
- **Previsto:** practicar contratos de datos, evaluación temporal, auditoría por subgrupo y gobernanza.
- **Fuera de alcance:** perfilado operativo, inferencia sobre poblaciones reales y decisiones sobre personas.
