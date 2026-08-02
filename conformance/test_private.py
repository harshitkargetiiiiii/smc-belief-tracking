"""
Unit tests for the private-delivery leakage checker (staged gate 2).

No MP-SPDZ: these test the leakage-evaluation logic on synthetic per-party
streams, including a NEGATIVE CONTROL proving the checker DETECTS a broadcast
leak (so a passing check is not vacuous). The end-to-end MPC run is exercised by
private_run.py in CI.
"""
from private_run import parse_party, evaluate_privacy, N


def _stream(records):
    return "\n".join(f"PRIV {j} {kind} {v}" for (j, kind, v) in records)


def test_parse_party():
    got = parse_party("noise\nPRIV 1 ACCEPT 0\nPRIV 1 PAYLOAD 0\nTime = 1")
    assert got == {"ACCEPT": {1: 0}, "PAYLOAD": {1: 0}}


def test_private_delivery_clean_passes():
    # each party sees only its own verdict
    outs = {
        0: _stream([(0, "ACCEPT", 1), (0, "PAYLOAD", 1)]),
        1: _stream([(1, "ACCEPT", 0), (1, "PAYLOAD", 0)]),
        2: _stream([(2, "ACCEPT", 0), (2, "PAYLOAD", 0)]),
    }
    assert evaluate_privacy(outs, [1, 0, 0], [1, 0, 0]) == []


def test_leak_detected_when_party_sees_others():
    # NEGATIVE CONTROL: party 0's stream contains everyone's verdicts (broadcast).
    # The checker must flag it, or a passing private test would be meaningless.
    broadcast = _stream([(0, "ACCEPT", 1), (0, "PAYLOAD", 1),
                         (1, "ACCEPT", 0), (1, "PAYLOAD", 0),
                         (2, "ACCEPT", 0), (2, "PAYLOAD", 0)])
    outs = {0: broadcast, 1: "", 2: ""}
    msgs = evaluate_privacy(outs, [1, 0, 0], [1, 0, 0])
    assert any("LEAK" in m for m in msgs)
    # and the parties that received nothing are also flagged (own verdict missing)
    assert any("party 1 own ACCEPT" in m for m in msgs)


def test_wrong_own_verdict_detected():
    outs = {
        0: _stream([(0, "ACCEPT", 0), (0, "PAYLOAD", 0)]),   # should be 1,1
        1: _stream([(1, "ACCEPT", 0), (1, "PAYLOAD", 0)]),
        2: _stream([(2, "ACCEPT", 0), (2, "PAYLOAD", 0)]),
    }
    msgs = evaluate_privacy(outs, [1, 0, 0], [1, 0, 0])
    assert any("party 0 own ACCEPT" in m for m in msgs)


def test_missing_own_verdict_detected():
    outs = {0: "", 1: "", 2: ""}
    msgs = evaluate_privacy(outs, [1, 0, 0], [1, 0, 0])
    assert len(msgs) >= N            # every party missing its own verdict
