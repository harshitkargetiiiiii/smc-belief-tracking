# ICST revision notes — PR #10 submission-hardening pass

Paper-and-packaging-only pass. **No** change to any scientific artifact: no edits
under `conformance/`, `mpc/`, `reference/`, `.github/`, or `delivery_inspect.py`; no
new experiment, mutant, benchmark, E3, or Sigma_T; no result, number, SHA, or
empirical outcome changed; no security/privacy claim broadened.

Deliverables: `paper/main.tex`, `paper/main.pdf` (IEEEtran conference, 7 pp,
Author=Anonymous), `paper/icst-artifact/` (anonymized supplementary package),
this note. Line numbers below are into `paper/main.tex` as revised.

## The 13 requested corrections → where applied

1. **Mutation fault model repaired.** Replaced "faults injected into source only"
   with the explicit operator-space statement (§II, "Mutation model (the operator
   space of the study)", ~L161–168) and a matching Construct-validity threat
   (~L570–574). Enumerates the permitted application-level transformations and the
   exclusions (arbitrary compile-time imports, filesystem/network side effects,
   compiler-environment modification, and mutation of oracle/checker/policy/CI/
   validator/compiler). Framed as the study's operator space, **not** an
   adversarial-security boundary.

2. **Exhaustive cross-tape claim removed.** §II now reads: "we observed cross-tape
   transfer through memory and through register arguments passed by `call_tape` and
   received by `call_arg`; we do not claim these are the only possible cross-tape
   channels" (~L149–152). Whole-manuscript scan: no residual "only channel" /
   "only through memory or call_tape/call_arg" wording; the sole "only" is the
   negated disclaimer.

3. **Held-out interpretation corrected.** "We remove that threat" and "Mutation
   analysis is only as credible as its independence…" are gone. Replaced with:
   freezing the checker + preregistering a temporally held-out corpus "reduces
   post-hoc adaptation; the study remains white-box and same-project, not an
   independent red-team" (~L57, ~L370). Preserved: no aggregate mutation score
   (~L62, L373, L428), no detector-effectiveness estimate, H-R2 exact-strength,
   synthetic probes separated from source-realizable mutants.

4. **Cross-version claim corrected (abstract + body).** Abstract: "The artifact
   reproduces from a fresh checkout at the pinned backend, and the paper-critical
   backend observations replicate on one additional MP-SPDZ version" (L1, ~L63).
   Negative framing retained (~L512, L523, L540, L591): no identical-signature,
   byte-identity, compatibility, or version-independence claim.

5. **Anonymity leaks removed.** `\hypersetup{pdfauthor={Anonymous},…}` (L16),
   `\IEEEauthorblockN{Anonymous Author(s)}` (L34–36). Manuscript scan clean of
   305a3a8, PR numbers, branch names, GitHub usernames, public repo URLs, internal
   review IDs (R-xx), and automated-reviewer / assistant names. PDF metadata:
   Author=Anonymous, neutral Title/Subject/Keywords, standard LaTeX Creator/Producer;
   raw-PDF scan finds no author-identifying strings. AI-assistance limitation kept but
   rewritten neutrally: "The implementation, tests, review synthesis, and manuscript
   were produced within one project with substantial AI assistance; model agreement
   is not independent validation" (~L576–577). MP-SPDZ upstream pin `9d809599` kept
   (public dependency, needed to reproduce).

6. **"No new research" phrasing removed.** Heading is now "Contributions" (no
   parenthetical). Added: "The contribution is in software testing; we introduce no
   new MPC protocol, privacy theorem, or static-analysis technique" (~L65, L98). Six
   testing contributions listed (conformance-test design without a trusted oracle;
   anti-echo interface; layered functional/transcript/evidence oracles; mutation
   analysis of the compiled-delivery checker; preregistered held-out protocol;
   reproducible adequacy-boundary evidence).

7. **Explicit RQs added.** RQ1/RQ2/RQ3 defined in §I (~L119–124) and answered in a
   per-RQ results summary (~L530–538). RQ1 = which functional/delivery/transcript/
   provenance fault classes are detected; RQ2 = which held-out source-realizable
   mutants survive and which downstream oracle detects them; RQ3 = reproduction +
   cross-version recurrence.

8. **H-R2 exhibited directly.** Compact source listing of the
   `for j in range(N): r=(j+1)%N; …reveal_to(r)` permutation (~L441–448), with the
   note that PAYLOAD receives the same permutation. Outcome table `tab:hr2` (~L460):
   destination multiset = preserved; delivery checker = survives; transcript oracle =
   killed (foreign `PRIV j` record); scope = this concrete labelled permutation only.
   No claim that the transcript oracle catches all permutations.

9. **Title improved.** "Testing Delivery-Conformance Checks in MP-SPDZ: A
   Pre-Registered Mutation Case Study."

10. **Metamorphic-testing discussion fixed.** Related work now states the method uses
    a separately-implemented pseudo-oracle rather than metamorphic relations across
    executions; it does not imply the method is metamorphic testing.

11. **Expanded to fuller ICST length.** 7 dense pages, IEEEtran two-column, using
    only existing evidence: RQs, H-R2 listing + table, mutation-operator table, the
    two-phase preregistration protocol, exact fault-model restrictions, and per-RQ
    interpretation. No filler added.

12. **Anonymized supplementary artifact built** at `paper/icst-artifact/` (48 files,
    all checksummed in `SHA256SUMS.txt`). Neutral project name; no author name,
    username, remote URL, PR/branch, or identifying metadata in the authored prose.
    Contents: `checker/` (delivery linter, pseudo-oracle, runtime driver + gate,
    validator, tests), `subject-and-controls/` (honest builds + 5 leak controls),
    `reference/`, `prereg/` (PLAN.md + 22-mutant corpus + runner + 8 source mutants),
    `mutations/` (detection matrix), `results/`, `reproduce/` (both wrappers), plus
    `README.md`, `REPRODUCE.md`, `ERRATA.md`. Frozen scientific files shipped
    byte-identical; `ERRATA.md` discloses (a) that historical "memory-only" comments
    in the frozen checker are superseded by the manuscript's non-exhaustive cross-tape
    wording, and (b) that the frozen files retain non-identifying development
    annotations. Preregistration ordering (plan before results) documented and
    reviewer-verifiable by re-running the runner. Git-clone requirement for the
    wrappers documented as a packaging limitation, with a direct on-the-flat-files run
    path (Path A) given.

13. **Verification checklist — all pass** (see below).

## Verification checklist (item 13)

- **IEEEtran, compiles clean:** `\documentclass[conference]{IEEEtran}`; two
  `pdflatex` passes, `halt-on-error`, exit 0.
- **No undefined refs/citations:** none in the log (one benign Times
  italic-small-caps font substitution, cosmetic).
- **No identifying info** in `.tex`, PDF body, or PDF metadata; artifact authored
  prose clean; frozen-file annotations disclosed in `ERRATA.md`.
- **No 305a3a8 / PR# / username / automated-reviewer name / R-xx** in
  submission-facing material (manuscript + package prose).
- **No exhaustive cross-tape "only"** channel claim.
- **Held-out = partial mitigation, not removal.**
- **Cross-version:** no signature-across-versions / compatibility claim.
- **H-R2 shown and scoped** to the one concrete labelled permutation.
- **No new experiment / artifact change:** `git diff 305a3a8 HEAD -- conformance/
  mpc/ reference/ .github/` is empty (verified pre-push).
- **All newly added citations verified** (sources below).
- **Anonymous package reproduces or documents the limitation:** Path A regenerates
  the held-out outcomes on the flat files; the git-history dependency of the wrappers
  is documented as a packaging limitation.

## Citation verification (recorded here, not in the manuscript)

- **Just, Jalali, Ernst — The Major mutation framework**, FSE 2014, pp. 654–665,
  ACM DL `10.1145/2635868.2635929`.
- **Barr, Harman, McMinn, Shahbaz, Yoo — The Oracle Problem in Software Testing: A
  Survey**, IEEE TSE 41(5):507–525, 2015 (IEEE doc 6963470).
- **Chen et al. — Metamorphic Testing: A Review of Challenges and Opportunities**,
  ACM Computing Surveys 51(1), Article 4, pp. 4:1–4:27, 2018.
- **Jia & Harman — An Analysis and Survey of the Development of Mutation Testing**,
  IEEE TSE 37(5):649–678, 2011, DOI `10.1109/tse.2010.62`.
- **DeMillo, Lipton, Sayward — Hints on Test Data Selection**, IEEE Computer
  11(4):34–41, 1978.
- **Keller — MP-SPDZ: A Versatile Framework for Multi-Party Computation**, ACM CCS
  2020, pp. 1575–1590.
- **Skalka & Near — (positive dual, delivery correctness)**, ESOP 2025, LNCS 15695,
  pp. 258–285.

## Next step

Stop for Codex re-review of the manuscript and the anonymized package. No further
scientific work is intended in this pass.
