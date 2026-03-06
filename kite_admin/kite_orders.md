# kite_orders

## Description

WHEN TO USE:

Customer asks about:
- Today's order status — whether it was executed, pending, cancelled, or rejected
- Order rejection reason or error message when placing an order
- Order pending or not getting executed despite being placed
- Order cancelled at end of day or by exchange
- Partial fill — only some quantity executed, rest cancelled
- Execution price different from expected — market order filled at multiple levels, limit order got a better price, SL triggered at unexpected price
- Market orders blocked for a specific instrument (stock options, T2T, illiquid, deep ITM, ETFs)
- MIS or intraday orders blocked for a stock or contract (T2T, ASM/GSM, ban period, low liquidity)
- Auto square-off — position squared off by Zerodha/RMS, timings, charges, or why it failed and carried forward
- Unauthorized order — customer says they didn't place an order
- AMO (After Market Order) — placement, rejection, conversion to limit in pre-open, timing
- Product type conversion — MIS↔CNC, MIS↔NRML, CO conversion blocked
- Circuit limit or ban period impact on open orders
- Order types (MARKET, LIMIT, SL, SL-M), product types (CNC, MIS, NRML, MTF, CO), or validity types (DAY, IOC, TTL)
- Auto square-off timings, charges (₹50 + GST), or consequences of failed square-off
- Order book display issues — rejected order not visible, downloaded file showing dates instead of quantities, execution time beyond market hours

TRIGGER KEYWORDS: "order rejected", "order pending", "order cancelled", "not executed", "not filled", "rejection reason", "squared off", "square off", "auto square", "RMS", "ADMINSQF", "market order blocked", "MIS blocked", "intraday blocked", "AMO", "after market order", "wrong price", "different price", "execution price", "circuit limit", "ban period", "order status", "product conversion", "convert MIS", "convert CNC", "convert NRML", "unauthorized order", "order error", "order not placed", "partial fill", "IOC", "SL triggered", "stoploss triggered", "cover order", "iceberg", "order book", "order window"

## Protocol

# KITE_ORDERS PROTOCOL

## Knowledge Base

<knowledge_base>
<facts>
- kite_orders returns today's orders only — for historical, use kite_order_history
- Clicking instrument hyperlink opens Order History sub-view showing full lifecycle: OPEN PENDING → OPEN → COMPLETE/CANCELLED/REJECTED with timestamps, exchange times, filled qty, avg price, variety
- Orders follow price-time priority: first come, first served at same price
- Unmatched order cancellation: Equity 4:00 PM | Currency 5:00 PM | Commodities at MCX market close (MCX shifts with US DST: Nov–Mar closes 11:55 PM, Mar–Nov closes 11:30 PM)
- Max 5,000 orders/day across all segments; 400 orders/minute; 25 modifications per order
- Max order value ₹10 Crore equity; max quantity 1,00,000 equity (regular can exceed; iceberg/CO cannot)
- Zerodha pre-validates orders — some rejections won't appear in order book (shown in status notification only)
- Market orders may fill at multiple price points if insufficient depth at one level
- Limit orders may execute at better price (price improvement by exchange matching engine)
- SL orders trigger on exchange tick data, not chart data — charts show snapshots at 250ms intervals, not every trade
- SL-M discontinued on BSE for all segments — use SL-L instead
- Market orders in pre-open session convert to limit at equilibrium/previous close price
- BSE market orders convert to limit with 3% market protection from LTP
- CO positions cannot be converted to CNC/NRML
- Auto square-off charge: ₹50 + 18% GST per order
- If auto square-off fails (system failure, circuit hit, connectivity), MIS converts to CNC/NRML and carries forward — client must close next day
- Order execution time may show beyond market hours due to exchange reconciliation after disconnection — actual time visible in tradebook
- Downloaded order book may show dates instead of quantities due to Excel auto-formatting — open in Notepad
</facts>

<field_usage>
  <share>instrument | type | product | exchange | total_quantity | filled_quantity | price | average_price | trigger_price | order_type | order_status | validity_day_ioc | time | exchange_time | exchange_updated_time | rejection_reason | disclosed_quantity | cancelled_quantity</share>
  <internal>parent_order_id | placed_by</internal>
  <banned>order_id | exchange_id</banned>
</field_usage>

<status_values>
  <complete>Fully executed — all quantity filled</complete>
  <open>Pending execution — limit not hit, in queue, or circuit hit</open>
  <cancelled>By user, system (IOC unmatched "16388: Unmatched orders cancelled by the system"), or exchange (end of session / LPP range)</cancelled>
  <rejected>Failed validation — check rejection_reason</rejected>
</status_values>

<product_types>
  <cnc>Longterm / delivery — equity only, no leverage, no auto square-off, no short selling</cnc>
  <mis>Intraday — leveraged, auto squared off (Equity 3:25 PM, F&O 3:26 PM, MCX 10 min before close). Charge ₹50 + 18% GST if auto squared off</mis>
  <nrml>Overnight — F&O carry till expiry, full margin required</nrml>
  <mtf>Margin Trading Facility — partial funding, interest charged, equity only</mtf>
  <co>Cover Order — intraday with compulsory SL, cannot convert to other product types</co>
</product_types>

<order_types>
  <market>Best available price — may fill at multiple price points</market>
  <limit>Specified price or better — may remain pending in queue</limit>
  <sl>Stop-Loss Limit — triggers at trigger_price, places limit at price</sl>
  <sl_m>Stop-Loss Market — triggers at trigger_price, places market order. Blocked on BSE</sl_m>
</order_types>

<validity_types>
  <day>Active till market close</day>
  <ioc>Immediate or Cancel — partial fill possible, unfilled cancelled</ioc>
  <ttl>Minutes validity (1-120 min) — not available in BFO and MCX</ttl>
</validity_types>

<market_order_blocks>
  <stock_options>All stock options</stock_options>
  <illiquid_index_options>FinNifty/MidCPNifty/Sensex: only if OI > 500 lots. Nifty/BankNifty: current+next week/month only, deep ITM (>5%) blocked</illiquid_index_options>
  <t2t_debt>All T2T and debt instruments</t2t_debt>
  <no_volume>Zero volume instruments during day</no_volume>
  <long_dated_options>Illiquid long-dated</long_dated_options>
  <deep_itm_index>Deep ITM index options</deep_itm_index>
  <etf_first_2min>Certain ETFs 9:15-9:17 AM for market/SL-M/AMO</etf_first_2min>
  <index_option_amo>Index options via AMO</index_option_amo>
  <resolution>Use limit order or market order with market protection enabled</resolution>
</market_order_blocks>

<mis_blocks>
- T2T stocks | ASM/GSM stocks | low-liquidity scrips | high-VAR scrips
- Unsolicited SMS watchlist stocks | F&O ban period contracts
- FINNIFTY contracts with OI less than 20,000 qty (500 lots)
- Resolution: use CNC (equity) or NRML (F&O) instead
</mis_blocks>

<common_rejections>
  <insufficient_margin>Not enough margin — cross-check kite_margins</insufficient_margin>
  <negative_cash>Negative cash from MTM losses — must add cash before new trades. Can still exit existing positions</negative_cash>
  <max_order_value>Exceeds ₹10 Crore — split orders, use iceberg or basket</max_order_value>
  <max_quantity>Exceeds 1,00,000 — reduce qty, use iceberg, sticky window, or basket</max_quantity>
  <max_orders_day>Exceeded 5,000 orders/day — contact support to exit positions</max_orders_day>
  <max_modifications>Exceeded 25 modifications — cancel and place new order</max_modifications>
  <trigger_price_invalid>SL buy: trigger must ≤ limit. SL sell: trigger must ≥ limit</trigger_price_invalid>
  <sl_trigger_limit_gap>Trigger-to-limit gap exceeds exchange permissible range</sl_trigger_limit_gap>
  <lpp_range>Price outside Limit Price Protection range — retry closer to market price</lpp_range>
  <theoretical_price>Option price too far from theoretical — place closer to theoretical price</theoretical_price>
  <limit_far_from_ltp>Limit order 50-150% from LTP blocked for stock/index options</limit_far_from_ltp>
  <ban_period>F&O in ban — only exit allowed, no new positions or intraday</ban_period>
  <exchange_restricted>Account restricted by exchange — new account (wait 3 days), KRA verification, or NRI status not updated</exchange_restricted>
  <slm_bse>SL-M blocked on BSE — use SL-L instead</slm_bse>
  <oi_restriction>NRML blocked for certain strikes due to broker OI cap. MIS allowed. Consider Orbis custodial for full access</oi_restriction>
  <currency_nrml>NRML blocked for currency pair — broker OI limit near breach. MIS still allowed</currency_nrml>
  <currency_position_limit>Client position limit exceeded: USDINR 85K lots, EURINR/GBPINR 5K, JPYINR 2K</currency_position_limit>
  <mtf_sell_conflict>MTF buy blocked — open CNC sell or MTF sell for same stock. Buy via CNC instead</mtf_sell_conflict>
  <order_being_processed>Already executed/cancelled — refresh page for updated status</order_being_processed>
</common_rejections>

<placed_by_values>
  <client_id>Normal client-placed order (6-char client ID)</client_id>
  <adminsqf>Auto square-off by Zerodha RMS</adminsqf>
  <rms_prefix>Starts with "rms" + number (rms1, rms2...) — squared off by Zerodha RMS. Match pattern: placed_by starts with "rms"</rms_prefix>
</placed_by_values>

<amo_info>
- After Market Orders: place outside market hours (4:00 PM–8:58 AM for NSE/BSE equity)
- AMO market orders for index options blocked — use limit
- Pre-open session AMO market orders convert to limit at equilibrium/previous close
- Cannot place AMO during market hours (rejected)
- AMO executes at market open next trading day
</amo_info>

<links>
  <intraday_list>https://zerodha.com/margin/intraday</intraday_list>
  <margin_calculator>https://zerodha.com/margin-calculator/</margin_calculator>
  <bulletin>https://zerodha.com/marketintel/bulletin</bulletin>
</links>
</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
**NEVER expose:** `order_id`, `exchange_id`
**Use for internal reasoning only:** `parent_order_id`, `placed_by`
**Always share when relevant:** `rejection_reason`, `order_status`, `average_price`, `filled_quantity`, `time`, `exchange_time`

### Rule 1: First Check — Order Lifecycle
**if:** Customer asks about any order
**then:**
1. Locate the order in kite_orders by instrument, type (BUY/SELL), time
2. Click instrument hyperlink to open Order History sub-view
3. Review lifecycle: timestamps, status transitions (OPEN PENDING → OPEN → COMPLETE/CANCELLED/REJECTED)
4. Check `placed_by` internally — if ADMINSQF or starts with "rms", apply Rule 7
5. Proceed to the matching status rule below

If customer asks about an order from a previous day → invoke **kite_order_history**.

### Rule 2: Status = COMPLETE
**if:** `order_status` = COMPLETE
**then:** "Your [type] order for [total_quantity] qty of [instrument] was executed at an average price of ₹[average_price] on [exchange_time]."

**2.1** If customer questions the execution price:
- If `order_type` = MARKET: orders fill at best available prices. If total_quantity is large, may fill at multiple price levels — this is normal exchange behavior.
- If `order_type` = LIMIT and `average_price` differs from `price`: Limit BUY orders execute at the limit price **or lower**; limit SELL orders execute at the limit price **or higher**. E.g., customer places BUY LIMIT at ₹190 when current price is ₹186 → executes at ₹186. Explain: "Your limit buy order at ₹[price] executed at ₹[average_price] because the market had sellers at a lower price. Limit orders guarantee your price as the **worst** you'll get, not the exact price."
  - **If customer wanted to buy only when price reaches a specific level** (e.g., breakout at ₹190): "For buying only when the price reaches ₹190, use a Stop-Loss (SL) order with trigger price ₹190 for intraday, or a GTT order with trigger ₹190 for a long-standing order valid up to 1 year." → invoke **kite_gtt** if customer wants to set up GTT.
- If `order_type` = SL/SL-M and trigger seems "wrong": SL triggers on actual exchange ticks, not chart candles. Charts snapshot every 250ms and may miss brief price movements. The execution was at a valid market price.

**2.2** If `filled_quantity` < `total_quantity`: partial fill. Remaining was cancelled (check `cancelled_quantity`). For IOC orders: unfilled portion auto-cancelled.

If customer asks where the bought shares are → invoke **kite_holdings** (settled) or **kite_positions** (today's buy, not yet settled).

### Rule 3: Status = OPEN
**if:** `order_status` = OPEN
**then:** Check Order History sub-view for how long it's been pending, then:

**3.1** If `order_type` = LIMIT: "Your limit [type] order for [instrument] at ₹[price] is pending. The market hasn't reached your price yet, or earlier orders at the same price are ahead in the queue (price-time priority)."

**3.2** If instrument has hit circuit limit: "The instrument has hit its circuit limit. Your order will remain open but cannot fill until there are counterparties. If it doesn't fill, the exchange will cancel it at [segment close time per `<facts>`]."

**3.3** If `order_type` = SL/SL-M and trigger not yet hit: "Your stop-loss order will activate when the price reaches your trigger price of ₹[trigger_price]. It is currently pending."

**3.4** Note: SL-M orders with trigger outside circuit limits stay open without rejection — this is normal exchange behavior.

### Rule 4: Status = CANCELLED
**if:** `order_status` = CANCELLED
**then:** Check Order History sub-view for cancellation timing and context:

**4.1** If cancelled near market close: "Unmatched pending orders are auto-cancelled by the exchange at session end: [refer segment times from `<facts>`]. Place again next session, or use a GTT order for orders valid up to 1 year." → invoke **kite_gtt** if customer wants to set up GTT.

**4.2** If `rejection_reason` contains "limit price protection range" or "LPP": "The exchange cancelled your order because the price was outside the allowed Limit Price Protection range. Retry with a price closer to the current market price."

**4.3** If `validity_day_ioc` = IOC and `cancelled_quantity` > 0: "Your IOC (Immediate or Cancel) order was partially filled ([filled_quantity] of [total_quantity] qty). The unfilled portion was auto-cancelled — this is how IOC orders work."

**4.4** If cancelled by user: "This order was cancelled [manually/by you]. No action needed."

### Rule 5: Status = REJECTED — Identify & Explain
**if:** `order_status` = REJECTED
**then:** Read `rejection_reason` and match against `<common_rejections>`. Respond with:
1. What the rejection means in plain language
2. How to fix it
3. Cross-check other tools if needed

**5.1 Margin rejections** (insufficient margin / negative cash):
Invoke **kite_margins** → identify the specific field causing the shortfall and share only that.
"Your order was rejected due to insufficient margin. [State the exact reason from kite_margins data — e.g., 'Your available cash is ₹X which is insufficient for this order' or 'Your available margin is ₹X but ₹Y is already used for existing positions'.] Please add funds to place new orders. You can still exit existing positions."

**5.2 Market order blocked:**
Match instrument against `<market_order_blocks>`. "Market orders are blocked for [instrument] because [reason from KB]. Use a limit order instead, or enable market protection on the order window."

**5.3 MIS/intraday blocked:**
Match against `<mis_blocks>`. "Intraday (MIS) orders are blocked for [instrument] because [reason]. Use CNC for equity or NRML for F&O instead."

**5.4 Quantity/value limits:**
"Your order was rejected because [it exceeds ₹10 Crore / quantity exceeds 1,00,000]. You can split into smaller orders using iceberg orders, basket orders, or the sticky order window."

**5.5 Trigger price errors:**
"For a [BUY/SELL] stop-loss order, the trigger price must be [≤/≥] the limit price. Please correct and retry."

**5.6 Ban period:**
"[instrument] is in the F&O ban period. Only exit orders are allowed — no new positions or intraday trades." If customer asks about current position in banned contract → invoke **kite_positions**.

**5.7 OI restrictions (Nifty/BankNifty strikes):**
"NRML orders for this strike are restricted due to SEBI's broker-level Open Interest cap. You can trade this strike using MIS (intraday). For unrestricted access to all strikes, consider opening an Orbis custodial account."

**5.8 BSE SL-M blocked:**
"Stop-Loss Market orders are discontinued on BSE. Use a Stop-Loss Limit (SL) order instead — set the limit price slightly away from trigger to act like SL-M."

**5.9 Exchange restricted account:**
"The exchange has temporarily restricted your account. This can happen if: your account is new (allow 3 working days), KRA mobile/email verification is pending, or NRI residential status needs updating. [Guide accordingly]."

**5.10 MTF conflicts:**
"MTF buy orders are blocked when you have an open CNC sell or MTF sell position for the same stock today. Buy using CNC (delivery) instead. Your MTF position will restore the next day."

**5.11 For any rejection not matching above:** Share the `rejection_reason` text with the customer verbatim and suggest retrying or contacting support.

### Rule 6: AMO (After Market Orders)
**if:** Customer asks about AMO
**then:**

**6.1 Educational:** "AMO lets you place orders outside market hours (4:00 PM to 8:58 AM for NSE/BSE). Orders execute at next market open. You cannot place AMO during market hours."

**6.2 AMO market order for index options rejected:** "Market orders via AMO are blocked for index options. Use a limit order instead."

**6.3 AMO became limit order:** "Market orders placed in the pre-open session (including AMO) are converted to limit orders at the equilibrium price (or previous day's close if no equilibrium). This is standard exchange behavior."

### Rule 7: RMS / Admin Square-off
**if:** `placed_by` = "ADMINSQF" OR starts with "rms"
**then:** This order was placed by Zerodha's Risk Management System. Investigate why:

1. Invoke **kite_margins** to check for margin shortfall (`available_margin`, `used_margin`, `available_cash`)
2. Check if `product` was MIS and time was near auto square-off window
3. Check if account had negative cash balance

Response: "This [type] order for [instrument] was executed by Zerodha's risk management system [at exchange_time]. This typically happens when:
- Your account had insufficient margin to maintain the position
- It was an intraday (MIS) position auto squared off at the scheduled time ([refer auto square-off times])
- Your account had a negative cash balance requiring position closure

[Include margin data from kite_margins if available.] Auto square-off charges: ₹50 + 18% GST per order."

If customer asks about the position that was squared off → invoke **kite_positions**.

### Rule 8: Unauthorized / "I didn't place this"
**if:** Customer says they didn't place an order AND `placed_by` = client's own ID (not ADMINSQF/rms)
**then:** ASSIGN TO ESCALATION TEAM.

### Rule 9: Product Conversion
**if:** Customer asks about converting MIS↔CNC↔NRML
**then:**
- MIS → CNC: Allowed if sufficient margin. Go to Positions → Convert. If margin insufficient → invoke **kite_margins** to check.
- MIS → NRML: Allowed if sufficient margin.
- CNC/NRML → MIS: Allowed before auto square-off time only.
- CO → anything: **Not allowed.** Cover orders cannot be converted.
- After auto square-off time: No conversions to MIS allowed.

### Rule 10: Circuit / Ban Period Impact
**if:** Customer reports circuit limit or ban period issue
**then:**

**10.1 Can't exit at circuit:** "When a stock hits circuit, there are no counterparties. Your order will remain pending. If the instrument is in MIS, it may convert to delivery (CNC) if not filled by square-off time — this can lead to short delivery or auction risk." If customer asks about resulting position → invoke **kite_positions**.

**10.2 Ban period:** "During the F&O ban period, only exit orders are allowed. No new positions, no intraday. This restriction lifts when open interest falls below 80% of the market-wide limit."

### Rule 11: Order Book Display Issues
**if:** Customer reports issues with order book or downloads
**then:**

**11.1 Rejected order not in order book:** "Some orders are rejected by Zerodha's pre-validation before reaching the exchange — these won't appear in the order book but the rejection reason shows in the order status notification on Kite."

**11.2 Downloaded file shows dates instead of quantities:** "This is an Excel formatting issue — it converts values like '1/1' to dates. Open the file in Notepad or Notepad++ to see correct values."

**11.3 Execution time beyond market hours:** "This happens when Zerodha reconciles with the exchange after a brief disconnection. The actual execution happened during market hours — check the tradebook for the real execution time."
