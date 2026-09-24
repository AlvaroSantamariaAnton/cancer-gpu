# Entornos: PC Casa y PC Universidad

## Objetivo y límites

**Estado actual:** GPU y lectura de datos operativas en casa; cálculo de métricas
bloqueado por Windows. Véase [BLOQUEO_WINDOWS.md](BLOQUEO_WINDOWS.md).
La sincronización comprueba las importaciones y falla si persiste ese bloqueo;
no es suficiente que `pip check` termine bien.

Compartir código, versiones de bibliotecas, configuraciones y decisiones por Git.
Cada equipo necesita su propia instalación del entorno `cancer`: una carpeta
Conda de Windows no sirve en Ubuntu. El Python global no determina el del entorno.

| Equipo | Sistema | GPU | Memoria | Variante PyTorch |
|---|---|---|---|---|
| Casa | Windows | NVIDIA RTX 3060 Ti | 8 GB | CUDA |
| Universidad | Ubuntu | AMD Radeon RX 6700 XT | 12 GB | ROCm/HIP |

`environment.yml` fija Python 3.12.14, NumPy 2.5.3 y SciPy 1.18.1.
NumPy y SciPy se instalan con Conda: la distribución pip de SciPy provocó un
bloqueo de Control de aplicaciones en este PC; no se cambian políticas de Windows.
La alternativa conda-forge también resultó bloqueada en otra extensión: **no se
considera resuelto**. Estas versiones quedan documentadas para reproducir el estado,
no certificadas como una instalación completa de Windows.
`requirements.txt` fija las bibliotecas
compartidas. Los archivos `requirements/torch-*.txt` fijan la misma versión pública
de torch/torchvision con binarios distintos para cada GPU.

La propuesta inicial es torch 2.13.0 y torchvision 0.28.0, con CUDA 12.6 en casa
y ROCm 7.1 en universidad. **No se ha comprobado aún que coincida con la
instalación universitaria ni que esa combinación ejecute kernels en la RX 6700 XT.**
La versión final común debe confirmarse a partir de ambos diagnósticos; si hay que
cambiarla, se actualizan los dos perfiles y se repiten las pruebas.

El índice comunicado `rocm7.14` queda pendiente de aclarar: la documentación
oficial consultada publica `rocm7.1`, no permite deducir qué se instaló allí.
No sustituir el entorno universitario que funcione sin guardar primero su estado.

## Primera instalación

```text
conda env create -f environment.yml
conda activate cancer
```

Si `cancer` ya existe, no repetir la creación. Comprobar `python --version`
y guardar primero el diagnóstico. No exportar todo un entorno Linux como receta
para Windows: contiene paquetes y builds específicos de plataforma.

Si Miniconda intenta consultar sus canales predeterminados pese a `nodefaults`,
la alternativa equivalente y comprobada en casa es:

```text
conda create -n cancer --override-channels -c conda-forge python=3.12.14 pip numpy=2.5.3 scipy=1.18.1
```

En este PC, Miniconda está instalado en `D:\proyectos\_herramientas\miniconda3`.
Desde PowerShell, situado en el repositorio, se puede activar sin modificar el
perfil global de la terminal:

```powershell
. .\scripts\activar_casa.ps1
```

También se puede abrir Miniconda Prompt y ejecutar `conda activate cancer`.

En casa:

```text
python scripts/sincronizar_entorno.py --equipo casa --instalar-torch
```

En universidad, antes de instalar o actualizar:

```text
conda activate cancer
python scripts/diagnostico_entorno.py --equipo universidad --probar-gpu
python -m pip freeze
```

El primer comando guarda `reports/local/entorno-universidad.json`. Compartir el
informe para cerrar la combinación de versiones. Instalar un paquete ROCm no
demuestra que la GPU funcione: la prueba incluye convolución y cálculo de gradientes.
No instalar controladores ni ROCm a nivel de sistema en el PC universitario.

El material docente menciona `HSA_OVERRIDE_GFX_VERSION=10.3.0` para esa GPU.
No lo aplicamos automáticamente ni lo consideramos garantía de compatibilidad.
Debe contrastarse con el entorno preparado por el laboratorio. El diagnóstico
registra si esa variable ya está definida.

Una vez verificado el perfil AMD:

```text
python scripts/sincronizar_entorno.py --equipo universidad --instalar-torch
```

## Al cambiar de ordenador

Antes de salir:

1. Actualizar `docs/DECISIONES_Y_ESTADO.md` con lo hecho y el siguiente paso.
2. Guardar cambios de código/configuración con commit y push.
3. Si hay entrenamiento, guardar y transferir su checkpoint por separado.

Al llegar, desde el repositorio:

```text
git pull --ff-only
conda activate cancer
python scripts/sincronizar_entorno.py --equipo casa
```

Sustituir `casa` por `universidad` en Ubuntu. La sincronización detiene el proceso
si PyTorch no coincide con el perfil; no lo reemplaza silenciosamente.
`--instalar-torch` se usa en la primera instalación o cuando acordemos actualizarlo.
Si cambia `environment.yml`, revisar y aplicar también `conda env update -f environment.yml`
antes de sincronizar pip.

`git pull` descarga archivos, **no instala bibliotecas ni descarga dataset o pesos**.
Para añadir una biblioteca: instalarla en `cancer`, registrar la versión en
`requirements.txt` y comprobar ambos equipos. Las dependencias de sistema se
documentan aparte. El entorno de Conda y los binarios CUDA/ROCm nunca se suben.

## Entrenamiento portátil: requisitos para la fase de implementación

- Código PyTorch común: `torch.cuda` también es la interfaz usada por ROCm;
  `torch.version.hip` distingue la variante AMD.
- `batch_size` configurable en cada ejecución y registrado junto a la GPU.
  Todavía no se fija ninguno: se medirá con la CNN que diseñe Álvaro.
- Variar el lote puede cambiar la optimización. Considerar acumulación de
  gradientes para conservar el lote efectivo, sin asumir equivalencia exacta
  cuando existan operaciones dependientes del lote, como BatchNorm.
- Guardar configuración, arquitectura/versionado del código, pesos, optimizador,
  scheduler, época, mejor métrica, partición, semillas y estados aleatorios;
  estado del escalador si se usa precisión mixta. Cargar con `map_location`
  y trasladar los tensores al dispositivo de destino.
- Preferir cambio de equipo entre épocas. Reanudar a mitad de época necesita
  además recuperar orden de muestreo y progreso del DataLoader.
- Windows requiere proteger el punto de entrada con `if __name__ == '__main__'`
  para DataLoader con procesos. Empezar con `num_workers=0` al depurar.
- Git comparte el código; `checkpoints/` está ignorado y hay que transferirlo.
  Antes de entrenar elegiremos el medio para esos ficheros y verificaremos hashes.
- No se promete reproducción bit a bit entre Windows/CUDA y Ubuntu/ROCm.

## Fuentes consultadas

- [Versiones oficiales de PyTorch](https://pytorch.org/get-started/previous-versions/).
- [Gestión de entornos Conda](https://docs.conda.io/projects/conda/en/stable/user-guide/tasks/manage-environments.html).
- `GPUs, entornos y GitHub.pdf`, material docente aportado por Álvaro.
