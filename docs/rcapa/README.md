# RCAPA: does not apply to swarm-routing/benchmarks's own changes

An **RCAPA** (root cause analysis with corrective and preventive actions) is
required for a regression in a **published library**: a version another
project consumes (a swarm-core or ns3-tools release through its lock or PyPI,
a protocol core's vcpkg port), and for every upstream ns-3 bug. The rule and
its decision table are in [CONTRIBUTING.md, "RCAPA"](https://github.com/swarm-routing/.github/blob/main/CONTRIBUTING.md#rcapa) ([ADR-0003](https://github.com/swarm-routing/.github/blob/main/docs/adr/0003-rcapa-for-ns3-bugs-and-released-regressions.md)).

**RCAPA does not apply to this repository's own changes**, because
nothing consumes it at a version as a library: its releases are datasets of
recorded runs. A wrong run is corrected by a new run that names the one it
supersedes (golden rule 10), with an issue explaining why; a validator bug is
an ordinary `bug` issue.

**Where RCAPA applies instead:** a run that is wrong because a library it ran on was wrong (swarm-core,
ns3-tools' harness, a protocol core) is an RCAPA in that library's
repository; the superseding run here links it.

The "open RCAPA" badge in the README counts this repository's open issues
labelled `rcapa`, so it reads 0 here.
