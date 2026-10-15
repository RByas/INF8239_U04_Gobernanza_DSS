# Declaración de uso de IA

| Elemento | Detalle |
|---|---|
| **Herramienta** | Claude Code (Anthropic, modelo Claude Opus 5.5), usado como asistente en la aplicación de escritorio. |
| **Finalidad** | Leer el manual del laboratorio y el proyecto base, proponer la redacción inicial de los archivos de `student_inputs/` y del registro de decisión, y detectar errores en los scripts. |
| **Prompts relevantes** | "Ayúdame con esta tarea" (con el manual LAB11 y el Ejercicio 07 adjuntos); "indícame si falta algo". |
| **Fragmentos afectados** | `student_inputs/lab11_impact.yml`, `stakeholders.csv`, `risk_register.csv`, `lab12_decision.yml`, `reports/lab11/DECISION_RECORD.md` y la corrección de `scripts/lab11_impact.py`. |
| **Verificaciones humanas** | Contrasté cada cifra citada con los archivos generados en `reports/lab12/` y ejecuté `pytest` y los scripts de validación. Revisé que los riesgos, responsables y la decisión reflejen mi propio criterio. *(El estudiante debe confirmar y completar esta fila.)* |
| **Errores detectados** | `scripts/lab11_impact.py` del proyecto base tenía un texto partido en varias líneas que causaba `SyntaxError`. |
| **Correcciones** | Se escribió el texto con saltos de línea `\n` y se evitó sobrescribir un `DECISION_RECORD.md` ya existente. |

La IA no decidió los valores del análisis ni generó evidencia. Las métricas provienen de la ejecución de los scripts del proyecto.
