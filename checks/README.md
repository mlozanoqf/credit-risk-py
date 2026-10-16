# Verification

Commands below use the Windows virtual-environment interpreter. On macOS/Linux,
use `.venv/bin/python` instead.

Run each of the seven chapters with `.venv\Scripts\python.exe run.py <chapter-id>`, then run
`.venv\Scripts\python.exe checks/verify.py`. This checks frozen inputs, book-result identifiers,
index titles, source links, generated figures/tables, source freshness and numerical
references. Unit tests run with `.venv\Scripts\python.exe -m unittest discover -s checks -p "test_*.py"`.

`book-results.csv` records the 211 numbered results checked against book revision
`d7a08d03801b73d9801b14eaffe095563c0e47a0`, with caption-only updates
checked against the local publication manuscript on 16 October 2026. Numbering
and result identifiers are unchanged. Companion captions can describe
language-specific results, such as the selected Python applicant. Update the index
and this reference together after checking any later changes in book numbering.

`numeric-reference.json` contains compact numerical checkpoints from the
independently executed 15 October 2026 audit, before these verification changes.
They include valuation, model evaluation, decision rules and portfolio/climate
results. They test reproducibility in the pinned Python environment, including
seeded simulations, rather than equality of random draws across languages.
The R repository carries its own numerical reference. Numerical regressions
require investigation; regenerating a fixture is a deliberate maintenance action.

The runner records normalized source hashes only after successful execution and
checks that numbered outputs were written by that run. Running Quarto directly
does not produce this verification record. Changes to shared code or chapter
sources invalidate the record and require rerunning the chapters.

Maintainer `compare_*` scripts provide separate comparisons against R. Foundations
uses exact deterministic comparisons and sampling-error checks for simulations.
The simple tree and XGBoost retain their documented implementation differences.
The title check concerns the reader-facing result index. Caption wording inside
rendered figures and tables still requires editorial review against the book.
These checks complement financial interpretation and visual review; they do not
prove that every possible modification or untested platform is equivalent.

## Extension checks

Run `.venv\Scripts\python.exe checks/test_extensions.py` from the repository root
in its recorded environment.
This checks incoming-applicant encoding against the training matrix, rejects
unknown categories and invalid numeric inputs, verifies heterogeneous portfolio
expected loss and borrower alignment, and deliberately tests missing climate
coverage, duplicates, incorrect units and invalid PDs. These are implementation
checks; they do not validate the economic assumptions of a new application.
