# Verification

Run each of the seven chapters with `python run.py <chapter-id>`, then run
`python checks/verify.py`. This checks frozen inputs, book-result identifiers,
index titles, source links, generated figures/tables, source freshness and numerical
references. Unit tests run with `python -m unittest discover -s checks -p "test_*.py"`.

`book-results.csv` records the 211 numbered results checked against book revision
`d7a08d03801b73d9801b14eaffe095563c0e47a0`. Companion captions can describe
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
