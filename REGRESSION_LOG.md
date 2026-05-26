# Regression Log

A regression is when the **same rule or section** in a tool needs to be fixed again after a prior fix was already applied. Track it here so we can see if a change didn't stick, was incomplete, or is being pulled back by a competing edit.

## How to use

When adding an entry to `CHANGELOG.md` for a tool + section that was **previously modified**, check this file first:
- If the section appears in the table → it's a regression. Set `Regression?` to `Yes` and fill in `Previous Fix`.
- If the section is not here → add it as a new row for future monitoring.

---

## Regression Table

| Date | Tool | Rule / Section | Issue Summary | Previous Fix (Date + CHANGELOG entry) | Regression? |
|------|------|----------------|---------------|----------------------------------------|-------------|
| 2026-05-21 | `cashier_payins` | Rule 2 (status logic) | Escalation wording re-standardised | 2026-04-13 batch update | No — additive |
| 2026-05-21 | `account_modification_report` | Escalation directives (21 rules) | Collapsed to `escalate.` after pilot on same tool | 2026-05-21 pilot | No — planned rollout |
| 2026-04-13 | `withdrawal_request` | Rule 8 (payout timing) | Restructured with query-date anchor | 2026-03-09 (added Rule 15 fallback) | No — separate area |
| 2026-04-13 | `ledger_report` | Rule 8 (BTST detection) | Complete rewrite | 2026-03-06 (T+1 settlement grouping) | No — separate area |

> **Note:** Rows marked `No` document that we checked and confirmed it is NOT a regression — the sections are distinct. Only a `Yes` row means the same fix was needed twice.

---

## Watch List

These tools have been modified **3 or more times** across different batches. Higher chance of a real regression appearing here — verify carefully before each edit.

| Tool | Modification Count | Areas Most Changed |
|------|-------------------|--------------------|
| `account_modification_report` | 4 | Segment activation, ReKYC, dormancy, escalation |
| `withdrawal_request` | 3 | Payout timing, bank rejection logic, fallback |
| `cashier_payins` | 3 | Status logic, NRI PIS, bank alt details |
| `ledger_report` | 3 | Settlement grouping, BTST, MTF interest |
| `kite_orders` | 2 | Margin rejection flow, GTT linkage |
| `mf_order_history` | 2 | Cancel status, NFO detection, SIP mandate |
| `sip_report` | 2 | SIP skip logic, NRI PIS mandate, UPI timing |

---

## Confirmed Regressions

None yet. If a `Yes` row is added to the table above, move it here with a brief root cause note.

| Date | Tool | Section | Root Cause | Resolution |
|------|------|---------|-----------|-----------|
| — | — | — | — | — |
