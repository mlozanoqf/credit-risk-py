# Clean Installation and Publication Audit

Audit date: 14 October 2026. Status: **clean Windows execution passed; public
release authorized by the author with credit-scoring inputs excluded and the
iShares extract retained. iShares redistribution rights remain unconfirmed**.
The clean-install audit preceded the initial commit and public release.

## Clean installation

A temporary copy was assembled from the files Git would include, without the
original `.venv`, `.local`, `.quarto`, outputs, Git metadata or restricted loan
inputs. A new Python 3.12.14 virtual environment was created with system/user
site packages disabled. Dependencies were installed from `requirements-lock.txt`
using the PyPI index (cached package wheels were allowed). `pip check` passed.
Quarto 1.5.54 was supplied separately, as required by the setup instructions.
Jupyter configuration and Matplotlib cache paths were isolated for this run.

| Unit | Clean execution | Numeric comparison with prior Python run |
|---|---|---|
| Foundations | Passed | Byte-identical JSON |
| Chapter 1 | Intentionally unavailable without restricted inputs | No execution or output |
| Chapter 2 | Intentionally unavailable without restricted inputs | No execution or output |
| Chapter 3 | Passed | Byte-identical JSON |
| Chapter 4 | Passed with local frozen bond extract | Byte-identical JSON |
| Chapter 5 | Passed | Byte-identical JSON |
| Chapter 6 | Passed with local frozen climate extract | Byte-identical JSON |

The five successful reports contain 130 numbered outputs and 55 nonblank
figures, including two unnumbered Foundations figures. Code links, HTML result
anchors and embedded images passed validation. No R installation or sibling
project is used by the reader calculations. Existing comparisons with R remain
documented in the three numerical-validation reports.

The clean suite discovered 37 tests: 31 passed and six scoring-model tests were
explicitly skipped because the restricted data were absent. Classification and
policy tests still ran with small, explicitly constructed test inputs. Missing
dataset/manifest combinations were tested for both scoring chapters. Direct
attempts to run Chapters 1-2 returned a clear error before starting Quarto;
no download, partial model output or replacement data were generated.

## Technical publication audit

`checks/audit_release.py` inspects the current Git candidate without staging it.
Its per-file SHA256 manifest is saved locally under `.local/release-audit.json`.
The audit found no restricted data, trained scoring models, individual prediction
files, rendered reports, PDFs, contracts or instructor solutions in that candidate.
The scoring dataset, split manifest and generated outputs remain ignored. There
are no existing Git refs or remote, so there is no prior committed history to
scrub in this Python repository. A new audit is necessary if that state changes.

The source scan found no embedded credential matching the checked patterns,
personal absolute paths in executable source, or reader dependency on maintainer
R exports. Relative documentation links and all 211 source-code result links
were checked. These checks reduce accidental-disclosure risk; they do not replace
review of future additions or constitute a general security certification.

Two small execution improvements were made during the audit. `run.py` now
checks restricted-input availability before launching Quarto. The output checker
accepts `--chapters` so that readers can verify the available units without
having scoring outputs. Financial calculations and reference data were unchanged.

## Decisions before release

1. **Loan data:** remain excluded pending permission. The code can be distributed
   with that limitation, but full replication of Chapters 1-2 remains unavailable
   to readers without the reference dataset and split manifest.
2. **Bond extract:** on 14 October 2026 the author chose to retain the 19 iShares
   observations after reviewing the source restrictions. The data are unchanged.
   Written permission remains unconfirmed; this author decision does not resolve
   redistribution rights. Source notices remain explicit in the data documentation.
3. **Climate extract:** on the same date the author chose to retain the limited
   CLIMACRED/DAPS extracts under the source license with attribution, copyright,
   source/license links, disclaimer reference and transformation notes. This
   decision relies on their chapter-specific scope, not on separate permission
   or a legal determination of substantiality. Reassess if the scope changes.
4. **Author approval:** the author subsequently authorized the final file audit
   and public release, explicitly keeping the credit-scoring data excluded and
   retaining iShares. This is publication authorization from the author, not
   source-rights clearance. The first-release audit must pass before committing.

Supporting official links and source-specific conditions are in
[Data Sources and Release Review](DATA_TERMS.md). The source review is not a
legal opinion. The code's GPL-3.0 license does not resolve data rights.

## Remaining compatibility checks

Linux/macOS installation and execution have not been certified. Ubuntu was found
locally, but no Linux dependency environment was installed in this audit. The
documented tested platform remains Windows. A Linux/macOS test is recommended
before claiming cross-platform support; it is separate from the data decisions.

The optional live NGFS download was not refreshed. Frozen-data execution passed;
the download helper has mocked-response tests. Current API availability remains
unverified and does not affect the frozen-data computations.
