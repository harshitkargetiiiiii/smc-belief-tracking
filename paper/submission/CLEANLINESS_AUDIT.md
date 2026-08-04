# Submission cleanliness + anonymity audit (audit 5)

Searched `paper/main.tex` (the submitted artifact → PDF) and `paper/EXTERNAL_REVIEW_BRIEF.md`
(review-facing, not submitted). Flags only — **no edits made**, and per the hard rules
the AI-assistance disclosure is preserved, not stripped.

## Blocking (renders in the PDF / must resolve before submission)

| # | Item | Location | Why it blocks |
|---|---|---|---|
| CL1 | `\open{author metadata}` | `main.tex:40` | Renders as red **[OPEN: author metadata]** in the PDF; a visible placeholder. |
| CL2 | `\open{confirm pages}` | `main.tex:647` (Keller bibitem) | Renders as red **[OPEN: confirm pages]**; unresolved citation field (see CITATION_AUDIT — CCS 2020 pp. 1575–1590). |

## Anonymity (venue-dependent — blocking iff the venue is double-blind)

| # | Item | Location | Note |
|---|---|---|---|
| CL3 | `\author{Harshit Kargeti…}` (real name + `\thanks`) | `main.tex:39` | De-anonymize for a double-blind venue; fine for single-blind. |
| CL4 | **16 internal review IDs `R-xx`** (R-10…R-45) inside `\repo{}` annotations | throughout `main.tex` | Reveal an internal review-log process; appear in the PDF as gray "[ docs/review-log.md R-41 ]". Not identity per se, but internal and unusual for a camera-ready. |
| CL5 | **34 `\repo{}` gray pointers** to repo paths (`conformance/…`, `docs/…`, `paper/…`) | throughout `main.tex` | Expose the repository layout; for a double-blind submission the repo must be anonymized anyway (anonymous artifact). Consider consolidating into one artifact-availability footnote/appendix. |

## Source-only (not in the PDF; matters if the `.tex` source is shared)

| # | Item | Location | Note |
|---|---|---|---|
| CL6 | Comment naming **Codex** + an internal PR-review number | `main.tex:5` (`% CONSOLIDATED REVISION (responds to … Codex PR review #4848189566)`) | LaTeX comment — invisible in the PDF, but present in source. Remove before releasing `.tex`. |
| CL7 | Comment describing the `\open{…}` convention | `main.tex:7` | Harmless; remove with CL6 during source cleanup. |

## Present-and-intentional (do NOT remove without a venue reason)

- **AI-assistance disclosure** — `main.tex:39–43` (`\thanks`) and §Threats
  (`main.tex:550–552`, "Correlated authorship and AI assistance"). This is a deliberate
  scientific-integrity disclosure. Keep it; a double-blind venue may require rephrasing
  to a non-identifying form, but the disclosure itself should remain in the record.
- **"Privacy proof" / "non-leakage guarantee" wording** — title (`main.tex:36`, "Where
  It Stops Short of a Privacy Proof"), §5 hand-off, §5 layered account. These are the
  paper **disclaiming** such guarantees, not asserting them. **Correct; no action.**

## Explicit negative checks (searched, none found)

- No `E3` reference in `main.tex`. `\Sigma_T` appears once as a scope/out-of-scope
  statement (intentional).
- No `2/3`, `10/12`, `0.67`, `0.83`, or "detection rate"-as-metric remnants.
- No claim that **H-O3** is an executable attack (always "synthetic / manifest-level /
  rule-gap").
- No claim that the runtime layer catches **H-R2**-style permutations **in general**
  (the text explicitly says "for that concrete build" and "we do not claim … in
  general").
- No `github.com` URL, GitHub username, or absolute local path (`/home/…`, `/Users/…`,
  `/tmp/…`) in `main.tex`. (`EXTERNAL_REVIEW_BRIEF.md` uses `.github/` as a *path*, not a
  URL, and references `Codex-reviewed`/`305a3a8` — acceptable in a review-facing doc, but
  see CL8.)

## Review-facing file note

- CL8: `EXTERNAL_REVIEW_BRIEF.md` names "Codex-reviewed" (line 9). The brief is not the
  submitted paper; harmless for the artifact/reviewer packet, but if the brief ships with
  a double-blind artifact it should be de-identified too.

## Summary

- **2 blocking placeholders** (CL1, CL2) that render in the PDF — must fix regardless of
  venue.
- **Anonymity/presentation cleanup** (CL3–CL5) — blocking **only** for a double-blind
  venue; otherwise a polish item (the 16 `R-xx` IDs + 34 `\repo{}` pointers are the main
  camera-ready-style concern).
- **Source hygiene** (CL6–CL7) — remove the Codex/PR comment before releasing `.tex`.
- **No stale experimental language, no E3, no detector-rate remnants, no H-O3/H-R2
  overclaim, no simulation-security overclaim.**
