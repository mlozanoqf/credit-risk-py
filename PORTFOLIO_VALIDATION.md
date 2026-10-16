# Bond, Copula and Climate Validation

Local validation on 14 October 2026 against R companion commit
`24a5616326e2f6759c0e793c7d0f5ec1728dc99b`. The R project and both book versions
remain unchanged. This validation preceded the public release.

## Coverage and inputs

Chapter 4 implements 27 tables and 8 figures; Chapter 5 implements 22 tables and
12 figures; Chapter 6 implements 14 tables and 7 figures. These 90 results extend
the earlier units to all 211 numbered reference results, plus Foundations.
The chapter indexes link directly to the Python code. Each chapter executes in
its own session, with its helpers and inputs available from the project root.

All five bond/climate CSV files are byte-identical to R, including the climate
download manifest. Market dates, contract terms, day counts, source units,
scenario mapping, exposure and recovery assumptions are preserved. R is used
only for maintainer comparisons, never by the reader-facing Python calculations.

## Chapter 4

Basic bond prices, CDS legs, implied hazard and the Brazilian sovereign example
agree to numerical precision. The Merton bridge retains the previously diagnosed
optimizer stopping difference, below 5e-8 in debt value. Semiannual schedules,
accrual, settlement-adjusted Treasury discounting and price-consistent yields
are checked explicitly.

Issuer calibration uses SciPy bounded nonlinear least squares instead of R
`nlminb`. The residual objective, DV01 weights, bounds and three starts agree.
All 72 recovery/rate/weight/timing fits were compared, along with peer omission,
step-curve tests and all 19 leave-one-bond-out residuals. The largest difference
among the 72 yield residuals is below 0.000008 basis points.

| Measure | Python | Comparison with R |
|---|---:|---|
| CCO model clean price | 85.493076 | Difference below 0.0000003 per 100 |
| Verizon model clean price | 84.143497 | Same displayed value |
| CCO residual | 33.099484 bp | Same displayed value |
| Verizon residual | 3.189867 bp | Same displayed value |
| CCO residual advantage | 29.909617 bp | Difference below 0.000007 bp |

The conditional CCO preference survives every stated sensitivity test. This
reproduces a model-based relative-value conclusion, not an executable arbitrage
or a general investment recommendation. Source marks, liquidity and optionality
limitations remain explicit in the chapter and source notes.

## Chapter 5

Normal thresholds, recovered marginal PDs, analytical expected loss and the
Vasicek Credit VaR formula agree to numerical precision. NumPy/Cholesky and
R/MASS generate different draws. Both retain the same copula distributions,
parameters and sample sizes. Every Python scenario trace is reconstructed from
its own simulated scores rather than copied from the R example.

| 99.9% metric, USD millions | R | Python |
|---|---:|---:|
| Gaussian finite-portfolio VaR | 5.1600 | 5.3600 |
| Gaussian finite-portfolio ES | 5.9046 | 6.2282 |
| t(4) finite-portfolio VaR | 17.4000 | 17.0000 |
| t(4) finite-portfolio ES | 19.8846 | 19.9212 |
| Mean t(4) minus Gaussian ES across 20 runs | 13.8321 | 13.7841 |

Some single-run tail differences are visibly larger than rounding. At 99.9%,
200,000 scenarios leave only 200 observations' worth of tail probability.
The Gaussian ES difference is about 2.84 combined estimated standard errors.
The difference between the two 20-run Gaussian ES means is about 3.03 combined
standard errors, a relatively unusual discrepancy that warranted a separate
check. Direct integration of the conditional binomial distribution gives finite
Gaussian ES of $6.087293m and VaR of $5.240m. This independent reference lies
between the R and Python estimates. The asymptotic Gaussian ES from direct
integration is $5.980020m. The diagnostic is reproducible in
`checks/exact_gaussian_tail.py`; it does not replace the chapter's simulations.

The financially important t(4)-minus-Gaussian ES comparison differs by only
0.63 combined standard errors across the 20 repetitions. The higher tail risk
under the t-copula and the exposure-concentration result remain unchanged.

Checks also compare Gaussian default-count frequencies with independently
integrated conditional-binomial probabilities, and two-firm joint defaults with
direct normal integration. Type-1 quantiles and exact probability-mass ES are
preserved, including ties at the VaR boundary. Quantile diagnostics use overlapping
sampling intervals; mean/ES diagnostics use combined Monte Carlo standard errors.
The five-standard-error automated threshold is a broad multi-check diagnostic,
not proof that every estimate or implementation is identical.

## Chapter 6

All 270 cleaned scenario-sector-year observations, 30 sector loss decompositions,
18 regional physical-risk maxima and the spread bridge match R. The five-year
portfolio PV expected loss increases by $5.2636m in Diverging Realities,
$6.5938m in Highway to Paris and $7.1481m in Sudden Wake-up Call, as in R.

For the one-year Highway to Paris simulation in 2030:

| Metric, USD millions | R baseline | Python baseline | R climate | Python climate |
|---|---:|---:|---:|---:|
| Mean loss | 4.1025 | 4.1668 | 8.1210 | 8.1439 |
| 95% VaR | 17.6000 | 17.7000 | 24.7000 | 24.7000 |
| 95% ES | 23.3540 | 23.9918 | 30.1600 | 30.5686 |

These differences are consistent with the sampling diagnostics; the largest
ES comparison is about 2.66 combined standard errors. The simulation also agrees
with analytical one-year expected loss. Within each language the same scores
couple baseline and climate outcomes. The main financial conclusions remain
unchanged, while individual trace rows differ.

The optional download helper preserves the R API request and writes into a new
directory. Mocked-response tests check request filters and response handling.
No live refresh was performed, so current endpoint availability is not certified.

## Reproducibility and maintenance

All 36 tests passed: 32 financial/data/model tests and four download-request
tests. The comparison script checks 75 deterministic/distribution groups and
27 sampling diagnostics. Fresh-session repeat renders, numbered-output checks,
embedded-image checks and visual figure inspection complete the local workflow.
The second fresh-session run of each of Chapters 4-6 produced byte-identical
numeric-results JSON files. The log-scale tail chart uses significant digits
so that small positive probabilities remain visible rather than rounding to 0%.
This validation applies to the pinned Windows environment; clean installation
on other operating systems remains a separate release task.

```powershell
.venv\Scripts\python.exe -m unittest discover -s checks -p "test_*.py" -v
.venv\Scripts\python.exe run.py 04-credit-spreads-cds
.venv\Scripts\python.exe run.py 05-copulas
.venv\Scripts\python.exe run.py 06-climate-credit-risk
.venv\Scripts\python.exe checks/check_outputs.py --chapters 04-credit-spreads-cds 05-copulas 06-climate-credit-risk
```

Maintainer-only R comparisons save diagnostics under ignored `.local/`:

```powershell
Rscript --vanilla checks/export_portfolio_reference.R ../credit-risk-r .local
.venv\Scripts\python.exe checks/compare_portfolio.py
.venv\Scripts\python.exe checks/exact_gaussian_tail.py
```

Generated HTML, tables, plots and diagnostic arrays remain local. No publisher PDF, manuscript,
contracts or instructor solutions enter this companion.
