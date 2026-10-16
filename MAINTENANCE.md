# Maintenance and verification

For first use, follow [the reader walkthrough](README.md). This page records
repository maintenance and checks beyond the initial chapter run.

## Structure and maintenance

`chapters/` contains chapter QMDs and specific helpers; `shared/` contains common
presentation, scoring, simulation and loss-measure functions. `data/` holds frozen inputs and source notes.
`checks/` holds tests and maintainer comparisons. Pin tested dependency versions
in `requirements-lock.txt`; record deliberate changes and revalidate results.
The R repository is read-only reference material, not a runtime dependency.

## Checks

After rendering the chapters, run the tests and output checks:

```powershell
.venv\Scripts\python.exe -m unittest discover -s checks -p "test_*.py" -v
.venv\Scripts\python.exe checks/verify.py
```

The integrated check verifies frozen input bytes, book numbering and code links,
freshly generated outputs, and numerical regression references from the recorded
Python environment. Run all seven chapters through `run.py` first. After changing
sources, rerun the chapters before verification. A deliberate extension may change
the numerical references; investigate the differences before updating those references.
Use `--chapters` with `check_outputs.py` for a structural check of a subset.
See [verification details](checks/README.md) for the scope of these checks.
The scripts named `compare_*`, `diagnose_*`, `export_*` and `scoring_probe.py`
are maintainer diagnostics requiring separate local R references; they are
not part of the reader's execution workflow. `audit_release.py`
audits the Git candidate and writes its file hashes under ignored `.local/`.

## Validation scope

See [implementation status](IMPLEMENTATION_STATUS.md), [Merton validation](VALIDATION.md),
[Foundations/scoring validation](SCORING_VALIDATION.md) and [portfolio validation](PORTFOLIO_VALIDATION.md).
The clean Windows installation test covers Foundations and Chapters 3-6;
Chapters 1-2 were verified in the recorded environment. Other platforms require validation.

## Reader starter tests

Run `.venv\Scripts\python.exe -m unittest discover -s checks -p "test_start.py" -v`.
It tests selection, setup failures, runner delegation, browser handling and failed runs.
The starter delegates all calculations and output verification to the existing runner.
