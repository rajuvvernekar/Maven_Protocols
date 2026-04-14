# console_mf_pseudo_holdings

## Description

WHEN TO USE:

When clients:
- Ask about current holdings, invested value, or number of units
- Report units not visible after allotment
- Report buy average incorrect
- Ask about pledged or locked units
- Ask about free units available for redemption/SWP
- Report "Fix discrepancy" message on Coin
- Report P&L calculation failure

This is the PRIMARY tool for ALL MF holdings queries. Always check this tool first.

TRIGGER KEYWORDS: "holdings", "units", "buy average", "portfolio", "pledged", "not visible", "XIRR", "invested value", "discrepancy", "fix discrepancy", "PnL calculation failed", "coin"

## Protocol

# CONSOLE MF PSEUDO HOLDINGS PROTOCOL

---

## Section A: Reference Data

### A1 — Tool Purpose & Scope

- **Primary holdings tool — check this first for all MF holdings queries.**
- Shows client-facing holdings as displayed on Coin/Console.
- console_mf_holdings is the secondary tool — used only to cross-check `available` (units for redemption/SWP), `holdings_date`, and `total_quantity`.
- For MF holdings and discrepancy queries, always use this tool first.
- ETF FOF (Fund of Funds, e.g., "Silver ETF FoF", "Gold ETF FoF") is an MF and appears here. Pure ETFs appear in Kite holdings only.
- **Regular plan holdings:** Coin supports direct mutual fund plans only. If a client holds a regular plan (transferred from another platform), SIP and lumpsum purchase options will not be available for that fund on Coin. Regular plans can be identified when `tradingsymbol` does not contain "DIRECT" in the scheme name. The client can search for the direct plan variant on Coin to start a new SIP or lumpsum. Existing regular plan units can be held or redeemed through Coin.
- Scheme name field is `tradingsymbol`.
- `price` = NAV per unit (per-unit cost at allotment). `quantity` = number of units allotted. These are distinct — never swap when sharing order details with the client.
-**Stamp duty:** 0.005% is deducted from the investment amount before units are allotted. The client receives units based on the post-stamp-duty amount, while the investment summary shows the full amount. Example: ₹10,000 investment → stamp duty ₹0.50 → ₹9,999.50 invested → at NAV ₹10, client receives 999.95 units instead of 1,000. Stamp duty is not displayed under charges on Console. This explains minor unit/value differences — it is separate from the discrepancy diagnostic in A4.

### A2 — NAV Display Differences

| Platform | NAV Date |
|---|---|
| Console | T-2 days |
| Coin | T-1 day |

This difference in NAV dates causes P&L values to appear different. For the latest valuation, refer to Coin.

Reference: [Why does Console show a different MF NAV?](https://support.zerodha.com/category/mutual-funds/coin-general/coin-reports/articles/mf-nav-of-t-2-days-on-console)

### A3 — Internal Flags

| Flag | Meaning | Action |
|---|---|---|
| `failure_date` populated | P&L calculation failed | Escalate to support agent immediately — this tool is the authoritative source for failure_date |
| `discrepant` > 0 | Units exist but no matching trade entries in Tradebook | Investigate using Rule 2 diagnostic steps |
| `margin` > 0 | Units are pledged | Authoritative source for pledged unit checks |
| `dividend_type` = payout AND `discrepant` > 0 | Dividend payout fund with discrepancy | Escalate to support agent immediately — payout dividend funds with discrepancies require backend investigation |

### A4 — Discrepancy Causes (Diagnostic Order)

Check in this order — stop at the first match:

| Step | Cause | How to Identify | Action |
|---|---|---|---|
| 1 | Delay allotment (most common) | Recent order found in mf_order_history with `exchange_timestamp` within T+3 working days (excluding weekends and trading/settlement holidays). Cross-check console_mf_tradebook for allotment entry. | Respond per **A9** template R1. Share delay allotment link below. Do NOT suggest app troubleshooting (log out/in, clear cache, refresh) — the issue is settlement-side, not client-side. If specific funds show no values and no Coin purchase history exists, ask the client whether units were transferred from another platform before proceeding — transferred-in units require external trade entries (see Step 3). |
| 1a | Units allotted but invested value not updated | Units are allotted (confirmed in mf_order_history or console_mf_tradebook) but invested value still displays as NA or incorrectly | Respond per **A9** template R2. This is caused by incremental settlement file processing. Share delay allotment link below. |
| 1b | Delay allotment — escalation | Discrepancy from Step 1 persists beyond T+3 working days (client confirms issue is not resolved) | Escalate to support agent. |
| 2 | Wrongly entered external trades | All purchases through Coin + client added external entries manually | Escalate to support agent: "External trade entries were incorrectly added for this fund. We will request deletion from our end." |
| 3 | Transferred from another platform | Units transferred in, no external entries added | "Add external trades: Console → Portfolio → Holdings → fund → Add External Trade." |
| 4 | NFO recently allotted | New Fund Offer units allotted recently | "May auto-resolve in 3–5 days." |
| 5 | failure_date populated | `failure_date` has a value | Escalate to support agent immediately per Rule 1. |

Delay allotment link: [Why are the newly allotted units shown as NA on the Coin app?](https://support.zerodha.com/category/mutual-funds/payments-and-orders/orders-on-coin/articles/coin-app-na-new-units)

### A5 — Field Rules

**Shareable with client (if asked):** `tradingsymbol` (as fund name), `buy_average`, `buy_value`, `dividend_type`, `margin`.

**Internal reasoning only (use for analysis, never share):** `failure_date` (critical — escalate if populated), `available`, `discrepant` (critical — if > 0, investigate; never share value with client), `loan`.

**Suppress (no client use, only for reasoning purpose): client_id, isin, instrument_id, t1, pending

Client communication rules:

Use client-facing language only. Internal tool names ("pseudo holdings", "Console MF Holdings", "backend systems", "data mismatch") and system references are replaced with plain descriptions of what the client sees on Coin.
The discrepant field and unit count comparisons between internal reports are for internal reasoning only. Client-facing responses reference only what is visible on Coin.


### A6 — Tool Routing Reference

| Query Type | Tool | Notes |
|---|---|---|
| All MF holdings queries (default start) | **This tool** | Always start here |
| Units, buy average, portfolio value, pledged units, discrepancy | **This tool** | Authoritative |
| Units available for redemption/SWP | console_mf_holdings (`available`) | Secondary — invoke only for this field |
| Latest demat credit date | console_mf_holdings (`holdings_date`) | Secondary |
| Total quantity verification | console_mf_holdings (`total_quantity`) | Secondary |
| failure_date escalation | **This tool** | Authoritative source — escalation originates here |
| Pledged units / margin | **This tool** (`margin` field) | Authoritative |
| Client account classification (Silo) | get_all_client_data | For collateral margin reflection timeline |
| External trade entries | console_mf_external_trades | For transferred-in units, buy average corrections |
| Trade entry verification | console_mf_tradebook | For allotment verification, FIFO P&L |
| Pure ETF holdings | Kite equity holdings | Not an MF query |
| ETF FOF holdings | **This tool** | ETF FOF is treated as MF |

### A7 — Cross-Reference Protocols

| Topic | Refer to |
|---|---|
| Redeemable units (`available`), demat credit date, total quantity | console_mf_holdings |
| Missing trade entries, allotment verification | console_mf_tradebook |
| External trade entries, transferred-in units, buy average corrections | console_mf_external_trades |
| Order status, allotment confirmation, exchange_timestamp | mf_order_history |
| Non-demat MF unit transfer / dematerialization | Rule 7 (**A8a**) |
| Demat MF unit transfer / CDSL Easiest / ELSS lock-in transfer | Rule 7 (**A8b**) |
| LAS / Loan Against Securities queries | Rule 9 |
| Client account classification (Silo) for collateral timelines | get_all_client_data |

### A8a — Non-Demat MF Unit Transfer (Dematerialization)

For clients who hold non-demat (physical/statement-based) MF units with another platform and want to transfer them to Zerodha:

**Process:** Dematerialization is required before units can be transferred to Zerodha's demat account. If mutual fund units are in physical mode or held in Statement of Account (SOA), they must be dematerialised or destatementized before transferring.

**Charges:**
- ₹150 + 18% GST per scheme (for ELSS: ₹150 per investment within the scheme).
- ₹100 courier charges (one-time).

**Transfer timeline:** Up to 4 days after submitting all required documents.

**Support articles:**
- [How to transfer mutual funds from other platforms to Coin?](https://support.zerodha.com/category/mutual-funds/coin-general/transferring-mf/articles/how-do-i-move-my-existing-mutual-fund-investments-to-coin)
- [What is dematerialization and how to dematerialise MF investments?](https://support.zerodha.com/category/mutual-funds/coin-general/transferring-mf/articles/what-and-how-i-de-materialize-mutual-fund-investments)

### A8b — Demat MF Unit Transfer (CDSL Easiest / Inter-Depository Transfer)

For clients who hold MF units in demat mode with another broker and want to transfer to Zerodha:

**CDSL Easiest method:** If the source broker's depository is CDSL (Zerodha's DP is with CDSL), clients can use the CDSL Easiest online facility for inter-depository transfer.

**ELSS lock-in transfer:** ELSS units under lock-in can only be transferred via the closure cum transfer process to another demat account of the same account holder. Free (unlocked) ELSS units can be transferred without restriction.

**Transfer timeline:** Up to 4 days after submitting all required documents.

**Support article:** [How to transfer shares from another demat account to Zerodha?](https://support.zerodha.com/category/your-zerodha-account/transfer-of-shares-and-conversion-of-shares/transfer-securities/articles/how-do-i-transfer-shares-from-another-demat-account-to-my-zerodha-demat#H1)

### A9 — Response Templates

**R1 — Delay allotment (units not yet allotted):**
"Your order for [fund] of ₹[amount] was placed on [date]. The payment has been confirmed and the order is being processed. Units are typically allotted within T+3 working days. You do not need to add any trade details for purchases made through Coin. The invested value may temporarily show as 'NA' and will update automatically once the allotment is complete."

**R2 — Units allotted, invested value not updated:**
"Your order for [fund] of ₹[amount] was placed on [date]. The payment was settled, and units were allotted on [allotment date]. You received [X] units at a NAV of ₹[NAV]. The invested value display may take up to 24–48 hours to update due to settlement file processing. You can check the correct values in a day or two."

---

## Section B: Decision Flow

### Preflight (run on every query)

1. Fetch pseudo holdings data for the client and relevant fund.
2. Apply field protection per **A5** — identify shareable, internal, and banned fields.
3. **Check failure_date immediately:** if populated → escalate per Rule 1 before any other processing.
4. **Check dividend_type + discrepant:** if `dividend_type` = payout AND `discrepant` > 0 → escalate to support agent immediately per **A3**. Do not proceed with standard diagnostic.
5. Check `discrepant` value — if > 0, flag for investigation.
6. Check `margin` value — if > 0 and query involves redemption/SWP, note for Rule 5.
7. Format amounts with ₹ and Indian comma notation. Format dates as DD MMM YYYY.

### Routing Tree

```
Query relates to MF holdings →
│
├─ Preflight: failure_date populated?
│  → Rule 1 (escalate immediately)
│
├─ Preflight: dividend_type = payout AND discrepant > 0?
│  → Escalate to support agent immediately (per A3)
│
├─ Discrepancy detected (discrepant > 0 / "fix discrepancy" / "NA" invested amount)
│  → Rule 2 (Diagnostic steps per A4)
│
├─ Mismatch between this tool and console_mf_holdings
│  → Rule 3
│
├─ Client questions buy average or invested value
│  → Rule 4
│
├─ Pledged units blocking redemption/SWP, or collateral margin query
│  → Rule 5
│
├─ Console vs Coin value difference
│  → Rule 6
│
├─ Client asks about transferring MF units to Zerodha (demat or non-demat) / dematerialization
│  → Rule 7
│
├─ Fund still showing in portfolio after full redemption (residual decimal units)
│  → Rule 8
│
├─ Client asks about MF units in loan / collateral / LAS
│  → Rule 9
│
└─ General MF holdings query
   → Check data here first, invoke console_mf_holdings only if
     available/holdings_date/total_quantity needed (per A6)
```

### Scope

- Address: MF holdings status, discrepancy diagnosis, buy average verification, pledged units, NAV differences, MF unit transfer guidance (demat and non-demat), and residual unit display issues.
- Share only fields per **A5**. Use client-facing language for all tool references, discrepancy explanations, and unit comparisons.

### Fallback

If no root cause is identified after the diagnostic steps → escalate with fund name, discrepant value (internal), and the specific issue.

---

## Section C: Rules

### Rule 1 — Failure Date: Immediate Escalation

1. If `failure_date` is populated → escalate to human immediately (per **A3**).
2. Escalation message: "Data inconsistency requires backend investigation for [tradingsymbol]."
3. This tool is the authoritative source for `failure_date`. If seen in console_mf_holdings, route escalation here (per **A6**).

### Rule 2 — Discrepancy Detection & Diagnosis

1. Triggered when: `discrepant` > 0, client reports "fix discrepancy" message, or invested amount shows as "NA".
2. **Preflight for discrepancy:** Before entering the A4 diagnostic sequence, check mf_order_history (per **A7**) for recent orders in the affected fund. If recent orders exist, check `exchange_timestamp`: if T+3 working days (excluding weekends and trading/settlement holidays) have not elapsed from `exchange_timestamp` → this is a delay allotment. Respond per **A4** Step 1 with the appropriate template from **A9**. If units are confirmed allotted (in mf_order_history or console_mf_tradebook) but invested value shows as NA or incorrect → respond per **A4** Step 1a with template R2 from **A9**.
3. If no recent orders explain the discrepancy, work through the remaining diagnostic steps in **A4** in order — stop at the first match.
4. For Step 1b (delay allotment — escalation): only if the client confirms the discrepancy has persisted beyond T+3 working days, escalate to support agent.
5. For Step 2 (wrongly entered external trades): verify via console_mf_external_trades (per **A7**). If confirmed → escalate.
6. For Step 3 (transferred from another platform): guide client to add external trades using the Console path from **A4**.
7. For Step 4 (NFO): advise to wait 3–5 days.
8. For Step 5 (failure_date): route to Rule 1.

### Rule 3 — Mismatch Between Reports

1. If `available` or `discrepant` here differs from console_mf_holdings values → check console_mf_tradebook (per **A7**) for missing trade entries.
2. If trade entry exists but mismatch persists → escalate.

### Rule 4 — Buy Average / Investment Value

1. This tool is authoritative for `buy_average` and `buy_value`.
2. If values differ from client's expectation → check console_mf_external_trades (per **A7**) for missing or incorrect external entries.
3. If investment value not updated → may be a settlement delay (liquid: T day by 7 PM; non-liquid: T+1 by 7 PM).

### Rule 5 — Pledged Units

1. Confirm: `margin` > 0 (per **A3** — this field is authoritative here).
2. Check get_all_client_data for the client's Silo classification (per **A7**). If Silo = K → collateral margins from pledged mutual funds are updated at end of day only (not within 15 minutes). Respond: "Your pledge has been processed successfully. Collateral margins from pledged mutual funds are updated at end of day. The margin will be available from the next trading day."
3. For all other Silos or when the query is about redemption/SWP (not collateral): Respond: "You have [margin] pledged units. To redeem or set up an SWP, you'll need to unpledge first: Console → Portfolio → Holdings → [fund] → Unpledge."

### Rule 6 — Console vs Coin Value Difference

1. Respond using **A2**: "Console displays the NAV as of T-2 days, while Coin displays the NAV as of T-1 day. This difference in NAV dates causes the P&L values to appear different. For the latest valuation, please refer to Coin."
2. Share link from **A2**.

### Rule 7 — MF Unit Transfer to Zerodha

1. If client holds non-demat (physical/statement-based) MF units → dematerialization is required first (per **A8a**). Respond: "To transfer mutual fund units from another platform to Coin, the units need to be converted to demat form (dematerialization). Charges apply: ₹150 + 18% GST per scheme (₹150 per investment for ELSS schemes), plus ₹100 courier charges. If your units are in physical mode or held in Statement of Account (SOA), they must be dematerialised or destatementized before transferring." Share support article links from **A8a**.
2. If client holds MF units in demat mode with another broker → guide per **A8b**. If the source broker's depository is CDSL, the client can use the CDSL Easiest online facility. For ELSS units under lock-in, transfer is only via the closure cum transfer process to another demat account of the same holder. Share support article link from **A8b**.
3. Once units are transferred → they will appear in this tool. The client may then need to add external trade entries (Console → Portfolio → Holdings → fund → Add External Trade) for correct buy average and P&L calculation.

### Rule 8 — Residual Decimal Units After Full Redemption

1. Triggered when: client reports a fund still showing in their portfolio after full redemption.
2. Check console_mf_pseudo_holdings for the fund's `quantity`. Cross-check against console_mf_holdings `total_quantity` for the same fund.
3. If the fund exists in console_mf_pseudo_holdings but not in console_mf_holdings (or units mismatch between the two) → this is a residual decimal unit display issue requiring a backend data rerun.
4. Escalate — "Residual decimal units detected for [tradingsymbol] after full redemption. Backend data rerun required to clear the display."

### Rule 9 — LAS / Loan Against Securities Redirect

1. If the client asks about MF units not appearing in their loan, collateral, or LAS (Loan Against Securities) facility → redirect to the capital support team.
2. Respond: "For queries related to loans against mutual fund holdings, please email capitalsupport@zerodha.com. They will be able to assist you with this."
3. This is outside MF protocol scope.


---
---\
