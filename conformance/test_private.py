"""
Unit tests for gate 2 (private delivery), no MP-SPDZ:
- strict per-party transcript parser + the reviewer's adversarial mutations;
- the compiled-delivery classifier distinguishes privateoutput from public open
  (the executable negative control's core logic, on synthetic assembly).
The real end-to-end run + real compiled-delivery gate execute in CI.
"""
import pytest

from private_run import strict_parse_party, evaluate_privacy, N
import delivery_inspect as DI


# ---- strict per-party parser ----

def _own(j, acc, pay):
    return f"noise\nPRIV {j} ACCEPT {acc}\nPRIV {j} PAYLOAD {pay}\nTime = 1"


def test_clean_own_stream_parses():
    assert strict_parse_party(_own(0, 1, 1), 0) == {"ACCEPT": 1, "PAYLOAD": 1}


def test_foreign_verdict_raises():
    txt = _own(0, 1, 1) + "\nPRIV 1 ACCEPT 0"
    with pytest.raises(ValueError, match="foreign verdict"):
        strict_parse_party(txt, 0)


def test_duplicate_own_raises():
    txt = "PRIV 0 ACCEPT 9\nPRIV 0 ACCEPT 1\nPRIV 0 PAYLOAD 1"
    with pytest.raises(ValueError, match="duplicate ACCEPT"):
        strict_parse_party(txt, 0)


def test_unrecognized_verdict_line_raises():
    # the reviewer's "explicitly tagged non-PRIV leak"
    txt = "PRIV 0 ACCEPT 1\nLEAK 1 ACCEPT 0\nPRIV 0 PAYLOAD 1"
    with pytest.raises(ValueError, match="unrecognized"):
        strict_parse_party(txt, 0)


def test_out_of_range_id_raises():
    txt = "PRIV 9 ACCEPT 0\nPRIV 0 PAYLOAD 1"
    with pytest.raises(ValueError, match="foreign verdict"):
        strict_parse_party(txt, 0)


def test_missing_own_record_raises():
    with pytest.raises(ValueError, match="expected one ACCEPT"):
        strict_parse_party("PRIV 0 ACCEPT 1", 0)     # no PAYLOAD


def test_empty_stream_raises():
    with pytest.raises(ValueError, match="expected one ACCEPT"):
        strict_parse_party("Time = 1", 0)


def test_reviewer_exact_attack_is_rejected():
    # wrong duplicate values + tagged non-PRIV leak + expected values last
    txt = "PRIV 0 ACCEPT 9\nPRIV 0 PAYLOAD 9\nLEAK PAYLOAD 1 0\nPRIV 0 ACCEPT 1\nPRIV 0 PAYLOAD 1"
    with pytest.raises(ValueError):
        strict_parse_party(txt, 0)


def test_evaluate_privacy_flags_broadcast():
    # party 0's stream carries everyone's verdicts -> foreign verdict raises
    outs = {
        0: "PRIV 0 ACCEPT 1\nPRIV 0 PAYLOAD 1\nPRIV 1 ACCEPT 0\nPRIV 2 ACCEPT 0",
        1: _own(1, 0, 0),
        2: _own(2, 0, 0),
    }
    msgs = evaluate_privacy(outs, [1, 0, 0], [1, 0, 0])
    assert any("foreign verdict" in m for m in msgs)


def test_evaluate_privacy_clean_passes():
    outs = {0: _own(0, 1, 1), 1: _own(1, 0, 0), 2: _own(2, 0, 0)}
    assert evaluate_privacy(outs, [1, 0, 0], [1, 0, 0]) == []


# ---- compiled-delivery classifier (synthetic assembly) ----

PRIV_ASM = ("some prep\n"
            "privateoutput 24, 1, 0, c5, s5, 1, 0, c3, s4, 1, 1, c4, s3, "
            "1, 1, c0, s2, 1, 2, c2, s1, 1, 2, c1, s0 # 802\n"
            "end")
LEAKY_ASM = ("some prep\n"
             "asm_open 13, True, c5, s0, c3, s1, c4, s2, c0, s3, c2, s4, c1, s5 # 802\n"
             "end")


def test_classifier_accepts_private():
    ok, reasons = DI.is_private_delivery(PRIV_ASM)
    assert ok and reasons == []


def test_classifier_rejects_public_open():
    ok, reasons = DI.is_private_delivery(LEAKY_ASM)
    assert not ok
    assert any("public open" in r for r in reasons)


def test_classifier_rejects_wrong_players():
    bad = "privateoutput 8, 1, 0, c1, s1, 1, 0, c2, s2 # x"   # only player 0
    ok, reasons = DI.is_private_delivery(bad)
    assert not ok
    assert any("players" in r for r in reasons)


def test_delivery_signature_differs():
    assert DI.delivery_signature(PRIV_ASM) != DI.delivery_signature(LEAKY_ASM)


# ---- private evidence validator ----

def _phex(): return "a" * 64


def _priv_rec(cid="p0", **kw):
    base = dict(repo_sha="R", repo_sha_source="github_actions", bound=True,
                mpspdz_sha="M", query="sum_even", case_id=cid, input_hash=_phex(),
                source_sha256=_phex(), delivery_sig=_phex(),
                delivery_private_ok=True, tls_certs_present=True,
                channel_assumption="tls", privacy_ok=True, mismatches=[],
                error=None, final="PASS")
    for j in range(3):
        base[f"party{j}_rc"] = 0
        base[f"party{j}_stdout"] = f"PRIV {j} ACCEPT 0"
        base[f"party{j}_stderr"] = ""
        base[f"party{j}_cmd"] = "x"
    base.update(kw)
    return base


def _wp(tmp_path, recs):
    import json
    p = tmp_path / "p.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in recs))
    return str(p)


def test_private_validator_accepts_good(tmp_path):
    import validate_evidence as V
    p = _wp(tmp_path, [_priv_rec("p0"), _priv_rec("p1")])
    assert V.validate_private(p, 2, repo="R", mpspdz="M", require_bound=True) == []


def test_private_validator_rejects_public_delivery(tmp_path):
    import validate_evidence as V
    p = _wp(tmp_path, [_priv_rec(delivery_private_ok=False)])
    assert any("delivery_private_ok" in e for e in V.validate_private(p, 1))


def test_private_validator_rejects_missing_tls(tmp_path):
    import validate_evidence as V
    p = _wp(tmp_path, [_priv_rec(tls_certs_present=False)])
    assert any("tls_certs_present" in e for e in V.validate_private(p, 1))


def test_private_validator_rejects_nonzero_party_rc(tmp_path):
    import validate_evidence as V
    p = _wp(tmp_path, [_priv_rec(party1_rc=1)])
    assert any("party1_rc" in e for e in V.validate_private(p, 1))
