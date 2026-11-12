# CONTEXT.md — orientation and history

Background an agent or a new contributor needs that does not belong in
`AGENTS.md`: domain notes, current state, glossary, open questions. Read the
section a task needs, not the whole file.

## Current state

**Status: ready, no run yet.** The run layout, the manifest schema
(`schemas/manifest.schema.json`), the marker contract v1 (`schemas/markers/`)
and the validator CI runs (`tools/validate_run.py`) landed with #3, before the
first data, so the first runs (the ARA and BeeAdHoc anchors) do not set the
format by accident. The manifest follows swarm-routing/.github#107: one
campaign image per (commits, ns3-dev digest), every cell pulled by digest, and
the manifest and every `##PROV##` line naming the base digest, the
campaign-image digest and every module commit.

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

## Glossary

## Open questions
