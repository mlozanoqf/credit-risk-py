"""Save independently computed Python results; never load R outputs here."""
import csv
import importlib.metadata
import json
import platform
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import Markdown, display

BLUE, RED, GREEN = '#0072B2', '#B22222', '#009E73'


def setup(chapter):
    root = Path.cwd()
    if not (root / 'chapters.json').is_file():
        raise RuntimeError('Run from the project root using python run.py <chapter>.')
    out = root / 'output' / chapter
    for part in ('figures', 'tables'):
        (out / part).mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'figure.figsize': (7, 4.5), 'figure.dpi': 120,
                         'font.size': 10, 'axes.spines.top': False,
                         'axes.spines.right': False, 'legend.frameon': False,
                         'savefig.dpi': 160, 'axes.prop_cycle': plt.cycler(
                             color=[BLUE, RED, GREEN, '#7A5195', '#B77900'])})
    return out


def show_table(out, number, frame):
    with (out.parents[1] / 'results-index.csv').open(encoding='utf-8-sig', newline='') as handle:
        matches = [row for row in csv.DictReader(handle)
                   if row['kind'] == 'Table' and row['number'] == number]
    if len(matches) != 1:
        raise ValueError(f'Expected one indexed title for Table {number}.')
    frame.to_csv(out / 'tables' / f'table-{number.replace(".", "-")}.csv', index=False)
    display(Markdown(f"**Table {number}. {matches[0]['title']}**"))
    display(Markdown(frame.to_markdown(index=False)))


def show_figure(out, number, fig):
    fig.savefig(out / 'figures' / f'figure-{number.replace(".", "-")}.png',
                bbox_inches='tight', facecolor='white')
    plt.show()
    plt.close(fig)


def finish(out, values):
    def encode(x):
        if isinstance(x, np.ndarray):
            return x.tolist()
        if isinstance(x, np.generic):
            return x.item()
        raise TypeError(type(x).__name__)
    (out / 'numeric-results.json').write_text(
        json.dumps(values, default=encode, indent=2, allow_nan=False), encoding='utf-8')
    packages = sorted((d.metadata['Name'], d.version) for d in importlib.metadata.distributions())
    with (out / 'loaded-packages.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.writer(stream)
        writer.writerow(['Package', 'Version'])
        writer.writerows(packages)
    (out / 'session-info.txt').write_text(
        f'Python {platform.python_version()}\n{platform.platform()}\n', encoding='utf-8')
    print(f'Saved {len(values)} numeric results to {out.relative_to(Path.cwd())}.')
