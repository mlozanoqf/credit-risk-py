"""Rebuild reader indexes without replacing chapter introductions or data notices."""
import csv
import io
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def update_readme(path, rows):
    original = path.read_bytes()
    text = original.decode('utf-8')
    newline = '\r\n' if '\r\n' in text else '\n'
    pattern = r'^\| Result \| Title \| Code \|\r?\n\|---\|---\|---\|\r?\n(?:\|[^\r\n]*\|\r?\n)*'
    matches = list(re.finditer(pattern, text, re.MULTILINE))
    if len(matches) != 1:
        raise ValueError(f'Expected one result table in {path}')
    table = ['| Result | Title | Code |', '|---|---|---|']
    for row in rows:
        title = row['title'].replace('|', '\\|')
        table.append(f"| {row['kind']} {row['number']} | {title} | "
                     f"[Code](chapter.qmd#L{row['source_line']}) |")
    match = matches[0]
    updated = (text[:match.start()] + newline.join(table) + newline +
               text[match.end():]).encode('utf-8')
    if path.read_bytes() != original:
        raise RuntimeError(f'{path} changed during the rebuild; rerun it')
    if updated != original:
        path.write_bytes(updated)


def write_index(path, rows, fields):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    updated = stream.getvalue().encode('utf-8')
    if path.read_bytes() != updated:
        path.write_bytes(updated)


def main():
    with (ROOT / 'reference-results.csv').open(encoding='utf-8-sig', newline='') as stream:
        reference = list(csv.DictReader(stream))
    chapters = json.loads((ROOT / 'chapters.json').read_text())
    result_rows = []
    for chapter in chapters:
        folder = ROOT / 'chapters' / chapter['id']
        if chapter['status'] != 'implemented':
            continue
        lines = (ROOT / chapter['source']).read_text(encoding='utf-8').splitlines()
        chapter_rows = [r for r in reference if r['chapter'] == chapter['id']]
        for row in chapter_rows:
            marker = '{#' + row['anchor'] + '}'
            headings = [i for i, line in enumerate(lines) if marker in line]
            if len(headings) != 1:
                raise ValueError(f'Expected one {marker} in {chapter["source"]}')
            heading = headings[0]
            end = next((i for i in range(heading+1, len(lines))
                        if '{#result-' in lines[i]), len(lines))
            block = next((i for i in range(heading+1, end)
                          if lines[i] == '```{python}'), None)
            if block is None or row['source'] != chapter['source']:
                raise ValueError(f'Invalid source target for {marker}')
            row['source_line'] = block+1
            if row['kind'] == 'Figure':
                row['output'] = f"output/{chapter['id']}/figures/figure-{row['number'].replace('.', '-')}.png"
            result_rows.append(row)
        if chapter_rows:
            update_readme(folder / 'README.md', chapter_rows)
    write_index(ROOT / 'reference-results.csv', reference, reference[0].keys())
    write_index(ROOT / 'results-index.csv', result_rows, reference[0].keys())
    print(f'Indexed {len(result_rows)} implemented results; {len(reference)} in full planned scope.')


if __name__ == '__main__':
    main()
