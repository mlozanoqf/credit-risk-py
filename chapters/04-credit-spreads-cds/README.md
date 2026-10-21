# Credit Spreads and CDS Valuation

First use? Complete the [setup walkthrough](../../README.md#first-time-prepare-your-computer).
In **PowerShell**, opened in the extracted project folder, run:

```powershell
.\.venv\Scripts\python.exe start.py 04-credit-spreads-cds
```

On macOS/Linux, use `.venv/bin/python` in place of the Windows interpreter path.
After **Complete:** appears, the browser opens `output/04-credit-spreads-cds/chapter.html`.
If it stays closed, open that file manually from the extracted project folder.

Open [chapter.qmd](chapter.qmd) to read or edit the calculations.
Execute in source order. [Results](../../README.md#output-and-comparison-with-r) are created locally.

## Find code by book result

| Result | Title | Code |
|---|---|---|
| Table 4.1 | Merton quantities carried into the credit-spread chapter. Debt amounts retain Chapter 3's common monetary unit (MU). | [Code](chapter.qmd#L56) |
| Table 4.2 | Discrete default timeline with a constant 2.5% conditional PD. | [Code](chapter.qmd#L72) |
| Table 4.3 | Risk-free and risky zero-coupon valuation. Prices are per 100 of face value. | [Code](chapter.qmd#L92) |
| Table 4.4 | Risk-free and risky coupon bond valuation. Prices are per 100 of face value. | [Code](chapter.qmd#L111) |
| Table 4.5 | Risky coupon bond price decomposition. | [Code](chapter.qmd#L118) |
| Figure 4.1 | Coupon bond price and yield spread as conditional default risk changes. | [Code](chapter.qmd#L125) |
| Table 4.6 | Default probabilities, recovery, and their roles in bond valuation. | [Code](chapter.qmd#L140) |
| Table 4.7 | Real-world and market-implied default probabilities and their uses. | [Code](chapter.qmd#L152) |
| Table 4.8 | Historical PDs and spread-implied PDs answer different questions. | [Code](chapter.qmd#L160) |
| Table 4.9 | A one-year CDS spread implied by the Merton PD. | [Code](chapter.qmd#L177) |
| Figure 4.2 | Present values of the CDS premium and protection legs across spreads. | [Code](chapter.qmd#L185) |
| Table 4.10 | Survival and default probabilities for a 2% hazard rate. | [Code](chapter.qmd#L210) |
| Table 4.11 | Present value of expected CDS premium payments for a $1 notional. | [Code](chapter.qmd#L216) |
| Table 4.12 | Present value of expected protection payoff for a $1 notional. | [Code](chapter.qmd#L223) |
| Table 4.13 | Present value of expected accrued premium for a $1 notional. | [Code](chapter.qmd#L231) |
| Table 4.14 | Fair CDS spread including accrued premium, for a $1 notional. | [Code](chapter.qmd#L239) |
| Table 4.15 | Refining default timing while retaining annual CDS premiums. | [Code](chapter.qmd#L252) |
| Table 4.16 | Mark-to-market value of an existing CDS. Present values are per unit of notional. | [Code](chapter.qmd#L280) |
| Table 4.17 | Implied hazard rate from a CDS spread. | [Code](chapter.qmd#L290) |
| Table 4.18 | Quick CDS spread approximation compared with the accrued-premium valuation. | [Code](chapter.qmd#L299) |
| Figure 4.3 | Fair CDS spread under hazard and recovery assumptions. | [Code](chapter.qmd#L307) |
| Figure 4.4 | Mark-to-market value to the protection seller as the contractual spread changes. | [Code](chapter.qmd#L325) |
| Table 4.19 | Protection-seller value sensitivity to the contractual CDS premium. | [Code](chapter.qmd#L338) |
| Table 4.20 | CDS valuation tools and the credit questions they answer. | [Code](chapter.qmd#L345) |
| Table 4.21 | Two corporate bonds considered for purchase; prices per 100 of principal. | [Code](chapter.qmd#L369) |
| Figure 4.5 | Settlement-adjusted Treasury zero yields used to discount the corporate-bond payments. | [Code](chapter.qmd#L376) |
| Table 4.22 | Issuer-specific pricing curves and model values for the bonds excluded from calibration. Model clean prices are per 100 of principal. | [Code](chapter.qmd#L390) |
| Table 4.23 | Price and yield comparisons using the same promised payments for each bond. Clean prices and price differences are per 100 of principal. | [Code](chapter.qmd#L417) |
| Figure 4.6 | Additional promised yield relative to each bond's issuer-curve benchmark. | [Code](chapter.qmd#L425) |
| Table 4.24 | CCO minus Verizon yield-residual advantage under deterministic sensitivity checks. | [Code](chapter.qmd#L435) |
| Figure 4.7 | How a deduction from CCO's model value changes the conditional purchase preference. | [Code](chapter.qmd#L475) |
| Table 4.25 | First two and last two promised payments of the Brazilian sovereign bond, per 100 of principal. | [Code](chapter.qmd#L521) |
| Table 4.26 | Recovery sensitivity for the Brazilian bond. Fitted PDs hold price at 99.091; the last column holds annual PD at 3.4535%. All prices are per 100 of principal. | [Code](chapter.qmd#L529) |
| Figure 4.8 | Cumulative default probability implied by the Brazilian bond price under different recovery assumptions. | [Code](chapter.qmd#L542) |
| Table 4.27 | Credit-spread and CDS valuation checklist. | [Code](chapter.qmd#L555) |
