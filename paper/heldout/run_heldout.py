#!/usr/bin/env python3
"""
Single-run held-out evaluation harness for the FROZEN delivery linter
conformance/delivery_inspect.py @ 305a3a8.

ORCHESTRATION GLUE ONLY. Every PASS/REJECT verdict is produced by the frozen
delivery_inspect.is_private_manifest; every oracle verdict by the frozen
mpc_run.oracle_expect + private_run.strict_parse_party; every provenance verdict by
the frozen validate_evidence.py. This harness compiles/loads mutants and records
outcomes; it makes no detection or oracle decision of its own and NEVER modifies
the checker.

Fail-closed: aborts unless the imported delivery_inspect.py has the frozen git-blob
hash and MP-SPDZ is the pin.

Env:  PYTHONPATH -> FROZEN conformance/ ; HELDOUT -> this dir ; MPSPDZ -> pinned MP-SPDZ.
Output: $HELDOUT/results.json  (per-mutant records + summary). Deterministic.
"""
import glob
import hashlib
import json
import os
import subprocess
import sys

HELDOUT = os.environ["HELDOUT"]
sys.path.insert(0, HELDOUT)
import corpus as C
import synthetic_transforms as T

import delivery_inspect as DI
from mpc_run import MPSPDZ, N, S, state, oracle_expect, write_inputs
from private_run import strict_parse_party

QUERY = "p1_is_max"                      # query compiled for the linter probe (matches detection_matrix)


# --------------------------------------------------------- fail-closed checker --
def _git_blob_sha1(path):
    b = open(path, "rb").read()
    h = hashlib.sha1()
    h.update(b"blob " + str(len(b)).encode() + b"\0" + b)
    return h.hexdigest()


CHECKER_PATH = os.path.join(os.path.dirname(DI.__file__), "delivery_inspect.py")
blob = _git_blob_sha1(CHECKER_PATH)
if blob != C.CHECKER_BASELINE["delivery_inspect_blob"]:
    sys.exit(f"FAIL CLOSED: delivery_inspect.py blob {blob} != frozen "
             f"{C.CHECKER_BASELINE['delivery_inspect_blob']}")
mp = subprocess.run(["git", "rev-parse", "HEAD"], cwd=MPSPDZ,
                    capture_output=True, text=True).stdout.strip()
if mp != C.CHECKER_BASELINE["mpspdz_pin"]:
    sys.exit(f"FAIL CLOSED: MP-SPDZ {mp} != pin {C.CHECKER_BASELINE['mpspdz_pin']}")
print(f"[checker] delivery_inspect.py blob {blob} (frozen 305a3a8) ; MP-SPDZ {mp} (pin) -- verified")


# --------------------------------------------------------- glue helpers ---------
def compile_manifest_from(src, stem, query, prefix):
    """Compile an arbitrary .mpc to a {tape_kind: asm} manifest (mirrors the asm read
    in DI.compile_manifest). Raises RuntimeError on compile failure (-> compile-invalid)."""
    subprocess.run(["cp", src, f"{MPSPDZ}/Programs/Source/{stem}.mpc"], check=True)
    marker = f"{stem}-{query}-"
    for f in glob.glob(f"{MPSPDZ}/{prefix}-{marker}*"):
        os.remove(f)
    c = subprocess.run(["./compile.py", "-R", "64", "-a", prefix, stem, query],
                       cwd=MPSPDZ, capture_output=True, text=True)
    if c.returncode != 0:
        raise RuntimeError((c.stderr + c.stdout).strip()[-600:])
    man = {}
    for f in sorted(glob.glob(f"{MPSPDZ}/{prefix}-{marker}*")):
        kind = os.path.basename(f).split(marker, 1)[1]
        man[kind] = open(f).read()
    return man


def _support(j, sj):
    return [i for i in range(S) if state(i)[j] == sj]


def _wv_uniform(secrets):
    out = []
    for j in range(N):
        w = [0] * S
        for i in _support(j, secrets[j]):
            w[i] = 1
        out.append(w)
    return out


def run_oracle_cases(stem):
    """Compile the mutant to bytecode and run each pre-registered case at the pin.
    Returns (oracle_fail, runtime_reject, details): oracle_fail if any case's parsed
    delivery != frozen oracle; runtime_reject if any party's stream raises in the
    frozen strict parser (e.g. a foreign 'PRIV j' record). Frozen oracle + parser."""
    # the mutant .mpc is already at Programs/Source/<stem>.mpc (copied for the -a
    # linter compile); each case compiles its own query to bytecode below.
    oracle_fail = False
    runtime_reject = False
    details = []
    base_port = 17000
    for ci, (secrets, q) in enumerate(C.CASES_FOR_ORACLE):
        wv = _wv_uniform(secrets)
        cc = subprocess.run(["./compile.py", "-R", "64", stem, q],
                            cwd=MPSPDZ, capture_output=True, text=True)
        if cc.returncode != 0:
            details.append({"case": [secrets, q], "error": "compile_failed"})
            continue
        write_inputs(secrets, wv)
        prog = f"{stem}-{q}"
        port = str(base_port + ci)
        procs = []
        for i in range(N):
            cmd = [f"{MPSPDZ}/replicated-ring-party.x", str(i), prog,
                   "-pn", port, "-h", "localhost", "-OF", "."]
            procs.append(subprocess.Popen(cmd, cwd=MPSPDZ, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE, text=True))
        outs, rcs = {}, {}
        for i, p in enumerate(procs):
            o, e = p.communicate(timeout=120)
            outs[i], rcs[i] = o, p.returncode
        if any(v != 0 for v in rcs.values()):
            details.append({"case": [secrets, q], "rc": rcs, "note": "nonzero rc"})
            continue
        exp_acc, exp_pay, _, _ = oracle_expect(secrets, wv, q)
        case_reject, case_mismatch = None, []
        for i in range(N):
            try:
                got = strict_parse_party(outs[i], i)
            except ValueError as ex:
                case_reject = f"party {i}: {ex}"
                runtime_reject = True
                break
            if got["ACCEPT"] != exp_acc[i] or got["PAYLOAD"] != exp_pay[i]:
                case_mismatch.append({"party": i, "got": got,
                                      "oracle": {"ACCEPT": exp_acc[i], "PAYLOAD": exp_pay[i]}})
        if case_mismatch:
            oracle_fail = True
        details.append({"case": [secrets, q],
                        "runtime_reject": case_reject,
                        "oracle_mismatch": case_mismatch})
    return oracle_fail, runtime_reject, details


# --------------------------------------------------------- honest base ----------
honest = DI.compile_manifest("threshold_smc_private", QUERY, "asm_honest")
ok_h, r_h = DI.is_private_manifest(honest, DI.EXPECTED_SUBTAPES)
assert ok_h, f"sanity: honest build must PASS, got {r_h}"
print(f"[base] honest build PASS ; subtapes {sorted(DI._base(k) for k in honest if DI._base(k)!='0')}")


# --------------------------------------------------------- provenance eval ------
def provenance_eval(which):
    """Generate a fresh private evidence file at the frozen checkout, then probe the
    FROZEN validate_evidence.py. Returns (validate_rejected, detail)."""
    ev = os.path.join(HELDOUT, "_prov_evidence.jsonl")
    r = subprocess.run([sys.executable, os.path.join(os.path.dirname(DI.__file__), "private_run.py")],
                       cwd=os.path.dirname(DI.__file__),
                       env={**os.environ, "EVIDENCE": ev, "MPSPDZ": MPSPDZ},
                       capture_output=True, text=True)
    if not os.path.exists(ev):
        return None, {"error": "could not generate evidence", "stderr": r.stderr[-400:]}
    recs = [json.loads(l) for l in open(ev) if l.strip()]
    validator = os.path.join(os.path.dirname(DI.__file__), "validate_evidence.py")
    pin = C.CHECKER_BASELINE["mpspdz_pin"]
    if which == "prov_forge_sig":
        recs[0]["delivery_sig"] = "0" * 50                       # forge the delivery signature
        bad = os.path.join(HELDOUT, "_prov_forged.jsonl")
        open(bad, "w").write("\n".join(json.dumps(x) for x in recs) + "\n")
        v = subprocess.run([sys.executable, validator, bad, "--count", str(len(recs)),
                            "--private", "--mpspdz", pin, "--recompute"],
                           cwd=os.path.dirname(DI.__file__), env={**os.environ, "MPSPDZ": MPSPDZ},
                           capture_output=True, text=True)
    elif which == "prov_wrong_repo":
        v = subprocess.run([sys.executable, validator, ev, "--count", str(len(recs)),
                            "--private", "--repo", "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
                            "--mpspdz", pin],
                           cwd=os.path.dirname(DI.__file__), env={**os.environ, "MPSPDZ": MPSPDZ},
                           capture_output=True, text=True)
    else:
        return None, {"error": "unknown prov eval"}
    rejected = (v.returncode != 0)
    return rejected, {"returncode": v.returncode, "stdout": v.stdout.strip()[-300:]}


# --------------------------------------------------------- main loop ------------
results = []
for m in C.CORPUS:
    rec = {k: m[k] for k in ("id", "category", "kind", "title", "genuine_violation",
                             "realizable", "predicted_compile", "predicted_linter",
                             "predicted_rule", "oracle_needed", "bucket", "denominator")}
    try:
        if m["kind"] == "source":
            stem = m["id"].replace("-", "_")
            src = os.path.join(HELDOUT, m["ref"])
            try:
                man = compile_manifest_from(src, stem, QUERY, f"asm_{stem}")
                rec["compile"] = "valid"
            except RuntimeError as ex:
                rec["compile"] = "invalid"
                rec["compile_error"] = str(ex)[-300:]
                rec["linter"] = "n/a"
                results.append(rec)
                continue
            ok, reasons = DI.is_private_manifest(man, DI.EXPECTED_SUBTAPES)
            rec["linter"] = "PASS" if ok else "REJECT"
            rec["linter_reasons"] = reasons
            rec["manifest_signature"] = DI.manifest_signature(man)
            if m["oracle_needed"] and ok:
                of, rr, det = run_oracle_cases(stem)
                rec["oracle_fail"] = of
                rec["runtime_layer_reject"] = rr
                rec["runtime_detail"] = det
        elif m["kind"] == "synthetic":
            rec["compile"] = "n/a"
            man = T.TRANSFORMS[m["ref"]](honest)
            ok, reasons = DI.is_private_manifest(man, DI.EXPECTED_SUBTAPES)
            rec["linter"] = "PASS" if ok else "REJECT"
            rec["linter_reasons"] = reasons
            rec["manifest_signature"] = DI.manifest_signature(man)
        elif m["kind"] == "provenance":
            rec["compile"] = "n/a"
            rec["linter"] = "n/a (targets validate_evidence.py)"
            rejected, detail = provenance_eval(m["ref"])
            rec["validate_evidence_rejected"] = rejected
            rec["validate_detail"] = detail
    except Exception as ex:                              # never abort the whole run
        rec["harness_error"] = repr(ex)[-300:]
    results.append(rec)
    print(f"  {rec['id']:5} {rec['category']:15} compile={rec.get('compile'):5} "
          f"linter={rec.get('linter')}  pred={m['predicted_linter']}"
          + (f"  oracle_fail={rec.get('oracle_fail')}" if 'oracle_fail' in rec else "")
          + (f"  runtime_reject={rec.get('runtime_layer_reject')}" if 'runtime_layer_reject' in rec else "")
          + (f"  validate_rejected={rec.get('validate_evidence_rejected')}" if 'validate_evidence_rejected' in rec else ""))


# --------------------------------------------------------- summary --------------
def _match(m, rec):
    p = m["predicted_linter"]
    a = rec.get("linter")
    if p in ("PASS", "REJECT"):
        return a == p
    return None


by_id = {m["id"]: m for m in C.CORPUS}
struct = [r for r in results if r["bucket"] == "structural_security"]
struct_valid = [r for r in struct if r.get("compile") in ("valid", "n/a")]
strict = [r for r in struct_valid if r["denominator"] == "strict"]
inclusive = struct_valid  # strict + inclusive (all structural_security compile-valid)

def _rej(rs):
    return sum(1 for r in rs if r.get("linter") == "REJECT")

summary = {
    "checker_baseline": C.CHECKER_BASELINE,
    "n_mutants": len(results),
    "prediction_matches": sum(1 for r in results
                              for m in [by_id[r["id"]]] if _match(m, r) is True),
    "prediction_mismatches": [r["id"] for r in results
                              for m in [by_id[r["id"]]] if _match(m, r) is False],
    "strict_denominator": {
        "n": len(strict), "rejected": _rej(strict),
        "rate": (_rej(strict) / len(strict)) if strict else None,
        "false_accepts": [r["id"] for r in strict if r.get("linter") == "PASS"],
    },
    "inclusive_denominator": {
        "n": len(inclusive), "rejected": _rej(inclusive),
        "rate": (_rej(inclusive) / len(inclusive)) if inclusive else None,
        "false_accepts": [r["id"] for r in inclusive if r.get("linter") == "PASS"],
    },
    "semantic_out_of_scope": {
        "ids": [r["id"] for r in results if r["bucket"] == "semantic_out_of_scope"],
        "linter_pass": [r["id"] for r in results
                        if r["bucket"] == "semantic_out_of_scope" and r.get("linter") == "PASS"],
        "oracle_fail": [r["id"] for r in results
                        if r["bucket"] == "semantic_out_of_scope" and r.get("oracle_fail")],
    },
    "benign": {
        "correct_accept": [r["id"] for r in results
                           if r["bucket"] == "benign" and r.get("linter") == "PASS"],
        "false_reject": [r["id"] for r in results
                         if r["bucket"] == "benign" and r.get("linter") == "REJECT"],
    },
    "compile_invalid": [r["id"] for r in results if r["bucket"] == "compile_invalid"],
    "compile_invalid_actual": [r["id"] for r in results if r.get("compile") == "invalid"],
    "provenance": {r["id"]: r.get("validate_evidence_rejected")
                   for r in results if r["bucket"] == "provenance_other_checker"},
    "runtime_layer_rejects": [r["id"] for r in results if r.get("runtime_layer_reject")],
}

out = {"summary": summary, "results": results}
open(os.path.join(HELDOUT, "results.json"), "w").write(json.dumps(out, indent=2))
print("\n[summary]")
print(f"  prediction matches: {summary['prediction_matches']}/{len(results)}"
      f"  mismatches: {summary['prediction_mismatches']}")
print(f"  strict delivery detection: {summary['strict_denominator']['rejected']}/"
      f"{summary['strict_denominator']['n']} "
      f"false-accepts={summary['strict_denominator']['false_accepts']}")
print(f"  inclusive delivery detection: {summary['inclusive_denominator']['rejected']}/"
      f"{summary['inclusive_denominator']['n']} "
      f"false-accepts={summary['inclusive_denominator']['false_accepts']}")
print(f"  semantic PASS={summary['semantic_out_of_scope']['linter_pass']} "
      f"oracle_fail={summary['semantic_out_of_scope']['oracle_fail']}")
print(f"  benign correct-accept={summary['benign']['correct_accept']} "
      f"false-reject={summary['benign']['false_reject']}")
print(f"  compile-invalid={summary['compile_invalid_actual']}  "
      f"provenance={summary['provenance']}  runtime_rejects={summary['runtime_layer_rejects']}")
print("\nwrote results.json")
