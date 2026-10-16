"""Audit Git candidate files for unexpected artifacts and local-only dependencies.

This is a technical safeguard, not clearance of third-party data rights.
It reads the Git index and unignored files without staging or publishing them.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from shared.verification import check_inputs
SCORING_FILES = {
    'data/credit-scoring/credit_scoring.rds',
    'data/credit-scoring/reference-split.csv',
}
DATA_FILES = {
    'data/climate/ngfs_climacred_global_raw.csv',
    'data/climate/ngfs_climacred_daps_raw.csv',
    'data/climate/ngfs_climacred_download_manifest.csv',
    'data/credit-spreads/corporate-bond-snapshot.csv',
    'data/credit-spreads/corporate-treasury-curve.csv',
    'data/input-checksums.csv',
}
FORBIDDEN_PARTS = {'.local', '.venv', '.quarto', '__pycache__', 'output',
                   'publication', 'contracts', 'exercises', 'solutions', '.github'}
SECRET_PATTERNS = [r'github_pat_[A-Za-z0-9_]{30,}', r'gh[pousr]_[A-Za-z0-9]{30,}',
                   r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
                   r'AKIA[A-Z0-9]{16}']


def git(*args):
    return subprocess.run(['git', '-c', f'safe.directory={ROOT.as_posix()}', *args],
                          cwd=ROOT, capture_output=True, text=True, check=True).stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    allowed_scoring = SCORING_FILES
    candidates = sorted(set(git('ls-files', '--cached', '--others', '--exclude-standard', '-z').split('\0'))-{''})
    problems, manifest = [], []
    try:
        check_inputs(ROOT)
    except (ValueError, FileNotFoundError) as exc:
        problems.append(str(exc))
    for name in candidates:
        path = ROOT/name
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()):
            problems.append(f'External link: {name}')
            continue
        if FORBIDDEN_PARTS.intersection(Path(name).parts):
            problems.append(f'Local/private/generated directory: {name}')
        if name.startswith('data/credit-scoring/') and name not in allowed_scoring | {
                'data/credit-scoring/README.md', 'data/credit-scoring/PROVENANCE.md'}:
            problems.append(f'Unexpected scoring artifact: {name}')
        if path.suffix.lower() in {'.rds', '.rdata', '.npz', '.npy', '.ubj', '.pkl', '.pdf', '.docx', '.zip', '.html', '.ipynb'} and name not in allowed_scoring:
            problems.append(f'Unexpected binary or generated artifact: {name}')
        if name.startswith('data/') and path.suffix == '.csv' and name not in DATA_FILES | allowed_scoring:
            problems.append(f'Unreviewed input file: {name}')
        content = path.read_bytes()
        manifest.append({'path': name, 'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest()})
        if name == 'data/credit-scoring/credit_scoring.rds' and name in allowed_scoring:
            if hashlib.md5(content).hexdigest() != '1fbea5f14ec0c0174a946e010540b02f':
                problems.append('Scoring dataset differs from the approved frozen input.')
            continue
        if name == 'data/credit-scoring/reference-split.csv' and name in allowed_scoring:
            if hashlib.sha256(content).hexdigest() != 'a1fcea73deeea768a5d85050b701433140ef6be1293abaa04155e520fe36803c':
                problems.append('Scoring split differs from the approved reference.')
        try:
            text = content.decode('utf-8-sig')
        except UnicodeDecodeError:
            problems.append(f'Unexpected non-text content: {name}')
            continue
        for pattern in SECRET_PATTERNS:
            if re.search(pattern, text):
                problems.append(f'Credential pattern requires review: {name}')
        if path.suffix in {'.py', '.qmd', '.yml', '.R'} and re.search(r'[A-Za-z]:[\\/]Users[\\/]', text):
            problems.append(f'Personal absolute path: {name}')
        if path.suffix == '.md':
            for target in re.findall(r'\[[^\]]*\]\(([^\s)]+)\)', text):
                if '://' in target or target.startswith(('#', 'mailto:')):
                    continue
                local = unquote(target.split('#')[0])
                if local and not (path.parent/local).exists():
                    problems.append(f'Broken relative document link: {name} -> {target}')
    for name in ('output/01-logistic/chapter.html', '.local/scoring-reference.json'):
        result = subprocess.run(['git', '-c', f'safe.directory={ROOT.as_posix()}', 'check-ignore', '-q', '--no-index', name], cwd=ROOT)
        if result.returncode != 0:
            problems.append(f'Missing exclusion: {name}')
    reader_code = [p for p in candidates if p.startswith(('chapters/', 'shared/')) and Path(p).suffix in {'.py', '.qmd'}]
    for name in reader_code:
        text = (ROOT/name).read_text(encoding='utf-8')
        if re.search(r'Rscript|rpy2|\.local[/\\]|credit-risk-r[/\\]', text):
            problems.append(f'Reader code has maintainer/R dependency: {name}')
    index = list(csv.DictReader(io.StringIO((ROOT/'results-index.csv').read_text(encoding='utf-8-sig'))))
    for row in index:
        source = ROOT/row['source']
        if source.read_text(encoding='utf-8').splitlines()[int(row['source_line'])-1] != '```{python}':
            problems.append(f'Stale result link: {row["number"]}')
    refs = git('for-each-ref', '--format=%(refname)').splitlines()
    for name in SCORING_FILES:
        if name not in candidates:
            problems.append(f'Missing reference input: {name}')
    # Review history as well as the current candidate; keep private authoring
    # materials out even after their deletion from the working tree.
    for entry in git('rev-list', '--objects', '--all').splitlines():
        parts = entry.split(' ', 1)
        if len(parts) != 2:
            continue
        name = parts[1]
        if FORBIDDEN_PARTS.intersection(Path(name).parts):
            problems.append(f'Forbidden historical artifact: {name}')
    report = {'candidate_files': len(candidates), 'numbered_results': len(index),
              'remote_configured': bool(git('remote').strip()), 'git_refs': refs,
              'problems': problems, 'files': manifest,
              'scope': 'Technical content audit; source data terms require separate review.',
              'reference_scoring_inputs': sorted(SCORING_FILES)}
    (ROOT/'.local').mkdir(exist_ok=True)
    (ROOT/'.local/release-audit.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({key: value for key, value in report.items() if key != 'files'}, indent=2))
    if problems:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
