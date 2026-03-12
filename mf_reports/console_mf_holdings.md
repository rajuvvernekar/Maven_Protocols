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

## Knowledge Base

<knowledge_base>
<facts>
- SECONDARY holdings tool — backed by Tradebook + demat records
- Invoke only for: `available` (units free for redemption/SWP), `holdings_date` (latest demat credit), `total_quantity`
- For all other holdings queries → use console_mf_pseudo_holdings
- Liquid units visible T day by 7 PM; non-liquid T+1 day by 7 PM
- Pledged units (margin) → check console_mf_pseudo_holdings; margin is authoritative there
- failure_date: if seen here, route escalation through console_mf_pseudo_holdings (authoritative source)
- Console shows T-2 NAV; Coin shows T-1 NAV (explains value differences)
- Scheme name field is `tradingsymbol`
- ETF FOF is an MF — appears in Coin holdings. Pure ETFs appear in Kite holdings only.
</facts>

<field_usage>
  <share>tradingsymbol (as fund name) | buy_average (if asked) | buy_value (if asked) | total_quantity (if asked)</share>
  <internal>holdings_date (latest demat credit) | failure_date (passive — if seen, route to pseudo_holdings) | available (CRITICAL for redemption/SWP checks) | discrepant (cross-check only — NEVER share with client) | loan | closing_price</internal>
  <banned>name (not applicable for MF) | client_id | isin | instrument_id | t1 | pending</banned>
</field_usage>
</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
Never share `<banned>` fields. Use `<internal>` fields for reasoning only. NEVER mention "pseudo holdings", "backend systems", or any internal tool/system names to client. NEVER share the `discrepant` field value with the client.

### Rule 1: Units Available for Redemption/SWP
**if:** Need to verify units available for redemption or SWP
**then:** Check `available` field here — this is the authoritative source for redeemable units.
- `available` = 0 or insufficient → inform client units are not available.
- `available` > 0 but redemption failing → check if pledged via **console_mf_pseudo_holdings** (`margin`).

### Rule 2: Units Not Visible After Allotment
**if:** Units missing after allotment
**then:** Check **console_mf_pseudo_holdings** first for discrepancy diagnosis. Use this tool only to verify `holdings_date` (latest demat credit) and `total_quantity`.
- Within settlement timeline (liquid T day 7 PM, non-liquid T+1 7 PM) → "Units will be visible by [timeline]."
- Beyond timeline → check `holdings_date` here for latest credit date. Route full discrepancy diagnosis to **console_mf_pseudo_holdings**.

### Rule 3: Discrepancy Cross-Check
**if:** console_mf_pseudo_holdings shows discrepant > 0 and requests cross-check
**then:** Compare `available` and `discrepant` here with pseudo_holdings values. If mismatch → check **console_mf_tradebook** for missing trade entries. If trade entry exists but mismatch persists → escalate.

### Rule 4: Buy Average Incorrect
**if:** Wrong buy average flagged by console_mf_pseudo_holdings
**then:** Cross-check **console_mf_external_trades** — all entries correct/complete? If transferred, verify external entries added. If all correct + `failure_date` empty → escalate.

### Rule 5: Failure Date — Passive Note
**if:** `failure_date` seen here
**then:** Do NOT escalate from this tool. Route to **console_mf_pseudo_holdings** — it is the authoritative source for `failure_date`. Escalation must be triggered from there.

### Rule 6: Console vs Coin Value
**if:** Different values shown on Console vs Coin
**then:** "Console displays the NAV as of T-2 days, while Coin displays the NAV as of T-1 day. This difference in NAV dates causes the P&L values to appear different. For the latest valuation, please refer to Coin. For more details: [Why does Console show a different MF NAV?](https://support.zerodha.com/category/mutual-funds/coin-general/coin-reports/articles/mf-nav-of-t-2-days-on-console)"

### Rule 8: Tool Routing
**CRITICAL:**
- ALL MF holdings queries → start with **console_mf_pseudo_holdings**
- Invoke THIS tool only for: `available`, `holdings_date`, `total_quantity`
- NEVER use Kite/Console equity holdings tools for MF queries
- ETF FOF → console_mf_pseudo_holdings. Pure ETF → Kite holdings.
