"""Verify inputs, book-result navigation, fresh outputs and numerical references."""
import csv
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from shared.verification import check_inputs, check_freshness, check_numeric


def main():
    print(f'Inputs: {check_inputs(ROOT)} frozen files match.')
    with (ROOT/'results-index.csv').open(encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    with (ROOT/'checks/book-results.csv').open(encoding='utf-8-sig') as f:
        book = list(csv.DictReader(f))
    actual = {(r['kind'],r['number']):r['book_id'] for r in rows}
    expected = {(r['kind'],r['number']):r['book_id'] for r in book}
    if len(actual)!=len(rows) or actual!=expected:
        raise ValueError('Book/result numbering changed; review the reference index.')
    titles = {r['book_id']:r['companion_title'] for r in book}
    for row in rows:
        if row['title'] != titles[row['book_id']]:
            raise ValueError(f'Stale result title: {row["book_id"]}')
        readme = (ROOT/'chapters'/row['chapter']/'README.md').read_text(encoding='utf-8')
        if f"(chapter.qmd#L{row['source_line']})" not in readme:
            raise ValueError(f'Stale README code link: {row["book_id"]}')
    subprocess.run([sys.executable,str(ROOT/'checks/check_outputs.py')],cwd=ROOT,check=True)
    reference = json.loads((ROOT/'checks/numeric-reference.json').read_text())
    count = 0
    for chapter in json.loads((ROOT/'chapters.json').read_text()):
        cid = chapter['id']
        check_freshness(ROOT,cid)
        values = json.loads((ROOT/'output'/cid/'numeric-results.json').read_text())
        n = check_numeric(values,reference['chapters'][cid])
        count += n
        print(f'{cid}: fresh output; {n} numerical reference checks passed.')
    print(f'PASS: {len(rows)} book results and {count} pinned-environment numerical checks.')


if __name__=='__main__':
    main()
