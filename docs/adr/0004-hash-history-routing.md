# 0004. Use hash-history routing

- **Status:** Accepted
- **Date:** 2026-06-11 (as recorded in git)
- **Source:** Commit 517b1c2 "fix: use hash routing so app works behind dynamic proxy prefix"

## Context
Vite serves the app under `base: "/dashboard/"`. A sandbox environment additionally served the dev server under a dynamic path prefix (`/dashboard/proxy/<port>/`). That prefix stacked on top of the router's hard-coded base, so the initial route didn't match and the page stayed blank until a nav link was clicked.

## Decision
Use Vue Router's `createWebHashHistory()` (`client/src/main.js`). Routes live in the URL fragment, for example `/dashboard/#/orders`.

## Consequences
- Routing resolves correctly under any path prefix, with no server-side rewrite rules.
- URLs carry a `#`. Deep links work, but they look less clean and the fragment is never sent to the server.
- Switching back to HTML5 history would need the base path to be known at build or run time in every environment the app is served from.
