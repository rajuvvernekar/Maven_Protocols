# kite_order_history

## Description

WHEN TO USE:

Customer asks about:
- Orders placed on a past date or date range (not today's live orders)
- Order rejection reason from a previous day
- Execution details for historical orders — average price, filled quantity, exchange timestamp
- A specific instrument's order history (e.g., "what happened with my INFY order last week?")
- Whether an order was placed by them or auto-squared off by RMS (ADMINSQF/rms)
- Auto square-off history — when it happened, why, at what price, and the charge
- Auto square-off failure — MIS position carried forward as CNC/NRML
- SIP order execution or failures from past dates (wrong product type, insufficient margin)
- ATO (Alert Trigger Order) execution history and rejections (freeze quantity limit)
- GTT-triggered order results — whether the triggered order was executed or rejected
- Basket order execution history — which orders in the basket succeeded or failed
- AMO (After Market Order) execution from past dates — conversion to limit, pre-open behavior
- Iceberg order execution — parent-child order relationship
- Verifying order details from a past trading session (price, quantity, time, status)
- Disputing an order or trade from a previous day
- Identifying whether a trade was intraday or delivery (using product type and buy/sell pairing)
- F&O buy average calculation (FIFO method across product types)
- Equity buy average unchanged after same-day sell and rebuy (intraday treatment, except T2T)

TRIGGER KEYWORDS: "order history", "past order", "previous order", "old order", "trade history", "order on [date]", "last week order", "order rejected yesterday", "why was my order", "SIP order history", "ATO order", "basket order history", "GTT triggered order", "auto squared off", "squared off order", "execution time", "filled quantity", "rejection reason", "order status", "AMO order history", "iceberg order history", "intraday or delivery", "buy average FIFO", "who placed this order"

## Protocol

# KITE ORDER HISTORY PROTOCOL

## Knowledge Base

<knowledge_base>
<facts>
- kite_order_history returns orders for a date range (from_date to to_date) — for today's orders, use kite_orders
- Order statuses: COMPLETE, OPEN, CANCELLED, REJECTED
- Order types: MARKET, LIMIT, SL (Stop Loss Limit), SL-M (Stop Loss Market)
- Products: CNC (delivery), MIS (intraday), NRML (overnight F&O), MTF (margin trading), CO (cover order)
- Varieties: regular, amo, co, iceberg, auction
- Exchanges: NSE, BSE, NFO, BFO, MCX, NCO, CDS, BCD
- Orders follow price-time priority: first come, first served at same price
- Max 5,000 orders/day; 400 orders/minute; 25 modifications per order
- Max order value ₹10 Crore equity; max quantity 1,00,000 equity
- Unmatched order cancellation: Equity 4:00 PM | Currency 5:00 PM | MCX at market close (MCX shifts with US DST: Nov–Mar 11:55 PM, Mar–Nov 11:30 PM)
- Market orders may fill at multiple price points if insufficient depth at one level
- Limit orders may execute at better price (buy below limit, sell above limit)
- Pre-open market orders convert to limit at equilibrium price (or previous close if none)
- BSE market orders convert to limit with 3% market protection from LTP
- SL orders trigger on exchange tick data, not chart data — charts show 250ms snapshots, not every trade
- SL-M discontinued on BSE — use SL-L instead
- Auto square-off charge: ₹50 + 18% GST per order
- Auto square-off timings: Equity 3:25 PM, Equity F&O 3:26 PM, MCX 10 min before close
- If auto square-off fails (system failure, circuit hit, connectivity), MIS converts to CNC/NRML — client must close next day
- CO positions cannot be converted to CNC/NRML
- Zerodha pre-validates orders — some rejections won't appear in order book (shown in status notification only)
- F&O buy average uses FIFO method across product types (MIS + NRML combined)
- GTT-triggered orders: gtt field has trigger ID; check trigger details via kite_gtt/kite_gtt_archived
- SIP orders: sip = "Yes"; must use Regular CNC + market/limit order type
- ATO orders: ato = "Yes"; order slicing not supported for ATO; quantity must be within freeze limit
- Basket orders: basket field shows basket name; individual orders may succeed/fail independently
- Iceberg orders: parent_order_id links child orders to parent; sliced into smaller parts
- AMO timings: NSE/BSE equity 4:00 PM–8:58 AM, F&O 3:45 PM–9:10 AM, MCX 5:00 PM–9:10 AM
- AMO sell restriction without DDPI/POA: CNC/MTF sell AMO for T-day stocks only after 6:30 AM next day; delivered stocks after 5 PM
- AMO market orders for index options blocked — use limit
- Execution time beyond market hours = exchange reconciliation after connectivity issues, not actual execution beyond hours
</facts>

<field_usage>
  <share>client_id | created_at | instrument | type | product | exchange | total_quantity | filled_quantity | price | average_price | trigger_price | order_type | order_status | order_timestamp | exchange_timestamp | order_timestamp_date | rejection_reason | disclosed_quantity | cancelled_quantity | basket | sip | ato | gttp_sl_percentage | gttp_trgt_percentage</share>
  <internal>placed_by | variety</internal>
  <banned>validity | gtt | parent_order_id | order_id | exchange_id | validity_ttl | app_id | silo | basket_id | tags | gttp | order_result_id</banned>
</field_usage>

<status_values>
  <complete>Fully executed — all quantity filled</complete>
  <open>Pending execution — limit not hit, in queue, or circuit hit</open>
  <cancelled>By user, exchange end-of-session, IOC unfilled, or LPP range violation</cancelled>
  <rejected>Failed validation — check rejection_reason</rejected>
</status_values>

<placed_by_values>
  <client_id>Normal client-placed order (6-char client ID)</client_id>
  <adminsqf>Auto square-off by Zerodha RMS</adminsqf>
  <rms_prefix>Starts with "rms" + number (rms1, rms2...) — squared off by Zerodha RMS</rms_prefix>
</placed_by_values>

<auto_square_off>
  <equity>3:25 PM</equity>
  <equity_fno>3:26 PM</equity_fno>
  <mcx>10 minutes before market close</mcx>
  <charge>₹50 + 18% GST per order</charge>
  <failure>MIS converts to CNC/NRML if square-off fails — client must close next day</failure>
</auto_square_off>

<common_rejections>
  <insufficient_margin>Not enough margin — cross-check kite_margins</insufficient_margin>
  <negative_cash>Negative cash from MTM losses — must add cash. Can still exit existing positions</negative_cash>
  <max_order_value>Exceeds ₹10 Crore — split orders, use iceberg or basket</max_order_value>
  <max_quantity>Exceeds 1,00,000 — reduce qty, use iceberg or basket</max_quantity>
  <trigger_price_invalid>SL buy: trigger must ≤ limit price. SL sell: trigger must ≥ limit price</trigger_price_invalid>
  <sl_trigger_limit_gap>Trigger-to-limit gap exceeds exchange permissible range</sl_trigger_limit_gap>
  <lpp_range>Price outside Limit Price Protection range — retry closer to market price</lpp_range>
  <theoretical_price>Option price too far from theoretical — place closer to theoretical price</theoretical_price>
  <ban_period>F&O in ban — only exit allowed, no new positions or intraday</ban_period>
  <exchange_restricted>Account restricted by exchange — new account (wait 3 days), KRA verification pending, or NRI status</exchange_restricted>
  <slm_bse>SL-M blocked on BSE — use SL-L instead</slm_bse>
  <oi_restriction>NRML blocked for certain strikes due to broker OI cap. MIS allowed. Consider Orbis custodial</oi_restriction>
  <currency_position_limit>Client position limit exceeded: USDINR 85K lots, EURINR/GBPINR 5K, JPYINR 2K</currency_position_limit>
  <mtf_sell_conflict>MTF buy blocked — open CNC sell or MTF sell for same stock. Buy via CNC instead</mtf_sell_conflict>
  <market_order_blocked>Market orders blocked for stock options, T2T, debt, illiquid/deep ITM index options, zero-volume instruments. Use limit order</market_order_blocked>
  <mis_blocked>MIS blocked for T2T, ASM/GSM, low-liquidity, high-VAR, ban period. Use CNC or NRML</mis_blocked>
</common_rejections>

<links>
  <margin_calculator>zerodha.com/margin-calculator</margin_calculator>
  <market_intel>zerodha.com/marketintel/bulletin</market_intel>
</links>
</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
**NEVER expose:** fields in `<banned>` (order_id, exchange_id, validity, gtt, parent_order_id, validity_ttl, app_id, silo, basket_id, tags, gttp, order_result_id).
**Use for internal reasoning only:** `placed_by`, `variety` — do not expose field names or raw values.
**Always share when relevant:** `rejection_reason`, `order_status`, `average_price`, `filled_quantity`, `exchange_timestamp`.

### Rule 1: Order Status Check
**if:** Customer asks about a specific order
**then:** Locate by instrument + date. Share: `instrument`, `type`, `order_type`, `order_status`, `total_quantity`, `filled_quantity`, `average_price` (if COMPLETE), `exchange_timestamp`.
- COMPLETE → Rule 2
- OPEN → Rule 5
- CANCELLED → Rule 6
- REJECTED → Rule 3
- Check `placed_by` internally — if ADMINSQF or starts with "rms" → Rule 4

If customer asks about today's live orders → invoke **kite_orders**.

### Rule 2: Status = COMPLETE
**if:** `order_status` = COMPLETE
**then:** "Your [type] order for [total_quantity] qty of [instrument] was executed at ₹[average_price] on [exchange_timestamp]."

**2.1 Price discrepancy:**
- MARKET order → "Market orders fill at best available prices. Large quantities may fill across multiple price levels — average price reflects the weighted fill."
- LIMIT executed at better price → "Limit buy orders can execute below your limit price; limit sell orders above. Your limit at ₹[price] executed at ₹[average_price] because a better price was available."
- If customer wanted to buy only at a specific trigger level → "Use a Stop-Loss (SL) order with trigger price for intraday, or GTT for a long-standing order valid up to 1 year." If customer wants to set up GTT → invoke **kite_gtt**.
- SL/SL-M trigger dispute → "SL orders trigger on actual exchange ticks, not chart candles. Charts snapshot every 250ms and may miss brief price movements. The execution at ₹[average_price] was at a valid market price."

**2.2 Partial fill:** `filled_quantity` < `total_quantity` → "[filled_quantity] of [total_quantity] filled at ₹[average_price]. Remaining [cancelled_quantity] was cancelled. For IOC orders, unfilled portions are auto-cancelled."

If customer asks where the bought shares are now → invoke **kite_holdings** (if settled) or **kite_positions** (if same day / F&O).

### Rule 3: Status = REJECTED
**if:** `order_status` = REJECTED
**then:** Share `rejection_reason`. Match against `<common_rejections>` and provide actionable guidance:

- **Insufficient margin / negative cash** → Invoke **kite_margins** to cross-check. "Your order was rejected due to insufficient margin. [State available_margin/available_cash from kite_margins.] Please add funds. You can still exit existing positions."
- **Market order blocked** → "Market orders are blocked for [instrument]. Use a limit order instead."
- **MIS blocked** → "Intraday (MIS) is blocked for [instrument]. Use CNC for equity or NRML for F&O."
- **Max value/quantity** → "Order exceeds the limit (₹10 Crore / 1,00,000 qty). Split using iceberg or basket orders."
- **Trigger price errors** → "For [BUY/SELL] SL: trigger must be [≤/≥] limit price. Correct and retry."
- **Ban period** → "This F&O contract is in ban. Only exit orders allowed." If customer asks about current position in banned contract → invoke **kite_positions**.
- **OI restriction** → "NRML restricted for this strike due to broker OI cap. MIS still allowed. For full access, consider Orbis custodial account."
- **SL-M on BSE** → "SL-M discontinued on BSE. Use SL-L — set limit slightly away from trigger to mimic SL-M."
- **Exchange restricted** → "Exchange has restricted trading. Possible causes: new account (wait 3 working days), KRA verification pending, or NRI status update needed."
- **MTF conflict** → "MTF buy blocked — you have an open CNC sell or MTF sell for this stock today. Use CNC buy instead."
- **Currency position limit** → "Position limit exceeded. Limits: USDINR 85K lots, EURINR/GBPINR 5K, JPYINR 2K."
- **Unmatched rejection** → share `rejection_reason` verbatim.

### Rule 4: RMS / Admin Square-Off
**if:** `placed_by` = "ADMINSQF" OR starts with "rms"
**then:** This order was placed by Zerodha's Risk Management System. Investigate why:

1. Invoke **kite_margins** to check for margin shortfall (`available_margin`, `used_margin`, `available_cash`)
2. Check if `product` was MIS and order time was near auto square-off window
3. Check if account had negative cash balance

Response: "This [type] order for [instrument] was executed by Zerodha's risk management system on [exchange_timestamp]. This typically happens when:
- Your account had insufficient margin to maintain the position
- It was an intraday (MIS) position auto squared off at the scheduled time (Equity 3:25 PM, F&O 3:26 PM, MCX 10 min before close)
- Your account had a negative cash balance requiring position closure

Auto square-off charge: ₹50 + 18% GST per order."

**4.1 Auto square-off failed (MIS carried forward):**
**if:** Customer says MIS position carried overnight unexpectedly
**then:** "Auto square-off may fail due to circuit limits, system failures, or connectivity issues. When this happens, MIS converts to CNC (equity) or NRML (F&O) and carries forward. You must close the position on the next trading day."

### Rule 5: Status = OPEN (Historical)
**if:** `order_status` = OPEN in historical data
**then:** This is unusual in history — likely the order was later cancelled at end of session. Check if a corresponding CANCELLED entry exists for the same instrument/date. If so, apply Rule 6.

If genuinely open across days (shouldn't happen): "Unmatched pending orders are auto-cancelled by the exchange at session end: Equity 4:00 PM, Currency 5:00 PM, MCX at market close."

### Rule 6: Status = CANCELLED
**if:** `order_status` = CANCELLED
**then:**
- If cancelled near session end → "Unmatched pending orders are auto-cancelled by the exchange at session end. Place again next session, or use GTT for orders valid up to 1 year." If customer wants to set up GTT → invoke **kite_gtt**.
- If `rejection_reason` contains "limit price protection" or "LPP" → "Exchange cancelled your order — price was outside the allowed range. Retry closer to market price."
- If `filled_quantity` > 0 and `cancelled_quantity` > 0 → "Partially filled: [filled_quantity] of [total_quantity] executed at ₹[average_price]. Remaining [cancelled_quantity] was cancelled."
- If IOC order (infer from context) → "IOC orders auto-cancel any unfilled portion immediately."

### Rule 7: Unauthorized / "I Didn't Place This"
**if:** Customer says they didn't place an order
**then:** Check `placed_by` internally:
- If ADMINSQF or starts with "rms" → apply Rule 4 (RMS square-off)
- If `placed_by` = customer's client ID → **escalate to investigation team**. "This order appears to have been placed from your account. For security, we're escalating this for investigation. Please also check if any third-party apps have Kite Connect API access, and consider blocking your account if you suspect unauthorized activity."

### Rule 8: SIP Order Investigation
**if:** `sip` = "Yes" or customer asks about SIP order failure
**then:** Check `order_status` and `rejection_reason`:
- REJECTED → share reason. Common failures: wrong product type (must be Regular CNC), insufficient margin, instrument blocked for market orders, quantity exceeds limit.
- COMPLETE → share execution details normally.
- No order found → "SIP may not have triggered. Check that: basket is linked to SIP, product type is Regular CNC, order type is market or limit. Also check your registered email — Zerodha sends a SIP summary email with rejection reasons if the order failed."

### Rule 9: ATO Order Investigation
**if:** `ato` = "Yes" or customer asks about ATO order
**then:**
- REJECTED → share reason. Common: quantity exceeds freeze limit (order slicing not supported for ATO).
- "ATO orders place automatically when your Kite alert triggers. Order slicing is not available — quantity must be within the exchange freeze limit."

### Rule 10: AMO Orders
**if:** Customer asks about AMO behavior in history
**then:** Use `variety` internally to confirm AMO.
- AMO executes at next market open.
- AMO market order for index options → blocked; use limit.
- Pre-open AMO market order → converts to limit at equilibrium/previous close price.
- AMO sell restriction without DDPI/POA: T-day stocks → sell AMO only after 6:30 AM next day; delivered stocks → after 5 PM.

### Rule 11: Basket Order Investigation
**if:** `basket` field has a value
**then:** "This order was part of basket '[basket]'. Basket orders execute individually — each is subject to its own margin and exchange validation. Some may succeed while others fail."

### Rule 12: Execution Time Beyond Market Hours
**if:** Customer questions execution time showing after market close
**then:** "The displayed time reflects exchange reconciliation after a connectivity disruption. Your order was executed within market hours. Check the tradebook for actual execution time."

### Rule 13: F&O Buy Average (FIFO) & Intraday Identification
**if:** Customer asks about buy average from historical orders OR asks whether a trade was intraday
**then:**

**F&O:** Buy average uses FIFO (First In, First Out). Earliest buy matches first sell, regardless of MIS or NRML. Both product types combined for FIFO.

**Equity (CNC) — sell and buy back same day:** If customer sells shares from holdings and buys them back on the same day, the original buy average remains unchanged. The same-day buy+sell is treated as an intraday (speculative) trade since shares don't physically move in/out of the demat account. This is per income tax rules — transactions without delivery are classified as speculative and kept separate from delivery (capital gains) transactions.

Exception: This does not apply to T2T (Trade to Trade) stocks — for T2T, the buy average updates to the latest buy price.

**Identifying intraday:** If BUY + SELL of the same instrument and same quantity exist on the same day — regardless of product type (MIS, CNC, NRML) — it is treated as an intraday trade.

If customer asks about current holding buy average → invoke **kite_holdings**. If customer asks about current open positions → invoke **kite_positions**.

### Rule 14: Multiple Orders for Same Instrument
**if:** Multiple orders exist for same instrument on queried date
**then:** Summarize: "[N] orders found for [instrument] on [date]." List each with type, order_type, product, status, quantity, price. Let customer identify which one.

Use `product` and buy/sell pairing to identify trade type:
- MIS or CO → Intraday trade
- CNC with only BUY (no same-day SELL) → Delivery / longterm
- CNC with BUY + SELL of same instrument and same quantity on same day → treated as an intraday trade
- NRML → Overnight F&O position
- MTF → Margin Trading Facility (delivery with leverage)

If BUY + SELL for same instrument on same day with matching quantity → intraday round-trip (regardless of product type).
If BUY (MIS) + SELL by ADMINSQF/rms → intraday position that was auto squared off.

### Rule 15: No Matching Orders Found
**if:** No orders found for described instrument/date
**then:** "No orders found for [instrument] between [from_date] and [to_date]. Please verify the instrument name, exchange, and date range. Orders rejected pre-exchange (before reaching exchange) may not appear in history."
If customer is looking for today's orders → invoke **kite_orders**.
