# Feria de Robótica 2026: Innovación Tecnológica con Impresión 3D

Feria de Robótica de Grupo Editorial Amazonas, sede Guayaquil, **3 de
diciembre de 2026**. Este archivo sigue el reglamento y la rúbrica de la
categoría.

## Requisitos del reglamento

| # | Requisito | Estado | Notas |
|---|---|---|---|
| 1 | **Art. 2.1:** piezas diseñadas por los estudiantes e impresas en 3D | 🟡 | Pendiente. Base mecánica de 3DRODV (CC BY 4.0), elegida con el docente asesor. Pieza propia: la caja de la electrónica y la potencia, ya diseñada (falta imprimirla y probar el ajuste). El piñón y el soporte de la pistola siguen en diseño |
| 2 | **Art. 2.1:** archivos de modelado originales (STL y CAD) | 🟡 | Parcial: el modelo editable (`.blend`), el script de Blender y los STL de la caja ya están en [`cad/fuente/caja/`](../cad/fuente/caja/). Faltan los de las demás piezas propias, si se diseñan. Los STL y el proyecto del laminador de 3DRODV ya están en `cad/stl/` y `cad/proyecto/`. Llevarlos el día de la feria (por ejemplo, en USB) |
| 3 | **Art. 2.1:** informe técnico impreso de máximo 5 páginas | 🟡 | Borrador en [`informe/`](../informe/), con el análisis de las medidas. Faltan los resultados de las pruebas, los datos de las piezas propias, el tiempo de impresión en la Ender y los datos del equipo |
| 4 | **Cap. 4:** sin cambios en el prototipo después de la homologación | ✅ | La versión que se presenta es la base (solo motor). El tope de temperatura queda documentado como mejora opcional, desactivado en el firmware. Calibrar y grabar el firmware antes de la homologación |
| 5 | **Cap. 4:** presentes toda la jornada | ✅ | Preparado por el equipo |
| 6 | **Cap. 4:** la organización puede publicar imágenes y descripciones | ✅ | El repositorio ya es público |

## Rúbrica (anexo del reglamento)

| Criterio | Peso | Qué lo respalda | Pendiente |
|---|---|---|---|
| 1. Originalidad e innovación | 20 % | Pistola de silicón como fuente de calor, firmware propio, tope de temperatura, análisis con correcciones sobre la mecánica de 3DRODV, alimentación con un cargador de laptop y un buck a 12 V, y caja propia con carrete para el cable. Sección 5 del informe | Imprimir y probar la caja. El piñón y el soporte siguen en diseño |
| 2. Aplicabilidad práctica | 20 % | Comparación de costos con filamento comercial. Sección 6 del informe | Datos reales de la prueba de la tira (metros y gramos por botella, diámetro) |
| 3. Diseño y modelado propio | 20 % | Análisis del equipo sobre los STL de 3DRODV (dientes y diámetros comprobados, tabla de tolerancias) y parámetros de impresión; caja de la electrónica diseñada por el equipo en Blender, con su script. Sección 4 del informe | Imprimir y probar la caja (archivos en `cad/fuente/caja/`). Diseñar en Blender, si hace falta, el piñón corregido (Ø 5.2 en D) y el soporte de la pistola |
| 4. Presentación | 15 % | Pocos cables, prototipo limpio, caja que oculta la electrónica | Imprimir y montar la caja (el diseño está listo). Material de apoyo (póster, muestras) |
| 5. Informe técnico y archivos | 10 % | Informe de 5 páginas como máximo, repositorio ordenado | Completar los datos pendientes e imprimir |
| 6. Exposición y sustentación | 15 % | — | Planificar con todo el equipo |

## Uso de inteligencia artificial

Se declara en el informe (sección 5), en el README (Créditos) y en
[`cad/README.md`](../cad/README.md). Las ideas, los requisitos y las decisiones
de diseño son del equipo. Un asistente de IA (Claude, de Anthropic) ayudó a
crearlas e implementarlas: análisis de los STL, firmware, documentación y el
script de Blender de la caja. Para la exposición, preparar una respuesta clara
a «¿qué hizo el equipo y qué hizo la IA?».
