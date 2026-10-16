"""Check numbered outputs, reader links, embedded figures and image content."""
import argparse
import ast
import csv
from html.parser import HTMLParser
import json
from pathlib import Path
import re

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]


class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.images = set(), []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.add(a['id'])
        if tag == 'img':
            self.images.append(a.get('src',''))


def check_code_link(root, row):
    label = f"{row['kind']} {row['number']}"
    if row['source'] != f"chapters/{row['chapter']}/chapter.qmd":
        raise ValueError(f'{label}: source does not belong to the indexed chapter')
    lines = (root/row['source']).read_text(encoding='utf-8').splitlines()
    start = int(row['source_line'])-1
    if not 0 <= start < len(lines) or lines[start] != '```{python}':
        raise ValueError(f'{label}: source link is not a Python chunk')
    heading = next((line.strip() for line in reversed(lines[:start]) if line.strip()), '')
    if not re.fullmatch(r'#{1,6}\s+'+re.escape(label+' {#'+row['anchor']+'}'), heading):
        raise ValueError(f'{label}: source link points to the wrong result heading')
    end = lines.index('```', start+1)
    code = ast.parse('\n'.join(lines[start+1:end]))
    expected_call = 'show_'+row['kind'].lower()
    if not any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
               and node.func.id == expected_call and len(node.args) > 1
               and isinstance(node.args[1], ast.Constant) and node.args[1].value == row['number']
               for node in ast.walk(code)):
        raise ValueError(f'{label}: source chunk does not emit the indexed result')
    readme = (root/'chapters'/row['chapter']/'README.md').read_text(encoding='utf-8')
    entries = [line for line in readme.splitlines()
               if re.match(r'^\|\s*'+re.escape(label)+r'\s*\|', line)]
    link = f"[Code](chapter.qmd#L{row['source_line']})"
    if len(entries) != 1 or link not in entries[0]:
        raise ValueError(f'{label}: README code link does not match the indexed result')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    all_chapters = json.loads((ROOT/'chapters.json').read_text())
    parser.add_argument('--chapters', nargs='+', choices=[x['id'] for x in all_chapters],
                        help='Check only these rendered chapters; default checks all implemented chapters.')
    args = parser.parse_args()
    with (ROOT/'results-index.csv').open(newline='',encoding='utf-8') as stream:
        rows = list(csv.DictReader(stream))
    chapters = [x for x in all_chapters if x['status']=='implemented'
                and (args.chapters is None or x['id'] in args.chapters)]
    for chapter in chapters:
        selected = [r for r in rows if r['chapter']==chapter['id']]
        folder = ROOT/'output'/chapter['id']
        text = (folder/'chapter.html').read_text(encoding='utf-8')
        doc = Document()
        doc.feed(text)
        assert 'Traceback (most recent call last)' not in text
        assert len(doc.images) >= sum(r['kind']=='Figure' for r in selected)
        assert all(s.startswith('data:image/') for s in doc.images), 'Report has external image dependencies'
        for r in selected:
            assert r['anchor'] in doc.ids, r['anchor']
            assert (ROOT/r['output']).is_file(), r['output']
            check_code_link(ROOT, r)
        readme = (ROOT/'chapters'/chapter['id']/'README.md').read_text()
        assert '[Report]' not in readme and '[Output]' not in readme
        assert len(re.findall(r'\[Code\]\(',readme)) == len(selected)
        figures = [ROOT/r['output'] for r in selected if r['kind']=='Figure']
        if chapter['id']=='00-foundations':
            figures = [folder/'figures'/f'figure-foundations-{name}.png' for name in ['loss','normal']]
            assert all(p.is_file() for p in figures)
        review = ROOT/'.local'/f"{chapter['id']}-visual-review"
        review.mkdir(parents=True,exist_ok=True)
        for start in range(0,len(figures),4):
            sheet = Image.new('RGB',(1600,1200),'#dddddd')
            draw = ImageDraw.Draw(sheet)
            for j,file in enumerate(figures[start:start+4]):
                im = Image.open(file).convert('RGB')
                assert min(im.size)>200
                assert np.asarray(im).std()>5, f'Blank image: {file}'
                im.thumbnail((770,555))
                x,y=(j%2)*800,(j//2)*600
                draw.text((x+15,y+8),file.stem,fill='black')
                sheet.paste(im,(x+(800-im.width)//2,y+35))
            sheet.save(review/f'contact-{start//4+1:02}.png')
        print(f"{chapter['id']}: {len(selected)} numbered outputs, {len(figures)} nonblank figures, all code links and HTML anchors pass.")


if __name__ == '__main__':
    main()
