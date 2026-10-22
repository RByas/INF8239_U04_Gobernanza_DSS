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
| **Logístico (baseline)** | 0.719 | 0.717 | 0.776 | 0.279 | 0.531 | 0.10–0.35 s† | 3.6 KB |
| Árbol de decisión (`max_depth=5`) | 0.706 | 0.717 | 0.759 | 0.309 | 0.544 | 0.09–0.20 s† | 7.9 KB |

\*Valores calculados a partir de la proporción de positivos en la prueba. Sirven solo de referencia para mostrar que la accuracy sola no basta. La alternativa operativa no predictiva (FIFO con reglas públicas) está definida en LAB11.

†Rango observado en ocho ejecuciones de `lab12_audit.py` (mediana ≈0.16 s en el logístico y ≈0.15 s en el árbol). El tiempo de reloj varía según la carga del equipo, por eso `training_seconds` cambia en `global_metrics.json` cada vez que se ejecuta la auditoría. Con estos valores no se puede afirmar que un modelo entrene más rápido que el otro. Las métricas y el tamaño no cambian, porque el corte temporal y la semilla son fijos.

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

**Incertidumbre de las brechas (`scripts/lab12_bootstrap.py`).** Intervalos de confianza del 95 % por bootstrap de percentiles: 2 000 remuestreos del conjunto de prueba, estratificados por grupo y con semilla 42. Fuente: `reports/lab12/<modelo>/bootstrap_ci.csv`.

| Modelo | Métrica | Estimación | IC 95 % | Probabilidad bootstrap de incumplir |
|---|---|---|---|---|
| Logístico | Recall G1 | 0.653 | 0.519 – 0.786 | 65 % de quedar bajo 0.68 |
| Logístico | Recall G2 | 0.791 | 0.659 – 0.907 | 4 % de quedar bajo 0.68 |
| Logístico | Brecha de recall | 0.138 | 0.010 – 0.318 | 42 % de superar 0.16 |
| Logístico | Brecha de FPR | 0.125 | 0.006 – 0.398 | 42 % de superar 0.16 |
| Árbol | Recall G1 | 0.633 | 0.500 – 0.765 | 74 % de quedar bajo 0.68 |
| Árbol | Brecha de recall | 0.181 | 0.018 – 0.357 | 61 % de superar 0.16 |
| Árbol | Brecha de FPR | 0.168 | 0.008 – 0.438 | 52 % de superar 0.16 |

**Lectura:** los intervalos son amplios. Que el modelo logístico "cumpla" las tolerancias de brecha depende de la estimación puntual: en el 42 % de los remuestreos cada brecha supera 0.16. Además, los intervalos de ambos modelos se solapan, así que la muestra no permite afirmar que el árbol sea peor en equidad. La brecha de FPR es la más incierta, porque G2 solo tiene 16 negativos en la prueba. Un intervalo de Wilson, calculado aparte para cada grupo, da rangos parecidos a los del bootstrap, lo que confirma su amplitud. La falla de G1 es la señal más consistente: su recall queda bajo 0.68 en la mayoría de los remuestreos con los dos modelos. Esto refuerza la decisión LIMITAR en lugar de un GO.

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

**Lectura:** el único subgrupo interpretable (G1 | 45-59) tiene el recall más bajo con el modelo logístico (0.588). Esto concentra la falla de G1 y conviene investigarlo. Los demás subgrupos **no se ocultan**, pero sus valores extremos (por ejemplo, FPR 1.000 o recall 1.000) son inestables y no se usan para decidir. Con menos de 30 casos, un intervalo bootstrap tampoco sería fiable, así que para estos subgrupos hace falta reunir más datos.

## 4. Por qué una brecha no prueba discriminación causal
- La brecha es una **observación estadística** en una muestra pequeña: 59 casos de G2 y, en las intersecciones, entre 8 y 35. Con otra partición podría cambiar de tamaño o incluso de signo.
- Los grupos tienen **proporciones reales de positivos distintas** (0.485 y 0.729) y distribuciones distintas en las variables predictoras. Parte de la diferencia puede venir de los datos y no del trato que da el modelo.
- Demostrar discriminación causal exigiría un diseño causal: contrafactuales, control de *proxies* y revisión del proceso que generó las etiquetas. Una auditoría con MetricFrame no lo ofrece.
- Por eso la brecha **activa una investigación** (revisar datos, umbral, *proxies* y consecuencias) y una decisión humana. No es una conclusión automática de injusticia ni de justicia.

## 5. Comparación de alternativas y Green AI
| Criterio | Logístico | Árbol |
|---|---|---|
| Utilidad | Igual recall (0.717), mejor accuracy y precisión, y menor FPR. | Igual recall, pero peor accuracy, precisión y FPR. |
| Equidad | Cumple las dos tolerancias de brecha en la estimación puntual (con un 42 % de probabilidad bootstrap de superar cada una). | Supera las dos tolerancias de brecha en la estimación puntual. |
| Costo | 3.6 KB y 0.10–0.35 s de entrenamiento. | 7.9 KB (más del doble) y 0.09–0.20 s. |
| Explicabilidad | Coeficientes interpretables. | Reglas legibles, pero inestables con 5 niveles. |

**Green AI:** el árbol no mejora la utilidad, tiene brechas mayores en la estimación puntual (aunque los intervalos se solapan) y ocupa más del doble de espacio. El modelo logístico es la **opción suficiente**: más complejidad no está justificada. Los tiempos de entrenamiento son despreciables en ambos casos (menos de 0.4 s en CPU en todas las ejecuciones), así que el costo computacional no es el factor que decide.

## 6. Mitigación por umbral y trade-offs (`scripts/lab12_mitigation.py`)
**Diseño.** Se mantiene el modelo logístico y solo se cambia el umbral de decisión. Para no usar la prueba al elegir, los umbrales se fijan en una **validación temporal**: el modelo se entrena con los primeros 360 casos del entrenamiento y los umbrales se eligen con los 120 siguientes. Después, la regla se aplica al modelo entrenado con todo el entrenamiento y se evalúa en la prueba (n = 160). La probabilidad de incumplir viene de 2 000 remuestreos bootstrap con semilla 42. Fuente: `reports/lab12/mitigation/threshold_strategies.csv`.

| Estrategia | ¿Usa el grupo al decidir? | Recall G1 | Recall G2 | Brecha recall | Brecha FPR | Recall G1 \| 45-59 | FPR global | Precisión | Revisiones por cada 100 casos | Prob. de que G1 quede bajo 0.68 |
|---|---|---|---|---|---|---|---|---|---|---|
| A. Umbral base 0.50 | No | 0.653 | 0.791 | 0.138 | 0.125 | 0.588 | 0.279 | 0.776 | 53.1 | 65 % |
| B. Umbral global 0.63 (el más alto que da recall ≥ 0.68 en validación) | No | 0.612 | 0.744 | 0.132 | 0.154 | 0.588 | 0.132 | 0.873 | 44.4 | 83 % |
| B2. Umbral global 0.30 (igual que B, pero exige 0.68 + margen de 0.133) | No | **0.939** | 0.953 | **0.015** | **0.043** | **0.941** | 0.529 | 0.707 | **76.9** | 0 % |
| C. Umbral por grupo (G1 0.63, G2 0.69) | **Sí** | 0.612 | 0.674 | 0.062 | 0.154 | 0.588 | 0.132 | 0.868 | 42.5 | 83 % |
| D. Fairlearn `ThresholdOptimizer` con paridad de recall | **Sí, y es aleatoria** | **0.837** | 0.721 | 0.116 | **0.014** | 0.882 | 0.324 | 0.766 | 58.8 | 1 % |

El margen de B2 es la semiamplitud del intervalo bootstrap del recall de G1 calculado en la sección 2. Se fijó antes de mirar la prueba.

**Lectura de los trade-offs:**
- **Un umbral elegido con el pasado no corrige la falla (B y C).** En la validación (agosto–septiembre), G1 tenía un recall de 0.778 con el umbral de 0.50, así que la regla subió el umbral para generar menos alertas. En la prueba, la falla de G1 aparece **después** del periodo de validación, y B y C la empeoran (0.612). Es evidencia de **deriva temporal** (riesgo R07 de LAB11): un ajuste estático no protege a G1 si los datos cambian.
- **Un margen de seguridad sí la corrige, pero con un costo alto (B2).** El recall de G1 sube a 0.939, también en el subgrupo 45-59 (0.941), y las dos brechas quedan muy por debajo de 0.16. El costo: el equipo revisa 76.9 de cada 100 casos en lugar de 53.1 (**+45 % de carga**), y la mitad de los negativos recibe una alerta (FPR 0.529). Revisar casi tres de cada cuatro casos se acerca a revisarlo todo, así que el modelo aporta poco frente a la alternativa FIFO de LAB11. La decisión depende de la capacidad real de revisión.
- **La paridad de Fairlearn (D) es el mejor equilibrio numérico.** El recall de G1 llega a 0.837, la brecha de FPR casi desaparece (0.014) y la carga sube solo de 53.1 a 58.8 revisiones por cada 100 casos. Pero tiene **dos objeciones de fondo**:
  1. Usa `protected_group` en el momento de decidir. Eso contradice el diseño del proyecto, que reserva el atributo sensible para la auditoría, y puede considerarse trato diferenciado.
  2. Es **aleatoria**: dos casos idénticos pueden recibir resultados distintos, lo que es difícil de explicar y de defender ante una apelación.

  Además, sus resultados en la prueba cambian de signo respecto a A: ahora G1 supera a G2 en recall (0.837 frente a 0.721).
- **Cada mejora del recall se paga con más falsos positivos o más carga.** Ninguna estrategia mejora todo a la vez.

**Limitaciones del experimento:** la validación tiene solo 36 positivos de G1, la regla elegida con el modelo parcial se aplica al modelo final, y todo se mide sobre los mismos 160 casos de prueba. Los resultados orientan la decisión, pero no la cierran.

## 7. Decisión contextual
**LIMITAR.** Se descarta el árbol. El modelo logístico solo puede usarse como **orden de revisión con supervisión humana total**, nunca como decisión automática. La mitigación de la sección 6 muestra que la falla de G1 se puede corregir, pero cada opción tiene un costo que no le corresponde decidir al equipo técnico.

Antes de cualquier despliegue hay que cumplir tres condiciones:
1. Elegir una mitigación con evidencia. El Product Owner decide entre B2 (sin usar el grupo, con +45 % de carga) y D (con menos carga, pero usando el grupo y con decisiones aleatorias). D requiere además una revisión legal y ética previa (ver la sección 5 de [`docs/MARCO_NORMATIVO.md`](../../docs/MARCO_NORMATIVO.md)). Si la capacidad de revisión no alcanza para B2 y D no es admisible, se mantiene la alternativa FIFO.
2. Repetir la auditoría con más datos hasta que los intervalos de confianza de las brechas queden dentro de la tolerancia de 0.16 (hoy llegan hasta 0.32 en recall y 0.40 en FPR). Como la falla de G1 aparece por deriva temporal, el umbral se debe recalibrar y volver a auditar periódicamente (riesgo R07).
3. Obtener la aprobación del Product Owner.

**Acción humana:** el operador revisa todos los casos. Además, se revisa una muestra de los casos que el modelo no prioriza en G1 para detectar falsos negativos. Si al monitorear se supera cualquier tolerancia, se activa la condición de retiro de LAB11.
