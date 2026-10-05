# 0009. Split Claude Code guidance into path-scoped files

- **Status:** Accepted
- **Date:** 2026-10-05
- **Source:** PR #1 in the n-theoga-maersk fork (`refactor/modular-backend-and-docs`)

## Context
Guidance for Claude Code lived in three `CLAUDE.md` files. `client/CLAUDE.md` (~485 lines) and `server/CLAUDE.md` (~290 lines) were mostly general Vue and FastAPI advice. They contained wrong facts, such as a test command that fails and categories that don't exist in the data. Several facts were repeated across files and had drifted apart. Everything loaded into context whether or not it was relevant to the task.

## Decision
Organise guidance by scope, with **each fact in exactly one file**:

| File | Loaded |
|---|---|
| `CLAUDE.md` | always: overview, commands, tool rules, map of the other files |
| `server/CLAUDE.md`, `client/CLAUDE.md` | when working in that directory |
| `.claude/rules/*.md` with `paths:` frontmatter | when touching matching files (data, testing, i18n, design-system) |

Content is limited to facts specific to this codebase that can be checked, not general framework advice. Commands are tested before they're documented. *Why* things are the way they are goes in ADRs (`docs/adr/`), not in guidance files.

## Consequences
- Less irrelevant context in each session, and a single place to update each fact.
- A new rule needs a deliberate choice of scope. Cross-cutting facts that every session needs (such as the test command) belong in the root file.
- Path-scoped rules don't load until a matching file is touched, so the root file must name them (it does, in "Where guidance lives").
- Skills and subagents (`.claude/skills/`, `.claude/agents/`) are self-contained by design, so a few facts are repeated there. These must be updated when the facts change.
