"""Instala las dependencias versionadas dentro del entorno Conda cancer."""
import argparse
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--equipo', choices=['casa', 'universidad'], required=True)
    parser.add_argument('--instalar-torch', action='store_true',
                        help='Instalar la variante de PyTorch fijada para este equipo.')
    args = parser.parse_args()
    if sys.version_info[:2] != (3, 12):
        parser.error('Activa primero cancer con Python 3.12.')
    prefix = Path(sys.prefix).resolve()
    if not (prefix / 'conda-meta').is_dir() or prefix.name != 'cancer':
        parser.error('Ejecuta este script dentro del entorno Conda cancer.')
    expected = 'Windows' if args.equipo == 'casa' else 'Linux'
    if platform.system() != expected:
        parser.error(f'El perfil {args.equipo} requiere {expected}.')
    if not args.instalar_torch:
        try:
            import torch
            import torchvision
        except ImportError:
            parser.error('Falta PyTorch; usa --instalar-torch tras revisar el perfil.')
        expected_backend = torch.version.cuda if args.equipo == 'casa' else torch.version.hip
        if not expected_backend:
            parser.error('La variante de PyTorch instalada no corresponde a este equipo.')
        requirements = (ROOT / f'requirements/torch-{args.equipo}.txt').read_text()
        for name, version in [('torch', torch.__version__), ('torchvision', torchvision.__version__)]:
            if f'{name}=={version.split("+")[0]}' not in requirements.splitlines():
                parser.error(f'{name} {version} no coincide con el perfil. Guarda el diagnóstico y revisa antes de actualizar.')
    def pip(*extra):
        subprocess.run([sys.executable, '-m', 'pip', *extra], check=True, cwd=ROOT)
    if args.instalar_torch:
        pip('install', '-r', str(ROOT / f'requirements/torch-{args.equipo}.txt'),
            '-c', str(ROOT / 'requirements.txt'))
    pip('install', '-r', str(ROOT / 'requirements.txt'))
    pip('check')
    subprocess.run([sys.executable, str(ROOT / 'scripts/diagnostico_entorno.py'),
                    '--equipo', args.equipo, '--probar-gpu'], check=True, cwd=ROOT)
    subprocess.run([sys.executable, '-c',
                    'import numpy, pandas, PIL, matplotlib, sklearn, requests; '
                    'print("OK: importaciones de las bibliotecas compartidas")'], check=True, cwd=ROOT)

if __name__ == '__main__':
    main()
