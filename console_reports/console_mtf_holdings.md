# console_mtf_holdings

## Description

WHEN TO USE:

When clients:
- Ask about MTF holdings quantity, buy average, or unrealized P&L
- Report MTF holdings not visible or showing wrong quantity
- Report MTF buy average mismatch between Kite and Console
- Ask about MTF interest charges or how interest is calculated
- Ask about MTF auto square-off rules or why shares were squared off
- Ask about converting MTF position to CNC (delivery) or vice versa
- Ask about MTF margin, funded amount, or initial margin
- Ask about MTF obligation or settlement calculation
- Report MTF P&L not matching expectations
- Ask about corporate action impact on MTF holdings (bonus/split credited to MTF)
- Report MTF discrepancy after selling MTF shares

TRIGGER KEYWORDS: "MTF", "margin trading", "funded", "MTF holdings", "MTF interest", "MTF charges", "MTF square off", "auto square off", "MTF conversion", "convert to delivery", "convert to CNC", "MTF buy average", "MTF obligation", "MTF margin", "MTF P&L", "initial margin", "funded amount", "80% breach", "MTF pledge", "MTF brokerage"

## Protocol

# CONSOLE MTF HOLDINGS PROTOCOL 

---

## Section A: Reference Data

---

### A1 — Tool Purpose & Fundamentals

This tool looks up a client's MTF (Margin Trading Facility) holdings. MTF allows clients to buy shares by paying only initial margin (~20–50% depending on stock); Zerodha funds the rest.

Console P&L does not calculate separately for MTF — it uses FIFO across all holdings (CNC + MTF combined). Kite's MTF filter shows buy average calculated only from MTF product type trades, which will differ from Console's FIFO average. Both are correct for their purpose: Console = tax reporting (FIFO), Kite MTF filter = MTF-specific cost tracking.

Backedated MTM is available on Console MTF holdings — client can select a date to view historical MTM.

**Input:** Client ID.

---

### A2 — Field Usage Rules

**Shareable fields:**

`tradingsymbol` | `isin` | `quantity_available` | `buy_average` | `holdings_buy_value` | `closing_value` | `unrealized_profit` | `unrealized_profit_percentage`

**Internal-only fields** (use for reasoning; communicate outcomes in plain language):

`close_price`

**Client-facing terminology:**

| Internal Term | Client-Facing Alternative |
|---|---|
| close_price | Use `closing_value` (= close_price × quantity) when communicating current value to client |

---

### A3 — MTF Charges

| Charge Type | Amount | Notes |
|---|---|---|
| Interest | 0.04%/day (₹40 per lakh) on funded amount | Applied from T+1 day until stocks are sold. On total funded balance, not per scrip. Per-stock breakdown not available. Includes weekends/holidays. |
| Brokerage | ₹20 or 0.3% per order, whichever is lower | Applies to both intraday and delivery MTF trades |
| Square-off | ₹50 + GST per order | Charged when squared off by Zerodha |
| Auto-pledge (on buy) | ₹15 + GST per ISIN | Automatic on MTF purchase. Charges apply once per ISIN per day. |
| Unpledge (on sell) | ₹15 + GST per ISIN | Triggered on sell or MTF-to-CNC conversion. Charges apply once per ISIN per day. |

---

### A4 — Square-Off Rules

**Condition:** Margin shortfall exceeds 80% of funded value (stock price drops significantly, reducing collateral below required threshold).

**Action:** RMS team sells minimum qty needed to restore margin — partial square-off possible. Not all shares necessarily sold. Can happen anytime during market hours when breach detected.

**Post-square-off:** Remaining MTF shares continue as MTF holdings. Temporary discrepancy may appear for 24–28 working hours, then auto-resolves.

**Stock removed from approved list:** Existing MTF positions are NOT auto-squared-off unless a margin breach occurs (see **A9** for full removal rules).

---

### A5 — Conversion Rules (MTF to CNC)

**Requirement:** Client must have sufficient free cash equal to the funded amount. Place conversion request on Console or Kite.

**Insufficient margin:** Conversion fails silently — status may show "Processed" but shares remain under MTF (display issue).

**Ex-date restriction:** Conversions on ex-date of corporate action are not processed — client must retry after ex-date.

**Short delivery:** If MTF position is short-delivered and auto-converted to CNC, interest should stop. If interest continues → escalate for reversal.

---

### A6 — Cross-Reference Tools

| Tool | When to Use |
|---|---|
| `console_eq_holdings` | Regular equity holdings qty, buy avg, discrepancy. MTF qty also appears in console_eq_holdings total_quantity. |
| `console_mtf_conversion` | Track MTF-to-CNC conversion request status, converted qty, and remarks. |
| `console_eq_holdings_breakdown` | Transaction-level view of MTF trades impacting holdings. |

---

### A7 — Links

| Topic | URL / Path |
|---|---|
| MTF approved stock list | zerodha.com/margin/mtf |
| MTF interest statement | Console → Reports → MTF Interest Statement |

---

### A8 — Escalation Data Template

When escalating, always include: **client ID, tradingsymbol(s), specific issue, dates involved, and screenshots if available.**

---

### A9 — Stock Removal from MTF Approved List

**Reclassification (removed from Group 1 securities):** Zerodha notifies the client on the same day. Client has until 4 PM to either sell during market hours or convert to CNC. If neither done by 4 PM, Zerodha converts the MTF position to CNC on the same day.

**General removal (not reclassification):** Existing MTF position is NOT auto-squared-off. Client can continue to hold. Cannot buy more of that stock under MTF. Position only squared off if margin breach occurs per standard square-off rules (per **A4**).

---

### A10 — Response Templates

**R1 — Buy average mismatch (Console vs Kite MTF filter):**
"The buy average on Console is calculated using FIFO across all your holdings of [tradingsymbol] — both regular delivery (CNC) and MTF combined. This is mandated by the Income Tax Department for tax reporting.

The buy average shown under the MTF filter on Kite is calculated only from your MTF trades for that stock. Both values are correct for their respective purposes — Console reflects your tax-reportable average, while the Kite MTF filter shows your MTF-specific cost."

**R2 — Holdings display issue:**
"Your [quantity_available] shares of [tradingsymbol] are showing correctly in our records. Please try logging out and back in, or use a different browser/device."

**R3 — Interest calculation:**
"MTF interest is charged at 0.04% per day (₹40 per lakh) on the funded amount. Interest is applied from T+1 day until the stocks are sold, and accrues daily including weekends and holidays.

Please note that interest is calculated on the total funded amount across all your MTF positions combined — a per-stock interest breakdown is not available. You can view your interest statement on Console → Reports → MTF Interest Statement."

**R4 — Weekend interest:**
"Interest accrues on all calendar days since the funded amount remains outstanding regardless of whether markets are open."

**R5 — Auto square-off explanation:**
"MTF positions are auto-squared-off by our risk management team when the margin shortfall exceeds 80% of the funded value. This typically happens when the stock price drops significantly, reducing the value of your collateral below the required threshold.

Only the minimum quantity needed to restore your margin is sold — not necessarily all your MTF shares. Your remaining [quantity_available] shares of [tradingsymbol] continue as MTF holdings."

**R6 — Post-square-off discrepancy:**
"After an auto square-off, a temporary discrepancy may appear in your holdings. This is automatically resolved within 24–28 working hours. If the discrepancy persists beyond 2 trading days, we will investigate further."

**R7 — Conversion guidance:**
"You can convert your MTF position to regular delivery (CNC) through Kite or Console. To convert, you need sufficient free cash in your account equal to the funded amount for those shares.

If you don't have enough funds, the conversion will fail — it may show as 'Processed' in the status but the shares will remain under MTF. Please verify your available balance before placing the conversion request."

**R8 — Conversion failed (insufficient margin):**
"The conversion was not processed due to insufficient margin. The 'Processed' status is a display issue. Please add the required funds and place a new conversion request."

**R9 — Conversion failed on ex-date:**
"MTF conversions on the ex-date of a corporate action are not processed to avoid complications with the credit handling. Please place the conversion request again after the ex-date."

**R10 — P&L mismatch explanation:**
"Console calculates P&L using FIFO across all your holdings of [tradingsymbol] — both regular delivery and MTF combined. If you held [tradingsymbol] shares as CNC before purchasing under MTF, the FIFO calculation will use the oldest shares first when you sell, which can affect the realized P&L differently than expected.

The P&L figures in your ledger reflect the net settlement (exit value minus entry value for the specific MTF position), while Console P&L reflects FIFO-based accounting. These may differ but both are calculated correctly."

**R11 — Contract note obligation:**
"The contract note records the gross obligation — the full purchase value of the shares — which is the standard format. The initial margin you paid and the funded amount from Zerodha together make up this total. Your MTF ledger will show the breakup: initial margin from your equity ledger and the funded portion as a debit in your MTF ledger."

**R12 — Corporate action on MTF:**
"Corporate action adjustments and credits behave the same for MTF and regular holdings — there is no separate or delayed timeline for MTF positions. Your MTF holdings should reflect the updated quantity once the corporate action credit is processed.

If the update hasn't happened after 2 trading days from credit date, we'll escalate this for investigation."

**R13 — MTF charges breakdown:**
"Here are the charges applicable to MTF positions:
- Interest: 0.04% per day (₹40 per lakh) on funded amount, applied from T+1 day until stocks are sold (includes weekends/holidays)
- Brokerage: ₹20 or 0.3% per order, whichever is lower (both intraday and delivery)
- Square-off by Zerodha: ₹50 + GST per order
- Auto-pledge on buy: ₹15 + GST per ISIN (once per ISIN per day)
- Unpledge on sell or conversion: ₹15 + GST per ISIN (once per ISIN per day)"

**R14 — Reclassification (removed from Group 1):**
"If a stock you hold under MTF is reclassified and removed from Group 1 securities, Zerodha will notify you on the same day. You have until 4 PM to either sell the stock during market hours or convert it to CNC (delivery). If you don't sell or convert by 4 PM, Zerodha will convert your MTF position to CNC on the same day."

**R15 — General removal from MTF list:**
"If a stock is removed from the MTF approved list without reclassification, your existing MTF position is NOT automatically squared off. You can continue to hold the position. However, you cannot buy more of that stock under MTF. The position will only be squared off if a margin breach occurs as per standard square-off rules."

**R16 — Unrealized P&L verification:**
"Your unrealized P&L is calculated as: current market value (₹[closing_value]) minus invested value (₹[holdings_buy_value]) = ₹[unrealized_profit] ([unrealized_profit_percentage]%).

Note: This does not include MTF interest charges, brokerage, or other transaction costs. Your actual profit on exit will be lower after accounting for these charges."

---

## Section B: Decision Flow

---

### Preflight (run on every query)

```
1. Identify the stock (tradingsymbol / ISIN) and the MTF concern
   (interest, square-off, conversion, avg mismatch, charges, etc.)
```

### Route

```
Intent / Condition                                          → Rule
──────────────────────────────────────────────────────────────────────
Buy average mismatch (Console vs Kite MTF filter)           → Rule 1
MTF holdings not visible                                    → Rule 2
MTF interest query                                          → Rule 3
Auto square-off query                                       → Rule 4
MTF-to-CNC conversion query                                → Rule 5
MTF P&L not matching                                        → Rule 6
Contract note shows full obligation                         → Rule 7
Corporate action on MTF holdings                            → Rule 8
MTF charges / unexpected debits                             → Rule 9
Stock removed from MTF approved list                        → Rule 10
Unrealized P&L verification                                 → Rule 11
```

### Scope

- Address the client's query about their MTF holdings, charges, conversions, or square-offs.
- Use **A2** field rules and client-facing terminology in all client communication.
- Do not volunteer information about unrelated MTF topics unless directly relevant.

### Fallback

If no route matches, cross-reference with **A6** tools for additional context. If no root cause is found, escalate per **A8**.

---

## Section C: Rules

---

### Rule 1 — Buy Average Mismatch (Console vs Kite MTF Filter)

1. Respond per **A10-R1**. Both averages are correct for their purpose (per **A1**).

---

### Rule 2 — MTF Holdings Not Visible

1. Check `quantity_available` in this tool.
2. If qty > 0 → display issue. Respond per **A10-R2**.
3. If qty = 0 but client insists → check `console_eq_holdings` (per **A6**) for the same stock. MTF qty may appear in combined holdings. If found there but not here → possible conversion already processed.
4. If not found in either tool AND MTF interest still being charged → escalate per **A8**.

---

### Rule 3 — MTF Interest Calculation

1. Respond per **A10-R3**. Charges per **A3**.
2. If client asks about weekend interest → respond per **A10-R4**.
3. If client says interest charged after selling all MTF positions → verify MTF ledger closing balance was zero on the claimed dates. If balance was non-zero (e.g., settlement timing) → explain. If balance was zero and interest still charged → escalate per **A8**.

---

### Rule 4 — Auto Square-Off

1. Respond per **A10-R5**. Rules per **A4**.
2. If client reports discrepancy after square-off → respond per **A10-R6**. If discrepancy persists beyond 2 trading days → escalate per **A8**.

---

### Rule 5 — MTF Conversion (MTF to CNC)

1. Respond per **A10-R7**. Rules per **A5**.
2. If conversion shows "Processed" but shares still in MTF → check `console_mtf_conversion` (per **A6**) for actual `converted_quantity`.
   a. If `converted_quantity` = 0 → respond per **A10-R8**.
   b. If conversion was 2+ trading days ago and status unclear → escalate per **A8**.
3. If conversion failed on ex-date → respond per **A10-R9**. Per **A5** ex-date restriction.

---

### Rule 6 — MTF P&L Not Matching

1. Respond per **A10-R10**. FIFO context per **A1**.

---

### Rule 7 — MTF Obligation in Contract Note

1. Respond per **A10-R11**.

---

### Rule 8 — Corporate Action Impact on MTF Holdings

1. Respond per **A10-R12**.
2. If CA credits not reflected after 2+ trading days from credit date → escalate per **A8**.

---

### Rule 9 — MTF Charges Breakdown

1. Respond per **A10-R13**. All charge details per **A3**.

---

### Rule 10 — Stock Removed from MTF Approved List

1. Determine which scenario applies (per **A9**):
   a. Reclassification (removed from Group 1) → respond per **A10-R14**.
   b. General removal (not reclassification) → respond per **A10-R15**.

---

### Rule 11 — Unrealized P&L Verification

1. Respond per **A10-R16**.

---

## Section D: General Notes

- MTF interest: 0.04%/day (₹40 per lakh) on funded amount, applied from T+1 day until stocks are sold. Charged on all calendar days including weekends/holidays.
- Interest is on total funded balance, not per scrip — per-stock interest breakdown is not available.
- MTF shares are auto-pledged on purchase (₹15 + GST per ISIN) and auto-unpledged on sell (₹15 + GST per ISIN). Charges apply once per ISIN per day.
- Console P&L uses FIFO across CNC + MTF combined; Kite MTF filter shows MTF-specific average. Both are correct.
- Net settlement for MTF exit: funded amount reversed from MTF ledger, only P&L (exit value − entry value) settled in equity ledger.
- When a stock is removed from the MTF approved list, existing positions are NOT auto-squared-off unless a margin breach occurs.
- Conversions on ex-date of corporate actions are not processed.
- MTF obligation in contract note shows full purchase value (gross obligation) — this is correct.
- Short delivery auto-conversion from MTF to CNC should stop interest accrual; if it does not, escalate for reversal.
- MTF-to-CNC conversion is a self-service action via Kite or Console. Support cannot process conversions on behalf of the client. Selling MTF holdings and rebuying in CNC is not a valid conversion method — it incurs unnecessary charges and tax events.
