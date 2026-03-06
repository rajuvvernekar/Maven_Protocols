# console_fno_pnl

## Description

WHEN TO USE:

- Client questions realized F&O P&L (profit or loss from closed/expired contracts)
- Client reports F&O P&L values (buy value, sell value, profit) appearing wrong
- Client asks why a contract shows profit when they expected loss, or vice versa
- Agent needs to verify realized P&L for a specific F&O contract or date range
- Client asks about P&L for physically settled contracts (ITM options/futures at expiry)
- Client questions F&O P&L in Tax P&L report vs Console P&L
- Client asks about expired contract not showing in P&L
- Client reports asterisk (*) mark on P&L entries after contract symbol change

TRIGGER KEYWORDS: "F&O P&L", "FnO profit", "FnO loss", "futures P&L", "options P&L", "realized F&O", "F&O buy value", "F&O sell value", "derivative P&L", "contract P&L", "expiry P&L", "physical delivery P&L", "F&O tax P&L", "options turnover"

## Protocol

# CONSOLE FNO PNL PROTOCOL

## Business Rules

### Rule 0: Segment Selection
**if:** Agent looks up F&O P&L
**then:** Confirm correct segment: FO for equity F&O, CDS for currency, COM for commodities. Wrong segment = no results or incomplete data.

### Rule 1: Field Protection
**NEVER expose:** `client_id`
**ALWAYS share when relevant:** `tradingsymbol`, `quantity`, `buy_value`, `buy_average`, `sell_value`, `sell_average`, `realized_profit`, `realized_profit_percentage`

### Rule 2: P&L Verification
**if:** Client questions realized F&O P&L for a contract
**then:** "Your realized P&L for [tradingsymbol]: [quantity] contracts with buy value ₹[buy_value] (avg ₹[buy_average]) and sell value ₹[sell_value] (avg ₹[sell_average]), resulting in a [realized_profit > 0 ? 'profit' : 'loss'] of ₹[realized_profit] ([realized_profit_percentage]%)."

### Rule 3: Physical Delivery P&L
**if:** Client questions P&L for an ITM stock option or futures contract that expired with physical delivery
**then:** "Your [tradingsymbol] contract was physically settled at expiry. In F&O P&L, the ITM contract is closed at intrinsic value (or zero), which may show as a loss on the F&O side. However, the actual shares were delivered/received, and the delivery P&L is reflected in your equity P&L as an intraday delivery trade.

To see your total P&L on this position, you need to combine the F&O P&L entry with the corresponding equity delivery P&L entry in `console_eq_pnl`."

**if:** Client reports double quantity in equity P&L after physical settlement → escalate.

### Rule 4: OTM Options Expired Worthless
**if:** Client asks about P&L for options that expired worthless
**then:**
- Long position (bought options): "Your [tradingsymbol] option expired out-of-the-money (OTM) and became worthless. The entire premium paid (₹[buy_value]) is reflected as a realized loss."
- Short position (sold options): "Your [tradingsymbol] option expired OTM. The full premium received (₹[sell_value]) is reflected as realized profit since the option expired worthless."

### Rule 5: Asterisk (*) on P&L Entry
**if:** Client asks about asterisk mark on F&O P&L entries
**then:** "The asterisk (*) mark indicates that the contract symbol was changed during the series due to a corporate action on the underlying stock (e.g., lot size change, symbol rename). The system closed the old contract and opened a new one with adjusted terms. This appears only on the adjustment day — subsequent days will show normally. Your P&L is calculated correctly across both contract versions."

### Rule 6: Expired Contract Not in P&L
**if:** Client says an expired contract is not showing in P&L report
**then:** Verify internally:
- Correct segment selected (Rule 0)
- Date range covers the expiry date
- If both correct and contract still missing → escalate directly with: client ID, tradingsymbol, expiry date, segment, date range used. Do not send a response to the client asking them to check — escalate immediately.

### Rule 7: Tax P&L vs Console F&O P&L
**if:** Client says Tax P&L F&O values differ from Console F&O P&L
**then:** "The Tax P&L report and Console F&O P&L may show different values because:
- Tax P&L classifies trades by type (futures, options) and calculates turnover as the absolute value of profit per contract
- Console F&O P&L shows aggregate realized profit per contract for the selected date range
- Physical delivery contracts may appear split between F&O and equity sections in Tax P&L
- Intraday contracts on certain dates may be excluded from one tab — known issue for specific dates

For income tax filing, use the Tax P&L report."

If client reports significant unexplained difference between F&O tab and tradewise exits tab → escalate.

### Rule 8: Charges and MTM Queries
**if:** Client asks about charges, brokerage, STT, or MTM calculations on F&O P&L
**then:** **AGENT HAS TO MANUALLY HANDLE.** This tool shows realized P&L only — no charge or MTM breakdown. Agent must refer to contract note and ledger.

### Rule 9: Escalation Criteria
**if:** Any of the following:
- Expired contract not in P&L after verifying correct segment and date range (Rule 6)
- P&L values don't match tradebook calculations after agent verification (KB trigger)
- Verified P&L shows error or inconsistent data (KB trigger)
- Physical settlement showing double qty in equity P&L (Rule 3)
- Significant unexplained difference between Tax P&L tabs (Rule 7)
**then:** Escalate with: client ID, tradingsymbol, segment, date range, and specific discrepancy.
