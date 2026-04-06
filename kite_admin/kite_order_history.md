# kite_order_history

## Description

WHEN TO USE:

When clients:
- Ask about orders placed on a past date or date range (not today's live orders)
- Ask about order rejection reason from a previous day
- Ask about execution details for historical orders (average price, filled quantity, exchange timestamp)
- Ask about a specific instrument's order history (e.g., "what happened with my INFY order last week?")
- Ask whether an order was placed by them or auto-squared off by RMS (ADMINSQF/rms)
- Ask about auto square-off history (when it happened, why, at what price, and the charge)
- Report auto square-off failure (MIS position carried forward as CNC/NRML)
- Ask about SIP order execution or failures from past dates (wrong product type, insufficient margin)
- Ask about ATO (Alert Trigger Order) execution history and rejections (freeze quantity limit)
- Ask about GTT-triggered order results (whether the triggered order was executed or rejected)
- Ask about basket order execution history (which orders succeeded or failed)
- Ask about AMO (After Market Order) execution from past dates (conversion to limit, pre-open behavior)
- Ask about iceberg order execution (parent-child order relationship)
- Want to verify order details from a past trading session (price, quantity, time, status)
- Dispute an order or trade from a previous day
- Ask whether a trade was intraday or delivery (using product type and buy/sell pairing)
- Ask about F&O buy average calculation (FIFO method across product types)
- Ask why equity buy average unchanged after same-day sell and rebuy (intraday treatment, except T2T)

TRIGGER KEYWORDS: "order history", "past order", "previous order", "old order", "trade history", "order on [date]", "last week order", "order rejected yesterday", "why was my order", "SIP order history", "ATO order", "basket order history", "GTT triggered order", "auto squared off", "squared off order", "execution time", "filled quantity", "rejection reason", "order status", "AMO order history", "iceberg order history", "intraday or delivery", "buy average FIFO", "who placed this order"

## Protocol

# KITE ORDER HISTORY PROTOCOL 

---

## Section A: Reference Data

---

### A1 — Tool Purpose & Fundamentals

This tool returns **orders for a date range** (from_date to to_date). For today's live orders, use `kite_orders`.

Orders follow price-time priority: first come, first served at same price.

Zerodha pre-validates orders — some rejections won't appear in order book (shown in status notification only).

Execution time beyond market hours = exchange reconciliation after connectivity issues, not actual execution beyond hours.

**Input:** Client ID + from_date + to_date.

---

### A2 — Field Usage Rules

**Shareable fields:**

`client_id` | `created_at` | `instrument` | `type` | `product` | `exchange` | `total_quantity` | `filled_quantity` | `price` | `average_price` | `trigger_price` | `order_type` | `order_status` | `order_timestamp` | `exchange_timestamp` | `order_timestamp_date` | `rejection_reason` | `disclosed_quantity` | `cancelled_quantity` | `basket` | `sip` | `ato` | `gttp_sl_percentage` | `gttp_trgt_percentage`

**Internal-only fields** (use for reasoning; communicate outcomes in plain language):

`placed_by` | `variety` | `gtt` | `app_id`

**Client-facing terminology:**

| Internal Term | Client-Facing Alternative |
|---|---|
| `placed_by` = ADMINSQF or starts with "rms" | "executed by Zerodha's risk management system" |
| `placed_by` = client ID | (normal client order — do not mention the field) |
| `gtt` field with trigger ID | "this order was triggered by your GTT" (cross-verify via kite_gtt / kite_gtt_archived) |
| `app_id` = "GTT Orders" | (secondary GTT confirmation — do not expose) |
| `variety` | (use to identify AMO, CO, iceberg internally — do not expose field name) |

**Additional internal-only fields** (not for client communication):

`validity` | `parent_order_id` | `order_id` | `exchange_id` | `validity_ttl` | `silo` | `basket_id` | `tags` | `gttp` | `order_result_id`

---

### A3 — Order Statuses

| Status | Meaning |
|---|---|
| Complete | Fully executed — all quantity filled |
| Open | Pending execution — limit not hit, in queue, or circuit hit |
| Cancelled | By user, exchange end-of-session, IOC unfilled, or LPP range violation |
| Rejected | Failed validation — check `rejection_reason` |

---

### A4 — Product Types

| Product | Description |
|---|---|
| CNC | Delivery — equity only, no leverage, no auto square-off |
| MIS | Intraday — leveraged, auto squared off |
| NRML | Overnight — F&O carry till expiry, full margin |
| MTF | Margin Trading Facility — delivery with leverage |
| CO | Cover Order — intraday with compulsory SL, cannot convert |

---

### A5 — Order Limits

| Limit | Value |
|---|---|
| Max orders per day | 5,000 across all segments |
| Max orders per minute | 400 |
| Max modifications per order | 25 |
| Max order value (equity) | ₹10 Crore |
| Max quantity (equity) | 1,00,000 |

---

### A6 — Auto Square-Off

| Segment | Time |
|---|---|
| Equity | 3:25 PM |
| Equity F&O | 3:26 PM |
| MCX | 10 min before market close |

**Charge:** ₹50 + 18% GST per order. **Failure:** MIS converts to CNC/NRML, client must close next day. CO positions cannot be converted.

---

### A7 — Unmatched Order Cancellation Times

| Segment | Auto-Cancel Time |
|---|---|
| Equity | 4:00 PM |
| Currency | 5:00 PM |
| MCX | Market close (Nov–Mar 11:55 PM, Mar–Nov 11:30 PM — DST shift) |

---

### A8 — `placed_by` Values

| Value | Meaning |
|---|---|
| Client ID (6-char) | Normal client-placed order |
| ADMINSQF | Auto square-off by Zerodha RMS |
| Starts with "rms" + number | Squared off by Zerodha RMS |

---

### A9 — Common Rejections

| Rejection | Meaning | Resolution |
|---|---|---|
| Insufficient margin | Not enough margin | Cross-check `kite_margins`. Add funds. Can still exit. |
| Negative cash | MTM losses | Add cash. Can still exit existing positions. |
| Max order value | Exceeds ₹10 Crore | Split, use iceberg or basket. |
| Max quantity | Exceeds 1,00,000 | Reduce qty, use iceberg or basket. |
| Trigger price invalid | SL buy: trigger ≤ limit. SL sell: trigger ≥ limit. | Correct and retry. |
| SL trigger-limit gap | Exceeds exchange range | Narrow the gap. |
| LPP range | Price outside protection range | Retry closer to market price. |
| Theoretical price | Option too far from theoretical | Place closer to theoretical. |
| Ban period | F&O in ban | Exit only, no new positions/intraday. |
| Exchange restricted | Account restricted | New account (3 days), KRA pending, NRI status. |
| SL-M on BSE | Discontinued | Use SL-L instead. |
| OI restriction | Broker OI cap (NRML blocked) | MIS allowed. Consider Orbis custodial. |
| Currency position limit | Client limit exceeded | USDINR 85K, EURINR/GBPINR 5K, JPYINR 2K. |
| MTF sell conflict | Open CNC/MTF sell for same stock | Buy via CNC instead. |
| Market order blocked | Stock options, T2T, debt, illiquid/deep ITM, zero-volume | Use limit order. |
| MIS blocked | T2T, ASM/GSM, low-liquidity, high-VAR, ban period | Use CNC or NRML. |

---

### A10 — AMO Rules

| Rule | Detail |
|---|---|
| NSE/BSE equity window | 4:00 PM – 8:58 AM |
| F&O window | 3:45 PM – 9:10 AM |
| MCX window | 5:00 PM – 9:10 AM |
| AMO market for index options | Blocked — use limit |
| Pre-open AMO market | Converts to limit at equilibrium/previous close |
| Sell AMO without DDPI/POA | T-day stocks: only after 6:30 AM next day. Delivered stocks: after 5 PM. |

---

### A11 — Special Order Types

| Field | Value | Meaning |
|---|---|---|
| `sip` | "Yes" | SIP order — must use Regular CNC + market/limit |
| `ato` | "Yes" | ATO (alert-triggered) — order slicing not supported, qty within freeze limit |
| `basket` | basket name | Part of a basket — each order validated independently |
| `gtt` | trigger ID | GTT-triggered order — cross-verify via kite_gtt / kite_gtt_archived |
| `variety` = "iceberg" | — | Iceberg — `parent_order_id` links child orders to parent |

---

### A12 — Intraday Identification Logic

| Pattern | Classification |
|---|---|
| MIS or CO product | Intraday trade |
| CNC with only BUY (no same-day SELL) | Delivery / long-term |
| CNC with BUY + SELL same instrument same qty same day | Intraday round-trip (speculative, not delivery) |
| NRML | Overnight F&O position |
| MTF | Margin Trading Facility (delivery with leverage) |
| BUY (MIS) + SELL by ADMINSQF/rms | Intraday auto squared off |

**Exception:** T2T stocks — same-day buy+sell treated as delivery, buy average updates to latest buy price.

**F&O buy average:** FIFO across product types (MIS + NRML combined). Earliest buy matches first sell.

**Equity CNC sell + rebuy same day:** Original buy average unchanged. Same-day round-trip = speculative per income tax rules.

---

### A13 — Links

| Topic | URL |
|---|---|
| Margin calculator | zerodha.com/margin-calculator |
| Market intelligence bulletin | zerodha.com/marketintel/bulletin |
| SEBI retail algo compliance | https://kite.trade/forum/discussion/15912/preparing-to-comply-with-sebis-retail-algo-rules-static-ip-ratelimits-order-types#latest |

---

### A14 — Escalation Data Template

When escalating, always include: **client ID, instrument, date, order details, and specific issue.**

---

### A15 — Response Templates

**R1 — Complete (basic):**
"Your [type] order for [total_quantity] qty of [instrument] was executed at ₹[average_price] on [exchange_timestamp]."

**R2 — Market order multi-level fill:**
"Market orders fill at best available prices. Large quantities may fill across multiple price levels — average price reflects the weighted fill."

**R3 — Limit better price:**
"Limit buy orders can execute below your limit price; limit sell orders above. Your limit at ₹[price] executed at ₹[average_price] because a better price was available."

**R4 — Breakout → use SL or GTT:**
"Use a Stop-Loss (SL) order with trigger price for intraday, or GTT for a long-standing order valid up to 1 year."

**R5 — SL trigger vs chart:**
"SL orders trigger on actual exchange ticks, not chart candles. Charts snapshot every 250ms and may miss brief price movements. The execution at ₹[average_price] was at a valid market price."

**R6 — Partial fill:**
"[filled_quantity] of [total_quantity] filled at ₹[average_price]. Remaining [cancelled_quantity] was cancelled. For IOC orders, unfilled portions are auto-cancelled."

**R7 — RMS square-off:**
"This [type] order for [instrument] was executed by Zerodha's risk management system on [exchange_timestamp]. This typically happens when:
- Your account had insufficient margin to maintain the position
- It was an intraday (MIS) position auto squared off at the scheduled time (Equity 3:25 PM, F&O 3:26 PM, MCX 10 min before close)
- Your account had a negative cash balance requiring position closure

Auto square-off charge: ₹50 + 18% GST per order."

**R8 — Auto square-off failed (carried forward):**
"Auto square-off may fail due to circuit limits, system failures, or connectivity issues. When this happens, MIS converts to CNC (equity) or NRML (F&O) and carries forward. You must close the position on the next trading day."

**R9 — Open in history (should be cancelled):**
"Unmatched pending orders are auto-cancelled by the exchange at session end."

**R10 — Cancelled at session end:**
"Unmatched pending orders are auto-cancelled by the exchange at session end. Place again next session, or use GTT for orders valid up to 1 year."

**R11 — LPP cancellation:**
"Exchange cancelled your order — price was outside the allowed range. Retry closer to market price."

**R12 — Partial fill + cancelled remainder:**
"Partially filled: [filled_quantity] of [total_quantity] executed at ₹[average_price]. Remaining [cancelled_quantity] was cancelled."

**R13 — IOC auto-cancel:**
"IOC orders auto-cancel any unfilled portion immediately."

**R14 — Unauthorized (client ID placed_by):**
"This order appears to have been placed from your account. For security, we're escalating this for investigation. Please also check if any third-party apps have Kite Connect API access, and consider blocking your account if you suspect unauthorized activity."

**R15 — SIP order — no order found:**
"SIP may not have triggered. Check that: basket is linked to SIP, product type is Regular CNC, order type is market or limit. Also check your registered email — Zerodha sends a SIP summary email with rejection reasons if the order failed."

**R16 — ATO rejection:**
"ATO orders place automatically when your Kite alert triggers. Order slicing is not available — quantity must be within the exchange freeze limit."

**R17 — Basket order:**
"This order was part of basket '[basket]'. Basket orders execute individually — each is subject to its own margin and exchange validation. Some may succeed while others fail."

**R18 — Execution time beyond market hours:**
"The displayed time reflects exchange reconciliation after a connectivity disruption. Your order was executed within market hours. Check the tradebook for actual execution time."

**R19 — Multiple orders for same instrument:**
"[N] orders found for [instrument] on [date]."

**R20 — No orders found:**
"No orders found for [instrument] between [from_date] and [to_date]. Please verify the instrument name, exchange, and date range. Orders rejected pre-exchange (before reaching exchange) may not appear in history."

**R21 — MIS sell instead of CNC (product mismatch):**
"Your sell order for [instrument] was placed under MIS (intraday) instead of CNC (delivery). An MIS sell does not exit your CNC delivery holdings — it creates a fresh short intraday position. Your CNC holdings of [instrument] remain intact. The MIS short position was auto-squared off at 3:25 PM by buying back the shares, so you still hold your original shares. To sell delivery holdings, use CNC as the product type when placing the sell order."

**R22 — API rate limit (429 response):**
"Orders placed via third-party API applications are subject to a rate limit of 10 orders per second as per SEBI's retail algo regulations. Your order received a 429 response because it exceeded this limit. To place more than 10 orders per second, the trading strategy must be registered with the stock exchange. For details: [SEBI retail algo compliance](https://kite.trade/forum/discussion/15912/preparing-to-comply-with-sebis-retail-algo-rules-static-ip-ratelimits-order-types#latest)"

**R23 — API market protection rejection:**
"Orders placed via third-party API applications require market protection to be enabled. Orders with market protection set to 0 are rejected — this includes SL-M orders. This is mandated by the exchanges for all algo orders. Use a limit order or set an appropriate market protection value. For details: [SEBI retail algo compliance](https://kite.trade/forum/discussion/15912/preparing-to-comply-with-sebis-retail-algo-rules-static-ip-ratelimits-order-types#latest)"

**R24 — API MCX IOC rejection:**
"MCX does not support IOC (Immediate-or-Cancel) orders in the algo segment. Orders placed via third-party API applications on MCX with IOC validity will be rejected. Use DAY validity instead."

---

## Section B: Decision Flow

---

### Preflight (run on every query)

```
1. Locate order(s) by instrument + date range.
2. Check placed_by internally:
   └─ ADMINSQF or starts with "rms" → route to Rule 4 (RMS square-off).
3. Check gtt internally:
   └─ If GTT trigger ID present → cross-verify via kite_gtt / kite_gtt_archived.
      Scope investigation to GTT trigger date only — subsequent orders
      are independent client actions.
4. If customer asks about today's live orders → invoke kite_orders.
5. Check app_id internally:
   └─ If app_id is a numerical value (not "Kite Web", "Kite iOS",
      or other named Kite apps) → order was placed via a third-party
      API application. If query relates to rejection or rate limiting,
      route to Rule 16.
```

### Route

```
Intent / Condition                                          → Rule
──────────────────────────────────────────────────────────────────────
Order status check (complete/open/cancelled/rejected)       → Rule 1
Order complete — execution details / price questions        → Rule 2
Order rejected                                              → Rule 3
RMS / admin square-off                                      → Rule 4
Order open in history (unusual)                             → Rule 5
Order cancelled                                             → Rule 6
"I didn't place this order"                                 → Rule 7
SIP order investigation                                     → Rule 8
ATO order investigation                                     → Rule 9
AMO order behavior                                          → Rule 10
Basket order investigation                                  → Rule 11
Execution time beyond market hours                          → Rule 12
F&O buy average / intraday identification                   → Rule 13
Multiple orders for same instrument                         → Rule 14
No matching orders found                                    → Rule 15
API order rejection or rate limiting (app_id = numerical)   → Rule 16
```

### Scope

- Address the client's query about historical orders — status, execution, rejections, special order types, and buy average.
- Use **A2** field rules and client-facing terminology in all client communication.
- For today's live orders, redirect to `kite_orders`.

### Fallback

If no route matches, investigate using Section A reference data. If no root cause is found, escalate per **A14**.

---

## Section C: Rules

---

### Rule 1 — Order Status Check

1. Locate by instrument + date.
2. Share: instrument, type, order_type, order_status, total_quantity, filled_quantity, average_price (if COMPLETE), exchange_timestamp.
3. Check `placed_by` internally → ADMINSQF/rms → Rule 4.
4. Check `gtt` internally → GTT ID present → cross-verify via `kite_gtt` / `kite_gtt_archived`. Scope to trigger date only.
5. Check `app_id` internally → numerical value → if rejection or rate limit query, route to Rule 16.
6. Route by status: COMPLETE → Rule 2, REJECTED → Rule 3, OPEN → Rule 5, CANCELLED → Rule 6.

---

### Rule 2 — Order Complete

1. Respond per **A15-R1**.
2. Price discrepancy:
   a. Market order → **A15-R2**.
   b. Limit at better price → **A15-R3**.
   c. Client wanted breakout → **A15-R4**. Invoke `kite_gtt` if interested.
   d. SL trigger dispute → **A15-R5**.
3. Partial fill → **A15-R6**.
4. Where are bought shares? → invoke `kite_holdings` (settled) or `kite_positions` (same day / F&O).

---

### Rule 3 — Order Rejected

1. Read `rejection_reason`, match against **A9**.
2. For margin rejections → invoke `kite_margins`.
3. For ban period → if client asks about current position → invoke `kite_positions`.
4. If `app_id` is a numerical value and rejection relates to market protection, rate limit, or IOC on MCX → route to Rule 16.
5. For unmatched rejection → share `rejection_reason` verbatim.

---

### Rule 4 — RMS / Admin Square-Off

1. `placed_by` = ADMINSQF or starts with "rms" (per **A8**).
2. Invoke `kite_margins` to check margin shortfall.
3. Check if MIS + near auto square-off time (per **A6**).
4. Check for negative cash balance.
5. Respond per **A15-R7**.
6. If MIS carried forward (square-off failed) → respond per **A15-R8**.

---

### Rule 5 — Order Open in History

1. Unusual in history — likely later cancelled at session end.
2. Check for corresponding CANCELLED entry for same instrument/date. If found → apply Rule 6.
3. If genuinely open → respond per **A15-R9**. Times per **A7**.

---

### Rule 6 — Order Cancelled

1. Cancelled near session end → respond per **A15-R10**. Times per **A7**. Invoke `kite_gtt` if client wants persistent order.
2. LPP/price range → respond per **A15-R11**.
3. Partial fill + cancelled remainder → respond per **A15-R12**.
4. IOC → respond per **A15-R13**.

---

### Rule 7 — Unauthorized ("I Didn't Place This")

1. Check `placed_by`:
   a. ADMINSQF/rms → apply Rule 4.
   b. Client's own ID → respond per **A15-R14**. Escalate to support agent, investigation required.

---

### Rule 8 — SIP Order Investigation

1. `sip` = "Yes" or client asks about SIP failure.
2. If REJECTED → share reason. Common: wrong product (must be Regular CNC), insufficient margin, instrument blocked, qty exceeded.
3. If COMPLETE → share execution details per Rule 2.
4. If no order found → respond per **A15-R15**.

---

### Rule 9 — ATO Order Investigation

1. `ato` = "Yes" or client asks about ATO.
2. If REJECTED → share reason + respond per **A15-R16**.

---

### Rule 10 — AMO Order Behavior

1. Use `variety` internally to confirm AMO. Rules per **A10**.
2. AMO market for index options → blocked, use limit.
3. Pre-open AMO market → converts to limit at equilibrium/previous close.
4. Sell AMO without DDPI/POA: T-day stocks → after 6:30 AM next day; delivered → after 5 PM.

---

### Rule 11 — Basket Order Investigation

1. `basket` field has a value → respond per **A15-R17**.

---

### Rule 12 — Execution Time Beyond Market Hours

1. Respond per **A15-R18**.

---

### Rule 13 — F&O Buy Average / Intraday Identification

1. **F&O buy average:** FIFO across MIS + NRML combined. Per **A12**.
2. **Equity CNC sell + rebuy same day:** Original avg unchanged — speculative per income tax rules. Exception: T2T stocks. Per **A12**.
3. **Identifying intraday:** Use patterns from **A12**.
4. **MIS sell instead of CNC:** If client sold under MIS while holding CNC shares → the MIS sell created a fresh short intraday position, not a delivery exit. CNC holdings remain. MIS position auto-squared off at 3:25 PM. Respond per **A15-R21**.
5. If client asks about current buy average → invoke `kite_holdings`. Current positions → invoke `kite_positions`.

---

### Rule 14 — Multiple Orders for Same Instrument

1. Respond per **A15-R19** — summarize count, list each with type/order_type/product/status/quantity/price.
2. Use **A12** to identify trade type from product and buy/sell pairing.

---

### Rule 15 — No Matching Orders Found

1. Respond per **A15-R20**.

---

### Rule 16 — API Order Issues (SEBI Retail Algo Rules)

Applies when `app_id` is a numerical value (indicating a third-party Kite Connect API application — not "Kite Web", "Kite iOS", or other named Kite apps).

1. **Rate limit (429 response):** The client's API application exceeded the 10 orders-per-second rate limit. Respond per **A15-R22**. To place more than 10 orders per second, the strategy must be registered with the stock exchange.
2. **Market protection rejection:** Market orders and SL-M orders placed via API with market protection set to 0 are rejected. Respond per **A15-R23**. The client must set an appropriate market protection value, or use limit orders.
3. **MCX IOC rejection:** MCX does not support IOC validity in the algo segment. Respond per **A15-R24**. The client must use DAY validity for MCX orders via API.
4. **Order slicing:** API order slicing should be capped at a maximum of 10 slices to stay within the 10 orders-per-second rate limit.
5. For details on all SEBI retail algo compliance requirements, share the link from **A13**.
