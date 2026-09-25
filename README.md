# cancer-gpu

Trabajo individual BreastDCEDL: predicción educativa de pCR con una CNN 2D propia.
La arquitectura la diseña Álvaro; todavía no hay modelo entrenado.
Fase 1 completada: auditoría y visualizaciones revisadas. Próximo paso: acordar
el protocolo experimental de la fase 2.

PC Casa preparado: PyTorch 2.14.0+cu126, GPU, carga y métricas sintéticas
verificados. El bloqueo de SciPy está resuelto por el usuario. La AMD ha pasado convolución y gradientes con
ROCm 7.14. Quedan pendientes las dependencias comunes y la prueba completa de
carga en universidad. Consulta [el estado](docs/DECISIONES_Y_ESTADO.md).

- [Instrucciones para retomar el proyecto en otro chat](AGENTS.md)
- [Notebook de auditoría y visualización](notebooks/01_auditoria_datos.ipynb) · [Cómo ejecutarlo](notebooks/README.md)
- [Hoja de ruta aprobada](docs/HOJA_DE_RUTA.md)
- [Decisiones y estado del trabajo](docs/DECISIONES_Y_ESTADO.md)
- [Trabajar desde casa y universidad](docs/ENTORNOS.md)
- [Guía docente original](GUIA.md)
- [Enunciado oficial](documentation/caso_breastdcedl.pdf)

El repositorio ya es la raíz de BreastDCEDL: `metadata/`, `dataset/` y
`utils_caso.py` van aquí, sin otra carpeta `breastdcedl/` intermedia.
El dataset se conserva localmente y está excluido de Git.

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
