"""Diagnóstico que ejecuta Álvaro: memorizar ocho cortes, no medir generalización."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import platform
import random
import signal
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from entrenar import guardar_atomico, huella


def seleccionar(filas, semilla=42):
    """Cuatro pacientes por clase y un corte por paciente, solo folds 1–4."""
    pacientes = {}
    for fila in filas:
        if fila['split'] != 'train' or int(fila['fold']) not in (1, 2, 3, 4):
            continue
        pacientes.setdefault(fila['patient_id'], []).append(fila)
    rng = random.Random(semilla)
    por_clase = {0: [], 1: []}
    for paciente in sorted(pacientes):
        etiquetas = {int(float(f['pCR'])) for f in pacientes[paciente]}
        if len(etiquetas) != 1 or not etiquetas <= {0, 1}:
            raise ValueError('Etiquetas inconsistentes por paciente.')
        por_clase[etiquetas.pop()].append(paciente)
    elegidas = []
    for clase in (0, 1):
        if len(por_clase[clase]) < 4:
            raise ValueError('Se necesitan cuatro pacientes de entrenamiento por clase.')
        for paciente in rng.sample(por_clase[clase], 4):
            cortes = sorted(pacientes[paciente], key=lambda f: f['sample_id'])
            elegidas.append(rng.choice(cortes))
    return elegidas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--nombre', default='cnn-v1-memorizacion')
    parser.add_argument('--pasos', type=int, default=200,
                        help='Actualizaciones sobre los mismos ocho cortes; diagnóstico, no épocas completas.')
    parser.add_argument('--device', choices=['cuda', 'cpu'], default='cuda')
    args = parser.parse_args()
    if args.pasos < 1 or not args.nombre or any(c not in
            'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in args.nombre):
        parser.error('Pasos positivos y nombre con letras ASCII, números, _ o -.')
    carpeta = ROOT / 'runs' / args.nombre
    if carpeta.exists():
        raise FileExistsError('La carpeta existe. Elige otro --nombre; no se sobrescribe.')

    import numpy as np
    import pandas as pd
    import torch
    from torch import nn
    from torch.utils.data import DataLoader
    from models.cnn_v1 import CNNV1
    import utils_caso as uc

    device = torch.device(args.device)
    if device.type == 'cuda' and not torch.cuda.is_available():
        raise RuntimeError('GPU no disponible; no se cambia automáticamente a CPU.')
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    with (ROOT / 'metadata/samples.csv').open(encoding='utf-8-sig', newline='') as f:
        filas = pd.DataFrame(seleccionar(list(csv.DictReader(f))))
    loader = DataLoader(uc.BreastDCEDataset(filas), batch_size=8, shuffle=False, num_workers=0)
    x, y = next(iter(loader))
    if x.shape != (8, 3, 256, 256) or not torch.isfinite(x).all() or x.min() < 0 or x.max() > 1:
        raise ValueError('Entrada incorrecta.')
    x, y = x.to(device), y.to(device).reshape(-1, 1)
    modelo = CNNV1().to(device)  # Desde cero, no carga modelos anteriores.
    optimizador = torch.optim.Adam(modelo.parameters(), lr=0.001, weight_decay=0)
    criterio = nn.BCEWithLogitsLoss()
    carpeta.mkdir(parents=True, exist_ok=False)
    config = {'tipo': 'diagnostico_memorizacion_no_validacion', 'semilla': 42,
              'cortes': 8, 'pacientes': 8, 'por_clase': 4, 'pasos': args.pasos,
              'lr': 0.001, 'perdida': 'normal', 'equipo': platform.node(),
              'python': platform.python_version(), 'torch': str(torch.__version__),
              'device': str(device), 'gpu': torch.cuda.get_device_name() if device.type == 'cuda' else None,
              'fuentes': {p: huella(ROOT / p) for p in
                         ['models/cnn_v1.py', 'scripts/probar_memorizacion.py', 'scripts/entrenar.py',
                          'utils_caso.py', 'metadata/samples.csv']}}
    guardar_atomico(carpeta / 'config.json', json.dumps(config, indent=2).encode())
    guardar_atomico(carpeta / 'muestras.csv', filas.to_csv(index=False).encode())
    parar = False

    def solicitar_parada(signum, frame):
        nonlocal parar
        parar = True
        print('\nParada solicitada: guardando tras completar el paso actual.', flush=True)

    signal.signal(signal.SIGINT, solicitar_parada)
    historial = []
    t0 = time.perf_counter()
    print('Diagnóstico: ocho cortes fijos de train, cuatro por clase. No es validación.', flush=True)
    if device.type == 'cuda':
        torch.cuda.reset_peak_memory_stats()
    for paso in range(args.pasos + 1):
        if paso:
            modelo.train()
            optimizador.zero_grad(set_to_none=True)
            loss = criterio(modelo(x), y)
            if not torch.isfinite(loss):
                raise RuntimeError('Pérdida no finita.')
            loss.backward()
            if any(p.grad is None or not torch.isfinite(p.grad).all() for p in modelo.parameters()):
                raise RuntimeError('Gradientes no finitos.')
            optimizador.step()
        modelo.eval()
        with torch.no_grad():
            logits = modelo(x)
            perdida = criterio(logits, y).item()
            probs = logits.sigmoid()
        if not torch.isfinite(logits).all():
            raise RuntimeError('Salida no finita.')
        aciertos = int(((probs >= 0.5) == y.bool()).sum().item())
        historial.append({'paso': paso, 'bce_mismas_muestras': perdida,
                           'aciertos_de_8': aciertos, 'segundos_acumulados': time.perf_counter() - t0})
        guardar_atomico(carpeta / 'metricas.csv', pd.DataFrame(historial).to_csv(index=False).encode())
        if paso % 10 == 0 or paso == args.pasos or parar:
            print(f'Paso {paso}/{args.pasos} | BCE={perdida:.6f} | aciertos={aciertos}/8', flush=True)
        if paso == args.pasos or parar:
            break
    predicciones = filas[['patient_id', 'sample_id', 'pCR']].copy()
    predicciones['prob'] = probs.flatten().cpu().numpy()
    predicciones['prediccion_050'] = (predicciones.prob >= 0.5).astype(int)
    guardar_atomico(carpeta / 'predicciones_finales.csv', predicciones.to_csv(index=False).encode())
    buffer = io.BytesIO()
    torch.save({'modelo': modelo.state_dict(), 'config': config, 'paso': paso,
                'uso': 'Solo diagnóstico; no reanudable ni modelo final'}, buffer)
    guardar_atomico(carpeta / 'diagnostico.pt', buffer.getvalue())
    guardar_atomico(carpeta / 'resumen.json', json.dumps({
        'pasos_completados': paso, 'bce_inicial': historial[0]['bce_mismas_muestras'],
        'bce_final': perdida, 'aciertos_finales': aciertos,
        'interrumpido': parar, 'memoria_max_mib':
        torch.cuda.max_memory_allocated() / 2**20 if device.type == 'cuda' else None,
        'nota': 'No demuestra generalización; no es criterio automático de descarte.'}, indent=2).encode())
    print(f'Diagnóstico guardado en {carpeta}. No se ha usado validación ni test.', flush=True)


if __name__ == '__main__':
    main()
