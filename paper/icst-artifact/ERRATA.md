# ERRATA — supersession notes for the frozen files

The files under `checker/`, `subject-and-controls/`, `reference/`, `prereg/`,
`mutations/`, `results/`, and `reproduce/` are shipped **byte-identical** to the
reviewed research artifact (see `SHA256SUMS.txt`). They are therefore **not edited**
to fix wording, even where an inline comment is narrower than the manuscript's final
claim. This file records the two places where the shipped text is superseded, so a
reviewer reading the frozen code is not misled.

## 1. "Memory is the only channel" comments are superseded

The frozen delivery linter `checker/delivery_inspect.py` contains inline comments
(in and around the rule-(g) and rule-(h) memory blocks) that describe memory as the
channel by which a verdict register could reach a non-main tape — for example,
phrasing to the effect that a MAIN store is *the* channel by which the verdict can
reach a subtape. Those comments reflect the linter's design rationale for the
memory rules; they are **not** a claim that memory is the only cross-tape channel in
general.

The manuscript's final, controlling wording is non-exhaustive:

> In the compiled paths exercised here, we observed cross-tape transfer through
> memory and through register arguments passed by `call_tape` and received by
> `call_arg`; we do not claim these are the only possible cross-tape channels.

Where any frozen comment reads as "memory-only," treat the manuscript's
non-exhaustive statement as controlling. (The same file's docstring already notes
that the `call_tape` / `call_arg` register channel cannot be blocklisted because the
honest build uses it, which is consistent with the non-exhaustive wording.)

## 2. Frozen files retain non-identifying development annotations

For byte-identity, the frozen files are **not** scrubbed of development-time
annotations. These annotations do **not** identify the authors, the institution, or
any repository, and are immaterial to the scientific content:

- **References to an automated code-review assistant.** Several comments credit an
  automated code-review tool for a counterexample or a hardening step. This names a
  reviewing *tool*, not a person or an affiliation. The paper's own limitations
  section already discloses that the implementation, tests, review synthesis, and
  manuscript were produced within one project with substantial AI assistance, and
  that model agreement is not independent validation.
- **Internal review-iteration identifiers.** Tokens such as review-round and
  issue-number labels are internal bookkeeping for the project's own iterative
  review; they do not resolve to any external identity.
- **Internal commit and tag identifiers.** The frozen files and reproduction
  wrappers reference the project's internal baseline commit hash and an internal
  review tag. These are private-repository identifiers; on their own they do not
  resolve to a public repository or an author. The only *public* dependency
  identifier retained is the MP-SPDZ upstream pin (`9d809599`), which is required to
  reproduce and is intentionally kept.

None of the above changes any result, number, checksum, or outcome. The manuscript
and this artifact's Markdown prose (`README.md`, `REPRODUCE.md`, this file) contain
no author-identifying information.
