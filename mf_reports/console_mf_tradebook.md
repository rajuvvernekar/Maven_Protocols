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
- ELSS lock-in: exactly 3 calendar years from trade_date (allotment date) per BUY entry (FIFO basis)
- trade_date = allotment date — NOT the order placement date or payment date
- If lock-in ends today → units redeemable from tomorrow (T+1 settlement)
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
**then:**
1. Filter `tradingsymbol` for ELSS fund, `trade_type` = buy.
2. Sort `trade_date` ascending (FIFO). Lock-in end = `trade_date` + exactly 3 calendar years per entry.
   - `trade_date` is the allotment date — NOT the order placement date or payment date.
   - Example: allotted on 15-Mar-2022 → unlocks on 15-Mar-2025.
3. If only one lot → share single unlock date: "Your [X units] allotted on [date] will unlock on [date]."
4. If multiple lots → show earliest unlocking lot first:
   "Your earliest [X units] (allotted [date]) unlock on [unlock date]. Remaining lots unlock on: [date] ([Y units]), [date] ([Z units])."
5. If earliest lock-in ends today → "Your units will be redeemable from tomorrow. ELSS redemption follows T+1 settlement."

### Rule 2: Allotment Verification
**if:** Order Allotted in **mf_order_history** but units missing
**then:** Check if trade entry exists here for matching fund and date.
- Trade entry exists → units allotted, check **console_mf_pseudo_holdings** (primary) for discrepancy.
- Missing → NFO: wait listing + T+1 day. Regular fund: escalate.

### Rule 3: P&L FIFO
**if:** Customer disputes P&L
**then:**
1. List BUY entries from this tool sorted by `trade_date` ascending. Match SELL entries against oldest BUY first (FIFO).
2. **ALWAYS cross-reference console_mf_external_trades** for any transferred-in units — missing external entries will skew P&L regardless of whether tradebook entries look complete.
3. If calculation still differs after both checks → escalate.
