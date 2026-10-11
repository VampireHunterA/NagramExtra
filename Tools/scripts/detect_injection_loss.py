#!/usr/bin/env python3
"""Detect fork-injection lines lost to an upstream sync commit.

After each `update to X.Y.Z` squash merge, run:

    python3 Tools/scripts/detect_injection_loss.py <sync_sha>

For every file the sync touches that our fork commits also touched before the
sync, the script intersects lines added by our commits with lines removed by
the sync. Every hit is a candidate for manual triage: either the sync really
dropped our injection (bug), or our code was adapted to an upstream API change
(benign), or upstream absorbed our mechanism (benign). Static line matching
cannot tell these apart — the output is a review list, not a verdict.

Validated on syncs 12.10.3 (c21f3c2a8e) and 12.10.6 (f9d33af325): 3 hits, all
benign after triage.
"""

import argparse
import subprocess
import sys
from collections import defaultdict

FROZEN_BASE = "nagramx/dev"
SYNC_SUBJECT_PREFIX = "update to"


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        check=False,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed:\n{result.stderr.strip()}")
    return result.stdout


def strip_line(raw: str) -> str:
    return raw[1:].strip() if raw else ""


def is_noise(line: str) -> bool:
    if len(line) < 8:
        return True
    if line.startswith("@") and line[1:].replace(" ", "").isalpha():
        return True
    return all(ch in "{}()[];,.=<>+-*!:?|&" or ch.isspace() for ch in line)


def is_ours(commit_subject: str) -> bool:
    return not commit_subject.lower().startswith(SYNC_SUBJECT_PREFIX)


def sync_removed_lines(sync_sha: str, path: str) -> set:
    diff = git("diff", "--no-renames", f"{sync_sha}^", sync_sha, "--", path)
    removed = set()
    for line in diff.splitlines():
        if line.startswith("---"):
            continue
        if line.startswith("-"):
            stripped = strip_line(line)
            if stripped and not is_noise(stripped):
                removed.add(stripped)
    return removed


def our_added_lines(sync_sha: str, base_ref: str, path: str) -> set:
    log = git(
        "log", f"{base_ref}..{sync_sha}^", "--format=%H %s", "--", path
    )
    our_commits = []
    for entry in log.splitlines():
        if not entry:
            continue
        _sha, subject = entry.split(" ", 1)
        if is_ours(subject):
            our_commits.append(entry.split(" ", 1)[0])
    added = set()
    for sha in our_commits:
        diff = git("show", sha, "--", path)
        for line in diff.splitlines():
            if line.startswith("+++"):
                continue
            if line.startswith("+"):
                stripped = strip_line(line)
                if stripped and not is_noise(stripped):
                    added.add(stripped)
    return added


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("sync_sha", help="squash-merge commit of an upstream sync")
    parser.add_argument(
        "--base",
        default=FROZEN_BASE,
        help=f"frozen fork base ref (default: {FROZEN_BASE})",
    )
    args = parser.parse_args()

    subject = git("log", "-1", "--format=%s", args.sync_sha).strip()
    if is_ours(subject):
        print(f"warning: {args.sync_sha[:10]} may not be a sync commit: «{subject}»")

    sync_files = git(
        "diff", "--no-renames", f"{args.sync_sha}^", args.sync_sha, "--name-only"
    ).splitlines()
    risk_files = [f for f in sync_files if f.endswith((".java", ".kt"))]

    touched_before = defaultdict(bool)
    log_all = git(
        "log", f"{args.base}..{args.sync_sha}^", "--format=%H %s", "--name-only"
    )
    current_is_ours = False
    for line in log_all.splitlines():
        if not line:
            continue
        if len(line) > 40 and line[40] == " " and all(
            c in "0123456789abcdef" for c in line[:40]
        ):
            current_is_ours = is_ours(line[41:])
        elif current_is_ours:
            touched_before[line] = True

    hits = 0
    checked = 0
    for path in risk_files:
        if not touched_before.get(path):
            continue
        checked += 1
        lost = our_added_lines(args.sync_sha, args.base, path) & sync_removed_lines(
            args.sync_sha, path
        )
        if lost:
            hits += len(lost)
            print(f"{path}: {len(lost)} candidate line(s) removed by sync")
            for line in sorted(lost):
                print(f"  - {line[:120]}")

    print(f"\nchecked {checked} risk file(s), {hits} candidate line(s)")
    print("triage each hit: real loss (restore) / API adaptation (ok) / upstream absorbed (ok)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
