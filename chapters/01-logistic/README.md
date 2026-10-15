# Logistic credit scoring

From the project root: `python run.py 01-logistic`.

Open [chapter.qmd](chapter.qmd) to read or edit the calculations.
Execute in source order. [Results](../../README.md#results) are created locally.

**Restricted data required.** Supply the authorized RDS and frozen split manifest locally; both are excluded from distribution. No R session is required.

## Find code by book result

| Result | Title | Code |
|---|---|---|
| Table 1.1 | Variable names used in the chapter. | [Code](chapter.qmd#L45) |
| Table 1.2 | First 10 loan records before cleaning. | [Code](chapter.qmd#L50) |
| Table 1.3 | Loan counts by home ownership. | [Code](chapter.qmd#L59) |
| Table 1.4 | Default rate by home-ownership category. | [Code](chapter.qmd#L66) |
| Figure 1.1 | Interest rate histogram. | [Code](chapter.qmd#L74) |
| Figure 1.2 | Annual income dotplot. | [Code](chapter.qmd#L98) |
| Figure 1.3 | Annual income without extreme values. | [Code](chapter.qmd#L103) |
| Figure 1.4 | Sigmoid curve or logistic curve: age model. | [Code](chapter.qmd#L133) |
| Table 1.5 | Coefficient and odds-ratio interpretation for `logi_multi`. | [Code](chapter.qmd#L151) |
| Table 1.6 | AIC comparison across logistic model candidates. | [Code](chapter.qmd#L165) |
| Figure 1.5 | Predicted PDs from the age-only model across the test set. | [Code](chapter.qmd#L180) |
| Figure 1.6 | Narrow distribution of age-only predicted PDs. | [Code](chapter.qmd#L189) |
| Figure 1.7 | Prediction distributions for the interest-rate and multi-factor models. | [Code](chapter.qmd#L194) |
| Figure 1.8 | Prediction ranges across age, interest-rate, and multi-factor models. | [Code](chapter.qmd#L199) |
| Figure 1.9 | Sigmoid curve or logistic curve: full-model score. | [Code](chapter.qmd#L204) |
| Table 1.7 | Prediction ranges and AIC across logistic model candidates. | [Code](chapter.qmd#L223) |
| Figure 1.10 | Prediction distributions for the multi-factor and full models. | [Code](chapter.qmd#L229) |
| Figure 1.11 | Prediction ranges across all logistic model candidates. | [Code](chapter.qmd#L234) |
| Figure 1.12 | Full-model predicted PDs with a 15% cutoff. | [Code](chapter.qmd#L239) |
| Figure 1.13 | Full-model prediction distribution with a 15% cutoff. | [Code](chapter.qmd#L264) |
| Table 1.8 | First six full-model predictions after applying the 15% cutoff. | [Code](chapter.qmd#L269) |
| Table 1.9 | Ten test-set cases comparing predicted PD, cutoff decision, observed outcome, and credit consequence. | [Code](chapter.qmd#L274) |
| Table 1.10 | Accuracy can reward poor credit-screening rules. | [Code](chapter.qmd#L294) |
| Figure 1.14 | Full model prediction histogram with acceptance-rate cutoff. | [Code](chapter.qmd#L302) |
| Table 1.11 | Cutoffs implied by target acceptance rates. | [Code](chapter.qmd#L307) |
| Table 1.12 | Classification outcomes under the 15% cutoff and the 80% acceptance rule. | [Code](chapter.qmd#L314) |
| Table 1.13 | Sample of test-set outcomes under the 80% acceptance rule. | [Code](chapter.qmd#L322) |
| Table 1.14 | First 12 accept/reject decisions with ex-post evaluation. | [Code](chapter.qmd#L327) |
| Table 1.15 | First 10 accepted applications and their observed outcomes. | [Code](chapter.qmd#L332) |
| Table 1.16 | Bad rate among accepted loans at the 80% acceptance rule. | [Code](chapter.qmd#L337) |
| Table 1.17 | Bad rate among accepted loans at the 65% acceptance rule. | [Code](chapter.qmd#L344) |
| Table 1.18 | Bad rate by target acceptance rate for the age-only and full logistic models. | [Code](chapter.qmd#L353) |
| Figure 1.15 | Bad-rate comparison between the age-only model and the full model. | [Code](chapter.qmd#L361) |
| Table 1.19 | Net payoff across acceptance rates for the full logistic model. | [Code](chapter.qmd#L379) |
| Table 1.20 | Numerical check of the best net-payoff row. | [Code](chapter.qmd#L385) |
| Table 1.21 | Net-payoff sensitivity to the cost of accepting a default. | [Code](chapter.qmd#L395) |
| Table 1.22 | Confusion-matrix language translated into credit decisions. | [Code](chapter.qmd#L411) |
| Table 1.23 | Sensitivity, specificity, and error rates in credit language. | [Code](chapter.qmd#L421) |
| Figure 1.16 | ROC curves: Full model in blue, age model in orange. | [Code](chapter.qmd#L431) |
| Table 1.24 | Calibration by predicted-risk decile for the full and age-only models. | [Code](chapter.qmd#L437) |
| Figure 1.17 | Calibration by decile: full model in blue, age model in orange. | [Code](chapter.qmd#L444) |
| Table 1.25 | Brier score and Brier skill against a constant default-rate benchmark. | [Code](chapter.qmd#L453) |
| Table 1.26 | Cutoffs and error rates implied by two acceptance policies. | [Code](chapter.qmd#L461) |
| Figure 1.18 | Full model in blue, evaluated in two acceptance rates: 65% in black, 80% in red. | [Code](chapter.qmd#L473) |
| Figure 1.19 | Random-score ROC benchmark. | [Code](chapter.qmd#L486) |
| Figure 1.20 | Perfect-score ROC benchmark. | [Code](chapter.qmd#L495) |
