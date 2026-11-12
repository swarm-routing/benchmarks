#!/usr/bin/env python3
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
"""Import AntHocNet's committed cells into legacy/anthocnet/, one family at a time.

  import_anthocnet.py --src AHN --tag vX.Y.Z --family F --ns3-tools PYDIR [--offline]
  import_anthocnet.py index [DEST]        regenerate DEST/INDEX.md (default legacy/anthocnet)
  import_anthocnet.py --self-test         every branch, on a fixture AntHocNet repository

What one import does (ADR-0003, #7):
  - lists results/cells/<F>-*.txt (and <F>.txt) in the tree of the release tag
    vX.Y.Z of the AntHocNet checkout AHN; a tag that is not vX.Y.Z is refused;
  - for each cell, builds its manifest (validate_run.legacy_build): the source
    (repo, tag, the tag's commit, path, sha256), every ##PROV## commit with
    whether it contains the #459 fix (git in AHN, else GitHub's compare API
    through `gh api`, else "unresolved"; --offline skips GitHub), every image
    with its digest (a rolling tag takes its digest of record from AntHocNet's
    docker/README.md "Images of record" at --images-ref, marked unverified),
    arms and seeds, the defects found, and the #460 invalid entry;
  - runs swarm-routing/ns3-tools' bench_parse (PYDIR holds the ns3_tool
    package: the release AntHocNet's ns3-tools.lock pins) over each cell and
    refuses the whole import if it rejects a cell, unless that cell declares a
    garbled-marker defect (then the manifest's notes say so);
  - writes nothing unless every cell passes; a cell already imported with the
    same bytes is skipped, one with other bytes is refused (golden rule 10);
  - writes the cells, their manifests and the generated INDEX.md, then checks
    the result with validate_run.py legacy.

Stdlib only (plus git, and gh for the compare API). Exit 0 on success, 1 on a
refusal, 2 on a usage error.
"""

import argparse
import contextlib
import hashlib
import io
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import validate_run as vr  # noqa: E402

REPO = "swarm-routing/AntHocNet"
DEST = os.path.join(vr.LEGACY_DIR, "anthocnet")
# AntHocNet #931: docker/README.md "Images of record" (the frozen danieljoppi images).
IMAGES_REF = "77e71237e178966ee50962f0dd6333b1a9a9a571"
RELEASE_TAG = re.compile(r"^v[0-9]+\.[0-9]+\.[0-9]+$")
FAMILY = re.compile(r"^[a-z0-9][a-z0-9-]*$")  # as the legacy schema's family
HEX40 = re.compile(r"^[0-9a-f]{40}$")
RECORD_ROW = re.compile(r"^\|\s*`([^`]+)`[^|]*\|\s*`(sha256:[0-9a-f]{64})`")
READ_DATE = re.compile(r"Digests read from the registry on ([0-9]{4}-[0-9]{2}-[0-9]{2})")
BENCH_PARSE = (
    "import runpy, sys; sys.path.insert(0, sys.argv[1]); "
    "sys.argv = ['bench_parse', '--all', sys.argv[2]]; "
    "runpy.run_module('ns3_tool.bench_parse', run_name='__main__')"
)


class Refused(Exception):
    pass


def git(src, *args, binary=False):
    r = subprocess.run(["git", "-C", src, *args], capture_output=True, check=False)
    if r.returncode:
        raise Refused(f"git {' '.join(args)}: {r.stderr.decode(errors='replace').strip()}")
    return r.stdout if binary else r.stdout.decode()


def images_of_record(src, ref, repo):
    """Rolling tag -> {digest, source, read} from docker/README.md at `ref`."""
    commit = git(src, "rev-parse", f"{ref}^{{commit}}").strip()
    text = git(src, "show", f"{commit}:docker/README.md")
    read = READ_DATE.search(text)
    if not read:
        raise Refused(
            f"docker/README.md at {commit[:7]}: no 'Digests read from the registry on' date"
        )
    url = f"https://github.com/{repo}/blob/{commit}/docker/README.md"
    out = {}
    for line in text.splitlines():
        m = RECORD_ROW.match(line)
        if m:
            out[m.group(1)] = {"digest": m.group(2), "source": url, "read": read.group(1)}
    return out


def make_ancestry(src, repo, fix, offline):
    cache = {}

    def via_github(commit):
        r = subprocess.run(
            ["gh", "api", f"repos/{repo}/compare/{fix}...{commit}", "--jq", ".status"],
            capture_output=True,
            text=True,
            check=False,
        )
        status = r.stdout.strip() if r.returncode == 0 else ""
        if status in ("ahead", "identical"):
            return True, "github-compare"
        if status in ("behind", "diverged"):
            return False, "github-compare"
        return "unresolved", "none"

    def ancestry(commit):
        if commit in cache:
            return cache[commit]
        if not HEX40.match(commit) or not HEX40.match(fix):
            return "unresolved", "none"  # never hand git or gh a value that is not a commit
        have = all(
            subprocess.run(
                ["git", "-C", src, "cat-file", "-e", f"{c}^{{commit}}"], capture_output=True
            ).returncode
            == 0
            for c in (commit, fix)
        )
        if have:
            rc = subprocess.run(
                ["git", "-C", src, "merge-base", "--is-ancestor", fix, commit], capture_output=True
            ).returncode
            ans = (rc == 0, "git") if rc in (0, 1) else ("unresolved", "none")
        elif offline:
            ans = ("unresolved", "none")
        else:
            ans = via_github(commit)
        cache[commit] = ans
        return ans

    return ancestry


def bench_parse(pydir, path):
    r = subprocess.run(
        [sys.executable, "-I", "-c", BENCH_PARSE, pydir, path], capture_output=True, text=True
    )
    return r.returncode, (r.stderr or r.stdout).strip().splitlines()[-1:] or [""]


def import_family(
    src,
    tag,
    family,
    ns3_tools,
    dest=DEST,
    repo=REPO,
    images_ref=IMAGES_REF,
    fix=vr.FIX_459,
    offline=False,
    out=print,
):
    if not RELEASE_TAG.match(tag):
        raise Refused(f"{tag} is not a release tag vX.Y.Z (ADR-0003)")
    if not FAMILY.match(family):
        raise Refused(f"{family!r} is not a family name ([a-z0-9][a-z0-9-]*)")
    commit = git(src, "rev-parse", f"refs/tags/{tag}^{{commit}}").strip()
    names = [
        p
        for p in git(src, "ls-tree", "--name-only", commit, "results/cells/").split()
        if re.fullmatch(rf"results/cells/{re.escape(family)}(-[A-Za-z0-9._-]+)?\.txt", p)
    ]
    if not names:
        raise Refused(f"{tag}: no results/cells/{family}-*.txt")
    records = images_of_record(src, images_ref, repo)
    ancestry = make_ancestry(src, repo, fix, offline)
    planned, problems = [], []
    with tempfile.TemporaryDirectory() as tmp:
        for path in names:
            data = git(src, "show", f"{commit}:{path}", binary=True)
            cell = os.path.basename(path)[: -len(".txt")]
            digest = hashlib.sha256(data).hexdigest()
            existing = os.path.join(dest, cell, vr.MANIFEST)
            if os.path.isfile(existing):
                if vr.load_json(existing)["source"]["sha256"] == digest:
                    out(f"skip {cell}: already imported with these bytes")
                    continue
                problems.append(f"{cell}: imported before with other bytes (golden rule 10)")
                continue
            source = {"repo": repo, "tag": tag, "commit": commit, "path": path, "sha256": digest}
            try:
                m = vr.legacy_build(
                    cell, family, source, data.decode("utf-8", "replace"), ancestry, records
                )
            except ValueError as e:
                problems.append(str(e))
                continue
            tpath = os.path.join(tmp, os.path.basename(path))
            with open(tpath, "wb") as f:
                f.write(data)
            rc, why = bench_parse(ns3_tools, tpath)
            if rc:
                if any(d["kind"] == "garbled-marker" for d in m["defects"]):
                    m["notes"] = f"ns3-tools bench_parse rejects this file (exit {rc}: {why[0]})."
                else:
                    problems.append(f"{cell}: bench_parse rejects it (exit {rc}: {why[0]})")
                    continue
            planned.append((m, data))
    if problems:
        raise Refused("nothing written:\n  - " + "\n  - ".join(problems))
    for m, data in planned:
        vr.legacy_write(dest, m, data)
        flags = [d["kind"] for d in m["defects"]] + [
            "invalid " + "/".join(i["markers"]) for i in m["invalid"]
        ]
        out(f"add  {m['cell']}" + (f" ({', '.join(flags)})" if flags else ""))
    os.makedirs(dest, exist_ok=True)
    vr.legacy_write_index(dest)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ok = vr.legacy_check_all(os.path.dirname(os.path.abspath(dest)))
    if not ok:
        raise Refused("the written cells do not validate:\n" + buf.getvalue())
    out(f"{len(planned)} cell(s) imported from {repo} {tag} ({commit[:7]}), {family}")
    return len(planned)


# --- self-test ---------------------------------------------------------------


def _fixture(root):
    """A fixture AntHocNet: pre, fix and post commits, release tags, a fake ns3_tool."""
    src = os.path.join(root, "ahn")
    os.makedirs(os.path.join(src, "results", "cells"))
    os.makedirs(os.path.join(src, "docker"))
    env = ["-c", "user.name=t", "-c", "user.email=t@example.invalid"]

    def g(*a):
        return subprocess.run(
            ["git", "-C", src, *env, *a], capture_output=True, text=True, check=True
        ).stdout.strip()

    def write(rel, text):
        with open(os.path.join(src, rel), "w", encoding="utf-8") as f:
            f.write(text)

    g("init", "-q", "-b", "main")
    write("README.md", "pre\n")
    g("add", "-A")
    g("commit", "-qm", "pre")
    pre = g("rev-parse", "HEAD")
    write("README.md", "fix\n")
    g("commit", "-qam", "fix")
    fix = g("rev-parse", "HEAD")
    write(
        "docker/README.md",
        (
            "### Images of record\n\nDigests read from the registry on 2026-11-11.\n\n"
            "| Image | Digest |\n|---|---|\n"
            f"| `ghcr.io/example/ns3:3.42-opt` | `sha256:{'c' * 64}` |\n"
        ),
    )
    g("add", "-A")
    g("commit", "-qm", "post")
    post = g("rev-parse", "HEAD")
    cell = vr._legacy_cell_text
    verified = (
        f"##PROV## commit={post} ref=main run_id=9 attempt=1 "
        f"image=ghcr.io/example/campaign@sha256:{'1' * 64} "
        f"base=ghcr.io/example/ns3-dev:3.48-optimized@sha256:{'2' * 64}"
    )
    cells = {
        "fam-ok": cell(post),
        "fam-pre": cell(pre),
        "fam-gone": cell("9" * 40),
        "fam-short": cell(pre, seeds=(1, 2)).replace("##COMMON##", "##ROUTE##"),
        "fam-garbled": cell(post, extra=("##AI##RSS## t=1",)),
        "fam-noprov": cell(post, prov=False),
        "fam-two": cell(post) + cell(pre).split("\n", 1)[1],
        "fam-verified": cell(post, prov=False) + verified + "\n",
        "other-x": cell(post),
        "fam-reject": cell(post) + "REJECT\n",
    }
    for name, text in cells.items():
        write(f"results/cells/{name}.txt", text)
    g("add", "-A")
    g("commit", "-qm", "cells")
    g("tag", "v0.1.0")
    g("tag", "ctl867")
    os.remove(os.path.join(src, "results", "cells", "fam-reject.txt"))
    g("commit", "-qam", "drop the rejected cell")
    g("tag", "v0.2.0")
    write("results/cells/fam-ok.txt", cell(post) + "# changed\n")
    g("commit", "-qam", "change a published cell")
    g("tag", "v0.3.0")
    pydir = os.path.join(root, "ns3tools")
    os.makedirs(os.path.join(pydir, "ns3_tool"))
    with open(os.path.join(pydir, "ns3_tool", "__init__.py"), "w", encoding="utf-8"):
        pass
    with open(os.path.join(pydir, "ns3_tool", "bench_parse.py"), "w", encoding="utf-8") as f:
        f.write("import sys\nsys.exit(1 if 'REJECT' in open(sys.argv[-1]).read() else 0)\n")
    return src, pydir, fix


def self_test():
    failures = []

    def expect(name, ok, detail=""):
        if not ok:
            failures.append(f"{name} {detail}".strip())

    def run(*a, **kw):
        try:
            return import_family(*a, **kw, out=lambda *_: None), None
        except Refused as e:
            return None, str(e)

    with tempfile.TemporaryDirectory() as root:
        src, pydir, fix = _fixture(root)
        dest = os.path.join(root, "legacy", "anthocnet")
        kw = {
            "dest": dest + os.sep,  # a trailing separator still validates legacy/
            "repo": "example/ahn",
            "images_ref": "HEAD",
            "fix": fix,
            "offline": True,
        }
        n, err = run(src, "ctl867", "fam", pydir, **kw)
        expect("a non-release tag is refused", err and "not a release tag" in err, err)
        n, err = run(src, "v0.1.0", "fam", pydir, **kw)
        expect("a bench_parse rejection refuses the import", err and "fam-reject" in err, err)
        expect("a refused import writes nothing", not os.path.exists(dest))
        n, err = run(src, "v0.2.0", "../fam", pydir, **kw)
        expect("a family that is not a name is refused", err and "not a family name" in err, err)
        n, err = run(src, "v0.2.0", "nofam", pydir, **kw)
        expect("an empty family is refused", err and "no results/cells" in err, err)
        n, err = run(src, "v0.2.0", "fam", pydir, **kw)
        expect("v0.2.0 imports eight cells", n == 8, f"{n} {err}")

        def manifest(cell):
            return vr.load_json(os.path.join(dest, cell, vr.MANIFEST))

        if n == 8:
            expect("other families are left out", not os.path.exists(os.path.join(dest, "other-x")))
            ok, pre = manifest("fam-ok"), manifest("fam-pre")
            expect("post-fix: no defect, no invalid", not ok["defects"] and not ok["invalid"])
            expect(
                "the tag and its commit are recorded",
                ok["source"]["tag"] == "v0.2.0" and len(ok["source"]["commit"]) == 40,
            )
            expect(
                "unverified digest of record",
                ok["images"][0]["verified"] is False
                and ok["images"][0]["digest_read"] == "2026-11-11",
            )
            expect(
                "pre-fix COMMON is invalid",
                pre["invalid"] and pre["measured"][0]["contains_fix"] is False,
            )
            gone = manifest("fam-gone")
            expect(
                "offline unresolved ancestry is invalid",
                gone["invalid"] and gone["measured"][0]["contains_fix"] == "unresolved",
            )
            short = manifest("fam-short")
            expect(
                "short seeds declared, no matched marker so nothing invalid",
                [d["kind"] for d in short["defects"]] == ["seeds-below-20"]
                and not short["invalid"],
            )
            expect(
                "garbled declared",
                manifest("fam-garbled")["defects"][0]["kind"] == "garbled-marker",
            )
            expect("no-prov declared and flagged", manifest("fam-noprov")["invalid"])
            two = manifest("fam-two")
            expect(
                "two commits declared",
                "multi-commit" in [d["kind"] for d in two["defects"]] and two["invalid"],
            )
            ver = manifest("fam-verified")
            expect(
                "PROV digests verified",
                all(i["verified"] for i in ver["images"])
                and {i["role"] for i in ver["images"]} == {"run", "base"},
            )
            with open(os.path.join(dest, vr.LEGACY_INDEX), encoding="utf-8") as f:
                index = f.read()
            expect("index lists every cell", index.count("| [`fam-") == 8)
        n, err = run(src, "v0.2.0", "fam", pydir, **kw)
        expect("re-import is idempotent", n == 0 and err is None, err)
        n, err = run(src, "v0.3.0", "fam", pydir, **kw)
        expect("a changed published cell is refused", err and "other bytes" in err, err)
        with open(os.path.join(src, "docker", "README.md"), "w", encoding="utf-8") as f:
            f.write("Digests read from the registry on 2026-11-11.\n")
        subprocess.run(
            [
                "git",
                "-C",
                src,
                "-c",
                "user.name=t",
                "-c",
                "user.email=t@e.invalid",
                "commit",
                "-qam",
                "no records",
            ],
            check=True,
        )
        n, err = run(src, "v0.2.0", "fam", pydir, **{**kw, "dest": os.path.join(root, "l2", "a")})
        expect(
            "a rolling tag without a digest of record is refused",
            err and "no digest of record" in err,
            err,
        )
    for f in failures:
        print(f"FAIL {f}")
    print(
        f"import_anthocnet self-test: {'FAILED' if failures else 'ok'} ({len(failures)} failures)"
    )
    return 1 if failures else 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--self-test", action="store_true")
    p.add_argument("command", nargs="?", choices=["index"], help="index: regenerate INDEX.md")
    p.add_argument(
        "dest_arg", nargs="?", help="index: the source directory (default legacy/anthocnet)"
    )
    p.add_argument("--src", help="an AntHocNet checkout with its tags")
    p.add_argument("--tag", help="the release tag to import from (vX.Y.Z)")
    p.add_argument("--family", help="the cell-name prefix (e.g. static-mesh)")
    p.add_argument(
        "--ns3-tools", help="the python/ directory of the ns3-tools release AntHocNet pins"
    )
    p.add_argument("--dest", default=DEST)
    p.add_argument(
        "--images-ref",
        default=IMAGES_REF,
        help="the AntHocNet commit whose docker/README.md lists the images of record",
    )
    p.add_argument("--offline", action="store_true", help="never ask GitHub (ancestry unresolved)")
    args = p.parse_args(argv)
    if args.self_test:
        return self_test()
    if args.command == "index":
        d = args.dest_arg or DEST
        vr.legacy_write_index(d)
        print(f"wrote {os.path.join(d, vr.LEGACY_INDEX)}")
        return 0
    missing = [o for o in ("src", "tag", "family", "ns3_tools") if not getattr(args, o)]
    if missing:
        p.error("an import needs " + ", ".join("--" + o.replace("_", "-") for o in missing))
    try:
        import_family(
            args.src,
            args.tag,
            args.family,
            args.ns3_tools,
            dest=args.dest,
            images_ref=args.images_ref,
            offline=args.offline,
        )
    except Refused as e:
        print(f"REFUSED {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
