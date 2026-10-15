"""Rebuild reader indexes from the frozen result metadata and current QMD lines."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    with (ROOT / 'reference-results.csv').open(encoding='utf-8-sig', newline='') as stream:
        reference = list(csv.DictReader(stream))
    chapters = json.loads((ROOT / 'chapters.json').read_text())
    result_rows = []
    for chapter in chapters:
        folder = ROOT / 'chapters' / chapter['id']
        folder.mkdir(parents=True, exist_ok=True)
        intro = f"# {chapter['title']}\n\n"
        if chapter['status'] != 'implemented':
            intro += ('Planned Python implementation. The R companion is the reference.\n'
                      'This chapter is not yet executable in Python.\n')
            if chapter['id'] in ('01-logistic', '02-tree-based'):
                intro += '\nSee the scoring data provenance and availability note.\n'
            (folder / 'README.md').write_text(intro, encoding='utf-8')
            continue
        intro += (f"From the project root: `python run.py {chapter['id']}`.\n\n"
                  'Open [chapter.qmd](chapter.qmd) to read or edit the calculations.\n'
                  'Execute in source order. [Results](../../README.md#results) are created locally.\n\n'
                  '## Find code by book result\n\n| Result | Title | Code |\n|---|---|---|\n')
        if chapter['id'] in ('01-logistic','02-tree-based'):
            intro = intro.replace('## Find code by book result',
                '**Frozen data included.** The complete private checkout supplies the RDS and reference split, '
                'with a source and modification notice. No R session is required.\n\n## Find code by book result')
        lines = (ROOT / chapter['source']).read_text(encoding='utf-8').splitlines()
        for row in [r for r in reference if r['chapter'] == chapter['id']]:
            marker = '{#' + row['anchor'] + '}'
            heading = next(i for i, line in enumerate(lines) if marker in line)
            block = next(i for i in range(heading+1, len(lines)) if lines[i] == '```{python}')
            row = dict(row)
            if chapter['id']=='02-tree-based' and row['kind']=='Table':
                row['title'] = {'2.9':'First two XGBoost rounds: code values and algebraic updates.',
                                '2.10':'First five XGBoost rounds for the selected applicant.'}.get(row['number'],row['title'])
            if chapter['id']=='05-copulas' and row['kind']=='Table' and row['number']=='5.17':
                row['title'] = 'Mapping the Credit VaR notation to the Python implementation.'
            row['source_line'] = block+1
            if row['kind'] == 'Figure':
                row['output'] = f"output/{chapter['id']}/figures/figure-{row['number'].replace('.', '-')}.png"
            result_rows.append(row)
            title = row['title'].replace('|', '\\|')
            intro += f"| {row['kind']} {row['number']} | {title} | [Code](chapter.qmd#L{block+1}) |\n"
        (folder / 'README.md').write_text(intro, encoding='utf-8')
    with (ROOT / 'results-index.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=reference[0].keys())
        writer.writeheader()
        writer.writerows(result_rows)
    print(f'Indexed {len(result_rows)} implemented results; {len(reference)} in full planned scope.')


if __name__ == '__main__':
    main()
