"""Entrenamiento CNN v1 iniciado exclusivamente por el usuario. Nunca usa test."""
import argparse
import hashlib
import io
import json
import math
import os
from pathlib import Path
import platform
import random
import signal
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def actualizar_parada(auc, mejor, sin_mejora, epoca):
    if not math.isfinite(auc):
        raise ValueError('AUC de validación no finita; no se guarda esta época.')
    mejora = auc > mejor
    contador = 0 if mejora else sin_mejora + 1
    return max(auc, mejor), contador, mejora, epoca >= 10 and contador >= 10


def guardar_atomico(ruta, contenido):
    temporal = ruta.with_suffix(ruta.suffix + '.tmp')
    with temporal.open('wb') as archivo:
        archivo.write(contenido)
        archivo.flush()
        os.fsync(archivo.fileno())
    os.replace(temporal, ruta)


def huella(ruta):
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def argumentos():
    parser = argparse.ArgumentParser(description=__doc__)
    grupo = parser.add_mutually_exclusive_group(required=True)
    grupo.add_argument('--perdida', choices=['normal', 'ponderada'], help='Nueva ejecución.')
    grupo.add_argument('--reanudar', type=Path, help='Ruta a ultimo.pt propio y de confianza.')
    parser.add_argument('--nombre', help='Nombre nuevo dentro de runs/. No se sobrescribe.')
    parser.add_argument('--fold', type=int, choices=range(5), default=0)
    parser.add_argument('--batch-size', type=int, default=32)
    parser.add_argument('--arquitectura', choices=['v1', 'v2'], default=None,
                        help='Nueva ejecución: v1 por defecto; v2 reduce filtros a 8/16/32.')
    parser.add_argument('--weight-decay', type=float, default=None,
                        help='Penalización Adam para ejecución nueva (por defecto 0). Al reanudar se recupera del checkpoint.')
    parser.add_argument('--device', choices=['cuda', 'cpu'], default='cuda')
    parser.add_argument('--hasta-epoca', type=int, default=50,
                        help='Pausa al guardar esa época (1–50); no cambia presupuesto ni paciencia.')
    args = parser.parse_args()
    if args.reanudar and args.arquitectura is not None:
        parser.error('Al reanudar la arquitectura se recupera del checkpoint.')
    if args.weight_decay is not None and (not math.isfinite(args.weight_decay) or args.weight_decay < 0):
        parser.error('weight-decay debe ser finito y no negativo.')
    if args.reanudar and args.weight_decay is not None:
        parser.error('No especifiques weight-decay al reanudar: se conserva el del checkpoint.')
    if not 1 <= args.hasta_epoca <= 50 or args.batch_size < 1:
        parser.error('hasta-epoca debe estar entre 1 y 50; batch-size debe ser positivo.')
    if args.perdida and (not args.nombre or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in args.nombre)):
        parser.error('Una ejecución nueva requiere --nombre con letras ASCII, números, _ o -.')
    if args.reanudar and args.nombre:
        parser.error('Al reanudar no se usa --nombre: se conserva la carpeta del checkpoint.')
    return args


def main():
    args = argumentos()  # --help no importa torch ni abre datos.
    import numpy as np
    import pandas as pd
    import torch
    from torch import nn
    from torch.utils.data import DataLoader
    from sklearn.metrics import roc_auc_score, confusion_matrix, brier_score_loss
    from models.cnn_v1 import CNNV1
    from models.cnn_v2 import CNNV2
    import utils_caso as uc

    device = torch.device(args.device)
    if device.type == 'cuda' and not torch.cuda.is_available():
        raise RuntimeError('GPU no disponible. No se cambia a CPU automáticamente.')
    fuentes = {p: huella(ROOT / p) for p in
               ['models/cnn_v1.py', 'models/cnn_v2.py', 'scripts/entrenar.py', 'utils_caso.py', 'metadata/samples.csv']}
    estado = None
    if args.reanudar:
        ruta = args.reanudar.resolve()
        if ruta.name != 'ultimo.pt':
            raise ValueError('Reanudar desde ultimo.pt; mejor.pt es solo para inferencia.')
        # Contiene estados Python/NumPy: cargar únicamente checkpoints propios.
        estado = torch.load(ruta, map_location='cpu', weights_only=False)
        if estado['fuentes'] != fuentes:
            raise ValueError('El código o los metadatos no coinciden con el checkpoint.')
        if estado['terminado']:
            raise ValueError('Esta ejecución ya terminó por paciencia o por 50 épocas.')
        config = estado['config']
        carpeta = ruta.parent
        if args.hasta_epoca <= estado['epoca']:
            raise ValueError('hasta-epoca debe superar la última época guardada.')
        print('Se conservan fold, lote y pérdida del checkpoint:', config, flush=True)
    else:
        config = {'arquitectura': 'CNNV2' if args.arquitectura == 'v2' else 'CNNV1',
                  'perdida': args.perdida, 'fold': args.fold,
                  'batch_size': args.batch_size, 'semilla': 42, 'lr': 0.001,
                  'weight_decay': args.weight_decay if args.weight_decay is not None else 0.0,
                  'max_epocas': 50, 'paciencia': 10,
                  'precision': 'float32', 'num_workers': 0}
        carpeta = ROOT / 'runs' / args.nombre
        if carpeta.exists():
            raise FileExistsError('Ese nombre ya existe; elige otro o usa --reanudar.')

    random.seed(config['semilla'])
    np.random.seed(config['semilla'])
    torch.manual_seed(config['semilla'])
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    generador = torch.Generator().manual_seed(config['semilla'])
    generador_val = torch.Generator().manual_seed(config['semilla'])
    train, val = uc.particion(uc.cargar_samples(), fold_val=config['fold'])
    for filas in [train, val]:
        if set(filas.pCR) != {0, 1} or not (filas.split == 'train').all():
            raise ValueError('Partición o clases incorrectas.')
        if (filas.groupby('patient_id').pCR.nunique() != 1).any():
            raise ValueError('Etiquetas inconsistentes por paciente.')
    peso = uc.pos_weight(train) if config['perdida'] == 'ponderada' else None
    loader = DataLoader(uc.BreastDCEDataset(train), batch_size=config['batch_size'],
                        shuffle=True, generator=generador, num_workers=0)
    validacion = DataLoader(uc.BreastDCEDataset(val), batch_size=config['batch_size'],
                            shuffle=False, generator=generador_val, num_workers=0)
    modelos = {'CNNV1': CNNV1, 'CNNV2': CNNV2}
    modelo = modelos[config['arquitectura']]().to(device)
    optimizador = torch.optim.Adam(modelo.parameters(), lr=config['lr'],
                                   weight_decay=config['weight_decay'])
    criterio = nn.BCEWithLogitsLoss(pos_weight=None if peso is None else torch.tensor(peso, device=device))
    inicio, mejor_auc, contador, mejor_epoca = 1, -math.inf, 0, None
    mejor_pesos, historial = None, []
    entorno = {'equipo': platform.node(), 'python': platform.python_version(),
               'torch': str(torch.__version__), 'numpy': np.__version__,
               'device': str(device), 'gpu': torch.cuda.get_device_name() if device.type == 'cuda' else None,
               'cuda': torch.version.cuda, 'hip': torch.version.hip}
    if estado:
        modelo.load_state_dict(estado['modelo'])
        optimizador.load_state_dict(estado['optimizador'])
        # Adam traslada sus estados a los parámetros al cargar (checkpoint leído en CPU).
        inicio = estado['epoca'] + 1
        mejor_auc, contador = estado['mejor_auc'], estado['sin_mejora']
        mejor_epoca, mejor_pesos = estado['mejor_epoca'], estado['mejor_pesos']
        historial = estado['historial']
        random.setstate(estado['rng_python'])
        np.random.set_state(estado['rng_numpy'])
        torch.set_rng_state(estado['rng_torch'])
        generador.set_state(estado['rng_loader'])
        generador_val.set_state(estado['rng_val'])
        anterior = estado['entorno']
        misma_gpu = all(anterior.get(k) == entorno.get(k) for k in ['gpu', 'torch', 'cuda', 'hip'])
        if device.type == 'cuda' and estado['rng_gpu'] is not None and misma_gpu:
            torch.cuda.set_rng_state(estado['rng_gpu'], device)
        elif device.type == 'cuda':
            torch.cuda.manual_seed_all(config['semilla'] + inicio)
            print('Cambio de plataforma: RNG GPU reiniciado; no hay identidad numérica garantizada.')
    else:
        carpeta.mkdir(parents=True, exist_ok=False)
    guardar_atomico(carpeta / 'config.json', json.dumps(
        {'config': config, 'pos_weight': peso, 'fuentes': fuentes, 'entorno': entorno},
        indent=2).encode())

    parar = False

    def solicitar_parada(signum, frame):
        nonlocal parar
        parar = True
        print('\nParada solicitada. Terminando y guardando esta época; espera la confirmación.', flush=True)

    signal.signal(signal.SIGINT, solicitar_parada)
    solicitud = carpeta / 'PARAR'
    if solicitud.exists():
        raise RuntimeError('Retira el archivo PARAR antes de comenzar o reanudar.')
    print(f'Inicio: {carpeta}\n{entorno}\nCtrl+C solicita parada al final de época.', flush=True)

    for epoca in range(inicio, args.hasta_epoca + 1):
        t0 = time.perf_counter()
        if device.type == 'cuda':
            torch.cuda.reset_peak_memory_stats()
        modelo.train()
        suma = 0.0
        for numero, (x, y) in enumerate(loader, 1):
            x, y = x.to(device), y.to(device).reshape(-1, 1)
            optimizador.zero_grad(set_to_none=True)
            loss = criterio(modelo(x), y)
            if not torch.isfinite(loss):
                raise RuntimeError('Pérdida no finita; reanudar desde la última época completa.')
            loss.backward()
            if any(p.grad is None or not torch.isfinite(p.grad).all() for p in modelo.parameters()):
                raise RuntimeError('Gradientes no finitos; esta época no se guarda.')
            optimizador.step()
            suma += loss.item() * len(x)
            if numero % 50 == 0 or numero == len(loader):
                print(f'Época {epoca}: lote {numero}/{len(loader)}', flush=True)
        modelo.eval()
        probabilidades, suma_val = [], 0.0
        with torch.no_grad():
            for x, y in validacion:
                x, y = x.to(device), y.to(device).reshape(-1, 1)
                logits = modelo(x)
                suma_val += criterio(logits, y).item() * len(x)
                probabilidades.extend(logits.sigmoid().flatten().cpu().tolist())
        if not math.isfinite(suma_val) or not np.isfinite(probabilidades).all():
            raise RuntimeError('Validación no finita; esta época no se guarda.')
        tabla = uc.agregar_por_paciente(val.patient_id, probabilidades).join(val.groupby('patient_id').pCR.first())
        auc = float(roc_auc_score(tabla.pCR, tabla.prob))
        vn, fp, fn, vp = confusion_matrix(tabla.pCR, tabla.prob >= 0.5, labels=[0, 1]).ravel()
        mejor_auc, contador, mejora, terminado = actualizar_parada(auc, mejor_auc, contador, epoca)
        if mejora:
            mejor_epoca = epoca
            mejor_pesos = {k: v.detach().cpu().clone() for k, v in modelo.state_dict().items()}
        terminado = terminado or epoca == 50
        registro = {'epoca': epoca, 'train_loss': suma / len(train), 'val_loss': suma_val / len(val),
                    'auc': auc, 'sensibilidad': float(vp / (vp + fn)),
                    'especificidad': float(vn / (vn + fp)), 'accuracy': float((vp + vn) / len(tabla)),
                    'brier': float(brier_score_loss(tabla.pCR, tabla.prob)),
                    'VP': int(vp), 'VN': int(vn), 'FP': int(fp), 'FN': int(fn),
                    'segundos': time.perf_counter() - t0, 'equipo': entorno['equipo'],
                    'memoria_max_mib': torch.cuda.max_memory_allocated() / 2**20 if device.type == 'cuda' else None}
        historial.append(registro)
        checkpoint = {'config': config, 'fuentes': fuentes, 'entorno': entorno, 'epoca': epoca,
                      'modelo': modelo.state_dict(), 'optimizador': optimizador.state_dict(),
                      'mejor_auc': mejor_auc, 'sin_mejora': contador, 'mejor_epoca': mejor_epoca,
                      'mejor_pesos': mejor_pesos, 'historial': historial, 'terminado': terminado,
                      'rng_python': random.getstate(), 'rng_numpy': np.random.get_state(),
                      'rng_torch': torch.get_rng_state(), 'rng_loader': generador.get_state(),
                      'rng_val': generador_val.get_state(),
                      'rng_gpu': torch.cuda.get_rng_state(device) if device.type == 'cuda' else None}
        buffer = io.BytesIO()
        torch.save(checkpoint, buffer)
        guardar_atomico(carpeta / 'ultimo.pt', buffer.getvalue())
        # La mejor versión también está dentro de ultimo.pt: se conserva al transportar solo este.
        buffer = io.BytesIO()
        torch.save({'modelo': mejor_pesos, 'config': config, 'epoca': mejor_epoca,
                    'auc': mejor_auc, 'fuentes': fuentes}, buffer)
        guardar_atomico(carpeta / 'mejor.pt', buffer.getvalue())
        guardar_atomico(carpeta / 'metricas.csv', pd.DataFrame(historial).to_csv(index=False).encode())
        guardar_atomico(carpeta / 'validacion_ultima.csv', tabla.to_csv().encode())
        print(f'Época {epoca} GUARDADA | train={registro["train_loss"]:.4f} '
              f'val={registro["val_loss"]:.4f} AUC={auc:.4f} | mejor={mejor_auc:.4f} '
              f'(época {mejor_epoca}) | sin mejora={contador}', flush=True)
        if epoca in [5, 10]:
            print('Punto acordado de revisión conjunta: revisa las métricas antes de seguir.', flush=True)
        if terminado or parar or solicitud.exists():
            break
    print('Ejecución detenida y checkpoint completo guardado. Ya puedes cerrar o copiar la carpeta.', flush=True)
    print(f'SHA-256 ultimo.pt: {huella(carpeta / "ultimo.pt")}', flush=True)


if __name__ == '__main__':
    main()
