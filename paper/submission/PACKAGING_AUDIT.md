# Packaging & fresh-clone reproducibility audit (audit 4)

**Candidate:** `paper/manuscript-integration` @ `4081a95bec5440046cd77ad0708866eecfdffdd8`
(fresh `git clone` + `git checkout`, verified HEAD). Frozen artifact byte-identical to
`305a3a8` (`git diff 305a3a8 HEAD -- conformance/ mpc/ reference/ .github/` empty).
No scientific logic was changed to aid reproduction. All outcomes recorded exactly.

## Environment (this run)

| tool | version |
|---|---|
| OS | Linux (container) |
| Python | 3.11.15 |
| pytest | 9.1.1 |
| pdflatex | pdfTeX 3.141592653-2.6-1.40.25 (TeX Live 2023/Debian) |
| C++/build | clang, make (MP-SPDZ default `CONFIG`) |
| MP-SPDZ | pin `9d809599` **reused** from a prior build (`MPSPDZ` env pre-set) |

## Commands run and outcomes

| step | command | outcome |
|---|---|---|
| Fresh clone | `git clone … && git checkout paper/manuscript-integration` | HEAD `4081a95` (verified) |
| PDF rebuild | `pdflatex -interaction=nonstopmode main.tex` (×2) | **OK, 11 pages, no undefined refs/citations** |
| Core artifact | `MPSPDZ=… bash paper/reproduce.sh` | **EXIT 0** — 117 tests, harness 4/4, gate + 5 controls, 228/228, evidence `--recompute` OK, **B4 synthetic / B6 caught / S1 lint-PASS + runtime oracle mismatch**; frozen tag `67da5eb` + MP-SPDZ `9d809599` verified |
| Held-out eval | `MPSPDZ=… bash paper/heldout/reproduce.sh` | **EXIT 0** — semantic PASS `[H-V1,H-V2,H-V3]` + oracle_fail; benign correct-accept `[H-T1,H-C3]`, false-reject `[H-T2]`; compile-invalid `[H-X1,H-X2]`; provenance `{H-E1:True,H-E2:True}`; **runtime_rejects `[H-R2]`** |

**Failures / retries in this run: none.** Everything reproduced on the first correct
invocation (the MP-SPDZ pin was reused; see the cold-reviewer caveat below).

## Dependencies & assumptions an artifact reviewer must satisfy

These are **not defects** in the science; they are packaging facts a reviewer needs.

1. **Network to `github.com/data61/MP-SPDZ`.** With `MPSPDZ` unset, `reproduce.sh`
   clones and builds MP-SPDZ at the pin (`make -j replicated-ring-party.x`, ~150 s in
   our earlier cold runs). A reviewer behind a firewall, or one who cannot build MP-SPDZ,
   cannot run the runtime steps. **Not documented in a top-level README at the paper
   root** — the reproduction entry points are the two `reproduce.sh` scripts and
   `paper/REPRODUCIBILITY.md`.
2. **A full git checkout with tags — not a release tarball/ZIP.** Both scripts use
   `git -C "$ROOT" worktree add … <tag/commit>` (`paper-external-review-v1`/`305a3a8`).
   A ZIP export (no `.git`) or a shallow clone missing the tag will **fail closed** at
   the worktree step. **Reviewer-facing risk:** an artifact-evaluation ZIP would not
   reproduce; the artifact must be distributed as a git repository (or the scripts
   documented as git-only). *(Logic not changed per the hard rules; flagged only.)*
3. **TLS certificates for the runtime.** `Scripts/setup-ssl.sh 3` (OpenSSL) generates
   `Player-Data/*.pem`; the scripts create them if absent. Requires `openssl`.
4. **Localhost sockets / ports.** The 3-party runtime (S1 and the held-out oracle runs)
   launches `replicated-ring-party.x` on `localhost` with `-pn <port>`. An environment
   that blocks loopback TCP would fail the runtime (not the lint) steps.
5. **Single host.** All runtime evidence is single-host (the paper already states this
   is not an adversarially isolated deployment).
6. **TeX Live** with `tikz` (+ `arrows.meta,positioning,fit,backgrounds`), `booktabs`,
   `tabularx`, `enumitem`, `hyperref`, `listings`, `xcolor`. No non-standard packages.
7. **Fail-closed guards are a feature.** Both scripts abort unless MP-SPDZ is exactly the
   pin and the checkout is exactly the frozen commit / git-blob. Good for integrity;
   means a reviewer must use the exact pin (no "latest MP-SPDZ" substitution).

## Cold-reviewer caveat (honest)

This run **reused** a pre-built MP-SPDZ pin, so it did not exercise the from-scratch
clone+build path or its ~150 s build and network fetch. A true cold artifact reviewer
will additionally incur that build and its network dependency (item 1). The one
version tested for cross-version was **not** rebuilt here (v0.4.3 build is not part of
`reproduce.sh`; that evidence lives in `paper/CROSS_VERSION.md` and was not re-executed
in this gate — see the claim→evidence audit).

## Verdict

Reproduction of the **core artifact + held-out evaluation + PDF** from a fresh clone of
the exact candidate **succeeds end-to-end (both scripts EXIT 0, PDF clean)**. The
packaging gaps are: (a) **no paper-root README** naming the two reproduction entry
points and their MP-SPDZ/network/git-clone prerequisites; (b) **git-only reproduction**
(a ZIP export would fail the worktree step). Both are **packaging/documentation**
fixes, not scientific ones.
