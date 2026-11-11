#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# dist.sh VERSION OUT-DIR: the dataset release asset (#39), as `make dist` runs
# it for swarm-routing/.github's reusable-release.yml:
#
#   benchmarks-VERSION.tar.gz   benchmarks-VERSION/ holding every git-tracked
#                               file of runs/, verdicts/ (when present),
#                               schemas/, tools/, the licence texts, README.md
#                               and CITATION.cff; RUNS.md (every run with its
#                               pinned inputs, tools/release/runs_notes.py) and
#                               SHA256SUMS.txt (a checksum per file inside)
#
# It validates every run first (tools/validate_run.py all), so a release never
# ships a run the validator refuses. Deterministic: sorted entries, a fixed
# owner and mode, the release commit's time, gzip -n; the same commit gives
# the same bytes.
set -euo pipefail
ver=${1:?usage: dist.sh VERSION OUT-DIR}
out=${2:?usage: dist.sh VERSION OUT-DIR}
repo=$(cd "$(dirname "$0")/../.." && pwd)
mkdir -p "$out"
out=$(cd "$out" && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
epoch=$(git -C "$repo" log -1 --format=%ct)

python3 -I "$repo/tools/validate_run.py" all

name="benchmarks-$ver"
pkg="$tmp/$name"
mkdir -p "$pkg"
paths=(runs schemas tools LICENSE LICENSE-MIT LICENSING.md README.md CITATION.cff)
if [[ -d "$repo/verdicts" ]]; then paths+=(verdicts); fi
for p in CITATION.cff LICENSE README.md; do
    [[ -f "$repo/$p" ]] || { echo "dist.sh: $p is missing" >&2; exit 1; }
done
git -C "$repo" ls-files -z -- "${paths[@]}" | (cd "$repo" && xargs -0 cp --parents -t "$pkg")
python3 -I "$repo/tools/release/runs_notes.py" index "v$ver" > "$pkg/RUNS.md"
(cd "$pkg" && find . -type f -printf '%P\n' | LC_ALL=C sort | xargs -d '\n' sha256sum) > "$tmp/sums"
mv "$tmp/sums" "$pkg/SHA256SUMS.txt"

tar --sort=name --owner=0 --group=0 --numeric-owner --mode='a+rX,u+w,go-w' \
    --mtime="@${epoch}" -C "$tmp" -cf - "$name" | gzip -n > "$out/$name.tar.gz"
echo "dist.sh: $out/$name.tar.gz ($(tar -tzf "$out/$name.tar.gz" | grep -vc '/$') files)"
