# 0001. Record architecture decisions

- **Status:** Accepted
- **Date:** 2026-10-05
- **Source:** Introduced with the backend modularisation (PR #1 in the n-theoga-maersk fork)

## Context
Several load-bearing choices in this repo were only visible in the code or in commit messages: the in-memory data, the dev proxy, hash routing and singleton state. People and AI agents changing the code kept running into them without knowing why they existed. The Claude guidance files (`CLAUDE.md`, `.claude/rules/`) say *how* to work in the codebase. They are not a good place for *why* it is shaped this way.

## Decision
Record significant architecture decisions as short Markdown ADRs in `docs/adr/`, numbered sequentially, using the structure in `template.md` (context, decision, consequences). An accepted ADR is not rewritten. A change of direction gets a new ADR that supersedes the old one.

For decisions that existed before this record, the ADR says where its context came from (commit message vs. inferred from code), so readers don't mistake a reconstruction for the original reasoning.

## Consequences
- Rationale lives next to the code and is versioned with it.
- Guidance files can link to an ADR instead of re-explaining the reasons.
- It takes some discipline: a decision that changes architecture should arrive with its ADR in the same PR.
