# Entrenamiento de CNN v1: ejecución por Álvaro

## Ubicación del código

Arquitecturas en models/cnn_v1.py y models/cnn_v2.py; ejecutables en scripts/.
Los comandos desde la raíz no cambian. V2 sigue sin ejecutar. La reorganización
cambia rutas/hashes de fuentes, no pesos ni nombres de parámetros del state_dict.
Los checkpoints anteriores de v1 conservan sus pesos y metadatos originales;
pueden cargarse para inferencia con CNNV1, pero no se omite la comprobación de
fuentes para reanudar con código diferente. Sus ejecuciones ya habían terminado.

El asistente prepara código y analiza resultados; Álvaro ejecuta los entrenamientos.
Álvaro ha completado ambas ejecuciones de fold 0 por paciencia: normal 36 épocas
(mejor 26), ponderada 11 (mejor 1). Memorización ejecutada por separado:
8/8 aciertos en 200 pasos; véase [MEMORIZACION.md](MEMORIZACION.md).
Reanudación en el mismo equipo comprobada; portabilidad entre GPUs
e identidad frente a una ejecución ininterrumpida siguen sin verificar.

## Primera ejecución: revisar al terminar cinco épocas

## CNN v2: menos filtros, siguiente experimento aprobado

Diseño en ARQUITECTURA_ACTUAL.md; v1 conservada en ARQUITECTURA_V1.md.
Solo cambia anchura de la red. Adam 0,001, BCE normal, weight_decay=0, lote 32,
semilla 42 y mismas reglas de entrenamiento. Comandos por etapas, revisando
las salidas entre ellas:

```powershell
python scripts/entrenar.py --nombre cnn-v2-normal-fold0 --arquitectura v2 --perdida normal --weight-decay 0 --hasta-epoca 5
python scripts/entrenar.py --reanudar runs/cnn-v2-normal-fold0/ultimo.pt --hasta-epoca 10
python scripts/entrenar.py --reanudar runs/cnn-v2-normal-fold0/ultimo.pt
```

Al reanudar no especificar arquitectura: se recupera de config. Nueva ejecución
sin --arquitectura mantiene v1 por defecto. Cada checkpoint identifica su modelo;
no cargar pesos v1 en v2. Resultados v2 pendientes; lote 32 pendiente de prueba
real en GPU con esta variante. Sin entrenamientos iniciados por el asistente.

## Referencia histórica de comandos v1

Los comandos de esta sección describen la referencia sin penalización, ya
completada. Para el nuevo experimento aprobado, usar la sección siguiente.

## Experimento aprobado: Adam con weight_decay=0,0001

Misma CNN v1, BCE normal, fold 0, semilla 42, lote 32, tasa 0,001 y reglas de
parada. Solo cambia la penalización de Adam; no se cambia a AdamW. Se aplica
a todos los parámetros del optimizador, incluidos sesgos. Las pérdidas registradas
siguen siendo BCE, sin sumar manualmente la penalización a las métricas.
Referencia: normal sin penalización, mejor AUC 0,602520 en época 26.

Ejecutar primero hasta cinco épocas y compartir resultados:

```powershell
conda activate cancer
python scripts/entrenar.py --nombre cnn-v1-normal-wd1e4-fold0 --perdida normal --weight-decay 1e-4 --hasta-epoca 5
```

Tras revisar, continuar hasta diez:

```powershell
python scripts/entrenar.py --reanudar runs/cnn-v1-normal-wd1e4-fold0/ultimo.pt --hasta-epoca 10
```

Tras esa revisión, completar según paciencia/máximo 50:

```powershell
python scripts/entrenar.py --reanudar runs/cnn-v1-normal-wd1e4-fold0/ultimo.pt
```

No añadir --weight-decay al reanudar: se recupera del checkpoint y se rechaza
intentar sobrescribirlo. El valor por defecto para ejecuciones nuevas sigue
siendo cero. Se rechazan valores negativos o no finitos.
Los resultados van a runs/cnn-v1-normal-wd1e4-fold0/; los anteriores se conservan.
El cambio de script cambia su hash: los checkpoints antiguos mantienen la huella
anterior y no se reanudan con este código modificado. Esas dos ejecuciones ya
terminaron por paciencia; sus mejores pesos y métricas siguen siendo válidos.
La arquitectura modelo.py no cambia. No se ha ejecutado el nuevo experimento.

## Comandos de la referencia sin penalización

En PowerShell desde la raíz del proyecto:

```powershell
conda activate cancer
python scripts/entrenar.py --nombre cnn-v1-normal-fold0 --perdida normal --hasta-epoca 5
```

Utiliza CNN v1, Adam 0,001, lote 32, semilla 42, float32, sin aumentos,
dropout, BatchNorm, scheduler ni weight decay. Fold 0 valida, folds 1–4 entrenan.
Nunca evalúa test. La consola muestra progreso cada 50 lotes y métricas cada época.
Esta es una ejecución real sobre el subconjunto de entrenamiento completo,
no la prueba de memorización pequeña, disponible en un script separado.

`--hasta-epoca 5` pausa tras guardar la quinta época; no cambia el presupuesto
máximo de 50 ni descarta la red. Comparte metricas.csv para revisar las curvas.

## Continuar hasta diez épocas y después hasta el límite

Tras revisar las primeras cinco:

```powershell
python scripts/entrenar.py --reanudar runs/cnn-v1-normal-fold0/ultimo.pt --hasta-epoca 10
```

Después de la revisión de la época diez:

```powershell
python scripts/entrenar.py --reanudar runs/cnn-v1-normal-fold0/ultimo.pt
```

El máximo sigue siendo 50; desde época 10 se detiene al acumular diez épocas
consecutivas sin superar estrictamente la mejor AUC de validación por paciente.
Empates no reinician paciencia. Se mantienen los pesos de la mejor época anterior.
Un checkpoint ya terminado por paciencia o presupuesto no se prolonga.

## Comparación con BCE ponderada

Cuando proceda lanzar la segunda variante:

```powershell
python scripts/entrenar.py --nombre cnn-v1-ponderada-fold0 --perdida ponderada --hasta-epoca 5
```

Parte de cero con la misma semilla y orden de muestreo; nunca de pesos entrenados
de la variante normal. Calcula pos_weight=N0/N1 por cortes de folds 1–4.
Para continuar se usa su propio ultimo.pt. Mantener mismo lote, fold y equipo
en la comparación cuando sea posible. No comparar magnitudes absolutas de las
dos pérdidas como si fueran la misma función; analizar métricas por paciente.

## Resultados y guardado

Cada ejecución crea una carpeta nueva en runs/ (ignorada por Git). No sobrescribe
una ejecución existente. Contiene:

- config.json: configuración, entorno y SHA-256 del código y metadatos.
- metricas.csv: pérdidas por corte; AUC, sensibilidad, especificidad, accuracy,
  matriz de confusión y Brier por paciente; tiempo por época y memoria asignada.
  Probabilidades agregadas por media y umbral inicial 0,50.
- ultimo.pt: estado reanudable tras la última época completa, incluido Adam,
  generadores aleatorios, historial, contador de paciencia y copia de mejores pesos.
- mejor.pt: mejores pesos por AUC y configuración para futura inferencia.
- validacion_ultima.csv: probabilidades y etiquetas por paciente de la última época.

No hay selección de umbral, evaluación final, reentrenamiento de todo train ni
despliegue en este script. Son pasos posteriores. No usa AMP ni scheduler;
por tanto no hay escalador ni scheduler que restaurar.

## Parar y trasladar

Pulsa Ctrl+C una vez: solicita parada al terminar y guardar la época actual,
incluida su validación. Espera el mensaje de confirmación antes de cerrar.
Alternativamente, crea un archivo vacío PARAR dentro de la carpeta de ejecución;
retíralo antes de reanudar. Cerrar por la fuerza pierde la época incompleta.

El checkpoint se escribe en un temporal y se sustituye solo al terminar.
ultimo.pt es la fuente principal; los CSV son salidas auxiliares regenerables.
No ejecutes dos procesos a la vez sobre la misma carpeta.

Copia la carpeta terminada al pendrive y después al disco local de destino.
Compara hashes de origen y copia (también se imprime el de ultimo.pt al parar):

```powershell
Get-FileHash runs/cnn-v1-normal-fold0/ultimo.pt -Algorithm SHA256
```

En Ubuntu: `sha256sum runs/cnn-v1-normal-fold0/ultimo.pt`.
Debe mantenerse el mismo código y metadata/samples.csv: se verifica su hash
al reanudar. Las dependencias del destino deben estar preparadas según ENTORNOS.md.
`--device cuda` sirve para NVIDIA y ROCm; no se sustituye automáticamente por CPU.
Fold, pérdida y lote se recuperan del checkpoint. No se garantiza identidad numérica
entre plataformas; al cambiar backend/GPU se reinicia el RNG GPU y se informa.
La portabilidad real sigue sin probar. Solo cargar checkpoints propios de confianza:
el estado completo de Python/NumPy requiere deserialización con weights_only=False.
