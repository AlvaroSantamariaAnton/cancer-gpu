# Hoja de ruta del trabajo BreastDCEDL

**Estado: orden, alcance y criterios de las fases aprobados por Álvaro el 2026-09-25.**
Fecha: 2026-09-25. La aprobación del plan no elige arquitectura o software ni
autoriza ejecutar todas las fases automáticamente.
Las fases futuras se concretarán con Álvaro antes de ejecutarlas.
Estado operativo y evidencias: [DECISIONES_Y_ESTADO.md](DECISIONES_Y_ESTADO.md).
Instrucciones para otro chat: [AGENTS.md](../AGENTS.md).

## Objetivo y procedencia

Construir una CNN 2D propia para estimar pCR a partir de PRE/EARLY/LATE anteriores
al tratamiento, evaluar correctamente y ofrecer una demostración web reproducible.
No es detección de cáncer, estimación de supervivencia ni recomendación terapéutica.

- **Requisitos docentes:** GUIA.md y documentation/caso_breastdcedl.pdf, especialmente
  secciones 6–13. El enunciado exige CNN desde cero, salida de un logit,
  BCEWithLogitsLoss normal y ponderada, partición por paciente, evaluación final,
  app por URL y exactamente cinco diapositivas.
- **Material complementario revisado:** ACLARACION_CORTES.md; presentacion_caso.pdf;
  GPUs, entornos y GitHub.pdf; artículo s41597-026-06589-6.pdf. Estos cuatro originales
  siguen fuera del repositorio. El artículo describe el dataset fuente, no es una
  receta para reemplazar el preprocesado de los PNG docentes.
- **Decisiones de Álvaro:** él diseña la arquitectura; el asistente explica y dibuja;
  revisión de candidatos tras 5–10 épocas; trabajo entre dos PC; tecnología de app
  más adelante; presentación al final; cambios y publicaciones acordados previamente.
- **Organización aprobada:** las fases y criterios siguientes. No se fija un
  número de candidatos, un resultado mínimo de AUC ni un calendario ficticio.

## Resumen de fases

| Fase | Resultado esperado | Estado |
|---|---|---|
| 0. Preparación técnica | Entorno y datos operativos | Casa verificado; universidad parcialmente verificada |
| 1. Auditoría y visualización | Entender datos, clases, cohortes y posibles sesgos | Terminada; notebook ejecutado y revisado con Álvaro |
| 2. Protocolo experimental | Reglas de entrenamiento y evaluación acordadas | Aprobada como fase, no iniciada |
| 3. Arquitectura propia | Diseño de Álvaro, implementación y diagrama | Aprobada como fase, no iniciada |
| 4. Entrenamiento y comparación | Experimentos trazables, normal frente a ponderada | Aprobada como fase, no iniciada |
| 5. Cierre del modelo y test | Modelo fijado y evaluación final por paciente | Aprobada como fase, no iniciada |
| 6. Aplicación desplegada | Inferencia coherente y URL funcional | Aprobada como fase, no iniciada |
| 7. Informe y entrega reproducible | Código, pesos, configuración y evidencias | Aprobada como fase, no iniciada |
| 8. Presentación y defensa | Cinco diapositivas y ensayo final | Última fase de preparación |

## 0. Preparación técnica

Hecho: dataset en raíz (38.109 PNG), comprobación técnica de archivos; casa con
Python 3.12.14, torch 2.14.0+cu126, torchvision 0.29.0+cu126 y pruebas de dependencias,
GPU, carga y métricas sintéticas correctas. No confundir esas métricas con resultados
predictivos. Universidad: torch 2.14.0+rocm7.14, torchvision 0.29.0+rocm7.14,
convolución y gradientes OK con HSA_OVERRIDE_GFX_VERSION=10.3.0.

Pendiente para la próxima visita: instalar dependencias comunes, actualizar NumPy
a 2.5.3 y comprobar carga y métricas en AMD según [ENTORNOS.md](ENTORNOS.md).
Los avisos MIOpen/xnack no impidieron la prueba pequeña, pero falta entrenamiento real.
Esto no bloquea avanzar en casa.

**Cierre:** diagnóstico y carga correctos en cada equipo. La portabilidad de
checkpoints se verificará cuando exista código de entrenamiento, no se da por hecha.

## 1. Auditoría y visualización de datos

- Verificar relaciones patients/samples, identificadores, etiquetas constantes,
  nulos, fases, rutas, número de cortes y ausencia de pacientes compartidas entre
  splits/folds. Reutilizar la comprobación técnica ya hecha; no repetirla sin motivo.
- Analizar clases por paciente y por corte, cohortes y folds del conjunto train.
  El test queda reservado: comprobaciones estructurales sin usar sus resultados
  o ejemplos para elegir el modelo ni transformaciones.
- Visualizar ejemplos de train: PRE, EARLY, LATE, EARLY-PRE y cortes de una paciente.
  Revisar orden de fases, rangos, alineación y diferencias entre cohortes.
- Explicar por qué 12.703 cortes no son 12.703 pacientes independientes.
  Distinguir 1.273 pacientes públicos de los 2.070 del artículo y los 177 privados.
- Respetar la aclaración I-SPY: índices PNG en volumen recortado; no filtrar por
  mask_start/end originales. Registrar diferencias de selección respecto de Duke.

**Entregable:** script o cuaderno reproducible, tablas y figuras comentadas.
Formato elegido por Álvaro: notebook de exploración con funciones reutilizables.
Disponible en notebooks/01_auditoria_datos.ipynb; resultados locales ignorados.
No publicar imágenes sin revisar atribución/licencia.
**Cierre completado (2026-09-25):** entradas, etiquetas, particiones y discrepancias
revisadas con Álvaro; no se eliminaron datos. Notebook ejecutado en VS Code.

## 2. Acordar el protocolo experimental

- Usar la partición interna por paciente de train. Decidir si desarrollar con un
  fold y confirmar finalistas en los cinco, o emplear otro alcance justificado.
  Los cinco folds completos son una opción, no una obligación inventada.
- Elegir métrica principal para seleccionar candidatos; propuesta: ROC-AUC por
  paciente, acompañada de sensibilidad, especificidad, accuracy y matriz de confusión.
- Decidir agregación de cortes y umbral con validación interna, nunca con test.
  Documentar además calibración e incertidumbre; acordar método concreto y, si
  usamos intervalos por remuestreo, hacerlo por paciente, no por corte.
- Establecer semilla, presupuesto, criterio de parada y qué significa «no mejora»
  al revisar 5–10 épocas. No basta accuracy cercana a la clase mayoritaria.
- Para comparar pérdidas, mantener condiciones comparables: arquitectura,
  partición, inicialización/semillas y presupuesto. pos_weight=N0/N1 se calcula
  solo con el subconjunto de entrenamiento de cada fold; no usar una constante
  copiada ni incorporar validación/test.
- Acordar normalización, aumentos geométricos alineados en las tres fases y su
  aplicación solo durante entrenamiento. No ImageNet, ColorJitter o ImageFolder.
- Definir registro de experimentos y checkpoints: pesos, optimizador, scheduler
  si existe, época, configuración, código, semillas y estado de precisión mixta
  si se usa. Elegir transferencia/almacenamiento antes de depender de ella.

**Entregable:** protocolo fechado con decisiones y motivos.
**Cierre:** reglas de selección y parada definidas antes de comparar candidatos.

## 3. Diseñar e implementar la CNN con Álvaro

Álvaro propone los bloques y decisiones; el asistente explica alternativas y
comprueba dimensiones, parámetros y memoria. Solo después se implementa el diseño
y se dibuja. La red de ejemplo de la presentación sirve para entender conceptos,
no se adopta como arquitectura del trabajo.

Entrada (3,256,256), orden PRE/EARLY/LATE, un logit de salida. Sin redes de catálogo
ni pesos preentrenados. Justificar inicialización, activaciones, regularización,
optimizador y tasa de aprendizaje con el diseño acordado.

Medir memoria y elegir batch para la RTX de 8 GB; dejarlo configurable para AMD.
Si usamos acumulación, registrar batch efectivo y no asumir equivalencia exacta
con cambios de lote, especialmente con BatchNorm.

**Entregable:** código propio, configuración y diagrama con formas y parámetros.
**Cierre:** Álvaro puede explicar la red; forward, pérdida, gradientes finitos y
actualización de pesos comprobados. Propuesta de diagnóstico: sobreajustar un
subconjunto pequeño de train para detectar errores antes de lanzamientos largos.

## 4. Entrenar, comparar e iterar

- Ejecutar los candidatos acordados y registrar curvas train/validación, métricas
  por paciente, hiperparámetros, GPU/entorno, VRAM máxima, batch, tiempo por época
  y tiempo total. Comparación corta CPU/GPU opcional, no necesaria para completar.
- Revisar tras 5–10 épocas conforme al protocolo. Si un candidato se descarta,
  guardar evidencia y motivo; Álvaro diseña el siguiente. Distinguir errores de
  datos/código, falta de aprendizaje y sobreajuste antes de atribuirlo al diseño.
- Comparar obligatoriamente BCE normal y ponderada y explicar el efecto en
  sensibilidad/especificidad. No descartar una variante solo por su accuracy.
- Justificar agregación, umbral, regularización y ajustes con validación interna.
  Mantener test fuera del ciclo de experimentación.
- Cuando se vuelva a universidad, probar cargar un checkpoint de casa, hacer
  inferencia y reanudar entrenamiento; comprobar también la vuelta si se usará.
  No prometer resultados idénticos bit a bit entre plataformas.

**Entregable:** tabla comparativa, curvas, checkpoints y decisiones conservadas.
**Cierre:** candidato elegido por las reglas acordadas, comparación de pérdidas
completa y limitaciones registradas. No hay una AUC objetivo garantizada.

## 5. Fijar el modelo y realizar la evaluación final

Cerrar arquitectura, pesos o procedimiento final de entrenamiento, preprocesado,
agregación y umbral antes de consultar el rendimiento en test. Si se decide
reentrenar con todo train, fijar previamente número de épocas y procedimiento;
no usar test como validación para esa ejecución.

Evaluar una sola vez el modelo cerrado sobre test, por paciente. Guardar métricas,
matriz de confusión, incertidumbre según protocolo y predicciones para análisis.
Examinar errores, calibración y posibles diferencias por cohorte sin volver a
ajustar el modelo tras ver test. No convertir pocos casos en conclusiones clínicas.

**Entregable:** pesos finales, configuración/versionado, checksum y resultados finales.
**Cierre:** el resultado puede reproducirse y queda claro qué se seleccionó con
validación y qué se midió al final con test.

## 6. Crear, probar y desplegar la aplicación

Elegir software y alojamiento con Álvaro al llegar aquí. Reutilizar exactamente
el preprocesado y la inferencia del modelo cerrado.

- Admitir tres PNG 256x256 PRE/EARLY/LATE del mismo corte, incluyendo casos nuevos
  compatibles; no presentar cualquier fotografía o MRI sin preparar como válida.
- Mostrar fases y mapa de realce; probabilidad, clase, umbral, versión/checksum,
  dispositivo, latencia, parámetros de entrenamiento y métricas internas.
- Distinguir predicción de un corte (defensa) de la evaluación agregada por paciente.
  El modo de cargar varios cortes, si se desea, se decidirá expresamente.
- Validar tamaño, formato, dimensiones, fases ausentes/duplicadas y valores finitos;
  mensajes claros para errores; no ejecutar contenido subido ni aceptar rutas del sistema.
- model.eval(), sin gradientes, inferencia repetible y coherente con el pipeline.
  Aviso educativo, incertidumbre y ausencia de validez clínica visibles.
- Desplegar por URL y probar entradas válidas e inválidas y varias peticiones
  consecutivas, sin editar código, reentrenar o reiniciar entre muestras.
  No incluir muestras ni etiquetas de validación privada.

**Entregable:** aplicación, URL e instrucciones/pruebas de uso.
**Cierre:** funciona desde otro navegador/equipo y coincide con el pipeline dentro
de tolerancias numéricas justificadas; no basta que funcione localmente.

## 7. Cerrar informe y entrega reproducible

El registro de decisiones se mantiene durante todo el proyecto; aquí se redacta
el informe final con datos, arquitectura, pérdidas, resultados, recursos, errores,
sesgos entre cohortes, correlación de cortes, calibración y límites de generalización.

Revisar README, instalación, inferencia, referencias, atribución y discrepancia de
licencias. Publicar código, configuración, diagrama y pesos finales de forma accesible
desde GitHub; acordar Git normal/LFS/release según tamaño antes de subirlos.
Dataset, secretos, entornos y validación privada permanecen excluidos.
Elegir qué tablas/figuras derivadas publicar sin subir todos los resultados locales.

**Entregable:** informe, repositorio reproducible y modelo accesible.
**Cierre:** checklist de entregables completo y prueba de cargar los pesos entregados
con su configuración. Subidas revisadas y acordadas con Álvaro.

## 8. Presentación y defensa, al final

Con modelo, informe y app terminados, preparar exactamente cinco diapositivas:

1. Problema, pCR y objetivo.
2. Datos, separación por paciente y clases.
3. Arquitectura propia con tamaños y parámetros.
4. Entrenamiento, decisiones y resultados internos.
5. App, demostración, limitaciones y conclusiones.

Ensayar cinco muestras públicas de pacientes distintas, sin adaptaciones entre
peticiones. En la defensa el profesor usará cinco muestras privadas desconocidas;
registrará probabilidad, umbral y clase antes de revelar etiquetas. Esa prueba
no es una estimación fiable del rendimiento clínico.

**Cierre de preparación:** cinco diapositivas, URL operativa y Álvaro puede explicar
las decisiones. La evaluación privada real queda para el acto de defensa.

## Discrepancias y decisiones abiertas

- GUIA.md y presentacion_caso.pdf difieren en cortes por fold: por ejemplo fold 0
  indica 2.187 frente a 2.186. Auditar metadata/samples.csv, comprobar que se usa la
  misma versión y registrar recuentos reales sin modificar folds para encajar tablas.
- Enunciado exige cinco diapositivas; la petición inicial decía 4–5. Se acuerda
  respetar las cinco del enunciado, manteniéndolas como último entregable.
- LICENSE del repositorio, licencia docente y licencia del artículo difieren;
  aclarar alcance antes de redistribuir material, sin sobrescribir licencias.
- Imágenes «aleatorias» significa casos externos compatibles con tres fases,
  formato y preprocesado. No garantiza generalización a cualquier imagen médica.
- Pendientes de acordar: folds/presupuesto, criterio de mejora y descarte,
  arquitectura, hiperparámetros, agregación/umbral, tratamiento de calibración e
  incertidumbre, almacenamiento de checkpoints/pesos y tecnología de app.

## Continuidad y publicación

Mantener fechas, estado y próximo paso en DECISIONES_Y_ESTADO.md; actualizar este
plan cuando Álvaro acuerde cambios. AGENTS.md permite que otro chat recupere reglas
y contexto. Plan aprobado y subida conjunta autorizada por Álvaro el 2026-09-25.
Fase 1 terminada el 2026-09-25. Álvaro autoriza publicar la auditoría y su
documentación. Consultar Git para comprobar la publicación. Próximo paso acordado:
fase 2, protocolo experimental, en un nuevo chat; todavía no iniciada.
