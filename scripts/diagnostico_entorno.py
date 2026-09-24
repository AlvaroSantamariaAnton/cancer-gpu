"""Registra versiones y prueba una operación convolucional; no define la CNN del trabajo."""
import argparse
from datetime import datetime, timezone
from importlib import metadata
import json
import os
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--equipo', choices=['casa', 'universidad'], required=True)
    parser.add_argument('--probar-gpu', action='store_true')
    args = parser.parse_args()
    report = {'fecha_utc': datetime.now(timezone.utc).isoformat(), 'equipo': args.equipo,
              'sistema': platform.platform(), 'python': platform.python_version(),
              'paquetes': {}, 'hsa_override': os.getenv('HSA_OVERRIDE_GFX_VERSION'),
              'prueba_gpu': 'no solicitada'}
    for package in ['torch', 'torchvision', 'numpy', 'scipy', 'pandas', 'Pillow', 'matplotlib', 'scikit-learn', 'requests']:
        try:
            report['paquetes'][package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            report['paquetes'][package] = None
    failed = False
    try:
        import torch
        report.update(cuda=torch.version.cuda, hip=torch.version.hip,
                      gpu_disponible=torch.cuda.is_available())
        if torch.cuda.is_available():
            info = torch.cuda.get_device_properties(0)
            report.update(gpu=info.name, vram_bytes=info.total_memory)
        if args.probar_gpu:
            if not torch.cuda.is_available():
                raise RuntimeError('PyTorch no puede utilizar la GPU.')
            if args.equipo == 'casa' and not torch.version.cuda:
                raise RuntimeError('Se esperaba CUDA en casa.')
            if args.equipo == 'universidad' and not torch.version.hip:
                raise RuntimeError('Se esperaba ROCm/HIP en universidad.')
            # Operación sintética pequeña para comprobar GPU y gradientes, sin entrenar un modelo.
            x = torch.randn(2, 3, 32, 32, device='cuda', requires_grad=True)
            kernel = torch.randn(4, 3, 3, 3, device='cuda', requires_grad=True)
            output = torch.nn.functional.conv2d(x, kernel)
            output.square().mean().backward()
            torch.cuda.synchronize()
            if not torch.isfinite(output).all() or not torch.isfinite(kernel.grad).all():
                raise RuntimeError('La operación produjo valores no finitos.')
            report['prueba_gpu'] = 'OK: convolución y backward'
    except Exception as exc:
        report['error'] = str(exc)
        failed = True
    dest = ROOT / 'reports/local' / f'entorno-{args.equipo}.json'
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f'Informe: {dest}')
    return int(failed)

if __name__ == '__main__':
    sys.exit(main())
