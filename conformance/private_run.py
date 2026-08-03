"""
Private-delivery gate (staged gate 2, re-review). Three layers:

1. COMPILED-DELIVERY inspection (delivery_inspect): the private build must
   deliver the six verdicts via `privateoutput`, and the leaky sibling must be
   rejected. A stdout oracle cannot distinguish these; this does.
2. STRICT per-party runtime check: each party's stdout must contain exactly one
   own ACCEPT and one own PAYLOAD, no duplicate/foreign/unknown verdict lines;
   fail closed on missing streams. Cross-party verdicts raise.
3. BOUND raw evidence: per case, retain each party's raw stdout/stderr, rc, the
   command, source/delivery hashes, provenance, and encrypted-channel status.

Functional demonstration only; NOT a simulation-security proof (ADVERSARY.md).
"""
import glob
import hashlib
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mpc_run import (
    MPSPDZ, HERE, N, write_inputs, oracle_expect, mpspdz_sha, repo_provenance,
    _evidence,
)
import delivery_inspect

PORT = int(os.environ.get("PRIV_PORT", "15577"))
_compiled = set()
PRIV = re.compile(r"^PRIV (\d+) (ACCEPT|PAYLOAD) (-?\d+)$")

CHANNEL_ASSUMPTION = ("authenticated encrypted point-to-point (TLS via "
                      "setup-ssl); required for honest-majority Rep3")

# The pinned canonical case set. Single source of truth for the runner AND the
# evidence validator's --recompute case-table binding (re-review-3): the validator
# recomputes each case's input_hash + oracle verdict from THIS list, so replayed
# duplicates and forged verdict values are rejected.
CASES = [((0, 0, 1), "sum_even"), ((0, 0, 1), "p1_is_max"),
         ((2, 0, 0), "p1_is_max"), ((1, 2, 0), "sum_even")]


def _sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def tls_certs_present():
    return len(glob.glob(f"{MPSPDZ}/Player-Data/*.pem")) >= N


def _compile(query):
    subprocess.run(["cp", f"{HERE}/mpc/threshold_smc_private.mpc",
                    f"{MPSPDZ}/Programs/Source/"], check=True)
    if query not in _compiled:
        c = subprocess.run(["./compile.py", "-R", "64", "threshold_smc_private", query],
                           cwd=MPSPDZ, capture_output=True, text=True)
        if c.returncode != 0:
            raise RuntimeError(f"compile failed:\n{c.stderr}\n{c.stdout}")
        _compiled.add(query)


def run_private(secrets, weight_vectors, query, port=None):
    """Run all 3 parties; return {j: {stdout, stderr, rc, cmd}}. Fail closed."""
    port = port or PORT
    write_inputs(secrets, weight_vectors)
    _compile(query)
    prog = f"threshold_smc_private-{query}"
    procs, res = [], {}
    for i in range(N):
        cmd = [f"{MPSPDZ}/replicated-ring-party.x", str(i), prog,
               "-pn", str(port), "-h", "localhost", "-OF", "."]
        p = subprocess.Popen(cmd, cwd=MPSPDZ, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, text=True)
        procs.append((cmd, p))
    for i, (cmd, p) in enumerate(procs):
        out, err = p.communicate(timeout=120)
        res[i] = {"stdout": out, "stderr": err, "rc": p.returncode, "cmd": cmd}
    for i in range(N):
        if res[i]["rc"] != 0:
            raise RuntimeError(f"party {i} failed ({res[i]['rc']}):\n{res[i]['stderr']}")
    return res


def strict_parse_party(text, own_j):
    """Return {'ACCEPT': v, 'PAYLOAD': v} for party own_j's OWN stream, or raise.

    EXACT two-line enforcement (gate-2 re-review-2, blocker 2). The private build
    emits program output ONLY via print_ln_to(own_j, ...), so a correct run's
    STDOUT is exactly two non-empty lines: one own ACCEPT and one own PAYLOAD.
    Every framework diagnostic ('Trying to run', 'Time =', 'Data sent', ...) goes
    to STDERR, never stdout (verified live against replicated-ring-party.x). So we
    do NOT skip any line by an allowlist -- the previous version's fatal weakness.
    EVERY non-empty stdout line must be a well-formed own PRIV record, and there
    must be exactly two of them. An unconditional public leak (e.g. a separate
    tape's print_ln('LEAK ...')) surfaces here as a forbidden third line and is
    rejected; a foreign / duplicate / malformed / missing record also raises."""
    nonempty = [ln.strip() for ln in text.splitlines() if ln.strip()]
    records = {}
    for s in nonempty:
        m = PRIV.match(s)
        if not m:
            raise ValueError(f"unrecognized stdout line: {s!r}")
        j, kind, val = int(m.group(1)), m.group(2), int(m.group(3))
        if j != own_j:
            raise ValueError(f"foreign verdict for party {j} in party {own_j} stream")
        if kind in records:
            raise ValueError(f"duplicate {kind} in party {own_j} stream")
        records[kind] = val
    if len(nonempty) != 2 or set(records) != {"ACCEPT", "PAYLOAD"}:
        raise ValueError(f"party {own_j}: expected exactly one ACCEPT + one "
                         f"PAYLOAD stdout line, got {len(nonempty)} line(s) "
                         f"{sorted(records)}")
    return records


def evaluate_privacy(outs, exp_acc, exp_pay):
    """Strict per-party check. `outs` maps j -> stdout text (or the run dict).
    Returns list of failure messages ([] == clean)."""
    msgs = []
    for j in range(N):
        text = outs[j]["stdout"] if isinstance(outs[j], dict) else outs[j]
        try:
            got = strict_parse_party(text, j)
        except ValueError as e:
            msgs.append(f"party {j}: {e}")
            continue
        if got["ACCEPT"] != exp_acc[j]:
            msgs.append(f"party {j} own ACCEPT {got['ACCEPT']} != {exp_acc[j]}")
        if got["PAYLOAD"] != exp_pay[j]:
            msgs.append(f"party {j} own PAYLOAD {got['PAYLOAD']} != {exp_pay[j]}")
    return msgs


def parse_party(text):                                 # kept for unit tests
    got = {"ACCEPT": {}, "PAYLOAD": {}}
    for line in text.splitlines():
        m = PRIV.match(line.strip())
        if m:
            got[m.group(2)][int(m.group(1))] = int(m.group(3))
    return got


def check_case(secrets, weight_vectors, query, case_id, delivery_sig):
    exp_acc, exp_pay, _, _ = oracle_expect(secrets, weight_vectors, query)
    sha, src, bound = repo_provenance()
    ih = hashlib.sha256(repr((secrets, weight_vectors, query)).encode()).hexdigest()
    rec = {
        "repo_sha": sha, "repo_sha_source": src, "bound": bound,
        "mpspdz_sha": mpspdz_sha(), "query": query, "case_id": case_id,
        "input_hash": ih,
        "source_sha256": _sha256_file(f"{HERE}/mpc/threshold_smc_private.mpc"),
        "delivery_sig": delivery_sig, "delivery_private_ok": True,
        "tls_certs_present": tls_certs_present(),
        "channel_assumption": CHANNEL_ASSUMPTION,
        "privacy_ok": False, "mismatches": None, "error": None, "final": "FAIL",
    }
    try:
        res = run_private(secrets, weight_vectors, query)
    except Exception as e:
        rec["error"] = repr(e)
        _evidence(rec)
        raise
    for j in range(N):
        rec[f"party{j}_rc"] = res[j]["rc"]
        rec[f"party{j}_stdout"] = res[j]["stdout"]
        rec[f"party{j}_stderr"] = res[j]["stderr"]
        rec[f"party{j}_cmd"] = " ".join(res[j]["cmd"])
    msgs = evaluate_privacy(res, exp_acc, exp_pay)
    rec["privacy_ok"] = not msgs
    rec["mismatches"] = msgs
    rec["final"] = "PASS" if not msgs else "FAIL"
    _evidence(rec)
    return (not msgs), msgs


def support_weights(secrets):
    from mpc_run import S, state
    return [[1 if state(i)[j] == secrets[j] else 0 for i in range(S)]
            for j in range(N)]


def main():
    print(f"MP-SPDZ commit under test: {mpspdz_sha()}")
    print(f"TLS certs present: {tls_certs_present()}")
    ok_all = True

    # Layer 1: compiled-delivery inspection + executable public-open negative control
    delivery_sig = {}
    for q in ("sum_even", "p1_is_max"):
        ok, d = delivery_inspect.gate(q)
        delivery_sig[q] = d["private_delivery_sig"]
        print(f"[delivery] {q}: private_ok={d['private_ok']} "
              f"leaky_rejected={d['leaky_rejected']} "
              f"subleak_rejected={d['subleak_rejected']} "
              f"namespoof_rejected={d['namespoof_rejected']} "
              f"openfalse_rejected={d['openfalse_rejected']} "
              f"openfalse_vec_rejected={d['openfalse_vec_rejected']} -> {'PASS' if ok else 'FAIL'}")
        if not ok:
            print("   ", d.get("private_reasons"))
        ok_all = ok_all and ok

    # Layer 2+3: strict runtime + bound evidence
    for secrets, q in CASES:
        ok, msgs = check_case(secrets, support_weights(secrets), q,
                              f"{secrets}-{q}", delivery_sig[q])
        print(f"[private] secrets={secrets} q={q} -> {'PASS' if ok else 'FAIL'}")
        for m in msgs:
            print("    ", m)
        ok_all = ok_all and ok

    print("=" * 56)
    print("PRIVATE DELIVERY OK" if ok_all else "PRIVATE DELIVERY FAILED")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
