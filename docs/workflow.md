# How we work

Three participants: Harshit (direction, decisions), Claude (implementation,
experiments), ChatGPT (adversarial review). This repo is the shared mailbox.

## The loop

1. Claude pushes work and opens a PR, or posts a brief as an issue
2. Harshit: "Review PR #N" / "Review issue #N"
3. ChatGPT reads the repo, code, CI and thread, posts its review as a comment
4. Harshit: "Claude, review is in"
5. Claude reads the comment, logs it to `docs/review-log.md` with a resolution,
   fixes what lands, pushes
6. Repeat

No copy-paste, no screenshots. Harshit's only job is nudging each side to take
its turn.

## How Claude reaches GitHub

Claude runs in an Anthropic cloud sandbox whose GitHub proxy only permits repos
explicitly attached to the session — and there is no way to attach one from the
mobile app. Every direct call returns:

    403 "sessions are bound to their configured repositories"

The route that works: **Desktop Commander MCP on the Mac.** That gives Claude a
shell on a machine where `gh` is already authenticated
(`harshitkargetiiiiii`, scopes `gist read:org repo workflow`). All git and `gh`
operations run there.

    cloud sandbox          Mac (Desktop Commander)        GitHub
    ─────────────          ───────────────────────        ──────
    experiments,      →    git / gh / push / PR      →    repo
    LaTeX, analysis        (authenticated)                issues, CI

**Requirement: the Mac must be awake with the Claude desktop app running.**
Harshit does not need to touch it or be at it — he can drive everything from
mobile — but if the Mac sleeps or the app closes, Claude loses GitHub until it
comes back. Nothing else in the loop depends on the Mac.

## Where work happens

| | |
|---|---|
| Cloud sandbox | MP-SPDZ builds and runs, LaTeX, analysis. **Ephemeral** — reclaimed on inactivity. Nothing lives here. |
| This repo | The only persistent memory. Everything of value gets committed. |
| GitHub Actions | Real benchmarks. Runners have root, so `tc netem` works for LAN/WAN emulation — the sandbox cannot do this. |
| The Mac | Git/gh transport only. Not a compute target. |

## Rules

- **The repo is the source of truth.** If it is not committed, it does not exist.
  The sandbox forgets everything between sessions.
- **Every external critique gets an entry in `docs/review-log.md`**, whether it
  survived or not. Append-only. Refuted objections stay, marked resolved.
- **No claim ships unhedged.** Anything unverified says so, in the file, next to
  the claim. `docs/claims.md` is the register of what is still hypothesis.
- **Reviews are adversarial by construction.** Briefs instruct the reviewer to
  refute and list what does not count as a review. Two models agreeing is weak
  evidence — they agree for correlated reasons.
- **A human MPC expert still has to sign off** before anything is submitted
  anywhere. Model review is a filter, not a substitute.
