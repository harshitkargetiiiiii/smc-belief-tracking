"""
Regression tests for the strict runner/parser (round-5 re-review, issue #4).
No MP-SPDZ needed: parse_strict is tested on synthetic output, run_circuit's
fail-closed behavior via a fake subprocess, and pipefail propagation directly.
"""
import subprocess

import pytest

import mpc_run
from mpc_run import parse_strict, N, S


def valid_output(acc=(1, 1, 1), pay=(0, 0, 0), weights=None):
    lines = [f"ACCEPT {j} {acc[j]}" for j in range(N)]
    lines += [f"PAYLOAD {j} {pay[j]}" for j in range(N)]
    for j in range(N):
        for idx in range(S):
            w = 0 if weights is None else weights[j][idx]
            lines.append(f"W {j} {idx} {w}")
    return "\n".join(lines)


def test_valid_output_parses():
    acc, pay, Wl = parse_strict(valid_output())
    assert acc == {0: 1, 1: 1, 2: 1}
    assert len(Wl) == N and all(len(w) == S for w in Wl)


def test_framework_noise_is_ignored():
    out = "Trying to run 64-bit computation\n" + valid_output() + "\nTime = 0.01 seconds"
    parse_strict(out)                                   # must not raise


def test_missing_row_raises():
    lines = valid_output().splitlines()
    lines = [l for l in lines if l != "W 1 5 0"]        # delete one row
    with pytest.raises(ValueError, match="missing W 1 5"):
        parse_strict("\n".join(lines))


def test_deleting_all_zero_rows_raises():
    # the exact reviewer attack: drop every zero-valued W row
    lines = [l for l in valid_output().splitlines()
             if not (l.startswith("W ") and l.endswith(" 0"))]
    with pytest.raises(ValueError, match="missing W"):
        parse_strict("\n".join(lines))


def test_duplicate_row_raises():
    with pytest.raises(ValueError, match="duplicate W 0 0"):
        parse_strict(valid_output() + "\nW 0 0 0")


def test_out_of_range_index_raises():
    with pytest.raises(ValueError, match="out of range"):
        parse_strict(valid_output() + "\nW 0 27 1")


def test_out_of_range_party_raises():
    with pytest.raises(ValueError, match="out of range"):
        parse_strict(valid_output() + "\nACCEPT 3 1")


def test_malformed_record_raises():
    with pytest.raises(ValueError, match="malformed W"):
        parse_strict(valid_output() + "\nW 0 0")


def test_negative_weight_raises():
    lines = valid_output().splitlines()
    lines[6] = "W 0 0 -1"                               # first W row
    with pytest.raises(ValueError, match="negative weight"):
        parse_strict("\n".join(lines))


def test_accept_not_a_bit_raises():
    lines = valid_output().splitlines()
    lines[0] = "ACCEPT 0 2"
    with pytest.raises(ValueError, match="not a bit"):
        parse_strict("\n".join(lines))


# ---- fail-closed runner ----

class _R:
    def __init__(self, rc, out="", err=""):
        self.returncode, self.stdout, self.stderr = rc, out, err


def test_run_circuit_fails_closed_on_ring_nonzero(monkeypatch):
    def fake_run(cmd, **kw):
        if cmd[0] == "cp":
            return _R(0)
        if cmd[0] == "./compile.py":
            return _R(0, "compiled ok")
        if cmd[0] == "Scripts/ring.sh":
            return _R(73, "partial stdout", "ring boom")   # non-zero
        if cmd[:2] == ["git", "rev-parse"]:
            return _R(0, "deadbeef")
        return _R(0)
    monkeypatch.setattr(mpc_run.subprocess, "run", fake_run)
    monkeypatch.setattr(mpc_run, "_compiled", set())
    with pytest.raises(RuntimeError, match=r"ring\.sh failed \(73\)"):
        mpc_run.run_circuit("p1_is_max")


def test_run_circuit_fails_closed_on_compile_nonzero(monkeypatch):
    def fake_run(cmd, **kw):
        if cmd[0] == "cp":
            return _R(0)
        if cmd[0] == "./compile.py":
            return _R(2, "", "compile boom")
        if cmd[:2] == ["git", "rev-parse"]:
            return _R(0, "deadbeef")
        return _R(0)
    monkeypatch.setattr(mpc_run.subprocess, "run", fake_run)
    monkeypatch.setattr(mpc_run, "_compiled", set())
    with pytest.raises(RuntimeError, match=r"compile failed \(2\)"):
        mpc_run.run_circuit("sum_even")


# ---- the CI false-green mechanism, pinned ----

def test_pipefail_propagates_nonzero():
    """Documents the CI fix: with pipefail a failing left side of `| tee` makes
    the pipeline non-zero; without it, the pipeline takes tee's zero status."""
    with_pf = subprocess.run(
        ["bash", "-c", "set -o pipefail; (exit 73) | tee /dev/null"]).returncode
    without_pf = subprocess.run(
        ["bash", "-c", "(exit 73) | tee /dev/null"]).returncode
    assert with_pf != 0            # gate fails closed under pipefail
    assert without_pf == 0         # the false-green the CI job must avoid
