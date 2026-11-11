# benchmarks

<!-- org-sync:begin badges -->
[![Release](https://img.shields.io/github/v/release/swarm-routing/benchmarks?sort=semver&cacheSeconds=1800)](https://github.com/swarm-routing/benchmarks/releases)
[![Cite](https://img.shields.io/badge/cite-CITATION.cff-blue)](CITATION.cff)
[![Licence: GPL-2.0-only, tools/ MIT OR GPL-2.0-only](https://img.shields.io/badge/licence-GPL--2.0--only%2C%20tools%2F%20MIT%20OR%20GPL--2.0--only-blue)](LICENSING.md)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow)](https://www.conventionalcommits.org)
[![Colony Arena: benchmarks](https://img.shields.io/badge/Colony%20Arena-project%20page-orange)](https://swarm-routing.github.io/arena/benchmarks/)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/swarm-routing/benchmarks/badge)](https://scorecard.dev/viewer/?uri=github.com/swarm-routing/benchmarks)
<!-- org-sync:end badges -->

The org's immutable benchmark datasets: 20-seed `##RUN##`/`##BENCH##` data,
paired statistical verdicts, and a reproducibility manifest for every run
(image digest, protocol commits, scenario, seeds, command). It records
**released versions**; each protocol repository benchmarks its own changes
([ADR-0002](docs/adr/0002-benchmarks-records-released-versions.md)).
**Status:** the format and its validator are in place and one run is recorded,
landed by hand. Planned (epic swarm-routing/.github#156): a run started by every
protocol release, new supported ns-3 release or tool release (#24), and the
overview across protocols generated from those runs (#25).

How to work here, for people and AI agents alike: [AGENTS.md](AGENTS.md) has
the rules and how to build and verify; the org conventions are in
[CONTRIBUTING.md](https://github.com/swarm-routing/.github/blob/main/CONTRIBUTING.md).

## Layout

```
runs/<yyyy-mm-dd>-<campaign>/   one run, immutable once merged
  manifest.json                 what reproduces it (schemas/manifest.schema.json)
  cells/<cell>.txt              the raw marker lines, as the harness and workflow printed them
  <preregistration>             the plan, when it is a file here rather than a pinned URL
verdicts/                       (planned) paired comparison tables, recomputed from runs/ by a script
schemas/                        the manifest schema and the marker-line contract versions
tools/validate_run.py           the validator CI runs on every PR
tools/release/                  the dataset release: dist.sh (`make dist`), runs_notes.py (the runs each release adds)
CITATION.cff                    how to cite the dataset (type: dataset)
```

A manifest records (all required unless marked):

| Field | What |
|-------|------|
| `campaign`, `date` | the run directory is `<date>-<campaign>` |
| `base_image` | the `ghcr.io/swarm-routing/ns3-dev:<ver>-optimized-<sha7>` tag (never a rolling tag), its `sha256:` digest, the ns-3 version, `profile: optimized` |
| `campaign_image` | the image every cell pulled, by ref and digest: `<repo>-ns3-campaign:<commit7>-<basesha7>` (or with the `-optimized` suffix `reusable-ns3-image.yml` pushes), or a release image `<repo>-ns3:<version>-optimized` |
| `modules` | every module built into that image (protocols, `swarm-core`, `routing-bench`, each arm), with its repository and 40-character commit |
| `harness` | the program (`routing-compare`) and the module that holds it |
| `scenarios` | each cell: its name, its arms, its parameters |
| `preregistration` | the plan, a file in the run or a pinned GitHub URL |
| `seeds` | the RngRun values, at least 20; every arm of every scenario runs each once |
| `commands` | the exact command lines |
| `markers.schema_version` | the marker contract, `schemas/markers/v<N>.json` |
| `files` | every other file of the directory, with its sha256; a cell names its scenario |
| `supersedes` (optional) | the run this one corrects and the issue that says why |
| `notes` (optional) | free text |

[`schemas/examples/manifest.example.json`](schemas/examples/manifest.example.json)
is a complete example (its digests and commits are made up).

## Adding a run

1. **Pre-register.** Write the plan (scenarios, arms, seeds, the trend
   expected) as an issue or a file before dispatch.
2. **Dispatch.** The campaign driver resolves the base `ns3-dev` tag to its
   digest, builds one campaign image of the commits under test, and runs every
   cell from that image by digest (swarm-routing/.github#107). Every cell's
   `##PROV##` line names the base digest, the campaign-image digest and every
   module commit.
3. **Collect.** Put each cell's raw output under `runs/<date>-<campaign>/cells/`
   unedited, and write `manifest.json` listing every file with its sha256.
4. **Validate.** `python3 -I tools/validate_run.py check runs/<date>-<campaign>`
   until it prints `OK`.
5. **PR.** One run per PR. CI validates every run and refuses any change to a
   merged one.

## Corrections

A merged run is never edited or deleted (golden rule 10); CI fails a PR that
changes, removes or adds a file in one. A correction is a new run whose
manifest says what it replaces:

```json
"supersedes": {
  "run": "2026-11-20-ara-anchor",
  "issue": "https://github.com/swarm-routing/benchmarks/issues/<n>"
}
```

Open the issue first: it says what was wrong with the old run. Both runs stay
in the repository.

## Releases

The dataset is released in versions, each tagged `vX.Y.Z` and archived on
Zenodo with its own DOI, so a published number cites the exact version that
holds its run ([#39](https://github.com/swarm-routing/benchmarks/issues/39)).
Versions are [SemVer](https://semver.org), computed by Commitizen from the PR
titles (Conventional Commits) since the last tag:

| Change | PR title | Version |
|--------|----------|---------|
| a new run (or a correction, which is a new run) | `feat(runs): <date>-<campaign> ...` | minor |
| a fix or a docs change (tooling, README, schema docs) | `fix: ...`, `docs: ...` | patch |
| a manifest `schema_version` or marker-contract version change | `feat(schemas)!: ...` (a breaking change) | major (minor while 0.x) |

**When.** A version is cut deliberately, never on a schedule or on every
merge: its scope is the set of issues carrying its `release:vX.Y.Z` label, set
when the issue is opened or triaged. A run that should be citable is scheduled
into a release by its issue's release label. When that version's issues are
done, the maintainer (or an agent on their instruction) dispatches the
`Release` workflow with mode `bump`; it opens `chore(release): bump version A
to B`, and merging that PR publishes the release (swarm-routing/.github
CONTRIBUTING "Cutting a release"). v0.1.0 holds the first run,
`runs/2026-11-10-anthocnet-aodv-smoke`.

**What a release holds.** Its notes list every run it adds, each with its
directory and every pinned input of its manifest (the base `ns3-dev` image by
tag and digest, the campaign image digest, every module commit, the harness,
the scenarios, the seeds and the exact commands), any run it supersedes, and
the verdicts it adds (`tools/release/runs_notes.py`, Commitizen's pre-bump
hook, writes them into `CHANGELOG.md`). Its asset `benchmarks-X.Y.Z.tar.gz`
holds `runs/`, `verdicts/`, `schemas/`, `tools/`, the licence texts, this
README, `CITATION.cff`, `RUNS.md` (every run with its pins) and
`SHA256SUMS.txt`; `make dist` builds it, byte for byte the same from the same
commit, after `tools/validate_run.py all` passes. The release also carries
`SHA256SUMS`, a CycloneDX SBOM and signed build provenance, with the verify
commands in its notes. Zenodo archives the whole tagged tree.

## How to cite a number

Cite the dataset version that first contains the run, by its version DOI
(the release's Zenodo record; [`CITATION.cff`](CITATION.cff) has the
metadata), and name the run directory, for example: *swarm-routing benchmarks
vX.Y.Z, doi:10.5281/zenodo.NNNN, `runs/2026-11-10-anthocnet-aodv-smoke`*. The
run's `manifest.json` in that version reproduces the number: the image
digests, the module commits, the scenario, the seeds and the commands. The
concept DOI (the badge, once the first release is archived) always resolves
to the latest version; a number cites a version DOI.

## Epics

<!-- epics:begin -->
<!-- Generated by swarm-routing/.github tools/epics/epics.py from the issues labelled `epic`; edit the issues, then re-run it. -->

What is planned and in progress here: the issues labelled [`epic`](https://github.com/swarm-routing/benchmarks/issues?q=label%3Aepic). An epic's open sub-issues carry a `priority:*` and a `model:*` label, so a contributor or an AI agent can pick one up ([how issues work](https://github.com/swarm-routing/.github/blob/main/CONTRIBUTING.md#issues)). The whole org's plan: the [roadmap](https://github.com/swarm-routing/.github/blob/main/ROADMAP.md#epics).

No open epic: the work here is tracked as single issues.

<!-- epics:end -->

## Licence

See [LICENSING.md](LICENSING.md).
