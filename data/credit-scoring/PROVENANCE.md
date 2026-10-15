# Credit-scoring dataset: provenance and modifications

## Source and attribution

The starting material is the `loan_data` dataset supplied with Lore Dirick's
DataCamp course, *Credit Risk Modeling in R*
(https://www.datacamp.com/courses/credit-risk-modeling-in-r).
The version accompanying *Credit Risk Modeling with R*, by Martin Lozano, is
a substantially modified, semi-synthetic derivative. Cite the course as the
source of the starting data and Lozano's book as the source of this adaptation.

## What was changed

The adaptation retains the original 29,092 records as its starting cohort and
adds 932 synthetic records, giving 30,024 records and ten fields. Default
labels for the starting cohort were retained; labels for the added records
were simulated. The supplied file is the frozen input used by the book,
rather than an unmodified extract from an identified lender.

- Earlier preparation imputed some missing values and added synthetic sex
  and region fields. Those fields were subsequently revised through randomized
  assignments; the final region field has eight categories. They should not
  be interpreted as observed demographic or geographic evidence.
- Employment tenure was revised, expressed in quarter-years and checked
  against age. Selected ages and tenure values were also adjusted. Fifteen
  incompatible tenure records were deliberately retained for the cleaning
  exercise.
- Interest rates were perturbed, including conspicuous repeated or imputed
  values and low-rate cases. Credit grades were reassigned, with the final
  scale running from A to E. The former OTHER housing category was reassigned.
- Income and loan amounts were perturbed while preserving positive values
  and useful variation in affordability. Some transformations used model
  risk groups, and model diagnostics informed the development of the dataset.
- The 932 added records broaden the age distribution and include simulated
  outcomes. The file was ordered by region, grade and age; row numbers are
  positions in this frozen file, not persistent customer identifiers.

The analysis removes nine records with income above $1,000,000 and then
fifteen with employment tenure greater than age minus 16, leaving 30,000
records. The book creates a 20,000/10,000 training/test split. The split seed
was selected after examining default proportions in several random splits.
Python supplies that same membership and order in `reference-split.csv`,
so an R installation is unnecessary for running the Python chapters.

## Interpretation and reproduction

The dataset supports comparisons of calculations, predictions and credit
decisions under a common, reproducible sample. Its construction was informed
by outcomes and model diagnostics, so the test results are descriptive
comparisons within this semi-synthetic application, rather than independent
validation on future borrowers. In particular, demographic associations and
model rankings should not be generalized to a lender or borrower population.

The R and Python companions use the same unchanged RDS file. The input checksum
manifest identifies the reference version. Internal data-construction scripts
are separate authoring materials; the companion code starts from the supplied
data and reproduces cleaning, estimation and results.
