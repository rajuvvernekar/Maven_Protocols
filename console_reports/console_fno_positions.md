# console_fno_positions

## Description

WHEN TO USE:

- Client asks about open F&O positions (futures or options) for a specific date
- Client questions unrealized P&L on F&O positions
- Agent needs to verify open quantity, average cost, or closing value of an F&O position
- Client reports position quantity mismatch between Kite and Console
- Client asks about MTM (Mark-to-Market) obligation on their positions
- Client questions carry-forward positions or overnight margin
- Agent needs to check position data for a past date (historical snapshot)
- Client asks about position value on a specific date (e.g., for margin or settlement queries)

TRIGGER KEYWORDS: "F&O position", "FnO position", "futures position", "options position", "open position", "open quantity", "carry forward position", "MTM", "mark to market", "position P&L", "position value", "overnight position", "position not showing", "position wrong", "unrealized F&O"

## Protocol

# CONSOLE FNO POSITIONS PROTOCOL

## PROTOCOL

<knowledge_base>

<facts>
- This tool shows a snapshot of open F&O positions as of a selected trade date — you can check previous days' positions by selecting the date, but it does not show real-time intraday data
- Segments: FO (equity F&O), CDS (currency derivatives), COM (commodities) — must select correct segment
- Unrealized P&L = closing_value − open_value = (close_price − open_average) × open_quantity
- Positive open_quantity = long position; negative open_quantity = short position
- Closing price used is the settlement price for that date — may differ from last traded price
- MTM (Mark-to-Market) is settled daily: profit credited / loss debited based on closing price vs previous day closing price
- Positions auto-squared-off on expiry if not closed by client — ITM options exercised, OTM expire worthless
- Physical delivery applicable for stock F&O positions expiring ITM — shares delivered/received T+1 after expiry
- Carry-forward positions: positions held overnight incur margin requirements; margin recalculated at EOD
- Contract symbol includes: underlying + expiry date + strike (for options) + CE/PE (e.g., NIFTY2621727100CE)
- If position shows on a past date but not current date → position was closed/expired between those dates
- Console positions use settlement/closing price; Kite positions use LTP — values will differ during market hours
</facts>

<field_usage>
  <share>trade_date | tradingsymbol | open_quantity | open_average | open_value | close_price | closing_value | unrealized_profit | unrealized_profit_percentage</share>
  <banned>client_id</banned>
</field_usage>

<segments>
  <fo>Equity Futures & Options — NIFTY, BANKNIFTY, SENSEX, stock futures/options</fo>
  <cds>Currency Derivatives — USDINR, EURINR, etc.</cds>
  <com>Commodities — GOLD, SILVER, CRUDEOIL, NATURALGAS, etc. (MCX)</com>
</segments>

<cross_reference>
  <console_fno_tradebook>Trade-level execution details feeding into positions. Use to verify entry trades.</console_fno_tradebook>
  <console_fno_pnl>Realized P&L for closed/expired positions.</console_fno_pnl>
</cross_reference>

<escalation_triggers>
  <position_mismatch>Open quantity differs between Console and Kite after EOD (not during market hours)</position_mismatch>
  <wrong_avg>Open average doesn't match expected entry price after verifying with tradebook</wrong_avg>
  <missing_position>Position expected but not found for the selected date and segment</missing_position>
</escalation_triggers>

</knowledge_base>

---

## Business Rules

### Rule 0: Segment Selection
**if:** Agent looks up positions
**then:** Always confirm correct segment: FO for equity F&O, CDS for currency, COM for commodities. Wrong segment = no results.

### Rule 1: Field Protection
**NEVER expose:** `client_id`
**ALWAYS share when relevant:** `trade_date`, `tradingsymbol`, `open_quantity`, `open_average`, `open_value`, `close_price`, `closing_value`, `unrealized_profit`, `unrealized_profit_percentage`

### Rule 2: Position Verification
**if:** Client asks about their open F&O position
**then:** "Your open position in [tradingsymbol] as of [trade_date]: [open_quantity] lots at an average price of ₹[open_average]. The closing price on that date was ₹[close_price], giving an unrealized P&L of ₹[unrealized_profit] ([unrealized_profit_percentage]%)."

Note: Positive open_quantity = long; negative = short. Frame accordingly: "You are long/short [abs(open_quantity)] lots."

### Rule 3: MTM Obligation Explanation
**if:** Client questions MTM debit/credit on their ledger
**then:** "Mark-to-Market (MTM) is settled daily for F&O positions. Each day, the difference between today's closing price and the previous day's closing price is credited (if favorable) or debited (if unfavorable) from your account. This is the daily settlement mechanism for futures and ITM options.

Your position in [tradingsymbol] closed at ₹[close_price] on [trade_date]. The MTM for that day is calculated as: (today's closing price − previous day's closing price) × quantity."

**if:** Client asks for detailed MTM calculation → **AGENT HAS TO MANUALLY HANDLE.** This tool shows position snapshot, not day-by-day MTM breakdown. Agent must calculate from consecutive days' closing prices or refer to contract note/ledger.

### Rule 4: Console vs Kite Position Value Difference
**if:** Client says position value differs between Console and Kite
**then:** "Console positions show values based on the settlement/closing price for the selected date, while Kite shows values based on the live last traded price (LTP). These will differ during market hours and may also differ slightly after market close if the settlement price differs from the last traded price."

If values differ AFTER EOD settlement → verify both show same open_quantity. If quantity matches but value differs → closing price source difference (normal). If quantity differs → escalate.

### Rule 5: Expired / Closed Position Not Showing
**if:** Client asks about a position that no longer appears
**then:** Check the position for the previous trade date.
- If found on earlier date but not on requested date → "Your [tradingsymbol] position was closed or expired between [earlier date] and [requested date]. If it expired, ITM options were exercised and OTM options expired worthless."
- For realized P&L on closed positions → use `console_fno_pnl`.

### Rule 6: Physical Delivery on Expiry
**if:** Client asks about stock F&O position expiring ITM and physical delivery
**then:** "Stock futures and ITM stock options that expire are subject to physical delivery. If you held a long futures/ITM call position, shares will be credited to your demat account. If you held a short futures/ITM put position, shares will be debited. Physical delivery happens T+1 after expiry.

Delivery margin is blocked from the Wednesday before expiry for stock F&O positions."

**if:** Client questions delivery margin or charges → **AGENT HAS TO MANUALLY HANDLE.** Delivery margin and penalty calculations depend on multiple factors not available in this tool.

### Rule 7: Historical Position Snapshot
**if:** Agent or client needs position data for a past date
**then:** This tool provides historical snapshots. Enter the specific trade_date to see what positions were open on that day, their quantities, and closing values.

"Your positions as of [trade_date] were: [list tradingsymbol, open_quantity, open_average, unrealized_profit for each]."

### Rule 8: Margin Shortfall Queries
**if:** Client asks about margin shortfall or penalty related to F&O positions
**then:** This tool does not contain margin requirement or penalty calculations. Escalate directly with: client ID, tradingsymbol, trade_date, and client's concern about margin shortfall/penalty. Do not attempt to calculate or share partial information with the client.

### Rule 9: Escalation Criteria
**if:** Any of the following:
- Open quantity differs between Console and Kite after EOD settlement (Rule 4)
- Open average doesn't match entry price after verifying with `console_fno_tradebook` (KB trigger)
- Position expected but not found for selected date and correct segment (KB trigger)
**then:** Escalate with: client ID, tradingsymbol, trade_date, segment, and specific discrepancy.
