# Clean Installation and Publication Audit

## Current verification

The repository contains the complete frozen scoring dataset and reference
split. Their source and modifications are described in the
[provenance note](data/credit-scoring/PROVENANCE.md).
Both companion repositories are publicly accessible on GitHub.

On 15 October 2026, both scoring chapters executed independently in the
recorded Windows environment and reproduced byte-identical numeric JSON
snapshots. All 37 tests passed, with none skipped. Checks covered 81 numbered
results, 32 nonblank figures, code links and report anchors. The R split
export matches the supplied manifest exactly.

The maintainer comparison with `--scoring-only` passes 77 deterministic groups
covering 670,292 values. Logistic predictions agree with R to about 3.6e-12.
Documented CART and XGBoost differences remain unchanged. This scoring rerun
used existing packages and is distinct from a clean dependency installation.
The staged Foundations comparator repair was separately verified against the
existing audit snapshots on 15 October. It maps R's nested simulation records
to Python's summary arrays and passes 56 shared deterministic keys (72 values)
at absolute and relative tolerances of 1e-12. The combined comparison passes
133 deterministic groups containing 670,364 values; all 77 scoring groups and
scoring summary outputs remain identical between combined and scoring-only
modes.

Twelve separate Monte Carlo checks pass at a four-analytical-standard-error
limit: eight engine/portfolio/summary checks against analytical targets and
four R/Python differences using combined independent-run uncertainty. The
design is two loans, n=10,000, $5,000 loss per default and p=0.1, with mean
loss $1,000 and joint probabilities 0.01/0.1. Maximum deviations are 2.30 SE
from targets and 1.683 SE across engines. Formulas, schema assumptions and
diagnostic fields are documented in [Scoring Validation](SCORING_VALIDATION.md).
These stochastic diagnostics are not counted as deterministic equivalence.

The focused comparator tests include deliberately corrupted deterministic and
simulation summaries. The integrated verification entry point is now
`python checks/verify.py`; its recorded-environment regression checks are
separate from the clean-install audit below.

## Integrated verification update, 15 October 2026

All seven chapters were rerun through `run.py` in the recorded environment.
The integrated check passed 211 book-result references, 1,027 compact numerical
checkpoints, frozen-input checksums and fresh-output hashes. All seven numerical
snapshots are unchanged from the preceding audit, and all 85 numbered figures
retain identical pixels. Four table exports changed in the intended descriptions
or percentage-point presentation.

All 66 unit tests passed. The complete Foundations/scoring comparison passed
133 deterministic groups and 12 separate Monte Carlo diagnostics. Merton passed
its existing optimizer-aware comparison; bonds, copulas and climate passed 75
deterministic/distribution checks and 27 sampling diagnostics. The documented
tree, XGBoost and random-stream differences remain explicit.

Frozen CSVs are marked as binary for Git newline handling, preserving their exact
recorded bytes on checkout. This update used the installed environment and did
not repeat the clean installation or refresh provider data.

## Clean installation

The 14 October clean-install test used a new Python 3.12.14 environment,
with system/user site packages disabled and dependencies installed from
`requirements-lock.txt`. Cached package wheels were allowed. `pip check`
passed. Quarto 1.5.54 was supplied separately; Jupyter configuration and
Matplotlib cache paths were isolated.

| Unit | Verification environment | Numeric comparison |
|---|---|---|
| Foundations | Clean installation, 14 October | Byte-identical JSON |
| Chapter 1 | Recorded environment, 15 October | Byte-identical JSON |
| Chapter 2 | Recorded environment, 15 October | Byte-identical JSON |
| Chapter 3 | Clean installation, 14 October | Byte-identical JSON |
| Chapter 4 | Clean installation, 14 October | Byte-identical JSON |
| Chapter 5 | Clean installation, 14 October | Byte-identical JSON |
| Chapter 6 | Clean installation, 14 October | Byte-identical JSON |

The five clean-install reports contain 130 numbered outputs and 55 nonblank
figures, including two unnumbered Foundations figures. Code links, report
anchors and embedded images passed. The clean test suite ran 31 tests;
the six model tests are covered by the complete 37-test scoring rerun above.
Missing-file checks verify that incomplete checkouts stop before Quarto starts.

## Technical file audit

`checks/audit_release.py` inspects the Git candidate without staging or
publishing it and saves a SHA256 manifest under `.local/release-audit.json`.
It verifies both scoring inputs against their reference hashes and checks
for unexpected binaries, generated outputs, credentials, broken relative
links and personal paths. It checks the 211 source-code result links and
keeps publisher files, contracts and instructor solutions outside this
reader package. These checks do not certify future additions automatically.

## Other source records

1. **Bond extract:** on 14 October 2026 the author chose to retain the 19 iShares
   observations after reviewing the source restrictions. The data are unchanged.
   Written permission remains unconfirmed; this author decision does not resolve
   redistribution rights. Source notices remain explicit in the data documentation.
2. **Climate extract:** on the same date the author chose to retain the limited
   CLIMACRED/DAPS extracts under the source license with attribution, copyright,
   source/license links, disclaimer reference and transformation notes. This
   decision relies on their chapter-specific scope, not on separate permission
   or a legal determination of substantiality. Reassess if the scope changes.

Supporting source notices are in [Data Sources and Release Review](DATA_TERMS.md).

## Remaining compatibility checks

Linux/macOS installation and execution have not been certified. Ubuntu was found
locally, but no Linux dependency environment was installed in this audit. The
documented tested platform remains Windows. A Linux/macOS test is recommended
before claiming cross-platform support; it is separate from the data decisions.

The optional live NGFS download was not refreshed. Frozen-data execution passed;
the download helper has mocked-response tests. Current API availability remains
unverified and does not affect the frozen-data computations.
