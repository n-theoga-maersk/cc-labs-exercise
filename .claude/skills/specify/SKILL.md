---
name: specify
description: Draft a feature spec for the Factory Inventory Management System (Vue 3 + FastAPI) before any code is written. Use when the user says "write a spec", "spec this feature", "specify ...", "draft a spec for ...", or asks for a spec, design doc or requirements for a new endpoint, view or behaviour change in this repo. Produces docs/specs/NNNN-<kebab-feature>.md and stops for review; never implements.
argument-hint: <feature>
model: opus
effort: high
---

# Specify a feature

Draft a spec for: **$ARGUMENTS**

If no feature was given, ask the user what to specify and wait for the answer.

Your only outputs are the spec file, its row in the specs index and, if missing, the template. **Do not write, edit or scaffold any implementation code, tests or config.**

## 1. Read before writing
The spec must describe the codebase as it is, and respect decisions already made. Read, and cite file paths in the spec:

- **`CLAUDE.md`**, plus `server/CLAUDE.md` and/or `client/CLAUDE.md` for the side(s) the feature touches, and any relevant `.claude/rules/*.md`.
- **Every ADR in `docs/adr/`.** Note which ones the feature relies on, extends or would contradict. Load-bearing ones:
  - in-memory JSON data that resets on restart;
  - relative `/api` URLs through the Vite proxy;
  - hash routing;
  - module-level composables;
  - amounts stored in USD, with the display currency taken from the locale;
  - one router per area under `server/app/routers/`.
- **The code the feature touches:**
  - **Backend:** `server/app/routers/`, `server/app/models.py`, `server/app/filters.py` (`apply_filters`, `filter_by_month`), `server/app/data.py`, `server/data/*.json`.
  - **Frontend:** `client/src/api.js`, plus the relevant `client/src/views/` and `components/` and `client/src/composables/`. Check whether the client *already* calls or renders something for this feature: half-built UI and calls to missing endpoints exist in this repo.
  - **Tests:** `tests/backend/`.
- **`docs/specs/`:**
  - `README.md`: when a spec is needed, the lifecycle (Draft → Approved → Implemented / Abandoned) and the index.
  - The existing specs, for precedent (`0001-purchase-orders-api.md` is a complete worked example), and to avoid duplicating one that already exists.

Read the code itself rather than relying on what the docs say about it. If you find a difference between the two, record it in the spec.

## 2. Open the template
Open `docs/specs/template.md`. Its HTML comments explain what each section needs; follow them.

If the file doesn't exist, create it with exactly this lean version, then continue:

```markdown
# SPEC-NNNN: Feature name

| | |
|---|---|
| **Status** | Draft |
| **Owner** | |
| **Created** | YYYY-MM-DD |
| **Related** | ADRs, PRs, issues |

## Summary
## Problem
## Goals
## Non-goals
## User-facing behaviour
## API contract
| Method | Path | Query params | Request body | Response | Errors |
|---|---|---|---|---|---|
## Data and models
## Implementation outline
## Architecture impact
## Edge cases and errors
## Test plan
## Acceptance criteria
- [ ] 
## Open questions
## Decisions
| # | Question | Decision |
|---|---|---|
## Follow-ups
```

## 3. Fill every section
Work through the template top to bottom. For each section, write what the code and ADRs support, and cite where it comes from. Delete a section only where the template allows it (for example, *User-facing behaviour* for backend-only work), and say why. Repo-specific things to get right:

- **Contract:**
  - Mark which endpoints are **new** and which are **changed**. A change to an existing endpoint is a contract change, so call it out.
  - For filtered endpoints, use the standard query params: `warehouse`, `category`, `status`, `month` (`YYYY-MM` or `Q1-2025`). A missing value or `'all'` means no filter.
  - Say explicitly if the filters don't apply.
- **Models:**
  - Prefer a `response_model` to an untyped dict.
  - Date-only inputs use `IsoDate` / `FutureIsoDate` from `server/app/models.py`, never `date`.
  - Float inputs need `allow_inf_nan=False`.
- **Data:**
  - Data lives in memory and is lost on restart.
  - Shared lists in `server/app/data.py` are read-only, except for deliberate in-place appends (never rebinding the name).
  - Say whether losing data on restart is acceptable for this feature.
- **UI:**
  - New strings go into all three locales (`en`, `ja`, `pt_BR` in `client/src/locales/`).
  - Money is USD from the API, shown via `client/src/utils/currency.js`.
  - Any `.vue` work goes through the vue-expert subagent.
- **Tests:**
  - Name the test files and tests.
  - Tests that write must restore the shared store in place, and compute dates relative to today inside the test body.
  - For changes to existing endpoints, plan a before/after comparison of full responses.
- **Acceptance criteria** must each be observable: a request and its expected result, or a UI state.

**When you can't infer something with confidence, ask the user.** That includes any product decision, any choice between reasonable options, and any conflict with an ADR. Rules for asking:

- Ask **one question at a time**, and wait for the answer before asking the next.
- Give a short recommended default, with your reason, and the alternatives.
- Ask only about what changes the spec. Don't ask about things the code already answers.
- Record each answer in the **Decisions** table with today's date, and update every section it affects.
- If the user defers a question, leave it under **Open questions**. The spec stays **Draft** while any open question affects the API contract.

## 4. Write the spec
1. **Number it:** find the highest `NNNN` in `docs/specs/NNNN-*.md` and add 1, zero-padded to 4 digits.
2. **Name it:** derive the kebab-case name from the feature (for example, "Approve or reject purchase orders" becomes `approve-reject-purchase-orders`).
3. **Check for an existing spec:** if one already covers this feature, ask the user whether to update it or write a new one before writing anything.
4. **Write the file:** save the result as `docs/specs/NNNN-<kebab-feature>.md`, titled `SPEC-NNNN: <Feature name>`.
5. **Fill in the header:**
   - Set **Created** to today's date.
   - Leave **Owner** blank.
   - Set **Status** to `Draft`, or to `Approved` only if the user explicitly says so.
   - Remove the template's guidance comments and placeholder text.
6. **Index it:** add a row for the spec, with its status, to the index in `docs/specs/README.md`.

## 5. Stop for review
Stop. **Do not implement anything:** no code, no tests, no branches, no commits. Report:
- the spec's path;
- a two- or three-line summary;
- which ADRs it relies on or affects;
- any open questions left.

Then wait for the user's review.
