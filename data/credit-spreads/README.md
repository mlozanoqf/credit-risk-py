# Frozen Chapter 4 Corporate-Bond Inputs

The CSV files are extracted observations, not simulated prices. Reproduction
uses these fixed files rather than downloading a changing market snapshot.
Public redistribution of the iShares extract remains under review; see
[data terms](../../DATA_TERMS.md). Its availability for local calculation is
separate from permission to include it in a public repository.
On 14 October 2026 the author decided to retain this extract. This decision
does not constitute source permission; redistribution rights remain unconfirmed.

- `corporate-bond-snapshot.csv`: nine CCO Holdings LLC 144A bonds from HYG and
  ten Verizon Communications Inc bonds from LQD, holdings dated 2026-09-28.
  The source field is Price; it is treated as a clean valuation mark, not an
  executable bid, ask or a trade. Settlement 2026-09-29 is an analytical
  convention. Exact intraday quote times are unavailable.
- HYG: https://www.ishares.com/us/products/239565/ishares-iboxx-high-yield-corporate-bond-etf/latest-holdings.csv
  Frozen raw SHA256: 863437a1dd63e5e90b6bd26607b15b736da35913bf6146287d0128033a740186.
- LQD: https://www.ishares.com/us/products/239566/ishares-iboxx-investment-grade-corporate-bond-etf/latest-holdings.csv
  Frozen raw SHA256: 73193a4f592e80b31abfd8f1abb437b27f76991f38bee3c67e25ab14db540666.
- `corporate-treasury-curve.csv`: GSW/Svensson parameter row dated 2026-09-25,
  https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv.
  These are continuously compounded zero yields, in percent, with maturities
  in years. The Fed describes weekly publication and possible revisions at
  https://www.federalreserve.gov/data/nominal-yield-curve.htm.
  The curve is one trading day older than the holdings; rate-shift sensitivity
  qualifies that mismatch and does not convert it into same-date data.

CCO maturities span
2028-2033; Verizon uses 2028-2033 maturities and issue/effective dates before
2026. These are available fund holdings, not a census of issuer debt.
Coupon precision is restored for US1248EPCB75 (5.375), US1248EPCS01 (6.375),
US1248EPCT83 (7.375), US92343VEU44 (4.016), and US92343VGN82 (2.355).
The source's rounded coupon is not used in place of the contractual coupon.

Selected CCO 4.75% 2032 terms:
https://www.sec.gov/Archives/edgar/data/1091667/000110465922007405/tm222869d3_ex4-2.htm
Selected Verizon 2.355% 2032 terms:
https://www.sec.gov/Archives/edgar/data/732712/000119312522008485/d436979dex410.htm
CCO corporate structure:
https://www.sec.gov/Archives/edgar/data/1271833/000127183326000014/ccoh-20260630.htm
Post-Cox operating-entity guarantees:
https://www.sec.gov/Archives/edgar/data/1091667/000110465926100972/tm2623711d1_8k.htm

CCO Holdings debt must not be pooled with Charter Operating secured debt.
Verizon debt is calibrated separately. Common recovery is an assumption;
independent recoveries are used in sensitivity analysis. Neither issuer's
fitted curve identifies physical PDs or separates liquidity and call value.
The baseline models maturity cash flows with coupon-date recovery and
unadjusted coupon dates. Optional redemption and business-day adjustments
are outside that baseline. Call-yield scenarios are conditional cash-flow
checks, not an option-adjusted spread calculation.
