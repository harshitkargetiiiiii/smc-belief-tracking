"""
Strict run/parse/compare core for the threshold_SMC conformance gate.

Round-5 review (issue #4) found the previous harness unsound as a gate:
- Scripts/ring.sh ran without checking its exit status (a forced rc=73 passed);
- the parser pre-filled 81 zero weights and did not enforce
  completeness/uniqueness (deleting all zero rows still "passed").

This module fails closed: non-zero exit -> raise (with stderr); the parser
requires exactly one ACCEPT/PAYLOAD per party and exactly one W per (party,idx),
rejects duplicates, missing rows, out-of-range indices, malformed and unexpected
records. Expected values are computed by the independent Fraction oracle and
never enter the circuit.
"""
import os
import subprocess
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oracle import SmcBeliefTracking, REJECT

MPSPDZ = os.environ.get("MPSPDZ", "/tmp/data61_MP-SPDZ")
HERE = os.path.dirname(os.path.abspath(__file__))
D = [0, 1, 2]
N = 3
S = 27


def state(idx):
    return (idx // 9, (idx // 3) % 3, idx % 3)


def idx_of(s):
    return s[0] * 9 + s[1] * 3 + s[2]


def mpspdz_sha():
    r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=MPSPDZ,
                       capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else "UNKNOWN"


def write_inputs(secrets, weight_vectors):
    """weight_vectors: list of N dense length-27 non-negative integer vectors."""
    os.makedirs(f"{MPSPDZ}/Player-Data", exist_ok=True)
    for j in range(N):
        w = weight_vectors[j]
        assert len(w) == S and all(isinstance(x, int) and x >= 0 for x in w)
        with open(f"{MPSPDZ}/Player-Data/Input-P{j}-0", "w") as f:
            f.write(f"{secrets[j]}\n")
            for wv in w:
                f.write(f"{wv}\n")


_compiled = set()


def run_circuit(query):
    subprocess.run(["cp", f"{HERE}/mpc/threshold_smc.mpc",
                    f"{MPSPDZ}/Programs/Source/"], check=True)
    if query not in _compiled:
        c = subprocess.run(["./compile.py", "-R", "64", "threshold_smc", query],
                           cwd=MPSPDZ, capture_output=True, text=True)
        if c.returncode != 0:
            raise RuntimeError(f"compile failed ({c.returncode}):\n{c.stderr}\n{c.stdout}")
        _compiled.add(query)
    r = subprocess.run(["Scripts/ring.sh", f"threshold_smc-{query}"],
                       cwd=MPSPDZ, capture_output=True, text=True)
    if r.returncode != 0:                       # FAIL CLOSED on non-zero exit
        raise RuntimeError(f"ring.sh failed ({r.returncode}):\n"
                           f"--- stderr ---\n{r.stderr}\n--- stdout ---\n{r.stdout}")
    return r.stdout


def parse_strict(out):
    """Require exactly one ACCEPT j, one PAYLOAD j (j in 0..N-1) and one W j idx
    (idx in 0..S-1). Reject duplicates/missing/out-of-range/malformed/unexpected."""
    acc, pay = {}, {}
    W = {}
    for raw in out.splitlines():
        line = raw.strip()
        if not line:
            continue
        t = line.split()
        tag = t[0]
        # Only ACCEPT/PAYLOAD/W are result records; everything else is MP-SPDZ
        # framework noise and is ignored. Tampering with the result set cannot
        # hide here: completeness (all 81 W + 3 accept/payload) and uniqueness
        # are enforced below, so a deleted row -> missing -> raise, and an
        # injected row collides with a filled slot -> duplicate -> raise.
        if tag not in ("ACCEPT", "PAYLOAD", "W"):
            continue
        if tag == "ACCEPT":
            if len(t) != 3:
                raise ValueError(f"malformed ACCEPT: {raw!r}")
            j, v = int(t[1]), int(t[2])
            if not (0 <= j < N):
                raise ValueError(f"ACCEPT party out of range: {raw!r}")
            if j in acc:
                raise ValueError(f"duplicate ACCEPT {j}")
            if v not in (0, 1):
                raise ValueError(f"ACCEPT not a bit: {raw!r}")
            acc[j] = v
        elif tag == "PAYLOAD":
            if len(t) != 3:
                raise ValueError(f"malformed PAYLOAD: {raw!r}")
            j, v = int(t[1]), int(t[2])
            if not (0 <= j < N):
                raise ValueError(f"PAYLOAD party out of range: {raw!r}")
            if j in pay:
                raise ValueError(f"duplicate PAYLOAD {j}")
            pay[j] = v
        elif tag == "W":
            if len(t) != 4:
                raise ValueError(f"malformed W: {raw!r}")
            j, idx, v = int(t[1]), int(t[2]), int(t[3])
            if not (0 <= j < N) or not (0 <= idx < S):
                raise ValueError(f"W index out of range: {raw!r}")
            if (j, idx) in W:
                raise ValueError(f"duplicate W {j} {idx}")
            if v < 0:
                raise ValueError(f"negative weight: {raw!r}")
            W[(j, idx)] = v
        else:
            raise ValueError(f"unexpected record: {raw!r}")
    # completeness
    for j in range(N):
        if j not in acc:
            raise ValueError(f"missing ACCEPT {j}")
        if j not in pay:
            raise ValueError(f"missing PAYLOAD {j}")
        for idx in range(S):
            if (j, idx) not in W:
                raise ValueError(f"missing W {j} {idx}")
    Wl = [[W[(j, idx)] for idx in range(S)] for j in range(N)]
    return acc, pay, Wl


# ---- oracle-side expectation, decision routed through the Fraction oracle ----

QUERIES = {
    "sum_even": lambda s: int(sum(s) % 2 == 0),
    "p1_is_max": lambda s: int(s[0] >= s[1] and s[0] >= s[2]),
}


def beliefs_from_weights(secrets, weight_vectors):
    """Normalized Fraction beliefs from integer weight vectors (valid Sigma_T:
    each party's support lies within x_j = s_j)."""
    beliefs = []
    for j in range(N):
        w = weight_vectors[j]
        tot = sum(w)
        assert tot > 0
        b = {}
        for idx in range(S):
            if w[idx] > 0:
                s = state(idx)
                assert s[j] == secrets[j], "invalid Sigma_T: support off x_j=s_j"
                b[s] = Fraction(w[idx], tot)
        beliefs.append(b)
    return beliefs


def oracle_expect(secrets, weight_vectors, query):
    qfn = QUERIES[query]
    m = SmcBeliefTracking.__new__(SmcBeliefTracking)
    m.n, m.domain, m.secrets = N, list(D), tuple(secrets)
    m.thresholds = [Fraction(1, 2)] * N
    m.beliefs = beliefs_from_weights(secrets, weight_vectors)
    o_actual = qfn(secrets)
    visible = m.invoke(qfn)
    exp_acc = [0 if v == REJECT else 1 for v in visible]
    exp_pay = [o_actual if v != REJECT else 0 for v in visible]
    return exp_acc, exp_pay, m.beliefs, o_actual


def proportional_equal(wvec, belief):
    supp_w = {idx for idx, x in enumerate(wvec) if x > 0}
    supp_b = {idx_of(s) for s in belief}
    if supp_w != supp_b:
        return False
    if not supp_w:
        return True
    sw = sum(wvec)
    return all(Fraction(wvec[idx], sw) == belief[state(idx)] for idx in supp_w)


def compare(secrets, weight_vectors, query, acc, pay, Wl):
    """Return list of mismatch strings ([] == pass)."""
    exp_acc, exp_pay, exp_beliefs, _ = oracle_expect(secrets, weight_vectors, query)
    msgs = []
    for j in range(N):
        if acc[j] != exp_acc[j]:
            msgs.append(f"accept[{j}] circuit {acc[j]} != oracle {exp_acc[j]}")
        if pay[j] != exp_pay[j]:
            msgs.append(f"payload[{j}] circuit {pay[j]} != oracle {exp_pay[j]}")
        if not proportional_equal(Wl[j], exp_beliefs[j]):
            msgs.append(f"weights[{j}] not proportional to oracle belief")
    return msgs
