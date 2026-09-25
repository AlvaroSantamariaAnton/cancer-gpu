# Entornos: PC Casa y PC Universidad

## Objetivo y límites

**Estado actual (2026-09-25):** bloqueo de SciPy resuelto por el usuario al
desactivar Smart App Control; prueba completa de carga y métricas superada.
Casa actualizado a PyTorch 2.14.0+cu126: dependencias, importaciones, GPU, carga
y métricas sintéticas verificadas. La AMD ha pasado la prueba
de convolución y gradientes; faltan dependencias comunes y carga de datos en universidad.

Compartir código, versiones de bibliotecas, configuraciones y decisiones por Git.
Cada equipo necesita su propia instalación del entorno `cancer`: una carpeta
Conda de Windows no sirve en Ubuntu. El Python global no determina el del entorno.

| Equipo | Sistema | GPU | Memoria | Variante PyTorch |
|---|---|---|---|---|
| Casa | Windows | NVIDIA RTX 3060 Ti | 8 GB | CUDA |
| Universidad | Ubuntu | AMD Radeon RX 6700 XT | 12 GB | ROCm/HIP |

`environment.yml` fija Python 3.12.14, NumPy 2.5.3 y SciPy 1.18.1.
NumPy y SciPy se mantienen en Conda. Cambiar de pip a conda-forge no resolvió
el bloqueo de Windows; véase el historial en [BLOQUEO_WINDOWS.md](BLOQUEO_WINDOWS.md).
`requirements.txt` fija las dependencias comunes y los perfiles GPU fijan:

| Componente | Casa | Universidad |
|---|---|---|
| Python | 3.12.14 | 3.12.14 |
| torch | 2.14.0+cu126 | 2.14.0+rocm7.14 |
| torchvision | 0.29.0+cu126 | 0.29.0+rocm7.14 |
| NumPy objetivo | 2.5.3 | 2.5.3 (instalado actualmente: 2.5.2) |

El usuario confirmó Ubuntu 26.04.1, HIP 7.14.60850 y paquetes ROCm SDK 7.14.1.
La RX 6700 XT pasó convolución y gradientes con
`HSA_OVERRIDE_GFX_VERSION=10.3.0`. Se conserva ese ajuste existente, sin afirmar
que sea imprescindible. MIOpen avisó de una base de datos ilegible y biblioteca CK
no encontrada para gfx1030; también apareció un aviso xnack. La prueba pasó,
pero no certifica rendimiento ni estabilidad de entrenamientos completos.

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
PowerShell ya está inicializado para Conda en casa. En una terminal nueva:

```powershell
conda activate cancer
```

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

El diagnóstico guarda `reports/local/entorno-universidad.json`. La prueba manual
compartida por Álvaro ya confirmó las versiones y la operación GPU.
No instalar controladores ni ROCm de sistema ni sustituir el PyTorch funcional.
El diagnóstico registra `HSA_OVERRIDE_GFX_VERSION`; comprobar que sigue siendo 10.3.0.

Cuando Álvaro vuelva a universidad, tras revisar los cambios y actualizar el repo:

```text
conda activate cancer
conda env update -f environment.yml
python scripts/sincronizar_entorno.py --equipo universidad
python scripts/comprobar_carga.py
```

Esto instala las dependencias comunes pendientes y actualiza NumPy a 2.5.3.
No usar `--instalar-torch` en ese equipo: sus versiones ya coinciden.
La instalación y validación completa allí siguen pendientes.

## Al cambiar de ordenador

Antes de salir:

1. Actualizar `docs/DECISIONES_Y_ESTADO.md` con lo hecho y el siguiente paso.
2. Revisar con Álvaro los cambios de código/configuración antes de commit y push.
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
