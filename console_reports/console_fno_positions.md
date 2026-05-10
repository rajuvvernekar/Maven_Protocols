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

TAGS: holdings

## Protocol

# CONSOLE FNO POSITIONS PROTOCOL

---

## Section A: Reference Data

---

### A1 — Fundamentals

- **Unrealized P&L** = closing_value − open_value = (close_price − open_average) × open_quantity.  
- Positive `open_quantity` = long position. Negative `open_quantity` = short position.  
- Closing price used is the settlement price for that date — may differ from last traded price.  
- Margin requirements, penalty calculations, and delivery margin amounts are not available in this tool.

---

### A2 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |  
|---|---|  
| `trade_date` | Date of the position |  
| `tradingsymbol` | Trading symbol of the instrument |  
| `open_quantity` | Number of open contracts in the position |  
| `open_average` | Average entry price of the open position |  
| `open_value` | Total value of the position at entry price |  
| `close_price` | Current closing price |  
| `closing_value` | Current value of the position (close price × quantity) |  
| `unrealized_profit` | Unrealized P&L on the open position |  
| `unrealized_profit_percentage` | Unrealized P&L as a percentage |

**Non-shareable:**

| Field | Interpretation |  
|---|---|  
| `client_id` | Internal client identifier |

---

### A3 — Segment Mapping

| Segment Code | Covers | Examples |  
|---|---|---|  
| FO | Equity Futures & Options | NIFTY, BANKNIFTY, SENSEX, stock futures/options |  
| CDS | Currency Derivatives | USDINR, EURINR, etc. |  
| COM | Commodities (MCX) | GOLD, SILVER, CRUDEOIL, NATURALGAS, etc. |

---

### A4 — Escalation Data

- Include when escalating to human agent: client ID, tradingsymbol, trade_date, segment, specific discrepancy.

---

### A5 — Key F&O Mechanics

- **MTM (Mark-to-Market):** Settled daily — profit credited / loss debited based on closing price vs previous day's closing price. Applies to futures and ITM options. This tool shows position snapshots only — day-by-day MTM breakdown is not available here.  
- **Auto-square-off on expiry:** ITM options exercised; OTM options expire worthless.  
- **Physical delivery (stock F&O):** Stock futures and ITM stock options expiring are subject to physical delivery. Long futures / ITM call → shares credited to demat T+1 after expiry. Short futures / ITM put → shares debited. Delivery margin blocked from the Wednesday before expiry.  
- **Carry-forward positions:** Positions held overnight incur margin requirements; margin recalculated at EOD.  
- **Contract symbol format:** underlying \+ expiry date \+ strike (for options) \+ CE/PE (e.g., NIFTY2621727100CE).  
- **MCX commodity physical delivery:** Zerodha does not support physical delivery of MCX commodity contracts. Positions not closed before the delivery period are auto-squared-off, with a charge of ₹50 \+ 18% GST per order.  
- **Position disappeared:** If a position appears on a past date but not on the current date, it was closed or expired in between. Realized P&L for closed/expired positions is available via `console_fno_pnl`.  
- **Console vs Kite price source:** Console positions use the settlement/closing price for the selected date; Kite positions use live LTP. Values will differ during market hours and may differ slightly after market close if settlement price differs from LTP.

---

## Section B: Decision Flow

### Routing

```  
Route by scenario  
   ├─ Open F&O position verification → Rule 1  
   ├─ MTM debit / credit on ledger → Rule 2  
   ├─ Position value differs between Console and Kite → Rule 3  
   ├─ Expired / closed position not showing → Rule 4  
   ├─ Physical delivery on expiry (stock F&O ITM) → Rule 5  
   ├─ Historical position snapshot for a past date → Rule 6  
   ├─ Margin shortfall / penalty query → Rule 7  
   └─ MCX commodity physical delivery query → Rule 8  
```

### Fallback

If no route matches → escalate to human agent.

---

## Section C: Rules

---

### Rule 1 — Position Verification

- Identify direction from `open_quantity` (positive = long, negative = short) and communicate the position details using shareable fields per A2.

---

### Rule 2 — MTM Obligation Explanation

1. Explain MTM mechanics per A5.  
2. If client asks for detailed day-by-day MTM calculation → escalate to human agent per A5.

---

### Rule 3 — Console vs Kite Position Value Difference

1. Explain the price source difference per A5 (Console vs Kite price source).  
2. If values differ after EOD settlement → verify both show the same `open_quantity`.  
   - Quantity matches but value differs → closing price source difference, normal.  
   - Quantity differs → escalate to human agent.

---

### Rule 4 — Expired / Closed Position Not Showing

1. Check the position for the previous trade date.  
2. If found on earlier date but not on requested date → explain per A5 (Position disappeared).  
3. For realized P&L on closed positions → invoke `console_fno_pnl`.

---

### Rule 5 — Physical Delivery on Expiry (Stock F&O)

1. Explain delivery mechanics per A5 (Physical delivery).  
2. If client questions delivery margin or charges → escalate to human agent per A4. Margin and penalty calculations are not available in this tool per A1.

---

### Rule 6 — Historical Position Snapshot

1. Communicate that positions retrieved for a past `trade_date` reflect what was open on that day — `open_quantity`, `open_average`, and `unrealized_profit` are as of that date's settlement price.  
2. List each position with `tradingsymbol`, `open_quantity`, `open_average`, and `unrealized_profit`.

---

### Rule 7 — Margin Shortfall Queries

- Margin requirements and penalty calculations are not available in this tool per A1 → escalate to human agent.

---

### Rule 8 — MCX Commodity Physical Delivery

1. Explain policy per A5 (MCX commodity physical delivery).  
2. If client has already been auto-squared-off and disputes the charge → escalate to human agent.
