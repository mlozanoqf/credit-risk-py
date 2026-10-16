"""Render one implemented chapter in a fresh Quarto/Jupyter process."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


def main():
    root = Path(__file__).resolve().parent
    chapters = {x['id']: x for x in json.loads((root / 'chapters.json').read_text())}
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('chapter', choices=chapters)
    args = parser.parse_args()
    chapter = chapters[args.chapter]
    if chapter['status'] != 'implemented':
        parser.error(f'{args.chapter} is planned and has not been implemented yet.')
    if args.chapter in ('01-logistic', '02-tree-based'):
        required = ['credit_scoring.rds', 'reference-split.csv']
        missing = [name for name in required
                   if not (root / 'data' / 'credit-scoring' / name).is_file()]
        if missing:
            parser.error('Chapters 1-2 require the supplied input files: '
                         + ', '.join(missing)
                         + '. These files are supplied in the complete repository checkout. '
                         'See data/credit-scoring/README.md. No data will be downloaded.')
    quarto = shutil.which('quarto')
    if not quarto:
        parser.error('Install Quarto and put its executable on PATH.')
    env = dict(os.environ, QUARTO_PYTHON=sys.executable, PYTHONHASHSEED='0')
    from shared.verification import check_inputs, source_hashes, complete_run
    check_inputs(root)
    before = source_hashes(root)
    started = time.time()
    manifest = root/'output'/args.chapter/'run-manifest.json'
    if manifest.exists():
        manifest.unlink()
    subprocess.run([quarto, 'render', chapter['source'], '--to', 'html'],
                   cwd=root, env=env, check=True)
    report = root / Path(chapter['source']).with_suffix('.html')
    destination = root / 'output' / args.chapter / 'chapter.html'
    shutil.copy2(report, destination)
    count = complete_run(root, args.chapter, started, before)
    print(f'Complete: {destination}\nVerified and fingerprinted {count} fresh output files.')


if __name__ == '__main__':
    main()
