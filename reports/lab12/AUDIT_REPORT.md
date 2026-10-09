# Informe LAB12 · Auditoría de equidad con Fairlearn

**Reproducir:**
```bash
uv run python scripts/lab12_audit.py --model logistic
uv run python scripts/lab12_audit.py --model tree
uv run python scripts/lab12_compare.py
uv run python scripts/validate_lab12_decision.py
```

## 1. Comprensión del dataset (`describe_dataset.py`)

| Comprobación | Resultado | Interpretación |
|---|---|---|
| Distribución de target | 1 = 0.552, 0 = 0.448 | El desbalance es leve. Aun así accuracy no basta, porque el daño prioritario es el falso negativo y accuracy lo mezcla con los falsos positivos. |
| Tamaño por grupo | G1 = 396, G2 = 244 (test: 101 y 59) | La comparación G1 vs G2 tiene soporte moderado. Las celdas interseccionales casi no tienen soporte. |
| Corte temporal | train hasta 2026-09-24, test desde 2026-09-25 | Evalúa como en producción, sin usar el futuro para predecir el pasado. |
| Variables excluidas | case_id, received_date, protected_group, target | Excluir el grupo no basta: `infrastructure_score` (G1 0.566 / G2 0.444) y `exposure` (0.469 / 0.559) son proxies (R02). |

## 2. Métricas globales y por grupo (umbral 0.5, test n = 160)

| Modelo | Accuracy | Recall | FPR | Recall G1 | Recall G2 | FPR G1 | FPR G2 | Brecha recall (IC95) | Brecha FPR (IC95) |
|---|---|---|---|---|---|---|---|---|---|
| Baseline reglas (no predictivo) | 0.644 | **0.467** ✗ | 0.118 | 0.490 | 0.442 | 0.135 | 0.062 | 0.048 [0.004, 0.261] | 0.072 [0.003, 0.215] |
| Logistic | 0.719 | 0.717 ✓ | 0.279 | 0.653 | 0.791 | 0.250 | 0.375 | 0.138 ✓ [0.007, 0.330] | 0.125 ✓ [0.005, 0.397] |
| Tree (max_depth 5) | 0.706 | 0.717 ✓ | 0.309 | 0.633 | 0.814 | 0.269 | 0.438 | **0.181** ✗ [0.021, 0.334] | **0.168** ✗ [0.006, 0.465] |

Fuente: `reports/lab12/model_comparison.csv`, `reports/lab12/{logistic,tree}/global_metrics.json` y
`fairness_by_group.csv`. Los IC95 salen de un bootstrap de 500 remuestreos con semilla 42.

**Lectura:**
- **El promedio oculta una falla localizada.** El recall global de 0.717 cumple el gate, pero en G1 baja
  a 0.653, por debajo de 0.68. Esto contradice la hipótesis de LAB11 de que G2 sería el grupo
  perjudicado, y por eso se actualizó R01 en el registro de riesgos.
- **Hay dos daños en direcciones opuestas.** G1 sufre más falsos negativos (riesgo real no priorizado)
  y G2 más falsos positivos (revisiones innecesarias). Coincide con la tasa base: G2 tiene 0.639 de
  positivos y el modelo lo selecciona más (selection rate 0.678 frente a 0.446).
- **La incertidumbre es grande.** Con 160 casos, el límite superior del IC95 de ambas brechas supera
  0.16. La logística cumple el gate solo en la estimación puntual.

## 3. Interseccional (protected_group × age_band)

Mínimo documentado: `min_group_size: 30` en `configs/governance.yml`.
Solo **G1 | 45-59 (n = 35)** tiene soporte suficiente. Los otros 7 subgrupos (n = 8 a 26) aparecen en
`reports/lab12/support_warnings.json` y **no se interpretan**. Se reportan, no se ocultan.

En G1 | 45-59 (logistic) el recall es 0.588 y la FPR 0.389. Es el único subgrupo con soporte y rinde
peor que el global en ambas métricas. Hay que investigarlo y no tomarlo como conclusión: una brecha
observada **no prueba discriminación causal**. Puede venir de la etiqueta (R10), de proxies (R02), del
umbral o del azar en una muestra pequeña. Para separar esas causas se necesitan más datos, análisis por
variable y revisión del proceso que genera `target`.

## 4. Green AI: utilidad, brechas y costo

| Modelo | Recall | Entrenamiento | Tamaño | Gates de equidad |
|---|---|---|---|---|
| Logistic | 0.717 | 0.39 s | 3.6 KB | Cumple |
| Tree | 0.717 | 0.11 s | 7.9 KB | Falla ambos |

El árbol **no mejora la utilidad**, empeora ambas brechas y ocupa más del doble. Entrena más rápido,
pero la diferencia (0.28 s) no compensa el resto. Se prefiere la **opción suficiente**: la regresión
logística, que además es más interpretable por sus coeficientes. El baseline de reglas tiene las brechas
más pequeñas, pero pierde 25 puntos de recall. Es un compromiso, no una victoria: sirve como respaldo
(rollback), no como reemplazo.

## 5. Decisión contextual

Ver `student_inputs/lab12_decision.yml`. Se elige la regresión logística con decisión **LIMITAR**:
piloto en modo sombra con revisión humana de toda la cola, sin GO hasta reducir la incertidumbre.
Durante el piloto se vigilan el recall de G1 y la FPR de G2.

**Acción humana:** el Product Owner revisa este informe y firma la decisión. El Data Scientist
investiga G1 | 45-59 y los proxies (R02) antes de la siguiente revisión.
