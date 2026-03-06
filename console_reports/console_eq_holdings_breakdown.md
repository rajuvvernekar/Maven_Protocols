# console_eq_holdings_breakdown

## Description

WHEN TO USE:

- Agent needs to see the transaction-level detail of how a client's holdings were built (every buy, sell, CA entry)
- Client questions buy average and agent needs to walk through the FIFO calculation entry by entry
- Client asks to see the breakdown of their holdings for a specific stock
- Agent needs to verify if a corporate action entry (bonus, split, dividend reinvestment, merger, demerger) was posted
- Agent needs to confirm if an external/discrepant trade entry is reflected in the breakdown
- Client reports breakdown not matching tradebook or missing entries
- Client asks about LIQUIDBEES or ETF dividend reinvestment entries (fractional units at price 0)
- Agent needs to check if a specific buy/sell trade is included in the holdings calculation

TRIGGER KEYWORDS: "breakdown", "view breakdown", "holdings breakdown", "FIFO calculation", "how average calculated", "trade entries", "dividend reinvestment", "LIQUIDBEES dividend", "bonus entry", "split entry", "breakdown missing", "breakdown not showing"

## Protocol

## PROTOCOL

<knowledge_base>

<facts>
- This tool shows ALL entries impacting holdings: regular trades + external trades + corporate action credits/debits
- Each entry shows how the holding qty was built or adjusted over time — the complete audit trail
- Entries include: exchange trades (NSE/BSE), dividend reinvestments (exchange = DIVIDEND, price = 0), bonus credits (price = 0), split adjustments, merger/demerger entries, discrepant entries, buyback exits, gift/ESOP entries
- Buy average is calculated from these entries using FIFO — agent can walk through entries to verify
- pseudo_trade = true → system-generated entry (CA, dividend reinvestment, internal adjustment), not a client-initiated trade
- external_trade_type populated → entry came from external trades (discrepant, buyback, IPO, gift, ESOP, internal transfer)
- corporate_action_id populated → entry is linked to a specific corporate action event
- LIQUIDBEES/ETF dividend reinvestments: exchange = "DIVIDEND", price = 0, fractional qty credited — these are normal and directly impact avg price
- Breakdown entries may be delayed by up to 1 day after trade execution due to file processing
- Breakdown reflects the same data that drives buy average and P&L on Console — if breakdown is correct, avg and P&L are correct
- pledged field shows if specific entry's qty is currently pledged
</facts>

<field_usage>
  <share>tradingsymbol | isin | price | quantity | exchange | order_execution_time | external_trade_type | trade_type | trade_id | order_id</share>
  <banned>client_id | instrument_id | pseudo_trade (use internally to identify system entries but don't expose the term) | corporate_action_id (use internally to identify CA entries) | pledged (use internally)</banned>
</field_usage>

<entry_types>
  <regular_trade>exchange = NSE/BSE, pseudo_trade = false, external_trade_type = blank → normal buy/sell from tradebook</regular_trade>
  <dividend_reinvestment>exchange = DIVIDEND, price = 0, fractional qty, pseudo_trade = true → ETF/MF dividend unit credit (e.g., LIQUIDBEES)</dividend_reinvestment>
  <bonus_credit>price = 0, pseudo_trade = true, corporate_action_id populated → bonus shares credited at zero cost</bonus_credit>
  <split_adjustment>pseudo_trade = true, corporate_action_id populated → qty multiplied, price divided per split ratio</split_adjustment>
  <external_entry>external_trade_type = discrepant/buyback/IPO/gift/ESOP/internal_transfer → came from external trades</external_entry>
</entry_types>

<cross_reference>
  <console_eq_holdings>Current holdings summary with buy avg. If avg appears wrong, use breakdown to trace FIFO entry by entry.</console_eq_holdings>
  <console_eq_tradebook>Regular exchange trades. Breakdown should include all tradebook entries plus CA and external entries.</console_eq_tradebook>
  <console_eq_external_trades>External entries only. Breakdown includes these; use external trades tool to check if a specific entry was posted.</console_eq_external_trades>
  <console_eq_pnl>Realized P&L. Both breakdown and P&L are computed from the same FIFO logic.</console_eq_pnl>
</cross_reference>

<escalation_triggers>
  <breakdown_not_loading>Breakdown page returns error or fails to load for a stock</breakdown_not_loading>
  <entry_missing>Trade exists in tradebook but not in breakdown after 1+ trading day</entry_missing>
  <wrong_ca_entry>Corporate action entry has wrong qty or price in breakdown</wrong_ca_entry>
  <breakdown_tradebook_mismatch>Breakdown shows entries not found in tradebook and not explained by CA or external trades</breakdown_tradebook_mismatch>
</escalation_triggers>

</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
**NEVER expose:** `client_id`, `instrument_id`, `pseudo_trade`, `corporate_action_id`, `pledged`
**ALWAYS share when relevant:** `tradingsymbol`, `isin`, `price`, `quantity`, `exchange`, `order_execution_time`, `external_trade_type`, `trade_type`, `trade_id`, `order_id`
**NEVER say:** "pseudo trade" or "corporate action ID" to client. Instead say "system entry" or "corporate action entry".

### Rule 1: Walk Through FIFO Calculation
**if:** Client questions buy average and agent needs to verify
**then:** List all entries for the tradingsymbol chronologically. For each entry show: date, trade_type (buy/sell), quantity, price, and source (exchange trade / corporate action / external entry).

"Here is the breakdown of your [tradingsymbol] holdings:
[Date] — [Buy/Sell] [qty] shares at ₹[price] ([exchange/source])
[...continue for all entries...]

Your buy average is calculated using FIFO — when you sell, the oldest purchased shares are consumed first, changing the average of remaining shares."

If a sell entry exists, explain which buy entries it consumed under FIFO.

### Rule 2: Dividend Reinvestment Entries
**if:** Client questions entries with price = 0 or fractional quantities (typically LIQUIDBEES, GOLDBEES, other ETFs)
**then:** "The entries showing ₹0 price with small/fractional quantities for [tradingsymbol] are dividend reinvestment credits. When ETFs like LIQUIDBEES distribute dividends, the dividend amount is reinvested as additional units at zero acquisition cost. These are normal entries and directly impact your buy average calculation."

### Rule 3: Bonus/Split Entries in Breakdown
**if:** Client questions entries related to bonus or split in breakdown
**then:**
- Bonus: "The entry showing [quantity] shares at ₹0 on [date] is your bonus share credit. Bonus shares are credited at zero cost, which reduces your overall buy average."
- Split: "The split adjustment on [date] changed your holding from [old qty] shares to [new qty] shares. The price per share was proportionally adjusted. Your total investment value remains unchanged."

### Rule 4: Entry Missing from Breakdown
**if:** Client or agent finds a trade in tradebook that doesn't appear in breakdown
**then:** Check if the trade was executed within the last 1 trading day — breakdown entries may be delayed by up to 1 day due to file processing.

- If trade was yesterday → "Breakdown entries can take up to 1 trading day to reflect. The trade is recorded in the tradebook and will appear in the breakdown shortly. This delay does not affect your buy average or P&L."
- If trade was 2+ trading days ago and still not in breakdown → escalate.

### Rule 5: Breakdown Shows Extra Entries Not in Tradebook
**if:** Client says breakdown has entries they don't recognize
**then:** Check the entry type:
- If external_trade_type is populated → "This entry is a [external_trade_type] entry — it was recorded for shares received via [transfer/gift/IPO/ESOP/buyback]. You can verify the details in the external trades section."
- If exchange = DIVIDEND → "This is a dividend reinvestment credit." (Rule 2)
- If corporate action entry (price = 0, system entry) → "This is a corporate action entry for [bonus/split/merger/demerger] of [tradingsymbol]."
- If none of the above explain it → escalate as potential breakdown-tradebook mismatch.

### Rule 6: Breakdown Not Loading / Error
**if:** Client or agent reports breakdown not loading, showing error, or blank
**then:** Try a different stock to confirm if it's stock-specific or account-wide.
- If stock-specific → may be a data issue for that ISIN. Escalate with client ID and tradingsymbol.
- If account-wide → known intermittent issue. "The breakdown view is experiencing a temporary issue. Please try again after some time or use a different browser. If the issue persists, we'll investigate further." If persists beyond 24 hours → escalate.

### Rule 7: Verifying Buy Average is Correct
**if:** Client insists buy average is wrong and agent needs to prove it
**then:** Use breakdown entries to demonstrate FIFO step by step:
1. List all buy entries chronologically with qty and price
2. List all sell entries chronologically with qty
3. Show FIFO consumption: "When you sold [qty] on [date], the oldest [qty] shares bought at ₹[price] on [buy date] were consumed."
4. Calculate remaining shares and their weighted average

"Based on the FIFO calculation from your transaction history, your current buy average of ₹[buy_average] for [remaining qty] shares is correct."

If the calculation doesn't match what `console_eq_holdings` shows → escalate.

### Rule 8: Corporate Action Entry Verification
**if:** Agent needs to check if a specific CA (bonus, split, merger, demerger) was posted in breakdown
**then:** Look for entries with price = 0 (bonus), or entries around the CA date with adjusted qty/price (split/merger/demerger).
- If CA entry found → confirm to agent with date, qty, price.
- If CA entry not found and CA should have been processed → check timeline (bonus = T+2, split = immediate, demerger = 30-45 days). If beyond expected timeline → escalate.

### Rule 9: Escalation Criteria
**if:** Any of the following:
- Trade exists in tradebook but not in breakdown after 1+ trading day (Rule 4)
- Breakdown shows unidentifiable entries not explained by CA, external, or dividend (Rule 5)
- Breakdown page fails to load persistently (Rule 6)
- FIFO calculation from breakdown entries doesn't match buy average in `console_eq_holdings` (Rule 7)
- Expected CA entry not found in breakdown beyond expected timeline (Rule 8)
**then:** Escalate with: client ID, tradingsymbol, ISIN, specific missing/wrong entries, and dates.
