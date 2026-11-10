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

## Glossary

## Open questions
