# Citation & Bibliography Audit — `paper/main.tex`

**Scope.** Bibliography of `paper/main.tex` (`\thebibliography`, lines 645–657; 11 `\bibitem`s), plus in-text `\cite{}`/`\repo{}` usage, un-cited claims, and novelty framing in the abstract / intro / Related Work (`sec:related`). The manuscript was **not** modified. Positioning context read from `paper/LITERATURE_REVIEW.md`.

**Method.** Each entry checked against an authoritative record (publisher page, USENIX/ACM/IEEE proceedings, Springer/OAPEN, arXiv, or the paper's own hosted page). DBLP's JSON API was robots-blocked from the fetcher, so DBLP was reached indirectly via search-surfaced records; primary publisher/venue pages were used for the load-bearing checks.

---

## 1. Per-reference verification table

| key | as-written (authors / title / venue / year) | authoritative check + source URL | verdict | note |
|---|---|---|---|---|
| `plas2012` | P. Mardziel, M. Hicks, J. Katz, M. Srivatsa. *Knowledge-Oriented Secure Multiparty Computation.* PLAS, 2012. | Confirmed verbatim: Piotr Mardziel, Michael Hicks, Jonathan Katz, Mudhakar Srivatsa; *Knowledge-Oriented Secure Multiparty Computation*; ACM SIGPLAN Workshop on Programming Languages and Analysis for Security (PLAS); 2012. https://mhicks.me/papers/mardziel12smc.html | **OK** | Authors/title/venue/year all correct. |
| `keller2020mpspdz` | M. Keller. *MP-SPDZ: A Versatile Framework for Multi-Party Computation.* ACM CCS, 2020. IACR ePrint 2020/521. `\open{confirm pages}` | Confirmed: CCS '20, ACM, 2020, **pp. 1575–1590**; ePrint 2020/521 correct. https://dl.acm.org/doi/10.1145/3372297.3417872 · https://researchr.org/publication/Keller20-0/bibliographies · https://eprint.iacr.org/2020/521 | **ISSUE** | Bibliographic facts correct, but the entry still carries an unresolved `\open{confirm pages}` placeholder. Pages = **1575–1590**. |
| `ctverif` | J. B. Almeida, M. Barbosa, G. Barthe, F. Dupressoir, M. Emmi. *Verifying Constant-Time Implementations.* USENIX Security, 2016. | Confirmed: 5 authors as listed; USENIX Security Symposium 2016. https://www.usenix.org/conference/usenixsecurity16/technical-sessions/presentation/almeida | **OK** | Complete and correct. |
| `binsecrel` | L.-A. Daniel, S. Bardin, T. Rezk. *Binsec/Rel: Efficient Relational Symbolic Execution for Constant-Time at Binary Level.* IEEE S&P, 2020. | Confirmed authors/venue/year; official title is "…at Binary-**Level**" (hyphenated). https://dblp.org/rec/conf/sp/DanielBR20.html · https://arxiv.org/abs/1912.08788 | **OK** (minor) | Only deviation is "Binary Level" vs official hyphenated "Binary-Level". Cosmetic. |
| `securify` | P. Tsankov et al. *Securify: Practical Security Analysis of Smart Contracts.* ACM CCS, 2018. | Confirmed: Tsankov, Dan, Drachsler-Cohen, Gervais, Bünzli, Vechev; CCS 2018. https://dl.acm.org/doi/10.1145/3243734.3243780 · https://dblp.org/rec/conf/ccs/TsankovDDGBV18.html | **OK** | "et al." acceptable; venue/year correct. |
| `kerschbaum` | F. Kerschbaum. *An Information-Flow Type-System for Mixed Protocol Secure Computation.* ACM ASIACCS, 2013. | Confirmed: appears in *Proc. 8th ACM SIGSAC Symposium on Information, Computer and Communications Security* = **ASIACCS 2013**. (DBLP files ASIACCS under its `conf/ccs` branch — the suspicious-looking key in the lit review is not an error.) https://dl.acm.org/doi/10.1145/2484313.2484364 · https://dblp.org/db/conf/ccs/asiaccs2013.html | **OK** | Venue genuinely ASIACCS 2013; title matches. |
| `skalkanear` | C. Skalka, J. P. Near. *Language-Based Security for Low-Level MPC.* PPDP, 2024. arXiv:2407.16504. | Confirmed: PPDP 2024 (26th Int. Symp. on Principles and Practice of Declarative Programming), DOI 10.1145/3678232.3678246; arXiv 2407.16504. https://dl.acm.org/doi/10.1145/3678232.3678246 · https://arxiv.org/abs/2407.16504 | **OK** | Complete and correct. |
| `skalkanear2` | C. Skalka, J. P. Near. *SMT-Boosted Security Types for Low-Level MPC.* **FASE/ETAPS, 2025.** arXiv:2501.17824. | Title/authors/arXiv correct, but the venue is wrong: Springer vol. 978-3-031-91121-7 (LNCS 15695), chapter _11, pp. 258–285, is **ESOP 2025** (34th European Symposium on Programming), **not FASE**. Both are ETAPS 2025 but distinct conferences. https://link.springer.com/chapter/10.1007/978-3-031-91121-7_11 · https://link.springer.com/book/10.1007/978-3-031-91121-7 · https://library.oapen.org/bitstream/handle/20.500.12657/101667/1/9783031911217.pdf | **ISSUE** | **Wrong venue.** Should read "ESOP/ETAPS 2025" (European Symposium on Programming), pp. 258–285. The `LITERATURE_REVIEW.md` Track B mislabel (FASE) was propagated into the bibliography. |
| `oracleproblem` | E. T. Barr, M. Harman, P. McMinn, M. Shahbaz, S. Yoo. *The Oracle Problem in Software Testing: A Survey.* IEEE TSE, 2015. | Confirmed: IEEE TSE vol. 41(5), 2015, DOI 10.1109/TSE.2014.2372785. https://dl.acm.org/doi/10.1109/TSE.2014.2372785 · https://discovery.ucl.ac.uk/1471263/ | **OK** | Complete and correct (DOI year-stamp 2014 = early access; issue is 2015). |
| `masc` | A. S. Ami, N. Cooper, K. Kafle, K. Moran, D. Poshyvanyk, A. Nadkarni. *Why Crypto-detectors Fail: A Systematic Evaluation of Cryptographic Misuse Detection Techniques.* IEEE S&P, 2022. | Confirmed: 6 authors as listed; IEEE S&P 2022. https://par.nsf.gov/biblio/10334397 · https://amitsealami.com/MASC/ | **OK** | Complete and correct. |
| `reprobuilds` | C. Lamb, S. Zacchiroli. *Reproducible Builds: Increasing the Integrity of Software Supply Chains.* IEEE Software, 2022. | Confirmed: IEEE Software vol. 39(2), 2022. https://www.computer.org/csdl/magazine/so/5555/01/09403390 · https://arxiv.org/abs/2104.06020 | **OK** | Correct (early-access 2021; canonical issue 2022 — cite as 2022 is right). |

---

## 2. Placeholders & incomplete fields

| location | marker | status |
|---|---|---|
| line 647 (`keller2020mpspdz` bibitem) | `\open{confirm pages}` | **Unresolved.** Renders as red `[OPEN: confirm pages]` in the references. Pages are **1575–1590** (CCS '20). |
| line 39–40 (author `\thanks` footnote) | `\open{author metadata}` — "Author list, affiliations, and acknowledgments" | **Unresolved.** Renders as red `[OPEN: author metadata]` in the author block. (Author is named "Harshit Kargeti"; affiliations/acknowledgments still stubbed.) |

No `TODO`/`XXX`/`FIXME` markers found. No other `\open{}` in the bibliography. The header comment (line 7) documents `\open{}` as the deliberate "unsupported item" flag, so both above are intentional stubs that must be filled before submission.

---

## 3. Duplicates / uncited bibitems / cited-but-missing

- **Duplicates:** none. All 11 `\bibitem` keys are distinct. `skalkanear` (PPDP 2024) and `skalkanear2` (ESOP 2025) are two genuinely different papers, not a duplicate.
- **Bibitems never `\cite{}`d:** none. All 11 keys are cited in the body:
  `plas2012` (L142), `keller2020mpspdz` (L87, L159), `ctverif` (L510), `binsecrel` (L512), `securify` (L514), `kerschbaum` (L520), `skalkanear`+`skalkanear2` (L523), `oracleproblem` (L533), `masc` (L536), `reprobuilds` (L538).
- **`\cite{}` with no matching bibitem (undefined citation):** none. Every cited key resolves to a `\bibitem`.

The `\cite{}`/`\bibitem` sets match exactly (11 = 11), so there are no LaTeX "undefined citation" or "uncited entry" defects.

---

## 4. Statements needing citations

The manuscript uses a lightweight `\repo{...}` gray-text pointer convention for repository artifacts, and in Related Work it points several *named prior works* to `LITERATURE_REVIEW.md` via `\repo{}` instead of giving them real `\bibitem` entries. The following are factual/technical claims about specific prior work (or documented third-party behavior) that name a source but carry **no formal citation**:

1. **Named MPC verification works with no `\bibitem`** — `sec:related`, lines 528–530:
   > "Verified MPC stacks and mechanized simulation proofs (Wys$^\star$, verified SFE, EasyUC, replicated-secret-sharing proofs) are the protocol-level targets our hand-off … defers to~\repo{LITERATURE\_REVIEW.md §3}."
   Wys★ (Rastogi–Swamy–Hicks 2019), verified SFE (Almeida et al., CCS 2017), EasyUC (Canetti–Stoughton–Varia, CSF 2019), and the replicated-SS proofs (Haagh et al., CSF 2018) are named as specific results but only `\repo{}`-pointed to the internal review file. These should be proper citations.

2. **Wycheproof** — `sec:related`, lines 534–535:
   > "Wycheproof applies reference-oracle conformance to crypto *primitives* (feeding expected outputs, the opposite of our anti-echo design)~\repo{LITERATURE\_REVIEW.md §4}."
   Named prior artifact, `\repo{}`-only. `LITERATURE_REVIEW.md` §11 itself notes there is no peer-reviewed paper and recommends citing the repository (with commit) — currently no such reference exists.

3. **in-toto / SLSA** — `sec:related`, lines 538–540:
   > "Reproducible Builds~\cite{reprobuilds} and in-toto/SLSA are the evidence-discipline neighbours…"
   in-toto (Torres-Arias et al., USENIX Security 2019) and SLSA (OpenSSF spec) are named inline with **no citation and no `\repo{}` pointer at all** — the weakest-supported of the four.

4. **MP-SPDZ instruction-set semantics** — `sec:background`, lines 160–161:
   > "a value in one tape reaches another only through memory or through register arguments passed by `call_tape` (opcode 0xec) and received by `call_arg` (opcode 0xed); a cross-tape register reference is a compiler error~\repo{MP-SPDZ docs: instructions.html}."
   A load-bearing technical claim about MP-SPDZ's documented opcode behavior, supported only by a `\repo{}` gray pointer. `LITERATURE_REVIEW.md` §12 explicitly recommends a formal citation to the MP-SPDZ docs (`instructions.html`) for the `call_tape`/`call_arg` (0xec/0xed) mechanism.

*Lower-priority (abstract-level factual claim, substantiated later in `sec:related`, so acceptable but worth noting):* abstract lines 76–78, "that leakage is a dataflow rather than opcode-identity property is established for constant-time and smart-contract bytecode analysis" — no inline cite in the abstract; the supporting `\cite{ctverif,binsecrel,securify}` appear only in Related Work.

---

## 5. Novelty-overstatement check

**Overall: the manuscript does *not* overstate novelty.** Its framing is consistently and explicitly "incremental / instantiation, not a new principle," and it credits each of the six reference points (Skalka & Near, ct-verif, Binsec/Rel, Securify, Keller/MP-SPDZ, PLAS 2012) as prior/established. Representative hedges that match the intended stance:

- Abstract, L75–78: "We do **not** claim this principle is new --- that leakage is a dataflow rather than opcode-identity property is established for constant-time and smart-contract bytecode analysis; our contribution is the MPC-application instantiation, the pinned-backend mechanism, and a reproducible mutation study."
- Intro, L96–104: "It is **not** 'the first implementation of PLAS belief tracking' … It is also **not** a new analysis *technique*: the principle … is prior art."
- `sec:related`, L514–516: "Our §b6 instantiates this principle in the MPC-application setting; **we claim the instantiation and the pinned-backend mechanism, not the principle**."
- `sec:related`, L523–527: Skalka & Near framed as "**Closest to our finding** … the positive dual of our negative case-study observation" — correct, non-competitive positioning.
- `sec:boundary`, L447–449: "**General prior principle (not novel here)**: information-flow safety depends on dataflow and semantics, not opcode names."

**Only borderline wording (minor, non-blocking):**
- Contributions, L128: "adds the **decisive new result** --- a source-realizable structural false accept (H-R2)." The phrase "decisive new result" is the strongest novelty language in the paper. It refers to the authors' own held-out empirical finding (H-R2), *not* to a new principle or a "first vs. prior work" claim, so it does not contradict the incremental stance — but "decisive" is a strong descriptor a reviewer may ask to soften. (Cf. also "the decisive result concerns delivery structure," L420.)

No instance was found where the abstract, intro, or Related Work claims priority/first-ness or a new principle over the six named works. The paper is, if anything, more conservative than `LITERATURE_REVIEW.md` §10 (which suggested "first concrete instantiation…" language the manuscript declined to adopt).

---

## 6. Summary

**Submission-blocking (3):**
1. `skalkanear2` — **wrong venue**: "FASE/ETAPS, 2025" is incorrect; the paper is in **ESOP 2025** (European Symposium on Programming), LNCS 15695, pp. 258–285. Factual error in the references.
2. `keller2020mpspdz` — unresolved **`\open{confirm pages}`** placeholder in the bibliography (fill in **pp. 1575–1590**).
3. Author block — unresolved **`\open{author metadata}`** placeholder (affiliations/acknowledgments); prints as a visible `[OPEN: …]` marker.

**Non-blocking (recommended):**
- `binsecrel` — cosmetic title fix "Binary Level" → "Binary-Level".
- Named related works lacking formal citations: Wys★, verified SFE, EasyUC, replicated-SS proofs, Wycheproof (`\repo{}`-only) and in-toto/SLSA (no pointer) — add proper references.
- MP-SPDZ `call_tape`/`call_arg` (0xec/0xed) opcode claim — promote from `\repo{}` pointer to a formal citation of the MP-SPDZ documentation.
- Novelty wording "decisive new result" (L128) — optionally soften.

**Count:** 11 references checked → 9 OK (2 with cosmetic/notes) · 2 with issues (1 wrong venue, 1 placeholder) · +1 placeholder in the author block · 0 duplicates · 0 uncited bibitems · 0 undefined citations · 4 citation-gap clusters · 0 genuine novelty overstatements (1 borderline phrase). **Blocking: 3 · Non-blocking: 4.**
