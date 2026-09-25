# Historial del bloqueo de Windows: SciPy

## Estado actualizado — 2026-09-25

Álvaro desactivó personalmente Control inteligente de aplicaciones de Windows y
compartió una ejecución completa correcta de `scripts/comprobar_carga.py`,
incluidas agregación y AUC sintéticas. El bloqueo queda resuelto en esa configuración.
El agente no cambió protecciones. Desactivar Smart App Control es un cambio global
del equipo, no un requisito automático de instalación del proyecto.

Los eventos aportados 3033 y 3077 identificaron
`scipy/optimize/_group_columns.cp312-win_amd64.pyd` y la política
`VerifiedAndReputableDesktop` ({0283ac0f-fff1-49ae-ada1-8a933130cad6}).

Lo que sigue documenta el diagnóstico previo, no el estado actual.

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

## Pasos propuestos durante el diagnóstico (histórico)

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
