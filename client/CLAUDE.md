# CLAUDE.md - Client

Guidance for the Vue 3 frontend. Any `.vue` creation or significant change goes through the **vue-expert** subagent. Styling rules are in `.claude/rules/design-system.md` and translation rules in `.claude/rules/i18n.md`.

## Commands (from `client/`)
```bash
npm run dev      # http://localhost:3000/dashboard/ (needs the backend on 8001 for /api)
npm run build    # production build; the only check available (no linter or test runner)
```

## Structure
- `src/main.js`: router with **hash history** under Vite `base: "/dashboard/"`, so URLs look like `/dashboard/#/orders`. `views/Backlog.vue` exists but has no route.
- `src/api.js`: the only place that makes HTTP calls. It uses relative `/api` URLs (proxied by Vite) and leaves out any filter param whose value is `'all'`.
- `src/views/`: one view per route. Views own their data loading and modals.
- `src/composables/`: shared state lives in **module-level refs**, so every caller of the composable gets the same singleton state (no Pinia, no provide/inject):
  - `useFilters`: the four global filters. `getCurrentFilters()` turns them into API params (`selectedLocation` → `warehouse`, `selectedPeriod` → `month`). Views `watch` the filter refs and refetch.
  - `useI18n`: current locale, currency and translation helpers (see rules/i18n.md).
  - `useAuth`: a mock current user; there is no real authentication.

## Conventions
- Both `setup()`-returning components (most views) and `<script setup>` (most components) exist. Match whichever the file you're editing already uses.
- Keep raw API data in refs (`allOrders`, `inventoryItems`) and derive everything else with `computed`.
- Use unique keys in `v-for` (`sku`, `id`, `month`), never the index.
- Validate dates before calling `.getMonth()`.
- Inventory has no time dimension, so the period filter doesn't apply to it.
