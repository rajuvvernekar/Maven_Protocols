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

All rules reference these blocks as single sources of truth.

### A1 — Tool Purpose & Scope

- **Primary holdings tool — check this first for all MF holdings queries.**
- Shows client-facing holdings as displayed on Coin/Console.
- console_mf_holdings is the secondary tool — used only to cross-check `available` (units for redemption/SWP), `holdings_date`, and `total_quantity`.
- For MF holdings and discrepancy queries, always use this tool first.
- ETF FOF (Fund of Funds, e.g., "Silver ETF FoF", "Gold ETF FoF") is an MF and appears here. Pure ETFs appear in Kite holdings only.
- Scheme name field is `tradingsymbol`.
- `price` = NAV per unit (per-unit cost at allotment). `quantity` = number of units allotted. These are distinct — never swap when sharing order details with the client.

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
| `failure_date` populated | P&L calculation failed | **ESCALATE** immediately — this tool is the authoritative source for failure_date |
| `discrepant` > 0 | Units exist but no matching trade entries in Tradebook | Investigate using Rule 2 diagnostic steps |
| `margin` > 0 | Units are pledged | Authoritative source for pledged unit checks |

### A4 — Discrepancy Causes (Diagnostic Order)

Check in this order — stop at the first match:

| Step | Cause | How to Identify | Action |
|---|---|---|---|
| 1 | Delay allotment (most common) | Recent allotment (within 3–4 days) found in console_mf_tradebook or mf_order_history | "Invested value may temporarily show as 'NA'. Automatically corrected within 24–48 hours. You do not need to add any trade details for purchases made through Coin." Share link below. Do NOT suggest app troubleshooting (log out/in, clear cache, refresh) — the issue is settlement-side, not client-side. **If discrepancy persists beyond 48 hours:** **ESCALATE** — agent review needed. Additionally, if specific funds show no values and no Coin purchase history exists, ask the client whether units were transferred from another platform before proceeding — transferred-in units require external trade entries (see Step 3). |
| 2 | Wrongly entered external trades | All purchases through Coin + client added external entries manually | **ESCALATE** — agent review needed: "External trade entries were incorrectly added for this fund. We will request deletion from our end." |
| 3 | Transferred from another platform | Units transferred in, no external entries added | "Add external trades: Console → Portfolio → Holdings → fund → Add External Trade." |
| 4 | NFO recently allotted | New Fund Offer units allotted recently | "May auto-resolve in 3–5 days." |
| 5 | failure_date populated | `failure_date` has a value | **ESCALATE** immediately per Rule 1. |

Delay allotment link: [Why are the newly allotted units shown as NA on the Coin app?](https://support.zerodha.com/category/mutual-funds/coin-web-app/articles/newly-allotted-units-shown-as-na)

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
| Order status, allotment confirmation | mf_order_history |
| Non-demat MF unit transfer / dematerialization | Rule 7 (**A8**) |

### A8 — Non-Demat MF Unit Transfer (Dematerialization)

For clients who hold non-demat (physical/statement-based) MF units with another platform and want to transfer them to Zerodha:

**Process:** Dematerialization is required before units can be transferred to Zerodha's demat account.

**Charges:**
- ₹150 + 18% GST per scheme (for ELSS: ₹150 per investment within the scheme).
- ₹100 courier charges (one-time).

**Support article:** [How to transfer mutual funds from other platforms to Coin?](https://support.zerodha.com/category/mutual-funds/coin-web-app/articles/transfer-mutual-funds-to-coin)

---

**Escalation behavior:** When any rule in this protocol says **ESCALATE**, do not draft a customer-facing response. Instead, output only: **HUMAN AGENT ACTION REQUIRED** — followed by the reason from the rule. The human agent will handle the query manually.

## Section B: Decision Flow

### Preflight (run on every query)

1. Fetch pseudo holdings data for the client and relevant fund.
2. Apply field protection per **A5** — identify shareable, internal, and banned fields.
3. **Check failure_date immediately:** if populated → escalate per Rule 1 before any other processing.
4. Check `discrepant` value — if > 0, flag for investigation.
5. Check `margin` value — if > 0 and query involves redemption/SWP, note for Rule 5.
6. Format amounts with ₹ and Indian comma notation. Format dates as DD MMM YYYY.

### Routing Tree

```
Query relates to MF holdings →
│
├─ Preflight: failure_date populated?
│  → Rule 1 (**ESCALATE** immediately)
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
├─ Pledged units blocking redemption/SWP
│  → Rule 5
│
├─ Console vs Coin value difference
│  → Rule 6
│
├─ Client asks about transferring non-demat MF units to Zerodha / dematerialization
│  → Rule 7
│
└─ General MF holdings query
   → Check data here first, invoke console_mf_holdings only if
     available/holdings_date/total_quantity needed (per A6)
```

### Scope

- Address: MF holdings status, discrepancy diagnosis, buy average verification, pledged units, NAV differences, and non-demat MF unit transfer guidance.
- Do not volunteer: internal field values (per **A5**), tool/system names, discrepant field values, or unit count comparisons between reports.

### Fallback

If no root cause is identified after the diagnostic steps → escalate with fund name, discrepant value (internal), and the specific issue.

---

## Section C: Rules

Rules reference Section A blocks. They do not redefine what is already defined there.

### Rule 1 — Failure Date: Immediate Escalation

1. If `failure_date` is populated → escalate to human immediately (per **A3**).
2. Escalation message: "Data inconsistency requires backend investigation for [tradingsymbol]."
3. This tool is the authoritative source for `failure_date`. If seen in console_mf_holdings, route escalation here (per **A6**).

### Rule 2 — Discrepancy Detection & Diagnosis

1. Triggered when: `discrepant` > 0, client reports "fix discrepancy" message, or invested amount shows as "NA".
2. Work through the diagnostic steps in **A4** in order — stop at the first match.
3. For Step 1 (delay allotment): check console_mf_tradebook or mf_order_history (per **A7**) for recent allotment within 3–4 days. If found, respond with the delay allotment explanation from **A4**. Do not suggest app troubleshooting. If the discrepancy has persisted beyond 48 hours → **ESCALATE** — agent review needed. If no Coin purchase history exists for the fund, ask the client whether units were transferred from another platform before proceeding.
4. For Step 2 (wrongly entered external trades): verify via console_mf_external_trades (per **A7**). If confirmed → escalate.
5. For Step 3 (transferred from another platform): guide client to add external trades using the Console path from **A4**.
6. For Step 4 (NFO): advise to wait 3–5 days.
7. For Step 5 (failure_date): route to Rule 1.

### Rule 3 — Mismatch Between Reports

1. If `available` or `discrepant` here differs from console_mf_holdings values → check console_mf_tradebook (per **A7**) for missing trade entries.
2. If trade entry exists but mismatch persists → escalate.

### Rule 4 — Buy Average / Investment Value

1. This tool is authoritative for `buy_average` and `buy_value`.
2. If values differ from client's expectation → check console_mf_external_trades (per **A7**) for missing or incorrect external entries.
3. If investment value not updated → may be a settlement delay (liquid: T day by 7 PM; non-liquid: T+1 by 7 PM).

### Rule 5 — Pledged Units

1. Confirm: `margin` > 0 (per **A3** — this field is authoritative here).
2. Respond: "You have [margin] pledged units. To redeem or set up an SWP, you'll need to unpledge first: Console → Portfolio → Holdings → [fund] → Unpledge."

### Rule 6 — Console vs Coin Value Difference

1. Respond using **A2**: "Console displays the NAV as of T-2 days, while Coin displays the NAV as of T-1 day. This difference in NAV dates causes the P&L values to appear different. For the latest valuation, please refer to Coin."
2. Share link from **A2**.

### Rule 7 — Non-Demat MF Unit Transfer to Zerodha

1. If client holds non-demat (physical/statement-based) MF units with another platform and wants to transfer to Zerodha → dematerialization is required first (per **A8**).
2. Respond: "To transfer mutual fund units from another platform to Coin, the units need to be converted to demat form (dematerialization). Charges apply: ₹150 + 18% GST per scheme (₹150 per investment for ELSS schemes), plus ₹100 courier charges." Share support article link from **A8**.
3. Once units are dematerialized and transferred → they will appear in this tool. The client may then need to add external trade entries (Console → Portfolio → Holdings → fund → Add External Trade) for correct buy average and P&L calculation.

---

## Section D: General Notes

1. This is the primary MF holdings tool. Every MF holdings query starts here. console_mf_holdings is secondary and should only be invoked for three specific fields: `available`, `holdings_date`, `total_quantity`.
2. The `failure_date` check in Preflight step 3 is an absolute gate — if populated, escalate before doing anything else. No diagnostic steps, no client communication, just escalate.
3. Delay allotment (A4 Step 1) is the most common cause of discrepancies. The critical instruction is to never suggest app troubleshooting (log out, clear cache, refresh) for this issue — it's settlement-side, not client-side. Suggesting troubleshooting wastes the client's time and erodes trust.
4. `price` = NAV per unit and `quantity` = number of units. Swapping these in client communication is a common error — always verify before sharing.
5. Stamp duty on MF purchases: A stamp duty of 0.005% is deducted from the investment amount before units are allotted. This means the client receives units based on the post-stamp-duty amount, while the investment summary shows the full amount. Example: ₹10,000 investment → stamp duty of ₹0.50 → ₹9,999.50 actually invested → at NAV ₹10, client receives 999.95 units instead of 1,000. Stamp duty is currently not displayed under charges on Console. If a client asks why they received slightly fewer units than expected for their investment amount, stamp duty is the explanation. This is a minor unit/value difference — it is separate from the discrepancy diagnostic in A4 (which covers missing trade entries, transferred units, and settlement delays).
