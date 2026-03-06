# kite_gtt

## Description

WHEN TO USE:

Customer asks about:
- Active GTT order details — status, trigger price, quantity, limit price, product type
- GTT triggered — what price it triggered at, when, and the order outcome
- GTT triggered but order was rejected or not executed (insufficient margin, TPIN, holdings, price band)
- GTT not triggered even though the price was reached (tick not captured by system)
- GTT disabled, cancelled, or expired — reason and what to do next
- GTT trigger price vs execution price or email price mismatch (gap up/down scenarios)
- GTT email notification showing a different price than the set trigger
- Triggered GTT order not visible in the order book the next day
- Sell GTT rejection — TPIN not authorised, insufficient holdings, series change, segment killed
- Buy GTT rejection — insufficient margin, trigger too close to LTP, price band violation
- GTT OCO (two-leg) behavior — which leg triggered, other leg auto-cancelled
- GTT for F&O contracts — validity until contract expiry, physical delivery risk, hedge leg impact
- GTT creation errors — trigger too close to LTP (0.25% minimum for stocks > ₹50, 9 paise for < ₹50), no LTP for illiquid stocks
- Maximum active GTTs (500 per account) or GTT limits
- GTT stoploss prompt when buying index options

TRIGGER KEYWORDS: "GTT", "good till triggered", "trigger order", "GTT triggered", "GTT not triggered", "GTT rejected", "GTT expired", "GTT cancelled", "GTT disabled", "GTT deleted", "OCO", "two-leg", "single trigger", "GTT stoploss", "GTT target", "GTT email", "GTT validity", "GTT order status", "triggered but not executed", "GTT creation error", "GTT limit", "500 GTT"

## Protocol

# KITE GTT PROTOCOL

## Knowledge Base

<knowledge_base>
<facts>
- GTT = Good Till Triggered — order stays active until trigger condition is met or validity expires
- Validity: Equity GTT = 1 year from creation. F&O GTT = until contract expiry
- Trigger is valid only once. If triggered order is placed but not executed, customer must create a new GTT
- Triggered GTT becomes a CNC limit order with DAY validity — cancelled by exchange at end of day if unfilled. Not visible from next day
- Max 500 active GTTs per account
- GTT is free — no additional charges
- Notifications: email + Kite push notification on trigger and order placement
- Single trigger: one trigger price → one order placed when LTP hits/breaches trigger
- OCO (two-leg): stoploss + target triggers. When one triggers, other is cancelled
- Buy GTT OCO available only for F&O contracts. OCO uses NRML only for index F&O
- GTT triggers based on ticks recorded by system — if tick not captured, GTT may not trigger even if price briefly touched
- GTT email may show price different from trigger price — this is the actual LTP at trigger moment (gap up/down can cause mismatch)
- Trigger minimum distance: stock price > ₹50 → trigger must be 0.25% away from LTP. Stock price < ₹50 → trigger at least 9 paise away
- Sell GTT executes only if shares are in demat and order fills on exchange
- GTT closing one leg of hedged position → margin requirement increases → Zerodha may square off remaining position
- F&O GTTs cancelled when lot size changes or corporate action affects lot size/price
- GTT not available for Currency segment
</facts>

<field_usage>
  <share>id | tradingsymbol | transaction_type | status | type | quantity | trigger_values | price | product | order_type | trigger_percentage | order_result_status | order_result_rejection_reason | created_at | updated_at | rejection_reason</share>
  <internal>order_result_id</internal>
  <banned>ltp | exchange | expires_at</banned>
</field_usage>

<status_values>
  <active>Pending trigger — GTT is live and monitoring price</active>
  <triggered>Trigger hit — order placed on exchange. Check order_result_status for outcome</triggered>
  <cancelled>Cancelled due to corporate action (series change, delisting, suspension, extraordinary dividend, rights issue, consolidation, capital reduction), or lot size change for index F&O</cancelled>
  <expired>Equity: 1 year validity lapsed. F&O: contract expired</expired>
  <disabled>GTT trigger set too close to LTP (< 0.25% for stocks > ₹50), or corporate action like bonus/stock split affected instrument</disabled>
  <deleted>Removed by user</deleted>
</status_values>

<buy_gtt_rejections>
  <insufficient_margin>No funds at trigger time — GTT can be created without funds, but needs funds when triggered</insufficient_margin>
  <trigger_too_close>Trigger < 0.25% from LTP (for stocks > ₹50) or < 9 paise (for stocks < ₹50)</trigger_too_close>
  <price_band>Limit price outside exchange circuit limit on trigger day</price_band>
  <contract_not_allowed>F&O contract not allowed for trading by Zerodha at trigger time</contract_not_allowed>
  <segment_killed>Segment disabled via Kill Switch at trigger time</segment_killed>
</buy_gtt_rejections>

<sell_gtt_rejections>
  <tpin_not_authorised>Holdings not authorised via CDSL TPIN — must authorise daily after 7 AM if no POA/DDPI</tpin_not_authorised>
  <insufficient_holdings>Not enough shares in demat at trigger time</insufficient_holdings>
  <series_change>Instrument underwent series change or suspension</series_change>
  <segment_killed>Segment disabled via Kill Switch</segment_killed>
</sell_gtt_rejections>

<fno_gtt_rules>
  <validity>Valid until contract expiry — not 1 year</validity>
  <physical_delivery>Stock F&O GTT may lead to physical delivery obligation if contract expires ITM</physical_delivery>
  <hedge_risk>GTT closing one leg of hedge → margin increases → Zerodha may square off</hedge_risk>
  <corporate_action>Equity F&O GTTs cancelled if corporate action affects lot size/price</corporate_action>
  <index_lot_change>Index F&O GTTs cancelled when lot size changes</index_lot_change>
  <not_available>Currency segment — GTT not available</not_available>
  <oco_restriction>Buy OCO available only for F&O. NRML only for index F&O OCO</oco_restriction>
</fno_gtt_rules>

<links>
  <gtt_tos>zerodha.com/tos/gtt</gtt_tos>
  <generate_tpin>support.zerodha.com — How to generate CDSL TPIN</generate_tpin>
  <activate_ddpi>support.zerodha.com — How to activate DDPI</activate_ddpi>
</links>
</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
**NEVER expose:** `ltp` (LTP at GTT creation time), `exchange`, `expires_at`.
**Use for internal reasoning only:** `order_result_id`.
**Always share when relevant:** `trigger_values`, `price`, `order_result_status`, `order_result_rejection_reason`, `status`, `created_at`.

### Rule 1: GTT Status Check
**if:** Customer asks about a specific GTT
**then:** Locate by `tradingsymbol`. Share: `tradingsymbol`, `transaction_type`, `type` (single/OCO), `status`, `trigger_values`, `price`, `quantity`, `product`, `created_at`.

Route by status:
- active → Rule 2
- triggered → Rule 3
- cancelled → Rule 5
- expired → Rule 6
- disabled → Rule 7
- deleted → "This GTT was deleted from your account [on updated_at]."

If customer asks about an old/expired/deleted GTT not found here → invoke **kite_gtt_archived**.

### Rule 2: Status = Active
**if:** `status` = active
**then:** "Your [transaction_type] GTT for [tradingsymbol] is active. Trigger price: ₹[trigger_values], limit price: ₹[price], quantity: [quantity]. Equity GTTs are valid for 1 year from creation; F&O GTTs until contract expiry."

**2.1 Customer asks when it will trigger:** "Your GTT will trigger when the LTP of [tradingsymbol] hits or breaches ₹[trigger_values]. Once triggered, a [order_type] order at ₹[price] will be placed on the exchange."

**2.2 OCO active:** "Your OCO GTT has two triggers — stoploss at ₹[lower_trigger] and target at ₹[upper_trigger]. When one triggers, the other is automatically cancelled."

### Rule 3: Status = Triggered — Check Order Result
**if:** `status` = triggered
**then:** Check `order_result_status`:

**3.1 order_result_status = COMPLETE:** "Your GTT for [tradingsymbol] was triggered and the order was executed." If triggered today → invoke **kite_orders** for execution details (average price, filled quantity, exchange time). If triggered on a past date → invoke **kite_order_history**.

**3.2 order_result_status = REJECTED:** Share `order_result_rejection_reason`. Match against rejection reasons:
- Insufficient margin → "Your GTT triggered but was rejected due to insufficient funds. GTTs can be created without funds, but funds must be available when the trigger fires." Invoke **kite_margins** to cross-check current balance.
- Holdings not authorised (TPIN) → "Your sell GTT was rejected because holdings were not authorised via CDSL TPIN. Without POA/DDPI, you must authorise daily after 7 AM. Consider activating DDPI to avoid this."
- Insufficient holdings → "Your sell GTT was rejected because you didn't have enough shares in your demat account when the trigger fired." Invoke **kite_holdings** to check current holdings.
- Price band / circuit → "Your GTT triggered but the limit price was outside the exchange's circuit limit for the day. The order was rejected."
- Series change / suspension → "Your GTT was rejected because the instrument underwent a series change or was suspended."
- Segment killed → "Your GTT was rejected because you had disabled this segment using Kill Switch."

**3.3 order_result_status = CANCELLED:** Invoke **kite_orders** to check the triggered order details.
- **Cancelled during market hours** → user cancelled it: "Your GTT for [tradingsymbol] was triggered and a [order_type] order was placed on the exchange. However, this order was cancelled from your end during the trading session. The GTT trigger is a one-time event — you'll need to create a new GTT if you still want this order."
- **Cancelled after market hours** → exchange EOD cancellation: "Your GTT triggered and an order was placed, but it wasn't filled by end of day. Triggered GTT orders become limit orders with DAY validity — if unfilled, the exchange cancels them at session end. You need to create a new GTT."

**3.4 Triggered GTT not visible in order book:** "Once triggered, the GTT order is a regular limit order with DAY validity. If it wasn't filled, the exchange cancelled it at end of day. From the next day, it won't appear in the order book. Check your email for the trigger and order details."

### Rule 4: GTT Not Triggered — Price Was Reached
**if:** Customer says price hit the trigger but GTT didn't fire
**then:** "GTT triggers based on ticks recorded by the system. Hundreds of transactions occur per second on the exchange, and each is represented by a tick. If the system didn't capture the tick at your trigger price of ₹[trigger_values], the GTT may not trigger. It will remain active until the price reaches the trigger again.

Check if:
- The price briefly touched the trigger and bounced — the tick may not have been recorded.
- The GTT was modified — check `updated_at` to confirm the latest trigger value.
- The GTT was disabled due to a corporate action or trigger being too close to LTP."

### Rule 5: Status = Cancelled
**if:** `status` = cancelled
**then:** Check `rejection_reason` if available. Common causes:
- "Your GTT was cancelled because [instrument] was [delisted/suspended/underwent a series change/category change]."
- "Your GTT for the F&O contract was cancelled due to a [corporate action affecting lot size/price / lot size change for index contracts]."
- "Extraordinary corporate actions (dividends above 2%, rights issue, consolidation, capital reduction) also cause GTT cancellation."
- "You'll need to create a new GTT."

### Rule 6: Status = Expired
**if:** `status` = expired
**then:**
- If equity → "Your GTT expired because it wasn't triggered within 1 year of creation (created on [created_at]). Create a new GTT if needed."
- If F&O → "Your GTT expired because the F&O contract expired. GTTs for derivatives are valid only until contract expiry."

### Rule 7: Status = Disabled
**if:** `status` = disabled
**then:** "Your GTT was disabled because:
- The trigger price was set too close to LTP (less than 0.25% for stocks above ₹50, or less than 9 paise for stocks below ₹50) after validation, OR
- The instrument underwent a corporate action like a bonus issue or stock split.

You'll need to create a new GTT with a valid trigger price."

### Rule 8: GTT Email Price Mismatch
**if:** Customer asks why the price in the GTT email differs from the trigger price
**then:** "The price in the email is the actual LTP at the moment the GTT triggered — not your trigger price. Due to market volatility or gaps (opening gap up/down), the LTP at trigger time may be higher or lower than your set trigger price. Example: if you set a sell trigger at ₹95 but the stock opened at ₹90 (gap down), the trigger fires at ₹90 and the email shows ₹90."

### Rule 9: F&O GTT Specifics
**if:** Customer asks about GTT for F&O contracts
**then:**
- "F&O GTTs are valid only until contract expiry — not 1 year."
- "Stock F&O: if your GTT leads to a position that expires ITM, you may have a physical delivery obligation."
- "If your GTT closes one leg of a hedged position, the margin for the remaining leg increases. Zerodha may square off the position if margin is insufficient." Invoke **kite_margins** to check available margin. If customer asks about the affected position → invoke **kite_positions**.
- "Corporate actions affecting lot size/price will cancel equity F&O GTTs. Lot size changes cancel index F&O GTTs."
- "GTT is not available for the Currency segment."
- "Buy OCO is available only for F&O. Index F&O OCO uses NRML only."

### Rule 10: GTT Creation Errors
**if:** Customer can't create a GTT
**then:**
- Trigger too close to LTP → "For stocks above ₹50, the trigger must be at least 0.25% away from the current market price. For stocks below ₹50, the trigger must be at least 9 paise away."
- No LTP (illiquid stock) → "GTTs require an LTP to validate the trigger. If the instrument has no LTP due to illiquidity, GTT creation is not possible."
- Max GTTs reached → "You can have a maximum of 500 active GTTs. Delete existing GTTs to create new ones."

### Rule 11: GTT Stoploss Prompt (Index Options)
**if:** Customer asks about the "GTT stoploss is invalid" nudge when buying index options
**then:** "This prompt encourages setting a stoploss when buying options to manage risk. You can proceed without setting one, but Zerodha recommends a GTT stoploss (5–10% is a reasonable starting point). Remember to cancel open GTT stoploss orders when you directly exit the position to avoid unintended positions."
