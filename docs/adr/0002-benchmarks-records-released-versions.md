# 0002. This repository benchmarks released versions; protocol repositories benchmark their changes

- **Status:** accepted
- **Date:** 2026-11-10
- **Issue:** swarm-routing/.github#156

## Context

Until now one repository, AntHocNet, ran every campaign. That covered both kinds of work:

- testing a change: an A/B on a branch, the #867 control campaign;
- recording a result: the v2.x comparator numbers.

Both used AntHocNet's own `benchmark-cell.yml` and `tools/bench/campaign.py`. With five protocols in the org, that mix does not scale:

- a protocol's change tests need its own code at its own commits;
- a result worth keeping needs one place where every protocol is measured the same way and kept immutable.

The #867 control campaign also showed that a cell has to build a pinned commit. A campaign dispatched from a moving branch over hours tests different code in different cells.

## Decision

1. **Each protocol repository benchmarks its own changes.** It calls the org's reusable cell workflow with a pinned `source_sha` and an image digest, runs its campaigns with `ns3-tools`' runner, and keeps its plans in `tools/bench/campaigns/`. Change tests (A/B, smoke, anchor, control) stay in that repository and are not recorded here.
2. **This repository records released versions only.** A new run starts, and is recorded under `runs/`, every time one of these happens:
   - a protocol publishes a release;
   - a new supported ns-3 release reaches `ns3-dev`;
   - a tool release changes what is measured (`ns3-tools`).
   
   The run uses the released commit and the released image, and is validated by `tools/validate_run.py` (rules 10, 11, 13).
3. **Suites.**
   - The **global** suite measures every released protocol that has cleared the three gates (golden rule 6) on every network family. It is the overview across protocols.
   - **Specialized** suites go deeper on one family or one question.
   
   Both are plan files here.
4. **The overview is generated.** The latest released verdict per protocol and family, and its history across releases, are recomputed from `runs/` by a script. The site's leaderboard reads that output.

## Consequences

- A protocol's published number always traces to a release tag, an image digest and a recorded run here. A number measured on a branch is never published as the protocol's result.
- Every protocol needs the shared machinery first: the reusable cell workflow and the runner in `ns3-tools`. AntHocNet migrates onto them.
- A release or ns-3 change costs runner minutes for a full rerun. Suites state their budget, and dispatch is throttled so PR CI keeps runners.
- `runs/2026-11-10-anthocnet-aodv-smoke` predates this ADR. It stays, since merged runs are immutable (rule 10). The legacy import (#7) is labelled pre-org.
