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

TAGS: margins, holdings

## Protocol

# CONSOLE MTF HOLDINGS PROTOCOL

---

## Section A: Reference Data

### A1 — Fundamentals

- MTF allows clients to buy shares by paying only initial margin (\~20–50% depending on stock); Zerodha funds the rest.
- Console P&L does not calculate separately for MTF — it uses FIFO across all holdings (CNC \+ MTF combined).
- Kite's MTF filter shows buy average calculated only from MTF product type trades, which differs from Console's FIFO average. Both are correct for their purpose: Console = tax reporting (FIFO); Kite MTF filter = MTF-specific cost tracking.
- Back dated MTM is available on Console MTF holdings — client can select a date to view historical MTM.
- Tool data for market holidays and weekends may return nil/empty — this does not mean holdings don't exist. Use the most recent trading day for date-specific queries.

---

### A2 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |
|---|---|
| `tradingsymbol` | Trading symbol of the stock |
| `isin` | ISIN code of the instrument |
| `quantity_available` | Number of shares available for trading |
| `buy_average` | Average buy price per share |
| `holdings_buy_value` | Total buy value of the holding |
| `closing_value` | Current value of the holding (close price × quantity) |
| `unrealized_profit` | Unrealized P&L on the holding |
| `unrealized_profit_percentage` | Unrealized P&L as a percentage |

**Non-shareable:**

| Field | Interpretation |
|---|---|
| `close_price` | Raw closing price per share — use `closing_value` when communicating current value to client |

---

### A3 — MTF Charges

| Charge Type | Amount | Notes |
|---|---|---|
| Interest | 0.04%/day (₹40 per lakh) on funded amount | Applied from T+1 day until stocks are sold. On total funded balance, not per scrip. Per-stock breakdown not available. Includes weekends/holidays. |
| Brokerage | ₹20 or 0.3% per order, whichever is lower | Applies to both intraday and delivery MTF trades |
| Square-off | ₹50 \+ GST per order | Charged when squared off by Zerodha |
| Auto-pledge (on buy) | ₹15 \+ GST per ISIN | Automatic on MTF purchase. Once per ISIN per day. |
| Unpledge (on sell) | ₹15 \+ GST per ISIN | Triggered on sell or MTF-to-CNC conversion. Once per ISIN per day. |

---

### A4 — Square-Off Rules

- **Condition:** Margin shortfall exceeds 80% of funded value.
- **Action:** RMS team sells minimum qty needed to restore margin — partial square-off possible. Can happen anytime during market hours when breach is detected.
- **Post-square-off:** Remaining MTF shares continue as MTF holdings. Temporary discrepancy may appear for 24–28 working hours, then auto-resolves.
- **Stock removed from approved list:** Existing MTF positions are NOT auto-squared-off unless a margin breach occurs (see **A8**).

---

### A5 — Conversion Facts (MTF to CNC)

- Conversion requires sufficient free cash equal to the funded amount. Request placed on Console or Kite.
- Insufficient funds: conversion fails silently — status may show "Processed" but shares remain under MTF (display issue).
- Ex-date restriction: conversions on ex-date of a corporate action are not processed — client must retry after ex-date.
- Short delivery: if MTF position is short-delivered and auto-converted to CNC, interest should stop accruing on the converted quantity.
- Same-day sell and re-buy (EQ series): if a client sells MTF shares and re-buys the same stock on the same day in any product type, trades are netted off as intraday for EQ category stocks — holdings category remains unchanged (MTF stays MTF). Does not apply to BE/T2T category stocks.

---

### A6 — Links

| Topic | URL / Path |
|---|---|
| MTF approved stock list | zerodha.com/margin/mtf |
| MTF interest statement | Console → Funds → Interest statement → select MTF → select date |

A full-year downloadable MTF holdings statement is not available. Zerodha does not create custom reports or statements on request. The MTF Interest Statement and tradebook download are the only available alternatives for MTF-related data.

---

### A7 — Escalation Required Data

Escalate to human agent. Include when escalating: client ID, tradingsymbol(s), specific issue, dates involved, and screenshots if available.

---

### A8 — Stock Removal from MTF Approved List

**Reclassification (removed from Group 1 securities):** Zerodha notifies the client on the same day. Client has until 4 PM to either sell during market hours or convert to CNC. If neither is done by 4 PM, Zerodha converts the MTF position to CNC on the same day.

**General removal (not reclassification):** Existing MTF position is NOT auto-squared-off. Client can continue to hold. Cannot buy more of that stock under MTF. Position only squared off if a margin breach occurs per **A4**.

---

## Section B: Decision Flow

### Routing

```
Query relates to MTF holdings →
│
├─ Buy average mismatch (Console vs Kite MTF filter)             → Rule 1
├─ MTF holdings not visible                                      → Rule 2
├─ MTF interest query                                            → Rule 3
├─ Auto square-off query                                         → Rule 4
├─ MTF-to-CNC conversion query                                   → Rule 5
├─ MTF P&L not matching                                          → Rule 6
├─ Contract note shows full obligation                           → Rule 7
├─ Corporate action on MTF holdings                              → Rule 8
├─ MTF charges / unexpected debits                               → Rule 9
├─ Stock removed from MTF approved list                          → Rule 10
└─ Unrealized P&L verification                                   → Rule 11
```

### Fallback

If no route matches, interpret MTF holdings data using Section A. If no root cause is identified, ESCALATE TO HUMAN AGENT per A7.

---

## Section C: Rules

### Rule 1 — Buy Average Mismatch (Console vs Kite MTF Filter)

1. Explain per **A1**: Console uses FIFO across all holdings (CNC \+ MTF combined) for tax reporting. Kite's MTF filter uses only MTF trades. Both are correct for their respective purposes.

---

### Rule 2 — MTF Holdings Not Visible

1. Check `quantity_available` in this tool.
2. If `quantity_available` > 0 → display issue. Advise client to log out and back in, or try a different browser/device.
3. If `quantity_available` = 0 → Invoke `console_eq_holdings` and Invoke `console_ledger` (MTF ledger type) before concluding no MTF holdings exist.
   - If `console_ledger` MTF closing balance shows Debit → funded amount is outstanding; MTF holdings exist.
4. If not found in either tool AND MTF interest is still being charged → ESCALATE TO HUMAN AGENT.

---

### Rule 3 — MTF Interest Calculation

1. Explain interest rate, accrual timing, and statement location per **A3** and **A6**.
2. If client asks about weekend interest: interest accrues on all calendar days — funded amount remains outstanding regardless of market hours.
3. If client says interest was charged after selling all MTF positions:
   - Invoke `console_ledger` (MTF ledger type) and verify closing balance was zero on the claimed dates.
   - If balance was non-zero (e.g., due to settlement timing) → explain the timing.
   - If balance was zero and interest was still charged → ESCALATE TO HUMAN AGENT.

---

### Rule 4 — Auto Square-Off

1. Explain per **A4**: square-off triggers when margin shortfall exceeds 80% of funded value; only minimum qty needed to restore margin is sold; remaining shares continue as MTF.
2. If client reports discrepancy after square-off: temporary discrepancy resolves automatically within 24–28 working hours.
   - If discrepancy persists beyond 2 trading days → ESCALATE TO HUMAN AGENT.

---

### Rule 5 — MTF-to-CNC Conversion Query

1. Explain conversion requirements per **A5**: free cash equal to funded amount required; if insufficient, conversion fails silently and may show "Processed" while shares remain under MTF.
2. If conversion shows "Processed" but shares still in MTF → Invoke `console_mtf_conversion` and check actual `converted_quantity`:
   - `converted_quantity` = 0 → conversion not processed due to insufficient margin; "Processed" status is a display issue; client should add funds and place a new request.
   - If conversion was 2+ trading days ago and status is still unclear → ESCALATE TO HUMAN AGENT.
3. If conversion failed on ex-date → per **A5**, conversions on ex-date are not processed; client should retry after ex-date.
4. If client sold MTF shares and re-bought in CNC same day but holdings still show MTF:
   - Invoke `console_eq_holdings_breakdown` to verify both trades.
   - If stock is EQ series (not BE/T2T) and both trades exist on the same day → trades were netted off as intraday per **A5**; holdings category remains unchanged; client should use the conversion flow to move shares from MTF to CNC.
5. If auto-converted from short delivery → verify interest has stopped. If interest is still being charged on the converted quantity → ESCALATE TO HUMAN AGENT.

---

### Rule 6 — MTF P&L Not Matching

1. Explain per **A1**: Console uses FIFO across all holdings (CNC \+ MTF combined). If client held CNC shares before MTF purchase, FIFO uses oldest shares first on sell, affecting realized P&L. Ledger P&L reflects net settlement for the specific MTF position; Console P&L reflects FIFO accounting — both are correct.

---

### Rule 7 — Contract Note Shows Full Obligation

1. Contract note records gross obligation (full purchase value) — standard format. Initial margin paid by client \+ funded amount from Zerodha = total. MTF ledger shows the breakup: initial margin in equity ledger, funded portion as debit in MTF ledger.

---

### Rule 8 — Corporate Action on MTF Holdings

1. CA adjustments and credits work the same for MTF and regular holdings — no separate or delayed timeline.
2. If CA credits not reflected after 2+ trading days from credit date → ESCALATE TO HUMAN AGENT.

---

### Rule 9 — MTF Charges / Unexpected Debits

1. Share charges breakdown per **A3**.

---

### Rule 10 — Stock Removed from MTF Approved List

1. Determine which scenario applies per **A8**:
   - Reclassification (removed from Group 1): client notified same day; has until 4 PM to sell or convert to CNC; if neither done, Zerodha converts to CNC on the same day.
   - General removal (not reclassification): existing MTF position not auto-squared-off; client can continue to hold but cannot buy more under MTF; square-off only if margin breach per **A4**.

---

### Rule 11 — Unrealized P&L Verification

1. Per **A2** shareable fields: unrealized P&L = `closing_value` − `holdings_buy_value` = `unrealized_profit` (`unrealized_profit_percentage`%). Note: excludes MTF interest, brokerage, and other charges — actual profit on exit will be lower.
