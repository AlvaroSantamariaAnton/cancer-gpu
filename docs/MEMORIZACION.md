# Diagnóstico de memorización de CNN v1

Ejecutado por Álvaro el 2026-09-30; el asistente no ha entrenado con este script.
Resultado: 200 pasos completos, BCE 0,711010 → 0,000715 y 8/8 aciertos finales.
La consola ya muestra 8/8 en paso 60. Esto demuestra ajuste de estos ejemplos,
no rendimiento en pacientes nuevas ni corrección de todos los componentes.

```powershell
conda activate cancer
python scripts/probar_memorizacion.py
```

Selecciona de forma reproducible ocho pacientes de train folds 1–4: cuatro por
clase y un corte por paciente. Usa siempre los mismos ocho cortes, PRE/EARLY/LATE
y PNG / 255. CNN v1 nueva, inicialización y semilla 42, Adam 0,001, BCE normal,
sin aumentos ni regularización. No carga pesos de los experimentos anteriores.

Presupuesto técnico inicial: 200 actualizaciones de un lote de ocho, configurable
con --pasos. No son 200 recorridos del train completo ni una modificación del
presupuesto experimental de 50 épocas. Sin validación, test ni selección por AUC.
Se registra antes de entrenar (paso 0) y después de cada actualización.

Buscamos una bajada clara de pérdida y que consiga aprender estos ejemplos.
Acertar ocho de ocho puede ser compatible con probabilidades poco seguras: leer
también BCE y predicciones. No hay umbral automático de éxito o descarte.
No memorizar en 200 pasos no demuestra que la arquitectura no sirva: revisaremos
la evolución, optimización y datos antes de decidir. Memorizar tampoco demuestra
generalización: se evalúan exactamente las muestras usadas para ajustar pesos.

## Archivos locales

Carpeta runs/cnn-v1-memorizacion/ ignorada por Git:

- config.json: parámetros, entorno y hashes de fuentes.
- muestras.csv: selección exacta de pacientes/cortes para reproducirla.
- metricas.csv: BCE y aciertos sobre las mismas muestras en cada paso.
- predicciones_finales.csv: etiquetas, probabilidades y clases finales.
- resumen.json: resultados inicial/final, pasos completados y memoria.
- diagnostico.pt: pesos finales solo para diagnóstico, no checkpoint reanudable.

Se rechaza una carpeta existente. Para una repetición acordada, usar otro
--nombre, por ejemplo cnn-v1-memorizacion-02. No borrar resultados anteriores.
Ctrl+C solicita acabar el paso y guardar; esperar al mensaje final. Una terminación
forzada puede dejar métricas parciales sin pesos/predicciones finales.

Comprobado sin entrenar: sintaxis, --help y selección reproducible de ocho pacientes
distintos, equilibrada y exclusivamente de folds 1–4 de train. Ejecución numérica
integral completada por el usuario con los resultados anteriores.
