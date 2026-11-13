# benchmarks

<!-- org-sync:begin badges -->
[![Release](https://img.shields.io/github/v/release/swarm-routing/benchmarks?sort=semver&cacheSeconds=1800)](https://github.com/swarm-routing/benchmarks/releases)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24145189.svg)](https://doi.org/10.5281/zenodo.24145189)
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
legacy/<source>/<cell>/         a pre-org cell (ADR-0003): the file a release tag published + manifest.json; never read by verdicts
legacy/<source>/INDEX.md        the cells of that source, generated from the manifests
schemas/                        the manifest schemas (runs, legacy cells) and the marker-line contract versions
tools/validate_run.py           the validator CI runs on every PR (runs, legacy cells, immutability)
tools/import_anthocnet.py       imports AntHocNet's committed cells from a release tag into legacy/anthocnet/
tools/release/                  the dataset release: dist.sh (`make dist`), runs_notes.py (the runs each release adds)
CITATION.cff                    how to cite the dataset (type: dataset)
```

A manifest records (all required unless marked):

| Field | What |
|-------|------|
| `campaign`, `date` | the run directory is `<date>-<campaign>` |
| `base_image` | the `ghcr.io/swarm-routing/ns3:<ver>-optimized-<sha7>` tag (`ns3-dev:` before swarm-routing/.github#370; never a rolling tag), its `sha256:` digest, the ns-3 version, `profile: optimized` |
| `campaign_image` | the image every cell pulled, by ref and digest: a campaign image `<repo>-dev:<commit7>-<basesha7>` (or with the `-optimized` suffix `reusable-ns3-image.yml` pushes), or a release image `<repo>:<version>-optimized`; before swarm-routing/.github#370 they were `<repo>-ns3-campaign` and `<repo>-ns3`, which stay valid. Never the base package, never a rolling tag (`latest…`) |
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

The validator compares the manifest with the data, per cell and per seed slice
of a cell (a slice opens at each `##CONFIG## scenario=...` line; the
`##CONFIG## attr ...` lines are not compared):

| Manifest field | Compared with |
|----------------|---------------|
| `scenarios[].parameters` | each key the slice's `##CONFIG##` line carries has the same value there; a key it does not carry (`diag` today) is read from the slice's `##ARGS##` line, as `--key=value`, or `--key` for a `true` flag; a key the `##ARGS##` line carries has the same value there too |
| `scenarios[].arms` | the `protocols=` of `##CONFIG##` and the `--protocols=` of `##ARGS##` (in any order, where the line has one), and the arms of the `##RUN##` rows |
| `harness.program` | the first word of each `##ARGS##` line |
| `commands` | each `##ARGS##` line, whole, is one of them |
| `seeds` | the `##RUN##` rows: every arm ran each seed once |
| `base_image.digest`, `campaign_image.digest`, `modules[].commit` | every `##PROV##` line names them, and nothing else |

`##ARGS##` stays optional in marker contract v1 (the dispatching workflow
writes it for every cell today): a slice without one has its `commands` and
the parameters `##CONFIG##` lacks unchecked. Requiring it is a change of the
contract, so it belongs to version 2 (#33).

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

## Legacy (pre-org) data

[`legacy/`](legacy/) keeps the numbers measured before this repository's run
format existed: AntHocNet's committed `results/cells/`, each imported byte for
byte from the AntHocNet **release tag** that published it
([ADR-0003](docs/adr/0003-pre-org-results-are-a-frozen-legacy-archive.md), #7).
They are **not runs and not current results**: `verdicts/` and the overview
read `runs/` only, so a legacy number never enters a ranking. Anything that
shows one labels it pre-org.

Each `legacy/<source>/<cell>/manifest.json` follows
[`schemas/legacy-manifest.schema.json`](schemas/legacy-manifest.schema.json):

| Field | What |
|-------|------|
| `provenance` | always `pre-org` |
| `cell`, `family` | the cell's name (the directory) and its family (the name prefix) |
| `source` | the repository, release tag, the tag's commit, the path and the file's sha256 |
| `measured` | each commit the cell's `##PROV##` lines name, with its ref (often a branch), run ids, and whether it contains swarm-routing/AntHocNet#459's fix (`contains_fix`: from git, GitHub's compare API, or `unresolved`) |
| `images` | each image `##PROV##` names; a rolling tag (e.g. `ghcr.io/danieljoppi/ns3:3.42-opt`) carries its digest of record from AntHocNet `docker/README.md` "Images of record", `verified: false`, where and when that digest was read |
| `arms` | the arms and the seeds each ran, as found |
| `defects` | what the cell breaks, declared: `garbled-marker`, `no-prov`, `multi-commit`, `duplicate-seed`, `seeds-below-20` |
| `invalid` | `##COMMON##`/`##MATCH##` of a cell not known to contain the #459 fix, flagged with swarm-routing/AntHocNet#460 (imported and flagged, never dropped) |
| `supersedes` (optional) | what this newer record replaces: a legacy cell, or a page at a pinned commit (tables never committed as cells) |

`validate_run.py legacy all` recomputes the defects, the `invalid` entry, the
arms, the commits and the images from each cell and requires them equal to
the manifest; `immutable` covers `legacy/` too. Supersession is carried by the
newer record only, and `INDEX.md` derives "superseded by" from it, so no
merged manifest is ever edited.

Import a family (one family per PR, from a release tag; `--ns3-tools` is the
`python/` directory of the ns3-tools release AntHocNet's `ns3-tools.lock`
pins, v0.1.0 today, whose `bench_parse` must accept every cell; `--src` is an
AntHocNet clone with its tags):

```bash
git clone -q https://github.com/swarm-routing/AntHocNet ../AntHocNet
git clone -q --depth 1 --branch v0.1.0 https://github.com/swarm-routing/ns3-tools ../ns3-tools-v0.1.0
python3 -I tools/import_anthocnet.py --src ../AntHocNet --tag v2.6.1 --family static-mesh \
    --ns3-tools ../ns3-tools-v0.1.0/python
python3 -I tools/validate_run.py legacy all
```

## Releases

The dataset is released in versions, each tagged `vX.Y.Z` and archived on
Zenodo with its own DOI, so a published number cites the exact version that
holds its run ([#39](https://github.com/swarm-routing/benchmarks/issues/39)).
Versions are [SemVer](https://semver.org), computed by Commitizen from the PR
titles (Conventional Commits) since the last tag:

| Change | PR title | Version |
|--------|----------|---------|
| a new run (or a correction, which is a new run) | `feat(runs): <date>-<campaign> ...` | minor |
| a fix, or a docs change that should ship (tooling, README, schema docs) | `fix: ...`, `fix(docs): ...` | patch |
| a manifest `schema_version` or marker-contract version change | `feat(schemas)!: ...` (a breaking change) | major (minor while 0.x) |

A `docs:`, `ci:` or `chore:` title bumps nothing: Commitizen's
`cz_conventional_commits` maps only `feat`, `fix`, `refactor`, `perf` and
breaking changes, so a release made only of those fails to bump.

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
concept DOI (the badge) always resolves
to the latest version; a number cites a version DOI.

<!-- org-sync:begin citing -->
## Releases & citing

Versions follow [SemVer](https://semver.org) ([CHANGELOG.md](CHANGELOG.md)). Each release is listed under [Releases](https://github.com/swarm-routing/benchmarks/releases), built by the org's release workflow and archived on [Zenodo](https://zenodo.org) with its own DOI.

To cite these data, use the “Cite this repository” button (from [CITATION.cff](CITATION.cff)):

| DOI | resolves to |
|---|---|
| [`10.5281/zenodo.24145189`](https://doi.org/10.5281/zenodo.24145189) | **concept DOI**: always the latest release. This is the badge above, and the right citation when you mean this project. |

Each release also has its own **version DOI**, listed on [its Zenodo record](https://doi.org/10.5281/zenodo.24145189): cite that one when you reproduce a number measured at that release.

Please also cite the work it builds on:

- D. H. Joppi, *AntHocNet for NS-3*, 2026, [doi:10.5281/zenodo.20981979](https://doi.org/10.5281/zenodo.20981979). The protocol module the recorded runs build and measure, at the commit each run's manifest pins.
- D. Joppi, *swarm-routing/ns3-tools: v0.1.0*, 2026, [doi:10.5281/zenodo.24136068](https://doi.org/10.5281/zenodo.24136068). The routing-bench harness and campaign image every recorded run comes from, at the commit each run's manifest pins.
- G. F. Riley, T. R. Henderson, *The ns-3 Network Simulator*, Modeling and Tools for Network Simulation, pp. 15–34, 2010, [doi:10.1007/978-3-642-12331-3_2](https://doi.org/10.1007/978-3-642-12331-3_2). ns-3, the simulator every recorded run ran on, in the ns3-dev image each run's manifest pins by digest.

Using it in your work? Contributions are welcome, and citing the DOI helps just as much.
<!-- org-sync:end citing -->

## Epics

<!-- epics:begin -->
<!-- Generated by swarm-routing/.github tools/epics/epics.py from the issues labelled `epic`; edit the issues, then re-run it. -->

What is planned and in progress here: the issues labelled [`epic`](https://github.com/swarm-routing/benchmarks/issues?q=label%3Aepic). An epic's open sub-issues carry a `priority:*` and a `model:*` label, so a contributor or an AI agent can pick one up ([how issues work](https://github.com/swarm-routing/.github/blob/main/CONTRIBUTING.md#issues)). The whole org's plan: the [roadmap](https://github.com/swarm-routing/.github/blob/main/ROADMAP.md#epics).

No open epic: the work here is tracked as single issues.

<!-- epics:end -->

## Licence

See [LICENSING.md](LICENSING.md).
