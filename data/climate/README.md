# Frozen NGFS/IIASA Climate Inputs

The three CSVs are byte-identical copies of the R companion inputs. The manifest
retains the original `data/raw/` paths; this project stores the files in
`data/climate/`. Original download timestamps and source observations are preserved.

- `ngfs_climacred_global_raw.csv`: global CLIMACRED sector metrics for DIRE,
  HWTP and SWUC, 2022-2030.
- `ngfs_climacred_daps_raw.csv`: regional DAPS physical-risk PD adjustments,
  2024-2030.
- `ngfs_climacred_download_manifest.csv`: file rows, source database, endpoint
  and download timestamps.

The data come from the NGFS Phase 5 Short Term Scenario Explorer / IIASA API.
The chapter preserves raw metric names, units and sector names before reshaping
and joining the explicit illustrative portfolio. Code licensing does not confer
rights over third-party data; retain NGFS/IIASA attribution and source conditions.
The [official license](https://data.ece.iiasa.ac.at/ngfs-phase-5-short-term/#/license)
is adapted from CC BY 4.0 and restricts redistribution of substantial portions
of the database. Copyright IIASA 2022 is displayed on that license page. The
data are provided without warranties, subject to the disclaimer and liability
provisions in Section 5 of that license. Neither NGFS nor IIASA endorses this
companion or its interpretations.

The author has chosen to retain the 1,350 global and 126 regional observations
as limited extracts supporting the chapter's reproducible calculations. The
license provides no numerical threshold for substantiality, and no separate
provider confirmation has been obtained. See [data terms](../../DATA_TERMS.md).
These frozen observations were downloaded on 4 June 2026 (UTC); they are not
a current or complete copy of the
[official database](https://data.ece.iiasa.ac.at/ngfs-phase-5-short-term/).
Selection and CSV serialization precede the chapter's documented transformations;
the Python translation does not alter the source values. Retain attribution,
copyright, source and license links, the disclaimer reference and an indication
of modifications in any redistribution. Review the scope again before expanding
or refreshing the extracts.

An optional Python translation of the source request is in
`chapters/06-climate-credit-risk/helpers/download_data.py`. From the project root:

```powershell
.venv\Scripts\python.exe chapters/06-climate-credit-risk/helpers/download_data.py --destination .local/ngfs-refresh
```

Use a new destination. The command requires internet access, writes a new manifest,
and refuses to overwrite an existing directory. Rendering never calls the API.
The optional request has been checked with mocked responses; live availability
has not been tested during this translation. A new download may reflect revised
values or an API change and requires separate validation before adoption.
