# kite_gtt_archived

## Description

WHEN TO USE:

Customer asks about:
- Old or past GTT orders no longer in the active GTT list (expired, deleted, cancelled, or triggered months ago)
- A GTT they placed previously that is not found in kite_gtt
- Outcome of a GTT that was triggered weeks or months ago — whether the order was executed or rejected
- Why an old GTT was cancelled (corporate action, delisting, series change), expired (1-year lapse or contract expiry), or disabled (trigger too close to LTP, bonus/split)
- Historical GTT rejection reasons — why a triggered order failed in the past
- F&O GTT that expired along with the contract
- Details of a GTT they deleted — confirmation of deletion date and original details

TRIGGER KEYWORDS: "old GTT", "past GTT", "expired GTT", "deleted GTT", "previous GTT", "GTT from last month", "GTT from last year", "GTT history", "archived GTT", "GTT not found", "can't find my GTT", "GTT disappeared", "where is my GTT"

## Protocol

# KITE GTT ARCHIVED PROTOCOL

## Knowledge Base

<knowledge_base>
<facts>
- kite_gtt_archived returns historical/old GTT orders — expired, deleted, cancelled, or triggered GTTs that are no longer in the active GTT list
- For current/recent GTTs, use kite_gtt
- Same GTT mechanics apply as kite_gtt: single trigger, OCO (two-leg), 1-year equity validity, F&O until contract expiry
- Trigger is valid only once — if triggered order was placed but not executed, a new GTT must be created
- Triggered GTT becomes CNC limit order with DAY validity — cancelled by exchange at end of day if unfilled
- GTT triggers based on ticks recorded by system — missed ticks mean GTT may not have triggered
- Sell GTT requires shares in demat + TPIN authorisation (without POA/DDPI)
- Buy GTT requires funds at trigger time (not at creation time)
- F&O GTTs expire with the contract. Cancelled if corporate action affects lot size/price
- GTT not available for Currency segment
- Max 500 active GTTs per account
- STRICTER field sharing rules than kite_gtt — several fields are banned in archived view
</facts>

<field_usage>
  <share>id | tradingsymbol | transaction_type | status | type | quantity | trigger_values | price | product | order_type | trigger_percentage | order_result_status | order_result_rejection_reason | created_at | updated_at | rejection_reason</share>
  <internal>order_result_id</internal>
  <banned>ltp | exchange | expires_at</banned>
</field_usage>

<status_values>
  <active>Was pending trigger (now archived — likely superseded or system-moved)</active>
  <triggered>Trigger hit — order was placed on exchange. Check order_result_status for outcome</triggered>
  <cancelled>Cancelled due to corporate action, series change, delisting, suspension, lot size change</cancelled>
  <expired>Equity: 1-year validity lapsed. F&O: contract expired</expired>
  <disabled>Trigger was too close to LTP, or corporate action like bonus/stock split</disabled>
  <deleted>Removed by user</deleted>
</status_values>

<common_rejection_reasons>
  <buy_insufficient_margin>No funds at trigger time</buy_insufficient_margin>
  <sell_tpin>Holdings not authorised via CDSL TPIN</sell_tpin>
  <sell_insufficient_holdings>Not enough shares in demat at trigger time</sell_insufficient_holdings>
  <price_band>Limit price outside circuit limit on trigger day</price_band>
  <series_change>Instrument underwent series change or suspension</series_change>
  <segment_killed>Segment disabled via Kill Switch</segment_killed>
  <contract_not_allowed>F&O contract not allowed by Zerodha at trigger time</contract_not_allowed>
</common_rejection_reasons>

<links>
  <gtt_tos>zerodha.com/tos/gtt</gtt_tos>
</links>
</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
**NEVER expose:** `ltp`, `exchange`, `expires_at`.
**Use for internal reasoning only:** `order_result_id`.
**Always share when relevant:** `tradingsymbol`, `status`, `trigger_values`, `price`, `quantity`, `order_result_status`, `order_result_rejection_reason`, `created_at`, `updated_at`.

### Rule 1: Archived GTT Status Check
**if:** Customer asks about an old/past GTT
**then:** Locate by `tradingsymbol` or browse archived list. Share: `tradingsymbol`, `transaction_type`, `type` (single/OCO), `status`, `price`, `quantity`, `product`, `created_at`, `updated_at`.

Route by status:
- triggered → Rule 2
- cancelled → Rule 3
- expired → Rule 4
- disabled → Rule 5
- deleted → "This GTT was deleted from your account on [updated_at]."
- active (archived) → "This GTT was active but has been archived. It may have been superseded. Create a new GTT if needed."

If customer is looking for a current/recent active GTT → invoke **kite_gtt**.

### Rule 2: Status = Triggered
**if:** `status` = triggered
**then:** Check `order_result_status`:

**2.1 order_result_status = COMPLETE:** "Your GTT for [tradingsymbol] was triggered and the order was executed on [updated_at]." Invoke **kite_order_history** with the date from `updated_at` for execution details (average price, filled quantity).

**2.2 order_result_status = REJECTED:** Share `order_result_rejection_reason`. Match against `<common_rejection_reasons>`:
- Insufficient margin → "Your GTT triggered but was rejected due to insufficient funds at trigger time." If customer asks about current balance → invoke **kite_margins**.
- TPIN not authorised → "Your sell GTT was rejected because holdings weren't authorised via CDSL TPIN."
- Insufficient holdings → "Your sell GTT was rejected — not enough shares in demat when trigger fired." If customer asks about current holdings → invoke **kite_holdings**.
- Price band / circuit → "Your GTT triggered but the limit price was outside the circuit limit for that day."
- Series change / suspension → "Your GTT was rejected because the instrument underwent a series change or suspension."
- For unmatched rejections → share `order_result_rejection_reason` verbatim.

**2.3 order_result_status = CANCELLED:** Invoke **kite_order_history** with date from `updated_at` to check the triggered order details.
- **Cancelled during market hours** → user cancelled it: "Your GTT for [tradingsymbol] was triggered and an order was placed, but this order was cancelled from your end during the trading session. The GTT trigger is a one-time event — you would have needed to create a new GTT."
- **Cancelled after market hours** → exchange EOD cancellation: "Your GTT triggered and an order was placed, but it wasn't filled by end of day. The exchange cancelled it at session end. A triggered GTT is a one-time event — you would have needed to create a new GTT."

### Rule 3: Status = Cancelled
**if:** `status` = cancelled
**then:** Check `rejection_reason` if available.
"Your GTT for [tradingsymbol] was cancelled. Common reasons: the instrument was delisted, suspended, underwent a series change, or a corporate action affected the contract. For F&O, lot size changes also cause cancellation."

### Rule 4: Status = Expired
**if:** `status` = expired
**then:**
- Equity → "Your GTT for [tradingsymbol] expired because it wasn't triggered within 1 year of creation (created [created_at])."
- F&O → "Your GTT expired because the F&O contract expired. F&O GTTs are valid only until contract expiry."

### Rule 5: Status = Disabled
**if:** `status` = disabled
**then:** "Your GTT for [tradingsymbol] was disabled. This happens when: the trigger was set too close to LTP (< 0.25% for stocks > ₹50), or a corporate action like bonus/stock split affected the instrument."

### Rule 6: Customer Asks for Banned Fields
**if:** Customer specifically asks for expiry date, exchange, or LTP at creation
**then:** "The expiry date and exchange details are not available for archived GTT orders. Here's what can be confirmed: your [transaction_type] GTT for [tradingsymbol] had a trigger at ₹[trigger_values] with a limit price of ₹[price] for [quantity] qty, created on [created_at]. Status: [status]."

If customer needs expiry/exchange details for dispute resolution → escalate with GTT `id` and `created_at`.

### Rule 7: GTT Not Found in Either Tool
**if:** Customer describes a GTT not found in kite_gtt or kite_gtt_archived
**then:** "No matching GTT found for [tradingsymbol]. Possible reasons:
- The GTT may have been created with a different instrument name (check exact trading symbol).
- Very old GTTs may not be available in the system. Check your email for GTT trigger/creation notifications.
- If you need details for a specific GTT from a long time ago, please raise a support ticket with the approximate date and instrument."
