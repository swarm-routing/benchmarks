#!/usr/bin/env python3
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
"""The runs a dataset release adds, with every pinned input of each (#39).

  runs_notes.py changelog   Commitizen's pre-bump hook (.cz.toml): inserts a
                            "Runs" section under the new version's heading of
                            CHANGELOG.md. reusable-release.yml publishes that
                            section as the release notes, so each release
                            names its run directories, their manifests' pins
                            (base image tag and digest, campaign image digest,
                            module commits, harness, scenarios, seeds,
                            commands) and the verdicts it adds.
  runs_notes.py index OUT TAG
                            RUNS.md for the release tarball: every run.
  runs_notes.py --self-test

A run is new in a release when its manifest.json is not in the previous v*
tag's tree (every run, for the first release). Reads only manifests that
tools/validate_run.py already checks; stdlib only; prints nothing on stdout
in `changelog` mode (the workflow captures Commitizen's stdout as notes).
"""

import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPO = "swarm-routing/benchmarks"


def git(*args, cwd=ROOT, check=True):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if check and r.returncode:
        raise SystemExit(f"runs_notes.py: git {' '.join(args)}: {r.stderr.strip()}")
    return r


def tag_exists(tag, cwd=ROOT):
    return (
        bool(tag)
        and git(
            "rev-parse", "-q", "--verify", f"refs/tags/{tag}^{{commit}}", cwd=cwd, check=False
        ).returncode
        == 0
    )


def run_dirs(root):
    d = os.path.join(root, "runs")
    if not os.path.isdir(d):
        return []
    return sorted(n for n in os.listdir(d) if os.path.isfile(os.path.join(d, n, "manifest.json")))


def new_runs(root, prev_tag):
    """Run directories whose manifest is not in prev_tag's tree (all of them without one)."""
    runs = run_dirs(root)
    if not tag_exists(prev_tag, root):
        return runs
    return [
        r
        for r in runs
        if git(
            "cat-file", "-e", f"{prev_tag}:runs/{r}/manifest.json", cwd=root, check=False
        ).returncode
    ]


def new_verdicts(root, prev_tag):
    d = os.path.join(root, "verdicts")
    if not os.path.isdir(d):
        return []
    files = sorted(
        os.path.relpath(os.path.join(p, f), root).replace(os.sep, "/")
        for p, _, fs in os.walk(d)
        for f in fs
    )
    if not tag_exists(prev_tag, root):
        return files
    return [
        f
        for f in files
        if git("cat-file", "-e", f"{prev_tag}:{f}", cwd=root, check=False).returncode
    ]


def seeds_text(seeds):
    s = sorted(seeds)
    if s and s == list(range(s[0], s[-1] + 1)):
        return f"{len(s)} ({s[0]}–{s[-1]})"
    return f"{len(s)} ({', '.join(map(str, s))})"


def describe(root, run, tag):
    """Markdown for one run: its directory and every pinned input of its manifest."""
    m = json.load(open(os.path.join(root, "runs", run, "manifest.json"), encoding="utf-8"))
    tree = f"https://github.com/{REPO}/tree/{tag}/runs/{run}"
    b, c = m["base_image"], m["campaign_image"]
    out = [f"#### [`runs/{run}`]({tree})", ""]
    out.append(
        f"- **Base image:** `{b['ref']}` @ `{b['digest']}` (ns-3 {b['ns3_version']}, {b['profile']})"
    )
    out.append(f"- **Campaign image:** `{c['ref']}` @ `{c['digest']}`")
    for mod in m["modules"]:
        out.append(
            f"- **Module `{mod['name']}`:** [`{mod['repo']}@{mod['commit']}`]"
            f"(https://github.com/{mod['repo']}/tree/{mod['commit']})"
        )
    h = m["harness"]
    out.append(f"- **Harness:** `{h['program']}` (module `{h['module']}`)")
    for s in m["scenarios"]:
        out.append(f"- **Scenario `{s['name']}`:** arms {', '.join(f'`{a}`' for a in s['arms'])}")
    out.append(f"- **Seeds:** {seeds_text(m['seeds'])}")
    pre = m.get("preregistration", {})
    if pre:
        out.append(f"- **Pre-registration:** `{pre.get('path') or pre.get('url')}`")
    out.append(
        f"- **Marker contract:** v{m['markers']['schema_version']}; manifest schema v{m['schema_version']}"
    )
    sup = m.get("supersedes")
    if sup:
        out.append(f"- **Supersedes:** `runs/{sup['run']}` ({sup['issue']})")
    out += ["", "<details><summary>The exact commands</summary>", "", "```bash"]
    out += m["commands"]
    out += ["```", "", "</details>", ""]
    return out


def section(root, prev_tag, tag):
    runs = new_runs(root, prev_tag)
    verdicts = new_verdicts(root, prev_tag)
    out = ["### Runs", ""]
    if runs:
        out.append(
            "Each run's `manifest.json` and raw cells are in this release's archive; "
            "cite a number by this version's DOI and its run directory (README, How to cite a number)."
        )
        out.append("")
        for r in runs:
            out += describe(root, r, tag)
    else:
        out += ["No run added in this release.", ""]
    out += ["### Verdicts", ""]
    if verdicts:
        out += [f"- [`{v}`](https://github.com/{REPO}/blob/{tag}/{v})" for v in verdicts]
    else:
        out.append("No verdict added in this release.")
    out.append("")
    return out


def insert(changelog, tag, lines):
    """Put lines right under the `## <tag>` heading Commitizen just wrote."""
    text = open(changelog, encoding="utf-8").read().split("\n")
    for i, line in enumerate(text):
        if line == f"## {tag}" or line.startswith(f"## {tag} "):
            text[i + 1 : i + 1] = ["", *lines]
            break
    else:
        raise SystemExit(f"runs_notes.py: no '## {tag}' heading in {changelog}")
    open(changelog, "w", encoding="utf-8").write("\n".join(text))


def changelog_hook():
    tag = os.environ.get("CZ_PRE_NEW_TAG_VERSION")
    prev = os.environ.get("CZ_PRE_CURRENT_TAG_VERSION", "")
    log = os.environ.get("CZ_PRE_CHANGELOG_FILE_NAME") or "CHANGELOG.md"
    if not tag:
        raise SystemExit(
            "runs_notes.py changelog: run as Commitizen's pre-bump hook (CZ_PRE_NEW_TAG_VERSION unset)"
        )
    insert(os.path.join(ROOT, log), tag, section(ROOT, prev, tag))
    print(
        f"runs_notes.py: the runs of {tag} (since {prev if tag_exists(prev) else 'the start'}) in {log}",
        file=sys.stderr,
    )


def index(out, tag):
    lines = [f"# swarm-routing/benchmarks {tag}: the runs", ""]
    for r in run_dirs(ROOT):
        lines += describe(ROOT, r, tag)
    open(out, "w", encoding="utf-8").write("\n".join(lines))


def self_test():
    manifest = {
        "schema_version": 1,
        "base_image": {
            "ref": "ns3-dev:3.48-optimized-abc1234",
            "digest": "sha256:" + "a" * 64,
            "ns3_version": "3.48",
            "profile": "optimized",
        },
        "campaign_image": {"ref": "x-ns3-campaign:1-2", "digest": "sha256:" + "b" * 64},
        "modules": [{"name": "anthocnet", "repo": "swarm-routing/AntHocNet", "commit": "c" * 40}],
        "harness": {"program": "routing-compare", "module": "routing-bench"},
        "scenarios": [{"name": "grid", "arms": ["anthocnet", "aodv"]}],
        "preregistration": {"path": "plan.toml"},
        "seeds": list(range(1, 21)),
        "commands": ["routing-compare --runs=20"],
        "markers": {"schema_version": 1},
    }
    with tempfile.TemporaryDirectory() as d:
        env = ["-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false"]

        def add_run(name, extra=None):
            os.makedirs(os.path.join(d, "runs", name))
            json.dump(
                {**manifest, **(extra or {})},
                open(os.path.join(d, "runs", name, "manifest.json"), "w"),
            )
            git("add", "-A", cwd=d)
            git(*env, "commit", "-qm", f"feat(runs): {name}", cwd=d)

        git("init", "-q", cwd=d)
        add_run("2026-01-01-a")
        first = "\n".join(section(d, "v0.0.0", "v0.1.0"))  # no previous tag: every run
        assert "runs/2026-01-01-a" in first and "20 (1–20)" in first, first
        assert (
            "sha256:" + "a" * 64 in first
            and "c" * 40 in first
            and "routing-compare --runs=20" in first
        ), first
        assert "No verdict added" in first, first
        git("tag", "v0.1.0", cwd=d)
        add_run(
            "2026-02-01-b",
            {"supersedes": {"run": "2026-01-01-a", "issue": "https://x/1"}, "seeds": [1, 3]},
        )
        os.makedirs(os.path.join(d, "verdicts"))
        open(os.path.join(d, "verdicts", "v.csv"), "w").write("x\n")
        second = "\n".join(section(d, "v0.1.0", "v0.2.0"))
        assert (
            "#### [`runs/2026-02-01-b`]" in second and "#### [`runs/2026-01-01-a`]" not in second
        ), second
        assert (
            "Supersedes:** `runs/2026-01-01-a`" in second
            and "2 (1, 3)" in second
            and "verdicts/v.csv" in second
        ), second
        git("tag", "v0.2.0", cwd=d)
        assert "No run added" in "\n".join(section(d, "v0.2.0", "v0.2.1"))
        log = os.path.join(d, "CHANGELOG.md")
        open(log, "w").write("## v0.2.1 (2026-03-01)\n\n### Fix\n\n- x\n\n## v0.2.0 (2026-02-01)\n")
        insert(log, "v0.2.1", ["### Runs", ""])
        t = open(log).read()
        assert t.index("### Runs") < t.index("### Fix") < t.index("## v0.2.0"), t
        try:
            insert(log, "v9.9.9", ["x"])
            raise AssertionError("a missing heading must fail")
        except SystemExit:
            pass
    print("runs_notes.py self-test: OK")


def main(argv):
    if argv[:1] == ["--self-test"]:
        self_test()
    elif argv[:1] == ["changelog"]:
        changelog_hook()
    elif argv[:1] == ["index"] and len(argv) == 3:
        index(argv[1], argv[2])
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
