# Feature specs

A spec describes **what** a change will do and how we'll know it's done, before the code is written. It's the companion to ADRs (`docs/adr/`), which record **why** the architecture is shaped the way it is.

## When to write one
Write a spec for anything that:
- adds or changes an API endpoint (its URL, params, request or response shape),
- changes data files or Pydantic models,
- adds a view, or changes user-visible behaviour across more than one view.

You don't need one for bug fixes that restore documented behaviour, copy changes or refactors that change no behaviour.

## How to write one
- **With Claude Code:** `/spec <short description>`. It creates the next numbered file, researches the code and fills in what it can. Anything it can't confirm goes under *Open questions*.
- **By hand:** copy [template.md](template.md) to `NNNN-short-title.md` using the next number, and add it to the index below.

## Lifecycle
| Status | Meaning |
|---|---|
| Draft | Being written; open questions remain |
| Approved | Open questions that affect the contract are resolved; OK to implement |
| Implemented | Merged; link the PR in **Related** |
| Abandoned | Not pursued; keep the file and add a line saying why |

A spec is a plan, not a living document. If the implementation has to differ, update the spec in the same PR so it describes what shipped. If the change is architectural, also add an ADR.

## Index
| Spec | Title | Status |
|---|---|---|
| [0001](0001-purchase-orders-api.md) | Purchase orders API | Approved |
