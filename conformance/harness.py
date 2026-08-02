"""
External conformance harness for the threshold_SMC circuit.

Runs the MP-SPDZ circuit on the pinned fixture (two invocations) AND one
additional valid state, and compares the circuit's revealed verdicts, payloads,
and reconstructed belief weights against the plaintext oracle.

The expected values are computed by the oracle and live ONLY here — they never
enter the circuit (INTERFACE.md anti-cheating rule). The circuit's reveals are
test-only reconstruction; a deployment returns private shares (see NOTES.md).

Requires a built MP-SPDZ with replicated-ring-party.x. Set MPSPDZ to its path.
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
HALF = Fraction(1, 2)

QUERIES = {
    "sum_even": lambda s: int(sum(s) % 2 == 0),
    "p1_is_max": lambda s: int(s[0] >= s[1] and s[0] >= s[2]),
}


def idx_of(s):
    return s[0] * 9 + s[1] * 3 + s[2]


def dense_weights(belief):
    """Oracle belief (uniform over support) -> dense 0/1 integer weight vector.
    Asserts uniform-over-support so 0/1 weights are exact (not just proportional)."""
    vals = set(belief.values())
    assert len(vals) == 1, "harness encoder requires uniform-over-support belief"
    w = [0] * S
    for s in belief:
        w[idx_of(s)] = 1
    return w


def write_inputs(secrets, beliefs):
    os.makedirs(f"{MPSPDZ}/Player-Data", exist_ok=True)
    for j in range(N):
        with open(f"{MPSPDZ}/Player-Data/Input-P{j}-0", "w") as f:
            f.write(f"{secrets[j]}\n")
            for wv in dense_weights(beliefs[j]):
                f.write(f"{wv}\n")


def run_circuit(query):
    subprocess.run(["cp", f"{HERE}/mpc/threshold_smc.mpc",
                    f"{MPSPDZ}/Programs/Source/"], check=True)
    subprocess.run(["./compile.py", "-R", "64", "threshold_smc", query],
                   cwd=MPSPDZ, check=True, capture_output=True)
    r = subprocess.run(["Scripts/ring.sh", f"threshold_smc-{query}"],
                       cwd=MPSPDZ, capture_output=True, text=True)
    return r.stdout


def parse(out):
    acc, pay = {}, {}
    W = {j: [0] * S for j in range(N)}
    for line in out.splitlines():
        t = line.split()
        if len(t) >= 3 and t[0] == "ACCEPT":
            acc[int(t[1])] = int(t[2])
        elif len(t) >= 3 and t[0] == "PAYLOAD":
            pay[int(t[1])] = int(t[2])
        elif len(t) >= 4 and t[0] == "W":
            W[int(t[1])][int(t[2])] = int(t[3])
    return acc, pay, W


def check_invocation(model, query, label):
    secrets = model.secrets
    write_inputs(secrets, model.beliefs)
    out = run_circuit(query)
    acc, pay, W = parse(out)

    qfn = QUERIES[query]
    o_actual = qfn(secrets)
    visible = model.invoke(qfn)                      # advances oracle state
    exp_acc = [0 if v == REJECT else 1 for v in visible]
    exp_pay = [o_actual if v != REJECT else 0 for v in visible]
    exp_W = [dense_weights(model.beliefs[j]) for j in range(N)]

    msgs = []
    for j in range(N):
        if acc.get(j) != exp_acc[j]:
            msgs.append(f"accept[{j}]: circuit {acc.get(j)} != oracle {exp_acc[j]}")
        if pay.get(j) != exp_pay[j]:
            msgs.append(f"payload[{j}]: circuit {pay.get(j)} != oracle {exp_pay[j]}")
        if W[j] != exp_W[j]:
            msgs.append(f"weights[{j}]: mismatch (support "
                        f"{[i for i,x in enumerate(W[j]) if x]} vs "
                        f"{[i for i,x in enumerate(exp_W[j]) if x]})")
    ok = not msgs
    print(f"[{label}] query={query} secrets={secrets} "
          f"circuit_accept={[acc.get(j) for j in range(N)]} "
          f"payload={[pay.get(j) for j in range(N)]} -> {'PASS' if ok else 'FAIL'}")
    for m in msgs:
        print("    ", m)
    return ok


def main():
    results = []
    # Pinned fixture, secrets (0,0,1), two invocations
    m = SmcBeliefTracking(D, (0, 0, 1), [HALF] * 3)
    results.append(check_invocation(m, "sum_even", "fixture-inv1"))
    results.append(check_invocation(m, "p1_is_max", "fixture-inv2"))
    # Additional valid state, secrets (1,0,2)
    m2 = SmcBeliefTracking(D, (1, 0, 2), [HALF] * 3)
    results.append(check_invocation(m2, "p1_is_max", "extra-state"))
    # Additional valid state exercising the reject mask: o_actual=1 with
    # divergence -> party 0 payload 1 (accept), parties 1,2 payload 0 (masked).
    m3 = SmcBeliefTracking(D, (2, 0, 0), [HALF] * 3)
    results.append(check_invocation(m3, "p1_is_max", "extra-mask"))

    print("=" * 60)
    print("ALL PASS" if all(results) else "SOME FAILED")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
