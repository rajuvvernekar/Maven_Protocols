# console_mf_holdings

## Description

WHEN TO USE:

When need to cross-check:
- Units available for redemption or SWP (`available` field)
- Latest demat credit date (`holdings_date`)
- Total quantity of units held (`total_quantity`)
- Mismatch between demat records and Coin-facing holdings

**This is the SECONDARY tool. Always check console_mf_pseudo_holdings first for MF holdings queries. Invoke this tool only for the specific fields listed above.**

TRIGGER KEYWORDS: "available units", "demat holdings", "units for redemption", "coin"

## Protocol

# CONSOLE MF HOLDINGS PROTOCOL

---

## Section A: Reference Data

### A1 — Tool Purpose & Scope

- This is a **secondary** holdings tool — backed by Tradebook + demat records.
- Invoke only for: `available` (units free for redemption/SWP), `holdings_date` (latest demat credit), `total_quantity`.
- For all other MF holdings queries → use console_mf_pseudo_holdings first.
- All MF holdings queries start with console_mf_pseudo_holdings. This tool is invoked only when specific fields above are needed.
- ETF FOF is an MF — appears in Coin holdings (use console_mf_pseudo_holdings). Pure ETFs appear in Kite holdings only.

### A2 — Settlement Timelines

| Fund Type | Units Visible |
|---|---|
| Liquid funds | T day by 7 PM |
| Non-liquid funds | T+1 day by 7 PM |

### A3 — NAV Display Differences

| Platform | NAV Date |
|---|---|
| Console | T-2 days |
| Coin | T-1 day |

This difference in NAV dates causes P&L values to appear different between platforms. For the latest valuation, refer to Coin.

Reference: [Why does Console show a different MF NAV?](https://support.zerodha.com/category/mutual-funds/coin-general/coin-reports/articles/mf-nav-of-t-2-days-on-console)

### A4 — Field Rules

**Shareable with client (if asked):** `tradingsymbol` (as fund name), `buy_average`, `buy_value`, `total_quantity`.

**Internal reasoning only (use for analysis, never share):** `holdings_date` (latest demat credit), `failure_date` (passive — if seen, route to console_mf_pseudo_holdings), `available` (critical for redemption/SWP checks), `discrepant` (cross-check only), `loan`, `closing_price`.

**Suppress (no client use, only reasoning purpose).** `name` (not applicable for MF), `client_id`, `isin`, `instrument_id`, `t1`, `pending`.

**Client communication rules:** Scheme name field is `tradingsymbol`. Never mention "pseudo holdings", "backend systems", or any internal tool/system names to the client. Never share the `discrepant` field value with the client.

### A5 — Tool Routing Reference

| Query Type | Primary Tool | This Tool's Role |
|---|---|---|
| All MF holdings queries (default) | console_mf_pseudo_holdings | Do not use this tool as starting point |
| Units available for redemption/SWP | **This tool** (`available` field) | Authoritative source |
| Latest demat credit date | **This tool** (`holdings_date` field) | Authoritative source |
| Total quantity verification | **This tool** (`total_quantity` field) | Authoritative source |
| Pledged units / margin | console_mf_pseudo_holdings | Margin is authoritative there |
| failure_date investigation | console_mf_pseudo_holdings | Authoritative source; route escalation from there |
| Discrepancy diagnosis | console_mf_pseudo_holdings (start) → this tool (cross-check) | Cross-check role only |
| Buy average issues | console_mf_pseudo_holdings → console_mf_external_trades | Cross-check external entries |
| Missing trade entries | console_mf_tradebook | Verify trade exists |
| Pure ETF holdings | Kite equity holdings | Not an MF query |
| ETF FOF holdings | console_mf_pseudo_holdings | ETF FOF is treated as MF |

### A6 — Cross-Reference Protocols

| Topic | Refer to |
|---|---|
| Primary MF holdings, discrepancy diagnosis, pledged units, failure_date | console_mf_pseudo_holdings |
| Missing trade entries verification | console_mf_tradebook |
| Buy average correction / external trade entries | console_mf_external_trades |
| Pure ETF holdings | Kite equity holdings |

## Section B: Decision Flow

### Preflight (run on every query)

1. Determine if this tool is needed: check if the query requires `available`, `holdings_date`, or `total_quantity`. If not → route to console_mf_pseudo_holdings per **A5**.
2. If this tool is needed, fetch the MF holdings data.
3. Apply field protection per **A4** — identify shareable, internal, and banned fields.
4. Check for `failure_date` — if present, note it but do not escalate from this tool (route to console_mf_pseudo_holdings per Rule 5).
5. Format amounts with ₹ and Indian comma notation.

### Routing Tree

```
Query relates to MF holdings →
│
├─ Need to verify units available for redemption/SWP
│  → Rule 1
│
├─ Units not visible after allotment
│  → Rule 2
│
├─ Discrepancy cross-check (requested by console_mf_pseudo_holdings)
│  → Rule 3
│
├─ Buy average incorrect (flagged by console_mf_pseudo_holdings)
│  → Rule 4
│
├─ failure_date seen in data
│  → Rule 5 (Route to console_mf_pseudo_holdings)
│
├─ Console vs Coin value difference
│  → Rule 6
│
└─ General MF holdings query (not requiring available/holdings_date/total_quantity)
   → Route to console_mf_pseudo_holdings per A5
```

### Scope

- Address: redeemable unit verification, demat credit dates, total quantity checks, and cross-check support for console_mf_pseudo_holdings.

### Fallback

If query doesn't match any rule and doesn't require this tool's specific fields → route to console_mf_pseudo_holdings per **A5**.

---

## Section C: Rules

### Rule 1 — Units Available for Redemption/SWP

1. Check the `available` field — this is the authoritative source for redeemable units.
2. If `available` = 0 or insufficient → inform client that units are not available for redemption/SWP.
3. If `available` > 0 but redemption is failing → check if units are pledged via console_mf_pseudo_holdings (`margin` field, per **A5**).

### Rule 2 — Units Not Visible After Allotment

1. Check console_mf_pseudo_holdings first for discrepancy diagnosis (per **A5**).
2. Use this tool only to verify `holdings_date` (latest demat credit) and `total_quantity`.
3. If within settlement timeline (per **A2**: liquid T day 7 PM, non-liquid T+1 7 PM) → "Units will be visible by [timeline]."
4. If beyond timeline → check `holdings_date` for latest credit date. Route full discrepancy diagnosis to console_mf_pseudo_holdings (per **A5**).

### Rule 3 — Discrepancy Cross-Check

1. Triggered when console_mf_pseudo_holdings shows `discrepant` > 0 and requests cross-check.
2. Compare `available` and `discrepant` here with console_mf_pseudo_holdings values.
3. If mismatch → check console_mf_tradebook for missing trade entries (per **A6**).
4. If trade entry exists but mismatch persists → escalate.

### Rule 4 — Buy Average Incorrect

1. Triggered when console_mf_pseudo_holdings flags wrong buy average.
2. Cross-check console_mf_external_trades (per **A6**) — verify all entries are correct and complete.
3. If units were transferred in, verify external trade entries have been added.
4. If all entries correct and `failure_date` is empty → escalate.

### Rule 5 — Failure Date: Passive Route

1. If `failure_date` is present in this tool's data → do not escalate from this tool.
2. Route to console_mf_pseudo_holdings — it is the authoritative source for `failure_date` (per **A5**).
3. Escalation for failure_date must be triggered from console_mf_pseudo_holdings, not from here.

### Rule 6 — Console vs Coin Value Difference

1. Respond using **A3**: "Console displays the NAV as of T-2 days, while Coin displays the NAV as of T-1 day. This difference in NAV dates causes the P&L values to appear different. For the latest valuation, please refer to Coin."
2. Share link from **A3**.


---
---
