# console_mf_external_trades

## Description

WHEN TO USE:

When customer asks about:
- Wrong buy average or P&L after transferring MF from another platform
- Holdings discrepancy for transferred units
- XIRR incorrect
- External trade entry corrections

TRIGGER KEYWORDS: "transferred from Groww/Kuvera", "wrong buy average", "P&L incorrect after transfer", "discrepancy", "external trade", "XIRR wrong", "coin"

## Protocol

# CONSOLE MF EXTERNAL TRADES PROTOCOL

## Knowledge Base

<knowledge_base>
<facts>
- Contains orders executed OUTSIDE Coin
- trade_id and order_id always "DISCREPANT"
- pending_recalc: false = PnL recalculated; true = pending
- Transferred-in units always show as discrepant until external entries added by the client
- External entries cannot be deleted by client — needs backend
- **CRITICAL: If all purchases for a fund were made through Coin (no transfer from another platform), external trade entries should NOT exist for that fund. If found, they were incorrectly entered and need deletion via backend.**
</facts>

<field_usage>
  <share>trade_date | tradingsymbol (as fund name) | quantity | price | trade_type | order_execution_time (if asked)</share>
  <internal>pending_recalc | creation | external_trade_type</internal>
  <banned>pk | client_id | isin | instrument_id | trade_id | order_id | exchange | series | segment | settlement_type</banned>
</field_usage>
</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
Never share `<banned>` fields. Use `<internal>` fields for reasoning only.

### Rule 1: Discrepancy After Transfer
**if:** Client reports wrong buy average or discrepancy
**then:**
**FIRST — Coin-only check:** Verify whether client transferred units from another platform or all purchases were made through Coin.
- If ALL purchases made through Coin (no external transfer) → do NOT advise adding external trades. Go to **Rule 3.5**.
- If units transferred from another platform → check if external entries exist:
  - Missing → "Add external trades: Console → Portfolio → Holdings → fund → Add External Trade."
  - `pending_recalc` = true → "Recalculation pending. Check again in 24 hours."

### Rule 2: Wrong Buy Average
**if:** Entries exist but average still wrong
**then:** Verify all purchase lots entered (dates, quantities, prices). If all correct + `pending_recalc` = false → escalate.

### Rule 3: Cannot Delete Entry
**if:** Customer entered wrong external trade OR external trade needs deletion
**then:** "External entries cannot be deleted from Console." → ESCALATE TO AGENT with: fund name, trade_date, quantity, price, trade_type.

### Rule 3.5: Wrongly Entered External Trades for Coin Purchases
**if:** Client has discrepancy on a fund where ALL purchases were made through Coin (no transfer from another platform), AND external trade entries exist in this report
**then:** The external trades were incorrectly entered. Do NOT tell client to add more entries. → ESCALATE TO AGENT: "External trade entries were incorrectly added for [fund name]. These need to be deleted and a data rerun is required. Client should not add any trade details for purchases made through Coin."

### Rule 4: Duplicate Entry Detection
**if:** Client reports doubled investment value or duplicate entries
**then:** Compare entries here with **console_mf_tradebook** entries for same fund/date/quantity. If duplicate found → "We have identified a duplicate entry. We will remove it. Your P&L will be corrected within 24-48 hours." → ESCALATE TO AGENT with: fund name, trade_date, quantity, price.

### Rule 5: XIRR
**if:** XIRR incorrect
**then:** XIRR needs complete buy/sell history across **console_mf_tradebook** + this tool. Any missing entry skews results. Verify all entries.
