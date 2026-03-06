# console_mf_pseudo_holdings

## Description

WHEN TO USE:

When customer asks about:
- Current holdings, invested value, number of units
- Units not visible after allotment
- Buy average incorrect
- Pledged or locked units
- Free units available for redemption/SWP
- "Fix discrepancy" message on Coin
- P&L calculation failure

**This is the PRIMARY tool for ALL MF holdings queries. Always check this tool first.**

TRIGGER KEYWORDS: "holdings", "units", "buy average", "portfolio", "pledged", "not visible", "XIRR", "invested value", "discrepancy", "fix discrepancy", "PnL calculation failed", "coin"

## Protocol

# CONSOLE MF PSEUDO HOLDINGS PROTOCOL

## Knowledge Base

<knowledge_base>
<facts>
- **PRIMARY holdings tool — check this first for ALL MF holdings queries**
- Shows client-facing holdings as displayed on Coin/Console
- console_mf_holdings is the SECONDARY tool — used only to cross-check `available` (units for redemption/SWP), `holdings_date`, and `total_quantity`
- failure_date populated → PnL calculation failed → escalate immediately. This tool is the authoritative source for failure_date.
- discrepant > 0 → units exist but no matching trade entries in Tradebook
- Transferred-in units appear as discrepant until external entries added
- margin field is authoritative for pledged unit checks
- Scheme name field is `tradingsymbol`
- `price` = NAV per unit (per-unit cost at allotment). `quantity` = number of units allotted. Never swap these when sharing order details with the client.
- ETF FOF (Fund of Funds, e.g., "Silver ETF FoF", "Gold ETF FoF") is an MF and appears here. Pure ETFs appear in Kite holdings only.
- For MF holdings and discrepancy queries, ALWAYS use this tool first. NEVER use Kite/Console equity holdings tools for MF queries.
- Console shows T-2 NAV; Coin shows T-1 NAV (explains value differences)
</facts>

<field_usage>
  <share>tradingsymbol (as fund name) | buy_average (if asked) | buy_value (if asked) | dividend_type (if asked) | margin (if asked)</share>
  <internal>failure_date (CRITICAL — if populated → escalate immediately) | available | discrepant (CRITICAL — if >0 → investigate. NEVER share value with client.) | loan</internal>
  <banned>client_id | isin | instrument_id | t1 | pending</banned>
</field_usage>
</knowledge_base>

---

## Business Rules

### Rule 0: Tool Routing — ALWAYS Start Here
**CRITICAL:** For ALL MF holdings queries, check this tool first.
- Units, buy average, portfolio value, pledged units, discrepancy → start here.
- Only invoke **console_mf_holdings** when you need: `available` (units for redemption/SWP), `holdings_date` (latest demat credit date), or `total_quantity`.
- NEVER use Kite/Console equity holdings tools for MF queries.
- ETF FOF → check here. Pure ETF → check Kite holdings.
- NEVER share `<banned>` fields. Use `<internal>` fields for reasoning only.
- NEVER mention "pseudo holdings", "Console MF Holdings", "backend systems", "data mismatch", or any internal tool/system names to the client.
- NEVER share the `discrepant` field value OR any comparison of unit counts between internal reports to the client. Use only client-friendly language based on what the client can see on Coin.

### Rule 1: Failure Date — Immediate Escalation
**if:** `failure_date` populated
**then:** Escalate to human immediately. "Data inconsistency requires backend investigation for [tradingsymbol]."
This tool is the authoritative source for `failure_date`. If seen in **console_mf_holdings**, route escalation here.

### Rule 2: Discrepancy Detection
**if:** `discrepant` > 0, OR client reports "fix discrepancy" message, OR invested amount showing as "NA"
**then:** Determine the cause in order:
**Step 1 — Delay allotment discrepancy (most common):**
Check **console_mf_tradebook** or **mf_order_history** for a recent allotment (within last 3-4 days). If found → late delivery discrepancy. "When units are recently allotted, the invested value may temporarily show as 'NA'. This is automatically corrected within 24-48 hours. You do not need to add any trade details for purchases made through Coin. For more details: [Why are the newly allotted units shown as NA on the Coin app?](https://support.zerodha.com/category/mutual-funds/coin-web-app/articles/newly-allotted-units-shown-as-na)"
**STOP here. Do NOT suggest app troubleshooting (log out/in, clear cache, refresh) for delay allotment discrepancies. The issue is settlement-side, not client-side.**
**Step 2 — Wrongly entered external trades:**
If all purchases made through Coin only and client added external trade entries manually → ESCALATE TO AGENT. "External trade entries were incorrectly added for this fund. We will request deletion from our end."
**Step 3 — Transferred from another platform:**
"Add external trades: Console → Portfolio → Holdings → fund → Add External Trade."
**Step 4 — NFO recently allotted:**
"May auto-resolve in 3-5 days."
**Step 5 — failure_date populated:**
→ Rule 1 (escalate immediately).

### Rule 3: Mismatch Between Reports
**if:** `available` or `discrepant` here differs from **console_mf_holdings**
**then:** Check **console_mf_tradebook** for missing trade entries. If trade entry exists but mismatch persists → escalate.

### Rule 4: Buy Average / Investment Value
**if:** Customer questions buy average or invested value
**then:** This tool is authoritative. If `buy_average` or `buy_value` differs from what client expects → check **console_mf_external_trades** for missing or incorrect external entries. If investment not updated → may be settlement delay (liquid T day, non-liquid T+1).

### Rule 5: Pledged Units
**if:** `margin` > 0 AND redemption/SWP failing
**then:** `margin` field here is authoritative. Say: "You have [margin] pledged units. Unpledge first: Console → Portfolio → Holdings → [fund] → Unpledge."

### Rule 6: Console vs Coin Value
**if:** Different values shown on Console vs Coin
**then:** "Console displays the NAV as of T-2 days, while Coin displays the NAV as of T-1 day. This difference in NAV dates causes the P&L values to appear different. For the latest valuation, please refer to Coin. For more details: [Why does Console show a different MF NAV?](https://support.zerodha.com/category/mutual-funds/coin-general/coin-reports/articles/mf-nav-of-t-2-days-on-console)"
