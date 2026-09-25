# Decisiones y estado del trabajo

Fecha de inicio del registro: 2026-09-24.
Responsable de arquitectura y decisiones académicas: Álvaro Santamaría Antón.

## Estado actual

Fase 1 terminada: auditoría, visualizaciones y revisión con Álvaro completadas.
Próximo paso acordado: fase 2, protocolo experimental, en un nuevo chat.
El usuario resolvió el bloqueo de SciPy desactivando Smart App Control.
Casa actualizado y verificado con PyTorch 2.14.0+cu126; sincronización
completa de universidad pendiente de su próxima visita.
Hoja de ruta aprobada por Álvaro el 2026-09-25 en docs/HOJA_DE_RUTA.md.
Las fases 2–8 no se han iniciado; las decisiones técnicas abiertas siguen pendientes.
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
- Instalación inicial: PyTorch 2.13.0+cu126 y torchvision 0.28.0+cu126.
- Prueba real de convolución y gradientes en la RTX 3060 Ti: OK.
- Verificada la resolución de las dependencias Python compartidas para Linux/Python 3.12.
- Probada la carga real PRE/EARLY/LATE con `utils_caso` y DataLoader: OK.

### En curso / pendiente de verificar

- Acordar el protocolo experimental (fase 2) con Álvaro; todavía no está definido.
- En la próxima visita: instalar dependencias comunes en universidad, actualizar
  NumPy de 2.5.2 a 2.5.3 y pasar carga/métricas y diagnóstico GPU.
- Fase 1 cerrada: notebook ejecutado también por Álvaro en VS Code y salidas revisadas.
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
| D12 | Aclarar incertidumbres, no inventar resultados | ROCm 7.14 y versiones universitarias confirmados por salida del usuario; falta validación completa de datos y entrenamiento entre equipos. |

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

### 2026-09-25 — Versiones comunes acordadas

Álvaro autorizó actualizar casa a torch 2.14.0+cu126 y torchvision 0.29.0+cu126,
mantener Python 3.12.14, NumPy 2.5.3 y las bibliotecas comunes actuales, y corregir
el perfil universidad a torch 2.14.0+rocm7.14 / torchvision 0.29.0+rocm7.14.
La simulación pip no detectó conflictos. Instalación completada.
Verificación: sincronizar_entorno.py --equipo casa y comprobar_carga.py
terminaron con código 0. pip check, importaciones comunes, convolución y backward
en NVIDIA, carga PRE/EARLY/LATE, partición por paciente y AUC sintética: OK.
Informe local ignorado por Git: reports/local/entorno-casa.json.

Evidencia universitaria aportada por el usuario: Ubuntu 26.04.1 LTS,
Python 3.12.14, HIP 7.14.60850, ROCm SDK 7.14.1, RX 6700 XT;
convolución y gradientes OK con HSA_OVERRIDE_GFX_VERSION=10.3.0.
Se conservan los avisos MIOpen y xnack como limitación de esa prueba pequeña.
Las bibliotecas adicionales no estaban instaladas porque aún no se necesitaban.

Miniconda permanece en D:/proyectos/_herramientas/miniconda3 por decisión de Álvaro.
Activación normal de Conda en PowerShell confirmada por el usuario.
SciPy: usuario desactivó Smart App Control y pasó carga/métricas completas.

Los cambios de esta sesión quedan locales. No se hace commit ni push sin avisar
y acordarlo con Álvaro. La arquitectura y las decisiones se trabajan con él;
no se adelanta diseño de CNN ni hoja de ruta académica.

### 2026-09-25 — Continuidad entre chats

Álvaro pide conservar también la hoja de ruta en GitHub y permitir retomar el
proyecto desde otro chat sin repetir todo el contexto. Se crean AGENTS.md en la
raíz y docs/HOJA_DE_RUTA.md, enlazados desde README.md. AGENTS.md dirige al estado,
reglas de colaboración, entornos y requisitos. La hoja de ruta se deja explícitamente
pendiente de elaborar y acordar; no se han iniciado fases académicas nuevas.
Los originales externos no se han copiado ni se presupone que otro chat los tenga.

Estado de publicación: estos archivos y las correcciones de entorno de la sesión
anterior siguen locales, pendientes de revisar y acordar commit/push con Álvaro.
Próximo paso: acordar la hoja de ruta con los documentos docentes.

### 2026-09-25 — Borrador de hoja de ruta

A petición de Álvaro se revisaron la guía, aclaración de cortes y los cuatro PDF
originales para rellenar docs/HOJA_DE_RUTA.md. Se distinguen requisitos docentes,
decisiones previas y propuestas pendientes; se incluyen criterios de cierre,
comparación de pérdidas, evaluación final, app, informe y cinco diapositivas al final.
Se detectó discrepancia de recuentos por fold entre guía y presentación (fold 0:
2.187 frente a 2.186 cortes); se contrastará con los CSV en la auditoría.
No se han elegido arquitectura, hiperparámetros ni tecnología de app.
Próximo paso: revisar el borrador con Álvaro, acordar ajustes y solo después
revisar la subida conjunta de documentación y configuración. Sin commit ni push.

### 2026-09-25 — Aprobación de la hoja de ruta

Álvaro confirma que le parece bien la hoja de ruta. Quedan aprobados su orden,
alcance y criterios de cierre. Arquitectura, hiperparámetros, protocolo concreto,
checkpoints y tecnología de app siguen pendientes de decidir en sus fases.
Se actualizan el estado del plan y el enlace del README.
Próximo paso de publicación: revisar y acordar commit/push de configuración,
AGENTS.md, hoja de ruta y documentación. Próxima fase académica: auditoría.
No se ha iniciado la auditoría ni realizado commit o push.

### 2026-09-25 — Subida autorizada y relevo de chat

Álvaro autoriza commit y push conjuntos de los ocho archivos de configuración y
documentación modificados o creados. Esta entrada forma parte de ese commit;
comprobar el estado real de publicación con Git, no inferirlo de este registro.

Para retomar: PC Casa preparado, plan aprobado y auditoría todavía no iniciada.
Leer AGENTS.md y los documentos enlazados. El siguiente paso académico es la fase 1,
auditoría y visualización, que se abordará con Álvaro. No reinstalar el entorno ni
rediseñar el plan por abrir otro chat. Universidad queda pendiente de su visita.


### 2026-09-25 — Fase 1: auditoría y notebook reutilizable

Álvaro autoriza continuar con auditoría/visualización y elige exploración reutilizable
en notebooks. Se crean notebooks/01_auditoria_datos.ipynb, notebooks/README.md y
scripts/auditoria_datos.py. Cuaderno sin salidas para Git; copia ejecutada, once
CSV y tres figuras en reports/local/auditoria/ (ignorado). Sin commit ni push.

Entorno comprobado: Windows, RTX 3060 Ti, Python 3.12.14 de cancer. Git estaba
limpio en master, coincidente con la referencia local origin/master (sin consultar
el remoto). Leídos AGENTS, estado, hoja de ruta, entornos, GUIA, enunciado y
ACLARACION_CORTES original del Escritorio. No se releen los otros PDF originales.

Resultados de controles estructurales: identificadores y pareja paciente/corte
únicos; samples sin nulos; etiquetas binarias y constantes; coincidencia de ambos
CSV; cada paciente pertenece a un único split/fold; folds train 0–4 y test -1;
rutas presentes, únicas y coherentes con fase, paciente y corte. No se repite la
decodificación previa de 38.109 PNG, cuyo informe local conserva cero errores.
No se comprueba duplicación por contenido ni identidad entre distintos IDs.

Train: 1.097 pacientes, 10.945 cortes; clases por paciente 775/322, por corte
7.729/3.216 (pCR=0/1). Cohortes: Duke 165/44, spy1 78/26, spy2 532/252.
Folds: 2.186, 2.190, 2.192, 2.192, 2.185 cortes; confirma la cifra 2.186 del
fold 0 frente a 2.187 de la guía. 1.091 pacientes aportan diez cortes, dos cinco,
tres seis y una siete. Se registran nulos clínicos sin imputar ni excluir.

Visualización: seis ejemplos deterministas (uno por cohorte/clase) y todos los
cortes de ISPY1_1001; escala común [0,1], resta float32 EARLY-PRE en [-1,1].
Inspección visual de las tres figuras completada: títulos legibles, fases con
estructuras correspondientes y realce visible; esto no certifica registro
anatómico perfecto ni representa toda la cohorte. En los seis ejemplos la media
EARLY supera PRE; LATE baja frente a EARLY en tres. Son medias de imagen completa,
no medidas segmentadas del tumor ni una frecuencia poblacional de washout.
La afirmación del enunciado sobre PRE < EARLY se refiere a 120 pacientes;
la guía la generaliza. No se adopta como condición píxel a píxel.

Pruebas: las cinco celdas de código se ejecutaron en orden con cancer activado,
sin errores finales; figuras PNG revisadas. Invocar directamente python.exe sin
activar Conda produjo un cierre nativo al dibujar (Windows registró 0xc06d007f).
Se resolvió usando conda run -n cancer, sin instalar ni modificar paquetes,
controladores o protecciones. No es una reaparición del bloqueo histórico SciPy.
No se ha verificado interfaz Jupyter ni registrado kernel: seleccionar cancer
y arrancar el editor desde el entorno activado, según notebooks/README.md.

Próximo paso dentro de fase 1: explorar el cuaderno con Álvaro y comentar clases,
correlación de cortes, fases y diferencias entre cohortes. Cierre conjunto pendiente;
fase 2 no iniciada. No se ha entrenado, elegido arquitectura ni usado test para
análisis de clases/ejemplos o decisiones de modelado.


### 2026-09-25 — Cierre de fase 1 y publicación autorizada

Álvaro ejecutó las cinco celdas en VS Code con cancer; se leyeron sus salidas
persistidas, sin errores, con todos los controles True y tres figuras.
Se comentaron separación por paciente, desbalance, fases temporales y sesgos
entre cohortes. Álvaro confirma la comprensión y solicita cerrar la fase,
actualizar documentación y subir los cambios a GitHub para continuar en otro chat.
Fase 1 terminada; fase 2 aún no iniciada.

Para VS Code faltaba ipykernel. Álvaro instaló ipykernel 7.3.0 y sus dependencias
en cancer; se registra la dependencia directa en requirements.txt. Comprobación
posterior: pip check sin conflictos. Universidad sigue pendiente de sincronizar.
Se documenta activar Conda y seleccionar cancer antes de ejecutar el notebook.

Las salidas de la ejecución del usuario se conservan en
reports/local/auditoria/01_auditoria_usuario.ipynb. El notebook a publicar se
limpia de salidas e imágenes. Dataset y resultados locales permanecen ignorados.
Esta entrada se incluye en el commit autorizado; verificar el resultado del push
en Git, no inferirlo de esta frase.

Para el siguiente chat: leer AGENTS.md y el estado vigente. Empezar por acordar
fase 2: uso de folds, métrica principal, agregación, umbral, presupuesto/criterio
de revisión tras 5–10 épocas, preprocesado y registro de experimentos. No elegir
arquitectura por Álvaro ni iniciar entrenamiento. No repetir auditoría ni instalar
paquetes por rutina. La discrepancia de licencias continúa pendiente.
