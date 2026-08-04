#!/usr/bin/env python3
"""
PRE-REGISTERED held-out corpus for the out-of-sample evaluation of the FROZEN
delivery linter conformance/delivery_inspect.py @ 305a3a8.

This file is committed BEFORE the evaluation runs. Every prediction here is made
from static reasoning about the frozen rules (a)-(h); NONE was obtained by running
the linter on these mutants. The single official run (run_heldout.py) fills in the
ACTUAL outcomes into results.json. Per the sprint rules, the checker is NOT
modified after seeing any result, and no mutant is tuned/deleted/replaced after
execution.

Fields per mutant:
  id, category, kind (source|synthetic|provenance),
  title, mechanism,
  genuine_violation:  true | false  (does it violate per-recipient delivery privacy?)
  realizable:         source | synthetic-manifest | source(compile-fail) | provenance
  predicted_compile:  valid | invalid | n/a
  predicted_linter:   PASS | REJECT | n/a        (delivery_inspect verdict)
  predicted_rule:     rule expected to trigger a REJECT (or null)
  oracle_needed:      does classifying the VIOLATION require functional/oracle exec?
  bucket:             reporting bucket (see COUNTING below)
  denominator:        strict | inclusive | none   (delivery_inspect detection-rate membership)
  ref: source_file | transform | prov_eval
  notes
"""

# Oracle classification uses the artifact's own canonical case set plus the S1
# discriminating case. Pre-registered so the value-semantic classification is fixed.
CASES_FOR_ORACLE = [
    ((0, 0, 1), "sum_even"),
    ((0, 0, 1), "p1_is_max"),
    ((2, 0, 0), "p1_is_max"),
    ((1, 2, 0), "sum_even"),
    ((0, 0, 0), "p1_is_max"),
]

CORPUS = [
    # ============================ category 1: recipient/destination ============
    dict(id="H-R1", category="recipient", kind="source",
         title="extra foreign recipient",
         mechanism="honest delivery PLUS one extra reveal_to(1) of party 0's payload",
         genuine_violation=True, realizable="source",
         predicted_compile="valid", predicted_linter="REJECT",
         predicted_rule="(a) main privateoutput player multiset != [0,0,1,1,2,2]",
         oracle_needed=False, bucket="structural_security", denominator="strict",
         ref="mutants/H-R1_recip_extra.mpc",
         notes="Adds a destination -> multiset [0,0,1,1,1,2,2]. Expected caught."),
    dict(id="H-R2", category="recipient", kind="source",
         title="recipient permutation (multiset-preserving)",
         mechanism="deliver party j's verdict to player (j+1)%N; destination multiset unchanged",
         genuine_violation=True, realizable="source",
         predicted_compile="valid", predicted_linter="PASS",
         predicted_rule=None,
         oracle_needed=True, bucket="structural_security", denominator="strict",
         ref="mutants/H-R2_recip_perm.mpc",
         notes="KEY false-accept probe: rule (a) checks the SORTED destination "
               "multiset, not the value->player pairing, so a permutation passes. "
               "Runtime layer (private_run strict parser) is expected to catch the "
               "foreign 'PRIV j' record on player (j+1)'s stream -- recorded separately."),
    dict(id="H-R3", category="recipient", kind="source",
         title="recipient collapse to one player",
         mechanism="deliver all six verdicts to player 0",
         genuine_violation=True, realizable="source",
         predicted_compile="valid", predicted_linter="REJECT",
         predicted_rule="(a) main privateoutput player multiset [0,0,0,0,0,0] != pinned",
         oracle_needed=False, bucket="structural_security", denominator="strict",
         ref="mutants/H-R3_recip_collapse.mpc",
         notes="Player 0 learns every verdict. Expected caught."),

    # ============================ category 2: public/private open ==============
    dict(id="H-O1", category="open", kind="synthetic",
         title="public open (True) inside an existing subtape via register",
         mechanism="append asm_open ...,True of a register-passed value to EQZ(3)_63 (no memory)",
         genuine_violation=True, realizable="synthetic-manifest",
         predicted_compile="n/a", predicted_linter="REJECT",
         predicted_rule="(c) public open-to-all in a tape",
         oracle_needed=False, bucket="structural_security", denominator="inclusive",
         ref="open_true_subtape",
         notes="Distinct from B4 (which used the False flag + memory). Tests (c) in a subtape."),
    dict(id="H-O2", category="open", kind="synthetic",
         title="vectorized public open (True) inside a subtape via register",
         mechanism="append vasm_open ...,True to EQZ(81)_63 (no memory)",
         genuine_violation=True, realizable="synthetic-manifest",
         predicted_compile="n/a", predicted_linter="REJECT",
         predicted_rule="(c) public open-to-all (vectorized) in a tape",
         oracle_needed=False, bucket="structural_security", denominator="inclusive",
         ref="open_true_vec_subtape",
         notes="Tests (c) on the vectorized open form inside a subtape."),
    dict(id="H-O3", category="open", kind="synthetic",
         title="open(False) of a register-passed value inside a masked subtape",
         mechanism="append asm_open ...,False (register operand, no memory, no new tape) to EQZ(3)_63",
         genuine_violation=True, realizable="synthetic-manifest",
         predicted_compile="n/a", predicted_linter="PASS",
         predicted_rule=None,
         oracle_needed=False, bucket="structural_security", denominator="inclusive",
         ref="open_false_callarg",
         notes="ACKNOWLEDGED-GAP probe. (c) needs True; (h) needs memory; (f) multiset "
               "intact -> no rule fires. The checker's own docstring states call_tape/"
               "call_arg cannot be blocklisted. Realizability from SOURCE is NOT "
               "demonstrated (B6: the naive source realization is caught). Predicted false-accept."),

    # ============================ category 3: subtape/topology =================
    dict(id="H-T1", category="topology", kind="synthetic",
         title="benign subtape reordering",
         mechanism="reverse the manifest tape order; same multiset, same bodies",
         genuine_violation=False, realizable="synthetic-manifest",
         predicted_compile="n/a", predicted_linter="PASS",
         predicted_rule=None,
         oracle_needed=False, bucket="benign", denominator="none",
         ref="topo_reorder",
         notes="Correct-accept expected: the linter sorts, so order is irrelevant."),
    dict(id="H-T2", category="topology", kind="synthetic",
         title="extra well-formed masked tape (benign bloat)",
         mechanism="add a pure duplicate EQZ(3)_63 body under a new key",
         genuine_violation=False, realizable="synthetic-manifest",
         predicted_compile="n/a", predicted_linter="REJECT",
         predicted_rule="(f) non-main tape multiset gains EQZ(3)_63",
         oracle_needed=False, bucket="benign", denominator="none",
         ref="topo_extra_masked",
         notes="Over-conservative REJECT of a NON-leaking topology change -- a precision "
               "cost, not a security detection. Reported as a false-reject example."),
    dict(id="H-T3", category="topology", kind="synthetic",
         title="off-pin but pattern-valid subtape name",
         mechanism="rename EQZ(81)_63 -> EQZ(7)_63 (matches (e), not in the pin)",
         genuine_violation=True, realizable="synthetic-manifest",
         predicted_compile="n/a", predicted_linter="REJECT",
         predicted_rule="(f) multiset {EQZ(3)_63,EQZ(7)_63,LTZ(36)_64} != pinned",
         oracle_needed=False, bucket="structural_security", denominator="inclusive",
         ref="topo_valid_name_offpin",
         notes="A renamed subtape could carry a different comparison; (f) pins the exact set."),

    # ============================ category 4: secret-transfer/channel ==========
    dict(id="H-C1", category="channel", kind="synthetic",
         title="indirect memory access inside a subtape",
         mechanism="append ldmsi (indirect load) to LTZ(36)_64",
         genuine_violation=True, realizable="synthetic-manifest",
         predicted_compile="n/a", predicted_linter="REJECT",
         predicted_rule="(h) non-main tape accesses memory",
         oracle_needed=False, bucket="structural_security", denominator="inclusive",
         ref="chan_indirect_mem",
         notes="Held-out memory FORM: B-series used scalar stms/ldms (B3) and vectorized "
               "vstms/vldms (B5); indirect ldmsi/stmsi were never exercised. Tests regex generality."),
    dict(id="H-C2", category="channel", kind="synthetic",
         title="GF2n memory access inside a subtape",
         mechanism="append gldms (gf2n load) to LTZ(36)_64",
         genuine_violation=True, realizable="synthetic-manifest",
         predicted_compile="n/a", predicted_linter="REJECT",
         predicted_rule="(h) non-main tape accesses memory (g? prefix)",
         oracle_needed=False, bucket="structural_security", denominator="inclusive",
         ref="chan_gf2n_mem",
         notes="Held-out memory FORM: the g? prefix was never exercised by the B-series."),
    dict(id="H-C3", category="channel", kind="synthetic",
         title="legitimate call_arg register use (no open)",
         mechanism="append movs (register move of a passed operand, no open/sink/memory)",
         genuine_violation=False, realizable="synthetic-manifest",
         predicted_compile="n/a", predicted_linter="PASS",
         predicted_rule=None,
         oracle_needed=False, bucket="benign", denominator="none",
         ref="chan_callarg_noop",
         notes="Correct-accept expected: the honest build passes operands this way; the "
               "channel per se must not be flagged. Guards against over-blocking."),

    # ============================ category 5: output/value-semantic ============
    dict(id="H-V1", category="value_semantic", kind="source",
         title="negated accept predicate",
         mechanism="accept[j] = (viol != 0) instead of (viol == 0)",
         genuine_violation=True, realizable="source",
         predicted_compile="valid", predicted_linter="PASS",
         predicted_rule=None,
         oracle_needed=True, bucket="semantic_out_of_scope", denominator="none",
         ref="mutants/H-V1_sem_negate_accept.mpc",
         notes="Delivery structure identical -> linter PASS by design; oracle FAIL. The "
               "linter explicitly disclaims value/semantics. Reported separately."),
    dict(id="H-V2", category="value_semantic", kind="source",
         title="swapped accept/payload values",
         mechanism="deliver payload as ACCEPT and accept as PAYLOAD",
         genuine_violation=True, realizable="source",
         predicted_compile="valid", predicted_linter="PASS",
         predicted_rule=None,
         oracle_needed=True, bucket="semantic_out_of_scope", denominator="none",
         ref="mutants/H-V2_sem_swap_acc_pay.mpc",
         notes="Structure intact -> linter PASS; oracle FAIL on a case where accept!=payload."),
    dict(id="H-V3", category="value_semantic", kind="source",
         title="neighbor payload value leak",
         mechanism="party j receives party (j+1)%N's payload VALUE (destination correct)",
         genuine_violation=True, realizable="source",
         predicted_compile="valid", predicted_linter="PASS",
         predicted_rule=None,
         oracle_needed=True, bucket="semantic_out_of_scope", denominator="none",
         ref="mutants/H-V3_sem_neighbor_payload.mpc",
         notes="Genuine cross-party VALUE leak with a correct destination multiset -> "
               "invisible to the delivery linter; oracle FAIL. Reinforces 'delivery "
               "linting != non-leakage'. Reported separately (not a structural detection)."),

    # ============================ category 6: transcript/output-channel ========
    dict(id="H-P1", category="transcript", kind="synthetic",
         title="write-to-file sink in a subtape",
         mechanism="append writesharestofile to EQZ(3)_63",
         genuine_violation=True, realizable="synthetic-manifest",
         predicted_compile="n/a", predicted_linter="REJECT",
         predicted_rule="(d) file/socket/print sink in a tape",
         oracle_needed=False, bucket="structural_security", denominator="inclusive",
         ref="sink_writefile",
         notes="Held-out sink OPCODE: B2 used intoutput (binary_output); writesharestofile "
               "is a different sink token in the (d) allowlist-complement."),
    dict(id="H-P2", category="transcript", kind="synthetic",
         title="write-to-socket (network) sink in a subtape",
         mechanism="append writesocketshare to LTZ(36)_64",
         genuine_violation=True, realizable="synthetic-manifest",
         predicted_compile="n/a", predicted_linter="REJECT",
         predicted_rule="(d) writesocket* sink in a tape",
         oracle_needed=False, bucket="structural_security", denominator="inclusive",
         ref="sink_writesocket",
         notes="Held-out CHANNEL: a network egress sink never exercised by the B-series."),
    dict(id="H-P3", category="transcript", kind="synthetic",
         title="numeric cleartext print in a subtape",
         mechanism="append print_int to EQZ(81)_63",
         genuine_violation=True, realizable="synthetic-manifest",
         predicted_compile="n/a", predicted_linter="REJECT",
         predicted_rule="(d) print_int* sink in a tape",
         oracle_needed=False, bucket="structural_security", denominator="inclusive",
         ref="sink_print_int",
         notes="Held-out placement/opcode: B1 used print_ln in a separate tape; print_int "
               "in a masked subtape is a different token and location."),

    # ============================ category 7: evidence/provenance ==============
    dict(id="H-E1", category="provenance", kind="provenance",
         title="forged delivery signature in an evidence record",
         mechanism="tamper delivery_sig in a valid private-evidence record",
         genuine_violation=True, realizable="provenance",
         predicted_compile="n/a", predicted_linter="n/a",
         predicted_rule="validate_evidence --recompute rejects (recomputed sig != stored)",
         oracle_needed=False, bucket="provenance_other_checker", denominator="none",
         ref="prov_forge_sig",
         notes="OUT OF SCOPE for delivery_inspect (which never reads evidence). Evaluated "
               "against the SEPARATE frozen checker validate_evidence.py @ 305a3a8."),
    dict(id="H-E2", category="provenance", kind="provenance",
         title="evidence replayed under a wrong repo SHA",
         mechanism="validate a valid record with --repo set to a wrong commit",
         genuine_violation=True, realizable="provenance",
         predicted_compile="n/a", predicted_linter="n/a",
         predicted_rule="validate_evidence rejects (record repo_sha != --repo)",
         oracle_needed=False, bucket="provenance_other_checker", denominator="none",
         ref="prov_wrong_repo",
         notes="OUT OF SCOPE for delivery_inspect. Maps the layered-defense boundary."),

    # ============================ compile-invalid bucket =======================
    dict(id="H-X1", category="compile_invalid", kind="source",
         title="direct cross-tape register reference",
         mechanism="a new_tape closes over a MAIN verdict register and reveal(False)s it",
         genuine_violation=True, realizable="source(compile-fail)",
         predicted_compile="invalid", predicted_linter="n/a",
         predicted_rule="MP-SPDZ compiler: 'Register from other tape'",
         oracle_needed=False, bucket="compile_invalid", denominator="none",
         ref="mutants/H-X1_invalid_crosstape_ref.mpc",
         notes="Meaningful: shows the COMPILER (not the linter) blocks the naive direct "
               "channel -- exactly why B3/B5 needed a memory hop. NOT a linter detection."),
    dict(id="H-X2", category="compile_invalid", kind="source",
         title="undefined symbol",
         mechanism="reference an undefined name",
         genuine_violation=False, realizable="source(compile-fail)",
         predicted_compile="invalid", predicted_linter="n/a",
         predicted_rule="MP-SPDZ compiler: NameError",
         oracle_needed=False, bucket="compile_invalid", denominator="none",
         ref="mutants/H-X2_invalid_undefined.mpc",
         notes="Exercises the runner's generic compile-fail bucketing. Not a detection."),
]

# ------------------------------------------------------------------ counting ----
COUNTING = {
    "buckets": {
        "structural_security": "compile-valid mutant that is a genuine gross-DELIVERY-"
            "STRUCTURE / wrong-recipient violation of the kind delivery_inspect targets. "
            "Detection = linter REJECT.",
        "semantic_out_of_scope": "genuine violation that is a VALUE/semantic error with a "
            "correct delivery structure. The linter explicitly disclaims semantics; these "
            "PASS by design and require the oracle to classify. NOT counted against the linter.",
        "benign": "a NON-violating transform (correct-accept expected) or a non-leaking "
            "topology change the linter conservatively rejects (false-reject; precision note).",
        "provenance_other_checker": "targets the provenance layer (validate_evidence.py), "
            "NOT delivery_inspect. Reported separately.",
        "compile_invalid": "does not compile. Recorded separately; NEVER counted as a "
            "linter true-positive.",
    },
    "delivery_denominators": {
        "strict": "structural_security mutants that are SOURCE-realizable & compile-valid. "
            "The scientifically conservative denominator for a delivery_inspect detection rate.",
        "inclusive": "strict PLUS synthetic-manifest structural_security counterexamples "
            "(realizability recorded per-mutant; reported with that caveat).",
    },
    "rules": [
        "A compile failure is NEVER a detector success (bucketed compile_invalid).",
        "semantic_out_of_scope mutants are NOT in any delivery_inspect denominator.",
        "benign mutants are NOT in any security denominator; a benign REJECT is a "
        "false-reject (precision), a benign PASS is a correct-accept.",
        "genuine_violation is judged against the goal of per-recipient private delivery, "
        "independent of whether the linter can see it.",
        "provenance mutants are scored against validate_evidence.py, not delivery_inspect.",
    ],
    "metrics": [
        "per-category table: predicted vs actual linter outcome, per mutant.",
        "strict delivery detection rate = REJECTED / (structural_security & source & compile-valid).",
        "inclusive delivery detection rate = REJECTED / (structural_security & compile-valid), "
        "reported with the synthetic-realizability caveat.",
        "false-accept list (genuine violation, linter PASS).",
        "semantic bucket: linter PASS count + oracle FAIL count (separate).",
        "compile_invalid count; provenance results; benign correct-accepts & false-rejects.",
    ],
}

CHECKER_BASELINE = {
    "commit": "305a3a8d1810c427edcc32520352e74610c7866c",
    "delivery_inspect_blob": "6ef7b6de4593b9a50e3a48e6136681f64423fda5",
    "mpspdz_pin": "9d809599ea6ce627216a389ca7d984fbb75d0cb9",
    "expected_subtapes": ["EQZ(3)_63", "EQZ(81)_63", "LTZ(36)_64"],
}
