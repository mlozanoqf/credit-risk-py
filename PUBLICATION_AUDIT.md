# Clean Installation and Publication Audit

## Current verification

The repository contains the complete frozen scoring dataset and reference
split. Their source and modifications are described in the
[provenance note](data/credit-scoring/PROVENANCE.md).
Both companion repositories remain private until book publication.

On 15 October 2026, both scoring chapters executed independently in the
recorded Windows environment and reproduced byte-identical numeric JSON
snapshots. All 37 tests passed, with none skipped. Checks covered 81 numbered
results, 32 nonblank figures, code links and report anchors. The R split
export matches the supplied manifest exactly.

The maintainer comparison with `--scoring-only` passes 77 deterministic groups
covering 670,292 values. Logistic predictions agree with R to about 3.6e-12.
Documented CART and XGBoost differences remain unchanged. This scoring rerun
used existing packages and is distinct from a clean dependency installation.
Foundations has separate local additions; the generic combined comparison
needs its Foundations mapping updated before its next use.

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
