# Credit Risk Modeling: Python Companion

Python implementations of the analyses in *Credit Risk Modeling with R*, by
Martin Lozano. The book and its [R companion](https://github.com/mlozanoqf/credit-risk-r)
remain the reference. This repository generates calculations, tables, figures
and local HTML reports. It does not build the publisher PDF.

**Pre-publication access:** this repository is private while the book is being
prepared. Public access is planned for publication, at the same URL. Foundations
and Chapters 1-6 are implemented, and the complete frozen credit-scoring data
and reference split are included.

## First time: prepare your computer

The recommended Windows route uses PowerShell and a project-specific Python
environment. You do not need Git, a GitHub account after public release, R,
LaTeX or the publisher's template to run this companion.

1. On this GitHub page, choose **Code > Download ZIP** and extract the entire
   ZIP into a folder on your computer. Keep its files together; a chapter uses
   the supplied data and helpers. Work in the extracted folder, not inside the ZIP.
2. Install [Python 3.12](https://www.python.org/downloads/)
   and [Quarto](https://quarto.org/docs/get-started/) (tested with **1.5.54**).
   Python performs the calculations; Quarto produces the report. On Windows,
   include the Python launcher (`py`) when installing Python.
3. Open the extracted folder in File Explorer. Right-click its background and
   choose **Open in Terminal** (or open PowerShell and use `cd` to enter that
   folder). You should see `start.py`, `run.py` and `requirements-lock.txt` there.
   The commands below belong in **PowerShell**, not at Python's `>>>` prompt.
4. Run these commands, waiting for each one to finish:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe start.py --check
```

The `.venv` folder holds this project's Python environment. The second command
installs its recorded package versions; first installation requires internet
access or an existing package cache and may take several minutes. It does not
install Python or Quarto. **Setup check passed** confirms that the packages
match their record, their dependency check passes and Quarto can start; a chapter
has not run yet. A version warning identifies a departure from the tested setup.
There is no environment activation command to remember: each command explicitly
uses `.venv`'s Python.

<details>
<summary>macOS/Linux commands</summary>

From a terminal in the extracted folder:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python start.py --check
.venv/bin/python start.py 00-foundations
```

Use `.venv/bin/python` instead of `.\.venv\Scripts\python.exe` in all later
commands. These platforms have not undergone the Windows clean-install test.
Some packages may need platform-specific build tools or system libraries.

</details>

## First result: run Foundations

In the same **PowerShell** window, run:

```powershell
.\.venv\Scripts\python.exe start.py 00-foundations
```

Keep the terminal open while Quarto prints its progress. A successful run prints
**Complete:** and **Your report is ready:**, followed by the report path, and
opens it in your browser. If it does not open automatically, double-click
`output/00-foundations/chapter.html` in the extracted folder. The `.qmd` is the
editable source; the `.html` is the finished report.

## Next time: choose any chapter

Open a terminal in the extracted project folder again and run:

```powershell
.\.venv\Scripts\python.exe start.py
```

Choose a chapter from the numbered menu; enter `0` to leave without running one.
For a particular chapter, add its ID, for example
`.\.venv\Scripts\python.exe start.py 03-merton`. Each chapter starts a fresh
Python process and prepares its own inputs; previous chapters need not run first.
You normally install packages only at first setup or after deliberately updating
the downloaded companion. Do not recreate `.venv` for each chapter.

The selector checks setup, calls the existing `run.py` executor and opens the
HTML only after success. Calculations, seeds and output checks remain the same.
Add `--no-open` to keep the report closed, or use `--list` to see chapter IDs
without running anything.

## Chapters and code for a book result

Each chapter README lists the book's numbered figures and tables. Its **Code**
links point to the corresponding Python blocks in `chapter.qmd` on GitHub.

- [Foundations](chapters/00-foundations/README.md) (`00-foundations`).
- [Logistic credit scoring](chapters/01-logistic/README.md) (`01-logistic`).
- [Tree-based credit scoring](chapters/02-tree-based/README.md) (`02-tree-based`).
- [The Merton model](chapters/03-merton/README.md) (`03-merton`).
- [Credit Spreads and CDS Valuation](chapters/04-credit-spreads-cds/README.md) (`04-credit-spreads-cds`).
- [Portfolio Credit Risk with Copulas](chapters/05-copulas/README.md) (`05-copulas`).
- [Climate Credit Risk](chapters/06-climate-credit-risk/README.md) (`06-climate-credit-risk`).

Run a complete unchanged chapter first. For an extension, open its local QMD
in a text editor, edit the Python code and rerun through `start.py`. Individual
blocks can depend on setup and earlier calculations. Save copies of outputs you
want to compare outside `output/`; rerunning replaces the chapter's outputs.
Keep the frozen inputs, seeds and software versions for the first replication.

## Output and comparison with R

Generated results stay on your computer, under `output/<chapter>/`:

- `chapter.html` shows code and results in the browser.
- `figures/` holds numbered PNGs and `tables/` holds CSVs.
- `numeric-results.json` holds unrounded values for numerical comparisons.
- Session files record the environment used for that run.

For example, Merton produces `output/03-merton/chapter.html`. CSV tables may
contain display rounding. Generated reports are not stored on GitHub.

Python preserves the financial questions, inputs and models where possible.
Deterministic formulas are checked against R. Simulation draws and fitted
models can differ with random streams and algorithms. In particular, the simple
tree is a documented scikit-learn adaptation with different leaves and predictions.
Chapter notes explain the differences. See [implementation status](IMPLEMENTATION_STATUS.md)
and [validation details](MAINTENANCE.md); R is a reference, not a runtime dependency.

## If something stops

| What you see | What to do |
|---|---|
| `py` is not recognized | Install Python 3.12 with its Windows launcher, reopen PowerShell and retry. |
| Python reports a syntax error for a terminal command | Exit the `>>>` prompt with `exit()` and enter the command in PowerShell. |
| `start.py` or `requirements-lock.txt` cannot be found | Open a terminal in the extracted project folder, where those files are visible. |
| `.venv`'s Python cannot be found | Complete the environment creation step from that folder. |
| Packages are missing or versions do not match | Rerun the documented pip install command using `.venv`'s Python, then `start.py --check`. Retain the first installation error if it fails. |
| Quarto was not found | Install Quarto, reopen the terminal, and rerun `start.py --check`. |
| A chapter stops with an error | Retain the first error, chapter ID and setup version messages. An older HTML is not evidence that the new run succeeded. |
| The browser does not open | Open `output/<chapter>/chapter.html` manually after a successful run. |

The starter never installs packages or downloads replacement data automatically.
The executor checks input integrity and fresh outputs. Full numerical regression
tests are available under [maintenance and verification](MAINTENANCE.md).

## Data and instructor resources

Chapters 1-2 include the same RDS input as the R companion and its frozen split
manifest. Python reads this file without installing R. The [provenance note](data/credit-scoring/PROVENANCE.md)
identifies the original course and the substantially modified, semi-synthetic
adaptation. Other frozen inputs retain their source notes and conditions.

The author has chosen to include limited iShares and NGFS extracts. NGFS extracts
carry the required notices. Written iShares redistribution permission remains
unconfirmed; inclusion does not grant unrestricted reuse rights. See
[data terms](DATA_TERMS.md) and the [release audit](PUBLICATION_AUDIT.md).

The instructor manual uses the **R companion** and a separately distributed,
restricted package of exercise-specific R scripts. Those scripts reuse the
book's inputs and shared R functions. This Python companion provides adaptations
of the book applications; it does not execute the instructor solutions.

## Alternative execution and maintenance

Experienced users can keep using `.\.venv\Scripts\python.exe run.py 03-merton`.
Running Quarto directly skips the executor's complete output-checking workflow.
See [maintenance](MAINTENANCE.md) for structure, validation scope and full test
commands. These are not prerequisites for opening your first report.

## License

Author-supplied code follows GPL-3.0; see [LICENSE](LICENSE). Data have separate
source terms and are not implicitly relicensed. Publisher manuscripts, PDFs,
contracts and instructor solutions are excluded from this repository.
