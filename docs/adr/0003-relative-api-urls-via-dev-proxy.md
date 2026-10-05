# 0003. Frontend calls the API through relative `/api` URLs and the Vite proxy

- **Status:** Accepted
- **Date:** 2026-06-11 (as recorded in git)
- **Source:** Commit 3f8b188 "fix: use relative API URLs in Reports so it works behind proxy"

## Context
The frontend (port 3000) and the backend (port 8001) are separate processes. `Reports.vue` called the backend at a hard-coded `http://localhost:8001`. When the app was served through a tunnel, the browser couldn't reach that address, while every other view, which used relative paths, kept working.

## Decision
All HTTP calls use relative `/api/...` URLs. Most go through `client/src/api.js`; `Reports.vue` still calls `axios` directly, but with relative paths. The Vite dev server proxies `/api` to `http://localhost:8001` (`client/vite.config.js`). Nothing in the client may hard-code a backend host.

## Consequences
- The app works unchanged on localhost, through tunnels and behind sandbox proxies, because the browser only ever talks to the origin that served it.
- There's no CORS round-trip in normal use (the backend still allows `*`; see `server/CLAUDE.md`).
- The frontend only works when something proxies `/api`. A static `npm run build` output needs a web server configured to proxy `/api` the same way, and there is none in this repo.
