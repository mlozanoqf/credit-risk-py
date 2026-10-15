# Tree-based credit scoring

From the project root: `python run.py 02-tree-based`.

Open [chapter.qmd](chapter.qmd) to read or edit the calculations.
Execute in source order. [Results](../../README.md#results) are created locally.

**Restricted data required.** Supply the authorized RDS and frozen split manifest locally; both are excluded from distribution. No R session is required.

## Find code by book result

| Result | Title | Code |
|---|---|---|
| Figure 2.1 | A single decision tree for credit scoring. | [Code](chapter.qmd#L74) |
| Table 2.1 | Terminal leaves of the single decision tree. | [Code](chapter.qmd#L86) |
| Table 2.2 | Single-tree prediction summary on the test set. | [Code](chapter.qmd#L96) |
| Table 2.3 | Bridge between credit-scoring objects and XGBoost objects. | [Code](chapter.qmd#L106) |
| Table 2.4 | Dimensions of the encoded XGBoost design matrices. | [Code](chapter.qmd#L118) |
| Table 2.5 | XGBoost settings used for the checkpoint path and the full model. | [Code](chapter.qmd#L143) |
| Table 2.6 | Applicants selected to inspect two XGBoost checkpoint paths. | [Code](chapter.qmd#L166) |
| Table 2.7 | Selected XGBoost checkpoint corrections for two applicants. | [Code](chapter.qmd#L182) |
| Table 2.8 | Individual log-loss check for the two selected applicants. | [Code](chapter.qmd#L195) |
| Table 2.9 | First two XGBoost rounds: code values and algebraic updates. | [Code](chapter.qmd#L208) |
| Table 2.10 | First five XGBoost rounds for the selected applicant. | [Code](chapter.qmd#L244) |
| Figure 2.2 | Predicted PD for two applicants as XGBoost boosting rounds accumulate. | [Code](chapter.qmd#L251) |
| Table 2.11 | Inputs used by the XGBoost estimation call. | [Code](chapter.qmd#L276) |
| Table 2.12 | Estimated XGBoost model summary. | [Code](chapter.qmd#L287) |
| Figure 2.3 | Final predicted PD distributions for the full logistic model and XGBoost. | [Code](chapter.qmd#L293) |
| Figure 2.4 | Full logistic-model PDs compared with final XGBoost PDs by observed outcome. | [Code](chapter.qmd#L298) |
| Figure 2.5 | XGBoost learning curve: test AUC with train AUC as a diagnostic reference. | [Code](chapter.qmd#L313) |
| Table 2.13 | Direct overfitting diagnostic from the XGBoost learning curve. | [Code](chapter.qmd#L327) |
| Table 2.14 | Estimation, tuning, final evaluation and monitoring for XGBoost credit scoring. | [Code](chapter.qmd#L343) |
| Table 2.15 | XGBoost prediction range and test-set performance summary. | [Code](chapter.qmd#L353) |
| Figure 2.6 | XGBoost feature importance. | [Code](chapter.qmd#L362) |
| Figure 2.7 | Average absolute XGBoost contribution by feature. | [Code](chapter.qmd#L374) |
| Table 2.16 | Predicted PDs for selected test-set applicants. | [Code](chapter.qmd#L390) |
| Table 2.17 | Reconstructing John Doe's XGBoost score and predicted PD. | [Code](chapter.qmd#L400) |
| Table 2.18 | Largest local XGBoost contributions for John Doe. | [Code](chapter.qmd#L408) |
| Figure 2.8 | Partial dependence of XGBoost predicted default probability. | [Code](chapter.qmd#L415) |
| Table 2.19 | Out-of-sample performance of the credit-scoring models. | [Code](chapter.qmd#L447) |
| Figure 2.9 | ROC curves: logistic regression, single tree, and XGBoost. | [Code](chapter.qmd#L455) |
| Table 2.20 | Probability checks within each model's own risk deciles. | [Code](chapter.qmd#L460) |
| Figure 2.10 | Calibration by decile: logistic regression and XGBoost. | [Code](chapter.qmd#L465) |
| Figure 2.11 | Bad rate by acceptance rate: logistic regression, single tree, and XGBoost. | [Code](chapter.qmd#L470) |
| Figure 2.12 | Net payoff by acceptance rate: logistic regression, single tree, and XGBoost. | [Code](chapter.qmd#L481) |
| Table 2.21 | Numerical check of the overall best net-payoff strategy. | [Code](chapter.qmd#L497) |
| Table 2.22 | Best net-payoff row by model. | [Code](chapter.qmd#L506) |
| Table 2.23 | Governance checklist for moving from a tree-based score to a credit policy. | [Code](chapter.qmd#L518) |
