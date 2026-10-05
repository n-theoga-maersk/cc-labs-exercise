---
description: Draft a feature spec from docs/specs/template.md
argument-hint: <short feature description>
---

Draft a new feature spec for: $ARGUMENTS

Steps:
1. If no description was given, ask for one and stop.
2. Find the next number: look at existing `docs/specs/NNNN-*.md` files and use the highest number + 1, zero-padded to 4 digits. Choose a short kebab-case slug.
3. Copy `docs/specs/template.md` to `docs/specs/NNNN-<slug>.md`.
4. Research before writing. Read the code this feature touches, and don't guess:
   - `client/src/api.js` and the relevant views/components, to see what the client already expects
   - `server/app/routers/`, `server/app/models.py`, `server/app/filters.py`
   - the relevant files in `server/data/`
   - the ADRs in `docs/adr/` that relate to this area
5. Fill in every section from what you found, and cite file paths as evidence. Then:
   - Replace the guidance comments with real content. Delete a section only if the template says it may be deleted, and say why.
   - Anything you could not confirm from the code, and any product decision, goes under **Open questions**. Don't invent answers.
   - Make the acceptance criteria observable (a request and its expected result, or a UI state).
   - Under **Architecture impact**, name any ADR that the feature affects or contradicts.
6. Leave **Status** as `Draft`, set **Created** to today's date, and leave **Owner** for the user.
7. Add a row to the index in `docs/specs/README.md`.
8. Don't implement anything. Report the file path, a summary in two or three lines, and the open questions the user needs to answer.

When the user later answers an open question, move it into the **Decisions** table with the date, and update every section it affects (contract, models, edge cases, tests, acceptance criteria).
