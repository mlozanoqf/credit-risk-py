# Foundations and Credit-Scoring Validation

Local validation on 14 October 2026. Reference R companion commit
24a5616326e2f6759c0e793c7d0f5ec1728dc99b. No files in the R companion or
publisher manuscript were changed. This validation preceded the public release.

## Implemented coverage

- Foundations: all worked calculations, including both unnumbered figures.
  Forty-four numeric objects agree with R to numerical precision.
- Chapter 1: all 20 numbered figures and 26 numbered tables, four logistic
  models, odds ratios, policy decisions, payoff comparisons, ROC and calibration.
- Chapter 2: all 12 numbered figures and 23 numbered tables, CART adaptation,
  160-round XGBoost, checkpoints, leaf arithmetic, feature contributions, partial
  dependence and lending-policy comparisons.

The reference data contain 30,024 rows, reduced to 30,000 by the same two
cleaning rules. Training and test sets retain exactly the same 20,000/10,000
memberships and row order as R. All 19 encoded predictor columns agree with
R's design matrices. The intercept is an additional logistic-regression column.

## Aggregate comparison

| Model | R AUC | Python AUC | R Brier | Python Brier | R best payoff | Python best payoff |
|---|---:|---:|---:|---:|---:|---:|
| Full logistic | 0.820691 | 0.820691 | 0.079990 | 0.079990 | $5,426 | $5,426 |
| Single tree | 0.734638 | 0.795930 | 0.084598 | 0.082388 | $5,200 | $5,266 |
| XGBoost, 160 rounds | 0.819049 | 0.819022 | 0.080323 | 0.080347 | $5,414 | $5,408 |

Payoffs use the same $1 gain per repaying loan, $5 cost per default and
50%-95% acceptance-target grid in five-percentage-point increments. They are
retrospective test-set calculations rather than a prospective policy estimate.

## Differences that affect interpretation

### Logistic regression

The full-model maximum individual PD difference is approximately 3.51e-12.
Acceptance decisions, decile membership and the preferred policy agree.
For the age-only model, the default R GLM convergence tolerance gives a
maximum standard-error difference of 7.93e-6 and p-value difference of 7.28e-6.
Re-estimating the same R specification with tighter convergence reduces those
differences to approximately 1e-14. Significance conclusions are unchanged.
The diagnostic keeps the original discrepancy and its checked explanation.

### Single tree

The authorized scikit-learn adaptation has 16 leaves; the R rpart model has 5.
Both use depth 4, minimum split size 100 and minimum leaf size 33. However,
rpart can group nominal categories and uses its relative error cp=0.001
pruning rule. Python uses treatment-coded features and ccp_alpha=0, with its
depth/sample restrictions explicit. Copying cp directly into ccp_alpha would
not preserve the same criterion.

At an 80% acceptance target, realized acceptance is 88.96% in R and 84.34% in
Python because leaf-PD ties are accepted together. Bad rates are 7.3516% and
6.2604%, respectively; 462 accept/reject decisions differ. The first maximizing
target on the tested grid changes from 50% to 70%. These are materially different
fitted trees, not numerically interchangeable implementations. This comparison
does not establish a general advantage of one software package.

### XGBoost

R uses xgboost 3.2.1.1; Python uses xgboost 3.4.1. The model objective,
encoded predictors, learning rate, depth, sampling fractions, minimum child
weight, regularization and initial probability are preserved. Python explicitly
uses the histogram method, engine seed 1049419804 and one thread. The saved
R configuration records this engine seed after the R call `set.seed(567)`.
The seed was aligned to that configuration rather than selected by predictive
performance. R's automatic tree method resolves to its histogram updater;
R uses its default thread count, while Python fixes one thread for portability.
Library versions remain different.

The mean absolute individual PD difference is 0.5315 percentage points and the
maximum is 7.4684 percentage points. At the 80% target, 142 decisions change
among 10,000 test borrowers. Accepted defaults change from 431 to 432, with
bad rates of 5.3875% and 5.4000%. Aggregate closeness therefore coexists with
meaningful differences for some individuals.

The best payoff target stays at 80%, and the full logistic model remains
slightly ahead of XGBoost in AUC, Brier and best payoff. Both learning curves
have their highest monitored test AUC at round 120, although the illustrated
model stays fixed at 160 rounds. This monitoring is not a separate tuning study.
The selected default case stays at test position 7127; the selected non-default
case changes from 8332 to 2661 under the same selection rule. Their profiles
and arithmetic are recomputed from the Python fit.

As an additional diagnostic, the R-trained model was exported locally and
loaded into Python. All 10,000 predictions matched exactly. This isolates the
observed differences to fitting rather than encoding or inference. The Python
chapter trains its own model and never loads that exported R model.

Each model constructs its own deciles. XGBoost's largest difference in observed
default rate within equally numbered R/Python deciles is 0.7 percentage points.
Those groups can contain different borrowers. The full logistic deciles agree.

### Presentation and random benchmark

NumPy's random-score benchmark has AUC 0.508698 versus R's 0.501245; both are
near the chance benchmark. Random streams differ despite using seed 2020.
The perfect-score AUC remains 1. Density plots use SciPy KDE smoothing, and
income dotplots stack records within fixed-width income bins. Plotting defaults
can change appearance without changing the fitted probabilities.

## Checks and reproducibility

Sixteen unit tests pass, including the existing Merton tests. They check
cleaning, split membership, link functions, tie handling, confusion-matrix
direction, leaf PDs, short-fit/prefix agreement, leaf-score arithmetic, contribution
reconstruction and payoff/decile accounting.

The R comparison verifies 121 deterministic groups containing 670,350 values,
including input matrices, split IDs and predictions; this count is not a count
of distinct financial results. Retrained CART/XGBoost differences are reported
separately rather than forced through exact-equivalence tests. Reader indexes,
numbered outputs, embedded images and source links are checked automatically.
Figures were inspected as images, with annotation and legend placements revised.
The single tree is split into two panels under a shared root so that all its
nodes and leaves can be read. Two fresh executions of each new chapter produced
identical numeric snapshots. This repeatability check uses the pinned Windows
Python environment; other platforms still require testing.

```powershell
.venv\Scripts\python.exe -m unittest discover -s checks -p "test_*.py" -v
.venv\Scripts\python.exe run.py 00-foundations
.venv\Scripts\python.exe run.py 01-logistic
.venv\Scripts\python.exe run.py 02-tree-based
.venv\Scripts\python.exe checks/check_outputs.py
```

Maintainer comparison commands additionally require the local R reference:

```powershell
Rscript --vanilla checks/export_scoring_reference.R <R-repository> .local
.venv\Scripts\python.exe checks/compare_scoring.py
```

The repository supplies the RDS and split manifest. Exported R models,
person-level comparisons, generated reports and diagnostics remain local.
Readers use the supplied inputs and Python environment to execute the chapters. Cross-platform installation remains a later release check.

## Foundations additions (October 14, 2026)

Added segment-based PD predictions and simulation of the existing independent
and always-together two-loan portfolios. The previous 44 Python numerical
results and 72 R numerical objects are unchanged. New applicant probabilities
are 0.04, 0.12 and 0.12 in both implementations.

At 10,000 scenarios with seed 20261014, Python mean losses are $996.50 and
$1,013.00; R gives $1,047.00 and $1,069.00. The analytical expectation is
$1,000 in both cases. Python joint-default frequencies are 1.04% and 10.13%;
R gives 1.01% and 10.69%, against analytical values of 1% and 10%.
All four mean-loss and joint-frequency comparisons fall within four analytical
Monte Carlo standard errors of their targets. Different pseudo-random number
generators explain why identical seeds do not imply identical scenarios.
Both independent chapter renders pass in the recorded local environments.

## Foundations bond example (October 15, 2026)

Added the one-year fixed-recovery bond calibration and default-protection
valuation. All 11 new numerical inputs/results agree with the R companion
within 1e-12. The supplied price is kept at 94/1.05 throughout calculation;
q=0.10, the risk-neutral expected payment is 94, and protection costs
6/1.05=5.714285714285714. Valuation by the risk-free/risky bond price
difference agrees within floating-point precision. Statewise combined
payments are 100 in both repayment and default. The 44 original Python
results and 72 original R numerical objects remain unchanged against the
pre-addition snapshots. Both Foundations chapter renders pass. These are
local checks; no claim of a new cross-platform or clean-install audit is made.
