# Cuadernos de exploración

`01_auditoria_datos.ipynb` es el cuaderno de la fase 1. Ábrelo en tu editor de
notebooks y selecciona el Python del entorno **cancer**. Activa ese entorno antes
de iniciar el editor/Jupyter: `conda activate cancer`. No instala dependencias.
Verificado también en VS Code por Álvaro: las cinco celdas terminan sin errores.
Selecciona **cancer (Python 3.12.14)** y pulsa **Ejecutar todo**. No ejecutes el
archivo `.py` por separado: el notebook importa sus funciones automáticamente.
El entorno necesita `ipykernel` (incluido en requirements.txt).

Ejecuta las celdas en orden. Las funciones reutilizables están en
`scripts/auditoria_datos.py`. Los CSV, figuras y la copia ejecutada se guardan en
`reports/local/auditoria/`, excluido de Git. El cuaderno versionable conserva
solo código y explicaciones, sin imágenes del dataset incrustadas.

Para reutilizar desde otro notebook, añade la raíz del repositorio a `sys.path`
y usa `from scripts import auditoria_datos as ad`. `cargar`, `auditar`,
`tablas_train`, `figura_fases` y `figura_paciente` aceptan los mismos metadatos.
Las funciones de lectura de imágenes rechazan filas de test.

La selección de ejemplos es determinista, no representativa. Las comprobaciones
no detectan duplicados de contenido ni aseguran alineación anatómica perfecta.
No se modifican metadatos ni se excluyen pacientes automáticamente.
