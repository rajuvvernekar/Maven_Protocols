# kite_positions

## Description

WHEN TO USE:

Customer asks about:
- Current open positions — intraday (MIS/CO), F&O (NRML), or same-day delivery (CNC)
- Position showing profit when buy average is higher than LTP or vice versa (multiple trades in same instrument, realised P&L included)
- P&L mismatch between positions page and funds page (entry price vs MTM settlement price)
- P&L changed after 3:30 PM, after market hours, or before market opens next day (closing price switch, BHAVCOPY update)
- Net vs day positions — difference between actual portfolio and today's trading activity
- Auto square-off — why it happened, timings (Equity 3:25 PM, F&O 3:26 PM, MCX), charges (₹50 + GST)
- Auto square-off failure — MIS position carried forward as CNC/NRML, circuit limit impact
- Circuit limit impact on MIS — upper circuit on sell position (short delivery risk), lower circuit on buy position (delivery conversion)
- Hedged positions — can't close hedge leg due to margin requirement increase on remaining leg
- Peak margin penalty from exiting one leg of a hedge (intraday snapshots catching one leg open)
- Product conversion — MIS↔CNC, MIS↔NRML (allowed with margin), CO conversion (blocked)
- Margin call, margin shortfall, or margin penalty on open positions
- F&O expiry — physical settlement for ITM stock options/futures, OTM expiring worthless, index F&O cash-settled
- Settlement price showing 0 for options (OTM — normal regardless of LTP)
- Higher margins blocked close to expiry (4 days before for ITM long options, expiry day for futures/short options)
- Fresh OTM stock option buy blocked in last 2 days before expiry
- Sold holdings appearing as negative positions during the day (tagged HOLDING — normal)
- Overnight quantity or carry-forward positions
- Margin shown when exiting a position (increase in utilised portfolio margin — order still executes)
- When intraday/F&O profits, delivery sale proceeds, BTST proceeds, or option premium become available
- NRI Non-PIS sale proceeds availability (75% same day, rest T+1)

TRIGGER KEYWORDS: "position", "open position", "intraday", "MIS", "NRML", "carry forward", "overnight", "square off", "squared off", "auto square off", "P&L positions", "MTM", "mark to market", "margin call", "margin shortfall", "margin penalty", "hedged position", "convert position", "conversion", "expiry", "physical settlement", "physical delivery", "ITM expiry", "OTM expiry", "settlement price", "net position", "day position", "negative position", "profit available", "withdrawal after selling", "circuit limit position", "CO conversion", "BTST proceeds", "option premium available"

## Protocol

# KITE_POSITIONS PROTOCOL

## Knowledge Base

<knowledge_base>
<facts>
- Positions = open trades for current day: intraday (MIS/CO), F&O (NRML), and same-day delivery (CNC). Holdings = settled shares in demat
- CNC buy on same day appears in Positions → moves to Holdings on T+1
- Net position = actual current portfolio (overnight + today's trades). Day position = only today's trading activity
- P&L in positions includes both realised (closed trades) and unrealised (open trades). Calculated from original entry price
- Funds page uses MTM settlement price for futures/short options — will differ from positions P&L
- P&L during market hours uses LTP. After 3:30 PM: equity uses closing price; F&O uses LTP at 3:30 PM. Next day before 9:15 AM: uses previous close
- F&O settlement prices update on positions page between 6:30–7:00 AM when BHAVCOPY arrives from NSE
- Settlement price = 0 for OTM options regardless of LTP — this is normal
- Multiple trades in same instrument same day: buy avg calculated across ALL trades, not just current position. Can show profit even if current buy avg > LTP
- Intraday profits available only after T+1 settlement. Sale proceeds from delivery available T+1
- Option premium from selling/exiting can be used only for buying options in same segment same day. Available for all trades from next day
- 100% of delivery sale proceeds available for new trades on same day (stocks or F&O). NRI Non-PIS: only 75% same day, rest T+1
- Intraday equity/F&O profits not usable on T day — available only after T+1 settlement
- BTST (T1 holdings) sale proceeds: available from next day only (no change)
- Margin shown when exiting a position = increase in utilised portfolio margin. Order will execute regardless
- Zerodha does NOT square off for freak trades — unrealised loss lasts only a fraction of a second
</facts>

<field_usage>
  <share>instrument_name | product | exchange | quantity | overnight_quantity | avg_price | pnl | buy_quantity | buy_value | buy_average_price | sell_quantity | sell_value | sell_average_price | last_close_price | net_change_percentage</share>
  <internal>ltp | day_buy_quantity | day_buy_price | day_sell_quantity | day_sell_price | day_sell_value</internal>
  <banned>None</banned>
</field_usage>

<auto_squareoff>
  <timings>
    <equity>3:25 PM</equity>
    <equity_fo>3:26 PM</equity_fo>
    <mcx>10 min before market close (MCX closes Nov–Mar: 11:55 PM; Mar–Nov: 11:30 PM — shifts with US DST)</mcx>
  </timings>
  <charge>₹50 + 18% GST per order squared off</charge>
  <failure_reasons>System/link failure, stock at circuit limit, connectivity issues</failure_reasons>
  <failure_consequence>MIS converts to CNC (equity) or NRML (F&O). Client responsible for closing. Zerodha may square off at discretion without margin call</failure_consequence>
</auto_squareoff>

<product_conversion>
  <allowed>MIS↔CNC (equity), MIS↔NRML (F&O/commodity), CNC↔NRML not applicable</allowed>
  <requires>Sufficient margin for target product type. Sell MIS→CNC also requires holdings</requires>
  <blocked>CO positions cannot be converted to any other product type</blocked>
  <blocked_agri>Agricultural commodity contracts (cardamom, mentha oil) cannot convert to MIS one day before tender period</blocked_agri>
</product_conversion>

<expiry_physical_settlement>
  <stock_fo>ITM stock options + futures: compulsory physical delivery of underlying stock</stock_fo>
  <otm>OTM stock options expire worthless — no obligation</otm>
  <index_fo>Cash-settled (no physical delivery)</index_fo>
  <margin_increase>4 days before expiry for ITM long options. Expiry day for futures/short options</margin_increase>
  <otm_buy_block>Fresh long OTM stock option positions blocked last 2 days before expiry</otm_buy_block>
  <delivery_timeline>Stocks credited T+1 after expiry. Short delivery: up to T+2</delivery_timeline>
</expiry_physical_settlement>

<margin_shortfall>
  <causes>Exiting hedge leg (remaining leg needs full margin), expiry of hedge leg, MTM loss exceeding 50% of funds, pledged stock value drop, haircut increase</causes>
  <margin_call>SMS + email + voice message. Add funds by 11:59 PM same day (after hours) or immediately (before hours)</margin_call>
  <penalty_rate>0.5% of shortfall (< ₹1L), 1% (≥ ₹1L). Up to 5% for 3+ instances/month</penalty_rate>
  <snapshots>4 random intraday snapshots (all segments except commodity). 8 for commodity. Peak margin penalty if snapshot catches one leg open</snapshots>
</margin_shortfall>

<hedged_positions>
- Cannot close hedge leg unless sufficient margin for remaining unhedged position
- Hedged margin < unhedged margin. Closing low-risk leg increases margin requirement
- Order sequence matters: buy hedge first → lower margin. Sell/short first → full margin until hedge placed
</hedged_positions>

<circuit_limit_impact>
- MIS sell position + upper circuit: cannot buy back → converts to delivery. If no shares in demat → short delivery + auction penalty
- MIS buy position + lower circuit: cannot sell → converts to CNC. Must maintain margin for delivery
</circuit_limit_impact>

<links>
  <short_delivery>https://support.zerodha.com/category/trading-and-markets/trading-faqs/general/articles/what-is-short-delivery-and-what-are-its-consequences</short_delivery>
  <margin_calculator>https://zerodha.com/margin-calculator</margin_calculator>
  <bulletin>https://zerodha.com/marketintel/bulletin</bulletin>
  <approved_securities>https://zerodha.com/approved-securities</approved_securities>
</links>
</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
**NEVER share:** `ltp`, `day_buy_quantity`, `day_buy_price`, `day_sell_quantity`, `day_sell_price`, `day_sell_value`
**Always share when relevant:** All fields in `<field_usage><share>`

### Rule 1: First Check — Locate Position
**if:** Customer asks about a specific instrument
**then:**
1. Search kite_positions by `instrument_name`
2. If found: note `product`, `quantity`, `overnight_quantity`, `avg_price`, `pnl`, `buy_quantity`, `sell_quantity`
3. If NOT found and customer says "I have a position": check if it was already squared off today (quantity = 0 with buy/sell history), or if it's a holdings query → invoke **kite_holdings**

### Rule 2: P&L Questions

**2.1 Profit showing when buy avg > LTP (or vice versa):** "When you make multiple trades in the same stock during the day, Kite calculates buy average across ALL trades — not just your current position. Your realised profit from earlier trades is included, which can show overall profit even if the current position's entry price is above the market price."

**2.2 P&L changed after 3:30 PM / before market opens:** "After 3:30 PM, equity P&L switches to the exchange closing price. For F&O, settlement prices update between 6:30–7:00 AM next day when the exchange sends the BHAVCOPY. This commonly causes P&L to shift."

**2.3 Positions P&L ≠ funds page:** "The Positions page calculates P&L from your original entry price. The Funds page uses the MTM (Mark-to-Market) settlement price for futures and short options. These are different calculations — the funds page reflects what's actually settled in your account." If customer wants to see funds page breakdown → invoke **kite_margins**.

**2.4 Settlement price = 0 for options:** "A settlement price of 0 means your option expired OTM (Out of The Money). This is normal regardless of what the LTP was — the settlement price is based on the underlying's weighted average in the last 30 minutes."

### Rule 3: Net vs Day Positions
**if:** Customer confused about net/day position data
**then:** "Net position shows your actual current portfolio after combining overnight carry-forward and today's trades. Day position shows only today's trading activity. Example: if you carried forward 75 NIFTY FUT and squared off today — net shows 0 (current state), day shows -75 (today's sell action)."

### Rule 4: Auto Square-off

**4.1 Why was my position squared off?** Check `product` = MIS or CO. "Intraday positions are auto-squared off at [refer `<auto_squareoff><timings>`]. Auto square-off charge: ₹50 + GST per order. To avoid this, close intraday positions before the square-off time." If customer asks about the square-off order → invoke **kite_orders**.

**4.2 Why was my position NOT squared off (carried forward)?** "Auto square-off can fail due to: circuit limits hit, system issues, or connectivity problems. Your MIS position has been converted to [CNC for equity / NRML for F&O] and carried forward. You must close it yourself. Ensure sufficient margin is available — Zerodha may square off at its discretion." Invoke **kite_margins** to check if margin is sufficient for the carried-forward position.

**4.3 Circuit limit impact on MIS:** "If your MIS sell position hits upper circuit — you can't buy back, so it converts to delivery. If you don't have shares in your demat, this results in [short delivery and auction penalties](https://support.zerodha.com/category/trading-and-markets/trading-faqs/general/articles/what-is-short-delivery-and-what-are-its-consequences). If your MIS buy position hits lower circuit — it converts to CNC and you must maintain delivery margin." If customer asks about holdings in demat for delivery → invoke **kite_holdings**.

### Rule 5: Product Conversion
**if:** Customer asks about converting positions
**then:**

**5.1 MIS↔CNC or MIS↔NRML:** "You can convert via Kite: Positions → tap/click on position → Convert Position. Requires sufficient margin for the target product type. [If sell MIS→CNC: also needs sufficient holdings.]" If margin insufficient → invoke **kite_margins** to check available margin.

**5.2 CO conversion:** "Cover Order positions cannot be converted to any other product type."

**5.3 Agricultural commodity restriction:** "Agricultural commodity contracts (cardamom, mentha oil) cannot be converted to MIS one day before the tender period starts."

### Rule 6: Hedged Positions & Margin

**6.1 Can't close hedge leg:** "You need sufficient margin to cover the remaining unhedged position. Closing the hedge leg increases your margin requirement." Invoke **kite_margins** to check `available_margin` and `used_margin`. "Options: add funds first, or exit both legs simultaneously."

**6.2 Peak margin penalty from exiting one leg:** "Even if you close both legs, the exchange takes random intraday snapshots (4 for equity F&O, 8 for commodity). If a snapshot catches one leg open, you may face a penalty. Penalty: [refer `<margin_shortfall><penalty_rate>`]."

### Rule 7: Margin Call / Shortfall
**if:** Customer received margin call or asks about margin penalty
**then:**

**7.1 Margin call received:** "Add funds by 11:59 PM same day (if received after hours) or immediately (if before hours). If not resolved, Zerodha may square off positions at its discretion." Invoke **kite_margins** to check current shortfall amount.

**7.2 Margin penalty charged:** "Exchange imposes margin penalty when insufficient margin is detected during intraday snapshots or at end of day. Penalty: 0.5% for shortfall under ₹1 lakh, 1% for ₹1 lakh+, up to 5% for 3+ instances in a month."

**7.3 Why margin shortfall if positions are closed:** "Shortfall can occur from intraday snapshots taken while your position was still open. Even if you closed it later, the snapshot captured the shortfall at that moment."

### Rule 8: F&O Expiry & Physical Settlement
**if:** Customer asks about expiry outcome or physical settlement
**then:**

**8.1 Stock F&O — ITM:** "ITM stock options and futures result in compulsory physical delivery. You need full cash or shares. Stocks credited T+1 after expiry. Margins increase 4 days before expiry for ITM long options and on expiry day for futures/short options." If customer asks about delivery shares → invoke **kite_holdings** to check if shares are credited.

**8.2 Stock F&O — OTM:** "OTM stock options expire worthless — no delivery obligation, no action needed."

**8.3 Index F&O:** "Index options and futures are cash-settled. ITM index options are auto-exercised; P&L settled in cash. OTM/ATM expire worthless."

**8.4 OTM buy blocked near expiry:** "Fresh long OTM stock option positions are blocked in the last 2 days before expiry due to physical settlement risk."

**8.5 Higher margins near expiry:** "Margin requirements increase as contracts approach expiry and physical delivery. Check the [margin calculator](https://zerodha.com/margin-calculator) for current requirements." Invoke **kite_margins** to check current `delivery_margin`.

### Rule 9: Sold Holdings as Negative Positions
**if:** Customer sees sold holdings as negative in positions
**then:** "When you sell shares from holdings during the trading day, they appear as a negative position tagged HOLDING in Positions. This is normal — allows intraday traders to buy back. If you don't intend to rebuy, ignore it. Shares debited from demat by end of day." If customer asks about holdings status → invoke **kite_holdings**.

### Rule 10: Profit Availability
**if:** Customer asks when profits become available
**then:**
- **Delivery sale proceeds:** 100% available for new trades on the same day (stocks or F&O).
- **NRI Non-PIS:** Only 75% of sale proceeds available same day; remaining 25% available T+1.
- **BTST (T1 holdings) sale:** Proceeds available from next trading day only.
- **Intraday profits (equity/F&O):** Not usable on T day. Available after T+1 settlement.
- **Options sold/exited:** Proceeds usable only for buying options in the same segment same day. Available for all trades from T+1.

If customer asks why their balance doesn't reflect the profit → invoke **kite_margins** to show `available_margin` and explain T+1 settlement. If customer asks about order execution details → invoke **kite_orders**. If customer asks about historical trades → invoke **kite_order_history**.
