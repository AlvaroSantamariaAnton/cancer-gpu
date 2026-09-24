"""Verifica archivos y decodificación; no calcula métricas ni analiza etiquetas test."""
import csv
import json
from pathlib import Path, PurePosixPath
import sys
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

def main():
    with (ROOT / 'metadata/samples.csv').open(encoding='utf-8') as handle:
        rows = list(csv.DictReader(handle))
    paths = [row[key] for row in rows for key in ['path_pre', 'path_early', 'path_late']]
    errors = []
    for index, rel in enumerate(paths, 1):
        try:
            path = PurePosixPath(rel)
            if path.is_absolute() or '..' in path.parts or path.parts[0] != 'dataset':
                raise ValueError('Ruta fuera de dataset')
            with Image.open(ROOT / rel) as image:
                if image.format != 'PNG' or image.mode != 'L' or image.size != (256, 256):
                    raise ValueError(f'Formato inesperado: {image.format}, {image.mode}, {image.size}')
                image.load()
        except Exception as exc:
            errors.append({'ruta': rel, 'error': str(exc)})
        if index % 5000 == 0:
            print(f'{index}/{len(paths)} verificadas', flush=True)
    summary = {'cortes': len(rows), 'pacientes': len({r['patient_id'] for r in rows}),
               'imagenes_esperadas': len(paths), 'rutas_duplicadas': len(paths) - len(set(paths)),
               'archivos_png_presentes': sum(1 for _ in (ROOT / 'dataset').rglob('*.png')),
               'imagenes_validas': len(paths) - len(errors), 'errores': errors}
    dest = ROOT / 'reports/local/dataset.json'
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k != 'errores'}, indent=2))
    print(f'Errores: {len(errors)}. Informe: {dest}')
    return int(bool(errors) or summary['rutas_duplicadas'] != 0)

if __name__ == '__main__':
    sys.exit(main())
