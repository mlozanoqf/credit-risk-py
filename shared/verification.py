"""Frozen-input, source-freshness and pinned-environment regression checks."""
import csv
import hashlib
import json
import math
from pathlib import Path


def check_inputs(root):
    with (root/'data/input-checksums.csv').open(encoding='utf-8-sig') as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        path = root/row['path']
        if not path.is_file():
            raise FileNotFoundError(f'Missing reference input: {row["path"]}')
        if hashlib.md5(path.read_bytes()).hexdigest() != row['md5']:
            raise ValueError(f'Reference input checksum mismatch: {row["path"]}')
    return len(rows)


def source_hashes(root):
    files = [root/p for p in ('run.py','_quarto.yml','chapters.json','results-index.csv',
                              'requirements-lock.txt','data/input-checksums.csv')]
    for folder in ('chapters','shared'):
        files += [p for p in (root/folder).rglob('*') if p.suffix in ('.py','.qmd')]
    return {p.relative_to(root).as_posix(): hashlib.sha256(
        p.read_bytes().replace(b'\r\n',b'\n')).hexdigest() for p in sorted(files)}


def required_outputs(root, chapter):
    out = root/'output'/chapter
    with (root/'results-index.csv').open(encoding='utf-8-sig') as handle:
        rows = list(csv.DictReader(handle))
    paths = [root/r['output'] for r in rows if r['chapter']==chapter]
    paths += [out/'numeric-results.json',out/'chapter.html']
    if chapter == '00-foundations':
        paths += [out/'figures'/f'figure-foundations-{name}.png' for name in ('loss','normal')]
    return paths


def output_fingerprint(path):
    return {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'mtime_ns': path.stat().st_mtime_ns}


def complete_run(root, chapter, started, before):
    after = source_hashes(root)
    if after != before:
        raise RuntimeError('Sources changed during rendering; rerun the chapter.')
    paths = required_outputs(root, chapter)
    for p in paths:
        if not p.is_file() or p.stat().st_mtime < started-2:
            raise RuntimeError(f'Missing or stale output from this run: {p}')
    outputs = {p.relative_to(root).as_posix(): output_fingerprint(p) for p in paths}
    (root/'output'/chapter/'run-manifest.json').write_text(
        json.dumps({'sources':after,'started':started,'outputs':outputs},indent=2), encoding='utf-8')
    return len(paths)


def check_freshness(root, chapter):
    manifest = root/'output'/chapter/'run-manifest.json'
    if not manifest.is_file():
        raise ValueError(f'{chapter}: run the chapter through run.py before verification.')
    recorded = json.loads(manifest.read_text(encoding='utf-8'))
    if recorded['sources'] != source_hashes(root):
        raise ValueError(f'{chapter}: source files changed after rendering; rerun the chapter.')
    paths = required_outputs(root, chapter)
    outputs = recorded.get('outputs', {})
    if set(outputs) != {p.relative_to(root).as_posix() for p in paths}:
        raise ValueError(f'{chapter}: missing or incomplete output fingerprints; rerun the chapter.')
    for p in paths:
        if not p.is_file() or output_fingerprint(p) != outputs[p.relative_to(root).as_posix()]:
            raise ValueError(f'{chapter}: output changed or missing after rendering: {p}; rerun the chapter.')


def check_numeric(actual, cases):
    for case in cases:
        value = actual
        for key in case['path']:
            value = value[int(key)] if isinstance(value,list) else value[key]
        values = value if isinstance(value,list) else [value]
        expected = case['expected']
        if len(values)!=len(expected) or not all(
                math.isfinite(float(a)) and math.isclose(float(a),float(b),
                abs_tol=case['atol'],rel_tol=case['rtol']) for a,b in zip(values,expected)):
            raise ValueError(f'Numeric reference mismatch: {case["path"]}')
    return len(cases)
