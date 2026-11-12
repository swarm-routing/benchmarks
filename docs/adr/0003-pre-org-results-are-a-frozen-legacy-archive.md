# 0003. The pre-org AntHocNet results are a frozen legacy archive, apart from the runs

- **Status:** accepted (maintainer, 2026-11-12, option A of the [#7 pre-registration](https://github.com/swarm-routing/benchmarks/issues/7#issuecomment-6811996510))
- **Date:** 2026-11-12
- **Issue:** #7

## Context

Every benchmark number the org had before this repository lives in
swarm-routing/AntHocNet's `results/`. At the v2.6.1 release that is 420 cells
in `results/cells/` (16.6 MB) and 275 classified campaign CSVs. #7 imports
them here as a legacy dataset labelled pre-org, so that comparisons do not
start from nothing and the published numbers stay traceable.

The data cannot be held as runs. Each point breaks a rule of
`manifest.schema.json` v1, `validate_run.py` or [ADR-0002](0002-benchmarks-records-released-versions.md):

- **Images.** 419 cells name a rolling tag in `##PROV##`:
  `image=ghcr.io/danieljoppi/ns3:3.42-opt` in 310 cells,
  `ghcr.io/danieljoppi/ns3:3.48` in 109. None names a base digest or a
  campaign-image digest. AntHocNet's `docker/README.md` "Images of record"
  gives their digests, read from the registry on 2026-11-11, after the runs.
  For some cells, the bytes those digests name are not proven to be the bytes
  the run used. Manifest v1 requires an `ns3-dev:<ver>-optimized-<sha7>` base
  and a campaign image by digest, and `validate_run.py` requires each
  `##PROV##` to name both.
- **Sources.** Many cells were measured on branch commits (`ref=claude/...`),
  some at more than one commit. ADR-0002 records released versions only.
- **Seeds.** 56 cells have fewer than 20 seeds per arm (golden rule 6).
- **Garbled lines.** Some cells carry lines a log interleaving garbled
  (`##AI##RSS## ...`), which marker contract v1 rejects.
- **#460.** Cells measured before swarm-routing/AntHocNet#459
  (`1a7c32b9538d9a1d9449a00c114286ad49f64c93`) have `##COMMON##`/`##MATCH##`
  rows whose keys name a different transmission in each arm
  (swarm-routing/AntHocNet#460). The per-arm markers stand. The maintainer
  decided on #7 (2026-11-09) that such cells are imported and flagged, never
  dropped.
- **No forward pointers.** v1 has `additionalProperties: false`, so a
  `provenance` field would bump `schema_version`: a breaking change of this
  dataset. A `superseded_by` field in an immutable record could never be
  filled in later without editing a merged file (golden rule 10).

## Decision

1. **A separate tree.** Pre-org cells live in `legacy/<source>/<cell>/`
   (`legacy/anthocnet/` for AntHocNet), never under `runs/`. Each cell
   directory holds the cell file, byte-identical to the file a release tag
   published, and its `manifest.json`. `legacy/<source>/INDEX.md` lists them.
   It is generated from the manifests and never edited by hand.
2. **Its own schema.** `schemas/legacy-manifest.schema.json` has its own
   `schema_version: 1` and `provenance: "pre-org"`. `manifest.schema.json` v1
   is unchanged. A legacy manifest records:
   - the source repository, the **release tag** and the commit it names, the
     path and the sha256;
   - every `##PROV##` commit with its ref, its run ids and whether it contains
     the #459 fix (from git, else GitHub's compare API, else `unresolved`);
   - every image as `##PROV##` names it. A rolling tag carries its digest of
     record with `verified: false`, where it was read (a blob at a pinned
     commit) and when; a digest `##PROV##` names itself is `verified: true`;
   - the arms and seeds found;
   - the declared defects;
   - the `invalid` entry #460 requires;
   - optionally, what it `supersedes`.
3. **The exception to ADR-0002.** A legacy cell is importable because a
   protocol release tag published it: the released thing is the release tree
   that carried the number, not the measured commit. A file that no release
   tag holds yet waits for the next release. The import adds cells per
   release, and only through `tools/import_anthocnet.py`. The archive closes
   for a source once that repository stops committing cells, because every new
   number goes through `runs/` (ADR-0002).
4. **Never a current result.** `verdicts/` and the overview (#25) read
   `runs/` only. A legacy number cannot enter a current ranking or verdict:
   that follows from the layout, not from a flag someone must remember to
   filter. A comparison that shows legacy numbers recomputes them from
   `legacy/` with the ns3-tools readers and labels them pre-org.
5. **Defects are declared, not hidden.** The validator recomputes the
   defects (`garbled-marker`, `no-prov`, `multi-commit`, `duplicate-seed`,
   `seeds-below-20`) and the #460 `invalid` entry from the cell and the
   recorded ancestry, and requires both lists equal. An undeclared defect
   fails, and so does a stale one. Nothing is dropped and nothing is padded.
6. **Supersession is carried by the newer record.** A later legacy cell that
   replaces a legacy number names it in its own `supersedes`. A run under
   `runs/` cannot do so yet: manifest v1's `supersedes` takes a run name only,
   so a run naming a legacy cell needs that schema changed first (see
   Consequences). A target is either a
   legacy cell, or a page at a pinned commit for tables that were never
   committed as cells, such as `grid.md`'s superseded #460 tables. The index
   derives "superseded by" from those entries. No merged manifest is edited to
   point forward.
7. **The golden rules, as they apply here.**
   - Rule 10 holds unchanged: `immutable` covers `legacy/`. Only the generated
     `INDEX.md` may change, and `validate_run.py legacy` checks it equals its
     regeneration.
   - Rule 11 is met by the legacy manifest. It pins the tag, the commits and
     each image with its digest of record. It does not pin an ns3-dev image,
     which these runs never used.
   - Rule 12 holds because no verdict reads `legacy/`.
   - Rule 13 is recorded per cell (`profile=` in `##PROV##`), not enforced.

## Consequences

- **What the import keeps.** The pre-org numbers are kept, with what is known
  and what is not stated in their manifests. The leaderboard and comparisons
  can show them only as pre-org.
- **Two schemas.** `validate_run.py` maintains the run schema and the legacy
  schema separately. A change to either bumps only its own `schema_version`.
- **What it cannot do.** A run under `runs/` cannot yet name a legacy cell in
  its v1 `supersedes`, which takes a run name. Until that is needed, the
  relation lives on the legacy side: a newer legacy cell, such as AntHocNet
  v2.7.0's `g460` cells. Widening v1's `supersedes` is a manifest schema
  change.
- **Import order.** The import goes one family per PR:
  - static-mesh at v2.6.1 first;
  - then the remaining families;
  - the `g460` cells with their `supersedes` once AntHocNet v2.7.0 is
    released;
  - `results/campaign/`, which holds aggregates and not marker lines (#7
    acceptance criterion 2), separately.
