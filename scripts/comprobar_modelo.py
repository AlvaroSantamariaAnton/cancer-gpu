"""Diagnóstico CNN v1: pasos aislados; no entrena por épocas ni evalúa test."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import torch
from torch import nn
from torch.utils.data import DataLoader
from models.cnn_v1 import CNNV1
import utils_caso as uc


def comprobar(condicion, mensaje):
    if not condicion:
        raise RuntimeError(mensaje)


def paso(x, y, dispositivo, pos_weight=None):
    # Cada prueba empieza desde cero; sus pesos se descartan.
    torch.manual_seed(42)
    if dispositivo.type == 'cuda':
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
    modelo = CNNV1().to(dispositivo)
    comprobar(sum(p.numel() for p in modelo.parameters()) == 23649,
              'Conteo de parámetros inesperado.')
    comprobar(all(torch.count_nonzero(p) == 0 for n, p in modelo.named_parameters()
                  if n.endswith('bias')), 'Sesgos iniciales distintos de cero.')
    optimizador = torch.optim.Adam(modelo.parameters(), lr=0.001, weight_decay=0)
    x, y = x.to(dispositivo), y.to(dispositivo).reshape(-1, 1)
    formas = []
    handles = [b.register_forward_hook(lambda m, i, o: formas.append(list(o.shape)))
               for b in modelo.bloques]
    logits = modelo(x)
    for handle in handles:
        handle.remove()
    comprobar(formas == [[len(x), 16, 128, 128], [len(x), 32, 64, 64],
                         [len(x), 64, 32, 32]], 'Dimensiones de bloques incorrectas.')
    comprobar(logits.shape == (len(x), 1) and torch.isfinite(logits).all(),
              'Salida incorrecta o no finita.')
    peso = None if pos_weight is None else torch.tensor(pos_weight, device=dispositivo)
    perdida = nn.BCEWithLogitsLoss(pos_weight=peso)(logits, y)
    comprobar(torch.isfinite(perdida), 'Pérdida no finita.')
    perdida.backward()
    comprobar(all(p.grad is not None and torch.isfinite(p.grad).all()
                  for p in modelo.parameters()), 'Gradientes ausentes o no finitos.')
    antes = {n: p.detach().clone() for n, p in modelo.named_parameters()}
    optimizador.step()
    cambiados = [n for n, p in modelo.named_parameters() if not torch.equal(antes[n], p)]
    comprobar(all(torch.isfinite(p).all() for p in modelo.parameters()), 'Pesos no finitos.')
    comprobar(all(f'bloques.{i}.0.weight' in cambiados for i in range(3))
              and 'salida.weight' in cambiados, 'No se actualizan todas las capas.')
    modelo.eval()
    with torch.no_grad():
        uno = modelo(x[:1])
        dos = modelo(x[:1])
    comprobar(uno.shape == (1, 1) and torch.isfinite(uno).all(), 'Fallo con lote unitario.')
    comprobar(torch.equal(uno, dos), 'Inferencia repetida diferente en el mismo dispositivo.')
    memoria = None
    if dispositivo.type == 'cuda':
        torch.cuda.synchronize()
        memoria = {
            'max_allocated_mib': torch.cuda.max_memory_allocated() / 2**20,
            'max_reserved_mib': torch.cuda.max_memory_reserved() / 2**20,
        }
    return {'ok': True, 'formas_bloques': formas, 'salida': list(logits.shape),
            'perdida_diagnostica': perdida.item(), 'pos_weight': pos_weight,
            'tensores_actualizados': cambiados, 'memoria': memoria}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch-size', type=int, default=32)
    parser.add_argument('--device', choices=['cpu', 'cuda'], default='cuda')
    args = parser.parse_args()
    if args.batch_size < 2:
        parser.error('batch-size debe ser al menos 2 para incluir ambas clases.')
    if args.device == 'cuda' and not torch.cuda.is_available():
        raise RuntimeError('GPU no disponible; no se sustituye silenciosamente por CPU.')
    dispositivo = torch.device(args.device)
    torch.manual_seed(42)
    sintetica = paso(torch.rand(args.batch_size, 3, 256, 256),
                     (torch.arange(args.batch_size) % 2).float(), dispositivo)
    print('OK: datos sintéticos, formas, parámetros, gradientes y Adam.', flush=True)
    train, _ = uc.particion(uc.cargar_samples(), fold_val=0)
    # Selección técnica reproducible con ambas clases; no es un muestreador de entrenamiento.
    filas = train.groupby('pCR', group_keys=False).head((args.batch_size + 1) // 2)
    filas = filas.sort_values('pCR').groupby('pCR', group_keys=False).sample(frac=1, random_state=42)
    import pandas as pd
    filas = pd.concat([filas[filas.pCR == 0].head(args.batch_size // 2),
                       filas[filas.pCR == 1].head(args.batch_size - args.batch_size // 2)])
    comprobar(len(filas) == args.batch_size and set(filas.pCR) == {0, 1}, 'Lote incompleto.')
    comprobar((filas.split == 'train').all() and filas.fold.isin([1, 2, 3, 4]).all(),
              'Se han incluido cortes ajenos al entrenamiento.')
    x, y = next(iter(DataLoader(uc.BreastDCEDataset(filas), batch_size=args.batch_size,
                                shuffle=False, num_workers=0)))
    comprobar(x.dtype == torch.float32 and torch.isfinite(x).all()
              and x.min() >= 0 and x.max() <= 1, 'Entrada real incorrecta.')
    normal = paso(x, y, dispositivo)
    peso = float((train.pCR == 0).sum() / (train.pCR == 1).sum())
    ponderada = paso(x, y, dispositivo, peso)
    informe = {
        'fecha_utc': datetime.now(timezone.utc).isoformat(), 'equipo': platform.node(),
        'torch': torch.__version__, 'dispositivo': args.device,
        'gpu': torch.cuda.get_device_name() if args.device == 'cuda' else None,
        'batch_size': args.batch_size, 'parametros': 23649, 'precision': 'float32, sin AMP',
        'sintetica': sintetica, 'real_normal': normal, 'real_ponderada': ponderada,
        'nota': 'Pasos aislados, pesos descartados. No son métricas predictivas ni comparación de rendimiento.',
    }
    destino = ROOT / 'reports/local/comprobacion_modelo.json'
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(informe, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(informe, indent=2, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
