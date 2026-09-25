# Instrucciones para asistentes del proyecto cancer-gpu

## Al comenzar un chat

Este es un trabajo académico individual de Álvaro Santamaría Antón sobre
predicción de pCR con BreastDCEDL. Responde en español y acompaña su aprendizaje.
No dependas del historial de otro chat: recupera el contexto desde estos archivos.

1. Lee `docs/DECISIONES_Y_ESTADO.md`: estado vigente, acuerdos, pruebas y pendientes.
2. Lee `docs/HOJA_DE_RUTA.md`: planificación; distingue propuestas de fases aprobadas.
3. Lee `docs/ENTORNOS.md` antes de instalar, sincronizar o ejecutar código.
4. Consulta `GUIA.md` y `documentation/caso_breastdcedl.pdf` para requisitos docentes.
5. Comprueba `git status` y el equipo/entorno actual antes de modificar nada.
   Conserva cambios locales existentes. No asumas que este chat está en PC Casa.

La sección de estado actual prevalece sobre entradas históricas del registro.
Si las evidencias actuales contradicen el registro, explícalo y actualízalo dentro
del trabajo autorizado; no repitas como vigente un bloqueo ya resuelto.

## Forma de trabajar acordada con Álvaro

- Explica qué propones y por qué. No tomes decisiones del proyecto por tu cuenta,
  no adelantes fases ni interpretes una pregunta como autorización para instalar.
- Ejecuta el trabajo concreto que Álvaro ya haya autorizado, sin pedir de nuevo
  permiso para cada paso de esa misma tarea. Consulta cuando cambie el alcance.
- Antes de hacer commit o push, muestra qué cambios incluirías y acuerda la subida
  con Álvaro. Una autorización para editar localmente no autoriza publicar.
- Sé objetivo: corrige sugerencias incorrectas con motivos claros. Señala dudas,
  contradicciones documentales y límites de las pruebas, sin inventar resultados.
- Distingue requisitos de los documentos, decisiones del usuario y propuestas
  del asistente. No conviertas una propuesta en un acuerdo por escribirla aquí.

## Reglas del trabajo

- CNN 2D propia, entrenada desde cero: Álvaro diseña la arquitectura. Ayuda a
  razonar y dibuja la arquitectura cuando él la haya definido. No sustituyas su
  diseño por una red de catálogo ni uses pesos preentrenados.
- Álvaro quiere revisar el aprendizaje tras 5–10 épocas. El criterio concreto de
  descarte sigue pendiente de acordar; no inventes un umbral o paciencia.
- Las fases PRE/EARLY/LATE son canales temporales, no RGB. Evita introducir
  transformaciones de color o normalización ImageNet sin justificación y acuerdo.
- Divide por paciente y respeta las particiones docentes. No uses test para elegir
  arquitectura, hiperparámetros, agregación ni umbral; evaluación final tras cerrar
  esas decisiones. Comparar BCE normal y ponderada según el enunciado.
- No refiltres cortes PNG I-SPY usando mask_start/end del volumen original.
  Consulta la aclaración registrada en DECISIONES_Y_ESTADO.md.
- App accesible mediante enlace al final, con casos externos compatibles con la
  entrada del modelo. Tecnología pendiente de elegir con Álvaro en esa fase.
- Modelo y diagrama accesibles desde GitHub; almacenamiento de pesos por acordar.
  Presentación al final de todo, incluida la app; véase el requisito de diapositivas
  y su procedencia en el registro. No preparar entregables finales antes de tiempo.

## Entornos y verificaciones

Un entorno Conda `cancer` por ordenador. Versiones y comandos vigentes en
`environment.yml`, `requirements.txt`, `requirements/torch-*.txt` y ENTORNOS.md.
No copies un entorno binario Windows a Linux ni paquetes CUDA al equipo AMD.
`git pull` no instala dependencias. No sincronices o reinstales por rutina al abrir
un chat; primero consulta el estado y el alcance solicitado.

Casa: Windows / RTX 3060 Ti 8 GB. Universidad: Ubuntu / RX 6700 XT 12 GB.
El batch será configurable y se decidirá con la arquitectura; no hay uno elegido.
No prometas reanudación bit a bit entre GPUs. Checkpoints y transporte pendientes.

Para comprobaciones autorizadas dentro de cancer, desde la raíz:

```text
python -m pip check
python scripts/diagnostico_entorno.py --equipo casa --probar-gpu
python scripts/comprobar_carga.py
```

Usa `--equipo universidad` en el diagnóstico AMD. Son comprobaciones de entorno,
no entrenamiento ni métricas del modelo. `scripts/sincronizar_entorno.py` instala
paquetes: no lo trates como diagnóstico de solo lectura.

Dataset, entornos, credenciales y resultados locales no se suben a Git.
No cambies protecciones de Windows ni controladores automáticamente. El bloqueo
histórico de SciPy y su resolución por el usuario están en BLOQUEO_WINDOWS.md.

## Mantener continuidad

Al terminar una tarea, registra en DECISIONES_Y_ESTADO.md qué se hizo, qué se probó,
qué quedó pendiente y el próximo paso acordado. Actualiza HOJA_DE_RUTA.md cuando
se acuerden o completen fases. No marques como publicado algo que solo está local.
Mantén este AGENTS.md para instrucciones duraderas, evitando duplicar versiones
y resultados que ya tienen un documento propio.

Material original adicional aportado en el primer chat: ACLARACION_CORTES.md,
GPUs, entornos y GitHub.pdf, presentacion_caso.pdf y s41597-026-06589-6.pdf.
No están incluidos actualmente en el repositorio. Sus conclusiones registradas
sirven de contexto, pero no afirmes haber leído esos originales en un chat nuevo.
Si necesitas comprobar un detalle no recogido, localiza el original o pídelo.
La discrepancia de licencias sigue pendiente: no sobrescribas LICENSE.
