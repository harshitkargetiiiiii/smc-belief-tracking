# LITERATURE_REVIEW.md — E1

**Purpose.** Substantiate or refute the novelty claims in `paper/main.tex` /
`PAPER_PLAN.md` §6 against the primary literature, before those claims are
written un-hedged. This file **recommends** changes to the manuscript; it does
**not** edit the manuscript's novelty claims (per directive). No new
implementation was written; E3 and `Sigma_T` remain unauthorized.

**Verification discipline.** Primary sources only. Each entry names the venue and
a URL that was fetched to confirm authors/venue/year. Where a publisher page
(IEEE Xplore, ACM DL, IACR ePrint, Wiley) bot-blocked the fetcher, metadata was
confirmed via an authoritative bibliographic record (dblp / OpenAlex-Crossref) or
the authors' own hosted PDF or the official venue program page; such entries are
tagged **[pub-page blocked; metadata via …]**. That tag means "primary source,
publisher page not directly fetched," not "unverified." Genuinely unconfirmed
leads are quarantined under **§9 [OPEN]** and are not cited as established.

---

## 1. Search strategy (systematic)

- **Seed terms per category** (below), issued to web search, then snowballed
  forward/back from each hit's references and citing papers.
- **Category seeds.**
  - *MPC implementation verification:* "verified secure multiparty computation",
    "MPC compiler correctness", "information-flow type system secure computation",
    "mechanized simulation proof MPC", "EasyCrypt MPC", "replicated secret sharing
    formal proof".
  - *Differential / conformance testing:* "differential testing", "conformance
    test vectors cryptography", "test oracle problem", "metamorphic testing
    security", "adversarial testing certificate validation".
  - *Compiler / bytecode security analysis:* "constant-time verification",
    "relational/2-safety leakage", "secure compilation", "bytecode information-flow
    analysis", "smart-contract static analysis dataflow vs syntactic", "verified
    cryptographic compiler".
  - *Mutation testing for crypto/security:* "mutation testing cryptographic",
    "security mutation operators", "evaluate detector with injected
    vulnerabilities", "negative controls security analysis", "mutation testing
    protocol implementations".
  - *Reproducible security evidence:* "reproducible builds", "software supply
    chain provenance", "in-toto", "SLSA", "artifact evaluation badging",
    "verifiable CI evidence".
- **Discovery vs citation.** Search engines, Semantic Scholar, Wikipedia, and
  vendor blogs were used only to *locate* candidates; a candidate was admitted
  only after reaching a primary/authoritative record.
- **Anti-fabrication rule.** A paper is listed only with a fetched verifying URL.
  Uncertain items go to §9, not the body.
- **Known coverage gaps (see §9):** IACR ePrint and Google Scholar were not
  directly reachable by the fetcher, so a subset of cryptography-venue results may
  be under-sampled; this is logged as a residual `[OPEN]` on the negation ("no
  prior work does X").

## 2. Inclusion / exclusion criteria

**Include** if: (a) peer-reviewed paper at a CS venue, OR an official
standard/specification/versioned artifact for a named engineering effort (e.g.
SLSA, Reproducible Builds, Wycheproof); AND (b) authors/venue/year confirmed from
a primary or authoritative bibliographic record; AND (c) topically relevant to at
least one of our contributions C1–C5 / the evidence discipline.

**Exclude:** blog posts, vendor marketing, Wikipedia, and secondary summaries as
*citations* (allowed only for discovery); papers whose metadata could not be
confirmed (→ §9); work relevant only by keyword collision (e.g. "belief" in ML).

**Our contributions, for the overlap column** (from `PAPER_PLAN.md` §3):
C1 executable-conformance methodology for an MPC *application* (independent
oracle + anti-echo interface + recomputed SHA-bound evidence);
C2 reproducible conformance artifact (fixture + 228-case sweep + 5 executable
negative controls);
C3 empirical boundary result — opcode-level static inspection of compiled MPC
assembly cannot soundly certify per-recipient non-leakage vs a source-controlling
author (bypass taxonomy; masked-open ≡ raw-reveal opcode; `call_arg` channel);
C4 articulation of the hand-off (executed-circuit privacy AND semantic
source-to-spec binding);
C5 adversarial three-party review + reproduce-before-fix loop.

---

## 3. Category A — MPC implementation verification

### A1. Rastogi, Hammer, Hicks — Wysteria (IEEE S&P 2014)
[verify: https://www.microsoft.com/en-us/research/publication/wysteria-programming-language-generic-mixed-mode-multiparty-computations/]
- **Problem:** a typed DSL for mixed-mode MPC.
- **Method:** type-and-effect system; on-paper single-thread/distributed correspondence theorem.
- **Evidence:** type soundness + correspondence proved on paper; working implementation.
- **Limitations:** on-paper (not mechanized); certifies *source*, trusts the compiler/runtime; semi-honest.
- **Overlap:** touches C3/C4 as a *positive, source-level* certification — the trusted-source baseline our compiled-level negative result (C3) sits below. Orthogonal to C1/C2/C5.

### A2. Rastogi, Swamy, Hicks — Wys★ (POST/ETAPS 2019)
[verify: https://www.microsoft.com/en-us/research/publication/wys-a-dsl-for-verified-secure-multi-party-computations/ ; https://arxiv.org/abs/1711.06467]
- **Problem:** formally verified MPC programs.
- **Method:** deep embedding in F★; mechanized metatheory that source-level properties transfer to distributed semantics.
- **Evidence:** machine-checked metatheory; verified examples (PSI, median).
- **Limitations:** trusts the F★/Wys★ toolchain/interpreter; not MP-SPDZ; verifies programs *in* the DSL, not an untrusted compiler's assembly.
- **Overlap:** **closest to C4** — mechanizes exactly the semantic source-to-spec binding we say is required, formally rather than by testing. Does not touch our compiled-assembly / source-controlling-author threat model, or C1/C2.

### A3. Sweet, Darais, Heath, Harris, Estes, Hicks — Symphony (Programming, vol. 7(3), 2023)
[verify: https://programming-journal.org/2023/7/14/]
- **Problem:** expressive MPC with coordination (first-class shares/party sets).
- **Method:** λ-Symphony core calculus; view-correspondence proofs; prototype interpreter.
- **Evidence:** metatheory (SIMD-view = distributed semantics); competitive performance.
- **Limitations:** core metatheory on-paper; correspondence, not non-leakage certification.
- **Overlap:** touches C4 (a source→distributed correspondence). Orthogonal to C1/C2/C3/C5.

### A4. Almeida, Barbosa, Barthe, Dupressoir, Grégoire, Laporte, Pereira — A Fast and Verified Software Stack for SFE (ACM CCS 2017)
[verify: https://acmccs.github.io/topic-22/ ; IACR ePrint 2017/821 — pub-page blocked; metadata via official CCS'17 accepted-papers listing]
- **Problem:** end-to-end *verified* 2-party SFE (Yao + OT), proof down to assembly.
- **Method:** EasyCrypt machine-checked security + functional correctness, connected to verified low-level implementation.
- **Evidence:** machine-checked semi-honest security + correctness of the running assembly; competitive speed.
- **Limitations:** 2-party Yao, not 3-party Rep3/MP-SPDZ; builds a *verified* stack rather than certifying an *untrusted* compiler's output.
- **Overlap:** **closest realization of C4's target** (spec→proof→binary). Stands in exact contrast to C3 (which concerns an untrusted compiler under a source-controlling adversary).

### A5. Butler, Aspinall, Gascón — How to Simulate It in Isabelle (ITP 2017)
[verify: https://www.research.ed.ac.uk/en/publications/how-to-simulate-it-in-isabelle-towards-formal-proof-for-secure-mu/ ; https://arxiv.org/abs/1805.12482]
- **Problem:** mechanize the simulation paradigm for MPC security.
- **Method:** Isabelle/HOL + CryptHOL; simulation-based proofs for building blocks.
- **Evidence:** machine-checked simulation proofs for basic primitives.
- **Limitations:** building-block scope; no executable/compiled artifact; no conformance layer.
- **Overlap:** C4 — mechanizes the simulation privacy argument we hand off to. Orthogonal to C1/C2/C3/C5.

### A6. Haagh, Karbyshev, Oechsner, Spitters, Strub — Computer-Aided Proofs for MPC with Active Security (IEEE CSF 2018)
[verify: https://research.vu.nl/en/publications/computer-aided-proofs-for-multiparty-computation-with-active-secu ; https://arxiv.org/abs/1806.07197]
- **Problem:** machine-checked security for secret-sharing MPC (Maurer), active security.
- **Method:** EasyCrypt formalization of additive **and replicated** secret sharing, secure add/mult; "input independence" notion; program-equivalence proofs.
- **Evidence:** machine-checked active-security proofs for the primitives, incl. replicated SS.
- **Limitations:** protocol/primitive level; no implementation-to-assembly binding; no conformance.
- **Overlap:** **closest on the exact protocol primitive we use** — mechanizes replicated-secret-sharing security (our artifact is semi-honest Rep3). The protocol-level proof our C4 hand-off would invoke. Orthogonal to C1/C2/C3/C5.

### A7. Canetti, Stoughton, Varia — EasyUC (IEEE CSF 2019)
[verify: https://open.bu.edu/handle/2144/40575 ; IACR ePrint 2019/582]
- **Problem:** mechanize simulation-based, *composable* (UC) proofs.
- **Method:** UC real/ideal/simulator structure inside EasyCrypt; modular composition.
- **Evidence:** machine-checked UC proof for secure message transmission (DH + OTP), incl. composition.
- **Limitations:** general crypto case study, not an MPC application; no executable/conformance link.
- **Overlap:** C4 — the composable form of the privacy proof we defer to. Orthogonal to the rest.

### A8. Mood, Gupta, Carter, Butler, Traynor — Frigate (IEEE EuroS&P 2016)
[verify: official program https://www.ieee-security.org/TC/EuroSP2016/preliminary-papers.php ; DOI 10.1109/EuroSP.2016.20 — pub-page blocked; metadata via IEEE-Security TC program + dblp]
- **Problem:** existing MPC compilers emit buggy circuits; build a *validated* compiler+interpreter.
- **Method:** random test generation + **differential/self-consistency testing** of the compiler against a reference interpreter; efficient extensible IR.
- **Evidence:** finds correctness bugs in existing MPC compilers; own outputs pass its validation suite.
- **Limitations:** validates *compiler functional correctness* via self-consistency, **not** against an independent oracle, and **not** non-leakage; no anti-echo interface, no CI-bound recomputed evidence, no negative controls.
- **Overlap:** **closest to C1/C2 within MPC** — but at the *compiler* layer, using differential/self-consistency testing rather than an independently-written plaintext oracle with anti-echo + SHA-bound CI evidence, and with no leakage dimension. Does **not** subsume C1/C2.

### A9. Kerschbaum — An Information-Flow Type-System for Mixed Protocol Secure Computation (ACM ASIACCS 2013)
[verify: dblp https://dblp.org/rec/conf/ccs/Kerschbaum13.html ; ACM DOI 10.1145/2484313.2484364 (listing confirmed via search) ; patent US8839410B2 corroborates authorship — pub-page blocked; metadata via dblp + ACM listing]
- **Problem:** certify that a mixed-protocol secure computation does not leak more than intended.
- **Method:** a static **information-flow type system** tracking secret vs revealable values; type-checks the composed computation for non-leakage.
- **Evidence:** soundness of the type system; source/type-level certification.
- **Limitations:** trusts the type checker/compiler; certifies the *source*, not the compiled circuit; no adversary controlling the compiled program text.
- **Overlap:** **closest positive result to C3.** Our C3 is the *complementary negative result one layer below*: pushed down to untrusted compiled MP-SPDZ assembly under a source-controlling author, the same certification goal becomes unsound. Does **not** subsume C3 — different layer + threat model.

**Closest in A:** **Kerschbaum 2013** (positive source-level IFC ⟷ our negative compiled-level C3) and **Frigate 2016** (testing-based MPC-compiler validation ⟷ our independent-oracle application-level C1/C2). Neither addresses the compiled-assembly opcode ambiguity or a source-controlling author.

---

## 4. Category B — Differential & conformance testing

### B1. McKeeman — Differential Testing for Software (Digital Technical Journal, 1998)
[verify: https://dblp.org/rec/journals/dtj/McKeeman98.html]
- **Problem/method:** coins differential testing — mass random inputs; cross-implementation *disagreement is the oracle*.
- **Evidence:** applied to C compilers etc.
- **Limitations:** needs ≥2 implementations; blind to common-mode faults; no ground truth.
- **Overlap:** conceptual ancestor of C1 that we explicitly *depart from* — we use a single **independent** oracle, so a common-mode or author-controlled fault cannot hide in agreement.

### B2. Yang, Chen, Eide, Regehr — Csmith (PLDI 2011)
[verify: https://www.flux.utah.edu/paper/yang-pldi11]
- **Problem/method:** find compiler bugs via UB-free random C programs; voting/differential oracle.
- **Evidence:** >325 bugs in GCC/LLVM/commercial over 3 years.
- **Limitations:** voting oracle defeated by correlated bugs; UB-free subset only.
- **Overlap:** its constrained generator is the analogue of our **228-case adversarial sweep** (C2). Differential, not independent-oracle.

### B3. Brubaker, Jana, Ray, Khurshid, Shmatikov — Frankencerts (IEEE S&P 2014)
[verify: https://www.cs.columbia.edu/~suman/docs/frankencert.pdf ; program https://www.ieee-security.org/TC/SP2014/papers/toc.html]
- **Problem/method:** adversarially *mutate/recombine* real X.509 certs (>8M) that a validator must handle; cross-implementation discrepancy = oracle.
- **Evidence:** 208 discrepancies, 15 root causes across 8+ TLS stacks; some MITM-exploitable.
- **Limitations:** discrepancy oracle only (no ground truth, no common-mode, no author-controlled leakage); manual correctness attribution.
- **Overlap:** **closest applied neighbor to C1/C2 and to C5's adversarial-negative-control spirit** — but mutates *inputs* not *programs*, uses N-version discrepancy not an independent oracle, and structurally cannot cover a source-controlling adversary (our C3).

### B4. Chen, Su — Mucert (ESEC/FSE 2015)
[verify: https://dblp.org/rec/conf/sigsoft/ChenS15.html]
- **Problem/method:** MCMC-guided cert mutation to reach discrepancies with fewer tests.
- **Evidence:** new discrepancies with far fewer certs than frankencerts.
- **Limitations:** discrepancy-oracle; domain-specific.
- **Overlap:** guided coverage ≈ the goal of our sweep (C2). Differential, not independent-oracle.

### B5. Petsios, Tang, Stolfo, Keromytis, Jana — NEZHA (IEEE S&P 2017)
[verify: https://dblp.org/rec/conf/sp/PetsiosTSKJ17.html]
- **Problem/method:** domain-independent differential testing via "relative diversity" (δ-diversity) guidance.
- **Evidence:** 778 discrepancies / 8 memory bugs across TLS libs + parsers; beats frankencerts on yield.
- **Limitations:** discrepancy oracle across ≥2 implementations; manual attribution.
- **Overlap:** state-of-the-art differential testing we position against (C1/C2). Orthogonal to C3/C4/C5.

### B6. Project Wycheproof — Google → C2SP (2016–)
[verify: https://github.com/C2SP/wycheproof — **no peer-reviewed paper**; primary artifact = the test-vector repository; introduced via RWC 2016 talk]
- **Problem/method:** JSON **test vectors with expected accept/reject** encoding real attack edge cases for crypto **primitives**; conformant iff it matches every vector (reference-oracle conformance).
- **Evidence:** 80+ categories; surfaced real bugs in production libraries; de-facto standard.
- **Limitations:** tests *primitives*, not an application/compiled circuit; the vectors literally **feed expected outputs to the checker** (the opposite of our anti-echo design); no formal venue.
- **Overlap:** **closest to C2 and partial C1** (independent expected-output oracle) — one level down (primitive vs application) and with **no anti-echo constraint**, which is precisely the contamination risk our design addresses in the MPC setting.

### B7. Segura, Fraser, Sanchez, Ruiz-Cortes — A Survey on Metamorphic Testing (IEEE TSE 2016)
[verify: http://eprints.whiterose.ac.uk/110335/]
- **Problem/method:** testing "non-testable" programs via metamorphic relations instead of a full oracle; taxonomy/survey.
- **Evidence:** consolidates 100+ studies incl. security/crypto.
- **Limitations:** partial correctness only; survey.
- **Overlap:** the main *alternative* to a full oracle; we instead *build* an independent oracle (situates C1).

### B8. Barr, Harman, McMinn, Shahbaz, Yoo — The Oracle Problem in Software Testing: A Survey (IEEE TSE 2015)
[verify: https://discovery.ucl.ac.uk/1471263/]
- **Problem/method:** definitive taxonomy of test oracles — specified / derived (pseudo-oracle, N-version, metamorphic, regression) / implicit.
- **Evidence:** the standard framework situating differential + independent-reference oracles.
- **Limitations:** survey; no crypto/MPC application.
- **Overlap:** **conceptual anchor for C1** — our "independent plaintext oracle" is a *pseudo-oracle / independent-reference* oracle in this taxonomy; the anti-echo interface is a refinement (oracle contamination) not treated here.

**Closest in B:** **Wycheproof** (reference-oracle crypto conformance; gap = primitive-level, echoes expected outputs, no application/threat model) and **Frankencerts** (adversarial security-critical differential testing; gap = N-version discrepancy, input-mutation, no independent oracle, no source-controlling author).

---

## 5. Category C — Compiler & bytecode-level security analysis

### C-1. Leroy — CompCert (CACM 2009)
[verify: https://dblp.org/rec/journals/cacm/Leroy09.html]
- **Problem/method:** Coq-verified C compiler preserving observable *behavior* (semantic preservation).
- **Evidence:** end-to-end machine-checked proof; used in certified settings.
- **Limitations:** preserves behavior, **not** security hyperproperties (non-interference/leakage) — the gap that motivated CT-preservation work.
- **Overlap:** background for C4; the "trusted compilation" baseline a stock MPC compiler does not give us.

### C-2. Patrignani, Ahmed, Clarke — Formal Approaches to Secure Compilation (ACM CSUR 2019)
[verify: https://dblp.org/rec/journals/csur/PatrignaniAC19.html]
- **Problem/method:** survey/framework of full-abstraction / property-preserving compilation vs target-level attackers.
- **Evidence:** comprehensive taxonomy.
- **Limitations:** framework, not an analyzer; not MPC-specific.
- **Overlap:** vocabulary for C3's threat-model asymmetry (a *source-controlling* adversary vs a target-level check).

### C-3. Almeida, Barbosa, Barthe, Blot, Grégoire, Laporte, Oliveira, Pacheco, Schmidt, Strub — Jasmin (ACM CCS 2017)
[verify: https://dblp.org/rec/conf/ccs/AlmeidaBBBGLOPS17.html — pub-page blocked; metadata via dblp]
- **Problem/method:** low-level language + Coq-verified compiler; correctness + constant-time checked with predictable mapping to assembly.
- **Evidence:** verified, fast real primitives.
- **Limitations:** requires code written in Jasmin + proof effort; not a post-hoc check of arbitrary bytecode.
- **Overlap:** concrete instance of C4's "verified, dataflow-checked primitive" — the real-guarantee route our hand-off advocates.

### C-4. Barthe, Blazy, Grégoire, Hutin, Laporte, Pichardie, Trieu — Formal verification of a constant-time-preserving C compiler (POPL 2020, PACMPL 4)
[verify: https://dblp.org/rec/journals/pacmpl/BartheBGHLPT20.html]
- **Problem/method:** extend CompCert to *preserve* a leakage/observation model (memory+branch traces) — dataflow property, not just I/O.
- **Evidence:** machine-checked preservation over the pass pipeline.
- **Limitations:** preserves CT if it holds at source; does not *decide* leakage of adversarial source; timing model.
- **Overlap:** shares C3's premise (leakage must be tracked *through* compilation, not read off the surface). A positive/preservation result, not our negative boundary.

### C-5. Almeida, Barbosa, Barthe, Dupressoir, Emmi — Verifying Constant-Time Implementations / ct-verif (USENIX Security 2016)
[verify: https://www.usenix.org/conference/usenixsecurity16/technical-sessions/presentation/almeida]
- **Problem/method:** reduce constant-time to **2-safety** (safety of a self-composed product program) on optimized LLVM IR.
- **Evidence:** verifies real NaCl/OpenSSL routines at IR level.
- **Limitations:** LLVM IR (not final assembly); timing model, not MPC reveal.
- **Overlap:** **especially close to C3's structure** — canonically states the property is *relational/dataflow*, so single-execution per-instruction inspection is the wrong tool. Same shape as our "asm_open safe-vs-leaking is dataflow, not opcode identity."

### C-6. Daniel, Bardin, Rezk — Binsec/Rel (IEEE S&P 2020)
[verify: https://dblp.org/rec/conf/sp/DanielBR20.html ; https://arxiv.org/abs/1912.08788 — pub-page blocked; metadata via dblp + arXiv]
- **Problem/method:** relational symbolic execution deciding constant-time at **binary/opcode level** on operand *provenance*.
- **Evidence:** shows `gcc -O0` and clang backend passes inject CT violations invisible to IR-level tools; 338 binaries.
- **Limitations:** bounded/relational cost; timing model.
- **Overlap:** **especially close to C3** — operates at our exact granularity yet decides safety *relationally on operand provenance*, not opcode identity (a load with a public vs secret index). The binary-level analogue of our point (a) and the dataflow route in C4.

### C-7. Barthe, Betarte, Campo, Luna, Pichardie — System-level Non-interference for Constant-time Cryptography (ACM CCS 2014)
[verify: https://dblp.org/rec/conf/ccs/BartheBCLP14.html — pub-page blocked; metadata via dblp]
- **Problem/method:** formalize constant-time as **non-interference**; machine-checked.
- **Evidence:** machine-checked NI results.
- **Limitations:** timing/cache observations, not MPC opcode manifests.
- **Overlap:** grounds the "leakage is IFC/dataflow" framing behind C3, theoretically.

### C-8. Tsankov, Dan, Drachsler-Cohen, Gervais, Bünzli, Vechev — Securify (ACM CCS 2018)
[verify: https://dblp.org/rec/conf/ccs/TsankovDDGBV18.html ; https://ar5iv.labs.arxiv.org/html/1806.01143 — pub-page blocked; metadata via dblp + ar5iv]
- **Problem/method:** soundly decide security properties of **compiled EVM bytecode** by inferring **dataflow dependency facts** (stratified Datalog) and checking patterns over the *data-flow graph*, not bytecode syntax.
- **Evidence:** stated key observation — syntactic/opcode-pattern tools yield false pos/neg; patterns must be on dataflow.
- **Limitations:** per-property soundness; EVM domain; not an impossibility result.
- **Overlap:** **the clearest published bytecode-analyzer articulation of C3's principle** (security over compiled bytecode must be decided on dataflow, not opcode syntax) — transplanted from EVM to MP-SPDZ tapes. A *design choice* there; a *soundness boundary* for us.

### C-9. Arzt, Rasthofer, Fritz, Bodden, Bartel, Klein, Le Traon, Octeau, McDaniel — FlowDroid (PLDI 2014)
[verify: https://dblp.org/rec/conf/pldi/ArztRFBBKTOM14.html]
- **Problem/method:** precise static **taint (dataflow) analysis** on compiled Dalvik bytecode, source→sink.
- **Evidence:** precision/recall on Android suites.
- **Limitations:** taint over/under-approximation; app-privacy domain.
- **Overlap:** representative shape for C4 (sink-vs-source dataflow on compiled bytecode) — the "dataflow-aware route" we advocate over opcode identity.

**Closest in C:** **Binsec/Rel 2020** and **ct-verif 2016** (leakage is relational/dataflow, so per-instruction syntax is the wrong tool — our exact structural argument, but as *positive CT tools* for timing, not a *negative* MPC boundary vs a source-controlling author) and **Securify 2018** (bytecode security must be decided on dataflow, not opcode syntax — same principle, EVM domain, framed as design not soundness limit).

---

## 6. Category D — Mutation testing for cryptographic / security software

*Finding: the intersection is small and emerging. The real cluster is "leaky
mutants as negative controls to evaluate a security **detector**," which is close
to our C5.*

### D1. DeMillo, Lipton, Sayward — Hints on Test Data Selection (IEEE Computer 1978)
[verify: https://gse.ufsc.br/bezerra/disciplinas/Confiabilidade/docs/demillo-mutants.pdf]
- **Method:** program mutation; the *coupling effect*.
- **Overlap:** foundational — mutants as a yardstick for a suite's discriminating power. Orthogonal to our security specifics.

### D2. Hamlet — Testing Programs with the Aid of a Compiler (IEEE TSE 1977)
[verify: https://ftp.math.utah.edu/pub/tex/bib/toc/ieeetranssoftweng1970.html — pub-page blocked; metadata via authoritative TSE ToC bibliography]
- **Method:** compiler-assisted seeded variants for test adequacy.
- **Overlap:** foundational; orthogonal.

### D3. Ami, Cooper, Kafle, Moran, Poshyvanyk, Nadkarni — Why Crypto-detectors Fail / MASC (IEEE S&P 2022) ★ CLOSEST
[verify: https://ieeexplore.ieee.org/document/9833582/ ; project https://amitsealami.com/MASC/ ; artifact https://github.com/Secure-Platforms-Lab-W-M/MASC-Artifact ; journal ext. arXiv https://arxiv.org/abs/2107.07065]
- **Problem/method:** evaluate crypto-API-misuse detectors by generating thousands of *compilable* leaky-crypto mutants (12 usage-based operators × 3 scopes) that a detector **must** flag; a *surviving* mutant exposes a flaw.
- **Evidence:** 9 detectors; 19 undocumented flaws; responsibly disclosed.
- **Limitations:** evaluates *third-party detectors* on an offline benchmark, not a project's own CI gate; Java crypto-API-misuse domain (not MPC leakage); no committed-in-repo controls; no adversarial reproduce-before-fix loop.
- **Overlap:** **directly overlaps C5's epistemics** (a check is trustworthy only if it kills deliberately-planted leaks). Orthogonal on domain, on *committed executable controls in a CI gate*, and on the adversarial loop. Our single strongest anchor citation for C5.

### D4. Loise, Devroey, Perrouin, Papadakis, Heymans — Towards Security-Aware Mutation Testing (Mutation 2017 @ ICST)
[verify: https://orbilu.uni.lu/handle/10993/29780 ; PDF https://orbilu.uni.lu/bitstream/10993/29780/1/Mutation2017-SecurityMutationOperators.pdf]
- **Method:** 15 **security mutation operators**, several crypto-weakening (DES/ECB/short keys/predictable PRNG/removed hostname verification); implemented in PIT.
- **Evidence:** proof-of-concept; fires on known anti-patterns.
- **Limitations:** operator catalog; small eval; not MPC; no gate.
- **Overlap:** supplies a *vocabulary of security-degrading mutations* (prior art for "leaking mutation"). Orthogonal on method (test-suite scoring, not committed controls).

### D5. Büchler, Oudinet, Pretschner — Security Mutants for Property-Based Testing (TAP 2011)
[verify: https://link.springer.com/chapter/10.1007/978-3-642-21768-5_6]
- **Method:** security mutation operators on *models*; a model checker confirms the mutant violates a property; counterexample → test.
- **Limitations:** model-level test *generation*, not committed program controls.
- **Overlap:** the "deliberately-broken variant as ground truth" idea, but as a test source. Orthogonal on mechanism.

### D6. Dadeau, Héam, Kheddam — Mutation-Based Test Generation from Security Protocols in HLPSL (ICST 2011)
[verify: INRIA CASSIS activity report https://radar.inria.fr/report/2012/cassis/bibliography.html ; STVR 2015 ext. DOI 10.1002/stvr.1531 (see §9)]
- **Method:** mutate HLPSL protocol specs to derive tests revealing injected weaknesses.
- **Limitations:** protocol-model mutation for test generation; not a conformance gate; not MPC.
- **Overlap:** closest prior art on "mutation testing of *protocol implementations*"; orthogonal on gate/controls and MPC setting.

### D7. Alalfi, Parveen, Nazzal — A Mutation Framework for Evaluating Security Analysis Tools in IoT (STVR 2022; arXiv 2110.05562, 2021) ★ CLOSE PARADIGM
[verify: https://arxiv.org/abs/2110.05562]
- **Method:** 13 operators inject vulnerabilities into benign SmartThings apps; a taint tool that detects "kills" the mutant; precision/recall quantify blind spots.
- **Evidence:** eval across 3 tools / 3 sensitivity dimensions.
- **Limitations:** IoT taint domain; evaluates external tools; no committed gate; no adversarial loop.
- **Overlap:** **same negative-control paradigm as C5**, different domain — evidence the paradigm generalizes.

### D8. (cross-ref) Frankencerts (B3) — adversarial negative-control *inputs* a validator must reject; the adversarial-artifacts lineage predating our program-level version.

**Closest in D:** **MASC / Ami 2022** (leaky mutants as detector negative controls — nearest match; gap = offline third-party-detector benchmark, not committed CI controls; crypto-API-misuse, not MPC; no adversarial loop) and **Alalfi 2022** (same paradigm, IoT taint). **No verified source combines** committed executable sibling-mutant controls **in a CI gate** + **MPC leakage** + **adversarial reproduce-before-fix** — the seam C5 occupies.

---

## 7. Category E — Reproducible / trustworthy security evidence

### E1. Torres-Arias, Afzali, Kuppusamy, Curtmola, Cappos — in-toto (USENIX Security 2019)
[verify: https://www.usenix.org/conference/usenixsecurity19/presentation/torres-arias]
- **Method:** signed layout of expected steps/functionaries/artifact hashes; signed per-step "link" metadata; verification chains hashes+signatures to the layout.
- **Evidence:** 30 historical compromises; production deployment (millions of users).
- **Limitations:** *trusts signed attestations* rather than independently recomputing an artifact from source; no per-case oracle verdict; no false-green protection.
- **Overlap:** overlaps our SHA-bound provenance (source-hash + who-ran-what) but **orthogonal to independent recomputation + oracle verdict** — in-toto attests, we recompute.

### E2. OpenSSF — SLSA specification (v1.2)
[verify: https://slsa.dev/ ; https://slsa.dev/spec/v1.2/ — primary artifact = versioned spec]
- **Method:** graded assurance via signed **provenance** from the build platform; higher levels demand tamper-resistant/hermetic builds.
- **Evidence:** cross-industry adoption; consumable provenance formats.
- **Limitations:** provenance signed by the *builder* (trust the platform), not verifier recomputation; no case-level oracle binding; no canary.
- **Overlap:** overlaps provenance discipline + "green check = evidence" ethos; orthogonal on verifier-recomputation and oracle-bound cases.

### E3. Newman, Meyers, Torres-Arias — Sigstore (ACM CCS 2022)
[verify: OpenAlex DOI metadata https://api.openalex.org/works/doi:10.1145/3548606.3560596 ; https://blog.sigstore.dev — pub-page blocked; metadata via OpenAlex/Crossref + official project]
- **Method:** keyless signing (Fulcio, short-lived OIDC certs) + **Rekor** append-only transparency log.
- **Evidence:** ecosystem-scale deployment (npm, PyPI, registries).
- **Limitations:** establishes who-signed-what + tamper-evidence; does not recompute signed content or evaluate correctness; a valid signature over a wrong artifact still verifies.
- **Overlap:** overlaps delivery-signature binding + tamper-evidence; orthogonal on recomputation + oracle verdict.

### E4. Lamb, Zacchiroli — Reproducible Builds: Increasing the Integrity of Software Supply Chains (IEEE Software 2022) ★ CLOSEST BY PRINCIPLE
[verify: title/authors https://arxiv.org/pdf/2104.06020 ; venue/DOI via official effort list https://reproducible-builds.org/docs/publications/ ; effort https://reproducible-builds.org — IEEE Xplore blocked; metadata via arXiv + official effort]
- **Method:** make builds **bit-for-bit deterministic** so an *independent* rebuilder recomputes the binary and checks **hash equality** — trust shifts from builder to recomputation.
- **Evidence:** ecosystem-scale deployment (Debian; the Reproducible Builds project).
- **Limitations:** whole-binary determinism at ecosystem scale; **no** per-case oracle verdict, no CI-vs-local provenance at record level, no pipefail canary.
- **Overlap:** **directly embodies our recompute-and-compare discipline** (recompute source hash + fresh compile, require equality). Our delta: applying recompute-equality to **per-case security-conformance evidence in CI**, plus oracle-bound cases, CI-bound provenance, and false-green canaries.

### E5. Fourné, Wermke, Enck, Fahl, Acar — On the Importance and Challenges of Reproducible Builds (IEEE S&P 2023)
[verify: authors' PDF https://marcelfourne.de/fourne-reproducible-builds-2023.pdf ; OpenAlex DOI https://api.openalex.org/works/doi:10.1109/SP46215.2023.10179320 — Xplore blocked; metadata via author PDF + OpenAlex]
- **Method:** 24 interviews; qualitative coding of adoption obstacles.
- **Limitations:** human-factors study; no mechanism.
- **Overlap:** orthogonal; motivational support for low-friction recomputable evidence.

### E6. ACM — Artifact Review and Badging v1.1 (2020)
[verify: https://www.acm.org/publications/policies/artifact-review-and-badging-current]
- **Method:** badges — Available; Evaluated (Functional/Reusable); Results Reproduced/Replicated.
- **Limitations:** one-time human judgment; not automated/per-run/tamper-evident/SHA-bound.
- **Overlap:** overlaps the *goal* of independent verification; orthogonal on our automated, continuous, recomputed CI mechanism.

### E7. USENIX Security — Call for Artifacts (’25)
[verify: https://www.usenix.org/conference/usenixsecurity25/call-for-artifacts]
- **Method:** mandatory Available + optional Functional/Reproduced evaluation in a security venue.
- **Limitations:** human, episodic, non-tamper-evident, not recomputed-in-CI.
- **Overlap:** independent-verification ethos in the security setting; orthogonal on mechanism.

**Closest in E:** **Reproducible Builds (Lamb & Zacchiroli 2022)** — the canonical recompute-equality principle; gap = whole-binary determinism, not per-case oracle-bound CI evidence — and **in-toto/SLSA** — provenance/attestation binding; gap = trust signed attestations vs verifier recomputation + oracle verdict.

---

## 8. Novelty matrix (our paper vs closest work)

Columns are properties of *our* paper. `Y` = present, `~` = partial/adjacent,
`—` = absent.

| Work | P1 indep-oracle conformance | P2 target = MPC *application* | P3 anti-echo interface | P4 opcode/bytecode leakage analysis | P5 demonstrates UNSOUNDNESS vs source-controlling author | P6 committed exec negative controls in CI | P7 recomputed SHA-bound per-case evidence | P8 conformance→proof hand-off |
|---|---|---|---|---|---|---|---|---|
| **Ours** | Y | Y | Y | Y | Y | Y | Y | Y |
| Kerschbaum 2013 (IFC type system) | — | ~ (secure comp., source) | — | — (source, not opcode) | — (positive, trusted compiler) | — | — | ~ |
| Frigate 2016 (validated MPC compiler) | ~ (self/differential) | ~ (compiler, not app) | — | — | — | — | — | — |
| Wys★ 2019 (verified MPC DSL) | — | ~ (DSL) | — | — | — | — | — | Y (formal) |
| ct-verif 2016 / Binsec-Rel 2020 | — | — (CT/timing) | — | Y (IR/binary) | ~ (relational, not adversary-source) | — | — | ~ |
| Securify 2018 (EVM bytecode) | — | — (smart contracts) | — | Y (dataflow) | ~ (design, not soundness limit) | — | — | — |
| Wycheproof (crypto vectors) | Y | — (primitives) | — (echoes expected) | — | — | ~ (vectors) | — | — |
| Frankencerts 2014 (differential) | — (N-version) | — (TLS certs) | — | — | — | ~ (adversarial inputs) | — | — |
| MASC/Ami 2022 (mutation eval) | — | — (crypto-API misuse) | — | — | — | ~ (mutants, offline) | — | — |
| Reproducible Builds 2022 | — | — | — | — | — | — | ~ (whole-binary) | — |
| in-toto 2019 / SLSA | — | — | — | — | — | — | ~ (attestation) | — |

**Reading of the matrix:** every column is covered by *some* prior work, but **no
single work covers our combination**, and several columns are only ever `~`
(partial) in prior work (P2 MPC-application target; P3 anti-echo; P5 unsoundness
vs a source-controlling author; P6 committed CI controls; P7 per-case recomputed
evidence). The paper's defensible position is the *intersection*, not any single
column.

## 9. Verdict

**Per-contribution (evidence-based):**

- **C1 methodology — `incremental`.** Independent-reference/pseudo-oracle testing
  is established (Barr 2015 taxonomy; Wycheproof for crypto primitives; Frigate
  for MPC compilers via differential testing). The genuine deltas are (i)
  targeting an MPC *application* against an independently-written plaintext oracle
  and (ii) the **anti-echo interface** (a real, small refinement addressing oracle
  contamination that Wycheproof-style vectors do not). Novel *combination*, not a
  new principle.
- **C2 artifact — `incremental` (engineering).** A reproducible conformance
  artifact with an adversarial sweep; standard in kind (cf. Csmith-style
  generators), valuable as evidence, not a research novelty by itself.
- **C3 boundary result — `incremental`, and this is the sharpest correction.** The
  *principle* that leakage is a relational/dataflow property and that per-instruction
  syntactic checks are unsound is **already established** — ct-verif (2-safety on
  IR), Binsec/Rel (relational CT at binary/opcode level, operand provenance not
  opcode identity), Securify (bytecode security must be decided on dataflow, not
  syntax). Our contribution is **not** that insight. It is (i) the **first concrete
  instantiation in the MPC-application delivery-certification setting** (MP-SPDZ
  tapes; `asm_open` masked-open ≡ raw-reveal), (ii) the specific **unforbiddable
  `call_tape`/`call_arg` channel** finding (a secret enters a subtape's open via
  the channel the honest comparison code uses), and (iii) a **reproduced bypass
  taxonomy against a source-controlling author** (a threat model the CT literature
  does not adopt — it assumes an honest developer and asks about timing). This is a
  real, publishable *domain instantiation + specific finding*, but it must be
  framed as such, not as a new principle. `[OPEN]` whether the specific
  MPC/`call_arg` unsoundness has been stated before in a crypto venue not reached
  by our search (§ residual gaps).
- **C4 hand-off — `incremental` (framing).** The two target properties are exactly
  what the formal-MPC literature provides (Wys★ / Verified SFE stack / EasyUC /
  Haagh / Butler). Articulating the hand-off from a conformance artifact to them is
  useful positioning, not a new result.
- **C5 review process — `incremental` (novel combination / experience).** The
  negative-controls-as-detector-validation paradigm exists (MASC 2022; Alalfi 2022;
  security mutation operators; frankencerts). The specific combination — *committed
  executable sibling-mutant controls wired into a CI conformance gate for an MPC
  leakage property* + an *adversarial reproduce-before-fix loop* — is not present
  in the verified literature.

**Overall verdict: `incremental`.**
- **Not `duplicated`:** no single verified work does executable independent-oracle
  conformance of an MPC application + an opcode-level unsoundness demonstration vs a
  source-controlling author + the hand-off articulation. The matrix (§8) shows the
  combination is unique.
- **Not `novel` (in the strong sense):** no contribution is a new principle or
  theorem; each is a novel *combination* or *domain instantiation* of established
  ideas. The boundary result in particular re-derives, in the MPC-application
  setting, a dataflow-vs-syntax principle already established for constant-time and
  smart-contract bytecode.
- **Not `unclear`:** the positioning is well-supported by the primary sources
  above.
- **Publishability read:** defensible as a **methodology / experience / negative-
  result paper** at a PL-security or systematization/experience venue (PLAS-style),
  **conditioned on** the reframing in §10. Overclaiming C3 as a new insight, or C1
  as a new methodology, would not survive review by anyone who knows the CT-verification
  or oracle-problem literature.

## 10. Required changes to thesis / RQs / contributions / title (recommendations only — manuscript NOT edited)

1. **Related Work (must add).** Cite and engage: ct-verif (USENIX Sec 2016),
   Binsec/Rel (S&P 2020), Securify (CCS 2018) as establishing "leakage is
   dataflow, not opcode identity"; Kerschbaum (ASIACCS 2013) as the positive
   source-level IFC counterpart; Barr et al. (TSE 2015) + Wycheproof for the oracle
   / conformance framing; MASC/Ami (S&P 2022) + Alalfi (STVR 2022) for negative
   controls; Reproducible Builds (2022) + in-toto (2019)/SLSA for evidence.
   The manuscript's Related Work `[OPEN]` placeholders should be resolved with
   these.
2. **Contribution C3 (reword — do not delete).** Reframe from "static opcode-level
   inspection is unsound" to "**the first concrete demonstration, in the
   MPC-application delivery-certification setting, that** opcode-level inspection is
   unsound against a source-controlling author, **instantiating the
   dataflow-not-syntax principle of ct-verif/Binsec-Rel/Securify** and adding the
   specific `call_tape`/`call_arg` unforbiddable-channel finding." Explicitly credit
   the prior principle. (Do this in the next revision, not now.)
3. **Contribution C1 (reword).** Claim the *delta* (MPC-application target +
   anti-echo interface) over established independent-oracle/conformance testing,
   not a new methodology.
4. **RQ2 (narrow).** As written ("Can static opcode-level inspection soundly
   certify non-leakage…") the *general* form is largely answered by the CT
   literature. Narrow to: "**In the MPC-application setting, through which specific
   compiled channels does opcode-level certification fail against a
   source-controlling author, and is the failure structural (unforbiddable) rather
   than a patchable omission?**" — which is what our taxonomy actually answers.
5. **RQ1 / RQ3 / RQ4 — keep**, but RQ1 should reference the oracle-problem taxonomy
   (pseudo-oracle) so the framing is grounded.
6. **Title — optional.** Consider signaling scope, e.g. add "a case study" or
   "an experience report," so reviewers read it as methodology + boundary-finding
   rather than a new-technique claim. Current title is acceptable if the abstract
   makes the incremental framing explicit.
7. **Thesis — keep, with one hedge.** The one-sentence thesis is defensible as a
   *scoped* claim, but the surrounding text must not imply the dataflow boundary is
   newly discovered here; attribute the principle and claim the MPC instantiation.
8. **Do NOT weaken the honest scoping already present** (empirical-not-theorem for
   the boundary; Conjecture 1 with obligations). That scoping is corroborated by
   this review and is a strength.

## 11. `[OPEN]` items and residual search gaps

- **[OPEN] Negation coverage.** IACR ePrint and Google/Semantic Scholar were not
  directly fetchable, so the claim "no prior work states the specific
  MPC/`call_arg` opcode-ambiguity unsoundness" is **not fully verified**. A
  targeted ePrint + Scholar sweep ("MP-SPDZ leakage static", "secure computation
  compiler information flow bytecode", "reveal opcode masked open MPC") is required
  before C3's specific-finding novelty is asserted un-hedged.
- **[OPEN] MP-SPDZ-specific tooling.** No verified source surfaced a published
  static leakage checker specific to MP-SPDZ tapes; absence here is *not* proof of
  absence. Check the MP-SPDZ papers/repo and any follow-ups.
- **[OPEN] Publisher-page confirmations.** Entries tagged *[pub-page blocked]*
  (Jasmin CCS'17; Verified SFE Stack CCS'17; Kerschbaum ASIACCS'13; Binsec/Rel;
  System-level NI CCS'14; Securify; Hamlet TSE'77; Sigstore CCS'22; Reproducible
  Builds IEEE SW'22; Fourné S&P'23) are metadata-confirmed via dblp/OpenAlex/author
  PDFs/official program pages but not fetched from the publisher; treat as verified
  primary sources with that transparency caveat.
- **[OPEN] Wycheproof citation.** No peer-reviewed paper exists; cite the
  repository (with commit) if a venue requires a formal reference.
- **[OPEN] Journal extensions not fully fetched:** MASC→ACM TOPS (DOI
  10.1145/3796221) and Dadeau→STVR 2015 (DOI 10.1002/stvr.1531) — cite the
  conference versions as primary.
- **[OPEN] Deliberately excluded but real** (add if breadth wanted): FaCT (PLDI
  2019), Constant-Time Foundations for the New Spectre Era (PLDI 2020), Oyente (CCS
  2016).

---

## Sources (verifying URLs)

Grouped as cited above. Each was fetched or (where a publisher page bot-blocked
the fetcher) confirmed via the authoritative bibliographic record noted inline.

- Wysteria — https://www.microsoft.com/en-us/research/publication/wysteria-programming-language-generic-mixed-mode-multiparty-computations/
- Wys★ — https://www.microsoft.com/en-us/research/publication/wys-a-dsl-for-verified-secure-multi-party-computations/ · https://arxiv.org/abs/1711.06467
- Symphony — https://programming-journal.org/2023/7/14/
- Verified SFE Stack (CCS'17) — https://acmccs.github.io/topic-22/
- Butler, Isabelle (ITP'17) — https://arxiv.org/abs/1805.12482
- Haagh et al. (CSF'18) — https://arxiv.org/abs/1806.07197
- EasyUC (CSF'19) — https://open.bu.edu/handle/2144/40575
- Frigate (EuroS&P'16) — https://www.ieee-security.org/TC/EuroSP2016/preliminary-papers.php
- Kerschbaum (ASIACCS'13) — https://dblp.org/rec/conf/ccs/Kerschbaum13.html
- McKeeman (1998) — https://dblp.org/rec/journals/dtj/McKeeman98.html
- Csmith (PLDI'11) — https://www.flux.utah.edu/paper/yang-pldi11
- Frankencerts (S&P'14) — https://www.cs.columbia.edu/~suman/docs/frankencert.pdf
- Mucert (ESEC/FSE'15) — https://dblp.org/rec/conf/sigsoft/ChenS15.html
- NEZHA (S&P'17) — https://dblp.org/rec/conf/sp/PetsiosTSKJ17.html
- Wycheproof — https://github.com/C2SP/wycheproof
- Metamorphic testing survey (TSE'16) — http://eprints.whiterose.ac.uk/110335/
- Oracle problem survey (TSE'15) — https://discovery.ucl.ac.uk/1471263/
- CompCert (CACM'09) — https://dblp.org/rec/journals/cacm/Leroy09.html
- Secure compilation survey (CSUR'19) — https://dblp.org/rec/journals/csur/PatrignaniAC19.html
- Jasmin (CCS'17) — https://dblp.org/rec/conf/ccs/AlmeidaBBBGLOPS17.html
- CT-preserving compiler (POPL'20) — https://dblp.org/rec/journals/pacmpl/BartheBGHLPT20.html
- ct-verif (USENIX Sec'16) — https://www.usenix.org/conference/usenixsecurity16/technical-sessions/presentation/almeida
- Binsec/Rel (S&P'20) — https://dblp.org/rec/conf/sp/DanielBR20.html · https://arxiv.org/abs/1912.08788
- System-level NI (CCS'14) — https://dblp.org/rec/conf/ccs/BartheBCLP14.html
- Securify (CCS'18) — https://dblp.org/rec/conf/ccs/TsankovDDGBV18.html · https://ar5iv.labs.arxiv.org/html/1806.01143
- FlowDroid (PLDI'14) — https://dblp.org/rec/conf/pldi/ArztRFBBKTOM14.html
- DeMillo/Lipton/Sayward (1978) — https://gse.ufsc.br/bezerra/disciplinas/Confiabilidade/docs/demillo-mutants.pdf
- Hamlet (TSE'77) — https://ftp.math.utah.edu/pub/tex/bib/toc/ieeetranssoftweng1970.html
- MASC / Why Crypto-detectors Fail (S&P'22) — https://ieeexplore.ieee.org/document/9833582/ · https://amitsealami.com/MASC/ · https://arxiv.org/abs/2107.07065
- Security-Aware Mutation (Mutation'17) — https://orbilu.uni.lu/handle/10993/29780
- Security Mutants for PBT (TAP'11) — https://link.springer.com/chapter/10.1007/978-3-642-21768-5_6
- Dadeau et al. (ICST'11) — https://radar.inria.fr/report/2012/cassis/bibliography.html
- Alalfi et al. (STVR'22 / arXiv'21) — https://arxiv.org/abs/2110.05562
- in-toto (USENIX Sec'19) — https://www.usenix.org/conference/usenixsecurity19/presentation/torres-arias
- SLSA — https://slsa.dev/spec/v1.2/
- Sigstore (CCS'22) — https://api.openalex.org/works/doi:10.1145/3548606.3560596
- Reproducible Builds (IEEE SW'22) — https://arxiv.org/pdf/2104.06020 · https://reproducible-builds.org/docs/publications/
- Fourné et al. (S&P'23) — https://marcelfourne.de/fourne-reproducible-builds-2023.pdf
- ACM Artifact Badging — https://www.acm.org/publications/policies/artifact-review-and-badging-current
- USENIX Security Call for Artifacts — https://www.usenix.org/conference/usenixsecurity25/call-for-artifacts
