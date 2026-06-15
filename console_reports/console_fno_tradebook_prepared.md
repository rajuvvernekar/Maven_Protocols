# console_fno_tradebook_prepared

## Description

WHEN TO USE:

When clients:
- Ask about F&O trade history, execution details, or trade confirmation
- Report an F&O trade missing from tradebook
- Question execution price, quantity, or timing of a futures/options trade
- Ask to confirm strike price, expiry date, or instrument type of a contract
- Question why contract symbol changed (e.g., after corporate action on underlying)
- Ask if a trade was executed in FO, CDS, or COM segment
- Ask about F&O trades for any period (recent or older)
- Ask about contract note charges or MTM for F&O trades (requires manual handling)
- Need full F&O tradebook for tax filing, audit, or compliance
- Request F&O tradebook since account inception or for a past financial year
- Ask about old F&O trades to understand historical P&L or position
- Have a closed account and request historical F&O trade data

TRIGGER KEYWORDS: "FnO tradebook", "F&O trade", "futures trade", "options trade", "FnO execution", "strike price", "expiry date", "contract details", "FnO order id", "FnO trade id", "derivative trade", "FnO trade history", "old F&O trades", "last year F&O", "financial year", "historical F&O trades", "F&O since inception", "full derivative tradebook", "closed account F&O"

TAGS: orders, reports

## Protocol


# CONSOLE FNO TRADEBOOK PREPARED PROTOCOL

## Section A: Reference Data

### A1 — Fundamentals

- Each entry represents a single executed trade. One order may have multiple fills (multiple `trade_id`s for the same `order_id`).
- For charges, MTM calculations, and obligation breakdowns: contract note must be referred manually — not available in this tool.

---

### A2 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |
|---|---|
| `trade_date` | Date the trade was executed |
| `order_execution_time` | Timestamp of trade execution |
| `tradingsymbol` | Trading symbol of the instrument |
| `exchange` | Exchange on which the trade was executed |
| `segment` | Segment — FO (equity F&O), CDS (currency), COM (commodities) |
| `trade_type` | Buy or Sell |
| `quantity` | Number of contracts traded |
| `price` | Execution price per unit |
| `order_id` | Order identifier |
| `trade_id` | Trade identifier |
| `strike` | Strike price — populated for options only |
| `expiry_date` | Contract expiry date |
| `instrument_type` | FUT = futures; OPT = options |

**Non-shareable:**

| Field | Interpretation |
|---|---|
| `client_id` | Internal client identifier |

---

### A3 — Segment Mapping

| Segment Code | Covers |
|---|---|
| FO | Equity F&O |
| CDS | Currency Derivatives |
| COM | Commodities |

---

### A4 — Instrument Type Identification

| Field Value / Pattern | Contract Type |
|---|---|
| `instrument_type` = FUT | Futures contract |
| `instrument_type` = OPT + tradingsymbol ends with CE | Call option |
| `instrument_type` = OPT + tradingsymbol ends with PE | Put option |
| `strike` field | Strike price of the option contract (populated for options only) |
| `expiry_date` field | Last trading day of the contract |

- **Contract symbol format:** underlying + expiry + strike + CE/PE (e.g., NIFTY2621727100CE = NIFTY, 26 Feb 2026 expiry, 27100 strike, Call).

---

### A5 — Corporate Action Impact on F&O Contracts

When a corporate action occurs on the underlying stock (e.g., stock split, bonus), the exchange adjusts derivative contracts:

- **Options:** Strike price adjusted (Old Strike / Adjustment Factor), market lot adjusted (Old Lot × Adjustment Factor).
- **Futures:** Base price adjusted (Old Price / Adjustment Factor), market lot adjusted (Old Lot × Adjustment Factor).
- The contract symbol itself does not change — strike price and lot size change. Position value remains the same; only contract terms are adjusted.
- **Example — ANGELONE 10:1 split:** Old lot 250 → New lot 2500. Old strike ₹5000 → New strike ₹500.

---

### A6 — Links

| Topic | URL |
|---|---|
| How to download trade and funds reports | https://support.zerodha.com/category/console/reports/other-queries/articles/how-to-download-trade-and-funds-reports-in-pdf |
| Where to see trades for a particular period | https://support.zerodha.com/category/console/reports/other-queries/articles/where-can-i-see-all-the-trades-i-ve-taken-for-a-particular-period |
| Corporate action impact on derivatives | https://support.zerodha.com/category/console/corporate-actions/ca-others/articles/impact-of-corporate-actions-on-derivatives |

---

### A7 — Charges Reference

**Equity F&O (segment = FO):**

| Charge | F&O — Futures | F&O — Options |
|---|---|---|
| Brokerage | 0.03% or ₹20/executed order (whichever is lower) | Flat ₹20 per executed order |
| STT/CTT | 0.05% on sell side | 0.15% of intrinsic value on options bought and exercised; 0.15% on sell side (on premium) |
| Transaction charges | NSE: 0.00193%; BSE: 0 | NSE: 0.03553% (on premium); BSE: 0.03255% (on premium) |
| GST | 18% on brokerage + SEBI charges + transaction charges | 18% on brokerage + SEBI charges + transaction charges |
| SEBI charges | ₹10 / crore | ₹10 / crore |
| Stamp charges | 0.003% or ₹300 / crore on buy side | 0.003% or ₹300 / crore on buy side |

**Currency Derivatives (segment = CDS):**

| Charge | Currency Futures | Currency Options |
|---|---|---|
| Brokerage | 0.03% or ₹20/executed order (whichever is lower) | Flat ₹20 per executed order |
| STT/CTT | No STT | No STT |
| Transaction charges | NSE: 0.00035%; BSE: 0.00045% | NSE: 0.0311%; BSE: 0.001% |
| GST | 18% on brokerage + SEBI charges + transaction charges | 18% on brokerage + SEBI charges + transaction charges |
| SEBI charges | ₹10 / crore | ₹10 / crore |
| Stamp charges | 0.0001% or ₹10 / crore on buy side | 0.0001% or ₹10 / crore on buy side |

**Commodities (segment = COM):**

| Charge | Commodity Futures | Commodity Options |
|---|---|---|
| Brokerage | 0.03% or ₹20/executed order (whichever is lower) | Flat ₹20 per executed order |
| STT/CTT | 0.01% on sell side (Non-Agri) | 0.05% on sell side |
| Transaction charges | MCX: 0.0021%; NSE: 0.0001% | MCX: 0.0418%; NSE: 0.001% |
| GST | 18% on brokerage + SEBI charges + transaction charges | 18% on brokerage + SEBI charges + transaction charges |
| SEBI charges | Agri: ₹1 / crore; Non-Agri: ₹10 / crore | ₹10 / crore |
| Stamp charges | 0.002% or ₹200 / crore on buy side | 0.003% or ₹300 / crore on buy side |

---

## Section B: Decision Flow

### Routing

```
Route by scenario
   ├─ Full F&O tradebook needed (tax / audit / compliance) → Rule 1
   ├─ Closed account — historical F&O trade data needed → Rule 2
   ├─ Verify an F&O trade → Rule 3
   ├─ Trade missing from tradebook → Rule 4
   ├─ Execution price doesn't match (possible multiple fills) → Rule 5
   ├─ Contract details changed after corporate action → Rule 6
   ├─ Client asks about contract characteristics → Rule 7
   ├─ Charges / brokerage / STT / MTM query → Rule 8
   └─ Report fails to load or times out → Rule 9
```

### Fallback

- If still unresolved → escalate.

---

## Section C: Rules

### Rule 1 — Full F&O Tradebook Request (Tax / Audit / Compliance)

1. Share the links from A6 with the client.
2. If the client requests a formatted PDF, share the same links from A6.

---

### Rule 2 — Closed Account — Historical F&O Trade Data

- → escalate.

---

### Rule 3 — Trade Verification

- Confirm the trade by presenting shareable fields per A2.

---

### Rule 4 — Trade Missing from Tradebook

1. Search by date, segment (per A3), and tradingsymbol.
2. If found → confirm trade details per Rule 3.
3. Invoke `get_all_client_data` and check `segments` to confirm the client's enabled segments, then verify correct segment is selected (per A3).
4. If still not found after correct segment → escalate.

---

### Rule 5 — Multiple Fills for One Order

1. Check if multiple `trade_id`s exist for the same `order_id`.
2. If yes → confirm each fill (trade_id, quantity, price) and the calculated average execution price across all fills.

---

### Rule 6 — Contract Symbol Change After Corporate Action

1. Explain the CA adjustment per A5.
2. Share the corporate action impact link from A6.
3. If client is not satisfied → escalate.

---

### Rule 7 — Identifying Contract Details

1. Use A4 to identify the contract type from field values.
2. Communicate contract type (futures / call option / put option), strike price if applicable, and expiry date.

---

### Rule 8 — Charge Queries (Brokerage / STT / Stamp Duty / GST / SEBI)

1. For charge queries (any segment) → share applicable charges from A7 per segment (FO / CDS / COM) and instrument type (futures or options).
2. For MTM or obligation queries → contract note must be referred; this tool provides trade-level execution data only → escalate.

---

### Rule 9 — Report Fails to Load / Times Out

1. Retry with a narrower date range (e.g., one financial year at a time) or filter by segment.
2. If the issue persists → escalate.
