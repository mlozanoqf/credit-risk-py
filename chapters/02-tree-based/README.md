# Tree-based credit scoring

First use? Complete the [setup walkthrough](../../README.md#first-time-prepare-your-computer).
In **PowerShell**, opened in the extracted project folder, run:

```powershell
.\.venv\Scripts\python.exe start.py 02-tree-based
```

On macOS/Linux, use `.venv/bin/python` in place of the Windows interpreter path.
After **Complete:** appears, the browser opens `output/02-tree-based/chapter.html`.
If it stays closed, open that file manually from the extracted project folder.

Open [chapter.qmd](chapter.qmd) to read or edit the calculations.
Execute in source order. [Results](../../README.md#output-and-comparison-with-r) are created locally.

**Frozen data included.** The complete repository supplies the RDS and reference split, with a brief provenance note. No R session is required.

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
| Table 2.12 | Estimated XGBoost model summary. | [Code](chapter.qmd#L308) |
| Figure 2.3 | Final predicted PD distributions for the full logistic model and XGBoost. | [Code](chapter.qmd#L314) |
| Figure 2.4 | Full logistic-model PDs compared with final XGBoost PDs by observed outcome. | [Code](chapter.qmd#L319) |
| Figure 2.5 | XGBoost learning curve: test AUC with train AUC as a diagnostic reference. | [Code](chapter.qmd#L334) |
| Table 2.13 | Direct overfitting diagnostic from the XGBoost learning curve. | [Code](chapter.qmd#L348) |
| Table 2.14 | Estimation, tuning, final evaluation and monitoring for XGBoost credit scoring. | [Code](chapter.qmd#L364) |
| Table 2.15 | XGBoost prediction range and test-set performance summary. | [Code](chapter.qmd#L374) |
| Figure 2.6 | XGBoost feature importance by Gain. | [Code](chapter.qmd#L383) |
| Figure 2.7 | Average absolute contribution to the XGBoost log-odds score by feature. | [Code](chapter.qmd#L395) |
| Table 2.16 | Predicted PDs for selected test-set applicants. | [Code](chapter.qmd#L411) |
| Table 2.17 | Reconstructing John Doe's XGBoost score and predicted PD. | [Code](chapter.qmd#L421) |
| Table 2.18 | Largest local contributions to John Doe's XGBoost log-odds score. | [Code](chapter.qmd#L429) |
| Figure 2.8 | Partial dependence of XGBoost predicted default probability. | [Code](chapter.qmd#L436) |
| Table 2.19 | Out-of-sample performance of the credit-scoring models. | [Code](chapter.qmd#L465) |
| Figure 2.9 | ROC curves: logistic regression, single tree, and XGBoost. | [Code](chapter.qmd#L473) |
| Table 2.20 | Probability checks within each model's own risk deciles. | [Code](chapter.qmd#L478) |
| Figure 2.10 | Calibration by decile: logistic regression and XGBoost. | [Code](chapter.qmd#L483) |
| Figure 2.11 | Bad rate by target acceptance rate: logistic regression, single tree, and XGBoost. | [Code](chapter.qmd#L488) |
| Figure 2.12 | Net payoff by target acceptance rate: logistic regression, single tree, and XGBoost. | [Code](chapter.qmd#L499) |
| Table 2.21 | Numerical check of the overall best net-payoff strategy. | [Code](chapter.qmd#L515) |
| Table 2.22 | Best net-payoff row by model. | [Code](chapter.qmd#L524) |
| Table 2.23 | Governance checklist for moving from a tree-based score to a credit policy. | [Code](chapter.qmd#L536) |
