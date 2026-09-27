# Protocolo experimental BreastDCEDL

Fecha: 2026-09-27. Acuerdos de Álvaro durante la fase 2.
Estado: fase 2 completada mediante acuerdos revisados con Álvaro en el chat.
No autoriza entrenamiento ni fija la arquitectura de la fase 3.
Procedencia y motivos: D01–D25 de [DECISIONES_Y_ESTADO.md](DECISIONES_Y_ESTADO.md).

## Datos y entrada

- Respetar splits y folds docentes por paciente; test reservado al final.
- Desarrollo: fold 0 para validación, folds 1–4 para entrenamiento.
- Confirmar finalistas con cinco entrenamientos desde cero, rotando validación.
- Entrada float32 (3,256,256), orden PRE/EARLY/LATE, PNG dividido entre 255.
- Sin normalización independiente por fase ni aumentos en la primera comparación.
- CNN propia diseñada por Álvaro en fase 3, sin preentrenamiento, salida de un logit.

## Comparación y entrenamiento futuro

- Comparar BCEWithLogitsLoss normal y ponderada, cambiando solo la pérdida.
- Mismos pesos iniciales, particiones, semilla 42, muestreo, preprocesado,
  optimizador, lote, presupuesto y reglas de parada para cada pareja.
- pos_weight = N0/N1 calculado por cortes del entrenamiento de cada fold.
- Máximo 50 épocas; validar cada época y revisar conjuntamente en épocas 5 y 10.
- Paciencia de 10 épocas consecutivas sin superar la mejor AUC por paciente;
  aplicar parada a partir de época 10. Empates no reinician paciencia.
- Conservar pesos de la mejor AUC; en empate, la época anterior.
- Detener una ejecución no supone descartar automáticamente su arquitectura:
  revisar datos, código, gradientes, pérdida y tasa de aprendizaje.
- Arquitectura, optimizador, tasa de aprendizaje y lote se concretarán en fase 3.

## Evaluación y selección

- Convertir logits a probabilidades y promediar todos los cortes de cada paciente.
- Métrica principal: ROC-AUC por paciente; acompañar con sensibilidad,
  especificidad, accuracy y matriz de confusión, sin ponderación adicional.
- Elegir finalista por media aritmética de AUC en cinco folds y mostrar los cinco
  resultados. Empate exacto: menos parámetros; misma arquitectura: BCE normal.
- Diferencias pequeñas no demuestran superioridad concluyente.
- Umbral inicial 0,50. Ajustar después maximizando la media de sensibilidad y
  especificidad en las predicciones de validación reunidas de los cinco folds.
  Cada paciente aporta la predicción de la red que no entrenó con ella.
- Empate de umbral: más cercano a 0,50; si persiste, mayor. Conservar resultados
  con 0,50. El ajuste y selección sobre validación no son evaluación independiente.
- Calibración por paciente: gráfica con cinco intervalos de probabilidad y sus
  recuentos, y Brier como error probabilístico; sin recalibración inicialmente.
- Intervalos del 95 %: 2.000 remuestras válidas de pacientes con reemplazo,
  modelo y umbral fijos, límites percentiles 2,5 y 97,5. Repetir remuestras sin
  ambas clases. No reentrenar ni remuestrear cortes como unidades independientes.
- Estos intervalos no incluyen toda la variabilidad de entrenamiento/selección
  ni expresan probabilidad individual de acierto.

## Modelo final y test

- Reentrenar desde cero la configuración ganadora con las 1.097 pacientes de train.
- Duración fija: mediana de las cinco épocas de mejor AUC del candidato ganador.
  Sin parada por validación; si procede, recalcular pos_weight con todo train.
- Fijar umbral obtenido con validación interna antes de test. Documentar que
  trasladarlo al modelo reentrenado puede cambiar su comportamiento.
- Evaluar el modelo cerrado en test una vez, sin reajustarlo con esos resultados.
- Diferenciar evaluación agregada por paciente de inferencia de un corte en la app.

## Registro y transporte

- Guardar último estado reanudable cada época y mejor versión por separado.
- Registrar configuración, código, partición, semilla, métricas, época y equipo;
  guardar pesos, optimizador, estados aleatorios y scheduler/escalador si se usan.
- Checkpoints fuera de Git; traslado entre equipos mediante pendrive.
- Guardar en disco local al terminar cada época y continuar automáticamente.
  Implementar una solicitud de parada al final de la época: guardar y confirmar
  antes de apagar o copiar. Reanudar en la época siguiente a la última completada;
  una interrupción a mitad de época pierde el progreso no guardado de esa época.
- Escribir el checkpoint de forma segura mediante archivo temporal y sustitución
  al completar la escritura. Copiar al pendrive una vez terminado el guardado;
  comprobar SHA-256 de origen y copia, y copiar a disco local en el equipo destino.
- Guardar también mejor métrica y contador de paciencia para conservar la regla
  de parada al reanudar. El código y la configuración deben corresponder al checkpoint.
- No garantizar identidad numérica entre NVIDIA y AMD. Verificar portabilidad
  cuando exista código de entrenamiento, según ENTORNOS.md.
