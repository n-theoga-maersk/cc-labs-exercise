# 0006. Store amounts in USD; derive display currency from locale

- **Status:** Accepted
- **Date:** Predates this record; documented 2026-10-05
- **Source:** Inferred from code (`client/src/composables/useI18n.js`, `client/src/utils/currency.js`); pt_BR locale added in commit 4b77221

## Context
The UI is translated into English, Japanese and Brazilian Portuguese. Users of each locale expect amounts in their own currency. The backend has no notion of currency: every amount in `server/data/` is USD.

## Decision
- The backend serves USD only.
- The client derives the display currency from the locale, with no separate user setting (`en` → USD, `ja` → JPY, `pt_BR` → BRL, in `useI18n`'s `currentCurrency`).
- Conversion and formatting happen only in `client/src/utils/currency.js`, which converts at a fixed rate (`USD_TO_JPY = 150`).

## Consequences
- One source of truth for amounts, and conversion is purely presentational.
- Converted figures are approximate: there are no live rates and no historical rates per transaction.
- Revenue goals ($800K/month, $9.6M YTD) are USD figures, and must be converted the same way to stay comparable.
- **Known gap:** `currency.js` handles only JPY. BRL falls through to USD formatting, so pt_BR users see `$` amounts even though `currentCurrency` reports `BRL`. Supporting BRL needs a rate and a formatting branch in `currency.js`, and nothing else.
