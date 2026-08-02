"""
Strict run/parse/compare core for the threshold_SMC conformance gate.

Fail-closed (round 5): non-zero exit from compile.py or Scripts/ring.sh raises
with stderr retained. Parser policy (round-5 re-review, be precise): lines whose
first token is ACCEPT / PAYLOAD / W are RESULT RECORDS and are validated
strictly (arity, range, bit-ness, non-negativity, no duplicates); ALL OTHER
lines are treated as MP-SPDZ framework noise and IGNORED. Tampering with the
result set still cannot pass, because completeness (all 3 ACCEPT + 3 PAYLOAD +
81 W) and uniqueness are enforced: a deleted record -> missing -> raise; an
injected record collides with a filled slot -> duplicate -> raise.

Raw evidence: every run appends a machine-readable JSON record (repo SHA,
MP-SPDZ SHA, query, case id, input hash, return codes, compiler and runtime
stdout/stderr, parsed result) to $EVIDENCE, so the retained artifact is raw, not
a summary.
"""
import hashlib
import json
import os
import subprocess
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oracle import SmcBeliefTracking, REJECT

MPSPDZ = os.environ.get("MPSPDZ", "/tmp/data61_MP-SPDZ")
HERE = os.path.dirname(os.path.abspath(__file__))
EVIDENCE = os.environ.get("EVIDENCE", "")     # path to append JSONL raw evidence
D = [0, 1, 2]
N = 3
S = 27


def state(idx):
    return (idx // 9, (idx // 3) % 3, idx % 3)


def idx_of(s):
    return s[0] * 9 + s[1] * 3 + s[2]


def _git_sha(cwd):
    r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=cwd,
                       capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else "UNKNOWN"


def mpspdz_sha():
    return _git_sha(MPSPDZ)


def repo_sha():
    return os.environ.get("GITHUB_SHA") or _git_sha(HERE)


def _evidence(record):
    if not EVIDENCE:
        return
    os.makedirs(os.path.dirname(EVIDENCE) or ".", exist_ok=True)
    with open(EVIDENCE, "a") as f:
        f.write(json.dumps(record) + "\n")


def write_inputs(secrets, weight_vectors):
    """Write per-party inputs; return a deterministic hash of the exact bytes."""
    os.makedirs(f"{MPSPDZ}/Player-Data", exist_ok=True)
    h = hashlib.sha256()
    for j in range(N):
        w = weight_vectors[j]
        assert len(w) == S and all(isinstance(x, int) and x >= 0 for x in w)
        payload = f"{secrets[j]}\n" + "".join(f"{wv}\n" for wv in w)
        with open(f"{MPSPDZ}/Player-Data/Input-P{j}-0", "w") as f:
            f.write(payload)
        h.update(payload.encode())
    return h.hexdigest()


_compiled = set()


def run_circuit(query, case_id="", input_hash=""):
    subprocess.run(["cp", f"{HERE}/mpc/threshold_smc.mpc",
                    f"{MPSPDZ}/Programs/Source/"], check=True)
    crc, cout, cerr = None, "", ""
    if query not in _compiled:
        c = subprocess.run(["./compile.py", "-R", "64", "threshold_smc", query],
                           cwd=MPSPDZ, capture_output=True, text=True)
        crc, cout, cerr = c.returncode, c.stdout, c.stderr
    r = subprocess.run(["Scripts/ring.sh", f"threshold_smc-{query}"],
                       cwd=MPSPDZ, capture_output=True, text=True)
    _evidence({
        "repo_sha": repo_sha(), "mpspdz_sha": mpspdz_sha(),
        "query": query, "case_id": case_id, "input_hash": input_hash,
        "compile_rc": crc, "compile_stdout": cout, "compile_stderr": cerr,
        "ring_rc": r.returncode, "ring_stdout": r.stdout, "ring_stderr": r.stderr,
    })
    if crc is not None and crc != 0:
        raise RuntimeError(f"compile failed ({crc}):\n{cerr}\n{cout}")
    if r.returncode != 0:                         # FAIL CLOSED
        raise RuntimeError(f"ring.sh failed ({r.returncode}):\n"
                           f"--- stderr ---\n{r.stderr}\n--- stdout ---\n{r.stdout}")
    if query not in _compiled:
        _compiled.add(query)
    return r.stdout


def parse_strict(out):
    acc, pay = {}, {}
    W = {}
    for raw in out.splitlines():
        line = raw.strip()
        if not line:
            continue
        t = line.split()
        tag = t[0]
        if tag not in ("ACCEPT", "PAYLOAD", "W"):   # framework noise: ignore
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


QUERIES = {
    "sum_even": lambda s: int(sum(s) % 2 == 0),
    "p1_is_max": lambda s: int(s[0] >= s[1] and s[0] >= s[2]),
}


def beliefs_from_weights(secrets, weight_vectors):
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
