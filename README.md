# Credit Risk Modeling: Python Companion

Python implementations of the analyses in *Credit Risk Modeling with R*, by
Martin Lozano. The book and its [R companion](https://github.com/mlozanoqf/credit-risk-r)
remain the reference. This project produces calculations, tables, figures and
local HTML reports; it does not build the publisher PDF.

Foundations and Chapters 1-6 are implemented. The credit-scoring inputs for
Chapters 1-2 are excluded pending permission. Third-party data retain their
source conditions, and iShares redistribution permission remains unconfirmed; see
[data terms](DATA_TERMS.md) and [release audit](PUBLICATION_AUDIT.md).
Consult [implementation status](IMPLEMENTATION_STATUS.md), [Merton validation](VALIDATION.md),
[Foundations/scoring validation](SCORING_VALIDATION.md) and
[bond, copula and climate validation](PORTFOLIO_VALIDATION.md) for comparison with R.

## Setup

Use Python 3.12 and install Quarto separately (reference version 1.5.54).
From this folder, create an isolated environment. On Windows:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.venv\Scripts\python.exe -m pip check
```

On macOS/Linux use `python3.12 -m venv .venv` and `.venv/bin/python` in the
commands below. The recorded environment has been tested on Windows; other
platforms still require validation. A separate clean Windows environment has
been tested without the credit-scoring inputs. The lock includes a Windows-only dependency
with an environment marker. LaTeX is not required.

## Run a chapter

```powershell
.venv\Scripts\python.exe run.py 03-merton
```

Other chapter IDs are `00-foundations`, `01-logistic`, `02-tree-based`,
`04-credit-spreads-cds`, `05-copulas` and `06-climate-credit-risk`.
Each can run independently; Chapters 1-2 require the authorized dataset
and its frozen split manifest. The simple Python tree is an explicitly documented
scikit-learn adaptation of the R tree, with different leaves and predictions.
Without those two input files, Chapters 1-2 stop with a data-availability message.
Their full empirical results cannot currently be reproduced from the public
repository alone. Foundations and Chapters 3-6 run using the included frozen
inputs, subject to the source conditions described below.

Each chapter starts a fresh Python process through Quarto/Jupyter. To read or
extend the calculations, open its `chapter.qmd`. Download the complete project
using **Code > Download ZIP**, or clone it with Git. Individual QMD files depend
on its helpers and inputs.
Run setup and preceding calculations before an individual result block.

## Chapters

- [Foundations](chapters/00-foundations/README.md)
- [Logistic credit scoring](chapters/01-logistic/README.md)
- [Tree-based credit scoring](chapters/02-tree-based/README.md)
- [The Merton model](chapters/03-merton/README.md)
- [Credit Spreads and CDS Valuation](chapters/04-credit-spreads-cds/README.md)
- [Portfolio Credit Risk with Copulas](chapters/05-copulas/README.md)
- [Climate Credit Risk](chapters/06-climate-credit-risk/README.md)

Each implemented chapter README indexes the book result, its title and the
corresponding Python code. Book numbers are preserved. `results-index.csv` is
the technical source/output map used by the checks.

## Results

After running a chapter, open `output/<chapter>/chapter.html` in a browser.
The same folder holds `figures/` (PNG), `tables/` (CSV), `numeric-results.json`
(unrounded computed values) and session information. Generated files stay local.
Table CSVs may contain display rounding; use the numeric snapshot for comparisons.

## Numerical equivalence

The implementations preserve the financial question, inputs and model where
possible. Deterministic formulas are checked numerically against R. Simulation
draws and fitted models may differ because random streams, algorithms and
defaults differ. Chapter notes identify specific differences and checks;
substituting a financial method requires a separate decision.

## Data availability

The credit-scoring data for Chapters 1-2 remain excluded from Git and distribution
pending permission. An authorized local copy may be used for development and
validation. Changing programming language does not change those restrictions.
Other frozen inputs retain their original source notes and conditions.
The author has chosen to include the limited iShares and NGFS extracts.
NGFS extracts carry the required source notices. Written iShares redistribution
permission remains unconfirmed; inclusion does not grant unrestricted reuse
rights. See [data terms](DATA_TERMS.md). No source is implicitly relicensed under
the code license.

## Structure and maintenance

`chapters/` contains chapter QMDs and specific helpers; `shared/` contains common
presentation, scoring, simulation and loss-measure functions. `data/` holds frozen inputs and source notes.
`checks/` holds tests and maintainer comparisons. Pin tested dependency versions
in `requirements-lock.txt`; record deliberate changes and revalidate results.
The R repository is read-only reference material, not a runtime dependency.

## Checks

After rendering Foundations and Chapters 3-6, the data-independent check commands are:

```powershell
.venv\Scripts\python.exe -m unittest discover -s checks -p "test_*.py" -v
.venv\Scripts\python.exe checks/check_outputs.py --chapters 00-foundations 03-merton 04-credit-spreads-cds 05-copulas 06-climate-credit-risk
```

Six scoring-model tests are explicitly skipped when the restricted data are
absent. Generic classification and policy tests still run. With authorized
inputs and all chapters rendered, omit `--chapters` to check every output.
The scripts named `compare_*`, `diagnose_*`, `export_*` and `scoring_probe.py`
are maintainer diagnostics requiring separate local R references; they are
not part of the reader's execution workflow. `audit_release.py` audits the
first-publication Git candidate and writes its file hashes under ignored `.local/`.

## License

Author-supplied code follows GPL-3.0, as in the R companion; see LICENSE.
Data have separate source terms. No publisher manuscript, PDF, contracts or
instructor solutions are included.
