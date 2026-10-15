# Informe de auditoría de equidad · LAB12

**Sistema:** Territorial Review DSS (sintético) · **Fecha:** 2026-10-15 · **Decisión:** `student_inputs/lab12_decision.yml`

## 1. Comprensión del dataset (`scripts/describe_dataset.py`)
| Comprobación | Evidencia | Interpretación |
|---|---|---|
| Distribución de `target` | 55.2 % positivos y 44.8 % negativos. En la prueba hay 57.5 % positivos. | El desbalance es moderado. La accuracy es insuficiente porque un modelo que marque todo como positivo ya obtiene 0.575. Por eso se reportan recall, FPR y tasa de selección. |
| Tamaño por grupo | G1 = 396 y G2 = 244 en total. En la prueba: G1 = 101 y G2 = 59. | La comparación G1 frente a G2 tiene soporte limitado. En las intersecciones, solo **G1 \| 45-59 (35)** alcanza el mínimo de 30 casos. |
| Corte temporal | Entrenamiento hasta el 2026-09-24 y prueba desde el 2026-09-25 (75 % / 25 %). | Evita evaluar con información del futuro. Imita el uso real: el modelo se entrena con el pasado y se aplica a casos nuevos. |
| Variables excluidas | `case_id`, `received_date`, `protected_group` y `target`. | Quitar `protected_group` **no** elimina el sesgo. En la prueba, G2 tiene menor `infrastructure_score` (0.417 frente a 0.575) y mayor `exposure` (0.544 frente a 0.502), así que esas variables pueden funcionar como *proxies* del grupo. |

## 2. Métricas globales y por grupo (conjunto de prueba, n = 160)
| Modelo | Accuracy | Recall | Precisión | FPR | Tasa de selección | Tiempo de entrenamiento | Tamaño |
|---|---|---|---|---|---|---|---|
| Referencia trivial: marcar todo como positivo* | 0.575 | 1.000 | 0.575 | 1.000 | 1.000 | 0 s | 0 KB |
| **Logístico (baseline)** | 0.719 | 0.717 | 0.776 | 0.279 | 0.531 | ≈0.11 s | 3.6 KB |
| Árbol de decisión (`max_depth=5`) | 0.706 | 0.717 | 0.759 | 0.309 | 0.544 | ≈0.10 s | 7.9 KB |

\*Valores calculados a partir de la proporción de positivos en la prueba. Sirven solo de referencia para mostrar que la accuracy sola no basta. La alternativa operativa no predictiva (FIFO con reglas públicas) está definida en LAB11.

| Modelo | Grupo | n | Recall | FPR | Tasa de selección | Precisión |
|---|---|---|---|---|---|---|
| Logístico | G1 | 101 | **0.653** | 0.250 | 0.446 | 0.711 |
| Logístico | G2 | 59 | 0.791 | 0.375 | 0.678 | 0.850 |
| Árbol | G1 | 101 | **0.633** | 0.269 | 0.446 | 0.689 |
| Árbol | G2 | 59 | 0.814 | 0.438 | 0.712 | 0.833 |

**Brechas entre grupos frente a la tolerancia de `configs/governance.yml` (máximo 0.16):**

| Modelo | Brecha de recall | Brecha de FPR | ¿Recall mínimo de 0.68 en cada grupo? |
|---|---|---|---|
| Logístico | 0.138 ✅ | 0.125 ✅ | ❌ G1 = 0.653 |
| Árbol | 0.181 ❌ | 0.168 ❌ | ❌ G1 = 0.633 |

**Lectura:** el recall global de 0.717 cumple el mínimo de 0.68, pero **el promedio oculta una falla localizada**: el grupo G1 no lo alcanza con ningún modelo. La tasa de selección de G2 es mayor, en parte porque su proporción real de positivos también es mayor (0.729 frente a 0.485), así que esa diferencia por sí sola no indica un sesgo.

## 3. Análisis interseccional (`protected_group × age_band`)
Mínimo documentado para interpretar un subgrupo: **30 casos de prueba** (riesgo R03 de LAB11).

| Subgrupo | n | Recall (log / árbol) | FPR (log / árbol) | Estado |
|---|---|---|---|---|
| G1 \| 18-29 | 18 | 0.750 / 0.750 | 0.143 / 0.214 | ⚠️ Soporte insuficiente |
| G1 \| 30-44 | 24 | 0.563 / 0.625 | 0.125 / 0.375 | ⚠️ Soporte insuficiente |
| **G1 \| 45-59** | **35** | **0.588 / 0.647** | **0.389 / 0.278** | ✅ Interpretable |
| G1 \| 60+ | 24 | 0.833 / 0.583 | 0.250 / 0.250 | ⚠️ Soporte insuficiente |
| G2 \| 18-29 | 11 | 0.875 / 1.000 | 0.000 / 0.000 | ⚠️ Soporte insuficiente |
| G2 \| 30-44 | 14 | 0.667 / 0.833 | 0.500 / 1.000 | ⚠️ Soporte insuficiente |
| G2 \| 45-59 | 8 | 1.000 / 0.667 | 0.000 / 0.000 | ⚠️ Soporte insuficiente |
| G2 \| 60+ | 26 | 0.765 / 0.765 | 0.556 / 0.556 | ⚠️ Soporte insuficiente |

**Lectura:** el único subgrupo interpretable (G1 | 45-59) tiene el recall más bajo con el modelo logístico (0.588). Esto concentra la falla de G1 y conviene investigarlo. Los demás subgrupos **no se ocultan**, pero sus valores extremos (por ejemplo, FPR 1.000 o recall 1.000) son inestables y no se usan para decidir. Hace falta reunir más datos o calcular intervalos de confianza.

## 4. Por qué una brecha no prueba discriminación causal
- La brecha es una **observación estadística** en una muestra pequeña: 59 casos de G2 y, en las intersecciones, entre 8 y 35. Con otra partición podría cambiar de tamaño o incluso de signo.
- Los grupos tienen **proporciones reales de positivos distintas** (0.485 y 0.729) y distribuciones distintas en las variables predictoras. Parte de la diferencia puede venir de los datos y no del trato que da el modelo.
- Demostrar discriminación causal exigiría un diseño causal: contrafactuales, control de *proxies* y revisión del proceso que generó las etiquetas. Una auditoría con MetricFrame no lo ofrece.
- Por eso la brecha **activa una investigación** (revisar datos, umbral, *proxies* y consecuencias) y una decisión humana. No es una conclusión automática de injusticia ni de justicia.

## 5. Comparación de alternativas y Green AI
| Criterio | Logístico | Árbol |
|---|---|---|
| Utilidad | Igual recall (0.717), mejor accuracy y precisión, y menor FPR. | Igual recall, pero peor accuracy, precisión y FPR. |
| Equidad | Cumple las dos tolerancias de brecha. | Supera las dos tolerancias de brecha. |
| Costo | 3.6 KB y ≈0.11 s de entrenamiento. | 7.9 KB (más del doble) y ≈0.10 s. |
| Explicabilidad | Coeficientes interpretables. | Reglas legibles, pero inestables con 5 niveles. |

**Green AI:** el árbol no mejora la utilidad, empeora la equidad y ocupa más del doble de espacio. El modelo logístico es la **opción suficiente**: más complejidad no está justificada. Los tiempos de entrenamiento son despreciables en ambos casos (menos de 0.2 s en CPU), así que el costo computacional no es el factor que decide.

## 6. Decisión contextual
**LIMITAR.** Se descarta el árbol. El modelo logístico solo puede usarse como **orden de revisión con supervisión humana total**, nunca como decisión automática.

Antes de cualquier despliegue hay que cumplir tres condiciones:
1. Investigar y mitigar el recall de G1, en especial en el subgrupo 45-59. Se puede probar un ajuste de umbral, revisar los *proxies* y comparar con la alternativa FIFO.
2. Repetir la auditoría con más datos y con intervalos de confianza.
3. Obtener la aprobación del Product Owner.

**Acción humana:** el operador revisa todos los casos. Además, se revisa una muestra de los casos que el modelo no prioriza en G1 para detectar falsos negativos. Si al monitorear se supera cualquier tolerancia, se activa la condición de retiro de LAB11.
