# CONTEXT.md — orientation and history

Background an agent or a new contributor needs that does not belong in
`AGENTS.md`: domain notes, current state, glossary, open questions. Read the
section a task needs, not the whole file.

## Current state

**Status: one run recorded and released.**
`runs/2026-11-10-anthocnet-aodv-smoke/` (AntHocNet against AODV, two
scenarios, 20 paired seeds; landed by hand) is the first run, and v0.1.0
(2026-11-11) the dataset version that holds it, archived on Zenodo under the
concept DOI [`10.5281/zenodo.24145189`](https://doi.org/10.5281/zenodo.24145189)
(`CITATION.cff`). No verdict is recorded yet (`verdicts/` is planned). The run
layout, the manifest schema (`schemas/manifest.schema.json`), the marker
contract v1 (`schemas/markers/`) and the validator CI runs
(`tools/validate_run.py`) landed with #3, before the first data, so the first
run did not set the format by accident. The manifest follows swarm-routing/.github#107: one
campaign image per (commits, ns3-dev digest), every cell pulled by digest, and
the manifest and every `##PROV##` line naming the base digest, the
campaign-image digest and every module commit.

**What is recorded (ADR-0002).** Released versions only: a run starts when a
protocol, a supported ns-3 release in `ns3-dev`, or `ns3-tools` publishes a
release. Change tests and anchors stay in each protocol repository. Planned (swarm-routing/.github#156): suites
(#23), release-triggered runs opened by the bot instead of by hand (#24), the
generated overview (#25).

**Legacy data (#7, ADR-0003, accepted 2026-11-12).** AntHocNet's committed
`results/cells/` predate that format: rolling image tags with no campaign
digest, branch commits, short seed counts, a few log-garbled lines, and
`##COMMON##`/`##MATCH##` rows from before swarm-routing/AntHocNet#459 that
swarm-routing/AntHocNet#460 invalidates. They are imported apart from the
runs, under `legacy/anthocnet/`, byte for byte from the release tag that
published them, each with a legacy manifest that declares what it breaks. The
first family is static-mesh at v2.6.1 (19 cells: none from before #459; two
log-garbled lines, one 2-seed cell, one cell over two commits). The other
families, AntHocNet v2.7.0's `g460` cells (they supersede `grid.md`'s #460
tables) and `results/campaign/` follow in their own issues.
