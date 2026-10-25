# Implementation Status

## Reference inputs

The complete frozen scoring RDS and reference split are included, with a
[provenance note](data/credit-scoring/PROVENANCE.md).

Foundations and all six chapters are implemented. The initial comparison,
begun on 14 October 2026, used R companion commit
24a5616326e2f6759c0e793c7d0f5ec1728dc99b. Subsequent checks are documented
below and in the linked validation reports.

| Unit | Status | Validation notes |
|---|---|---|
| Foundations | Implemented; validated | Worked calculations and both unnumbered figures checked |
| 1. Logistic credit scoring | Implemented; validated | Complete frozen input and reference split included |
| 2. Tree-based credit scoring | Implemented; validated adaptation | CART tree differences and XGBoost comparisons documented |
| 3. Merton | Implemented; validated | Numerical and financial checks; see VALIDATION.md |
| 4. Credit Spreads and CDS Valuation | Implemented; validated | Valuations and relative-value comparisons checked |
| 5. Portfolio Credit Risk with Copulas | Implemented; validated | Monte Carlo differences assessed with sampling uncertainty |
| 6. Climate Credit Risk | Implemented; validated | Frozen inputs checked; optional live download not refreshed |

## Implementation and validation history

The Merton pilot established the chapter format, per-result code links, fixed
dependencies, financial identities, comparison with R and a fresh-process
repeat. The same approach was then applied to the other chapters.

Foundations and Chapters 1-2 were completed next. See SCORING_VALIDATION.md
for the comparison, including 16 versus 5 leaves in the Python/R simple trees.
The simple tree uses the documented scikit-learn CART adaptation. Both scoring
chapters retain the exact R split membership and order in the supplied
manifest, and run without an R runtime. Chapters 4-6 were subsequently completed
with 90 additional numbered results, financial tests and R comparisons. See
PORTFOLIO_VALIDATION.md.
The clean Windows installation passed for Foundations and Chapters 3-6.
Chapters 1-2 were verified separately in the recorded environment.
See PUBLICATION_AUDIT.md for technical checks and data-source conditions.
NGFS notices are retained and the iShares extract is included. Written iShares
redistribution permission remains unconfirmed.

## Interpreting comparisons

The comparisons use identical frozen inputs and financial assumptions. For
Chapters 1-2, the common training/test memberships separate implementation
differences from sample changes. Generated predictions and model objects stay
on the reader's computer. Deterministic calculations are checked against R;
Monte Carlo comparisons use sampling uncertainty and financial identities
because random paths and small-sample rankings can differ. Chapter QMDs explain
model and algorithm differences. Linux/macOS clean-install validation is
outside the completed checks.

## References for implementation choices

- [Quarto Python execution](https://quarto.org/docs/computations/python.html)
- [Quarto virtual environments](https://quarto.org/docs/projects/virtual-environments.html)
- [SciPy L-BFGS-B](https://docs.scipy.org/doc/scipy/reference/optimize.minimize-lbfgsb.html)
- [NumPy random-stream compatibility](https://numpy.org/neps/nep-0019-rng-policy.html)
- [Statsmodels binomial GLM](https://www.statsmodels.org/stable/glm.html)
- [Scikit-learn decision trees](https://scikit-learn.org/stable/modules/tree)
- [XGBoost prediction options](https://xgboost.readthedocs.io/en/stable/prediction.html)
