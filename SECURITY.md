# Security Policy

`swarm-routing/benchmarks` is the org's benchmark datasets: marker-line runs, their manifests and the verdicts recomputed from them. This document records its
security posture honestly; it promises nothing the code does not do. The
org-wide policy is [swarm-routing/.github SECURITY.md](https://github.com/swarm-routing/.github/blob/main/SECURITY.md).

## Trust boundary

<!-- Which input is untrusted, the only code that parses it, and what that
code guarantees. A protocol: its wire-format decoder (org invariant 3). A
tool: the parsers of files it reads. If nothing parses untrusted input, say
so in one line. -->
Contributed datasets. Each run's `manifest.json` pins the immutable
`ns3-dev:<ver>-<profile>-<sha7>` image (verifiable with `cosign verify`, see
swarm-routing/ns3-containers' `SECURITY.md`), each protocol's commit, the
scenario, the seeds and the command. A dataset without a manifest is not
merged; a merged run is immutable, and a correction is a new run.

**Report privately:** a merged dataset that does not reproduce from its
manifest, or evidence of edited numbers. An ordinary reproduction difference
goes in a public issue.

## Known, by-design limitations (out of scope)

- Reproducibility is to the pinned image digest and the seed, not across CPUs
  or compilers outside that image.

<!-- org-sync:begin reporting -->
## Reporting a vulnerability

Report privately through GitHub's private vulnerability reporting: the
repository's **Security** tab, then **Report a vulnerability**. If that is
not available, open an issue that only asks for a private contact, and put
no vulnerability details in it. This is a research project maintained on a
best-effort basis: expect an acknowledgement within a few days, not an SLA.
<!-- org-sync:end reporting -->

## Verifying what it ships
- **A release asset.** `benchmarks-X.Y.Z.tar.gz` unpacks with a
  `SHA256SUMS.txt` (`sha256sum -c SHA256SUMS.txt` in the unpacked directory);
  the release also carries `SHA256SUMS`, an SBOM and signed build provenance,
  with the verify commands in its notes (README "Releases").
- **A run.** `python3 -I tools/validate_run.py check runs/<dir>` checks the
  files against the manifest's hashes, and the cells against its seeds,
  scenarios, commands, image digests and module commits.
- **A verdict.** Recompute it from a cell with the `ns3-tool` reader, in a
  swarm-routing/ns3-tools checkout:
  `python3 python/ns3_tool/bench_parse.py --proto anthocnet --vs aodv <benchmarks>/runs/2026-11-10-anthocnet-aodv-smoke/cells/grid-rwp.txt`.
- **The image.** Check the image a manifest pins with `cosign verify`, as
  ns3-containers' `SECURITY.md` describes.
