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


# ---- finalized evidence record (round-5c) ----

def test_run_and_check_writes_finalized_record(monkeypatch, tmp_path):
    ev = tmp_path / "e.jsonl"
    monkeypatch.setattr(mpc_run, "EVIDENCE", str(ev))
    monkeypatch.setattr(mpc_run, "write_inputs", lambda s, w: "ihash")
    monkeypatch.setattr(mpc_run, "mpspdz_sha", lambda: "MPSHA")
    monkeypatch.setattr(mpc_run, "repo_provenance", lambda: ("REPOSHA", "github_actions", True))
    def fake_run_circuit(query, case_id="", input_hash=""):
        mpc_run.LAST_TRANSCRIPT = {
            "compile_rc": 0, "compile_stdout": "c", "compile_stderr": "",
            "ring_rc": 0, "ring_stdout": valid_output(), "ring_stderr": "",
        }
        return valid_output()
    monkeypatch.setattr(mpc_run, "run_circuit", fake_run_circuit)
    monkeypatch.setattr(mpc_run, "compare", lambda *a, **k: [])   # force comparison ok

    ok, msgs, acc, pay, Wl = mpc_run.run_and_check((0, 0, 1), None, "sum_even", "c1")
    assert ok and msgs == []
    import json
    rec = json.loads(ev.read_text().splitlines()[0])
    assert rec["parse_ok"] is True and rec["comparison_ok"] is True
    assert rec["final"] == "PASS" and rec["bound"] is True
    assert rec["repo_sha"] == "REPOSHA" and rec["mpspdz_sha"] == "MPSHA"
    for k in ("ring_stdout", "input_hash", "case_id", "query"):
        assert k in rec


def test_run_and_check_records_failure(monkeypatch, tmp_path):
    ev = tmp_path / "e.jsonl"
    monkeypatch.setattr(mpc_run, "EVIDENCE", str(ev))
    monkeypatch.setattr(mpc_run, "write_inputs", lambda s, w: "ihash")
    monkeypatch.setattr(mpc_run, "mpspdz_sha", lambda: "MPSHA")
    monkeypatch.setattr(mpc_run, "repo_provenance", lambda: (None, "unbound", False))
    def fake_run_circuit(query, case_id="", input_hash=""):
        mpc_run.LAST_TRANSCRIPT = {
            "compile_rc": 0, "compile_stdout": "", "compile_stderr": "",
            "ring_rc": 0, "ring_stdout": "W 0 0 0", "ring_stderr": "",  # incomplete
        }
        return "W 0 0 0"
    monkeypatch.setattr(mpc_run, "run_circuit", fake_run_circuit)
    with pytest.raises(ValueError):
        mpc_run.run_and_check((0, 0, 1), None, "sum_even", "bad")
    import json
    rec = json.loads(ev.read_text().splitlines()[0])
    assert rec["final"] == "FAIL" and rec["parse_ok"] is False and rec["error"]


# ---- evidence validator ----

_HEX = "a" * 64


def _rec(cid="c0", **kw):
    base = dict(repo_sha="R", repo_sha_source="github_actions", bound=True,
                mpspdz_sha="M", query="sum_even", case_id=cid, input_hash=_HEX,
                compile_rc=0, compile_stdout="", compile_stderr="",
                ring_rc=0, ring_stdout="x", ring_stderr="",
                parse_ok=True, comparison_ok=True, mismatches=[], error=None,
                final="PASS")
    base.update(kw)
    return base


def _write(tmp_path, recs, name="e.jsonl"):
    import json
    p = tmp_path / name
    p.write_text("\n".join(json.dumps(r) for r in recs))
    return str(p)


def test_validator_accepts_good(tmp_path):
    import validate_evidence as V
    p = _write(tmp_path, [_rec("c0"), _rec("c1")])          # unique, complete
    assert V.validate(p, 2, repo="R", mpspdz="M", require_bound=True) == []


# the four bypasses the reviewer forced through the old validator

def test_validator_rejects_contradictory_pass(tmp_path):
    import validate_evidence as V
    p = _write(tmp_path, [_rec(final="PASS", parse_ok=False, comparison_ok=False)])
    errs = V.validate(p, 1)
    assert any("parse_ok" in e for e in errs)


def test_validator_rejects_duplicate_case_id(tmp_path):
    import validate_evidence as V
    p = _write(tmp_path, [_rec("dup"), _rec("dup")])
    assert any("duplicate case_id" in e for e in V.validate(p, 2))


def test_validator_rejects_missing_fields(tmp_path):
    import validate_evidence as V
    r = _rec()
    for k in ("compile_rc", "compile_stdout", "ring_stderr", "mismatches", "error"):
        r.pop(k, None)
    p = _write(tmp_path, [r])
    errs = V.validate(p, 1)
    assert any("missing field" in e for e in errs)


def test_validator_rejects_bound_true_unbound_source(tmp_path):
    import validate_evidence as V
    p = _write(tmp_path, [_rec(bound=True, repo_sha_source="unbound")])
    assert any("source=" in e for e in V.validate(p, 1, require_bound=True))


def test_validator_rejects_bad_input_hash(tmp_path):
    import validate_evidence as V
    p = _write(tmp_path, [_rec(input_hash="short")])
    assert any("input_hash" in e for e in V.validate(p, 1))


def test_validator_rejects_wrong_count(tmp_path):
    import validate_evidence as V
    p = _write(tmp_path, [_rec()])
    assert any("expected 2" in e for e in V.validate(p, 2))


def test_validator_rejects_unbound_when_required(tmp_path):
    import validate_evidence as V
    p = _write(tmp_path, [_rec(bound=False, repo_sha=None, repo_sha_source="unbound")])
    assert any("unbound" in e for e in V.validate(p, 1, require_bound=True))


def test_validator_rejects_wrong_repo_sha(tmp_path):
    import validate_evidence as V
    p = _write(tmp_path, [_rec(repo_sha="OTHER")])
    assert any("repo_sha" in e for e in V.validate(p, 1, repo="R"))


def test_validator_rejects_missing_file(tmp_path):
    import validate_evidence as V
    assert any("missing" in e for e in V.validate(str(tmp_path / "nope.jsonl"), 1))


def test_validator_rejects_non_pass_final(tmp_path):
    import validate_evidence as V
    p = _write(tmp_path, [_rec(final="FAIL")])
    assert any("final=" in e for e in V.validate(p, 1))


def test_run_and_check_retains_comparison_exception(monkeypatch, tmp_path):
    """A comparison/oracle exception must still produce one complete FAIL record."""
    ev = tmp_path / "e.jsonl"
    monkeypatch.setattr(mpc_run, "EVIDENCE", str(ev))
    monkeypatch.setattr(mpc_run, "write_inputs", lambda s, w: "a" * 64)
    monkeypatch.setattr(mpc_run, "mpspdz_sha", lambda: "M")
    monkeypatch.setattr(mpc_run, "repo_provenance", lambda: ("R", "github_actions", True))
    def frc(q, case_id="", input_hash=""):
        mpc_run.LAST_TRANSCRIPT = {
            "compile_rc": 0, "compile_stdout": "", "compile_stderr": "",
            "ring_rc": 0, "ring_stdout": valid_output(), "ring_stderr": "",
        }
        return valid_output()
    monkeypatch.setattr(mpc_run, "run_circuit", frc)
    def boom(*a, **k):
        raise RuntimeError("compare boom")
    monkeypatch.setattr(mpc_run, "compare", boom)
    with pytest.raises(RuntimeError, match="compare boom"):
        mpc_run.run_and_check((0, 0, 1), None, "sum_even", "cx")
    import json
    rec = json.loads(ev.read_text().splitlines()[0])
    assert rec["final"] == "FAIL" and rec["parse_ok"] is True
    assert "compare boom" in rec["error"]
