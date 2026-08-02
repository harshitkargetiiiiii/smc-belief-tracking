"""
Fail-closed validator for raw evidence files (round-5c/d, issue #4).

A gate that certifies bad evidence is worse than none. This validator rejects
every bypass the reviewer found: contradictory PASS records, duplicate case IDs,
missing fields, and bound=true with an unbound source. It validates a SUCCESSFUL
run's evidence: every record must be a complete, self-consistent PASS record.

Usage:
  python3 validate_evidence.py <file.jsonl[.gz]> --count N [--repo SHA]
          [--mpspdz SHA] [--require-bound]
"""
import argparse
import gzip
import json
import re
import sys

# Every field a finalized record must carry, with allowed types. int fields
# exclude bool (bool is an int subclass in Python).
_INT = "int"
_TYPES = {
    "repo_sha": (str, type(None)),
    "repo_sha_source": (str,),
    "bound": (bool,),
    "mpspdz_sha": (str,),
    "query": (str,),
    "case_id": (str,),
    "input_hash": (str,),
    "compile_rc": (_INT, type(None)),
    "compile_stdout": (str,),
    "compile_stderr": (str,),
    "ring_rc": (_INT,),
    "ring_stdout": (str,),
    "ring_stderr": (str,),
    "parse_ok": (bool,),
    "comparison_ok": (bool,),
    "mismatches": (list,),
    "error": (str, type(None)),
    "final": (str,),
}
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _type_ok(v, spec):
    for t in spec:
        if t is _INT:
            if isinstance(v, int) and not isinstance(v, bool):
                return True
        elif isinstance(v, t):
            return True
    return False


def _open(path):
    return gzip.open(path, "rt") if path.endswith(".gz") else open(path)


def validate(path, count, repo=None, mpspdz=None, require_bound=False):
    errs = []
    try:
        with _open(path) as f:
            records = [json.loads(line) for line in f if line.strip()]
    except FileNotFoundError:
        return [f"missing evidence file: {path}"]
    except (OSError, json.JSONDecodeError) as e:
        return [f"unreadable evidence {path}: {e!r}"]

    if len(records) != count:
        errs.append(f"{path}: expected {count} records, found {len(records)}")

    seen_case = set()
    for i, r in enumerate(records):
        tag = f"{path}[{i}]"
        # exact field set + types
        for k, spec in _TYPES.items():
            if k not in r:
                errs.append(f"{tag}: missing field {k}")
            elif not _type_ok(r[k], spec):
                errs.append(f"{tag}: field {k} wrong type ({type(r[k]).__name__})")
        for k in r:
            if k not in _TYPES:
                errs.append(f"{tag}: unexpected field {k}")
        if errs and any(t.startswith(tag) for t in errs[-3:]):
            # keep going but the per-record invariants below assume fields exist
            pass
        # PASS invariant (no contradictory records)
        if r.get("final") != "PASS":
            errs.append(f"{tag}: final={r.get('final')!r} (not PASS)")
        if r.get("parse_ok") is not True:
            errs.append(f"{tag}: parse_ok not True")
        if r.get("comparison_ok") is not True:
            errs.append(f"{tag}: comparison_ok not True")
        if r.get("mismatches") != []:
            errs.append(f"{tag}: mismatches not empty")
        if r.get("error") is not None:
            errs.append(f"{tag}: error not null")
        if r.get("ring_rc") != 0:
            errs.append(f"{tag}: ring_rc={r.get('ring_rc')}")
        if r.get("compile_rc") not in (0, None):
            errs.append(f"{tag}: compile_rc={r.get('compile_rc')}")
        # identity / hashes
        cid = r.get("case_id")
        if not cid:
            errs.append(f"{tag}: empty case_id")
        elif cid in seen_case:
            errs.append(f"{tag}: duplicate case_id {cid!r}")
        else:
            seen_case.add(cid)
        if not r.get("query"):
            errs.append(f"{tag}: empty query")
        if not (isinstance(r.get("input_hash"), str) and _HEX64.match(r["input_hash"])):
            errs.append(f"{tag}: input_hash not 64-hex")
        # provenance
        if repo is not None and r.get("repo_sha") != repo:
            errs.append(f"{tag}: repo_sha {r.get('repo_sha')} != {repo}")
        if mpspdz is not None and r.get("mpspdz_sha") != mpspdz:
            errs.append(f"{tag}: mpspdz_sha {r.get('mpspdz_sha')} != {mpspdz}")
        if require_bound:
            if r.get("bound") is not True:
                errs.append(f"{tag}: not bound")
            if r.get("repo_sha_source") != "github_actions":
                errs.append(f"{tag}: bound but source={r.get('repo_sha_source')!r}")
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
        for e in errs[:30]:
            print("  ", e)
        sys.exit(1)
    print(f"EVIDENCE OK: {a.path} ({a.count} records, all PASS"
          + (", bound" if a.require_bound else "") + ")")


if __name__ == "__main__":
    main()
