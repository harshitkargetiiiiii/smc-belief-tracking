# Submission Hardening Gate — verdict

**Candidate:** `paper/manuscript-integration` @ `4081a95` (self-contained; frozen
artifact byte-identical to `305a3a8`). Six audits run; no manuscript edits, no checker
changes, no new experiments beyond reproduction. Companion reports in this directory:
`CLAIM_EVIDENCE_AUDIT.md`, `CITATION_AUDIT.md`, `CONSISTENCY_AUDIT.md`,
`PACKAGING_AUDIT.md`, `CLEANLINESS_AUDIT.md`, `REVIEWER2_MEMO.md`.

## Verdict: **MINOR REVISION** (packaging/wording only) — with a venue-fit caveat

The candidate is **scientifically clean and reproduces end-to-end**: both `reproduce.sh`
scripts exit 0 from a fresh clone, the PDF builds to 11 pp with no undefined
refs/citations, every repeated number is internally consistent and matches a live
re-derivation, and **no unsupported claim or over-strong wording was found**. What
stands between it and submission is a short list of **placeholder / citation / anonymity
/ packaging** fixes — **none requires new research**.

**Caveat (not a gate defect):** the hostile Reviewer #2 memo leans **reject** for a
*top-tier security main track*, on novelty and "no privacy result at a privacy venue
under a deliberately bounded build-time adversary." Those are **venue-fit** judgments,
addressed by venue choice + the paper's existing honest framing, **not** by editing the
manuscript. See "Venue fit" below.

## Blockers (must fix before any submission; all wording/packaging)

1. **`\open{author metadata}` placeholder** renders as red `[OPEN: …]` in the PDF
   (`main.tex:40`). — *CLEANLINESS CL1*
2. **`\open{confirm pages}` placeholder** in the Keller bibitem renders red
   (`main.tex:647`); fill CCS 2020 **pp. 1575–1590** (verify on ACM DL
   `10.1145/3372297.3417872`). — *CLEANLINESS CL2 / CITATION*
3. **Citation venue error:** `skalkanear2` is cited as "FASE/ETAPS, 2025"; authoritative
   sources place *SMT-Boosted Security Types for Low-Level MPC* at **ESOP 2025** (ETAPS,
   Springer LNCS 15695; arXiv:2501.17824). Verify and correct FASE → ESOP. — *CITATION*

## Must-fix if the target venue is **double-blind** (else: polish)

4. **De-anonymize** the author block (`\author{Harshit Kargeti…}`, `main.tex:39`). — *CL3*
5. **Neutralize internal artifacts that print in the PDF:** 16 `R-xx` review-log IDs and
   34 `\repo{}` gray pointers to repo paths. Convert to a single anonymous
   artifact-availability footnote/appendix. — *CL4/CL5*
6. **Remove the source comment** naming *Codex* + an internal PR number (`main.tex:5`)
   before releasing the `.tex`. — *CL6*

## Worthwhile but optional (improve reviewer experience / camera-ready)

- Add a **paper-root README** naming the two reproduction entry points and their
  prerequisites (MP-SPDZ pin, network to `data61/MP-SPDZ`, git-clone-with-tags,
  OpenSSL, localhost sockets). — *PACKAGING a*
- Make reproduction survive a **ZIP/tarball export** (the scripts currently `git worktree
  add` a tag and fail closed without `.git`), or document "reproduce from a git clone
  only." — *PACKAGING b*
- Add **real citations** for works currently referenced only via `\repo{}`/prose
  (Wys★, verified SFE, EasyUC, Wycheproof, in-toto/SLSA) and for the MP-SPDZ
  `call_tape`/`call_arg` opcode fact. — *CITATION §4*
- Cosmetic: "117 **collected** (all pass)"; optional in-text note that the v0.4.3
  cross-version result is archived evidence (already hedged to "two versions").

## New research vs wording/packaging

- **Wording/packaging only (no experiments):** *every* blocker and must-fix above, plus
  all optional items. The scientific content needs **no** change.
- **Would require new research (explicitly NOT done here, and NOT required to submit):**
  a genuine **operand-sensitive dataflow delivery checker** ("E3"). It is the single
  highest-leverage item to convert the negative boundary result into a positive
  contribution and to blunt Reviewer #2's novelty/thin-finding objections — but it is
  out of scope by this run's hard rules and is a **strategic contribution decision**, not
  a gate-mandated fix.

## Should the scientific baseline remain frozen?

**Yes.** Reproduction passed end-to-end; no audit surfaced a scientific defect,
contradiction, unsupported claim, or stale number. Nothing motivates touching
`conformance/`, `delivery_inspect.py`, or the frozen artifact. **Keep the baseline
frozen at `305a3a8`.**

## Does any finding justify reopening E3 or Sigma_T?

**No.** No reproduction failure, inconsistency, or unsupported claim emerged that forces
new work. E3 remains an *optional* strengthening (relevant only if aiming at a top-tier
novelty-expecting track); `Sigma_T` is unrelated to any finding. **Neither should be
reopened on the strength of this gate.**

## Venue fit (from the Reviewer #2 memo — decision for the author/Codex)

- The paper is honestly a **single-application experience report / case study** with a
  **negative** headline result (an opcode-identity delivery linter can't be a general
  non-leakage checker) plus one **source-realizable structural false-accept** (H-R2).
- At a **top-tier security main track** (S&P/USENIX/CCS), Reviewer #2's novelty and
  "no privacy result / artificial adversary" objections are **fatal-if-true** and the
  minor fixes above **will not** move them.
- **Better-fit targets** where this is a minor-revision-ready contribution: an
  **experience/SoK/artifact track**, a **PL-or-SE-security venue** valuing reproducible
  negative results and conformance methodology, or a **PoPETs-style systematization**.
  This is a **targeting** decision, not a manuscript defect.

## Bottom line

Fix the **3 blockers** (2 placeholders + 1 citation venue), decide **double-blind vs
single-blind** (drives items 4–6), pick a **venue that fits an experience report**, and
the candidate is submittable. Keep the baseline **frozen**; do **not** reopen E3 or
`Sigma_T` on this gate.
