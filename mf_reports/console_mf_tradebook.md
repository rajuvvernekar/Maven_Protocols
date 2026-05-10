# console_mf_tradebook

## Description

WHEN TO USE:

When clients:
- Ask about ELSS lock-in period or when they can redeem ELSS
- Report order shows Allotted but units missing
- Ask about exact NAV/price at which units were allotted
- Need P&L verification using FIFO
- Ask about trade entry existence for allotted/redeemed orders

TRIGGER KEYWORDS: "lock-in", "ELSS unlock", "when can I redeem ELSS", "allotment date", "trade date", "FIFO", "allotted but not visible", "coin"

TAGS: investments, reports

## Protocol

# CONSOLE MF TRADEBOOK PROTOCOL

## Section A: Reference Data

### A1 — Fundamentals

- P&L is calculated from this tool's data using FIFO.
- Zerodha fund house WhatsApp orders → trade entries posted here if allotted.

### A2 — ELSS Lock-in Rules

- ELSS lock-in: exactly 3 calendar years (1096 days) from `trade_date` (allotment date) per BUY entry, on a FIFO basis.
- `trade_date` = allotment date — not the order placement date or payment date.
- Example: allotted on 15-Mar-2022 → unlocks on 15-Mar-2025.
- If lock-in ends today → units redeemable from tomorrow (T+1 settlement).

### A3 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |
|---|---|
| `trade_date` | Allotment date |
| `tradingsymbol` | Fund name |
| `trade_type` | Buy/sell |
| `quantity` | Units |
| `price` | Price |

**Non-shareable:**

| Field | Interpretation |
|---|---|
| `order_execution_time` | NAV cutoff check — internal |
| `order_id` | Internal reference |
| `trade_id` | Internal reference |
| `client_id` | Internal client identifier |
| `exchange` | Internal exchange |
| `instrument_id` | Internal instrument id |
| `isin` | Internal ISIN |
| `scheme_code` | Internal scheme code |
| `settlement_type` | Internal settlement type |

## Section B: Decision Flow

### Routing

```
Route by scenario
   ├─ Client asks when ELSS units can be redeemed → Rule 1
   ├─ Order allotted but units missing (flagged by ‘mf_order_history’) → Rule 2
   └─ Client disputes MF P&L → Rule 3
```

### Fallback

If trade data seems inconsistent or missing entries cannot be explained → escalate to human agent with client ID, fund name, trade dates, and the specific discrepancy.

## Section C: Rules

### Rule 1 — ELSS Lock-in

1. Filter `tradingsymbol` for the ELSS fund, `trade_type` = BUY.
2. Sort by `trade_date` ascending. Calculate lock-in end per **A2** for each entry.
3. Apply FIFO: match `trade_type` = SELL entries against oldest BUY lots first. Use remaining quantities per lot for lock-in calculation.
4. If only one lot: share allotment date and unlock date.
5. If multiple lots — show earliest unlocking lot first, then list remaining lots with unlock dates and quantities.
6. If earliest lock-in ends today → communicate per **A2**.

### Rule 2 — Allotment Verification

1. Check if a trade entry exists for the matching fund and date.
2. Trade entry exists → units allotted. Invoke `console_mf_pseudo_holdings` for discrepancy diagnosis.
3. Trade entry missing → escalate to human agent.

### Rule 3 — P&L FIFO Verification

1. List BUY entries sorted by `trade_date` ascending. Match SELL entries against the oldest BUY first (FIFO).
2. Invoke `console_mf_external_trades` for transferred-in units.
3. If calculation still differs after both checks → escalate to human agent.
