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

TAGS: orders

## Protocol

# KITE ORDER HISTORY PROTOCOL

## Section A: Reference Data

### A1 — Fundamentals

- For today's live orders, invoke `kite_orders`.
- Orders follow price-time priority: first come, first served at same price.
- Zerodha pre-validates orders — some rejections won't appear in order book (shown in status notification only).
- Execution time beyond market hours = exchange reconciliation after connectivity issues, not actual execution beyond hours.

### A2 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |
|---|---|
| `created_at` | Order creation timestamp |
| `instrument` | Tradingsymbol |
| `type` | BUY/SELL |
| `product` | CNC/MIS/NRML/MTF/CO |
| `exchange` | Exchange |
| `total_quantity` | Total quantity |
| `filled_quantity` | Executed quantity |
| `price` | Price |
| `average_price` | Average execution price |
| `trigger_price` | SL trigger price |
| `order_type` | MARKET/LIMIT/SL/SL-M |
| `order_status` | Status |
| `order_timestamp` | Order time |
| `exchange_timestamp` | Exchange time |
| `order_timestamp_date` | Order date |
| `rejection_reason` | Rejection reason |
| `disclosed_quantity` | Disclosed qty |
| `cancelled_quantity` | Cancelled qty |
| `basket` | Basket name |
| `sip` | SIP indicator |
| `ato` | ATO indicator |
| `gttp_sl_percentage` | GTT SL % |
| `gttp_trgt_percentage` | GTT target % |

**Non-shareable:**

| Field | Interpretation |
|---|---|
| `client_id` | Internal client identifier |
| `placed_by` | Interpret per **A8** |
| `variety` | Identifies order subtype (AMO, CO, iceberg) — for internal routing only |
| `gtt` | GTT trigger ID — order was placed by a GTT trigger |
| `app_id` | GTT Orders or third-party API app identifier — for internal routing only |
| `validity` | Internal validity |
| `parent_order_id` | Internal — iceberg parent reference |
| `order_id` | Internal reference |
| `exchange_id` | Internal reference |
| `validity_ttl` | Internal TTL |
| `silo` | Internal |
| `basket_id` | Internal |
| `tags` | Internal tags |
| `gttp` | Internal |
| `order_result_id` | Internal |

### A3 — Order Statuses

| Status | Meaning |
|---|---|
| Complete | Fully executed — all quantity filled |
| Open | Pending execution — limit not hit, in queue, or circuit hit |
| Cancelled | By user, exchange end-of-session, IOC unfilled, or LPP range violation |
| Rejected | Failed validation — check `rejection_reason` |

### A4 — Product Types

| Product | Description |
|---|---|
| CNC | Delivery — equity only, no leverage, no auto square-off |
| MIS | Intraday — leveraged, auto squared off per **A6** |
| NRML | Overnight — F&O carry till expiry, full margin |
| MTF | Margin Trading Facility — delivery with leverage |
| CO | Cover Order — intraday with compulsory SL, cannot convert |

### A5 — Order Limits

| Limit | Value |
|---|---|
| Max orders per day | 5,000 across all segments |
| Max orders per minute | 400 |
| Max modifications per order | 25 |
| Max order value (equity) | ₹10 Crore |
| Max quantity (equity) | 1,00,000 |

### A6 — Auto Square-Off

| Segment | Time |
|---|---|
| Equity | 3:25 PM |
| Equity F&O | 3:26 PM |
| MCX | 10 min before market close |

- Charge: ₹50 + 18% GST per order. Failure: MIS converts to CNC/NRML, client must close next day. CO positions cannot be converted.

### A7 — Unmatched Order Cancellation Times

| Segment | Auto-Cancel Time |
|---|---|
| Equity | 4:00 PM |
| Currency | 5:00 PM |
| MCX | Market close (Nov–Mar 11:55 PM, Mar–Nov 11:30 PM — DST shift) |

### A8 — `placed_by` Values

| Value | Meaning |
|---|---|
| Client ID (6-char) | Normal client-placed order |
| ADMINSQF | Auto square-off by Zerodha RMS |
| Starts with "rms" + number | Squared off by Zerodha RMS |

### A9 — Common Rejections

| Rejection | Meaning | Resolution |
|---|---|---|
| Insufficient margin | Not enough margin | Invoke `kite_margins`. Add funds. Can still exit. |
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

### A10 — AMO Rules

| Rule | Detail |
|---|---|
| NSE/BSE equity window | 4:00 PM – 8:58 AM |
| F&O window | 3:45 PM – 9:10 AM |
| MCX window | 5:00 PM – 9:10 AM |
| AMO market for index options | Blocked — use limit |
| Pre-open AMO market | Converts to limit at equilibrium/previous close |
| Sell AMO without DDPI/POA | T-day stocks: only after 6:30 AM next day. Delivered stocks: after 5 PM. |

### A11 — Special Order Types

| Field | Value | Meaning |
|---|---|---|
| `sip` | "Yes" | SIP order — must use Regular CNC + market/limit |
| `ato` | "Yes" | ATO (alert-triggered) — order slicing not supported, qty within freeze limit |
| `basket` | basket name | Part of a basket — each order validated independently |
| `gtt` | trigger ID | GTT trigger ID — order was placed by a GTT trigger |
| `variety` = "iceberg" | — | Iceberg — `parent_order_id` links child orders to parent |

### A12 — Intraday Identification Logic

| Pattern | Classification |
|---|---|
| MIS or CO product | Intraday trade |
| CNC with only BUY (no same-day SELL) | Delivery / long-term |
| CNC with BUY + SELL same instrument same qty same day | Intraday round-trip (speculative, not delivery) |
| NRML | Overnight F&O position |
| MTF | Margin Trading Facility (delivery with leverage) |
| BUY (MIS) + SELL by ADMINSQF/rms | Intraday auto squared off |

- Exception: T2T stocks — same-day buy+sell treated as delivery, buy average updates to latest buy price.
- F&O buy average: FIFO across product types (MIS + NRML combined). Earliest buy matches first sell.
- Equity CNC sell + rebuy same day: Original buy average unchanged. Same-day round-trip = speculative per income tax rules.

### A13 — Links

| Topic | URL |
|---|---|
| Margin calculator | zerodha.com/margin-calculator |
| Market intelligence bulletin | zerodha.com/marketintel/bulletin |
| SEBI retail algo compliance | https://kite.trade/forum/discussion/15912/preparing-to-comply-with-sebis-retail-algo-rules-static-ip-ratelimits-order-types#latest |

### A14 — Escalation Data

Include when escalating to human agent: client ID, instrument, date, order details, and specific issue.

## Section B: Decision Flow

### Routing

```
Route by scenario
   ├─ Order status check (any) → Rule 1
   ├─ Order complete — execution / price questions → Rule 2
   ├─ Order rejected → Rule 3
   ├─ placed_by = ADMINSQF or "rms" prefix → Rule 4
   ├─ Order open in history (unusual) → Rule 5
   ├─ Order cancelled → Rule 6
   ├─ "I didn't place this order" → Rule 7
   ├─ SIP order investigation → Rule 8
   ├─ ATO order investigation → Rule 9
   ├─ AMO order behavior → Rule 10
   ├─ Basket order investigation → Rule 11
   ├─ Execution time beyond market hours → Rule 12
   ├─ F&O buy average / intraday identification → Rule 13
   ├─ Multiple orders for same instrument → Rule 14
   ├─ No matching orders found → Rule 15
   └─ app_id is numerical (third-party API) and rejection/rate limit query → Rule 16
```

### Fallback

If no root cause found after completing all diagnostic steps → escalate to human agent per **A14**.

## Section C: Rules

### Rule 1 — Order Status Check

1. Locate by instrument + date.
2. Share: `instrument`, `type`, `order_type`, `order_status`, `total_quantity`, `filled_quantity`, `average_price` (if COMPLETE), `exchange_timestamp`.
3. Check `placed_by` internally → ADMINSQF/rms → Rule 4.
4. Check `gtt` internally → GTT ID present → invoke `kite_gtt` or `kite_gtt_archived` scoped to the trigger date.
5. Check `app_id` internally → numerical value → if rejection or rate limit query, route to Rule 16.
6. Route by status: COMPLETE → Rule 2, REJECTED → Rule 3, OPEN → Rule 5, CANCELLED → Rule 6.

### Rule 2 — Order Complete

1. Confirm: `type` order for `total_quantity` of `instrument` was executed at `average_price` on `exchange_timestamp`.
2. Price discrepancy:
   a. Market order → market orders fill at the best available price.
   b. Limit at better price → limit orders guarantee the price as the worst, not the exact price.
   c. Client wanted breakout → use SL or GTT instead. Invoke `kite_gtt` if interested.
   d. SL trigger dispute → charts show snapshots; actual market price determines execution.
3. Partial fill → check `filled_quantity` < `total_quantity`; share `cancelled_quantity`.
4. Where are bought shares? → invoke `kite_holdings` (settled) or `kite_positions` (same day / F&O).

### Rule 3 — Order Rejected

1. Read `rejection_reason`, match against **A9**.
2. For margin rejections → invoke `kite_margins`.
3. For ban period → if client asks about current position → invoke `kite_positions`.
4. If `app_id` is numerical and rejection relates to market protection, rate limit, or IOC on MCX → route to Rule 16.
5. For unmatched rejection → share `rejection_reason` verbatim.

### Rule 4 — RMS / Admin Square-Off

1. `placed_by` = ADMINSQF or starts with "rms" per **A8**.
2. Invoke `kite_margins` to check margin shortfall.
3. Check if MIS + near auto square-off time per **A6**.
4. Check for negative cash balance.
5. Order was executed by Zerodha's risk management system on `exchange_timestamp`. Typical reasons: insufficient margin to maintain position; intraday (MIS) auto squared off at scheduled time per **A6**; negative cash balance requiring closure.
6. If MIS carried forward after square-off failure → failure can occur due to circuit limits, system failures, or connectivity. MIS converts to CNC/NRML per **A6** — client must close next trading day.

### Rule 5 — Order Open in History

1. Unusual in history — likely later cancelled at session end.
2. Check for corresponding CANCELLED entry for same instrument/date. If found → Rule 6.
3. If genuinely open → auto-cancelled at session end per **A7**.

### Rule 6 — Order Cancelled

1. Cancelled near session end → auto-cancelled at session end per **A7**. Suggest re-placing next session, or use GTT for orders valid up to 1 year. Invoke `kite_gtt` if client wants persistent order.
2. LPP/price range → exchange cancelled order — price was outside the allowed range. Retry closer to market price.
3. Partial fill + cancelled remainder → partially filled, share `filled_quantity` of `total_quantity` at `average_price`. Remaining `cancelled_quantity` was cancelled.
4. IOC → IOC orders auto-cancel any unfilled portion immediately.

### Rule 7 — Unauthorized ("I Didn't Place This")

1. Check `placed_by`:
   a. ADMINSQF/rms → apply Rule 4.
   b. Client's own ID → order appears placed from client's account. Escalate to human agent per **A14** for investigation. Suggest checking third-party Kite Connect API access; consider blocking account if unauthorized.

### Rule 8 — SIP Order Investigation

1. `sip` = "Yes" or client asks about SIP failure.
2. If REJECTED → share reason. Common: wrong product (must be Regular CNC), insufficient margin, instrument blocked, qty exceeded.
3. If COMPLETE → share execution details per Rule 2.
4. If no order found → SIP may not have triggered. Verify: basket linked to SIP, product type Regular CNC, order type market or limit. Check registered email — Zerodha sends a SIP summary email with rejection reasons.

### Rule 9 — ATO Order Investigation

1. `ato` = "Yes" or client asks about ATO.
2. If REJECTED → share reason. ATO orders place automatically when Kite alert triggers. Order slicing not supported — quantity must be within exchange freeze limit.

### Rule 10 — AMO Order Behavior

1. AMO market for index options → blocked per **A10**, use limit.
2. Pre-open AMO market → converts to limit at equilibrium/previous close per **A10**.
3. Sell AMO without DDPI/POA → per **A10**: T-day stocks after 6:30 AM next day; delivered after 5 PM.

### Rule 11 — Basket Order Investigation

1. `basket` field has a value → order was part of a basket. Basket orders execute individually — each subject to its own margin and exchange validation. Some may succeed while others fail.

### Rule 12 — Execution Time Beyond Market Hours

1. Displayed time reflects exchange reconciliation after a connectivity disruption per **A1**. Order was executed within market hours. Direct client to tradebook for actual execution time.

### Rule 13 — F&O Buy Average / Intraday Identification

1. F&O buy average: FIFO across MIS + NRML combined per **A12**.
2. Equity CNC sell + rebuy same day: per **A12**.
3. Identifying intraday: use patterns from **A12**.
4. MIS sell instead of CNC: if client sold under MIS while holding CNC shares → MIS sell created a fresh short intraday position, not a delivery exit. CNC holdings remain. MIS auto-squared off per **A6**. To sell delivery holdings, use CNC.
5. If client asks about current buy average → invoke `kite_holdings`. Current positions → invoke `kite_positions`.

### Rule 14 — Multiple Orders for Same Instrument

1. Summarize count and list each with `type`, `order_type`, `product`, `order_status`, `quantity`, `price`.
2. Use **A12** to identify trade type from product and buy/sell pairing.

### Rule 15 — No Matching Orders Found

1. No orders found for instrument between `from_date` and `to_date`. Direct client to verify instrument name, exchange, and date range. Orders rejected pre-exchange may not appear in history.

### Rule 16 — API Order Issues (SEBI Retail Algo Rules)

1. Rate limit (429 response): API application exceeded the 10 orders-per-second rate limit. Per SEBI retail algo regulations. To place more than 10 orders per second, the trading strategy must be registered with the stock exchange. Link per **A13**.
2. Market protection rejection: market and SL-M orders placed via API with market protection set to 0 are rejected. Mandated by exchanges for all algo orders. Use limit order or set an appropriate market protection value. Link per **A13**.
3. MCX IOC rejection: MCX does not support IOC validity in the algo segment. Orders via third-party API on MCX with IOC validity will be rejected. Use DAY validity instead.
4. Order slicing: API order slicing should be capped at a maximum of 10 slices to stay within the 10 orders-per-second rate limit.
5. For details on all SEBI retail algo compliance, share link from **A13**.

# # ACCOUNT MODIFICATION REPORT
