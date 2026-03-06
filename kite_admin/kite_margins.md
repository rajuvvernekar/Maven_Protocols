# kite_margins

## Description

WHEN TO USE:

Customer asks about:
- Available margin, available cash, used margin, or opening balance values
- What any field on the Kite funds page means — payin, payout, SPAN, exposure, delivery margin, option premium, collateral, M2M
- Balance seeming wrong, not matching, or showing an unexpected amount
- Why profits from today or yesterday are not reflecting in the balance (T+1 settlement)
- Account in negative balance or debit — interest charges, consequences, how to resolve
- Margin shortfall, margin call, or how to avoid margin penalty (CC snapshots, deadline to add funds)
- Why margin shortfall exists even after closing positions (peak snapshot already captured)
- Collateral margin — liquid collateral (cash equivalent), equity collateral (non-cash), total collateral, 50% cash requirement for F&O
- Unsettled funds or when profits will be available for trading/withdrawal
- Used margin showing negative (credit from selling holdings or closing long options)
- MTM (Mark to Market) — how M2M realised works, daily revaluation of futures, short options margin behavior
- Option premium field showing positive (sold) or negative (bought)
- Free cash calculation or how available margin is computed
- Difference between Kite positions P&L and funds page P&L (entry price vs MTM settlement price)
- Opening balance not matching expected amount (T+1 settlement, MTM, charges, holidays)
- Sale proceeds availability — 100% same day for holdings (since Oct 2024)
- Available cash rounding on Kite (1 decimal display, full amount withdrawable)
- Market order causing negative balance (validation vs execution price difference)
- Weekend or holiday payin visibility (appears on Monday)

TRIGGER KEYWORDS: "available margin", "available cash", "opening balance", "used margin", "fund balance", "funds page", "funds tab", "collateral", "SPAN", "exposure margin", "delivery margin", "option premium", "free cash", "negative balance", "debit balance", "margin shortfall", "margin call", "margin penalty", "MTM", "mark to market", "M2M", "unsettled funds", "profit not showing", "yesterday profit", "payin", "payout", "balance incorrect", "balance wrong", "balance mismatch", "margin blocked", "sale proceeds", "interest on negative", "opening balance wrong"

## Protocol

# KITE MARGINS PROTOCOL

## Knowledge Base

<knowledge_base>
<facts>
- Available Margin = total funds for trading (cash + collateral + premium received + realised/unrealised P&L - used margin)
- Available Cash = previous day closing balance + payin - payout ± day's settled activity; if negative → 0.05%/day (18% p.a.) interest
- Opening Balance = previous day's closing balance after reversing blocked margin
- Used Margin = margin blocked for open positions + open orders; negative when selling holdings or closing long options
- Free Cash = Cash Margin Available + Pay In + Direct Collateral - Margin Used
- Payin = funds added during the day; weekend payins appear on Monday
- Payout = funds withdrawn during the day
- Total Collateral = Liquid Collateral + Equity Collateral
- Liquid Collateral = pledged LiquidBees/liquid MFs after haircut; treated as cash equivalent
- Equity Collateral = pledged stocks/ETFs/MFs after haircut
- Option Premium = premium paid (-ve for buying) or received (+ve for selling); included in available cash, shown separately
- SPAN = exchange-calculated risk margin for F&O; revised throughout day
- Exposure = margin over SPAN (index: 2% contract value; stock: 3.5% or 1.5 SD)
- SPAN + Exposure = Initial Margin
- Delivery Margin = T1 sale proceeds + physical delivery margin for ITM stock options during expiry week + additional MCX margin near expiry
- M2M Realised = realised MTM P&L from closed F&O positions
- M2M Unrealised = unrealised MTM P&L from open F&O positions (BANNED — never share)
- Intraday/F&O profits available only after T+1 settlement; not usable same day
- Sale proceeds from holdings: 100% available same day (effective Oct 7, 2024)
- Exchange requires 50% of F&O margin in cash/cash-equivalent; non-cash shortfall → 0.035%/day (12.775% p.a.)
- MTM: exchange revalues open futures daily at closing price; settles P&L to account
- Short options: no daily MTM; margin increases as options move ITM
- Positions P&L uses entry price; Funds page uses last MTM settlement price → may differ intraday
- CC takes 4 random margin snapshots/day; peak used for shortfall calculation
- Available Cash on Kite rounded to 1 decimal; full amount withdrawable
- Only Equity category is relevant; ignore Commodity category
</facts>

<field_usage>
  <share>opening_balance | available_margin | used_margin | available_cash | payin | payout | span | delivery_margin | exposure_margin | option_premium | liquid_collateral | equity_collateral | total_collateral | m2m_realised</share>
  <internal></internal>
  <banned>m2m_unrealised</banned>
</field_usage>

<margin_call_rules>
  <before_market>Add funds immediately</before_market>
  <after_market>Add funds by 11:59 PM same day</after_market>
  <no_action>Positions squared off at Zerodha's discretion</no_action>
  <snapshots>CC takes 4 random snapshots/day; peak used for shortfall</snapshots>
</margin_call_rules>

<negative_balance>
  <interest>0.05%/day or 18% p.a.</interest>
  <brokerage>₹40 per executed F&O order (instead of ₹20)</brokerage>
  <action>Positions may be squared off without notice</action>
</negative_balance>

<collateral_rules>
  <cash_requirement>50% of F&O margin must be cash or cash-equivalent</cash_requirement>
  <cash_equivalent>LiquidBees ETF, liquid mutual funds (after haircut)</cash_equivalent>
  <non_cash_shortfall_charge>0.035%/day or 12.775% p.a.</non_cash_shortfall_charge>
  <usable_for>Equity intraday, futures, options buying and writing</usable_for>
</collateral_rules>

<links>
  <margin_calculator>zerodha.com/margin-calculator</margin_calculator>
  <intraday_leverages>zerodha.com/marketintel/bulletin/249809/latest-intraday-leverages-mis-bo-co</intraday_leverages>
  <approved_securities>zerodha.com/approved-securities</approved_securities>
  <verify_equity_collateral>investorhelpline.nseindia.com/ClientCollateral/welcomeCLUser</verify_equity_collateral>
  <verify_commodity_collateral>clientreports.mcxccl.com</verify_commodity_collateral>
</links>
</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
**if:** Responding to any query
**then:** NEVER share `m2m_unrealised`. All other fields in `<share>` can be shown to the customer. Always use `₹` formatting for amounts.

### Rule 1: Explain Funds Page Field
**if:** Customer asks what a specific field on the funds page means
**then:** Explain using `<facts>` definitions. Map customer language to field:
- "balance" / "available balance" → `available_margin` or `available_cash`
- "margin used" / "blocked margin" → `used_margin`
- "collateral" → check `liquid_collateral`, `equity_collateral`, or `total_collateral`
- "premium" → `option_premium`
- "SPAN" / "exposure" → `span`, `exposure_margin`
- "delivery margin" → `delivery_margin`
- "opening balance" → `opening_balance`
- "payin" / "funds added" → `payin`
- "payout" / "withdrawal" → `payout`
- "MTM" / "M2M" → `m2m_realised` (never share unrealised)

### Rule 2: Balance Inquiry
**if:** Customer asks about their current balance, available margin, or available cash
**then:** Share `available_margin` (₹[available_margin]), `available_cash` (₹[available_cash]), `opening_balance` (₹[opening_balance]), and `used_margin` (₹[used_margin]). If `used_margin` is negative, explain: negative used margin means credit from selling holdings or closing long options positions. If customer asks why margin is blocked or about a specific order blocking margin → invoke **kite_orders**.

### Rule 3: Profit Not Showing in Balance
**if:** Customer asks why today's or yesterday's intraday/F&O profits are not reflected
**then:** "Intraday and F&O profits are available only after T+1 settlement (next trading day). Your current available margin of ₹[available_margin] does not include today's unsettled profits. These will reflect in your opening balance on the next trading day. If the next day is a settlement holiday, it takes an additional day."
If customer asks about specific position P&L → invoke **kite_positions**.

### Rule 4: Negative Available Cash
**if:** `available_cash` < 0
**then:** "Your available cash is ₹[available_cash]. A negative cash balance attracts interest at 0.05% per day (18% p.a.). Please add funds to clear the negative balance. If no funds are added, open positions may be squared off."

### Rule 5: Used Margin Negative
**if:** `used_margin` < 0 AND customer is confused
**then:** "Your used margin shows ₹[used_margin] (negative) because you have received credit from selling holdings or closing long option positions today. This credit is included in your available margin."
If customer asks which holdings were sold → invoke **kite_holdings**.

### Rule 6: Collateral Query
**if:** Customer asks about collateral, pledge margin, or why collateral isn't being used
**then:** Share `liquid_collateral` (₹[liquid_collateral]), `equity_collateral` (₹[equity_collateral]), `total_collateral` (₹[total_collateral]).
- Liquid collateral = cash equivalent; can satisfy 50% cash requirement for F&O.
- Equity collateral = non-cash; if used beyond 50% cash limit, attracts 0.035%/day charge.
- Collateral usable for: equity intraday, futures, options buying and writing.
- Verify details: `<verify_equity_collateral>` for equity, `<verify_commodity_collateral>` for commodity.
- Approved list and haircuts: `<approved_securities>`.

### Rule 7: Margin Shortfall / Margin Call
**if:** Customer received margin call or asks about margin shortfall
**then:** "Please add funds to your Zerodha account to cover the shortfall.
- If margin call received before market hours → add funds immediately.
- If received after market hours → add by 11:59 PM same day.
- If funds are not added, positions may be squared off at Zerodha's discretion.

Note: The Clearing Corporation takes 4 random margin snapshots during the day. The peak requirement is used — so a shortfall can occur even after closing positions if a snapshot was already captured."
If customer asks which positions caused the shortfall → invoke **kite_positions**.

### Rule 8: Shortfall After Closing Positions
**if:** Customer asks why shortfall exists even though positions are already closed
**then:** "The Clearing Corporation captures 4 random margin snapshots during the day and uses the peak margin requirement. Even if you've closed your positions, a shortfall can occur if a snapshot was already captured when your margin was at its peak. Please add the shortfall amount mentioned in the email by 11:59 PM today to avoid a margin penalty."

### Rule 9: Option Premium Field
**if:** Customer asks about option premium showing positive or negative
**then:** "The option premium field shows:
- Positive (+ve): premium received from selling/writing options.
- Negative (-ve): premium paid for buying options.
This amount is included in your available cash and shown separately for visibility."

### Rule 10: SPAN / Exposure / Delivery Margin
**if:** Customer asks about SPAN, exposure, or delivery margin being blocked
**then:** Share `span` (₹[span]), `exposure_margin` (₹[exposure_margin]), `delivery_margin` (₹[delivery_margin]).
- SPAN + Exposure = Initial Margin required by exchange for F&O positions.
- Delivery margin is blocked for: T1 holding sale proceeds, ITM stock options during expiry week (physical delivery), or MCX contracts near expiry.
- SPAN is revised by exchanges throughout the day.
- Check margin requirements: `<margin_calculator>`.
If customer asks which position is blocking margin → invoke **kite_positions**. If customer asks about a specific order's margin requirement → invoke **kite_orders**.

### Rule 11: Payin/Payout Query
**if:** Customer asks about payin or payout values
**then:** Share `payin` (₹[payin]) and `payout` (₹[payout]).
- Payin = funds added to your account today.
- Payout = funds withdrawn today.
- Weekend payins appear under payin on Monday.

### Rule 12: P&L Mismatch — Positions vs Funds Page
**if:** Customer asks why P&L in positions differs from funds page
**then:** "Kite positions calculates P&L based on your original entry price. The funds page uses the last Mark to Market (MTM) settlement price for open futures and short options positions. The overall P&L will be the same once positions are closed, but intraday values may differ due to this MTM adjustment."
Share `m2m_realised` (₹[m2m_realised]) as reference. If customer wants position-level P&L breakdown → invoke **kite_positions**.

### Rule 13: Opening Balance Mismatch
**if:** Customer says today's opening balance doesn't match expected amount
**then:** "Your opening balance of ₹[opening_balance] is the previous day's closing balance after reversing any blocked margin. Differences may occur due to:
- Settlement of previous day's trades (T+1)
- MTM settlement on open F&O positions
- Charges/brokerage deducted
- Settlement holiday delays"
If customer asks about specific charges or ledger entries → invoke **ledger_report**.

### Rule 14: Sale Proceeds Availability
**if:** Customer asks when proceeds from selling holdings will be available
**then:** "As of October 7, 2024, 100% of the proceeds from selling your holdings are available on the same day for all trades, including stocks and F&O positions."
If customer asks about specific holdings sold → invoke **kite_holdings**.

### Rule 15: Unsettled Funds
**if:** Customer asks about unsettled funds
**then:** "Unsettled funds are credits you expect from profits or sold holdings that are pending T+1 settlement. You cannot withdraw these until settlement is complete. If T+1 falls on a settlement holiday, it takes an additional day."

### Rule 16: Available Cash Rounding
**if:** Customer notices decimal discrepancy in funds page
**then:** "Available cash on Kite is rounded to 1 decimal place for display. For example, ₹1005.53 shows as ₹1005.5. The full amount is withdrawable."

### Rule 17: Market Order Causing Negative Balance
**if:** Customer asks why account went negative after a market order
**then:** "Market orders are validated at the best available price but execution can occur at a different price — especially at market opening. This price difference can cause a negative balance. A negative cash balance attracts interest at 0.05%/day (18% p.a.), and a brokerage of ₹40 per executed F&O order applies. Please add funds to clear the negative balance."
If customer asks about the specific order → invoke **kite_orders**. If customer asks about order history → invoke **kite_order_history**.

### Rule 18: MTM Explanation
**if:** Customer asks about MTM / Mark to Market
**then:** "Mark to Market (MTM) is the daily revaluation of open futures positions by the exchange at the closing price. Profits or losses are settled to your account daily. This is reflected in `m2m_realised` (₹[m2m_realised]) for closed positions. Short options don't undergo daily MTM — instead, margin increases as they move in-the-money."
If customer asks about specific position MTM → invoke **kite_positions**.
