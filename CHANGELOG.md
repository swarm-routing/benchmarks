## v0.1.0 (2026-11-11)

### Runs

Each run's `manifest.json` and raw cells are in this release's archive; cite a number by this version's DOI and its run directory (README, How to cite a number).

#### [`runs/2026-11-10-anthocnet-aodv-smoke`](https://github.com/swarm-routing/benchmarks/tree/v0.1.0/runs/2026-11-10-anthocnet-aodv-smoke)

- **Base image:** `ghcr.io/swarm-routing/ns3-dev:3.48-optimized-fb7596b` @ `sha256:5585a93c5cea1980592539e2d26a4e111e0ff4b0cc63b3dfd6ea5de459d80d3f` (ns-3 3.48, optimized)
- **Campaign image:** `ghcr.io/swarm-routing/ns3-tools-ns3-campaign:4fe1400-5585a93-optimized` @ `sha256:3d565ff5b61a12dd841fcf9fc202292beb0a4bfc9ff054a2724d88afa0dca30a`
- **Module `anthocnet`:** [`swarm-routing/AntHocNet@4fe1400c98d8a1e2f053ced6b6580df3b27f1124`](https://github.com/swarm-routing/AntHocNet/tree/4fe1400c98d8a1e2f053ced6b6580df3b27f1124)
- **Module `routing-bench`:** [`swarm-routing/ns3-tools@ba986d87db91974749c580d1af76b9d0017d9f2b`](https://github.com/swarm-routing/ns3-tools/tree/ba986d87db91974749c580d1af76b9d0017d9f2b)
- **Harness:** `routing-compare` (module `routing-bench`)
- **Scenario `grid-rwp`:** arms `anthocnet`, `aodv`; `areaX=1500 areaY=300 diag=true mobility="rwp" nNodes=50 pause=30 propagation="range" range=300 scenario="paper" speed=20 time=300 transport="udp"`
- **Scenario `static-mesh`:** arms `anthocnet`, `aodv`; `areaX=1500 areaY=300 diag=true mobility="rwp" nNodes=50 pause=300 propagation="range" range=300 scenario="paper" speed=20 time=300 transport="udp"`
- **Seeds:** 20 (1–20)
- **Pre-registration:** `plan.toml`
- **Marker contract:** v1; manifest schema v1

<details><summary>The exact commands</summary>

```bash
gh api -X POST repos/swarm-routing/ns3-tools/actions/workflows/campaign-image.yml/dispatches --input - <<< '{"ref": "main", "inputs": {"plan": "campaigns/anthocnet-aodv-smoke.toml"}}'
gh api -X POST repos/swarm-routing/ns3-tools/actions/workflows/campaign-cell.yml/dispatches --input - <<< '{"ref": "main", "inputs": {"image": "ghcr.io/swarm-routing/ns3-tools-ns3-campaign@sha256:3d565ff5b61a12dd841fcf9fc202292beb0a4bfc9ff054a2724d88afa0dca30a", "program": "routing-compare", "args": "--scenario=paper --nNodes=50 --time=300 --areaX=1500 --areaY=300 --speed=20 --pause=30 --range=300 --propagation=range --mobility=rwp --transport=udp --diag --protocols=anthocnet,aodv --runs=20 --firstRun=1", "label": "anthocnet-aodv-smoke/grid-rwp"}}'
docker run --rm -e PROGRAM=routing-compare -e ARGS='--scenario=paper --nNodes=50 --time=300 --areaX=1500 --areaY=300 --speed=20 --pause=30 --range=300 --propagation=range --mobility=rwp --transport=udp --diag --protocols=anthocnet,aodv --runs=20 --firstRun=1' ghcr.io/swarm-routing/ns3-tools-ns3-campaign@sha256:3d565ff5b61a12dd841fcf9fc202292beb0a4bfc9ff054a2724d88afa0dca30a bash -c './ns3 run --no-build "$PROGRAM $ARGS"'
routing-compare --scenario=paper --nNodes=50 --time=300 --areaX=1500 --areaY=300 --speed=20 --pause=30 --range=300 --propagation=range --mobility=rwp --transport=udp --diag --protocols=anthocnet,aodv --runs=20 --firstRun=1
gh api -X POST repos/swarm-routing/ns3-tools/actions/workflows/campaign-cell.yml/dispatches --input - <<< '{"ref": "main", "inputs": {"image": "ghcr.io/swarm-routing/ns3-tools-ns3-campaign@sha256:3d565ff5b61a12dd841fcf9fc202292beb0a4bfc9ff054a2724d88afa0dca30a", "program": "routing-compare", "args": "--scenario=paper --nNodes=50 --time=300 --areaX=1500 --areaY=300 --speed=20 --pause=300 --range=300 --propagation=range --mobility=rwp --transport=udp --diag --protocols=anthocnet,aodv --runs=10 --firstRun=1", "label": "anthocnet-aodv-smoke/static-mesh-s1"}}'
docker run --rm -e PROGRAM=routing-compare -e ARGS='--scenario=paper --nNodes=50 --time=300 --areaX=1500 --areaY=300 --speed=20 --pause=300 --range=300 --propagation=range --mobility=rwp --transport=udp --diag --protocols=anthocnet,aodv --runs=10 --firstRun=1' ghcr.io/swarm-routing/ns3-tools-ns3-campaign@sha256:3d565ff5b61a12dd841fcf9fc202292beb0a4bfc9ff054a2724d88afa0dca30a bash -c './ns3 run --no-build "$PROGRAM $ARGS"'
routing-compare --scenario=paper --nNodes=50 --time=300 --areaX=1500 --areaY=300 --speed=20 --pause=300 --range=300 --propagation=range --mobility=rwp --transport=udp --diag --protocols=anthocnet,aodv --runs=10 --firstRun=1
gh api -X POST repos/swarm-routing/ns3-tools/actions/workflows/campaign-cell.yml/dispatches --input - <<< '{"ref": "main", "inputs": {"image": "ghcr.io/swarm-routing/ns3-tools-ns3-campaign@sha256:3d565ff5b61a12dd841fcf9fc202292beb0a4bfc9ff054a2724d88afa0dca30a", "program": "routing-compare", "args": "--scenario=paper --nNodes=50 --time=300 --areaX=1500 --areaY=300 --speed=20 --pause=300 --range=300 --propagation=range --mobility=rwp --transport=udp --diag --protocols=anthocnet,aodv --runs=10 --firstRun=11", "label": "anthocnet-aodv-smoke/static-mesh-s11"}}'
docker run --rm -e PROGRAM=routing-compare -e ARGS='--scenario=paper --nNodes=50 --time=300 --areaX=1500 --areaY=300 --speed=20 --pause=300 --range=300 --propagation=range --mobility=rwp --transport=udp --diag --protocols=anthocnet,aodv --runs=10 --firstRun=11' ghcr.io/swarm-routing/ns3-tools-ns3-campaign@sha256:3d565ff5b61a12dd841fcf9fc202292beb0a4bfc9ff054a2724d88afa0dca30a bash -c './ns3 run --no-build "$PROGRAM $ARGS"'
routing-compare --scenario=paper --nNodes=50 --time=300 --areaX=1500 --areaY=300 --speed=20 --pause=300 --range=300 --propagation=range --mobility=rwp --transport=udp --diag --protocols=anthocnet,aodv --runs=10 --firstRun=11
```

</details>

### Verdicts

No verdict added in this release.


### Feat

- **release**: dataset releases through the org release workflow, semver, a tag per recorded run (#40)
- **schema**: accept the campaign-image tag with its -optimized suffix (#17)
- **schema**: dataset layout, run manifest schema and a validator (#16)

### Fix

- **release**: notes name scenario parameters, sonar and review fixes (#41)
