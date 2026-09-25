"""Auditoría de metadatos y figuras de train, sin modificar el dataset."""
from pathlib import Path
import hashlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
FASES = ('PRE', 'EARLY', 'LATE')


def cargar(raiz=ROOT):
    raiz = Path(raiz)
    return (pd.read_csv(raiz / 'metadata/patients.csv'),
            pd.read_csv(raiz / 'metadata/samples.csv'))


def auditar(p, s, raiz=ROOT):
    """Test solo participa en controles estructurales, nunca en figuras/resúmenes de clase."""
    checks = {}
    checks['pid únicos'] = not p.pid.duplicated().any()
    checks['sample_id únicos'] = not s.sample_id.duplicated().any()
    checks['paciente/corte únicos'] = not s.duplicated(['patient_id', 'slice_index']).any()
    checks['samples sin nulos'] = not s.isna().any().any()
    checks['claves pacientes completas'] = not p[['pid', 'split', 'pCR', 'dataset']].isna().any().any()
    checks['relación pacientes/muestras completa'] = set(p.pid) == set(s.patient_id)
    checks['etiquetas binarias'] = p.pCR.isin([0, 1]).all() and s.pCR.isin([0, 1]).all()
    checks['splits válidos'] = p.split.isin(['train', 'test']).all() and s.split.isin(['train', 'test']).all()
    checks['split/fold/etiqueta constantes por paciente'] = s.groupby('patient_id')[['split', 'fold', 'pCR']].nunique(dropna=False).eq(1).all().all()
    checks['folds válidos'] = s.loc[s.split.eq('train'), 'fold'].isin(range(5)).all() and s.loc[s.split.eq('test'), 'fold'].eq(-1).all()
    if checks['pid únicos']:
        j = s.merge(p[['pid', 'pCR', 'split']], left_on='patient_id', right_on='pid', how='left', validate='many_to_one', suffixes=('_s', '_p'))
        checks['coinciden etiqueta y split entre CSV'] = j.pCR_s.eq(j.pCR_p).all() and j.split_s.eq(j.split_p).all()
    else:
        checks['coinciden etiqueta y split entre CSV'] = False
    checks['índices enteros no negativos'] = s.slice_index.ge(0).all() and s.slice_index.mod(1).eq(0).all()
    checks['identificador coherente con índice'] = s.sample_id.eq(s.patient_id + '_z' + s.slice_index.map(lambda x: f'{int(x):03d}' if pd.notna(x) else '?')).all()
    paths = []
    for fase in FASES:
        col = 'path_' + fase.lower()
        expected = 'dataset/' + s.split + '/' + s.patient_id + '/' + s.sample_id + '_' + fase + '.png'
        checks[f'rutas {fase} coherentes'] = s[col].eq(expected).all()
        paths.extend(s[col].dropna())
    checks['rutas únicas'] = len(paths) == len(set(paths))
    checks['rutas presentes y dentro de dataset'] = all(
        (Path(raiz) / v).resolve().is_relative_to((Path(raiz) / 'dataset').resolve())
        and (Path(raiz) / v).is_file() for v in paths)
    return pd.Series({k: bool(v) for k, v in checks.items()}, name='correcto')


def tablas_train(p, s):
    t = s.loc[s.split.eq('train')].copy()
    pt = p.loc[p.split.eq('train')].copy()
    folds = t[['patient_id', 'fold']].drop_duplicates()
    pt = pt.merge(folds, left_on='pid', right_on='patient_id', validate='one_to_one')
    tables = {}
    for nombre, df in [('pacientes', pt), ('cortes', t)]:
        tables['clases_' + nombre] = df.groupby('pCR').size().rename('n').to_frame()
        tables['clases_' + nombre]['porcentaje'] = 100 * tables['clases_' + nombre].n / len(df)
        tables['folds_' + nombre] = pd.crosstab(df.fold, df.pCR).reindex(columns=[0, 1], fill_value=0)
    tables['cohortes_pacientes'] = pd.crosstab(pt.dataset, pt.pCR).reindex(columns=[0, 1], fill_value=0)
    cortes_cohorte = t.merge(pt[['pid', 'dataset']], left_on='patient_id', right_on='pid', validate='many_to_one')
    tables['cohortes_cortes'] = pd.crosstab(cortes_cohorte.dataset, cortes_cohorte.pCR)
    counts = t.groupby('patient_id').size()
    tables['cortes_por_paciente'] = counts.value_counts().sort_index().rename_axis('cortes').to_frame('pacientes')
    tables['nulos_clinicos'] = pt.isna().sum().loc[lambda x: x.gt(0)].to_frame('nulos')
    tables['nulos_por_cohorte'] = pt.groupby('dataset')[list(p.columns)].agg(lambda x: x.isna().sum())
    ranges = t.groupby('patient_id').slice_index.agg(['min', 'max']).merge(pt, left_index=True, right_on='pid')
    ranges['dentro'] = ranges['min'].ge(ranges.mask_start) & ranges['max'].le(ranges.mask_end)
    tables['rangos_originales_no_filtrar'] = ranges.groupby('dataset').dentro.agg(['sum', 'count'])
    return tables


def leer_train(fila, raiz=ROOT):
    if fila['split'] != 'train':
        raise ValueError('Este explorador solo admite ejemplos de train.')
    planos = []
    for fase in FASES:
        with Image.open(Path(raiz) / fila['path_' + fase.lower()]) as im:
            if im.mode != 'L' or im.size != (256, 256):
                raise ValueError('Imagen fuera del formato esperado.')
            planos.append(np.asarray(im, dtype=np.float32) / 255.)
    return np.stack(planos)


def ejemplos_train(p, s):
    """Primer pid ordenado de cada cohorte/clase; corte mediano de los disponibles.

    Selección determinista para inspección, no muestra representativa ni aleatoria.
    """
    rows = []
    for _, grupo in p[p.split.eq('train')].groupby(['dataset', 'pCR'], sort=True):
        pid = sorted(grupo.pid)[0]
        cortes = s[(s.split == 'train') & (s.patient_id == pid)].sort_values('slice_index')
        rows.append(cortes.iloc[len(cortes) // 2])
    return pd.DataFrame(rows).merge(p[['pid', 'dataset']], left_on='patient_id', right_on='pid', validate='many_to_one')


def figura_fases(ejemplos, raiz=ROOT):
    fig, axes = plt.subplots(len(ejemplos), 4, figsize=(12, 3 * len(ejemplos)), squeeze=False, layout='constrained')
    stats = []
    for axes_row, (_, row) in zip(axes, ejemplos.iterrows()):
        arr = leer_train(row, raiz)
        for ax, phase, data in zip(axes_row, FASES, arr):
            ax.imshow(data, cmap='gray', vmin=0, vmax=1)
            ax.set_title(phase)
            ax.axis('off')
            stats.append({'sample_id': row.sample_id, 'cohorte': row.dataset, 'fase': phase,
                          'min': float(data.min()), 'max': float(data.max()), 'media_imagen': float(data.mean())})
        diff = arr[1] - arr[0]
        im = axes_row[3].imshow(diff, cmap='RdBu_r', vmin=-1, vmax=1)
        axes_row[3].set_title('EARLY − PRE'); axes_row[3].axis('off')
        axes_row[0].set_title(f'{row.dataset} | pCR={row.pCR}\n{row.sample_id}\nPRE', fontsize=9)
    fig.colorbar(im, ax=axes[:, 3], shrink=.6, label='Diferencia de intensidad (escala fija)')
    fig.suptitle('Ejemplos de train: tres fases temporales y realce', fontsize=15)
    return fig, pd.DataFrame(stats)


def figura_paciente(s, pid, raiz=ROOT):
    rows = s[(s.split == 'train') & (s.patient_id == pid)].sort_values('slice_index')
    if rows.empty:
        raise ValueError('Paciente ausente de train.')
    fig, axes = plt.subplots(int(np.ceil(len(rows) / 5)), 5, figsize=(14, 6), squeeze=False, layout='constrained')
    for ax in axes.flat:
        ax.axis('off')
    for ax, (_, row) in zip(axes.flat, rows.iterrows()):
        ax.imshow(leer_train(row, raiz)[1], cmap='gray', vmin=0, vmax=1)
        ax.set_title(f'z={row.slice_index}')
    fig.suptitle(f'{pid} | EARLY | cortes ordenados, no instantes temporales')
    return fig


def figura_clases(tables):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), layout='constrained')
    for ax, key, title in zip(axes, ['cohortes_pacientes', 'folds_pacientes'], ['Cohortes de train', 'Folds de train']):
        table = tables[key]
        table.plot.bar(stacked=True, ax=ax, color=['#325c80', '#dc9c36'], rot=0)
        ax.set_title(title); ax.set_ylabel('Pacientes'); ax.legend(['pCR=0', 'pCR=1'])
    return fig


def huellas(raiz=ROOT):
    return {name: hashlib.sha256((Path(raiz) / 'metadata' / name).read_bytes()).hexdigest()
            for name in ['patients.csv', 'samples.csv']}
