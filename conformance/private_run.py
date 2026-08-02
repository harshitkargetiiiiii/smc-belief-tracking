"""
Private-delivery runner + non-recipient-leakage checks (staged gate 2).

Launches the three parties of the PRIVATE build with per-player output enabled
(-OF .), capturing EACH party's stdout separately. Then asserts that party j's
cleartext output contains only its own (accept_j, payload_j) and NO other party's
verdict, and that the debug/broadcast channel semantics are not used here.

This demonstrates private delivery FUNCTIONALLY (the cleartext verdict reaches
only the intended party's process). It is NOT a simulation-security proof; see
ADVERSARY.md. The functional conformance suite (debug build) is unchanged.
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mpc_run import MPSPDZ, HERE, N, write_inputs, oracle_expect, mpspdz_sha

PORT = int(os.environ.get("PRIV_PORT", "15577"))
_compiled = set()
PRIV = re.compile(r"^PRIV (\d) (ACCEPT|PAYLOAD) (-?\d+)$")


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
    """Run all 3 parties, return {party: stdout_text}. Fail closed on any
    non-zero exit."""
    port = port or PORT
    write_inputs(secrets, weight_vectors)
    _compile(query)
    prog = f"threshold_smc_private-{query}"
    procs, outs = [], {}
    for i in range(N):
        p = subprocess.Popen(
            [f"{MPSPDZ}/replicated-ring-party.x", str(i), prog,
             "-pn", str(port), "-h", "localhost", "-OF", "."],
            cwd=MPSPDZ, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        procs.append(p)
    for i, p in enumerate(procs):
        out, err = p.communicate(timeout=120)
        outs[i] = out
        if p.returncode != 0:
            raise RuntimeError(f"party {i} failed ({p.returncode}):\n{err}\n{out}")
    return outs


def parse_party(text):
    """Return {'ACCEPT': {j: v}, 'PAYLOAD': {j: v}} of PRIV records in one
    party's stdout. Records for a party index other than this stream are a leak."""
    got = {"ACCEPT": {}, "PAYLOAD": {}}
    for line in text.splitlines():
        m = PRIV.match(line.strip())
        if m:
            j, kind, val = int(m.group(1)), m.group(2), int(m.group(3))
            got[kind][j] = val
    return got


def evaluate_privacy(outs, exp_acc, exp_pay):
    """Pure check (no MPC): each party learns exactly its own verdict and
    NOTHING about any other party. Returns a list of mismatch/leak messages.
    Factored out so the leakage logic is unit-testable with synthetic streams."""
    msgs = []
    for j in range(N):
        got = parse_party(outs[j])
        if got["ACCEPT"].get(j) != exp_acc[j]:
            msgs.append(f"party {j} own ACCEPT {got['ACCEPT'].get(j)} != {exp_acc[j]}")
        if got["PAYLOAD"].get(j) != exp_pay[j]:
            msgs.append(f"party {j} own PAYLOAD {got['PAYLOAD'].get(j)} != {exp_pay[j]}")
        leaked = [k for k in range(N) if k != j
                  and (k in got["ACCEPT"] or k in got["PAYLOAD"])]
        if leaked:
            msgs.append(f"party {j} LEAK: learned verdicts of {leaked}")
    return msgs


def check_private(secrets, weight_vectors, query):
    """Assert per-recipient privacy against the oracle. Returns (ok, messages)."""
    exp_acc, exp_pay, _, _ = oracle_expect(secrets, weight_vectors, query)
    outs = run_private(secrets, weight_vectors, query)
    msgs = evaluate_privacy(outs, exp_acc, exp_pay)
    return (not msgs), msgs


if __name__ == "__main__":
    print(f"MP-SPDZ commit under test: {mpspdz_sha()}")

    def support_weights(secrets):
        from mpc_run import S, state
        out = []
        for j in range(N):
            w = [1 if state(idx)[j] == secrets[j] else 0 for idx in range(S)]
            out.append(w)
        return out

    cases = [((0, 0, 1), "sum_even"), ((0, 0, 1), "p1_is_max"),
             ((2, 0, 0), "p1_is_max"), ((1, 2, 0), "sum_even")]
    allok = True
    for secrets, q in cases:
        ok, msgs = check_private(secrets, support_weights(secrets), q)
        print(f"[private] secrets={secrets} q={q} -> {'PASS' if ok else 'FAIL'}")
        for m in msgs:
            print("    ", m)
        allok = allok and ok
    print("=" * 56)
    print("PRIVATE DELIVERY OK" if allok else "PRIVATE DELIVERY FAILED")
    sys.exit(0 if allok else 1)
