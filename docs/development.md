# Developer guide

This repository holds the org's benchmark data: one directory per run under
`runs/` (the raw marker lines of every cell plus a `manifest.json` that pins
every image digest, module commit, scenario and seed), the older numbers
imported into `legacy/`, the JSON schemas they follow, and the Python
validator CI runs on every pull request. Most changes here add a run or fix a
tool; a merged run is never edited. This page shows how to set up, validate,
lint and release, and what CI checks. The rules are in
[AGENTS.md](../AGENTS.md) ("Golden rules"); how a run gets here is the
README's "Adding a run"; how issues and pull requests work is in the org's
[CONTRIBUTING.md](https://github.com/swarm-routing/.github/blob/main/CONTRIBUTING.md).

## Prerequisites

| Tool | Version | Needed for |
| --- | --- | --- |
| Linux or macOS, `git`, `make` | any recent | everything |
| Python | 3.11 or newer | the validator and its tests (standard library only) |
| ruff | 0.17.1 | Python lint and format |
| actionlint | 1.7.12 (`pip install actionlint-py==1.7.12.25`) | `make lint` |

Producing new benchmark numbers is not done here: runs are made with
swarm-routing/ns3-tools (`ns3-campaign`) on the `ns3-dev` images and only
their output lands in this repository.

## Get the code

```bash
git clone https://github.com/swarm-routing/benchmarks.git
cd benchmarks
```

There are no submodules. A run's raw files can be large; a shallow clone
(`--depth 1`) is enough to add a run.

## Dependencies

None to install: the tools use the Python standard library. The marker-line
contract a run's cells follow is `schemas/markers/v<N>.json`, owned by
swarm-routing/ns3-tools (its `docs/markers.md`); the readers that recompute a
verdict are ns3-tools' `ns3-tool` package (`pip install ns3-tools`, or
`pip install ./python` from a checkout). The release-lock and vcpkg plans of
swarm-routing/.github#489 do not apply to a data repository.

## Build

Nothing compiles here (`make build` says so). The one artifact is the
dataset release tarball:

```bash
make dist   # dist/benchmarks-<ver>.tar.gz, every run validated first
```

## Test

| What | Command | CI (`runs.yml`, check `validate runs`) |
| --- | --- | --- |
| the validator's self-test on fixtures | `python3 -I tools/validate_run.py --self-test` | yes |
| the release notes script | `python3 -I tools/release/runs_notes.py --self-test` | yes |
| the example manifest | `python3 -I tools/validate_run.py manifest schemas/examples/manifest.example.json` | yes |
| every run validates | `python3 -I tools/validate_run.py all` | yes |
| one run | `python3 -I tools/validate_run.py check runs/<date>-<campaign>` | (part of `all`) |
| the legacy importer and every legacy cell | `python3 -I tools/import_anthocnet.py --self-test && python3 -I tools/validate_run.py legacy all` | yes |
| no merged run changed | `git fetch origin main && python3 -I tools/validate_run.py immutable --base origin/main` | yes |
| the same self-tests as plain test scripts, as the coverage run | `python3 tools/test_validate_run.py && python3 tools/test_import_anthocnet.py` (without `-I`: they import the tool beside them) | `quality / python` |

`make test` runs the first and the example-manifest check. Each command
prints `OK` (or `ok`) per item when it passes.

## Run

Adding a run, in short (the README "Adding a run" has the details):

1. Pre-register the plan in an issue or a file.
2. Run it with ns3-tools' `ns3-campaign` (`dispatch`, then `collect`), which
   pins every cell to one campaign image by digest.
3. Copy the raw cell files, unedited, to `runs/<yyyy-mm-dd>-<campaign>/cells/`
   and write `manifest.json` (the schema is
   `schemas/manifest.schema.json`; `schemas/examples/` has a valid example).
4. `python3 -I tools/validate_run.py check runs/<yyyy-mm-dd>-<campaign>` until
   it prints `OK`.
5. Open one PR per run, titled `feat(runs): ...`.

A correction is a new run that names the one it supersedes, with an issue
explaining why.

## Docker and dev containers

Nothing here needs Docker. `make shell` opens a shell in the `ns3-dev` image
with this checkout at `/src`, useful only to look at a run beside ns-3.
There is no `.devcontainer/`.

## Lint and format

```bash
make lint      # actionlint, then ruff check and ruff format --check with the org's ruff.toml
ruff format --config ~/.cache/swarm-routing/dotgithub/ruff.toml tools   # fix formatting (after one make lint)
make headers   # licence headers (fetches the org tools)
make org-sync-check
make check     # lint, test, headers and org-sync together
```

## CI map

| Workflow | Job (check name) | What it checks | Required |
| --- | --- | --- | --- |
| `runs.yml` | `validate runs` | the self-tests, every run and legacy cell validates, no merged run changed | yes |
| `runs.yml` | `quality / python` | ruff, the Python tests with coverage | yes |
| `runs.yml` | `licence / licence` | licence headers | yes |
| `org-sync.yml` | `check / org-sync` | the org-managed files match the templates | yes |
| `pr-title.yml` | `title / title` | the PR title is a lowercase Conventional Commit | yes |
| `review-gate.yml` | `review / coderabbit` | CodeRabbit has reviewed the PR | yes |
| `release.yml` | | the dataset release (dispatched) | no |
| `dco.yml`, `scorecard.yml`, `sync-labels.yml` | | sign-off on outside contributions; OpenSSF Scorecard; labels | no |

The required checks are the ones the `main` ruleset lists: `gh api
repos/swarm-routing/benchmarks/rules/branches/main`. `main` merges through a
merge queue, so a pull request is merged by enabling auto-merge.

## Release

Releases follow the org procedure: [CONTRIBUTING "Cutting a release"](https://github.com/swarm-routing/.github/blob/main/CONTRIBUTING.md#cutting-a-release).
Versions are SemVer: a run PR (`feat(runs): ...`) is a minor, a fix a patch,
a manifest or marker `schema_version` change a major. When the issues of a
version's `release:vX.Y.Z` label are done, dispatch `release.yml` with mode
`bump` and merge the bump PR; the release ships `benchmarks-<ver>.tar.gz`,
and `tools/release/runs_notes.py` writes the runs it adds into
`CHANGELOG.md`. Each release gets a Zenodo DOI (the README's "Releases &
citing").

## Troubleshooting

- **`immutable` fails.** The PR changes a file under a merged run or
  `legacy/`. Revert it; a correction is a new run.
- **`check` says a file is not listed or its sha256 differs.** Every file in
  the run directory must be in `manifest.json` with its sha256
  (`sha256sum <file>`), and the file must be the raw output, unedited.
- **`check` says an arm ran the wrong seeds.** Each arm of each scenario must
  have run exactly the manifest's seeds, at least 20.
- **`check` rejects a `##PROV##` line.** It must name the base digest, the
  campaign-image digest and every module commit in the manifest, and nothing
  else; collect the cells again with `ns3-campaign collect`.
- **A new schema keyword fails the self-test.** The validator interprets a
  fixed set of keywords; teach it the new one in the same PR.
- **`make lint` stops at `actionlint: command not found`.** Install it as in
  "Prerequisites".
