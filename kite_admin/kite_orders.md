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

## Protocol

# KITE ORDERS PROTOCOL

---

## Section A: Reference Data

---

### A1 — Tool Purpose & Fundamentals

This tool returns **today's orders only**. For historical orders, use `kite_order_history`.

Clicking the instrument hyperlink opens the **Order History sub-view** showing the full lifecycle: OPEN PENDING → OPEN → COMPLETE/CANCELLED/REJECTED with timestamps, exchange times, filled qty, avg price, and variety.

Orders follow **price-time priority**: first come, first served at same price.

Zerodha pre-validates orders — some rejections won't appear in the order book (shown in status notification only).

**Input:** Client ID — returns today's orders.

---

### A2 — Field Usage Rules

**Shareable fields:**

`instrument` | `type` | `product` | `exchange` | `total_quantity` | `filled_quantity` | `price` | `average_price` | `trigger_price` | `order_type` | `order_status` | `validity_day_ioc` | `time` | `exchange_time` | `exchange_updated_time` | `rejection_reason` | `disclosed_quantity` | `cancelled_quantity`

**Internal-only fields** (use for reasoning; communicate outcomes in plain language):

`parent_order_id` | `placed_by`

**Client-facing terminology:**

| Internal Term | Client-Facing Alternative |
|---|---|
| `order_id` | (omit — internal reference) |
| `exchange_id` | (omit — internal reference) |
| `placed_by` = ADMINSQF or starts with "rms" | "executed by Zerodha's risk management system" |
| `placed_by` = client ID | (normal client-placed order — do not mention the field) |

---

### A3 — Order Statuses

| Status | Meaning |
|---|---|
| Complete | Fully executed — all quantity filled |
| Open | Pending execution — limit not hit, in queue, or circuit hit |
| Cancelled | By user, system (IOC unmatched), or exchange (end of session / LPP range) |
| Rejected | Failed validation — check `rejection_reason` |

---

### A4 — Product Types

| Product | Description |
|---|---|
| CNC | Long-term / delivery — equity only, no leverage, no auto square-off, no short selling |
| MIS | Intraday — leveraged, auto squared off (Equity 3:25 PM, F&O 3:26 PM, MCX 10 min before close). Charge ₹50 + 18% GST if auto squared off |
| NRML | Overnight — F&O carry till expiry, full margin required |
| MTF | Margin Trading Facility — partial funding, interest charged, equity only |
| CO | Cover Order — intraday with compulsory SL, cannot convert to other product types |

---

### A5 — Order Types

| Order Type | Behavior |
|---|---|
| Market | Best available price — may fill at multiple price points |
| Limit | Specified price or better — may remain pending in queue |
| SL | Stop-Loss Limit — triggers at `trigger_price`, places limit at `price` |
| SL-M | Stop-Loss Market — triggers at `trigger_price`, places market order. Discontinued on BSE. |

---

### A6 — Validity Types

| Validity | Behavior |
|---|---|
| Day | Active till market close |
| IOC | Immediate or Cancel — partial fill possible, unfilled auto-cancelled |
| TTL | Minutes validity (1–120 min) — not available in BFO and MCX |

---

### A7 — Order Limits

| Limit | Value |
|---|---|
| Max orders per day | 5,000 across all segments |
| Max orders per minute | 400 |
| Max modifications per order | 25 |
| Max order value (equity) | ₹10 Crore |
| Max quantity (equity) | 1,00,000 (regular can exceed; iceberg/CO cannot) |

---

### A8 — Unmatched Order Cancellation Times

| Segment | Auto-Cancel Time |
|---|---|
| Equity | 4:00 PM |
| Currency | 5:00 PM |
| Commodities (MCX) | MCX market close (shifts with US DST: Nov–Mar 11:55 PM, Mar–Nov 11:30 PM) |

---

### A9 — MIS Auto Square-Off Times

| Segment | Time |
|---|---|
| Equity | 3:25 PM |
| F&O | 3:26 PM |
| MCX | 10 min before market close |

Auto square-off charge: ₹50 + 18% GST per order. If auto square-off fails (system failure, circuit hit, connectivity), MIS converts to CNC/NRML and carries forward — client must close next day.

---

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

**Resolution:** Use limit order or market order with market protection enabled.

---

### A11 — MIS/Intraday Blocks

Blocked for: T2T stocks | ASM/GSM stocks | low-liquidity scrips | high-VAR scrips | unsolicited SMS watchlist stocks | F&O ban period contracts | FINNIFTY contracts with OI < 20,000 qty (500 lots).

**Resolution:** Use CNC (equity) or NRML (F&O) instead.

---

### A12 — Common Rejections

| Rejection | Meaning | Resolution |
|---|---|---|
| Insufficient margin | Not enough margin | Cross-check `kite_margins`. Add funds. |
| Multiple sell orders — insufficient margin | Client placed multiple sell orders for the same position. Only one sell order matching the position quantity is needed to exit. Additional sell orders are treated as fresh short positions requiring full margin. | Cancel excess pending sell orders. Place a single sell order matching the open position quantity to exit. |
| Negative cash | Negative cash from MTM losses | Add cash before new trades. Can still exit existing positions. |
| Max order value | Exceeds ₹10 Crore | Split orders, use iceberg or basket. |
| Max quantity | Exceeds 1,00,000 | Reduce qty, use iceberg, sticky window, or basket. |
| Max orders/day | Exceeded 5,000 | Contact support to exit positions. |
| Max modifications | Exceeded 25 per order | Cancel and place new order. |
| Trigger price invalid | SL buy: trigger must ≤ limit. SL sell: trigger must ≥ limit. | Correct trigger/limit relationship. |
| SL trigger-limit gap | Gap exceeds exchange permissible range | Narrow the gap. |
| LPP range | Price outside Limit Price Protection range | Retry closer to market price. |
| Theoretical price | Option price too far from theoretical | Place closer to theoretical price. |
| Limit far from LTP | Limit 50–150% from LTP for stock/index options | Place closer to LTP. |
| Ban period | F&O in ban | Only exit allowed, no new positions or intraday. |
| Exchange restricted | Account restricted by exchange | New account (wait 3 days), KRA verification, or NRI status not updated. |
| SL-M on BSE | SL-M discontinued on BSE | Use SL-L instead — set limit slightly away from trigger. |
| OI restriction | NRML blocked for certain strikes (broker OI cap) | Use MIS. Consider Orbis custodial for full access. |
| Currency NRML | NRML blocked for currency pair (broker OI limit) | MIS still allowed. |
| Currency position limit | Client limit exceeded | USDINR 85K lots, EURINR/GBPINR 5K, JPYINR 2K. |
| MTF sell conflict | MTF buy blocked — open CNC sell or MTF sell for same stock | Buy via CNC instead. MTF position restores next day. |
| Order being processed | Already executed/cancelled | Refresh page for updated status. |
| CO on ETF / restricted instruments | Cover orders are not allowed on ETFs, BSE scrips, stock options, currency options, and index options | Use CNC or MIS instead. |
| Invalid quantity / odd lot | Order quantity does not match the current lot size — residual odd-lot from SEBI lot size revision | Odd-lot positions cannot be traded. Must hold until expiry — will be cash-settled based on moneyness. Redirect to `kite_positions` Rule 10 for full guidance. For details on the lot size revision: [Lot size revision bulletin](https://zerodha.com/marketintel/bulletin/429705/revision-in-lot-size-of-index-derivative-contracts-from-december-30-2025). |

---

### A13 — `placed_by` Values

| Value | Meaning |
|---|---|
| Client ID (6-char) | Normal client-placed order |
| ADMINSQF | Auto square-off by Zerodha RMS |
| Starts with "rms" + number (rms1, rms2...) | Squared off by Zerodha RMS |

---

### A14 — AMO (After Market Orders)

**Placement window:** 4:00 PM to 8:58 AM for NSE/BSE equity. Executes at next market open. Cannot place during market hours.

**AMO market order for index options:** Blocked — use limit order instead.

**Pre-open session conversion:** AMO market orders convert to limit at equilibrium price (or previous day's close if no equilibrium). Standard exchange behavior.

---

### A15 — Product Conversion Rules

| Conversion | Allowed? | Notes |
|---|---|---|
| MIS → CNC | Yes | If sufficient margin. Go to Positions → Convert. |
| MIS → NRML | Yes | If sufficient margin. |
| CNC/NRML → MIS | Yes | Before auto square-off time only. |
| CO → anything | No | Cover orders cannot be converted. |
| Any → MIS (after square-off time) | No | No conversions to MIS after square-off time. |

---

### A16 — Links

| Topic | URL |
|---|---|
| Intraday/MIS approved list | https://docs.google.com/spreadsheets/d/1XwWNCASDmrXfx5LtFNna0Kmkt5vHtqkjICvVcUZaQhw/edit#gid=0 |
| Margin calculator | https://zerodha.com/margin-calculator/ |
| Bulletin (restrictions) | https://zerodha.com/marketintel/bulletin |
| NSE trade verification | https://www.nseindia.com/static/invest/first-time-investor-trade-verification |
| SL execution explained | https://support.zerodha.com/category/trading-and-markets/charts-and-orders/order/articles/why-was-my-sl-order-executed-even-though-the-price-did-not-breach-my-trigger |
| Lot size revision bulletin | https://zerodha.com/marketintel/bulletin/429705/revision-in-lot-size-of-index-derivative-contracts-from-december-30-2025 |

---

### A17 — Escalation Data Template

When escalating, always include: **client ID, instrument, order type, time, and specific issue.**

---

### A18 — Response Templates

**R1 — Complete (basic):**
"Your [type] order for [total_quantity] qty of [instrument] was executed at an average price of ₹[average_price] on [exchange_time]."

**R2 — Market order price explanation:**
"Market orders fill at the best available prices. If the order quantity is large, it may fill at multiple price levels. This is normal exchange behavior."

**R3 — Limit order better price:**
"Your limit [type] order at ₹[price] executed at ₹[average_price] because the market had [buyers/sellers] at a [better] price. Limit orders guarantee your price as the worst you'll get, not the exact price."

**R4 — SL trigger vs chart:**
"Charts display snapshots of trading activity and may not reflect every individual trade executed at the exchange. The actual market price at the exchange determines the execution of your order, and brokers have no control over this process. You can verify the execution of your trade using your exchange trade ID through the NSE trade verification module: [NSE Trade Verification](https://www.nseindia.com/static/invest/first-time-investor-trade-verification). For further details: [Why was my SL order executed even though the price did not breach my trigger?](https://support.zerodha.com/category/trading-and-markets/charts-and-orders/order/articles/why-was-my-sl-order-executed-even-though-the-price-did-not-breach-my-trigger)"

**R5 — Want to buy at breakout price:**
"For buying only when the price reaches ₹[price], use a Stop-Loss (SL) order with trigger price ₹[price] for intraday, or a GTT order with trigger ₹[price] for a long-standing order valid up to 1 year."

**R6 — Limit pending:**
"Your limit [type] order for [instrument] at ₹[price] is pending. The market hasn't reached your price yet, or earlier orders at the same price are ahead in the queue (price-time priority)."

**R7 — Circuit hit:**
"The instrument has hit its circuit limit. Your order will remain open but cannot fill until there are counterparties. If it doesn't fill, the exchange will cancel it at [segment close time]."

**R8 — SL pending:**
"Your stop-loss order will activate when the price reaches your trigger price of ₹[trigger_price]. It is currently pending."

**R9 — Cancelled at session end:**
"Unmatched pending orders are auto-cancelled by the exchange at session end. Place again next session, or use a GTT order for orders valid up to 1 year."

**R10 — LPP cancellation:**
"The exchange cancelled your order because the price was outside the allowed Limit Price Protection range. Retry with a price closer to the current market price."

**R11 — IOC partial fill:**
"Your IOC (Immediate or Cancel) order was partially filled ([filled_quantity] of [total_quantity] qty). The unfilled portion was auto-cancelled. This is how IOC orders work."

**R12 — User cancelled:**
"This order was cancelled. No action needed."

**R13 — RMS square-off:**
"This [type] order for [instrument] was executed by Zerodha's risk management system [at exchange_time]. This typically happens when:
- Your account had insufficient margin to maintain the position
- It was an intraday (MIS) position auto squared off at the scheduled time
- Your account had a negative cash balance requiring position closure

Auto square-off charges: ₹50 + 18% GST per order."

**R14 — AMO educational:**
"AMO lets you place orders outside market hours (4:00 PM to 8:58 AM for NSE/BSE). Orders execute at next market open. You cannot place AMO during market hours."

**R15 — AMO index option blocked:**
"Market orders via AMO are blocked for index options. Use a limit order instead."

**R16 — AMO became limit:**
"Market orders placed in the pre-open session (including AMO) are converted to limit orders at the equilibrium price (or previous day's close if no equilibrium). This is standard exchange behavior."

**R17 — Pre-validated rejection not in order book:**
"Some orders are rejected by Zerodha's pre-validation before reaching the exchange. These won't appear in the order book but the rejection reason shows in the order status notification on Kite."

**R18 — Downloaded file date formatting:**
"This is an Excel formatting issue. It converts values like '1/1' to dates. Open the file in Notepad or Notepad++ to see correct values."

**R19 — Execution time beyond market hours:**
"This happens when Zerodha reconciles with the exchange after a brief disconnection. The actual execution happened during market hours. Check the tradebook for the real execution time."

**R20 — BSE market order conversion:**
"BSE market orders are converted to limit orders with a 3% market protection from LTP. This is standard BSE behavior."

**R21 — Ban period:**
"[instrument] is in the F&O ban period. Only exit orders are allowed. No new positions or intraday trades."

**R22 — OI restriction (NRML blocked):**
"NRML orders for this strike are restricted due to SEBI's broker-level Open Interest cap. You can trade this strike using MIS (intraday). For unrestricted access to all strikes, consider opening an Orbis custodial account."

**R23 — Circuit + MIS risk:**
"When a stock hits circuit, there are no counterparties. Your order will remain pending. If the instrument is in MIS, it may convert to delivery (CNC) if not filled by square-off time. This can lead to short delivery or auction risk."

**R24 — Margin rejection due to negative opening balance:**
"Your order was rejected due to insufficient margin. Your opening balance is ₹[opening_balance] (negative), which means your account started the day with a deficit. A negative opening balance blocks all fresh positions until you add funds to clear it. [If option_premium is negative: Your option premium shows ₹[option_premium]. This reflects premium paid for buying options. Proceeds from exiting long options or entering short options can only be used for new long option trades in the same segment on the same day, and become available for other trades from the next trading day (per Kite Positions A10).] Please add funds to cover the deficit and retry your order."

**R25 — Multiple sell orders margin rejection:**
"You placed multiple sell orders for [instrument]. Only one sell order matching your position quantity of [quantity] is needed to exit. Additional sell orders are treated as fresh short positions, which require full margin. Cancel any excess pending sell orders and place a single sell order for [quantity] qty to close your position."

---

## Section B: Decision Flow

---

### Preflight (run on every query)

```
1. Locate the order by instrument, type (BUY/SELL), time.
2. Open Order History sub-view (click instrument hyperlink)
   → review lifecycle, timestamps, status transitions.
3. Check placed_by internally:
   └─ ADMINSQF or starts with "rms" → route to Rule 7 (RMS square-off).
4. If customer asks about a previous day's order
   → use kite_order_history instead.
```

### Route

```
Intent / Condition                                          → Rule
──────────────────────────────────────────────────────────────────────
Order complete — execution details / price questions        → Rule 1
Order open / pending                                        → Rule 2
Order cancelled                                             → Rule 3
Order rejected                                              → Rule 4
AMO query                                                   → Rule 5
Product conversion query                                    → Rule 6
RMS / admin square-off                                      → Rule 7
"I didn't place this order"                                 → Rule 8
Circuit / ban period impact                                 → Rule 9
Order book display issues                                   → Rule 10
```

### Scope

- Address the client's query about today's orders — status, execution, rejections, and conversions.
- Use **A2** field rules and client-facing terminology in all client communication.
- For historical orders, redirect to `kite_order_history`.

### Fallback

If no route matches, investigate using Order History sub-view and Section A reference data. If no root cause is found, escalate per **A17**.

---

## Section C: Rules

---

### Rule 1 — Order Complete

1. Respond per **A18-R1**.
2. If client questions execution price:
   a. Market order → respond per **A18-R2**.
   b. Limit order executed at better price → respond per **A18-R3**.
   c. Client wanted to buy at breakout price (not immediately) → respond per **A18-R5**. Invoke `kite_gtt` if client wants to set up GTT.
   d. SL trigger seems "wrong" → respond per **A18-R4**.
3. If `filled_quantity` < `total_quantity` → partial fill. Check `cancelled_quantity`. IOC orders: unfilled portion auto-cancelled.
4. If client asks where bought shares are → invoke `kite_holdings` (settled) or `kite_positions` (today's buy).

---

### Rule 2 — Order Open / Pending

1. Limit order → respond per **A18-R6**.
2. Circuit hit → respond per **A18-R7**. Auto-cancel times per **A8**.
3. SL/SL-M trigger not yet hit → respond per **A18-R8**.
4. SL-M orders with trigger outside circuit limits stay open without rejection — normal exchange behavior.

---

### Rule 3 — Order Cancelled

1. Check Order History sub-view for cancellation timing and context:
   a. Cancelled near market close → respond per **A18-R9**. Times per **A8**. Invoke `kite_gtt` if client wants persistent order.
   b. LPP range cancellation → respond per **A18-R10**.
   c. IOC partial fill + cancel → respond per **A18-R11**.
   d. Cancelled by user → respond per **A18-R12**.

---

### Rule 4 — Order Rejected

1. Read `rejection_reason` and match against **A12**.
2. For margin rejections:
   a. Check if the client has multiple pending sell orders for the same instrument. If multiple sell orders exist against a single position, the excess orders are treated as fresh short positions requiring margin — respond per **A18-R25**.
   b. Invoke `kite_margins`. Check `opening_balance` first. If `opening_balance` is negative, this is the primary cause — respond per **A18-R24**. Include the `opening_balance` amount. If `option_premium` is also negative, include the option premium context per **A18-R24**.
   c. If `opening_balance` is not negative, identify the specific margin shortfall from the remaining fields (`available_margin`, `used_margin`, `available_cash`).
3. For market order blocks → match against **A10**, respond with reason + resolution.
4. For MIS blocks → match against **A11**, respond with reason + resolution.
5. For quantity/value limits → refer to **A7**.
6. For trigger price errors, ban period, OI restrictions, BSE SL-M, exchange restricted, MTF conflicts → use matching row in **A12**.
7. For CO on ETF or other restricted instruments → use matching row in **A12**.
8. For invalid quantity / odd lot from lot size revision → use matching row in **A12**. Redirect to `kite_positions` Rule 10 for full guidance on holding until expiry and cash settlement.
9. For any rejection not matching **A12** → share the `rejection_reason` text verbatim and suggest retrying or contacting support.

---

### Rule 5 — AMO (After Market Orders)

1. General AMO query → respond per **A18-R14**. Details per **A14**.
2. AMO market order for index options rejected → respond per **A18-R15**.
3. AMO became limit order → respond per **A18-R16**.

---

### Rule 6 — Product Conversion

1. Check conversion rules per **A15**.
2. If margin insufficient for conversion → invoke `kite_margins`.

---

### Rule 7 — RMS / Admin Square-Off

1. `placed_by` = ADMINSQF or starts with "rms" (per **A13**).
2. Invoke `kite_margins` to check for margin shortfall.
3. Check if product was MIS and time was near auto square-off window (per **A9**).
4. Check if account had negative cash balance.
5. Respond per **A18-R13**. Include margin data from `kite_margins` if available.
6. If client asks about the squared-off position → invoke `kite_positions`.

---

### Rule 8 — Unauthorized Order ("I didn't place this")

1. Check `placed_by`:
   a. ADMINSQF or starts with "rms" → apply Rule 7 (RMS square-off).
   b. Client's own ID → escalate to escalation team immediately.

---

### Rule 9 — Circuit / Ban Period Impact

1. Can't exit at circuit → respond per **A18-R23**. If client asks about resulting position → invoke `kite_positions`.
2. Ban period → respond per **A18-R21**. Only exit allowed. Restriction lifts when OI falls below 80% of market-wide limit. If the client asks what specific trades are permitted during the ban (delta exposure rules) → redirect to `kite_positions` Rule 11.

---

### Rule 10 — Order Book Display Issues

1. Rejected order not in order book → respond per **A18-R17**.
2. Downloaded file shows dates instead of quantities → respond per **A18-R18**.
3. Execution time beyond market hours → respond per **A18-R19**.
