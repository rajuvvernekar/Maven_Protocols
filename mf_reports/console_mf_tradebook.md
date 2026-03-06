# console_mf_tradebook

## Description

WHEN TO USE:

When customer asks about:
- ELSS lock-in period / when they can redeem ELSS
- Allotment verification — order shows Allotted but units missing
- Exact NAV/price at which units were allotted
- P&L verification using FIFO
- Trade entry existence for allotted/redeemed orders

TRIGGER KEYWORDS: "lock-in", "ELSS unlock", "when can I redeem ELSS", "allotment date", "trade date", "FIFO", "allotted but not visible", "coin"

## Protocol

# CONSOLE MF TRADEBOOK PROTOCOL

## Knowledge Base

<knowledge_base>
<facts>
- Contains EXECUTED orders only (allotment/redemption completed)
- PnL calculated from this using FIFO
- If trade entry missing for allotted order → PnL/holdings issues
- ELSS lock-in: 3 years from trade_date per BUY entry (FIFO basis)
- If lock-in ends today → allotment T+1 day, redeemable next day
- Zerodha fund house WhatsApp orders → trade entries posted here if allotted
- Scheme name field is `tradingsymbol`
</facts>

<field_usage>
  <share>trade_date (if asked) | tradingsymbol (as fund name) | trade_type | quantity | price (if asked)</share>
  <internal>order_execution_time (NAV cutoff check) | order_id | trade_id | client_id</internal>
  <banned>exchange | instrument_id | isin | scheme_code | settlement_type</banned>
</field_usage>
</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
Never share `<banned>` fields. Use `<internal>` fields for reasoning only.

### Rule 1: ELSS Lock-in
**if:** Customer asks when they can redeem ELSS
**then:** Filter `tradingsymbol` for ELSS fund, `trade_type` = buy. Sort `trade_date` ascending (FIFO). Lock-in end = `trade_date` + 3 years per entry. If ends today → "Allotment is T+1. You can redeem after 24 hours."

### Rule 2: Allotment Verification
**if:** Order Allotted in **mf_order_history** but units missing
**then:** Check if trade entry exists here for matching fund and date. If trade entry exists → units allotted, check **console_mf_holdings** for discrepancy. If missing → NFO: wait listing + T+1 day. Regular: escalate.

### Rule 3: P&L FIFO
**if:** Customer disputes P&L
**then:** List BUY entries sorted by `trade_date` ascending. Match SELL entries against oldest BUY first. If calculation differs → check **console_mf_external_trades** for missing entries.

### Rule 4: Cross-Tool
- Units allotted but not in holdings → **console_mf_holdings** (`discrepant`)
- Discrepancy → **console_mf_pseudo_holdings** (comparison)
- `failure_date` populated in holdings → escalate to human
- Missing external entries → **console_mf_external_trades**
