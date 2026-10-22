# Marco normativo y ético · Territorial Review DSS (sintético)

> **Alcance y responsabilidad.** Este documento es una interpretación académica del estudiante y no constituye asesoría legal. El sistema trabaja con **datos sintéticos**, así que hoy no trata datos de personas reales. Las obligaciones legales se analizan para el escenario en que el sistema se desplegara con datos reales en República Dominicana. Las fuentes se consultaron en octubre de 2026 y se listan en [REFERENCIAS.md](REFERENCIAS.md).

## 1. Tres categorías distintas
| Categoría | Qué es | ¿Es exigible? | Ejemplo en este proyecto |
|---|---|---|---|
| **Obligación legal** | Norma vinculante dictada por una autoridad, con consecuencias jurídicas si se incumple. | Sí, ante tribunales u órganos de control. | No discriminar (Constitución, art. 39) y proteger los datos personales (Ley 172-13). |
| **Marco voluntario** | Estándar, guía o recomendación que una organización adopta por decisión propia. | No, salvo que se incorpore a un contrato, una política interna o una norma. | NIST AI RMF 1.0, la Recomendación de la OCDE y la ENIA 2023. |
| **Recomendación ética** | Juicio del equipo sobre lo que *debe* hacerse más allá de lo que exigen la ley y los marcos. | No. Se sostiene con argumentos y se rinden cuentas por ella. | Revisión humana de todos los casos y tolerancia de 0.16 en las brechas. |

La distinción importa porque los umbrales del proyecto (recall mínimo de 0.68 y brechas de 0.16 o menos en `configs/governance.yml`) **no son obligaciones legales**. Son decisiones éticas del equipo, inspiradas en marcos voluntarios. Ninguna ley dominicana fija un valor numérico de equidad.

## 2. Obligaciones legales (República Dominicana)
| Norma | Qué exige (resumen) | ¿Aplica hoy? | ¿Aplicaría en un despliegue real? | Cómo lo atiende el proyecto | Evidencia |
|---|---|---|---|---|---|
| **Constitución, art. 39** (derecho a la igualdad) | Igual protección y trato de las instituciones, y prohibición de la discriminación. | No: no hay personas reales. | **Sí**, si una institución pública usa el sistema para ordenar casos. | Auditoría por grupo e interseccional. La brecha de recall de G1 activa una investigación y la decisión LIMITAR. | `reports/lab12/AUDIT_REPORT.md` |
| **Constitución, art. 44** (intimidad y honor) | Respeto a la vida privada y derecho a acceder a los datos propios y a pedir su rectificación. | No. | Sí. | El esquema rechaza identificadores directos. | `src/inf8239_u04/data.py`, `tests/test_privacy.py` |
| **Constitución, art. 70** (hábeas data) | Acción judicial para conocer los datos que constan sobre una persona en registros y bancos de datos. | No. | Sí. | La apelación interna (`appeal_mechanism`) complementa este derecho, pero **no lo sustituye**. | `student_inputs/lab11_impact.yml` |
| **Ley 172-13** de protección integral de los datos personales | Protección de datos personales en archivos y registros públicos o privados: principios de licitud, calidad, finalidad y seguridad, entre otros, y derechos de acceso, rectificación, cancelación y oposición. | **No**: el dataset es sintético y no contiene personas identificables (`docs/DATASET_CARD.md`). | Sí. Haría falta una base legal para el tratamiento, limitar el uso a la finalidad declarada y proteger los datos. | Finalidad y usos prohibidos declarados, rechazo de identificadores directos y minimización de variables. | `configs/governance.yml`, `src/inf8239_u04/data.py` |
| **Ley 200-04** de libre acceso a la información pública | Las instituciones públicas deben dar acceso a la información que producen. | No. | Sí, si quien lo opera es una institución pública: la documentación del sistema podría ser solicitada. | La documentación es pública y verificable: Model Card, informe de auditoría y registro de decisión. | `docs/`, `reports/` |

**Ley específica de IA:** según las fuentes consultadas, República Dominicana **no tiene una ley vigente específica de inteligencia artificial**. La propia ENIA reconoce como pendientes la actualización de la Ley 172-13 y un código de ética para la IA. Esto debe volver a verificarse antes de cualquier despliegue real.

## 3. Marcos voluntarios
| Marco | Naturaleza | Cómo se usa en el proyecto | Evidencia |
|---|---|---|---|
| **NIST AI RMF 1.0** (NIST AI 100-1, 2023) | Marco voluntario de gestión de riesgos de IA, con las funciones GOVERN, MAP, MEASURE y MANAGE. | Mapa de controles por subcategoría, con su estado: verificado, documentado o pendiente. | `student_inputs/nist_rmf_map.csv`, `reports/lab11/rmf_summary.json` |
| **Recomendación de la OCDE sobre IA** (OECD/LEGAL/0449, 2019, revisada en 2023 y 2024) | Instrumento intergubernamental no vinculante: equidad y derechos humanos, transparencia, robustez y rendición de cuentas. | Principios de transparencia (documentación pública), rendición de cuentas (matriz RACI) y capacidad de anular o retirar el sistema (condición de retiro). | `student_inputs/raci.csv`, `student_inputs/lab11_impact.yml` |
| **Recomendación de la UNESCO sobre la ética de la IA** (2021) | Recomendación adoptada por los Estados miembros de la UNESCO; no es vinculante. | Supervisión humana, proporcionalidad y no discriminación. | `reports/lab11/DECISION_RECORD.md` |
| **ENIA · Estrategia Nacional de IA de República Dominicana** (OGTIC, 2023) | Política pública y hoja de ruta, no ley. Incluye el uso ético de la IA en el pilar de gobierno inteligente. | Contexto nacional: el sistema se presenta como apoyo a un gobierno basado en datos, con uso ético. | `docs/REFERENCIAS.md` |
| **Fairlearn** (documentación, guía de evaluación de equidad) | Guía técnica de código abierto, no una norma. | Métricas por grupo con `MetricFrame` y mitigación con `ThresholdOptimizer`. | `src/inf8239_u04/fairness.py`, `scripts/lab12_mitigation.py` |

**Estados del mapa NIST.** El mapa se valida con `validate_rmf_map` (`tests/test_nist_map.py`) y se resume en `reports/lab11/rmf_summary.json` al ejecutar `scripts/lab11_impact.py`. Cada control tiene uno de tres estados:
- `verificado`: la evidencia la generó o la comprobó código que se ejecutó, ya sea un script o una prueba.
- `documentado`: es una política escrita que todavía no se ha puesto en operación.
- `pendiente LAB13`: aún no existe.

Que un archivo de evidencia exista **no** basta para marcar un control como verificado.

## 4. Recomendaciones éticas (decisiones del equipo)
Ninguna ley ni ningún marco imponen estas decisiones; el equipo las asume y debe defenderlas:
1. **Supervisión humana total.** El sistema solo ordena la cola y nunca decide intervenciones ni elegibilidad (`prohibited_uses`).
2. **Priorizar los falsos negativos.** Perder un caso real es el daño más grave, así que el recall por grupo es la métrica principal (`lab12_decision.yml`).
3. **Tolerancias propias.** Un recall mínimo de 0.68 y brechas de 0.16 o menos. Son umbrales elegidos por el equipo, no exigencias legales, y se revisan con evidencia.
4. **Apelación sin puntuación.** Un analista distinto revisa el caso sin ver la puntuación del modelo y responde en 10 días hábiles.
5. **No usar el atributo sensible para decidir, salvo que una revisión lo autorice.** Se reserva para la auditoría. La estrategia D (Fairlearn) queda condicionada a esa revisión.
6. **Retiro hacia la alternativa FIFO** si se incumplen las tolerancias, si hay uso fuera de alcance o si se confirma un daño.
7. **No extrapolar.** Los datos sintéticos no permiten conclusiones sobre la población dominicana real.

## 5. Tensiones que requieren revisión legal y ética
- **Mitigación con el atributo sensible frente a igualdad de trato (art. 39).** La estrategia D mejora el recall de G1 (0.837), pero trata distinto según el grupo y es aleatoria. Puede defenderse como medida de igualdad material o cuestionarse como trato diferenciado. **Esto no se resuelve técnicamente:** decide el Product Owner con asesoría jurídica.
- **Minimización de datos frente a la necesidad de auditar.** Auditar la equidad exige conservar `protected_group`. En un despliegue real, conservar ese atributo necesitaría una base legal y salvaguardas según la Ley 172-13.
- **Apelación interna frente a hábeas data.** El mecanismo interno no reemplaza los derechos constitucionales de acceso y rectificación, que deben informarse a las personas afectadas.
