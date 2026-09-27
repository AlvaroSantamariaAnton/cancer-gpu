# Decisiones y estado del trabajo

Fecha de inicio del registro: 2026-09-24.
Responsable de arquitectura y decisiones académicas: Álvaro Santamaría Antón.

## Estado actual

Fase 1 terminada: auditoría, visualizaciones y revisión con Álvaro completadas.
Fase 1 publicada, según confirmación de Álvaro al iniciar esta sesión.
Fase 2 completada: protocolo experimental acordado, sin entrenamiento.
Documento consolidado: docs/PROTOCOLO_EXPERIMENTAL.md. Commit y push autorizados
por Álvaro para cerrar la fase; verificar publicación mediante Git.
Próximo paso: fase 3, diseño de la arquitectura propia con Álvaro en un nuevo chat.
El usuario resolvió el bloqueo de SciPy desactivando Smart App Control.
Casa actualizado y verificado con PyTorch 2.14.0+cu126; sincronización
completa de universidad pendiente de su próxima visita.
Hoja de ruta aprobada por Álvaro el 2026-09-25 en docs/HOJA_DE_RUTA.md.
Las fases 3–8 no se han iniciado; las decisiones técnicas abiertas siguen pendientes.
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

- Fase 2 completada mediante acuerdos sucesivos con Álvaro. Publicación autorizada;
  implementación y pruebas de checkpoints pendientes de las fases de código.
- En la próxima visita: instalar dependencias comunes en universidad, actualizar
  NumPy de 2.5.2 a 2.5.3 y pasar carga/métricas y diagnóstico GPU.
- Fase 1 cerrada: notebook ejecutado también por Álvaro en VS Code y salidas revisadas.
- Más adelante: diseño propio, experimentos, evaluación final, app y presentación.

## Acuerdos y precisiones

| ID | Decisión o criterio | Motivo / estado |
|---|---|---|
| D01 | CNN 2D propia, desde cero, en PyTorch | Obligatorio según enunciado. Álvaro diseña la arquitectura; la asistencia explica y dibuja su diseño. Sin modelos de catálogo ni pesos preentrenados. |
| D02 | Revisar aprendizaje en épocas 5 y 10, sin descarte automático de la arquitectura | Acordado el 2026-09-27. Revisar pérdida, ROC-AUC por paciente y errores; comprobar datos, gradientes, código y tasa de aprendizaje antes de atribuir falta de mejora a la arquitectura. Presupuesto y parada del entrenamiento acordados en D19. |
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
| D13 | Desarrollar con fold 0 como validación y folds 1–4 para entrenamiento; confirmar finalistas en cinco folds | Aceptado por Álvaro en este chat. Cada rotación se entrena desde cero. Es validación para selección; test sigue reservado. |
| D14 | ROC-AUC por paciente como métrica principal | Aceptado por Álvaro; acompañada de sensibilidad, especificidad, accuracy y matriz de confusión. |
| D15 | Media de probabilidades de todos los cortes disponibles de cada paciente | Aceptado por Álvaro; cada paciente aporta una predicción a la evaluación. |
| D16 | Umbral inicial 0,50 para BCE normal y ponderada; umbral ajustado por balanced accuracy | Aprobado el 2026-09-27: pCR si puntuación >= umbral. Elegir el umbral que maximice (sensibilidad + especificidad) / 2 por paciente usando solo validación interna. Conservar también resultados con 0,50. Fijar el umbral antes de evaluar test. Dar igual importancia a ambas clases es un criterio académico, no una equivalencia de daños clínicos ni una exigencia de métricas iguales. Reunir predicciones de validación de los cinco folds, una por paciente procedente del modelo que no entrenó con ella. En empate de criterio, elegir el umbral más cercano a 0,50 y, si persiste, el mayor. Valor numérico pendiente de los experimentos. |
| D17 | Entrada PRE/EARLY/LATE, 256 × 256, valores float32 en [0,1] al dividir PNG entre 255; sin aumentos en la primera comparación | Aprobado el 2026-09-27. Conservar la ventana compartida existente, sin normalizar cada fase por separado. Mismo preprocesado en entrenamiento, validación e inferencia. Posibles aumentos geométricos posteriores pendientes de acuerdo, alineados entre fases y solo durante entrenamiento. |
| D18 | Comparar BCE normal y ponderada cambiando solo la pérdida | Aprobado el 2026-09-27. Misma arquitectura, pesos iniciales, semillas/orden de muestreo, partición, preprocesado, optimizador, lote y presupuesto/reglas de parada; valores concretos pendientes. Entrenamientos independientes desde el mismo inicio, sin reutilizar pesos ya entrenados. pos_weight = N0/N1 por cortes del subconjunto de entrenamiento de cada fold, excluyendo validación y test. Mismas métricas por paciente sin ponderación adicional para favorecer una variante. |
| D19 | Máximo 50 épocas y paciencia de 10 por ROC-AUC de validación por paciente | Aprobado el 2026-09-27. Validar cada época; mejora significa superar estrictamente la mejor AUC previa (sin margen mínimo adicional). Contar épocas consecutivas sin mejora y aplicar la parada a partir de la época 10. Conservar pesos de la mejor época; empate conserva la anterior y no reinicia la paciencia. Misma regla para ambas pérdidas, aunque terminen en épocas diferentes. Parar una ejecución no descarta automáticamente su arquitectura. |
| D20 | Semilla inicial 42 y registro reproducible de experimentos | Aprobado el 2026-09-27. Misma semilla y pesos iniciales para comparar pérdidas en cada fold. Guardar al terminar cada época el último estado reanudable y conservar aparte la mejor versión por validación. Registrar configuración, métricas, época y equipo; incluir pesos, optimizador, estados aleatorios y scheduler/escalador si se usan, según ENTORNOS.md. Checkpoints fuera de Git; transferencia por pendrive según D25. No se garantiza identidad numérica entre NVIDIA y AMD. |
| D21 | Evaluar calibración con gráfica de calibración y puntuación Brier por paciente | Aprobado el 2026-09-27. Usar las probabilidades agregadas por paciente y sus etiquetas. Inicialmente evaluar sin ajustar ni corregir probabilidades; Brier mide error probabilístico y no exclusivamente calibración. Revisar en validación interna y describir en la evaluación final del modelo cerrado, sin reajustar tras ver test. Gráfica en cinco intervalos de probabilidad, mostrando el número de pacientes por intervalo. |
| D22 | Intervalos de confianza del 95 % mediante 2.000 remuestreos por paciente | Aprobado el 2026-09-27. Remuestrear pacientes con reemplazo y recalcular métricas sobre predicciones del modelo fijado, sin reentrenar; nunca remuestrear cortes como observaciones independientes. Describen incertidumbre muestral de las métricas, no probabilidad individual de acierto ni toda la variabilidad del entrenamiento. Mantener modelo y umbral fijos; límites percentiles 2,5 y 97,5 de 2.000 remuestras válidas. Repetir remuestras sin ambas clases. |
| D23 | Elegir finalista por mayor media aritmética de ROC-AUC por paciente de los cinco folds | Aprobado el 2026-09-27. Mostrar los cinco resultados individuales y su variabilidad. En empate exacto, preferir menos parámetros; con la misma arquitectura, preferir BCE normal. Cada candidato incluye arquitectura y configuración de entrenamiento/pérdida. No interpretar pequeñas diferencias como superioridad concluyente. Este criterio selecciona configuración; el procedimiento para obtener los pesos finales se acuerda en D24. |
| D24 | Una red final reentrenada desde cero con las 1.097 pacientes de train | Aprobado el 2026-09-27. Usar arquitectura/configuración ganadoras y duración fija igual a la mediana de las cinco épocas de mejor AUC de sus folds. Sin parada por validación en este reentrenamiento y sin usar test para elegir época. Si gana BCE ponderada, recalcular pos_weight con los cortes de todo train. Obtener el umbral de las predicciones de validación por paciente de los cinco folds y fijarlo antes de test; documentar que trasladarlo a una red reentrenada puede cambiar su comportamiento. No reajustar tras ver test. |
| D25 | Transporte de checkpoints por pendrive y parada al final de época | Aprobado el 2026-09-27. Guardado automático cada época sin detener el entrenamiento; permitir solicitar parada tras completar y guardar la época, confirmando antes de apagar. Reanudar en la siguiente época desde el último checkpoint completo. Copiar archivos terminados y verificar SHA-256; trabajar en disco local en destino. Implementación y prueba de portabilidad pendientes, no realizadas en fase 2. |

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

### 2026-09-27 — Publicación autorizada y relevo para fase 3

Álvaro solicita commit y push para cerrar fase 2 y abrirá otro chat para fase 3.
Se incluyen únicamente docs/PROTOCOLO_EXPERIMENTAL.md, docs/DECISIONES_Y_ESTADO.md
y docs/HOJA_DE_RUTA.md. Revisado el diff y comprobado git diff --check.
Esta entrada acompaña el commit autorizado; comprobar el push con Git.

Para retomar: leer AGENTS.md, estado, hoja de ruta, entornos y protocolo.
Fase 2 cerrada; fase 3 no iniciada. Álvaro debe proponer su arquitectura propia:
acompañar el razonamiento y comprobar dimensiones antes de implementarla.
No hay modelo, entrenamiento ni checkpoints; no reinstalar ni repetir auditoría.
Optimizador, tasa de aprendizaje y lote se concretarán con el diseño.
Universidad sigue pendiente de sincronización; licencia pendiente de aclarar.

### 2026-09-27 — Acuerdos parciales del protocolo

Álvaro acepta las propuestas sobre folds, ROC-AUC por paciente y media de cortes,
tras explicarlas en lenguaje sencillo. Se aclaran paciente, corte, fases y fold -1
para test. La consulta de samples.csv confirma pacientes/cortes por fold:
0: 219/2186; 1: 219/2190; 2: 220/2192; 3: 220/2192; 4: 219/2185.

Acepta umbral inicial 0,50 y revisión en épocas 5 y 10 sin descarte automático.
La revisión sirve para valorar cómo aprende su futura arquitectura; no implica
diseñarla ahora ni autoriza entrenamiento. No se interpreta esta aprobación como
elección de un criterio definitivo de umbral, máximo de épocas o paciencia.

Solo se actualiza documentación, conservando los cambios locales anteriores.
Sin entrenamiento, instalación, commit ni push. Validación: git diff --check.
Álvaro acepta después el preprocesado inicial D17 y comenzar sin aumentos de datos.
No se autoriza con ello ejecutar la comparación ni introducir aumentos después
automáticamente. Se propone abordar a continuación las condiciones comparables
entre BCE normal y ponderada; su concreción sigue pendiente.

Tras aclarar por qué ponderar no modifica etiquetas ni introduce información
de validación/test, Álvaro aprueba las condiciones de comparación D18.
La ponderación puede modificar sensibilidad, especificidad y calibración; no se
presupone superioridad. No se fijan aún valores de hiperparámetros ni semillas.

Álvaro aprueba máximo de 50 épocas y paciencia de 10 según D19, conservando el
checkpoint de mejor AUC y el anterior en caso de empate. Se mantienen las
revisiones de épocas 5 y 10. No se inicia entrenamiento.

Álvaro acepta semilla inicial 42 y organización del registro/checkpoints D20.
Solo cambios documentales locales, verificados con git diff --check; sin
entrenamiento, commit ni push. Se conservan cambios locales previos.

Álvaro aprueba elegir el umbral por máxima media de sensibilidad y especificidad
(balanced accuracy) en validación interna por paciente y conservar la referencia
0,50. No se calcula ningún umbral en esta sesión ni se evalúa test. El criterio
queda acordado; su valor y detalles operativos se cerrarán antes del test.
Actualización solo documental, comprobada con git diff --check; sin commit/push.

Álvaro acepta evaluar calibración con gráfica y puntuación Brier, inicialmente
sin corregir probabilidades (D21). No se han calculado resultados: no hay modelo
entrenado. Cambios documentales locales comprobados con git diff --check.

Álvaro acepta intervalos del 95 % con 2.000 remuestreos por paciente, sin volver
a entrenar (D22). No se han calculado intervalos ni métricas del modelo.
Solo se actualiza documentación local y se comprueba git diff --check.

Álvaro acepta selección de finalistas por AUC media en cinco folds y desempates
según D23. Sin resultados aún; no se selecciona ningún modelo ni se entrena.
Se actualiza documentación local, conservando cambios previos; git diff --check.

Álvaro aprueba el procedimiento D24: una red nueva con todo train y duración
fija según la mediana de las mejores épocas de los cinco folds. El umbral procede
de validación interna, con la limitación de transferirlo a una red reentrenada.
Se registra el acuerdo; no se ejecuta entrenamiento ni se evalúa test.

Álvaro aprueba los detalles de D16, D21 y D22: predicciones de validación reunidas, desempates del umbral, cinco intervalos de calibración e intervalos percentiles con modelo y umbral fijos. Se consolida el protocolo en docs/PROTOCOLO_EXPERIMENTAL.md. Sin entrenamiento, commit ni push; verificación documental con git diff --check.

Álvaro elige pendrive y aprueba guardado/reanudación y parada al final de época
(D25), tras explicar funcionamiento, duración y tamaños orientativos. Se cierra
fase 2 con los acuerdos revisados sucesivamente en este chat y consolidados en
PROTOCOLO_EXPERIMENTAL.md. La escritura segura y verificación de copias se
documentan como detalles de implementación; no hay código ni pruebas de reanudación.
Verificación documental: git diff --check. Sin entrenamiento, instalación, commit
ni push. Próximo paso: diseño de arquitectura propia por Álvaro en fase 3.

### 2026-09-25 — Inicio de fase 2

Álvaro confirma la fase 1 terminada y publicada y solicita acordar el protocolo,
sin iniciar entrenamiento. Leídos AGENTS.md, estado, hoja de ruta, entornos,
GUIA.md y texto del enunciado del repositorio. Git inicialmente limpio en master,
coincidente con la referencia local origin/master; no se consultó el remoto.
Equipo actual: Windows, DESKTOP-OGMPFDM; la shell no indica un entorno Conda activo.
Lectura del PDF con el runtime documental de Codex, sin ejecutar código del modelo,
instalar dependencias ni repetir auditoría o pruebas GPU.

Se abre la discusión de validación interna, métrica principal y agregación.
Las recomendaciones del asistente permanecen como propuestas hasta respuesta
de Álvaro. Pendientes también umbral, presupuesto, revisión/parada, preprocesado,
calibración, incertidumbre y registro/checkpoints. Fase 2 no cerrada.
Próximo paso: acordar estas reglas con Álvaro antes de diseñar y entrenar.
Cambios documentales locales; sin commit ni push.

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
