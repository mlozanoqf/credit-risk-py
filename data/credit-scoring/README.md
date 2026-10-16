# Credit-scoring data

## Availability

The repository includes the complete frozen `credit_scoring.rds`
and its `reference-split.csv`. See the [provenance note](PROVENANCE.md) for
the source.

The examples use a substantially modified, semi-synthetic dataset derived from the loan data accompanying Lore Dirick's DataCamp course, *Credit Risk Modeling in R*. The data support the applications in Chapters 1 and 2 and do not represent a particular lender's portfolio.

The split manifest lists original file rows in their reference training/test
order. It fixes the comparison sample without requiring an R installation.
Python checks the dataset checksum and verifies complete, disjoint membership
before fitting models. Missing inputs produce an explicit error.

Read the RDS directly with `rdata.read_rds`; the library preserves factor
levels. `shared/scoring.py` performs cleaning and applies the split. Run
`.venv\Scripts\python.exe run.py 01-logistic` from the project root after environment setup.
Chapter 2 rebuilds these steps independently.

## Dictionary

The dataset contains 30,024 records and ten fields. Cleaning removes
income above $1,000,000 and employment tenure exceeding age minus 16, leaving
30,000 records. The reference split contains 20,000 training and 10,000 test rows.

| Original field | Analysis name | Meaning |
|---|---|---|
| loan_status | loan_st | Observed default, 1; observed non-default, 0 |
| loan_amnt | l_amnt | Loan amount in dollars |
| int_rate | int | Interest rate in percentage points; 12 means 12% |
| grade | grade | Grades A through E |
| emp_length | emp_len | Employment tenure in years, including quarter-years |
| home_ownership | home | MORTGAGE, OWN or RENT |
| annual_inc | income | Annual income in dollars |
| age | age | Age in years |
| sex | sex | Recorded category: 0 male, 1 female |
| region | region | E, N, NE, NW, S, SE, SW or W |

Original file rows identify positions within this frozen file. Human-facing
test positions are one-based; Python `.iloc` positions are zero-based.
The outcome column is excluded from the design matrix. Category baselines are
A, MORTGAGE, 0 and E, following the R factor levels.

The supplied documentation leaves the follow-up horizon for `loan_status` unspecified. In Chapters 1 and 2, a fitted PD estimates the probability of this recorded default label conditional on the model's inputs. Its interpretation as an annual or lifetime PD remains unvalidated and would require a documented observation horizon and outcome validation over that horizon. The expected-loss illustration assumes a matching horizon for PD, LGD, and EAD; interpreting it as annual expected loss would require validation of those inputs for a one-year period.
