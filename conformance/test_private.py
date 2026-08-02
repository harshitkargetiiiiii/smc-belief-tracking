"""
Unit tests for gate 2 (private delivery), no MP-SPDZ:
- strict per-party transcript parser (exact two non-empty stdout lines) + the
  reviewer's adversarial mutations;
- the CONTENT-based manifest inspector: accepts the private shape, rejects a
  name-spoofed subtape, a digit-named content leak, a public open anywhere, and a
  main-tape sink (the executable negative control's core logic, synthetic);
- the typed private-evidence validator: rejects forged records, replayed
  duplicates, and verdict values that disagree with the oracle.
The real end-to-end run + real compiled-delivery gate execute in CI.
"""
import pytest

from private_run import strict_parse_party, evaluate_privacy, N, CHANNEL_ASSUMPTION
import delivery_inspect as DI


# ---- strict per-party parser (EXACT two-line stdout) ----

def _own(j, acc, pay):
    # real replicated-ring-party.x stdout is exactly the two print_ln_to lines;
    # all framework diagnostics go to stderr (verified live).
    return f"PRIV {j} ACCEPT {acc}\nPRIV {j} PAYLOAD {pay}\n"


def test_clean_own_stream_parses():
    assert strict_parse_party(_own(0, 1, 1), 0) == {"ACCEPT": 1, "PAYLOAD": 1}


def test_foreign_verdict_raises():
    txt = _own(0, 1, 1) + "PRIV 1 ACCEPT 0"
    with pytest.raises(ValueError, match="foreign verdict"):
        strict_parse_party(txt, 0)


def test_duplicate_own_raises():
    txt = "PRIV 0 ACCEPT 9\nPRIV 0 ACCEPT 1\nPRIV 0 PAYLOAD 1"
    with pytest.raises(ValueError, match="duplicate ACCEPT"):
        strict_parse_party(txt, 0)


def test_unrecognized_stdout_line_raises():
    txt = "PRIV 0 ACCEPT 1\nLEAK 1 ACCEPT 0\nPRIV 0 PAYLOAD 1"
    with pytest.raises(ValueError, match="unrecognized"):
        strict_parse_party(txt, 0)


def test_out_of_range_id_raises():
    txt = "PRIV 9 ACCEPT 0\nPRIV 0 PAYLOAD 1"
    with pytest.raises(ValueError, match="foreign verdict"):
        strict_parse_party(txt, 0)


def test_missing_own_record_raises():
    with pytest.raises(ValueError, match="expected exactly one ACCEPT"):
        strict_parse_party("PRIV 0 ACCEPT 1", 0)     # no PAYLOAD


def test_empty_stream_raises():
    with pytest.raises(ValueError, match="expected exactly one ACCEPT"):
        strict_parse_party("", 0)


def test_extra_framework_line_now_rejected():
    txt = "PRIV 0 ACCEPT 1\nPRIV 0 PAYLOAD 1\nTime = 1"
    with pytest.raises(ValueError, match="unrecognized"):
        strict_parse_party(txt, 0)


def test_public_leak_line_rejected():
    txt = "PRIV 0 ACCEPT 0\nPRIV 0 PAYLOAD 0\nLEAK 1"
    with pytest.raises(ValueError, match="unrecognized"):
        strict_parse_party(txt, 0)


def test_reviewer_exact_attack_is_rejected():
    txt = "PRIV 0 ACCEPT 9\nPRIV 0 PAYLOAD 9\nLEAK PAYLOAD 1 0\nPRIV 0 ACCEPT 1\nPRIV 0 PAYLOAD 1"
    with pytest.raises(ValueError):
        strict_parse_party(txt, 0)


def test_evaluate_privacy_flags_broadcast():
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


# ---- single-tape classifier (synthetic assembly) ----

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


# ---- CONTENT-based complete-manifest inspector (synthetic manifests) ----
# masked comparison subtapes: compiler-generated digit names + `False` opens only.

GOOD_MASKED = {"0": PRIV_ASM,
               "EQZ(3)_63-1": "vasm_open 3, 3, False, c0, s0",
               "LTZ(36)_64-2": "vasm_open 3, 3, False, c1, s1"}


def test_manifest_accepts_private_with_masked_subtapes():
    ok, reasons = DI.is_private_manifest(GOOD_MASKED)
    assert ok and reasons == []


def test_manifest_rejects_name_spoof_tape():
    # non-digit name spoof: EQZ(spoof) with wrong-player privateoutput + file sink
    m = dict(GOOD_MASKED)
    m["EQZ(spoof)-1"] = "privateoutput 4, 1, 0, c0, s0\nintoutput 0, ci0"
    ok, reasons = DI.is_private_manifest(m)
    assert not ok
    assert any("author-introduced" in r for r in reasons)
    assert any("privateoutput in non-main" in r for r in reasons)


def test_manifest_rejects_digit_named_content_leak():
    # NAME matches the strict masked pattern, but CONTENT leaks -> still rejected
    m = dict(GOOD_MASKED)
    m["EQZ(9)_99-1"] = "privateoutput 4, 1, 0, c0, s0\nintoutput 0, ci0"
    ok, reasons = DI.is_private_manifest(m)
    assert not ok
    assert any("privateoutput in non-main" in r for r in reasons)
    assert any("output/exfil" in r for r in reasons)


def test_manifest_rejects_public_open_anywhere():
    m = dict(GOOD_MASKED)
    m["EQZ(3)_63-1"] = "asm_open 3, True, c0, s0"     # public reveal (True) in a masked tape
    ok, reasons = DI.is_private_manifest(m)
    assert not ok
    assert any("public open-to-all" in r for r in reasons)


def test_manifest_rejects_main_tape_sink():
    m = {"0": PRIV_ASM + "\nintoutput 0, ci0",
         "EQZ(3)_63-1": "vasm_open 3, 3, False, c0, s0"}
    ok, reasons = DI.is_private_manifest(m)
    assert not ok
    assert any("non-delivery output" in r for r in reasons)


def test_manifest_rejects_wrong_main_players():
    m = {"0": "privateoutput 8, 1, 0, c1, s1, 1, 0, c2, s2 # x"}
    ok, reasons = DI.is_private_manifest(m)
    assert not ok
    assert any("players" in r for r in reasons)


def test_manifest_signature_detects_injected_sink():
    # the old 4-pattern hash collided on a sink injected into an existing tape
    leaked = dict(GOOD_MASKED)
    leaked["EQZ(3)_63-1"] = "vasm_open 3, 3, False, c0, s0\nintoutput 0, ci0"
    assert DI.manifest_signature(GOOD_MASKED) != DI.manifest_signature(leaked)


# ---- typed private evidence validator ----

def _phex(c="a"):
    return c * 64


def _priv_rec(cid="p0", query="sum_even", **kw):
    base = dict(repo_sha="R", repo_sha_source="github_actions", bound=True,
                mpspdz_sha="M", query=query, case_id=cid, input_hash=_phex(),
                source_sha256=_phex(), delivery_sig=_phex(),
                delivery_private_ok=True, tls_certs_present=True,
                channel_assumption=CHANNEL_ASSUMPTION, privacy_ok=True,
                mismatches=[], error=None, final="PASS")
    for j in range(3):
        base[f"party{j}_rc"] = 0
        base[f"party{j}_stdout"] = f"PRIV {j} ACCEPT 0\nPRIV {j} PAYLOAD 0\n"
        base[f"party{j}_stderr"] = ""
        base[f"party{j}_cmd"] = (f"/p/replicated-ring-party.x {j} "
                                 f"threshold_smc_private-{query} -pn 1 -h localhost -OF .")
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


def test_private_validator_rejects_unknown_field(tmp_path):
    import validate_evidence as V
    p = _wp(tmp_path, [_priv_rec(sneaky="x")])
    assert any("unexpected field sneaky" in e for e in V.validate_private(p, 1))


def test_private_validator_rejects_bool_rc(tmp_path):
    import validate_evidence as V
    p = _wp(tmp_path, [_priv_rec(party0_rc=True)])
    assert any("party0_rc wrong type (bool)" in e for e in V.validate_private(p, 1))


def test_private_validator_rejects_forged_stdout(tmp_path):
    import validate_evidence as V
    p = _wp(tmp_path, [_priv_rec(party0_stdout="LEAK 5\n")])
    assert any("party0_stdout not strict own delivery" in e
               for e in V.validate_private(p, 1))


def test_private_validator_rejects_public_leak_line_in_stdout(tmp_path):
    import validate_evidence as V
    leaked = "PRIV 0 ACCEPT 0\nPRIV 0 PAYLOAD 0\nLEAK 1\n"
    p = _wp(tmp_path, [_priv_rec(party0_stdout=leaked)])
    assert any("party0_stdout not strict own delivery" in e
               for e in V.validate_private(p, 1))


def test_private_validator_rejects_bad_cmd(tmp_path):
    import validate_evidence as V
    p = _wp(tmp_path, [_priv_rec(party0_cmd="x")])
    assert any("party0_cmd not the private ring command" in e
               for e in V.validate_private(p, 1))


def test_private_validator_rejects_bad_channel(tmp_path):
    import validate_evidence as V
    p = _wp(tmp_path, [_priv_rec(channel_assumption="tls")])
    assert any("channel_assumption" in e for e in V.validate_private(p, 1))


def test_private_validator_rejects_forged_source_binding(tmp_path):
    import validate_evidence as V
    p = _wp(tmp_path, [_priv_rec(source_sha256=_phex("a"))])
    errs = V.validate_private(p, 1, expected_source_sha256=_phex("b"),
                              expected_delivery_sigs={"sum_even": _phex("a")})
    assert any("source_sha256 != recomputed" in e for e in errs)


def test_private_validator_rejects_forged_delivery_binding(tmp_path):
    import validate_evidence as V
    p = _wp(tmp_path, [_priv_rec(delivery_sig=_phex("a"))])
    errs = V.validate_private(p, 1, expected_source_sha256=_phex("a"),
                              expected_delivery_sigs={"sum_even": _phex("b")})
    assert any("delivery_sig != recomputed" in e for e in errs)


def test_private_validator_accepts_matching_bindings(tmp_path):
    import validate_evidence as V
    p = _wp(tmp_path, [_priv_rec(source_sha256=_phex("a"), delivery_sig=_phex("c"))])
    errs = V.validate_private(p, 1, repo="R", mpspdz="M", require_bound=True,
                              expected_source_sha256=_phex("a"),
                              expected_delivery_sigs={"sum_even": _phex("c")})
    assert errs == []


# ---- canonical case-table binding (re-review-3 C1/C2/C3) ----

def test_case_table_accepts_matching(tmp_path):
    import validate_evidence as V
    tab = {_phex("a"): ("sum_even", [0, 0, 0], [0, 0, 0])}
    p = _wp(tmp_path, [_priv_rec(input_hash=_phex("a"))])
    assert V.validate_private(p, 1, expected_case_table=tab) == []


def test_case_table_rejects_replay(tmp_path):
    import validate_evidence as V
    tab = {_phex("a"): ("sum_even", [0, 0, 0], [0, 0, 0]),
           _phex("b"): ("sum_even", [0, 0, 0], [0, 0, 0])}
    p = _wp(tmp_path, [_priv_rec("c0", input_hash=_phex("a")),
                       _priv_rec("c1", input_hash=_phex("a"))])
    errs = V.validate_private(p, 2, expected_case_table=tab)
    assert any("replayed canonical case" in e for e in errs)


def test_case_table_rejects_forged_value(tmp_path):
    import validate_evidence as V
    tab = {_phex("a"): ("sum_even", [0, 0, 0], [0, 0, 0])}
    r = _priv_rec(input_hash=_phex("a"),
                  party0_stdout="PRIV 0 ACCEPT 1\nPRIV 0 PAYLOAD 0\n")
    errs = V.validate_private(_wp(tmp_path, [r]), 1, expected_case_table=tab)
    assert any("!= oracle" in e for e in errs)


def test_case_table_rejects_unbound_hash(tmp_path):
    import validate_evidence as V
    tab = {_phex("a"): ("sum_even", [0, 0, 0], [0, 0, 0])}
    p = _wp(tmp_path, [_priv_rec(input_hash=_phex("f"))])
    errs = V.validate_private(p, 1, expected_case_table=tab)
    assert any("not a canonical case" in e for e in errs)


def test_case_table_requires_full_coverage(tmp_path):
    import validate_evidence as V
    tab = {_phex("a"): ("sum_even", [0, 0, 0], [0, 0, 0]),
           _phex("b"): ("sum_even", [0, 0, 0], [0, 0, 0])}
    p = _wp(tmp_path, [_priv_rec(input_hash=_phex("a"))])
    errs = V.validate_private(p, 1, expected_case_table=tab)
    assert any("does not cover the canonical case set" in e for e in errs)
