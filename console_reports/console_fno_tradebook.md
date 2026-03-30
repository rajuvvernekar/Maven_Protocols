# console_fno_tradebook

## Description

WHEN TO USE:

When clients:
- Ask about F&O trade history, execution details, or trade confirmation
- Report an F&O trade missing from tradebook
- Question execution price, quantity, or timing of a futures/options trade
- Ask to confirm strike price, expiry date, or instrument type of a contract
- Question why contract symbol changed (e.g., after corporate action on underlying)
- Ask if a trade was executed in FO, CDS, or COM segment
- Ask about F&O trades within the last 100 days
- Ask about contract note charges or MTM for F&O trades (requires manual handling)

TRIGGER KEYWORDS: "FnO tradebook", "F&O trade", "futures trade", "options trade", "FnO execution", "strike price", "expiry date", "contract details", "FnO order id", "FnO trade id", "derivative trade", "FnO trade history"

## Protocol

# CONSOLE FNO TRADEBOOK PROTOCOL 

---

## Section A: Reference Data

---

### A1 — Tool Purpose & Fundamentals

This tool shows the **last 100 days of F&O trades**. For older data, use `console_fno_tradebook_prepared`.

Each entry represents a single executed trade. One order may have multiple fills (multiple `trade_id`s for the same `order_id`).

For charges, MTM calculations, and obligation breakdowns: contract note must be referred manually — not available in this tool.

Auction trades appear in tradebook with specific `order_id` patterns.

**Input:** Client ID + From Date + To Date + Segment (FO/CDS/COM).

---

### A2 — Field Usage Rules

**Shareable fields:**

`trade_date` | `order_execution_time` | `tradingsymbol` | `exchange` | `segment` | `trade_type` | `quantity` | `price` | `order_id` | `trade_id` | `strike` | `expiry_date` | `instrument_type`

**Internal-only fields** (use for reasoning; communicate outcomes in plain language):

`client_id`

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

**Contract symbol format:** underlying + expiry + strike + CE/PE (e.g., NIFTY2621727100CE = NIFTY, 26 Feb 2026 expiry, 27100 strike, Call).

---

### A5 — Corporate Action Impact on F&O Contracts

When a corporate action occurs on the underlying stock (e.g., stock split, bonus), the exchange adjusts derivative contracts:

**Options:** Strike price adjusted (Old Strike / Adjustment Factor), market lot adjusted (Old Lot × Adjustment Factor).

**Futures:** Base price adjusted (Old Price / Adjustment Factor), market lot adjusted (Old Lot × Adjustment Factor).

The contract symbol itself does not change — strike price and lot size change. Position value remains the same — only contract terms are adjusted.

**Example — ANGELONE 10:1 split:** Old lot 250 → New lot 2500. Old strike ₹5000 → New strike ₹500.

**Support article:** https://support.zerodha.com/category/console/corporate-actions/ca-others/articles/impact-of-corporate-actions-on-derivatives

Contract symbol may also change mid-series if a CA causes a symbol rename.

---

### A6 — Cross-Reference Tools

| Tool | When to Use |
|---|---|
| `console_fno_tradebook_prepared` | Same schema, no date limit. Use for F&O trades older than 100 days. |
| `console_fno_positions` | Open position snapshot. Tradebook entries feed into positions. |
| `console_fno_pnl` | Realized P&L computed from tradebook entries. |

---

### A7 — Escalation Data Template

When escalating, always include: **client ID, trade_date, tradingsymbol, segment, order_id, and specific issue.**

---

### A8 — Response Templates

**R1 — Trade verification:**
"Your [trade_type] trade for [tradingsymbol] ([instrument_type]) on [trade_date] at [order_execution_time]: [quantity] contracts at ₹[price]. Strike: ₹[strike], Expiry: [expiry_date]. Exchange: [exchange]. Order ID: [order_id], Trade ID: [trade_id]."

**R2 — Multiple fills:**
"Your order (Order ID: [order_id]) was executed in [N] parts at different prices: [list each trade_id with qty and price]. The average execution price across all fills is ₹[calculated avg]."

**R3 — Corporate action adjustment:**
"After the corporate action ([split/bonus]) on [underlying], your F&O contract was adjusted by the exchange. The strike price and lot size have been modified per the adjustment factor. Your position value remains the same — only the contract terms were adjusted. For more details: https://support.zerodha.com/category/console/corporate-actions/ca-others/articles/impact-of-corporate-actions-on-derivatives"

**R4 — Contract identification:**
- Futures: "This is a futures contract"
- Call option: "This is a call option with strike price ₹[strike]"
- Put option: "This is a put option with strike price ₹[strike]"
- Expiry: "This contract expires on [expiry_date]"

---

## Section B: Decision Flow

---

### Preflight (run on every query)

```
1. Confirm correct segment selected (per A3)
   └─ FO for equity F&O, CDS for currency, COM for commodities.
      Wrong segment = no results.

2. Check if date range exceeds 100 days
   └─ If yes → use console_fno_tradebook_prepared (per A6).
```

### Route

```
Intent / Condition                                          → Rule
──────────────────────────────────────────────────────────────────────
Verify an F&O trade                                         → Rule 1
Trade missing from tradebook                                → Rule 2
Execution price doesn't match (possible multiple fills)     → Rule 3
Contract details don't match what client traded (CA)        → Rule 4
Client asks about contract characteristics                  → Rule 5
Charges / brokerage / STT / MTM query                       → Rule 6
```

### Scope

- Address the client's query about F&O trade execution records, prices, contract details, and CA adjustments.
- Use **A2** field rules in all client communication.

### Fallback

If no route matches, cross-reference with **A6** tools for additional context. If no root cause is found, escalate per **A7**.

---

## Section C: Rules

---

### Rule 1 — Trade Verification

1. Respond per **A8-R1**.

---

### Rule 2 — Trade Missing from Tradebook

1. Search by date, segment, and tradingsymbol.
2. If found → respond per **A8-R1**.
3. If not found → verify correct segment selected (per Preflight / **A3**). Check if date is within 100 days — if not, use `console_fno_tradebook_prepared` (per **A6**).
4. If still not found after correct segment and date → escalate per **A7**.

---

### Rule 3 — Multiple Fills for One Order

1. Check if multiple `trade_id`s exist for the same `order_id`.
2. If yes → respond per **A8-R2** with each fill's qty and price plus calculated average.

---

### Rule 4 — Contract Symbol Change After Corporate Action

1. Explain the CA adjustment per **A5**.
2. Respond per **A8-R3**.
3. If client is not satisfied → escalate per **A7**.

---

### Rule 5 — Identifying Contract Details

1. Use **A4** to identify the contract type from field values.
2. Respond per **A8-R4**.

---

### Rule 6 — Contract Note Queries (Manual Handling)

1. This tool provides trade-level execution data only — no charge, MTM, or obligation data.
2. Escalate to support agent for actual contract note charges, MTM, and settlement details.

