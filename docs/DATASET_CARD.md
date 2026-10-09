# Dataset Card

Synthetic territorial-risk dataset generated with a fixed educational seed. It contains no real persons, locations, rates or official Dominican Republic statistics. Intended only to practice contracts, temporal evaluation, subgroup auditing and governance. Prohibited: operational profiling or inference about real populations.

*Estructura basada en Gebru et al., Datasheets for Datasets (DOI 10.1145/3458723).*

## Motivación y composición

- **Archivo:** `data/territorial_risk_synthetic.csv`, con 640 filas y 9 columnas. Un caso por fila, del
  2026-01-01 al 2026-12-27.
- **Target:** `target` binario (1 = incidente registrado). Prevalencia 0.552. Por grupo: G1 0.497 y
  G2 0.639. Por zona, entre 0.516 (Norte) y 0.616 (Sur).
- **Grupos:** G1 = 396 y G2 = 244. Cuatro franjas de edad y cuatro zonas balanceadas (155 a 164 casos).
- **Procedencia:** generado con semilla fija por el docente. No hay proceso de recolección real.

## Inventario de datos y minimización

| Columna | Tipo | Rol | ¿Entra al modelo? | Justificación / minimización |
|---|---|---|---|---|
| case_id | texto | Identificador técnico (seudónimo) | No | Solo trazabilidad. No identifica personas. |
| received_date | fecha | Orden temporal | No | Solo para el corte temporal. |
| zone | categórica | Contexto territorial | Sí | Granularidad gruesa (4 zonas). No se usan direcciones. |
| protected_group | categórica | **Sensible** | **No** | Solo auditoría de equidad. |
| age_band | categórica | **Sensible** | Sí ⚠ | Se agrupa en franjas en vez de edad exacta. Su uso como predictor está en revisión (R03). |
| previous_incidents | entero | Predictor | Sí | Historial agregado. |
| infrastructure_score | real 0-1 | Predictor | Sí | Posible proxy de grupo (R02). |
| exposure | real 0-1 | Predictor | Sí | Posible proxy de grupo (R02). |
| target | binario | Etiqueta | No | Refleja incidentes *registrados*, no daño real (R10). |

**Prohibidas por contrato:** `name`, `document_number`, `email` y `phone`. `validate_schema` las
rechaza antes de predecir, y se verifica en `tests/test_data.py` y `tests/test_privacy.py`.

## Retención y acceso (propuesta para un uso real)

| Artefacto | Retención | Acceso | Eliminación |
|---|---|---|---|
| Datos de casos | Durante el ciclo de revisión + 12 meses para auditoría | Data Engineer y Data Scientist, por rol | Borrado seguro programado y registro de borrado |
| Predicciones y logs de decisión | 24 meses (para atender apelaciones e incidentes) | Supervisor, ML Engineer y Legal | Agregación anónima al vencer |
| Reportes de auditoría (reports/) | Mientras el sistema esté activo + 5 años | Equipo y responsables | Archivo institucional |
| Modelos serializados (models/) | Versión vigente + 2 anteriores (para rollback) | ML Engineer | Se eliminan las versiones sin uso |

Estos plazos son una propuesta académica: la obligación legal concreta depende de la jurisdicción y no
se evaluó aquí. En República Dominicana el marco de referencia sería la Ley 172-13 de protección de
datos personales.

## Usos

- **Previsto:** practicar contratos de datos, evaluación temporal, auditoría por subgrupo y gobernanza.
- **Fuera de alcance:** perfilado operativo, inferencia sobre poblaciones reales y decisiones sobre personas.
