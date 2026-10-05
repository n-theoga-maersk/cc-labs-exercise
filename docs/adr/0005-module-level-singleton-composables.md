# 0005. Share client state through module-level composables

- **Status:** Accepted
- **Date:** Predates this record; documented 2026-10-05
- **Source:** Inferred from code (`client/src/composables/`)

## Context
Several pieces of state are app-wide: the four global filters (period, warehouse, category, status), the current locale and currency, and the current user. These are read by the filter bar, every view and several modals. The app is small, has no state-management dependency (`package.json` lists only `vue`, `vue-router` and `axios`), and isn't server-rendered.

## Decision
Declare shared state as `ref`s at **module level** in a composable (`useFilters`, `useI18n`, `useAuth`). Each call to the composable returns the same refs, so the module acts as a singleton store. Views `watch` the filter refs and refetch. Raw API data stays in view-local refs, and everything else is derived with `computed`.

## Consequences
- There's no Pinia or Vuex, and no provide/inject wiring. Any component can import the composable.
- State lives as long as the page. A reset means calling an explicit function (`resetFilters()`), and the locale survives reloads only because `useI18n` writes it to `localStorage`.
- This pattern isn't safe for server-side rendering, because module state would be shared across requests. Component tests would also share state unless it's reset between them. Neither is a concern today.
- There's no devtools store inspection or time-travel debugging. If shared state grows much further, moving to Pinia would be the natural next step and would deserve its own ADR.
