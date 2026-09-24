# Decisiones y estado del trabajo

Fecha de inicio del registro: 2026-09-24.
Responsable de arquitectura y decisiones académicas: Álvaro Santamaría Antón.

## Estado actual

Fase actual: preparar dataset y entorno del PC Casa, y documentar portabilidad.
**Bloqueo actual:** Windows impide importar una extensión de SciPy; la preparación
de casa está incompleta aunque la GPU y el cargador de imágenes funcionan.
La hoja de ruta detallada se acordará después, por petición de Álvaro.
No se ha diseñado la CNN, iniciado entrenamiento, elegido app ni preparado diapositivas.

### Hecho

- Leídos los seis documentos originales, incluidos figuras y diagramas.
- Revisados el repositorio `cancer-gpu` y la estructura de la plantilla propuesta.
- Localizado el clon en `D:\proyectos\cancer-gpu`, rama `master`.
- Confirmada RTX 3060 Ti, 8 GB, controlador 616.92 en PC Casa.
- Descargados exclusivamente los 38.109 PNG a `dataset/` de la raíz.
  Decodificados y comprobados: PNG en escala de grises, 256 × 256, cero fallos.
- Añadidas recetas de entorno y herramientas de diagnóstico y sincronización.
- Miniconda instalado; `cancer` usa Python 3.12.14.
- PyTorch 2.13.0+cu126 y torchvision 0.28.0+cu126 instalados.
- Prueba real de convolución y gradientes en la RTX 3060 Ti: OK.
- Verificada la resolución de las dependencias Python compartidas para Linux/Python 3.12.
- Probada la carga real PRE/EARLY/LATE con `utils_caso` y DataLoader: OK.

### En curso / pendiente de verificar

- Resolver el bloqueo de Control de aplicaciones y repetir la prueba completa
  de métricas. La alternativa conda-forge también fue bloqueada; detalle en
  [BLOQUEO_WINDOWS.md](BLOQUEO_WINDOWS.md).
- Recoger versión real de Python, torch, torchvision, HIP y prueba GPU en universidad.
- Validar versiones comunes en los dos equipos antes del primer entrenamiento.
- Una vez preparado el entorno: acordar hoja de ruta y auditoría/visualización.
- Más adelante: diseño propio, experimentos, evaluación final, app y presentación.

## Acuerdos y precisiones

| ID | Decisión o criterio | Motivo / estado |
|---|---|---|
| D01 | CNN 2D propia, desde cero, en PyTorch | Obligatorio según enunciado. Álvaro diseña la arquitectura; la asistencia explica y dibuja su diseño. Sin modelos de catálogo ni pesos preentrenados. |
| D02 | Revisar aprendizaje tras 5–10 épocas | Propuesta de Álvaro. Antes de descartar, comprobar datos, gradientes, pérdida y validación. Métrica, paciencia y criterio exactos todavía por acordar. No se afirma que toda arquitectura deba mejorar en ese plazo. |
| D03 | Decisiones y estado en este documento | Registrar fecha, motivo, evidencia, resultado y próximo paso tras cada sesión. |
| D04 | Un entorno cancer por equipo, Python 3.12.14 | Verificado en casa. El Python global no se modifica. Mismas versiones públicas compartidas, binarios GPU distintos. |
| D05 | Dataset local excluido de Git | Archivos pesados, ya ignorados. Raíz actual del repo equivale a breastdcedl/. |
| D06 | Parámetros de ejecución separados del diseño | Lote ajustable según VRAM, registrando cambios y efectos; no hay tamaños de lote elegidos aún. |
| D07 | App por URL al final; tecnología pendiente | Cargar PRE/EARLY/LATE compatibles, validar entrada, mostrar realce y predicción. Puede aceptar casos externos técnicamente compatibles, pero no imágenes arbitrarias ni garantizar generalización externa. |
| D08 | Exactamente cinco diapositivas, al final | El enunciado dice cinco; concreta la propuesta de 4–5. Después de terminar la app. |
| D09 | Modelo visible desde GitHub | Más adelante incluir código de arquitectura, diagrama legible y pesos/configuración del modelo final. Elegir almacenamiento según tamaño. |
| D10 | Separar siempre por paciente | Mantener train/test oficiales; validación interna por folds de train. Test una vez cerrado el modelo. |
| D11 | Comparar BCE normal y ponderada | Obligatorio; evaluar por paciente y justificar agregación/umbral con validación interna. |
| D12 | Aclarar incertidumbres, no inventar resultados | Índice ROCm y versión universitaria no confirmados; no dar por validada la portabilidad AMD. |

## Diferencias entre fuentes que hay que recordar

- Artículo: 2.070 pacientes originales, 1.452 con pCR. Adaptación docente:
  1.450 tras dos exclusiones, de las cuales 177 quedan en validación privada.
  El material público tiene 1.273 pacientes (1.097 train, 176 test).
- I-SPY usa índices de corte del volumen recortado; mask_start/end corresponden
  al original. En Duke coinciden. No filtrar PNG I-SPY usando esos límites.
- La guía incluye agregación por paciente; la demostración privada usa un corte
  con tres fases por paciente. Diferenciar la salida por corte de la evaluación
  agregada por paciente en el informe y en la app.
- El material recomienda un ajuste de compatibilidad para RX 6700 XT. Instalar
  PyTorch ROCm no basta para declarar la GPU operativa; probar cálculo real.
- La guía simplifica que accuracy cercana al 70,6 % implica no aprender. Se
  comprobará con matriz de confusión, AUC y sensibilidad: accuracy aislada no
  demuestra por sí misma ausencia de aprendizaje.
- **Contradicción de licencia pendiente:** guía/enunciado indican CC BY-NC 4.0;
  el `LICENSE` que ya tenía este repositorio dice CC BY 4.0 y permite uso comercial.
  Además, el PDF del artículo indica CC BY-NC-ND 4.0 para el artículo.
  No asumir que una licencia cubre todos los materiales. No se modifica LICENSE;
  aclarar la licencia de cada material antes de publicar ejemplos o redistribuir datos.

## Registro de sesiones

### 2026-09-24 — Preparación inicial en PC Casa

Se respeta la prioridad pedida: datos y entorno antes de hoja de ruta detallada.
Miniforge oficial verificado por SHA256 no pudo completar instalación: Windows
bloqueó su ejecutable interno mediante Control de aplicaciones. Se conserva la
protección y se instaló Miniconda oficial con firma digital válida como alternativa.
Se retiraron únicamente los restos de la instalación fallida de Miniforge.
SciPy instalado con pip también produjo un bloqueo de carga; NumPy y SciPy se
sustituyeron por las mismas versiones de conda-forge (2.5.3 y 1.18.1).
La prueba con conda-forge falló al cargar `_arpacklib`; Windows mantiene el bloqueo.
Se verificaron por separado la lectura de imágenes y la operación en GPU, ambas
correctas. No se ha calculado rendimiento del modelo ni evaluado test.
No se han cambiado controladores ni definido la arquitectura del trabajo.

Próximo paso inmediato: revisar con Álvaro el bloqueo de Windows y una solución
compatible con su política de seguridad; repetir métricas y sincronización completa.
Pendiente obligatorio en el laboratorio:
ejecutar diagnóstico antes de cambiar paquetes y compartir su resultado.
