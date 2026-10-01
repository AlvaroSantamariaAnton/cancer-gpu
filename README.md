# cancer-gpu

Trabajo individual BreastDCEDL: predicción educativa de pCR con una CNN 2D propia.
La arquitectura la diseña Álvaro; modelo candidato en entrenamiento, aún no final.
Fases 1 y 2 completadas. Fase 3 en curso: CNN v1 implementada y comprobaciones
técnicas superadas en RTX 3060 Ti. Primera comparación de fase 4 en fold 0
terminada: normal 36 épocas, ponderada 11; no hay modelo final ni evaluación test.

PC Casa preparado: PyTorch 2.14.0+cu126, GPU, carga y métricas sintéticas
verificados. El bloqueo de SciPy está resuelto por el usuario. La AMD ha pasado convolución y gradientes con
ROCm 7.14. Quedan pendientes las dependencias comunes y la prueba completa de
carga en universidad. Consulta [el estado](docs/DECISIONES_Y_ESTADO.md).

- [Instrucciones para retomar el proyecto en otro chat](AGENTS.md)
- [Notebook de auditoría y visualización](notebooks/01_auditoria_datos.ipynb) · [Cómo ejecutarlo](notebooks/README.md)
- [Hoja de ruta aprobada](docs/HOJA_DE_RUTA.md)
- [Arquitectura actual: diagrama horizontal y configuración](docs/ARQUITECTURA_ACTUAL.md)
- [Referencia CNN v1 y experimentos iniciales](docs/ARQUITECTURA_V1.md)
- [Entrenamiento: comandos para ejecutar y reanudar](docs/ENTRENAMIENTO.md)
- [Diagnóstico de memorización: ejecución por Álvaro](docs/MEMORIZACION.md)
- [Decisiones y estado del trabajo](docs/DECISIONES_Y_ESTADO.md)
- [Trabajar desde casa y universidad](docs/ENTORNOS.md)
- [Guía docente original](GUIA.md)
- [Enunciado oficial](documentation/caso_breastdcedl.pdf)

El repositorio ya es la raíz de BreastDCEDL: `metadata/`, `dataset/` y
`utils_caso.py` van aquí, sin otra carpeta `breastdcedl/` intermedia.
El dataset se conserva localmente y está excluido de Git.

## Organización

| Carpeta | Contenido |
|---|---|
| `models/` | Arquitecturas reutilizables: `cnn_v1.py` y `cnn_v2.py` |
| `scripts/` | Comandos de entrenamiento, diagnóstico y auditoría |
| `docs/` | Decisiones, arquitectura, protocolo e instrucciones |
| `documentation/` | Enunciado docente original |
| `notebooks/` | Exploración y visualizaciones |
| `metadata/` | Metadatos docentes |
| `dataset/` | Imágenes locales, excluidas de Git |
| `runs/`, `reports/local/` | Resultados y checkpoints locales, excluidos de Git |

Las utilidades docentes originales (`utils_caso.py`, `descargar_datos.py`,
`ver_muestras.py`) se conservan en la raíz por compatibilidad con la guía.
La CNN v2 está preparada pero Álvaro aún no la ha ejecutado.

## Entorno

Con Conda instalado, desde la raíz:

```text
conda env create -f environment.yml
conda activate cancer
```

En Windows/NVIDIA:

```text
python scripts/sincronizar_entorno.py --equipo casa --instalar-torch
```

En Ubuntu/AMD, **primero** conserva un diagnóstico de la instalación existente:

```text
conda activate cancer
python scripts/diagnostico_entorno.py --equipo universidad --probar-gpu
```

El perfil AMD recoge las versiones que ya funcionan en universidad. Revisa
[ENTORNOS.md](docs/ENTORNOS.md) antes de sustituir el PyTorch que ya tienes allí.

## Verificar los datos

```text
python scripts/verificar_dataset.py
```

La comprobación abre los PNG y valida formato, dimensiones y rutas; no evalúa
modelos ni usa las etiquetas test para tomar decisiones.

Uso docente, sin validez clínica. Se conserva [LICENSE](LICENSE) tal como estaba.
Hay una discrepancia entre ese archivo y la licencia indicada en el enunciado;
véase el registro de decisiones antes de redistribuir material de BreastDCEDL.
