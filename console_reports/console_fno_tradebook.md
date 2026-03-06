# console_fno_tradebook

## Description

WHEN TO USE:

- Client asks about F&O trade history, execution details, or trade confirmation
- Client reports an F&O trade missing from tradebook
- Client questions execution price, quantity, or timing of a futures/options trade
- Agent needs to verify F&O trade entries to explain position average or P&L
- Client asks to confirm strike price, expiry date, or instrument type of a contract
- Client questions why contract symbol changed (e.g., after corporate action on underlying)
- Agent needs to check if a trade was executed in FO, CDS, or COM segment
- Client asks about F&O trades within the last 100 days
- Client asks about contract note charges or MTM for F&O trades (requires manual handling)

TRIGGER KEYWORDS: "FnO tradebook", "F&O trade", "futures trade", "options trade", "FnO execution", "strike price", "expiry date", "contract details", "FnO order id", "FnO trade id", "derivative trade", "FnO trade history"

## Protocol

# CONSOLE FNO TRADEBOOK PROTOCOL

## PROTOCOL

<knowledge_base>

<facts>
- This tool shows last 100 days of F&O trades — for older data use `console_fno_tradebook_prepared`
- Required inputs: Client ID, From Date, To Date, Segment (FO/CDS/COM)
- Each entry represents a single executed trade — one order may have multiple fills (multiple trade_ids for same order_id)
- instrument_type: FUT = futures, OPT = options
- strike field: populated for options, indicates the strike price of the contract
- expiry_date: last trading day of the contract
- Negative quantity may represent sell side of the trade
- Contract symbols include underlying + expiry + strike + CE/PE (e.g., NIFTY2621727100CE = NIFTY, 26 Feb 2026 expiry, 27100 strike, Call)
- Contract symbol may change mid-series if corporate action occurs on underlying (e.g., lot size change, symbol rename)
- For charges, MTM calculations, and obligation breakdowns: contract note must be referred manually — not available in this tool
- Auction trades appear in tradebook with specific order_id patterns
</facts>

<field_usage>
  <share>trade_date | order_execution_time | tradingsymbol | exchange | segment | trade_type | quantity | price | order_id | trade_id | strike | expiry_date | instrument_type</share>
  <banned>client_id</banned>
</field_usage>

<cross_reference>
  <console_fno_tradebook_prepared>Same schema, no date limit. Use for F&O trades older than 100 days.</console_fno_tradebook_prepared>
  <console_fno_positions>Open position snapshot. Tradebook entries feed into positions.</console_fno_positions>
  <console_fno_pnl>Realized P&L computed from tradebook entries.</console_fno_pnl>
</cross_reference>

<escalation_triggers>
  <trade_missing>Trade visible in Kite order history but not in FnO tradebook after T+1</trade_missing>
  <wrong_symbol>Contract symbol in tradebook doesn't match what client traded (CA-related symbol change)</wrong_symbol>
</escalation_triggers>

</knowledge_base>

---

## Business Rules

### Rule 0: Segment and Date Range Check
**if:** Agent looks up F&O trades
**then:** Confirm correct segment (FO/CDS/COM) and date range within 100 days. Wrong segment = no results. If older than 100 days → use `console_fno_tradebook_prepared`.

### Rule 1: Field Protection
**NEVER expose:** `client_id`
**ALWAYS share when relevant:** `trade_date`, `order_execution_time`, `tradingsymbol`, `exchange`, `segment`, `trade_type`, `quantity`, `price`, `order_id`, `trade_id`, `strike`, `expiry_date`, `instrument_type`

### Rule 2: Trade Verification
**if:** Client asks to verify an F&O trade
**then:** "Your [trade_type] trade for [tradingsymbol] ([instrument_type]) on [trade_date] at [order_execution_time]: [quantity] contracts at ₹[price]. Strike: ₹[strike], Expiry: [expiry_date]. Exchange: [exchange]. Order ID: [order_id], Trade ID: [trade_id]."

### Rule 3: Trade Missing from Tradebook
**if:** Client says an F&O trade is missing
**then:** Search by date, segment, and tradingsymbol.
- If found → share details per Rule 2.
- If not found → verify correct segment selected. Check if date is within 100 days (if not, use `console_fno_tradebook_prepared`). If still not found after correct segment and date → escalate.

### Rule 4: Multiple Fills for One Order
**if:** Client says execution price doesn't match what they expected
**then:** Check if multiple trade_ids exist for the same order_id. If yes → "Your order (Order ID: [order_id]) was executed in [N] parts at different prices: [list each trade_id with qty and price]. The average execution price across all fills is ₹[calculated avg]."

### Rule 5: Contract Symbol Change After Corporate Action
**if:** Client says contract details in tradebook don't match what they traded
**then:** When a corporate action occurs on the underlying stock (e.g., stock split, bonus), the exchange adjusts the derivative contracts:

**Options:** Strike price is adjusted (Old Strike / Adjustment Factor), market lot is adjusted (Old Lot × Adjustment Factor).
**Futures:** Base price is adjusted (Old Price / Adjustment Factor), market lot is adjusted (Old Lot × Adjustment Factor).

Example — ANGELONE 10:1 split: Old lot 250 → New lot 2500. Old strike ₹5000 → New strike ₹500. The contract symbol itself doesn't change — the strike price and lot size change.

"After the corporate action ([split/bonus]) on [underlying], your F&O contract was adjusted by the exchange. The strike price and lot size have been modified per the adjustment factor. Your position value remains the same — only the contract terms were adjusted. For more details: https://support.zerodha.com/category/console/corporate-actions/ca-others/articles/impact-of-corporate-actions-on-derivatives"

If client is not satisfied → escalate with details.

### Rule 6: Identifying Contract Details
**if:** Client asks about specific contract characteristics
**then:** Use the schema fields:
- `instrument_type` = FUT → "This is a futures contract"
- `instrument_type` = OPT + tradingsymbol ends with CE → "This is a call option"
- `instrument_type` = OPT + tradingsymbol ends with PE → "This is a put option"
- `strike` → "Strike price: ₹[strike]"
- `expiry_date` → "This contract expires on [expiry_date]"

### Rule 7: Contract Note Queries — Manual Handling
**if:** Client asks about charges, brokerage, STT, MTM calculations, or obligation breakdowns for F&O trades
**then:** **AGENT HAS TO MANUALLY HANDLE.** This tool provides trade-level execution data only. Agent must refer to the actual contract note for charges, MTM, and settlement details.

### Rule 8: Escalation Criteria
**if:** Any of the following:
- Trade visible in Kite but missing from tradebook after T+1 and correct segment (Rule 3)
- Contract symbol discrepancy not explained by CA (Rule 5)
**then:** Escalate with: client ID, trade_date, tradingsymbol, segment, order_id, and specific issue.
