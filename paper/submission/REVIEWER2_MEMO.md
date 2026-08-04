# Reviewer #2 — Confidential Program Committee Memo

**Paper:** *Executable Conformance for a Secure-Multiparty Application: An MP-SPDZ Case Study on What Implementation-Level Evidence Checks, and Where It Stops Short of a Privacy Proof* (experience report / case study; artifact baseline `305a3a8`).

**Recommendation (see bottom line):** Reject.

**Reviewer stance:** I have only the manuscript (`main.tex`), no repository access. Every objection below is grounded in the text; where an objection targets a possible *misreading* of the paper, I say so explicitly and mark it `LIKELY-REVIEWER-MISUNDERSTANDING` so the AC can discount it.

**A structural observation that frames the whole review.** This manuscript's defensive strategy is *pre-emptive concession*: nearly every weakness a reviewer would raise is already conceded in the text ("not general coverage," "not independent validation," "not version-independent," "not a source `.mpc`," "not a bypass," "no aggregate rate," "we do not claim"). Conceding an objection is intellectually honest, but **it does not neutralize the objection's consequence for contribution value.** A paper that, by its own account, does not establish novelty, does not establish independence, does not establish generality, and does not establish a privacy property, has to be judged on the residue that survives its own disclaimers. My central finding is that after subtracting everything the authors concede they did not show, the residual durable contribution is a single-application engineering artifact plus one narrow, incidentally-caught observation — below the bar of a top security/MPC venue. I now go axis by axis.

---

## 1. Novelty

The paper disclaims its own core idea. From the abstract: *"We do not claim this principle is new --- that leakage is a dataflow rather than opcode-identity property is established for constant-time and smart-contract bytecode analysis; our contribution is the MPC-application instantiation, the pinned-backend mechanism, and a reproducible mutation study."* So the claimed novelty reduces to three items, and each is thin:

1. **"MPC-application instantiation" of a known principle.** The principle — information-flow safety is a dataflow/semantic property, not an instruction-name property — is credited (correctly) to ct-verif, Binsec/Rel, and Securify. The paper's own related-work sentence undercuts it: Binsec/Rel already *"decides constant-time relationally at the binary/opcode level on operand provenance, showing compiler backends inject leaks invisible to instruction-name checks."* That is the identical insight, already demonstrated *at the opcode level on a real compiler backend*. Re-observing it on MP-SPDZ bytecode ("a masked open and a raw reveal are the same opcode") is a change of *substrate*, not of *idea*. The paper never argues that the MPC setting poses a *qualitatively new* obstacle over the constant-time or EVM settings already covered — so the "instantiation" is textbook incremental work.
2. **"The pinned-backend mechanism."** Pinning a compiler commit and recomputing source hashes / delivery signatures is standard reproducible-builds and in-toto/SLSA practice — which the paper itself cites as the *"evidence-discipline neighbours."* Re-labeling it "the pinned-backend mechanism" does not make it a research novelty.
3. **"A reproducible mutation study."** Mutation testing predates this work by decades; the paper's own closest precedent, MASC, already *"evaluates crypto-misuse detectors with planted leaky mutants."* The delta claimed over MASC is "committed CI controls" versus "an offline third-party-detector benchmark" — a packaging/operational difference, not a conceptual advance. (And, per §3 below, the packaging difference actively *weakens* the evidence, because the same team writes both the mutants and the detector.)

**Objection 1a (core).** After the authors' own disclaimers, the residual novel content is a single-application re-instantiation of an explicitly-prior principle plus two pieces of standard engineering practice. That is below the novelty bar of IEEE S&P / USENIX / CCS / PoPETs, and — crucially — **novelty cannot be manufactured in revision.**
**Classification: FATAL-IF-TRUE.**

**Objection 1b.** The paper leans on a proliferation of bespoke terms — "anti-echo interface," "pseudo-oracle," "opcode-identity / channel-blocklist linter," "structural false accept," "manifest-level rule-coverage probe" — for what are, underneath, standard notions (an output-hiding differential-test harness, a differential oracle, a syntactic checker, a false negative, a synthetic test). The neologisms inflate the apparent conceptual footprint. **Classification: MINOR.**

---

## 2. Methodology

**Objection 2a — "conformance" is agreement with a possibly-wrong oracle on a hand-picked input set.** The functional contribution (Contribution 2) is that the circuit *"reproduces the pseudo-oracle's visible outputs"* on a fixture plus a *"bounded, constructed adversarial matrix of 228 cases,"* which the paper immediately concedes is *"a constructed test matrix, not general coverage."* All 228 cases are *functional* (circuit-vs-oracle agreement); none bear on leakage. So the headline "228/228" number establishes only that two co-developed artifacts agree on 228 author-chosen points — evidence that is weak in kind (agreement, not correctness) and small in quantity (constructed, bounded). For a privacy-adjacent artifact at a security venue this is far under what "conformance" would need to mean. **Classification: MAJOR-BUT-FIXABLE** (an independent reference model or a formal spec derivation would raise it; neither is present).

**Objection 2b — the decisive-category sample is n = 3.** The paper's "decisive" held-out finding rests on *three* pre-registered recipient-structure mutants (H-R1/H-R2/H-R3), of which the linter caught two and missed one. No statistics are possible on n = 3, and none are claimed — but then the evidentiary weight of "1 of 3" is close to anecdotal. The entire held-out corpus is 22 mutants, heavily subdivided (structural / semantic / synthetic / provenance / compile-invalid), so most cells contain a handful of items. **Classification: MAJOR-BUT-FIXABLE.**

**Objection 2c — single-host harness contaminates the one positive runtime result.** The paper concedes *"process isolation (stated, not enforced by the single-host test harness)"* and that *"the single-host harness is not adversarially isolated."* The S1 end-to-end run reports *"all three parties complete (return code 0)"* — but on one host this is a single process tree writing to a merged capture, i.e., *simulated* party semantics, not a distributed execution. This directly undermines the transcript check's evidentiary status (see §5, §8). **Classification: MAJOR-BUT-FIXABLE.**

**Objection 2d (misreading guard).** A reviewer might attack the paper for "claiming 92 tests / 117 items / 228 cases as coverage or as a result." The paper forecloses this: *"test counts are not themselves a result"* and *"This is a constructed test matrix, not general coverage."* Attacking it as a coverage claim would misread it. **Classification: LIKELY-REVIEWER-MISUNDERSTANDING.** (The valid form of the objection is 2a: the conformance evidence is weak *in kind*, regardless of counts.)

---

## 3. Adaptive overfitting

The paper is candid: *"the checker was repeatedly hardened against the same mutations later used as evidence (adaptive overfitting), so this sequence itself yields no held-out estimate of detector effectiveness."* This concession guts the B0–B6 mutation study as *evidence about the detector*. Every `REJECTED` row in Table 1 is tautological — the rule was added *because of* that mutation ("closed by whole-manifest inspection," "closed by content rules," "closed by broadened regex"). The "detection matrix" therefore measures only that the authors eventually wrote rules matching mutations they themselves wrote; it says nothing about power against unseen attacks.

**Objection 3a — the held-out "mitigation" is white-box, not out-of-sample in the sense that matters.** The paper offers the pre-registered corpus as the fix, but concedes it is *"out-of-sample but not an independent-adversary evaluation --- the mutants and predictions were authored within the same project that built the checker."* Worse than the paper admits: the *frozen linter's rules are visible to the mutant author*, and H-R2 is constructed to preserve *"the pinned destination-player multiset [0,0,1,1,2,2] --- all that rule (a) inspects."* That is a hand-computed evasion of a *known, read* rule. "Locked predictions" means the authors *predicted* H-R2 would pass — i.e., they knew it would evade rule (a) before running. So the held-out evaluation is **out-of-sample in time but white-box in construction**; it confirms that the authors can read their own frozen rule and write an input that dodges it. That is not a measurement of generalization, and the paper's "pre-registered, out-of-sample" framing oversells it. **Classification: MAJOR-BUT-FIXABLE** (a genuinely independent red-team with no rule visibility would fix it; expensive, and absent).

**Objection 3b — the Conclusion overclaims relative to the overfit evidence.** The Conclusion states the checks *"catch a family of gross delivery mistakes."* "A family" implies generalization beyond the specific five committed controls, but the only evidence that the controls are caught is precisely the overfit sequence in which each rule was added to catch its control. The defensible claim is "catch the five specific mutations we wrote rules for," which is materially weaker. **Classification: MINOR.**

**Objection 3c (misreading guard).** A reviewer might say "the authors hid the overfitting." They did not — they flag it repeatedly. Attacking them for concealment would misread. The valid objection (3a) is that the *mitigation is inadequate*, not that the problem is hidden. **Classification: LIKELY-REVIEWER-MISUNDERSTANDING.**

---

## 4. Pseudo-oracle independence

This is the load-bearing weakness for the functional half of the paper. The oracle is conceded to be *"a pseudo-oracle ... not an independently validated ground truth: it shares the specification with the circuit, so a correlated misreading of PLAS could make both agree on the wrong behaviour."* And the project's history proves the risk is live, not hypothetical: the oracle *"did carry one fatal transcription error (conditioning on the actual output only) until review caught it."*

**Objection 4a — there is no independent check on the oracle anywhere in the artifact.** The one candidate cross-check, the project's exact-rational reference model, *"implements a different (single-observer, stateless) functionality"* and so cannot validate it. Combined with the correlated-authorship disclosure — *"circuit, pseudo-oracle, tests, review synthesis, and manuscript were produced within one project and substantially with AI assistance; model agreement is not independent validation"* — the "separately implemented" framing collapses: the oracle is separate *from the circuit* but produced by the same author(s)/model from the same reading of PLAS 2012. **Separate implementation of the same misreading is not independence.** Since the entire functional-conformance case rests on circuit-vs-oracle agreement, and one fatal correlated error has already been found, there is no basis to assert the last one has been found. **Classification: MAJOR-BUT-FIXABLE** (an independent oracle, a formal derivation from the PLAS definitions, or third-party validation would fix it; none present).

**Objection 4b (misreading guard).** A reviewer might attack a claim that "the circuit is *correct*." The paper is careful never to claim this — it claims only *agreement on tested inputs*. Attacking a correctness claim it does not make would misread. **Classification: LIKELY-REVIEWER-MISUNDERSTANDING.** But note the sting in the tail: the claim the paper *does* make is so narrow (agreement of two co-authored artifacts on 228 points) that it is nearly vacuous as a security result — which loops back to §1/§2.

---

## 5. Significance of the H-R2 finding

H-R2 is billed as *"the decisive new result"* and *"the central new result"*: *"a demonstrated source-realizable structural false accept of the delivery linter"* — a build that delivers each verdict to the wrong recipient while preserving the destination multiset, *"caught only downstream"* by the transcript parser, *"for this concrete build,"* with the explicit disclaimer *"we do not claim the runtime layer catches recipient permutations in general."* I contend the significance is small, on four independent grounds.

**Objection 5a — it is true by construction, not a discovery.** The linter's rule (a) is *known* to inspect only the destination multiset; H-R2 is *defined* to preserve that multiset. "A multiset-preserving permutation passes a multiset check" is an immediate restatement of what rule (a) does, not an empirical surprise. Given the paper's own thesis (the linter is not a non-leakage checker), producing one input it misses is expected, not decisive. **Classification: MAJOR-BUT-FIXABLE** (reframing as an illustration rather than "the decisive result" would help; but then the paper's single new result evaporates).

**Objection 5b — it is caught by the very stack it lives in, and only incidentally.** End-to-end, the system has *no* false accept on H-R2 — the transcript parser rejects it because *"a foreign `PRIV j` record appears on the receiving party's stream."* The paper concedes this catch does not generalize. So H-R2 occupies a strange middle: a gap in layer A (linter) that layer B (transcript) happens to cover *for this one build, by luck of stdout multiplexing*. It demonstrates neither a real end-to-end vulnerability (it was caught) nor a general runtime gap (disclaimed). A finding that is simultaneously "caught" and "not generally caught" carries little transferable weight.

**Objection 5c — the "catch" is a single-host-harness artifact.** That *"a foreign `PRIV j` record appears on the receiving party's stream"* is a property of one-host merged stdout capture. In a real Rep3 deployment each party is a separate process on a separate host; party *i* delivering to the wrong party *j* over a channel would not necessarily surface on party *i*'s own stdout at all. So the one place the stack catches a leak is plausibly an artifact of the non-isolated test harness (§2c, §8), not a property of a real deployment. The paper's disclaimer ("not in general") quietly concedes this but does not draw the damaging conclusion.

**Objection 5d — the manuscript does not exhibit H-R2.** For "source-realizable" to carry weight the reader must see the source (or manifest) and be convinced it (i) looks like a legitimate `.mpc`, (ii) compiles to a multiset-preserving manifest, and (iii) survives the linter's *other* rules (memory, off-pin tapes). The manuscript asserts all three and points to `paper/heldout/`; with no repository access I can verify none of it. For "the central new result," an in-text construction or manifest excerpt is the minimum, and it is absent. **Classification (5b–5d combined): MAJOR-BUT-FIXABLE**, but compounding with §1 toward fatal: if the single new result is this narrow, incidentally-caught, and unexhibited, there is no durable contribution left once the non-novel principle is set aside.

---

## 6. Synthetic mutation realism

The mutations that most directly support the headline boundary claim are precisely the ones the paper concedes are *not* source-realizable.

**Objection 6a — the uncaught channel gap is synthetic; the source-realizable channel attack is caught.** The headline is *"the studied opcode-identity / channel-blocklist linter cannot be promoted to a general non-leakage checker ... `call_tape`/`call_arg` cannot be blocklisted, since the honest build uses it."* Examine the evidence for the *channel* half:
- **B6** (the *source-realizable* `call_arg` leak) is `REJECTED` by the final linter: *"the added tape breaks the pinned comparison-subtape multiset, and MP-SPDZ's call frame also spills through memory, tripping the memory rules ... B6 is not a demonstrated bypass of the final linter."*
- **H-O3** (the *uncaught* `call_arg` open in an existing masked subtape) is a *synthetic* probe with, in the paper's words, *"unproven source realizability, not executable attacks."* Likewise **B4** (multiset-blind-to-bodies), the cleanest demonstration of the gap, is *"a synthetic compiled-manifest counterexample, not a source `.mpc`."*

So the state of the evidence is: the one *realizable* attempt to leak via `call_arg` is *caught*, and the only *uncaught* `call_arg`/body leak is *synthetic and possibly not source-realizable at all*. If no legitimate `.mpc` compiles to the H-O3/B4 manifest, the "gap" exists only in a checker input the pinned compiler would never emit — a non-threat. The security bite of the headline therefore rests on manifests of unproven provenance. **Classification: MAJOR-BUT-FIXABLE** (exhibit a source-realizable H-O3, or prove impossibility; the paper does neither and defers it to future work).

**Objection 6b (partial concession to the authors).** The *false-positive* leg of the boundary claim — "you cannot blocklist `call_arg` because the honest build uses that channel" — is sound and does *not* need a realizable leak, since it follows from the honest build's own use of `call_tape`/`call_arg` (shown: `call_tape 12, 1, ci0, ... s202(81), s0(81)`). The *opcode-identity* leg ("a masked open and a raw reveal are the same instruction") is also sound. So the boundary claim's *"cannot be blocklisted without rejecting the honest build"* survives. What does *not* survive is any claim that a real author can *leak past the final linter* via that channel — B6 shows the opposite. The paper occasionally blurs "cannot be blocklisted" (true) into "the linter therefore misses real leaks here" (not demonstrated; the realizable one is caught). This blur should be scrubbed. **Classification: MAJOR-BUT-FIXABLE.**

---

## 7. Cross-version generality

**Objection 7a — the specific findings are pinned to two commits of one actively-developed tool.** The "backend findings" — the shared open instruction and the `call_tape`/`call_arg` path — are artifacts of MP-SPDZ's current bytecode design at commit `9d809599`, replicated only on *"one further MP-SPDZ version, v0.4.3 (`26a60536`)."* MP-SPDZ's bytecode/opcode layer is not a stable public interface; a codegen change can alter opcode identity or the register-passing mechanism without notice. The paper concedes the point five times over (*"two versions, not a cross-version compatibility or version-independence claim"; "backend-specific ... not version-independent"*). The lesson that *does* generalize — "syntactic checker ≠ semantic checker" — is exactly the *non-novel* part (§1); the part that is ostensibly *new* — the specific MP-SPDZ codegen facts — is exactly the part that *does not* generalize and may not survive the next release. That is an unfavorable pairing for an archival paper: the durable content is not new, and the new content is not durable. **Classification: MAJOR-BUT-FIXABLE** as a contribution-value matter (broad cross-version and cross-backend study would help). The *scoping* is accurate — this is not a misrepresentation — so it is not a soundness defect.

**Objection 7b — two versions of one lineage is near-tautological replication.** v0.4.3 and the pin likely share codegen ancestry; agreement between two close releases rules out little (e.g., a one-build transient) and establishes essentially no generality. Calling it "replication" dignifies it. **Classification: MINOR.**

---

## 8. Rep3 / privacy hand-off

This is, for a security/MPC venue, the decisive axis.

**Objection 8a — the paper establishes nothing about the privacy property its venue exists to evaluate.** The runtime Rep3 adversary — *"at most one semi-honest corrupted party ... This is the adversary a protocol-level privacy argument would target"* — is the one an MPC PC cares about, and the paper states plainly: *"Our functional and linting evidence does not address it."* The privacy property is deferred in full to future work: *"(i) privacy of the executed circuit --- a Rep3 simulation argument (a human MPC specialist) ...; (ii) semantic source-to-spec binding."* So the paper's relationship to MPC privacy is a *to-do list handed to a specialist*, not a result. A privacy paper that proves no privacy property, at a privacy venue, is mis-slotted. And this is not fixable in revision by the authors' own account — they say (i) needs a human MPC specialist's simulation proof they did not produce. **Classification: FATAL-IF-TRUE.**

**Objection 8b — the build-time adversary is an artificial model chosen so the tool has something to do.** The only adversary the paper *does* engage *"controls the target `.mpc` application source, and only that"* — not the compiler, oracle, checker, policy, CI, or evidence validator, all of which are trusted. The paper even admits the model is gerrymandered around the tool: *"Were the TCB itself adversarial, every automated check would be trivially void; stating the boundary is what makes the study meaningful."* A threat model defined precisely so that the defense is non-vacuous is a weak foundation for a *security* result: real supply-chain adversaries who can write application source typically also influence review/CI, and the paper's own defense (a linter written by the same team inside the TCB) would not survive that. This is a software-engineering conformance question wearing MPC-threat-model clothing. **Classification: MAJOR-BUT-FIXABLE** as framing, but it compounds 8a: strip the artificial model and there is no adversary the security community recognizes left standing.

**Objection 8c (misreading guard).** A reviewer might attack the paper for "claiming a privacy guarantee / a simulation proof." It claims neither; it is explicit that a *"privacy guarantee needs a protocol-level proof"* it does not supply. Attacking a claimed proof would misread. **Classification: LIKELY-REVIEWER-MISUNDERSTANDING.** The valid objection (8a) is the *absence* of the result, not a false claim of it.

---

## 9. Case-study scope

**Objection 9a — n = 1, on the trivial fragment.** One application, two toy queries (`p1_is_max`, `sum_even`), N = 3 parties, domain D = {0,1,2}, one backend, one host. The paper concedes it does *"not imply an evaluated methodology across MPC applications plural."* More damaging: it implements only *"deterministic, total, public queries,"* while *"persistent secret-shared state across invocations ($\Sigma_T$) is unimplemented and out of scope."* The belief *update* across invocations — the part that makes "knowledge-threshold belief tracking" more than a one-shot threshold check — is exactly what is omitted. So the "PLAS instantiation" is a partial instantiation of the *least novel, stateless* fragment. On a 3-element domain with 3 parties, even the functional instance is near-trivial. **Classification: MAJOR-BUT-FIXABLE** (broaden applications, implement $\Sigma_T$), and it compounds §1.

**Objection 9b — the "case-study lesson" did not need this artifact.** §Boundary item 2 distills the transferable lesson as: *"adaptive linting of a security property can produce false confidence, and such tooling should print its assurance boundary."* That is a generic software-engineering aphorism; it is not evidence-bearing and required no MP-SPDZ implementation to state. **Classification: MINOR.**

---

## 10. Artifact credibility (assessed from the manuscript only)

I cannot run the repository. These are traceability/credibility concerns *as presented in the text*.

**Objection 10a — the decisive results are not in the "frozen artifact."** The header and title pin the artifact to `305a3a8`, but the decisive material lives elsewhere: B4/B6/S1 are *"Not committed to the frozen artifact"* (Table 1 caption) and sit under `paper/mutations/`; the held-out corpus (including H-R2) is at *"preregistration `d3d11e4`, results `9e22007`,"* with the backend pinned separately at `9d809599`. So "the frozen artifact" (`305a3a8`) and "the artifact that produces the headline result H-R2" are *different code at different commits*. A reader cannot tell from the manuscript what is reproducible at the advertised baseline versus bolted on later. For a paper whose credibility rests on reproducibility, this commit sprawl around the load-bearing results is a real concern. **Classification: MAJOR-BUT-FIXABLE.**

**Objection 10b — "machine-checked/machine-readable" is doing unearned credibility work.** The header advertises *"Detection matrix data is machine-checked."* But the paper elsewhere concedes (for the evidence validator) that recomputation establishes *"self-consistency and provenance ... not integrity."* Machine-checking that a JSON's hashes recompute verifies *consistency*, not that a mutation means what the prose claims or that a "synthetic manifest" is source-realizable. The repeated "machine-readable" branding should not be read as validation. **Classification: MINOR.**

**Objection 10c — reproducibility is of a *normalized* object.** The paper reproduces *"normalized-assembly signatures, not raw binaries or assembly byte-for-byte."* The normalization step is inside the TCB and is not specified in the manuscript; a normalization that discards the wrong differences would mask exactly the kind of codegen change §7 worries about. **Classification: MINOR.**

**Objection 10d — the submission is not finished.** The byline carries *"\open{author metadata}"*, and the bibliography carries *"\open{confirm pages}"* on the MP-SPDZ citation. Load-bearing factual claims are cited to an *inaccessible internal review log* (R-10, R-13, R-22, R-31, R-34, R-41, R-45, ...) that a reviewer cannot check — e.g., the *"fatal transcription error ... until review caught it"* rests on "R-13," and B4's demonstration on "R-45." An `\open{}` in the author line plus unverifiable internal citations for the paper's most important admissions reads as a draft, not a submission-ready manuscript. **Classification: MINOR** individually; collectively they erode confidence.

**Objection 10e — no independent party anywhere in the loop.** *"the circuit, the pseudo-oracle, the tests, the review synthesis, and this manuscript were produced within a single project and substantially with AI assistance."* The much-advertised "three-party adversarial review" is three *roles* inside one AI-assisted project, not three independent parties. For a security artifact, the absence of any independent human or tool is a first-order credibility discount. **Classification: MAJOR-BUT-FIXABLE** (obtain independent validation) — overlaps §4 and Threats-to-Validity.

---

## 11. Writing / presentation

**Objection 11a — pathological hedging obscures the contribution.** The abstract alone contains a dozen negations; across the paper the reader must reconstruct the positive contribution by *subtraction*. Honesty is a virtue, but a scientific paper must state what it establishes crisply, and here almost every declarative sentence is immediately qualified into near-emptiness. The density of disclaimers is itself diagnostic: it signals the authors are aware the residue is thin. **Classification: MINOR** (but symptomatic of §1/§5).

**Objection 11b — the central result is buried and entangled.** H-R2, the "decisive new result," appears in a single mid-paragraph of §5.4, braided together with synthetic-probe caveats, the H-O3 aside, and the semantic-mutant list. A paper whose novelty hinges on one result should foreground and fully exhibit it, not fold it into a caveat-laden paragraph. **Classification: MINOR.**

**Objection 11c — lab-notebook texture.** The prose is saturated with build-specific tokens (`EQZ(3)_63`, `vstms`/`vldms`, `call_tape 12, 1, ci0`, `manifest_signature`, "rule (a)/(h)") and 40-plus `\repo{... R-xx}` pointers into a private log, reading like a distilled review-log rather than a self-contained paper. Counts are piled up (*"117 collected pytest items ... the 92 conformance items plus the 9 reference test functions, which expand to 25 ... 46 functional and 46 delivery-gate ..."*) immediately after asserting *"test counts are not themselves a result"* — an internal tension between foregrounding numbers and disowning them. **Classification: MINOR.**

---

## Cross-cutting synthesis (why the concessions compound)

Individually, most objections above are `MAJOR-BUT-FIXABLE` or `MINOR`, and the authors would rightly note they conceded many. But the concessions *interact multiplicatively*, and the survivors are the fatal ones:

- Novelty is disclaimed down to "instantiation + pinning + a mutation study" (§1, `FATAL-IF-TRUE`).
- The one *new* result (H-R2) is by-construction, incidentally caught, harness-dependent, and unexhibited in text (§5).
- The uncaught channel gap that would give the headline its bite is *synthetic and possibly not source-realizable*, while the realizable version is *caught* (§6).
- The specific findings are pinned to two commits of one tool and disclaimed as non-general (§7).
- The privacy property the venue exists for is *entirely future work* under an *artificial* build-time model (§8, `FATAL-IF-TRUE`).
- The functional core rests on a *co-authored, already-once-fatally-wrong* oracle with no independent check (§4), scoped to a *stateless, N=3, D={0,1,2}* fragment (§9).

Each concession is honest; together they leave a single-application engineering diary whose durable, generalizable, novel, privacy-relevant residue is close to empty. That is the rejection case.

---

## Reviewer #2 bottom line

**Overall leaning: Reject.** (Not "major revision": the two fatal axes — insufficient residual novelty and the total absence of a privacy result at a privacy venue under an artificial threat model — cannot be repaired by revision. The authors themselves defer the privacy result to a human MPC specialist and future work.) I acknowledge the paper is unusually honest and technically careful, and that several of the harshest-sounding attacks a careless reviewer would make are foreclosed by the text (I flagged those `LIKELY-REVIEWER-MISUNDERSTANDING`). Honesty, however, is not a contribution.

**The three objections most likely to sink the paper:**

1. **No novelty survives the paper's own disclaimers** (§1, Obj. 1a) — the residual contribution is a single-application re-instantiation of an explicitly-prior principle (leakage is dataflow, not opcode identity; already shown at the opcode level by Binsec/Rel) plus standard reproducible-builds and mutation-testing practice. **FATAL-IF-TRUE.**

2. **No privacy result at a privacy venue, under an artificial adversary** (§8, Obj. 8a/8b) — the paper explicitly addresses none of the runtime Rep3 privacy property and defers it wholesale to a "human MPC specialist," while the only adversary it engages is a gerrymandered build-time model the authors admit is defined so the tool is "not vacuous." **FATAL-IF-TRUE.**

3. **The evidentiary core is overfit/white-box and the one durable new finding is thin** (§3 + §5 + §6) — the mutation study is adaptively overfit by the authors' own admission; the "held-out" mitigation is white-box (mutants built against the read, frozen rules); the "decisive" H-R2 is a by-construction, incidentally-caught, harness-dependent, in-text-unexhibited false accept; and the uncaught channel gap that would give the headline security bite is synthetic with unproven source-realizability while the realizable attempt (B6) is caught. **MAJOR-BUT-FIXABLE individually, but jointly they leave no durable new result.**
