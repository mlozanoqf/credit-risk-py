# The Merton model

First use? Complete the [setup walkthrough](../../README.md#first-time-prepare-your-computer).
In **PowerShell**, opened in the extracted project folder, run:

```powershell
.\.venv\Scripts\python.exe start.py 03-merton
```

On macOS/Linux, use `.venv/bin/python` in place of the Windows interpreter path.
After **Complete:** appears, the browser opens `output/03-merton/chapter.html`.
If it stays closed, open that file manually from the extracted project folder.

Open [chapter.qmd](chapter.qmd) to read or edit the calculations.
Execute in source order. [Results](../../README.md#output-and-comparison-with-r) are created locally.

## Find code by book result

| Result | Title | Code |
|---|---|---|
| Table 3.1 | Estimated Merton asset value, asset volatility, and risk-neutral default probability. | [Code](chapter.qmd#L82) |
| Table 3.2 | The d-values and normal probabilities behind the Merton PD. | [Code](chapter.qmd#L90) |
| Figure 3.1 | The red area represents the risk-neutral probability of default. | [Code](chapter.qmd#L101) |
| Table 3.3 | Objective function value at the estimated Merton solution. | [Code](chapter.qmd#L118) |
| Figure 3.2 | Objective-function slice when asset volatility is held fixed. | [Code](chapter.qmd#L133) |
| Figure 3.3 | Objective-function slice when asset value is held fixed. | [Code](chapter.qmd#L145) |
| Figure 3.4 | Merton objective function: a contour view. | [Code](chapter.qmd#L157) |
| Figure 3.5 | Merton objective function: a three-dimensional view. | [Code](chapter.qmd#L173) |
| Table 3.4 | How to read the Merton numerical-solution diagnostics. | [Code](chapter.qmd#L184) |
| Table 3.5 | Debt measures implied by the fitted Merton model. | [Code](chapter.qmd#L214) |
| Table 3.6 | Merton-implied bond yield and credit spread. | [Code](chapter.qmd#L225) |
| Figure 3.6 | Ten risk-neutral valuation paths for the firm's assets. | [Code](chapter.qmd#L253) |
| Figure 3.7 | Paths that cross below D before maturity; only paths ending below D default. | [Code](chapter.qmd#L262) |
| Table 3.7 | Default count and simulated risk-neutral PD with 10 paths. | [Code](chapter.qmd#L269) |
| Figure 3.8 | One hundred risk-neutral valuation paths for the firm's assets. | [Code](chapter.qmd#L283) |
| Table 3.8 | Default count and simulated risk-neutral PD with 100 paths. | [Code](chapter.qmd#L290) |
| Figure 3.9 | Paths that end below the promised debt payment at maturity. | [Code](chapter.qmd#L298) |
| Figure 3.10 | These paths cross below $D$ before maturity, but finish with $V_T$ above $D$ and therefore do not default. | [Code](chapter.qmd#L305) |
| Table 3.9 | Observing the same 100 asset paths at different frequencies. | [Code](chapter.qmd#L313) |
| Figure 3.11 | Convergence of the simulated risk-neutral probability of default to the analytical Merton probability. | [Code](chapter.qmd#L331) |
| Figure 3.12 | Histogram of 100,000 terminal asset values simulated under the risk-neutral measure. | [Code](chapter.qmd#L350) |
| Table 3.10 | Large-sample simulated risk-neutral PD compared with the analytical Merton PD. | [Code](chapter.qmd#L370) |
| Table 3.11 | Correspondence between a European call and Merton equity. | [Code](chapter.qmd#L380) |
| Figure 3.13 | Equity at maturity as a European call payoff on the firm's assets. | [Code](chapter.qmd#L390) |
| Table 3.12 | Original Hull/Merton input position for the sensitivity analysis. | [Code](chapter.qmd#L412) |
| Figure 3.14 | The risk-neutral probability of default as a function of the equity at time zero. | [Code](chapter.qmd#L427) |
| Figure 3.15 | The risk-neutral probability of default as a function of the risk-free rate. | [Code](chapter.qmd#L433) |
| Figure 3.16 | The risk-neutral probability of default as a function of the promised debt payment due at maturity. | [Code](chapter.qmd#L440) |
| Figure 3.17 | The risk-neutral probability of default as a function of debt maturity. | [Code](chapter.qmd#L446) |
| Figure 3.18 | The risk-neutral probability of default as a function of the volatility of the equity. | [Code](chapter.qmd#L452) |
| Table 3.13 | Reading the one-input Merton sensitivity curves. | [Code](chapter.qmd#L458) |
| Figure 3.19 | A contour view of the risk-neutral probability of default as a function of equity value and equity volatility. | [Code](chapter.qmd#L470) |
| Figure 3.20 | The risk-neutral probability of default as a function of equity value and equity volatility: a three-dimensional view. | [Code](chapter.qmd#L499) |
| Table 3.14 | Capital-structure scenario summary under the Merton model. | [Code](chapter.qmd#L550) |
| Figure 3.21 | Initial capital-structure position and Merton risk-neutral PD. | [Code](chapter.qmd#L565) |
| Figure 3.22 | Lower promised debt versus higher equity value from the initial position. | [Code](chapter.qmd#L571) |
| Figure 3.23 | Alternative capital-structure position and Merton risk-neutral PD. | [Code](chapter.qmd#L578) |
| Figure 3.24 | Lower promised debt versus higher equity value from the alternative capital-structure position. | [Code](chapter.qmd#L585) |
| Figure 3.25 | Initial maturity-debt position and Merton risk-neutral PD. | [Code](chapter.qmd#L592) |
| Figure 3.26 | Higher promised debt payment versus longer maturity. | [Code](chapter.qmd#L600) |
