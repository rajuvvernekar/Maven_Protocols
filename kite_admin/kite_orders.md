# kite_orders

## Description

WHEN TO USE:

When clients:
- Ask about today's order status (executed, pending, cancelled, or rejected)
- Ask about order rejection reason or error message when placing an order
- Report order pending or not getting executed despite being placed
- Report order cancelled at end of day or by exchange
- Report partial fill (only some quantity executed, rest cancelled)
- Question execution price different from expected (market order filled at multiple levels, limit order got a better price, SL triggered at unexpected price)
- Ask why market orders are blocked for a specific instrument (stock options, T2T, illiquid, deep ITM, ETFs)
- Ask why MIS or intraday orders are blocked for a stock or contract (T2T, ASM/GSM, ban period, low liquidity)
- Ask about auto square-off (position squared off by Zerodha/RMS, timings, charges, or why it failed and carried forward)
- Report unauthorized order they didn't place
- Ask about AMO (After Market Order) placement, rejection, conversion to limit in pre-open, timing
- Ask about product type conversion (MIS↔CNC, MIS↔NRML, CO conversion blocked)
- Ask about circuit limit or ban period impact on open orders
- Ask about order types (MARKET, LIMIT, SL, SL-M), product types (CNC, MIS, NRML, MTF, CO), or validity types (DAY, IOC, TTL)
- Ask about auto square-off timings, charges (₹50 + GST), or consequences of failed square-off
- Report order book display issues (rejected order not visible, downloaded file showing dates instead of quantities, execution time beyond market hours)

TRIGGER KEYWORDS: "order rejected", "order pending", "order cancelled", "not executed", "not filled", "rejection reason", "squared off", "square off", "auto square", "RMS", "ADMINSQF", "market order blocked", "MIS blocked", "intraday blocked", "AMO", "after market order", "wrong price", "different price", "execution price", "circuit limit", "ban period", "order status", "product conversion", "convert MIS", "convert CNC", "convert NRML", "unauthorized order", "order error", "order not placed", "partial fill", "IOC", "SL triggered", "stoploss triggered", "cover order", "iceberg", "order book", "order window"

TAGS: orders, margins

## Protocol

# KITE ORDERS PROTOCOL

## Section A: Reference Data

### A1 — Fundamentals

- Today's orders only — for historical orders, invoke `kite_order_history`.
- Clicking the instrument hyperlink opens the Order History sub-view showing the full lifecycle: OPEN PENDING → OPEN → COMPLETE/CANCELLED/REJECTED with timestamps, exchange times, filled qty, avg price, and variety.
- Orders follow price-time priority: first come, first served at same price.
- Zerodha pre-validates orders — some rejections won't appear in the order book (shown in status notification only).

### A2 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |
|---|---|
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
| `validity_day_ioc` | DAY/IOC |
| `time` | Order time |
| `exchange_time` | Exchange time |
| `exchange_updated_time` | Exchange last update |
| `rejection_reason` | Rejection reason |
| `disclosed_quantity` | Disclosed qty |
| `cancelled_quantity` | Cancelled qty |

**Non-shareable:**

| Field | Interpretation |
|---|---|
| `parent_order_id` | Internal (iceberg parent) |
| `placed_by` | Placed by identifier — interpret per **A13** |
| `order_id` | Internal order identifier |
| `exchange_id` | Internal exchange identifier |

### A3 — Order Statuses

| Status | Meaning |
|---|---|
| Complete | Fully executed — all quantity filled |
| Open | Pending execution — limit not hit, in queue, or circuit hit |
| Cancelled | By user, system (IOC unmatched), or exchange (end of session / LPP range) |
| Rejected | Failed validation — check `rejection_reason` |

### A4 — Product Types

| Product | Description |
|---|---|
| CNC | Long-term / delivery — equity only, no leverage, no auto square-off, no short selling |
| MIS | Intraday — leveraged, auto squared off per **A9** |
| NRML | Overnight — F&O carry till expiry, full margin required |
| MTF | Margin Trading Facility — partial funding, interest charged, equity only |
| CO | Cover Order — intraday with compulsory SL, cannot convert to other product types |

### A5 — Order Types

| Order Type | Behavior |
|---|---|
| Market | Best available price — may fill at multiple price points |
| Limit | Specified price or better — may remain pending in queue |
| SL | Stop-Loss Limit — triggers at `trigger_price`, places limit at `price` |
| SL-M | Stop-Loss Market — triggers at `trigger_price`, places market order. Discontinued on BSE. |

### A6 — Validity Types

| Validity | Behavior |
|---|---|
| Day | Active till market close |
| IOC | Immediate or Cancel — partial fill possible, unfilled auto-cancelled |
| TTL | Minutes validity (1–120 min) — not available in BFO and MCX |

### A7 — Order Limits

| Limit | Value |
|---|---|
| Max orders per day | 5,000 across all segments |
| Max orders per minute | 400 |
| Max modifications per order | 25 |
| Max order value (equity) | ₹10 Crore |
| Max quantity (equity) | 1,00,000 (regular can exceed; iceberg/CO cannot) |

### A8 — Unmatched Order Cancellation Times

| Segment | Auto-Cancel Time |
|---|---|
| Equity | 4:00 PM |
| Currency | 5:00 PM |
| Commodities (MCX) | MCX market close (shifts with US DST: Nov–Mar 11:55 PM, Mar–Nov 11:30 PM) |

### A9 — MIS Auto Square-Off Times

| Segment | Time |
|---|---|
| Equity | 3:25 PM |
| F&O | 3:26 PM |
| MCX | 10 min before market close |

- Auto square-off charge: ₹50 \+ 18% GST per order.
- If auto square-off fails (system failure, circuit hit, connectivity), MIS converts to CNC/NRML and carries forward — client must close next day.

### A10 — Market Order Blocks

| Condition | Blocked For |
|---|---|
| Stock options | All stock options |
| Illiquid index options | FinNifty/MidCPNifty/Sensex: only if OI > 500 lots. Nifty/BankNifty: current+next week/month only, deep ITM (>5%) blocked |
| T2T and debt | All T2T and debt instruments |
| Zero volume | Zero volume instruments during day |
| Long-dated options | Illiquid long-dated options |
| Deep ITM index | Deep ITM index options |
| ETF first 2 min | Certain ETFs 9:15–9:17 AM for market/SL-M/AMO |
| Index options AMO | Index options via AMO |

- Resolution: use limit order or market order with market protection enabled.

### A11 — MIS / Intraday Blocks

- Blocked for: T2T stocks | ASM/GSM stocks | low-liquidity scrips | high-VAR scrips | unsolicited SMS watchlist stocks | F&O ban period contracts | FINNIFTY contracts with OI < 20,000 qty (500 lots).
- Resolution: use CNC (equity) or NRML (F&O) instead.

### A12 — Common Rejections

| Rejection | Meaning | Resolution |
|---|---|---|
| Insufficient margin | Not enough margin | Invoke `kite_margins`. Add funds. |
| Multiple sell orders — insufficient margin | Multiple sell orders for the same position. Only one matching the position quantity is needed. Excess sell orders are treated as fresh short positions requiring full margin. | Cancel excess pending sell orders. Place a single sell matching the open position quantity. |
| Negative cash | Negative cash from MTM losses | Add cash before new trades. Can still exit existing positions. |
| Max order value | Exceeds ₹10 Crore | Split orders, use iceberg or basket. |
| Max quantity | Exceeds 1,00,000 | Reduce qty, use iceberg, sticky window, or basket. |
| Max orders/day | Exceeded 5,000 | Contact support to exit positions. |
| Max modifications | Exceeded 25 per order | Cancel and place new order. |
| Trigger price invalid | SL buy: trigger ≤ limit. SL sell: trigger ≥ limit. | Correct trigger/limit relationship. |
| SL trigger-limit gap | Gap exceeds exchange permissible range | Narrow the gap. |
| LPP range | Price outside Limit Price Protection range | Retry closer to market price. |
| Theoretical price | Option price too far from theoretical | Place closer to theoretical price. |
| Limit far from LTP | Limit 50–150% from LTP for stock/index options | Place closer to LTP. |
| Ban period | F&O in ban | Only exit allowed. No new positions or intraday. |
| Exchange restricted | Account restricted by exchange | New account (wait 3 days), KRA verification, or NRI status not updated. |
| SL-M on BSE | SL-M discontinued on BSE | Use SL-L instead — set limit slightly away from trigger. |
| OI restriction | NRML blocked for certain strikes (broker OI cap) | Use MIS. Consider Orbis custodial for full access. |
| Currency NRML | NRML blocked for currency pair (broker OI limit) | MIS still allowed. |
| Currency position limit | Client limit exceeded | USDINR 85K lots, EURINR/GBPINR 5K, JPYINR 2K. |
| MTF sell conflict | MTF buy blocked — open CNC sell or MTF sell for same stock | Buy via CNC instead. MTF position restores next day. |
| Order being processed | Already executed/cancelled | Refresh page for updated status. |
| CO on ETF / restricted instruments | CO not allowed on ETFs, BSE scrips, stock options, currency options, index options | Use CNC or MIS instead. |
| Invalid quantity / odd lot | Quantity does not match current lot size — residual odd-lot from SEBI lot size revision | Odd-lot positions cannot be traded. Hold until expiry — cash-settled based on moneyness. Lot size revision link per **A16**. |

### A13 — `placed_by` Values

| Value | Meaning |
|---|---|
| Client ID (6-char) | Normal client-placed order |
| ADMINSQF | Auto square-off by Zerodha RMS |
| Starts with "rms" \+ number (rms1, rms2...) | Squared off by Zerodha RMS |

### A14 — AMO (After Market Orders)

- Placement window: 4:00 PM to 8:58 AM for NSE/BSE equity. Executes at next market open. Cannot place during market hours.
- AMO market order for index options: blocked — use limit instead.
- Pre-open session conversion: AMO market orders convert to limit at equilibrium price (or previous day's close if no equilibrium). Standard exchange behavior.

### A15 — Product Conversion Rules

| Conversion | Allowed? | Notes |
|---|---|---|
| MIS → CNC | Yes | If sufficient margin. Go to Positions → Convert. |
| MIS → NRML | Yes | If sufficient margin. |
| CNC/NRML → MIS | Yes | Before auto square-off time only. |
| CO → anything | No | Cover orders cannot be converted. |
| Any → MIS (after square-off time) | No | No conversions to MIS after square-off time. |

### A16 — Links

| Topic | URL |
|---|---|
| Intraday/MIS approved list | https://docs.google.com/spreadsheets/d/1XwWNCASDmrXfx5LtFNna0Kmkt5vHtqkjICvVcUZaQhw/edit#gid=0 |
| Margin calculator | https://zerodha.com/margin-calculator/ |
| Bulletin (restrictions) | https://zerodha.com/marketintel/bulletin |
| NSE trade verification | https://www.nseindia.com/static/invest/first-time-investor-trade-verification |
| SL execution explained | https://support.zerodha.com/category/trading-and-markets/charts-and-orders/order/articles/why-was-my-sl-order-executed-even-though-the-price-did-not-breach-my-trigger |
| Lot size revision bulletin | https://zerodha.com/marketintel/bulletin/429705/revision-in-lot-size-of-index-derivative-contracts-from-december-30-2025 |

### A17 — Escalation Data

Include when escalating to human agent: client ID, instrument, order type, time, and specific issue.

### A18 — Negative Opening Balance with Negative Option Premium

- When `opening_balance` is negative, blocks all fresh positions.
- If `option_premium` is also negative (premium paid for buying options), proceeds from exiting long options or entering short options can only be used for new long option trades in the same segment on the same day; available for other trades from next trading day.

## Section B: Decision Flow

### Routing

```
Route by scenario
   ├─ Order complete — execution / price questions → Rule 1
   ├─ Order open / pending → Rule 2
   ├─ Order cancelled → Rule 3
   ├─ Order rejected → Rule 4
   ├─ AMO query → Rule 5
   ├─ Product conversion query → Rule 6
   ├─ placed_by = ADMINSQF or "rms" prefix → Rule 7
   ├─ "I didn't place this order" → Rule 8
   ├─ Circuit / ban period impact → Rule 9
   └─ Order book display issues → Rule 10
```

### Fallback

If no root cause found after completing all diagnostic steps → escalate to human agent per **A17**.

## Section C: Rules

### Rule 1 — Order Complete

1. Confirm: `type` order for `total_quantity` of `instrument` was executed at `average_price` on `exchange_time`.
2. If client questions execution price:
   a. Market order → Per **A5**, market order fills at best available price — large quantity may fill at multiple price levels.
   b. Limit order executed at better price → limit order at `price` executed at `average_price` because market had counterparties at a better price. Limit guarantees price as the worst, not the exact price.
   c. Client wanted to buy at breakout (not immediately) → use SL (intraday) with trigger at `price` or GTT (valid up to 1 year). Invoke `kite_gtt` if client wants to set up GTT.
   d. SL trigger seems "wrong" → charts display snapshots; actual market price determines execution. Client can verify via NSE trade verification per **A16**. Reference SL execution link per **A16**.
3. If `filled_quantity` < `total_quantity` → partial fill. Check `cancelled_quantity`. IOC orders: unfilled portion auto-cancelled.
4. If client asks where bought shares are → invoke `kite_holdings` (settled) or `kite_positions` (today's buy).

### Rule 2 — Order Open / Pending

1. Limit order → market hasn't reached the price yet, or earlier orders at the same price are ahead in the queue (price-time priority).
2. Circuit hit → instrument hit circuit limit. Order remains open; cannot fill until counterparties exist. If unfilled, exchange cancels at segment close per **A8**.
3. SL/SL-M trigger not yet hit → stop-loss will activate when price reaches `trigger_price`.
4. SL-M orders with trigger outside circuit limits stay open without rejection — normal exchange behavior.

### Rule 3 — Order Cancelled

1. Check Order History sub-view for cancellation timing and context:
   a. Cancelled near market close → unmatched pending orders auto-cancelled at session end per **A8**. Suggest re-placing next session, or use GTT for orders valid up to 1 year. Invoke `kite_gtt`.
   b. LPP range cancellation → exchange cancelled because price was outside the allowed Limit Price Protection range. Retry closer to current market price.
   c. IOC partial fill \+ cancel → IOC order partially filled; unfilled portion auto-cancelled.
   d. Cancelled by user → no action needed.

### Rule 4 — Order Rejected

1. Read `rejection_reason` and match against **A12**.
2. For margin rejections:
   a. Check if client has multiple pending sell orders for same instrument. Excess orders treated as fresh short positions requiring full margin. Direct client to cancel excess pending sells and place a single sell matching position quantity.
   b. Invoke `kite_margins`. Check `opening_balance` first. Per **A18**, negative opening balance blocks all fresh positions — direct client to add funds. If `option_premium` is also negative, include option premium context per **A18**.
   c. If `opening_balance` is not negative, identify specific shortfall from `available_margin`, `used_margin`, `available_cash`.
3. For market order blocks → match against **A10**, respond with reason \+ resolution.
4. For MIS blocks → match against **A11**, respond with reason \+ resolution.
5. For quantity/value limits → refer to **A7**.
6. For trigger price errors, ban period, OI restrictions, BSE SL-M, exchange restricted, MTF conflicts → use matching row in **A12**.
7. For CO on ETF or other restricted instruments → use matching row in **A12**.
8. For invalid quantity / odd lot from lot size revision → use matching row in **A12**.
9. For any rejection not matching **A12** → share `rejection_reason` text verbatim and suggest retry or contact support.

### Rule 5 — AMO (After Market Orders)

1. General AMO query → Per **A14**, communicate AMO placement window and execution timing.
2. AMO market order for index options rejected → blocked per **A14**; use limit instead.
3. AMO became limit order → Per **A14**, AMO market orders convert to limit at equilibrium price — standard exchange behavior.

### Rule 6 — Product Conversion

1. Check conversion rules per **A15**.
2. If margin insufficient for conversion → invoke `kite_margins`.

### Rule 7 — RMS / Admin Square-Off

1. `placed_by` = ADMINSQF or starts with "rms" per **A13**.
2. Invoke `kite_margins` to check margin shortfall.
3. Check if product was MIS and time was near auto square-off window per **A9**.
4. Check if account had negative cash balance.
5. Order was executed by Zerodha's risk management system. Typical reasons: insufficient margin to maintain position; intraday (MIS) auto squared off at the scheduled time per **A9**; negative cash balance requiring closure. Include margin data from `kite_margins` if available.
6. If client asks about the squared-off position → invoke `kite_positions`.

### Rule 8 — Unauthorized Order ("I Didn't Place This")

1. Check `placed_by`:
   a. ADMINSQF or starts with "rms" → apply Rule 7.
   b. Client's own ID → escalate to human agent per **A17** immediately.

### Rule 9 — Circuit / Ban Period Impact

1. Can't exit at circuit → no counterparties when stock hits circuit. Order remains pending. If MIS, may convert to delivery (CNC) if not filled by square-off time — can lead to short delivery or auction risk. If client asks about resulting position → invoke `kite_positions`.
2. Ban period → only exit orders allowed. No new positions or intraday. Restriction lifts when OI falls below 80% of market-wide limit.

### Rule 10 — Order Book Display Issues

1. Rejected order not in order book → some orders rejected by Zerodha pre-validation before reaching exchange. Won't appear in order book; rejection reason shows in order status notification on Kite per **A1**.
2. Downloaded file shows dates instead of quantities → Excel formatting issue. Open in Notepad or Notepad++ to see correct values.
3. Execution time beyond market hours → Zerodha reconciles with exchange after a brief disconnection. Actual execution happened during market hours. Direct client to tradebook for real execution time.
