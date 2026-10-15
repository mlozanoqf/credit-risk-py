# Implementation Status

Scope approved on 14 October 2026: Foundations and all six chapters, in a
separate local project, before public release. Reference: credit-risk-r commit
24a5616326e2f6759c0e793c7d0f5ec1728dc99b. The R project remains unchanged.

| Unit | Status | Next check |
|---|---|---|
| Foundations | Implemented; validated | Author review of Python report |
| 1. Logistic credit scoring | Implemented; validated | Author review; restricted inputs remain local |
| 2. Tree-based credit scoring | Implemented; validated adaptation | Author review of the material tree differences and XGBoost comparison |
| 3. Merton | Implemented; pilot validated | Author review of rendered report; see VALIDATION.md |
| 4. Credit Spreads and CDS Valuation | Implemented; validated | Author review of report and relative-value comparison |
| 5. Portfolio Credit Risk with Copulas | Implemented; validated | Author review of Monte Carlo differences and uncertainty |
| 6. Climate Credit Risk | Implemented; validated | Author review; optional live download has not been refreshed |

## Order and acceptance criteria

Complete the Merton pilot first, including a rendered report, per-result code
links, fixed dependencies, financial identities, comparison with R and a fresh
process repeat. Then extend the same pattern to Foundations, Chapters 1-2,
Chapter 4, Chapter 5 and Chapter 6. This file records progress, not a claim that
planned units already work.

Foundations and Chapters 1-2 were completed next. See SCORING_VALIDATION.md
for the comparison, including 16 versus 5 leaves in the Python/R simple trees.
The user explicitly approved the scikit-learn CART adaptation. Both scoring
chapters retain the exact R split membership and order in a restricted local
manifest, and run without an R runtime. Chapters 4-6 were subsequently completed
with 90 additional numbered results, financial tests and R comparisons. See
PORTFOLIO_VALIDATION.md.
The subsequent clean Windows installation passed for Foundations and Chapters
3-6 without loan inputs. Chapters 1-2 stop with an explicit data requirement.
See PUBLICATION_AUDIT.md for technical checks and data-source conditions.
The author authorized initial publication with the scoring inputs excluded,
NGFS notices retained and the iShares extract included. Written iShares
redistribution permission remains unconfirmed.

Use identical frozen inputs and financial assumptions. For Chapters 1-2, retain
the same reference training/test memberships to distinguish language differences
from sample changes. Keep restricted data, derived person-level data and their
outputs excluded from public distribution. Ask before substituting methods.

Deterministic discrepancies require diagnosis rather than a blanket disclaimer.
Monte Carlo checks use uncertainty and financial identities; no requirement that
random paths or every small-sample ranking match R. Document model/algorithm
differences in the relevant QMD. Linux/macOS clean-install validation
remains a separate later step.

## References for implementation choices

- [Quarto Python execution](https://quarto.org/docs/computations/python.html)
- [Quarto virtual environments](https://quarto.org/docs/projects/virtual-environments.html)
- [SciPy L-BFGS-B](https://docs.scipy.org/doc/scipy/reference/optimize.minimize-lbfgsb.html)
- [NumPy random-stream compatibility](https://numpy.org/neps/nep-0019-rng-policy.html)
- [Statsmodels binomial GLM](https://www.statsmodels.org/stable/glm.html)
- [Scikit-learn decision trees](https://scikit-learn.org/stable/modules/tree)
- [XGBoost prediction options](https://xgboost.readthedocs.io/en/stable/prediction.html)
