# console_mf_external_trades

## Description

WHEN TO USE:

When clients:
- Report wrong buy average or P&L after transferring MF from another platform
- Report holdings discrepancy for transferred units
- Report XIRR incorrect after transfer
- Ask about external trade entry corrections

TRIGGER KEYWORDS: "transferred from Groww/Kuvera", "wrong buy average", "P&L incorrect after transfer", "discrepancy", "external trade", "XIRR wrong", "coin"

TAGS: investments, holdings

## Protocol

# CONSOLE MF EXTERNAL TRADES PROTOCOL

## Section A: Reference Data

### A1 — Fundamentals

- `trade_id` and `order_id` always show as "DISCREPANT" — expected behavior for external entries.
- Transferred-in units always show as discrepant until external entries are added by the client.
- External entries cannot be deleted by the client — requires backend deletion.

### A2 — Coin-Only Purchase Rule

If all purchases for a fund were made through Coin (no transfer from another platform), external trade entries should not exist for that fund. If found, they were incorrectly entered and need deletion via backend + data rerun.

### A3 — Recalculation Status

| `pending_recalc` Value | Meaning |
|---|---|
| false | P&L has been recalculated — entries are reflected |
| true | Recalculation pending — check again in 24 hours |

### A4 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |
|---|---|
| `trade_date` | Date of trade |
| `tradingsymbol` | Fund name |
| `quantity` | Units |
| `price` | Price |
| `trade_type` | Buy/sell |
| `order_execution_time` | Execution timestamp |

**Non-shareable:**

| Field | Interpretation |
|---|---|
| `pending_recalc` | Recalculation status — internal |
| `creation` | Internal record creation |
| `external_trade_type` | Internal |
| `pk` | Internal primary key |
| `client_id` | Internal client identifier |
| `isin` | Internal ISIN |
| `instrument_id` | Internal instrument id |
| `trade_id` | Internal |
| `order_id` | Internal |
| `exchange` | Internal exchange |
| `series` | Internal series |
| `segment` | Internal segment |
| `settlement_type` | Internal settlement type |

### A5 — Links

| Topic | Link |
|---|---|
| External trade addition path | Console → Portfolio → Holdings → select fund → Add External Trade |
| Why buy average shows as N/A | https://support.zerodha.com/category/mutual-funds/coin-general/coin-reports/articles/why-is-the-buy-average-for-some-mutual-funds-shown-as-na |

### A6 — Escalation Data

Include when escalating to human agent: fund name, trade_date, quantity, price, trade_type, and the specific issue.

## Section B: Decision Flow

### Routing

```
Route by scenario
   ├─ Coin-only fund, external entries exist → Rule 3
   ├─ Transferred units, missing or pending entries → Rule 1
   ├─ Transferred units, entries exist, still wrong → Rule 2
   ├─ Client needs to delete an external entry → Rule 3
   └─ Client reports doubled value / duplicate entries → Rule 4
```

### Fallback

If no root cause is identified after checking all relevant rules → escalate to human agent per **A6**.

## Section C: Rules

### Rule 1 — Discrepancy After Transfer

1. External entries missing → direct client to add entries per **A5**.
2. Entries exist, `pending_recalc` = true → per **A3**, communicate recalculation status.

### Rule 2 — Wrong Buy Average (Entries Exist)

1. Verify all purchase lots are entered correctly: dates, quantities, prices.
2. If all correct and `pending_recalc` = false → escalate to human agent per **A6**.

### Rule 3 — Wrongly Entered External Trades / Deletion Required

1. Invoke `console_mf_tradebook` — check trade entries for the fund. If found → units purchased through Zerodha; external entries in this tool are incorrectly added per **A2**. Escalate to human agent per **A6**.
2. Client requests deletion of any external entry: external entries cannot be deleted from Console. Escalate to human agent per **A6**.

### Rule 4 — Duplicate Entry Detection

1. Invoke `console_mf_tradebook` — compare entries for the same fund, date, and quantity.
2. If duplicate found: confirm a duplicate entry has been identified; will be removed; P&L corrected within 24–48 hours.
3. Escalate to human agent per **A6**.
