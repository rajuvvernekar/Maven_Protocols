# console_eq_tradebook

## Description

WHEN TO USE:

- Client asks about equity trade history, execution details, or trade confirmation
- Client reports a trade missing from their tradebook
- Client questions execution price, quantity, or trade timing
- Client asks to verify buy/sell trades for a specific stock or date range
- Agent needs to verify trade entries to explain buy average or P&L calculation
- Agent needs to check if a trade was executed on NSE or BSE
- Agent needs to confirm trade series (EQ, BE/T2T, etc.) for FIFO or settlement queries
- Client asks about tradebook data for a period within the last 100 days
- Client questions why P&L or buy average seems wrong — agent needs to verify underlying trades
- Client asks about contract note charges, MTM, or obligation details (requires manual handling)

TRIGGER KEYWORDS: "tradebook", "trade history", "trade details", "execution price", "trade missing", "order id", "trade id", "trade date", "buy trade", "sell trade", "contract note", "execution time", "T2T", "series", "trade confirmation"

## Protocol

# CONSOLE EQ TRADEBOOK PROTOCOL

## Business Rules

### Rule 0: Date Range Check
**if:** Client requests trade data older than 100 days
**then:** "This tool covers the last 100 days of trades. For older trade history, I'll need to use `console_eq_tradebook_prepared` which supports any date range."

### Rule 1: Field Protection
**NEVER expose:** `instrument_id`, `settlement_type`, `client_id`
**ALWAYS share when relevant:** `trade_date`, `order_execution_time`, `tradingsymbol`, `exchange`, `order_id`, `trade_id`, `trade_type`, `quantity`, `price`, `isin`, `series`

### Rule 2: Verify Trade Existence
**if:** Client says a trade is missing from tradebook
**then:** Search by tradingsymbol and date range.
- If found → share trade_date, trade_type, quantity, price, exchange, order_id, trade_id.
- If not found in tradebook → check `console_eq_external_trades` (may be an off-platform entry like IPO, transfer, buyback).
- If not found in either → check if trade date is within last 100 days (if not, use `console_eq_tradebook_prepared`). If still not found after checking all sources → escalate.

### Rule 3: Execution Price Verification
**if:** Client questions the execution price shown in tradebook
**then:** "Your [trade_type] order for [quantity] shares of [tradingsymbol] was executed at ₹[price] per share on [exchange] at [order_execution_time].

If you placed a market order, the execution price is the best available price at the time of execution, which may differ from the last traded price you saw. If you placed a limit order, the execution price will be at or better than your limit price."

**if:** Client says price differs from contract note → "The tradebook shows the execution price per trade. The contract note may show a weighted average if your order was executed in multiple parts. Both are correct — the tradebook shows individual fills while the CN shows the aggregated obligation."

### Rule 4: Trade Series and T2T
**if:** Client questions why a stock behaves differently (no intraday, different buy avg calculation)
**then:** Check the `series` field.
- If series = BE, BT, or BZ → "This stock ([tradingsymbol]) is in the Trade-to-Trade (T2T) category. T2T stocks require compulsory delivery — intraday trading is not allowed. If you bought and sold on the same day, both are treated as separate delivery trades, not intraday. Pure FIFO applies to T2T stocks — the key difference from regular EQ stocks is that same-day buy+sell is treated as delivery (not speculative), so it impacts your buy average."
- If series = EQ → standard FIFO rules apply.

### Rule 5: Buy Average Explanation via Tradebook
**if:** Client questions buy average and agent needs to verify using tradebook entries
**then:** Do NOT list all individual trade entries in the response — there may be many entries and sharing everything is not recommended. Instead: "Buy average is calculated using FIFO (First In, First Out). You can check the detailed breakdown of your [tradingsymbol] holdings on Console → Portfolio → Holdings → select the stock → View breakdown. This shows every entry that contributes to your current buy average."

If agent needs to verify internally, use console_eq_holdings_breakdown to walk through FIFO.

### Rule 6: Intraday vs Delivery Identification
**if:** Client asks whether a trade was intraday or delivery
**then:** First check the `series` field:
- If series = BE, BT, or BZ (T2T) → all trades are compulsory delivery regardless of same-day buy+sell. "This stock is in the T2T category — all trades are treated as delivery, even if you bought and sold on the same day."
- If series = EQ → check tradebook for same-day buy AND sell entries for the same tradingsymbol:
  - Both buy and sell on same date → "You had both a buy and sell trade for [tradingsymbol] on [trade_date]. If the net position at end of day was zero, these were intraday trades. If you still hold shares, the buy was delivery."
  - Only buy OR only sell on that date → delivery trade.

**Note:** Tradebook does not have a product type (CNC/MIS) field. For EQ series, intraday vs delivery must be inferred from whether offsetting trades exist on the same day. For T2T series, all trades are always delivery.

### Rule 7: NSE vs BSE Price Difference
**if:** Client questions why price differs from what they expected and trades were on different exchanges
**then:** "Your trade was executed on [exchange]. Prices on NSE and BSE can differ slightly for the same stock at the same time. The execution price of ₹[price] is correct as per the [exchange] order book at the time of execution."

### Rule 8: Contract Note Queries — Manual Handling Required
**if:** Client asks about charges, brokerage, STT, MTM calculations, obligation breakdowns, or net settlement amounts from contract note
**then:** **AGENT HAS TO MANUALLY HANDLE.** This tool does not contain charge or obligation data. The agent must refer to the actual contract note for:
- Brokerage, STT, exchange transaction charges, SEBI charges, stamp duty, GST
- MTM (Mark-to-Market) calculations
- Net obligation amounts
- Gross vs net value differences

Tradebook only provides trade-level execution data (price, qty, date, exchange).

### Rule 9: Duplicate Trade Entries
**if:** Client or agent notices duplicate entries in tradebook (same order_id, same trade details appearing twice)
**then:** This is a known system issue that occurs on specific dates. Escalate with: client ID, affected trade_date, order_id(s), and tradingsymbol(s). Do not attempt to explain or resolve — the Console team will fix the duplicate entries.

### Rule 10: Tradebook vs Tax P&L Value Difference
**if:** Client says sell value in tradebook doesn't match Tax P&L
**then:** "The tradebook shows gross trade values (price × quantity) for each individual trade. The Tax P&L report may show different values because it applies FIFO matching — the sell value is matched against the corresponding buy entries, and the calculation may span different financial years or exclude intraday trades. Both reports are correct for their respective purposes."

### Rule 11: Escalation Criteria
**if:** Any of the following:
- Trade visible in Kite order history but missing from tradebook after T+1 (Rule 2)
- Duplicate entries detected (Rule 9)
- Execution price materially differs from limit order price placed by client (Rule 3)
- Trade entries found in neither tradebook, external trades, nor prepared tradebook (Rule 2)
**then:** Escalate with: client ID, trade_date, tradingsymbol, order_id, and specific discrepancy details.
