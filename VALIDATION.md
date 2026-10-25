# Merton Pilot Validation

Validated locally on 14 October 2026 on Windows with Python 3.12.14 and
Quarto 1.5.54. The pinned environment is in requirements-lock.txt.
The reference is credit-risk-r commit
24a5616326e2f6759c0e793c7d0f5ec1728dc99b.

## Coverage

At the pilot validation date of 14 October 2026, the implemented pilot covered
all 26 figures and 14 tables in Chapter 3. Foundations and Chapters 1, 2, 4, 5
and 6 were still planned at that stage. See the current
[implementation status](IMPLEMENTATION_STATUS.md) for their subsequent coverage.
This pilot record covers Chapter 3 checks in the recorded local environment.

## Checks completed

- Seven unit tests cover the calibration equations, analytic Jacobian,
  independent solver, debt decomposition, nested simulations, Monte Carlo
  checks and input validation.
- All 40 numbered outputs exist. Code links and HTML anchors pass checks;
  report images are embedded and all 26 figure files are nonblank.
- All 26 figures were visually inspected. Contour label placement was adjusted.
  HTML structure was checked programmatically; interactive browser inspection
  was unavailable under the tool's local-file URL policy.
- Two fresh Quarto executions produced identical values for all 59 numeric
  snapshot objects. This is repeatability within the pinned Python environment.
- Comparison with R covered 48 groups containing 5,879 numeric values.
  Eleven grid entries exceeded the initial numerical tolerances. They were
  investigated individually rather than accepted through a global tolerance
  increase. Re-running R reproduced its saved values, while an independent
  least-squares solver confirmed the Python solutions with smaller equation
  residuals. The largest PD difference was about 0.341 basis points.
  The comparison file retains both the original tolerance outcome and the
  separately reviewed verification outcome.
- The three capital-structure comparisons retain the reference rankings.
- pip check reported no dependency conflicts.

## Main results

| Result | Python value |
|---|---:|
| Inferred asset value | 12.39538718866851 |
| Inferred asset volatility | 0.21230471342333637 |
| Analytic risk-neutral PD | 0.12697124106068558 |
| Simulated PD, 100,000 draws | 0.12792 |
| Monte Carlo standard error | 0.0010528511053524846 |

Random streams differ between R and NumPy. Simulation checks therefore use
financial identities and sampling uncertainty. The first ten Python paths
contain no defaults; the chapter explicitly explains why that can happen.
The chapter also documents the calibration stopping-criterion differences.

## Repeat the checks

From the project root on Windows, with Quarto on PATH:

```powershell
.venv\Scripts\python.exe -m unittest discover -s checks -p "test_*.py" -v
.venv\Scripts\python.exe run.py 03-merton
.venv\Scripts\python.exe checks/check_outputs.py --chapters 03-merton
.venv\Scripts\python.exe -m pip check
```

Maintainer-only R comparison inputs and diagnostics are kept in .local/.
The scripts in checks/ document their extraction and comparison. R is not
required to execute the Python chapter.

## Distribution

The public companion repository is https://github.com/mlozanoqf/credit-risk-py.
Local diagnostics, the virtual environment and generated outputs are ignored
by Git. See PUBLICATION_AUDIT.md for the scope of completed validation.
