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
import hashlib
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


# Exact typed schema for a private-delivery PASS record. Any field NOT here is
# rejected; any field here with the wrong type is rejected. `party*_rc` uses _INT
# (excludes bool), so a bool masquerading as a return code is caught.
_PRIV_TYPES = {
    "repo_sha": (str, type(None)),
    "repo_sha_source": (str,),
    "bound": (bool,),
    "mpspdz_sha": (str,),
    "query": (str,),
    "case_id": (str,),
    "input_hash": (str,),
    "source_sha256": (str,),
    "delivery_sig": (str,),
    "delivery_private_ok": (bool,),
    "tls_certs_present": (bool,),
    "channel_assumption": (str,),
    "privacy_ok": (bool,),
    "mismatches": (list,),
    "error": (str, type(None)),
    "final": (str,),
}
for _j in range(3):
    _PRIV_TYPES[f"party{_j}_rc"] = (_INT,)
    _PRIV_TYPES[f"party{_j}_stdout"] = (str,)
    _PRIV_TYPES[f"party{_j}_stderr"] = (str,)
    _PRIV_TYPES[f"party{_j}_cmd"] = (str,)

_EXPECTED_QUERIES = ("sum_even", "p1_is_max")


def _recompute_bindings(queries):
    """Independently recompute the expected private-source hash and per-query
    delivery-manifest signature from the CHECKED-OUT source + a fresh compile
    (needs MP-SPDZ). Used by --recompute in CI so a forged source_sha256 or
    delivery_sig cannot pass. Imported lazily -> the plain validator and the
    non-recompute path carry no MP-SPDZ dependency."""
    import delivery_inspect as DI
    from mpc_run import HERE
    src = f"{HERE}/mpc/threshold_smc_private.mpc"
    with open(src, "rb") as f:
        exp_source = hashlib.sha256(f.read()).hexdigest()
    exp_sigs = {}
    for q in queries:
        man = DI.compile_manifest("threshold_smc_private", q, f"asm_val_{q}")
        ok, reasons = DI.is_private_manifest(man)
        if not ok:
            raise RuntimeError(f"recompute: private build not private for {q}: {reasons}")
        exp_sigs[q] = DI.manifest_signature(man)
    return exp_source, exp_sigs


def _recompute_case_table():
    """Rebuild the canonical {input_hash: (query, exp_acc, exp_pay)} table from the
    pinned CASES + the plaintext oracle (no MP-SPDZ). Binds each record to a
    specific case, so a replayed duplicate, an unbound input_hash, or a forged
    verdict value fails (re-review-3 C1/C2/C3)."""
    from private_run import CASES, support_weights
    from mpc_run import oracle_expect
    table = {}
    for secrets, q in CASES:
        wv = support_weights(secrets)
        ih = hashlib.sha256(repr((secrets, wv, q)).encode()).hexdigest()
        exp_acc, exp_pay, _, _ = oracle_expect(secrets, wv, q)
        table[ih] = (q, list(exp_acc), list(exp_pay))
    return table


def validate_private(path, count, repo=None, mpspdz=None, require_bound=False,
                     expected_source_sha256=None, expected_delivery_sigs=None,
                     expected_case_table=None):
    """Typed, exact-schema validator for private-delivery evidence.

    Beyond the earlier flag checks it now (a) enforces an EXACT field set + types
    (an unknown field, or a bool where an int rc is required, is rejected);
    (b) re-parses each party's RETAINED stdout with the strict two-line parser, so
    a fabricated record whose stdout is not exactly that party's own ACCEPT+PAYLOAD
    is rejected; (c) validates the ring command and channel assumption
    semantically; and (d) when given recomputed bindings, requires every record's
    source_sha256 / delivery_sig to equal the independently recomputed values.
    Together these reject the forged bound record the reviewer previously slipped
    past a flag-only check."""
    from private_run import strict_parse_party, CHANNEL_ASSUMPTION
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
    seen = set()
    used_ih = set()
    for i, r in enumerate(records):
        tag = f"{path}[{i}]"
        # (a) exact typed schema
        for k, spec in _PRIV_TYPES.items():
            if k not in r:
                errs.append(f"{tag}: missing field {k}")
            elif not _type_ok(r[k], spec):
                errs.append(f"{tag}: field {k} wrong type ({type(r[k]).__name__})")
        for k in r:
            if k not in _PRIV_TYPES:
                errs.append(f"{tag}: unexpected field {k}")
        # PASS invariant
        if r.get("final") != "PASS":
            errs.append(f"{tag}: final={r.get('final')!r}")
        if r.get("privacy_ok") is not True:
            errs.append(f"{tag}: privacy_ok not True")
        if r.get("delivery_private_ok") is not True:
            errs.append(f"{tag}: delivery_private_ok not True")
        if r.get("tls_certs_present") is not True:
            errs.append(f"{tag}: tls_certs_present not True")
        if r.get("mismatches") != []:
            errs.append(f"{tag}: mismatches not empty")
        if r.get("error") is not None:
            errs.append(f"{tag}: error not null")
        for j in range(3):
            if r.get(f"party{j}_rc") != 0:
                errs.append(f"{tag}: party{j}_rc={r.get(f'party{j}_rc')}")
        # (b) re-parse each party's retained stdout with the strict parser
        q = r.get("query")
        for j in range(3):
            sj = r.get(f"party{j}_stdout")
            if not isinstance(sj, str):
                continue                                 # type error already logged
            try:
                strict_parse_party(sj, j)
            except ValueError as e:
                errs.append(f"{tag}: party{j}_stdout not strict own delivery: {e}")
        # (c) semantic ring command + channel assumption
        for j in range(3):
            cmd = r.get(f"party{j}_cmd", "")
            if not (isinstance(cmd, str) and re.search(
                    rf"replicated-ring-party\.x {j} threshold_smc_private-"
                    rf"{re.escape(str(q))}\b", cmd)):
                errs.append(f"{tag}: party{j}_cmd not the private ring command for query {q!r}")
        if r.get("channel_assumption") != CHANNEL_ASSUMPTION:
            errs.append(f"{tag}: channel_assumption not the pinned encrypted-channel string")
        # hashes are 64-hex
        for k in ("source_sha256", "delivery_sig", "input_hash"):
            v = r.get(k)
            if not (isinstance(v, str) and _HEX64.match(v)):
                errs.append(f"{tag}: {k} not 64-hex")
        # (d) recomputed source / delivery bindings
        if expected_source_sha256 is not None and \
                r.get("source_sha256") != expected_source_sha256:
            errs.append(f"{tag}: source_sha256 != recomputed source hash")
        if expected_delivery_sigs is not None:
            exp = expected_delivery_sigs.get(q)
            if exp is None:
                errs.append(f"{tag}: no recomputed delivery_sig for query {q!r}")
            elif r.get("delivery_sig") != exp:
                errs.append(f"{tag}: delivery_sig != recomputed manifest signature")
        # (e) bind the record to a canonical case: input_hash -> (query, oracle
        # verdict). Rejects replayed duplicates (C1), an unbound/forged input_hash
        # (C2), and verdict values that disagree with the plaintext oracle (C3).
        if expected_case_table is not None:
            ih = r.get("input_hash")
            ent = expected_case_table.get(ih)
            if ent is None:
                errs.append(f"{tag}: input_hash not a canonical case (unbound/forged)")
            elif ih in used_ih:
                errs.append(f"{tag}: replayed canonical case (duplicate input_hash)")
            else:
                used_ih.add(ih)
                exp_q, exp_acc, exp_pay = ent
                if q != exp_q:
                    errs.append(f"{tag}: query {q!r} != canonical {exp_q!r} for this input_hash")
                for j in range(3):
                    sj = r.get(f"party{j}_stdout")
                    if not isinstance(sj, str):
                        continue
                    try:
                        got = strict_parse_party(sj, j)
                    except ValueError:
                        continue                             # (b) already logged it
                    if got.get("ACCEPT") != exp_acc[j] or got.get("PAYLOAD") != exp_pay[j]:
                        errs.append(f"{tag}: party{j} verdict {got} != oracle "
                                    f"(ACCEPT {exp_acc[j]}, PAYLOAD {exp_pay[j]})")
        # identity + provenance
        cid = r.get("case_id")
        if not cid or cid in seen:
            errs.append(f"{tag}: bad/duplicate case_id {cid!r}")
        else:
            seen.add(cid)
        if repo is not None and r.get("repo_sha") != repo:
            errs.append(f"{tag}: repo_sha {r.get('repo_sha')} != {repo}")
        if mpspdz is not None and r.get("mpspdz_sha") != mpspdz:
            errs.append(f"{tag}: mpspdz_sha {r.get('mpspdz_sha')} != {mpspdz}")
        if require_bound:
            if r.get("bound") is not True:
                errs.append(f"{tag}: not bound")
            if r.get("repo_sha_source") != "github_actions":
                errs.append(f"{tag}: bound but source={r.get('repo_sha_source')!r}")
    if expected_case_table is not None and used_ih != set(expected_case_table):
        errs.append(f"{path}: evidence does not cover the canonical case set "
                    f"(covered {len(used_ih)}/{len(expected_case_table)})")
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--count", type=int, required=True)
    ap.add_argument("--repo")
    ap.add_argument("--mpspdz")
    ap.add_argument("--require-bound", action="store_true")
    ap.add_argument("--private", action="store_true",
                    help="validate private-delivery evidence schema")
    ap.add_argument("--recompute", action="store_true",
                    help="independently recompute source/delivery bindings from the "
                         "checked-out source + a fresh compile (needs MP-SPDZ)")
    a = ap.parse_args()
    if a.private:
        kw = {}
        if a.recompute:
            exp_src, exp_sigs = _recompute_bindings(_EXPECTED_QUERIES)
            kw = dict(expected_source_sha256=exp_src, expected_delivery_sigs=exp_sigs,
                      expected_case_table=_recompute_case_table())
        errs = validate_private(a.path, a.count, a.repo, a.mpspdz, a.require_bound, **kw)
    else:
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
