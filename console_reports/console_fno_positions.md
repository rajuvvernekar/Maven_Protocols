# console_fno_positions

## Description

WHEN TO USE:

When clients:
- Ask about open F&O positions (futures or options) for a specific date
- Question unrealized P&L on F&O positions
- Report position quantity mismatch between Kite and Console
- Ask about MTM (Mark-to-Market) obligation on their positions
- Question carry-forward positions or overnight margin
- Ask about position value on a specific date (e.g., for margin or settlement queries)

TRIGGER KEYWORDS: "F&O position", "FnO position", "futures position", "options position", "open position", "open quantity", "carry forward position", "MTM", "mark to market", "position P&L", "position value", "overnight position", "position not showing", "position wrong", "unrealized F&O"

## Protocol

# CONSOLE FNO POSITIONS PROTOCOL

---

## Section A: Reference Data

---

### A1 — Fundamentals

This tool shows a **snapshot of open F&O positions** as of a selected trade date. It supports historical lookups (select any past date to see positions on that day) but does not show real-time intraday data.

**Unrealized P&L** = closing_value − open_value = (close_price − open_average) × open_quantity.

Positive `open_quantity` = long position. Negative `open_quantity` = short position.

Closing price used is the **settlement price** for that date — may differ from last traded price.

Console positions use settlement/closing price; Kite positions use LTP — values will differ during market hours.


---

### A2 — Field Usage Rules

**Shareable fields:**

`trade_date` | `tradingsymbol` | `open_quantity` | `open_average` | `open_value` | `close_price` | `closing_value` | `unrealized_profit` | `unrealized_profit_percentage`

**Internal-only fields** (use for reasoning; communicate outcomes in plain language):

`client_id`

---

### A3 — Segment Mapping

| Segment Code | Covers | Examples |
|---|---|---|
| FO | Equity Futures & Options | NIFTY, BANKNIFTY, SENSEX, stock futures/options |
| CDS | Currency Derivatives | USDINR, EURINR, etc. |
| COM | Commodities (MCX) | GOLD, SILVER, CRUDEOIL, NATURALGAS, etc. |

---

### A4 — Cross-Reference Tools

| Tool | When to Use |
|---|---|
| `console_fno_tradebook` | Trade-level execution details feeding into positions. Use to verify entry trades. |
| `console_fno_pnl` | Realized P&L for closed/expired positions. |

---

### A5 — Escalation Data Template

When escalating, always include: **client ID, tradingsymbol, trade_date, segment, and specific discrepancy.**

---

### A6 — Key F&O Mechanics

**MTM (Mark-to-Market):** Settled daily — profit credited / loss debited based on closing price vs previous day's closing price. Applies to futures and ITM options.

**Positions auto-squared-off on expiry:** ITM options exercised, OTM expire worthless.

**Physical delivery (stock F&O):** Applicable for stock F&O positions expiring ITM. Shares delivered/received T+1 after expiry. Delivery margin blocked from the Wednesday before expiry for stock F&O positions.

**Carry-forward positions:** Positions held overnight incur margin requirements; margin recalculated at EOD.

**Contract symbol format:** underlying + expiry date + strike (for options) + CE/PE (e.g., NIFTY2621727100CE).

**MCX commodity physical delivery:** Zerodha does not support physical delivery of MCX commodity contracts (gold, silver, crude oil, etc.). Positions not closed before the delivery period begins are auto-squared-off by Zerodha. A charge of ₹50 + 18% GST applies per auto-squared-off order.

**Position disappeared:** If position shows on a past date but not current date → position was closed or expired between those dates.

---

## Section B: Decision Flow

---

### Preflight (run on every query)

```
1. Confirm correct segment selected (per A3)
   └─ FO for equity F&O, CDS for currency, COM for commodities.
      Wrong segment = no results.
```

### Route

```
Intent / Condition                                          → Rule
──────────────────────────────────────────────────────────────────────
Client asks about open F&O position                         → Rule 1
MTM debit/credit on ledger                                  → Rule 2
Position value differs between Console and Kite             → Rule 3
Expired / closed position not showing                       → Rule 4
Physical delivery on expiry (stock F&O ITM)                 → Rule 5
Historical position snapshot for a past date                → Rule 6
Margin shortfall / penalty query                            → Rule 7
MCX commodity physical delivery query                       → Rule 8
```

### Scope

- Address the client's query about their F&O position snapshots, unrealized P&L, MTM, and expiry handling.
- Use **A2** field rules in all client communication.
- Frame long/short based on `open_quantity` sign (positive = long, negative = short).

### Fallback

If no route matches, cross-reference with **A4** tools for additional context. If no root cause is found, escalate per **A5**.

---

## Section C: Rules

---

### Rule 1 — Position Verification

1. Your open position in [tradingsymbol] as of [trade_date]: [long/short] [abs(open_quantity)] lots at an average price of ₹[open_average]. The closing price on that date was ₹[close_price], giving an unrealized P&L of ₹[unrealized_profit] ([unrealized_profit_percentage]%).. Frame as long (positive qty) or short (negative qty).

---

### Rule 2 — MTM Obligation Explanation

1. Mark-to-Market (MTM) is settled daily for F&O positions. Each day, the difference between today's closing price and the previous day's closing price is credited (if favorable) or debited (if unfavorable) from your account. This is the daily settlement mechanism for futures and ITM options.

Your position in [tradingsymbol] closed at ₹[close_price] on [trade_date]. The MTM for that day is calculated as: (today's closing price − previous day's closing price) × quantity.. MTM mechanics per **A6**.
2. If client asks for detailed day-by-day MTM calculation → Escalate to support agent. This tool shows position snapshots, not day-by-day MTM breakdown.
---

### Rule 3 — Console vs Kite Position Value Difference

1. Console positions show values based on the settlement/closing price for the selected date, while Kite shows values based on the live last traded price (LTP). These will differ during market hours and may also differ slightly after market close if the settlement price differs from the last traded price..
2. If values differ after EOD settlement → verify both show same `open_quantity`.
   a. Quantity matches but value differs → closing price source difference (normal).
   b. Quantity differs → escalate per **A5**.

---

### Rule 4 — Expired / Closed Position Not Showing

1. Check the position for the previous trade date.
2. If found on earlier date but not on requested date → Your [tradingsymbol] position was closed or expired between [earlier date] and [requested date]. If it expired, ITM options were exercised and OTM options expired worthless..
3. For realized P&L on closed positions → use `console_fno_pnl` (per **A4**).

---

### Rule 5 — Physical Delivery on Expiry (Stock F&O)

1. Stock futures and ITM stock options that expire are subject to physical delivery. If you held a long futures/ITM call position, shares will be credited to your demat account. If you held a short futures/ITM put position, shares will be debited. Physical delivery happens T+1 after expiry.

Delivery margin is blocked from the Wednesday before expiry for stock F&O positions.. Delivery mechanics per **A6**.
2. If client questions delivery margin or charges → Escalate to support agent. Delivery margin and penalty calculations depend on multiple factors not available in this tool.

---

### Rule 6 — Historical Position Snapshot

1. Enter the specific trade_date to retrieve positions open on that day.
2. Your positions as of [trade_date] were: [list tradingsymbol, open_quantity, open_average, unrealized_profit for each]. — list each position's tradingsymbol, open_quantity, open_average, and unrealized_profit.

---

### Rule 7 — Margin Shortfall Queries

1. This tool does not contain margin requirement or penalty calculations.
2. Escalate per **A5** with: client ID, tradingsymbol, trade_date, and client's concern about margin shortfall/penalty.
3. Margin calculations require data outside this tool — escalate to a support agent.

---

### Rule 8 — MCX Commodity Physical Delivery

1. Zerodha does not support physical delivery of MCX commodity contracts. If you do not close your position before the start of the delivery period, Zerodha will auto-square it off. A charge of ₹50 + 18% GST applies per auto-squared-off order. Please ensure you close or roll over your commodity futures position before the delivery period begins.. Policy per **A6** (MCX commodity physical delivery).
2. If client has already been auto-squared-off and disputes the charge → escalate per **A5**.
