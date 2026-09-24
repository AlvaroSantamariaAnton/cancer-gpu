"""Prueba de integración de las utilidades docentes y el entorno, sin entrenar."""
from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--solo-datos', action='store_true',
                        help='Comprueba lectura de imágenes, sin probar el cálculo de métricas.')
    args = parser.parse_args()
    import numpy as np
    import pandas as pd
    import torch
    from torch.utils.data import DataLoader
    import utils_caso as uc

    samples = uc.cargar_samples()
    train, validation = uc.particion(samples, fold_val=0)
    if set(train.patient_id) & set(validation.patient_id):
        raise RuntimeError('Pacientes compartidas entre train y validación.')
    loader = DataLoader(uc.BreastDCEDataset(train.iloc[:2]), batch_size=2,
                        shuffle=False, num_workers=0)
    images, labels = next(iter(loader))
    if images.shape != (2, 3, 256, 256) or images.dtype != torch.float32:
        raise RuntimeError('Forma o tipo incorrecto al cargar las fases.')
    if not torch.isfinite(images).all() or images.min() < 0 or images.max() > 1:
        raise RuntimeError('Intensidades fuera de rango.')
    if labels.shape != (2,):
        raise RuntimeError('Forma incorrecta de las etiquetas.')
    print('OK: utilidades docentes, partición por paciente, lectura PRE/EARLY/LATE y DataLoader.', flush=True)
    if args.solo_datos:
        print('Métricas NO verificadas: se ha solicitado solo la carga de datos.')
        return
    from sklearn.metrics import roc_auc_score  # Detectar errores DLL sin que utils_caso los oculte.
    # Ejemplo sintético para comprobar compatibilidad pandas/NumPy/sklearn.
    synthetic = pd.DataFrame({'patient_id': ['a', 'a', 'b', 'b'], 'pCR': [0, 0, 1, 1]})
    metrics = uc.evaluar_por_paciente(np.array([0.1, 0.2, 0.8, 0.9]), synthetic)
    if metrics['auc'] != 1.0 or metrics['pacientes'] != 2:
        raise RuntimeError('La evaluación sintética no produce el resultado esperado.')
    print('OK: agregación y AUC sobre ejemplo sintético. No son resultados del modelo.')

if __name__ == '__main__':
    main()
