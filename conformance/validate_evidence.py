"""
Fail-closed validator for raw evidence files (round-5c, issue #4, blocker 3).

Usage:
  python3 validate_evidence.py <file.jsonl[.gz]> --count N [--repo SHA] \\
          [--mpspdz SHA] [--require-bound]

Exits non-zero if the file is missing, has the wrong record count, is missing
required fields, or (when --require-bound / --repo / --mpspdz are given) any
record is unbound or carries the wrong SHA. This is what stops a run from going
green with missing or mis-provenanced evidence.
"""
import argparse
import gzip
import json
import sys

REQUIRED = (
    "repo_sha", "repo_sha_source", "bound", "mpspdz_sha", "query", "case_id",
    "input_hash", "ring_rc", "ring_stdout", "parse_ok", "comparison_ok", "final",
)


def _open(path):
    return gzip.open(path, "rt") if path.endswith(".gz") else open(path)


def validate(path, count, repo=None, mpspdz=None, require_bound=False):
    errs = []
    try:
        with _open(path) as f:
            records = [json.loads(line) for line in f if line.strip()]
    except FileNotFoundError:
        return [f"missing evidence file: {path}"]

    if len(records) != count:
        errs.append(f"{path}: expected {count} records, found {len(records)}")

    for i, r in enumerate(records):
        for k in REQUIRED:
            if k not in r:
                errs.append(f"{path}[{i}]: missing field {k}")
        if require_bound and not r.get("bound"):
            errs.append(f"{path}[{i}]: unbound evidence (bound={r.get('bound')})")
        if repo is not None and r.get("repo_sha") != repo:
            errs.append(f"{path}[{i}]: repo_sha {r.get('repo_sha')} != {repo}")
        if mpspdz is not None and r.get("mpspdz_sha") != mpspdz:
            errs.append(f"{path}[{i}]: mpspdz_sha {r.get('mpspdz_sha')} != {mpspdz}")
        if r.get("final") != "PASS":
            errs.append(f"{path}[{i}]: final={r.get('final')} (not PASS)")
        if r.get("ring_rc") != 0:
            errs.append(f"{path}[{i}]: ring_rc={r.get('ring_rc')}")
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--count", type=int, required=True)
    ap.add_argument("--repo")
    ap.add_argument("--mpspdz")
    ap.add_argument("--require-bound", action="store_true")
    a = ap.parse_args()
    errs = validate(a.path, a.count, a.repo, a.mpspdz, a.require_bound)
    if errs:
        print(f"EVIDENCE INVALID: {a.path}")
        for e in errs[:20]:
            print("  ", e)
        sys.exit(1)
    print(f"EVIDENCE OK: {a.path} ({a.count} records"
          + (", bound" if a.require_bound else "") + ")")


if __name__ == "__main__":
    main()
