# Portfolio Credit Risk with Copulas

From the project root on Windows: `.venv\Scripts\python.exe run.py 05-copulas`.

On macOS/Linux, use `.venv/bin/python` in place of the Windows interpreter path.

Open [chapter.qmd](chapter.qmd) to read or edit the calculations.
Execute in source order. [Results](../../README.md#results) are created locally.

## Find code by book result

| Result | Title | Code |
|---|---|---|
| Table 5.1 | Practical ways to justify the copula correlation input. | [Code](chapter.qmd#L66) |
| Figure 5.1 | Gaussian copula workflow for portfolio credit risk. | [Code](chapter.qmd#L77) |
| Table 5.2 | Objects used in the Gaussian copula credit-risk workflow. | [Code](chapter.qmd#L92) |
| Table 5.3 | Hull Example 24.7 inputs and the corresponding Gaussian default thresholds. | [Code](chapter.qmd#L103) |
| Table 5.4 | Illustrative threshold rule for one hypothetical credit scenario. | [Code](chapter.qmd#L111) |
| Figure 5.2 | Default thresholds implied by Hull Example 24.7 cumulative PDs. | [Code](chapter.qmd#L119) |
| Figure 5.3 | Checking that each Gaussian threshold reproduces the original cumulative PD. | [Code](chapter.qmd#L135) |
| Figure 5.4 | Zoom: Gaussian thresholds and cumulative PDs for credit-state scores between -2.5 and -0.5. | [Code](chapter.qmd#L152) |
| Table 5.5 | One-firm simulation check for the 5-year marginal PD. | [Code](chapter.qmd#L167) |
| Figure 5.5 | One-firm simulation check with threshold comparison. | [Code](chapter.qmd#L174) |
| Table 5.6 | Direct two-firm simulation check for $\rho = 0.2$. | [Code](chapter.qmd#L202) |
| Table 5.7 | Two-firm default probabilities under different Gaussian copula correlations. | [Code](chapter.qmd#L208) |
| Figure 5.6 | Two-firm Gaussian copula simulations across negative and positive correlations. | [Code](chapter.qmd#L214) |
| Table 5.8 | Equal-correlation matrix for the ten-firm portfolio. | [Code](chapter.qmd#L241) |
| Table 5.9 | Distribution of the number of defaults by year 5 for ten firms and $\rho = 0.2$. | [Code](chapter.qmd#L247) |
| Table 5.10 | Default-event probabilities for ten firms under different copula correlations. | [Code](chapter.qmd#L253) |
| Figure 5.7 | Distribution of the number of defaults by year 5 under different copula correlations. | [Code](chapter.qmd#L259) |
| Table 5.11 | Portfolio loss summary for a homogeneous ten-firm portfolio. | [Code](chapter.qmd#L282) |
| Figure 5.8 | Portfolio loss distribution under different copula correlations. | [Code](chapter.qmd#L288) |
| Table 5.12 | Concentration risk with the same total exposure, PD, recovery, and copula correlation. | [Code](chapter.qmd#L303) |
| Figure 5.9 | Portfolio loss distributions with the same defaults and different exposure weights. | [Code](chapter.qmd#L311) |
| Table 5.13 | Two firms affected by the same t-copula scale draw. | [Code](chapter.qmd#L342) |
| Table 5.14 | Default clustering under Gaussian and t-copulas. | [Code](chapter.qmd#L354) |
| Table 5.15 | Portfolio loss measures under Gaussian and t-copulas. | [Code](chapter.qmd#L362) |
| Figure 5.10 | Default-count distribution under Gaussian and t-copulas. | [Code](chapter.qmd#L368) |
| Table 5.16 | Inputs for the Vasicek-style Credit VaR approximation. | [Code](chapter.qmd#L392) |
| Table 5.17 | Mapping the Credit VaR notation to the Python implementation. | [Code](chapter.qmd#L399) |
| Table 5.18 | Numerical substitution for the 99.9% Credit VaR calculation. | [Code](chapter.qmd#L410) |
| Table 5.19 | Gaussian Vasicek Credit VaR, expected loss, capital, and expected shortfall. | [Code](chapter.qmd#L424) |
| Table 5.20 | The 99.9% Gaussian Credit VaR calculation. | [Code](chapter.qmd#L432) |
| Figure 5.11 | Systematic factor and conditional portfolio loss. | [Code](chapter.qmd#L440) |
| Table 5.21 | Credit VaR model risk under Gaussian and t-copula assumptions. | [Code](chapter.qmd#L451) |
| Figure 5.12 | Loss-tail survival probabilities under Gaussian and t-copulas. | [Code](chapter.qmd#L462) |
| Table 5.22 | Monte Carlo precision of the 99.9% expected-shortfall comparison, in USD millions. | [Code](chapter.qmd#L478) |
