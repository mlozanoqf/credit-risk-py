# Data Sources and Release Review

Reviewed on 14 October 2026. GPL-3.0 applies to author-supplied code. It does not
relicense third-party data. This record distinguishes technical reproducibility
from permission to redistribute; it is not a legal opinion.

## Credit-scoring data

`credit_scoring.rds`, `reference-split.csv`, individual predictions, trained
models and rendered scoring outputs are excluded from the publication candidate.
Permission for the underlying loan data remains pending. Chapters 1-2 explain
the required inputs and stop before rendering when those inputs are absent.
The data dictionary and checksum identify the intended dataset without supplying
its observations. No alternative download or reconstruction is provided.

## Corporate-bond observations

`data/credit-spreads/corporate-bond-snapshot.csv` contains 19 extracted holdings
observations from iShares HYG/LQD, with documented contractual coupon corrections.
The source pages link to the [BlackRock terms and conditions](https://www.blackrock.com/corporate/compliance/terms-and-conditions).
Their intellectual-property section restricts public redistribution of website
material without written permission. The holdings disclaimer also describes
prices supplied by third-party vendors.

**Release review remains open for this extract.** Public download access alone
does not establish permission to republish it. The audit has not determined
whether a separate permission or applicable exception covers these selected
observations. On 14 October 2026 the author decided to retain the extract in
both companions after reviewing these restrictions. The file remains intact.
That retention decision does not supply source permission or resolve this
rights question; obtaining written confirmation remains recommended. No public
release of the Python companion was authorized by the retention decision alone.
The author subsequently authorized publication with this extract retained and
the credit-scoring inputs excluded. This publication instruction does not
constitute permission from iShares or its pricing providers.

## Treasury curve

`data/credit-spreads/corporate-treasury-curve.csv` contains one dated GSW/Svensson
parameter row from the Federal Reserve Board. Its [copyright notice](https://www.federalreserve.gov/disclaimer.htm)
allows copying and distribution of Board information unless otherwise indicated,
with source attribution. The source URL, observation date, units and qualifications
are recorded in the [Chapter 4 input notes](data/credit-spreads/README.md).

## Climate scenarios

Source: NGFS Phase 5 Short Term Scenario Explorer, hosted by IIASA. The
[official license](https://data.ece.iiasa.ac.at/ngfs-phase-5-short-term/#/license)
displays copyright IIASA 2022 and a public license adapted from CC BY 4.0.
It permits sharing non-substantial extracts and derived analyses with attribution;
it restricts republication of substantial portions of the database. It must not
be described as an unmodified CC BY 4.0 license or as GPL-licensed data.

The frozen files contain 1,350 global CLIMACRED observations and 126 regional
DAPS observations, selected for the chapter. The manifest preserves the original
download time and endpoint. The files have not been numerically modified in the
Python translation. Cleaning, reshaping and illustrative portfolio calculations
are performed openly in Chapter 6. Data are provided without warranties and
neither NGFS nor IIASA endorses this companion.

On 14 October 2026 the author decided to retain these limited, chapter-specific
extracts under the source license, with the required notices. The license
provides no numerical substantiality threshold; the limited scope supports
this interpretation but no separate provider confirmation or legal determination
has been obtained. Retain this attribution, the original manifest, the
[source link](https://data.ece.iiasa.ac.at/ngfs-phase-5-short-term/), the license
link and the reference to its Section 5 disclaimer and liability provisions in
any permitted distribution. The extracts were downloaded on 4 June 2026 (UTC)
and are not a current or complete database copy. Review the license and scope
again before expanding or refreshing the extracts.

The optional API refresh is independent of rendering. The clean-install test
uses frozen observations and does not certify current API availability.
