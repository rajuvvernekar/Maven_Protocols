# console_mf_holdings

## Description

WHEN TO USE:

When customer asks about:
- Current holdings, invested value, number of units
- Units not visible after allotment
- Buy average incorrect
- Pledged or locked units
- Free units available for redemption/SWP
- "Fix discrepancy" message on Coin

TRIGGER KEYWORDS: "holdings", "units", "buy average", "portfolio", "pledged", "not visible", "XIRR", "invested value", "coin"

## Protocol

# CONSOLE MF HOLDINGS PROTOCOL

## Knowledge Base

<knowledge_base>
<facts>
- Current holdings per fund, backed by Tradebook + depository records
- Console shows T-2 NAV; Coin shows T-1 NAV (explains value differences)
- Liquid units visible T day by 7 PM; non-liquid T+1 day by 7 PM
- Transferred-in units appear as discrepant until external entries added
- Pledged units (margin) can't be redeemed until unpledged
- failure_date populated → PnL calculation failed → escalate immediately
- discrepant > 0 → investigate
- Scheme name field is `tradingsymbol`
- ETF FOF (Fund of Funds, e.g., "Silver ETF FoF", "Gold ETF FoF") is an MF and appears in Coin holdings. Pure ETFs (e.g., "Gold ETF", "Silver ETF") appear in Kite holdings only, NOT Coin.
- When there is a late delivery of units to the demat account, 'NA' is displayed on T+2 days after allotment. This is automatically corrected on T+3 day. Client does NOT need to add any trade details for purchases made on Coin.
- For MF holdings and discrepancy queries, ALWAYS use this tool + console_mf_pseudo_holdings. NEVER use Kite/Console equity holdings tools.
</facts>

<field_usage>
  <share>tradingsymbol (as fund name) | buy_average (if asked) | buy_value (if asked) | margin (if asked) | total_quantity (if asked)</share>
  <internal>holdings_date (latest demat credit) | failure_date (CRITICAL: if populated → escalate) | available | discrepant (CRITICAL: if >0 → investigate. NEVER share this value with client.) | loan | closing_price</internal>
  <banned>name (not applicable for MF) | client_id | isin | instrument_id | t1 | pending</banned>
</field_usage>
</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
Never share `<banned>` fields. Use `<internal>` fields for reasoning only. NEVER mention "pseudo holdings", "backend systems", "data mismatch", or any internal tool/system names to client. NEVER share or mention the `discrepant` field value to the client (e.g., NEVER say "discrepant value is 0 in both reports"). Use: "Your recently allotted units may take 24-48 hours to sync. If not updated, write back and we will investigate."

### Rule 1: Units Not Visible
**if:** Units missing after allotment
**then:** Check settlement timeline: liquid T day 7 PM, non-liquid T+1 7 PM.
- Within timeline → "Units will be visible by [timeline]."
- Beyond → check `holdings_date` for latest credit. Check **console_mf_tradebook** for trade entry. If trade exists but units missing → check **console_mf_pseudo_holdings**. If mismatch → escalate.

### Rule 2: Discrepancy
**if:** `discrepant` > 0, OR client reports "fix discrepancy" message, OR invested amount showing as "NA"
**then:** Determine the cause:

**Step 1 — Delay allotment discrepancy (most common):**
Check **console_mf_tradebook** or **mf_order_history** for a recent allotment (within last 3-4 days) for this fund. If a recent allotment exists → this is a late delivery discrepancy. "When units are recently allotted, the invested value may temporarily show as 'NA'. This is automatically corrected within 24-48 hours. You do not need to add any trade details for purchases made through Coin. For more details: [Why are the newly allotted units shown as NA on the Coin app?](https://support.zerodha.com/category/mutual-funds/coin-web-app/articles/newly-allotted-units-shown-as-na)"

**Step 2 — Wrongly entered external trades:**
If purchases were made through Coin only (no transfer from other platform), and client added external trade entries manually → ESCALATE TO AGENT. "External trade entries were incorrectly added for this fund. We will request deletion from our end. You do not need to add any trade details for purchases made through Coin."

**Step 3 — Transferred from another platform:**
"Add external trades: Console → Portfolio → Holdings → fund → Add External Trade."

**Step 4 — NFO recently allotted:**
"May auto-resolve in 24-48 hours."

**Step 5 — `failure_date` populated:**
→ Rule 5 (escalate).

- Compare with **console_mf_pseudo_holdings** `discrepant` for cross-check.

### Rule 3: Pledged Units
**if:** `margin` > 0 AND redemption/SWP failing
**then:** "You have [margin] pledged units. Unpledge first: Console → Portfolio → Holdings → fund → Unpledge."

### Rule 4: Buy Average Incorrect
**if:** Wrong buy average
**then:** Check **console_mf_external_trades** — all entries correct/complete? If transferred, verify external entries added. If all correct + `failure_date` empty → escalate.

### Rule 5: Failure Date — Immediate Escalation
**if:** `failure_date` populated
**then:** Escalate to human immediately. "Data inconsistency requires backend investigation for [tradingsymbol]."

### Rule 6: Console vs Coin Value
**if:** Different values shown on Console vs Coin
**then:** "Console displays the NAV as of T-2 days, while Coin displays the NAV as of T-1 day. This difference in NAV dates causes the P&L values to appear different. For the latest valuation, please refer to Coin. For more details: [Why does Console show a different MF NAV?](https://support.zerodha.com/category/mutual-funds/coin-general/coin-reports/articles/mf-nav-of-t-2-days-on-console)"

### Rule 7: Cross-Tool
- Trade entry verification → **console_mf_tradebook**
- Discrepancy comparison → **console_mf_pseudo_holdings**
- Missing external entries → **console_mf_external_trades**
- Loan units query → `loan` field (externally pledged for loan)

### Rule 8: Tool Routing
**CRITICAL:** For ALL MF holdings, discrepancy, and portfolio queries:
- Use **this tool** (console_mf_holdings) + **console_mf_pseudo_holdings** for Coin MF holdings
- NEVER use Kite holdings or Console equity holdings tools for MF queries
- ETF FOF (Fund of Funds) → check here (it's an MF, appears in Coin)
- Pure ETF → check Kite/Console equity holdings (NOT this tool)
