"""Check numbered outputs, reader links, embedded figures and image content."""
import argparse
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
            lines = (ROOT/r['source']).read_text(encoding='utf-8').splitlines()
            assert lines[int(r['source_line'])-1] == '```{python}'
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
