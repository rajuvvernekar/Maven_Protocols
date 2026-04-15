# console_mf_external_trades

## Description

WHEN TO USE:

When clients:
- Report wrong buy average or P&L after transferring MF from another platform
- Report holdings discrepancy for transferred units
- Report XIRR incorrect after transfer
- Ask about external trade entry corrections

TRIGGER KEYWORDS: "transferred from Groww/Kuvera", "wrong buy average", "P&L incorrect after transfer", "discrepancy", "external trade", "XIRR wrong", "coin"

## Protocol

# CONSOLE MF EXTERNAL TRADES PROTOCOL


### A1 — Tool Purpose & Scope

- Contains orders executed outside Coin (transferred-in units, external platform purchases).
- `trade_id` and `order_id` always show as "DISCREPANT" — this is expected behavior for external entries.
- Transferred-in units always show as discrepant until external entries are added by the client.
- External entries cannot be deleted by the client — requires backend deletion.
- Scheme name field is `tradingsymbol`.

### A2 — Coin-Only Purchase Rule

If all purchases for a fund were made through Coin (no transfer from another platform), external trade entries should not exist for that fund. If found, they were incorrectly entered and need deletion via backend + data rerun. This is the most important diagnostic check in this protocol — always verify Coin-only vs transferred before advising any action.

### A3 — Recalculation Status

| `pending_recalc` Value | Meaning |
|---|---|
| false | P&L has been recalculated — entries are reflected |
| true | Recalculation pending — check again in 24 hours |

### A4 — Field Rules

**Shareable with client (if asked):** `trade_date`, `tradingsymbol` (as fund name), `quantity`, `price`, `trade_type`, `order_execution_time`.

**Internal reasoning only (use for analysis, never share):** `pending_recalc`, `creation`, `external_trade_type`.

**Suppress (no client use, only for reasoning purpose):** `pk`, `client_id`, `isin`, `instrument_id`, `trade_id`, `order_id`, `exchange`, `series`, `segment`, `settlement_type`.

### A5 — External Trade Addition Path

Console → Portfolio → Holdings → select fund → Add External Trade.

### A6 — Cross-Reference Protocols

| Topic | Refer to |
|---|---|
| Tradebook entries for duplicate detection / FIFO P&L | console_mf_tradebook |
| Holdings discrepancy diagnosis | console_mf_pseudo_holdings |
| Redeemable units verification | console_mf_holdings (`available` field) |

### A7 — Escalation Triggers (Consolidated)

Escalate to support agent when any of the following occur:
- External trade entries incorrectly added for a Coin-only fund — need deletion + data rerun (Rule 3).
- Client needs an external entry deleted (cannot self-serve) — provide fund name, trade_date, quantity, price, trade_type.
- All external entries correct, `pending_recalc` = false, but buy average still wrong (Rule 2).
- Duplicate entries found between this tool and console_mf_tradebook (Rule 4).

Include in escalation: fund name, trade_date, quantity, price, trade_type, and the specific issue.

### Preflight (run on every query)

1. Fetch the external trades data for the client and relevant fund.
2. Apply field protection per **A4** — identify shareable, internal, and banned fields.
3. **Coin-only check:** Determine whether the client transferred units from another platform or all purchases were made through Coin. This determines the entire diagnostic path (per **A2**).
4. Format amounts with ₹ and Indian comma notation. Format dates as DD MMM YYYY.

### Routing Tree

```
Query relates to MF external trades →
│
├─ Preflight: All purchases through Coin (no external transfer)?
│  ├─ YES, and external entries exist here
│  │  → Rule 3 (Wrongly entered — escalate for deletion)
│  └─ NO (units transferred from another platform)
│     ├─ External entries missing → Rule 1a (Guide to add)
│     ├─ Entries exist, pending_recalc = true → Rule 1b (Wait)
│     └─ Entries exist, still wrong → Rule 2 (Verify and escalate)
│
├─ Client needs to delete an external entry
│  → Rule 3 (Escalate for deletion)
│
├─ Client reports doubled value / duplicate entries
│  → Rule 4
│
├─ XIRR incorrect
│  → Rule 5
│
└─ Data inconsistency / no root cause found
   → Escalate per A7
```

### Scope

- Address: external trade entry management, discrepancy diagnosis from transferred units, buy average correction, duplicate detection, and XIRR verification.

### Fallback

If no root cause is identified after checking all relevant rules → escalate per **A7**.


### Rule 1 — Discrepancy After Transfer

1. Confirm: client transferred units from another platform (not Coin-only — verified in Preflight step 3 per **A2**).

**1a — External entries missing:**
"To correct the buy average for transferred units, please add external trade entries: [path from **A5**]. Enter the original purchase date, quantity, and price for each lot transferred."

**1b — Entries exist, recalculation pending:**
Check `pending_recalc` (per **A3**). If true: "The recalculation is pending. Please check again in 24 hours."

### Rule 2 — Wrong Buy Average (Entries Exist)

1. Verify all purchase lots are entered correctly: dates, quantities, prices.
2. If all correct and `pending_recalc` = false → escalate per **A7**.

### Rule 3 — Wrongly Entered External Trades / Deletion Required

**Coin-only fund with external entries (per A2):**
The external trades were incorrectly entered. Do not advise adding more entries. Escalate to support agent: "External trade entries were incorrectly added for [fund name]. These need to be deleted and a data rerun is required. Client should not add any trade details for purchases made through Coin."

**Client requests deletion of any external entry:**
"External entries cannot be deleted from Console." Escalate to support agent with: fund name, trade_date, quantity, price, trade_type (per **A7**).

### Rule 4 — Duplicate Entry Detection

1. Compare entries here with console_mf_tradebook entries (per **A6**) for the same fund, date, and quantity.
2. If duplicate found: "We have identified a duplicate entry. We will remove it. Your P&L will be corrected within 24–48 hours."
3. Escalate to support agent with: fund name, trade_date, quantity, price (per **A7**).

### Rule 5 — XIRR Incorrect

1. XIRR requires complete buy/sell history across both console_mf_tradebook and this tool (per **A6**).
2. Any missing entry skews XIRR results.
3. Verify all entries in both tools are present and correct. If entries are complete but XIRR still wrong → escalate.
