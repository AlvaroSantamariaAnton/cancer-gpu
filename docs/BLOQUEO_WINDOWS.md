# Bloqueo pendiente de Windows: SciPy

## Resultado

La preparación de PC Casa no está terminada. El dataset está completo y verificado,
Python 3.12.14 y PyTorch 2.13.0+cu126 están instalados, y la RTX 3060 Ti ejecuta
convoluciones y gradientes correctamente. La carga de imágenes también pasa.
Sin embargo, scikit-learn no puede importarse porque Windows rechaza una extensión
de SciPy. No se ha desactivado ni modificado ninguna protección.

## Evidencia y alternativas probadas

1. Miniforge 26.7.2-0, descargado de su publicación oficial y verificado por SHA256:
   Windows rechazó `_conda.exe`. Se retiró solo esa instalación fallida.
2. Miniconda oficial, SHA256 y firma digital de Anaconda válidos: instalado
   correctamente en `D:\proyectos\_herramientas\miniconda3`.
3. SciPy 1.18.1 mediante pip/PyPI: error de carga en `_cythonized_array_utils`:
   `Una directiva de Control de aplicaciones bloqueó este archivo.`
4. Sustitución por SciPy 1.18.1 y NumPy 2.5.3 de conda-forge: falla al cargar
   `_arpacklib` con el mismo mensaje. Esta alternativa tampoco resuelve el problema.

Módulo de la segunda variante:

```text
D:\proyectos\_herramientas\miniconda3\envs\cancer\Lib\site-packages\scipy\sparse\linalg\_eigen\arpack\_arpacklib.cp312-win_amd64.pyd
```

Firma Authenticode del módulo: `NotSigned`.
SHA256: `F12597733DFE60F5FE301C62ACDFAF1ADC91EEA1E73C9A83AD051ECDEE4B19A4`.
La ausencia de firma por sí sola no demuestra que sea malicioso ni identifica
la regla exacta: el error de carga sí confirma que interviene una política de Windows.
El fallo puede corresponder al módulo o a una dependencia que intenta cargar.

## Lo que funciona y lo que no demuestra cada prueba

```text
python scripts/diagnostico_entorno.py --equipo casa --probar-gpu
python scripts/comprobar_carga.py --solo-datos
python -m pip check
```

Estas pruebas comprueban GPU, lectura de datos y coherencia de dependencias.
No certifican el cálculo de métricas. `utils_caso.evaluar_por_paciente` captura
excepciones de scikit-learn y podría devolver AUC NaN; no interpretar eso como
un resultado del modelo ni continuar el experimento ignorándolo.

## Siguiente paso

Lectura de configuración realizada: `VerifiedAndReputablePolicyState = 1`,
compatible con Control inteligente de aplicaciones activo. Microsoft explica que
Smart App Control no ofrece excepciones individuales para aplicaciones:
[preguntas frecuentes oficiales](https://support.microsoft.com/en-us/windows/security/threat-malware-protection/smart-app-control-frequently-asked-questions).
No se ha modificado ese valor ni se propone desactivar la protección como paso automático.

Revisar con el propietario/administrador del PC qué regla rechaza la extensión y
buscar una distribución o entorno admitidos por su política. No añadir exclusiones,
autorizar binarios ni desactivar Control de aplicaciones automáticamente.
Después repetir:

```text
python scripts/comprobar_carga.py
python scripts/sincronizar_entorno.py --equipo casa
```

Solo tras completar ambas pruebas se marcará PC Casa como preparado. Cualquier
cambio de versiones o canal debe reflejarse en las recetas y en el registro de decisiones.
