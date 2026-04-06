# kite_positions

## Description

WHEN TO USE:

When clients:
- Ask about current open positions (intraday MIS/CO, F&O NRML, or same-day delivery CNC)
- Report position showing profit when buy average is higher than LTP or vice versa (multiple trades in same instrument, realised P&L included)
- Report P&L mismatch between positions page and funds page (entry price vs MTM settlement price)
- Report P&L changed after 3:30 PM, after market hours, or before market opens next day (closing price switch, BHAVCOPY update)
- Ask about net vs day positions (difference between actual portfolio and today's trading activity)
- Ask about auto square-off (why it happened, timings, charges ₹50 + GST)
- Report auto square-off failure (MIS position carried forward as CNC/NRML, circuit limit impact)
- Ask about circuit limit impact on MIS (upper circuit on sell position, lower circuit on buy position)
- Report can't close hedge leg due to margin requirement increase on remaining leg
- Ask about peak margin penalty from exiting one leg of a hedge
- Ask about product conversion (MIS↔CNC, MIS↔NRML allowed with margin, CO conversion blocked)
- Ask about margin call, margin shortfall, or margin penalty on open positions
- Ask about F&O expiry (physical settlement for ITM stock options/futures, OTM expiring worthless, index F&O cash-settled)
- Report settlement price showing 0 for options (OTM — normal regardless of LTP)
- Ask about higher margins blocked close to expiry (4 days before for ITM long options, expiry day for futures/short options)
- Ask why fresh OTM stock option buy blocked in last 2 days before expiry
- Report sold holdings appearing as negative positions during the day (tagged HOLDING — normal)
- Ask about overnight quantity or carry-forward positions
- Ask about margin shown when exiting a position (increase in utilised portfolio margin — order still executes)
- Ask when intraday/F&O profits, delivery sale proceeds, BTST proceeds, or option premium become available
- Ask about NRI Non-PIS sale proceeds availability (75% same day, rest T+1)

TRIGGER KEYWORDS: "position", "open position", "intraday", "MIS", "NRML", "carry forward", "overnight", "square off", "squared off", "auto square off", "P&L positions", "MTM", "mark to market", "margin call", "margin shortfall", "margin penalty", "hedged position", "convert position", "conversion", "expiry", "physical settlement", "physical delivery", "ITM expiry", "OTM expiry", "settlement price", "net position", "day position", "negative position", "profit available", "withdrawal after selling", "circuit limit position", "CO conversion", "BTST proceeds", "option premium available"

## Protocol

# KITE POSITIONS PROTOCOL 

---

## Section A: Reference Data

---

### A1 — Tool Purpose & Fundamentals

This tool shows **open trades for the current day**: intraday (MIS/CO), F&O (NRML), and same-day delivery (CNC). Holdings = settled shares in demat (separate tool).

CNC buy on the same day appears in Positions → moves to Holdings on T+1.

**Net position** = actual current portfolio (overnight + today's trades). **Day position** = only today's trading activity.

P&L in positions includes both realised (closed trades) and unrealised (open trades), calculated from original entry price. Multiple trades in same instrument same day: buy avg calculated across ALL trades, not just current position — can show profit even if current buy avg > LTP.

Zerodha does not square off for freak trades — unrealised loss lasts only a fraction of a second.

**Input:** Client ID.

---

### A2 — Field Usage Rules

**Shareable fields:**

`instrument_name` | `product` | `exchange` | `quantity` | `overnight_quantity` | `avg_price` | `pnl` | `buy_quantity` | `buy_value` | `buy_average_price` | `sell_quantity` | `sell_value` | `sell_average_price` | `last_close_price` | `net_change_percentage`

**Internal-only fields** (use for reasoning; communicate outcomes in plain language):

`ltp` | `day_buy_quantity` | `day_buy_price` | `day_sell_quantity` | `day_sell_price` | `day_sell_value`

**Client-facing terminology:**

| Internal Term | Client-Facing Alternative |
|---|---|
| `ltp` | "current market price" |
| `day_buy_*` / `day_sell_*` fields | (use for internal calculations; describe outcomes in plain language) |

---

### A3 — P&L Timing Rules

| Time Window | Equity P&L Source | F&O P&L Source |
|---|---|---|
| Market hours (9:15 AM – 3:30 PM) | LTP | LTP |
| After 3:30 PM | Exchange closing price | LTP at 3:30 PM |
| Next day before 9:15 AM | Previous close | Previous close |
| 6:30–7:00 AM (F&O only) | — | Settlement prices update (BHAVCOPY from NSE) |

Settlement price = 0 for OTM options regardless of LTP — this is normal.

Funds page uses MTM settlement price for futures/short options — will differ from positions P&L.

---

### A4 — Auto Square-Off

| Segment | Time |
|---|---|
| Equity | 3:25 PM |
| Equity F&O | 3:26 PM |
| MCX | 10 min before market close (Nov–Mar: 11:55 PM; Mar–Nov: 11:30 PM — shifts with US DST) |

**Charge:** ₹50 + 18% GST per order squared off.

**Failure reasons:** System/link failure, stock at circuit limit, connectivity issues.

**Failure consequence:** MIS converts to CNC (equity) or NRML (F&O). Client responsible for closing. Zerodha may square off at discretion without margin call.

---

### A5 — Product Conversion Rules

| Conversion | Allowed? | Notes |
|---|---|---|
| MIS ↔ CNC (equity) | Yes | Requires sufficient margin. Sell MIS→CNC also requires holdings. |
| MIS ↔ NRML (F&O/commodity) | Yes | Requires sufficient margin. |
| CNC ↔ NRML | N/A | Not applicable. |
| CO → anything | No | Cover Order positions cannot be converted. |
| Agricultural commodity → MIS | No | Blocked 1 day before tender period (cardamom, mentha oil). |

---

### A6 — Expiry & Physical Settlement

| Scenario | Outcome |
|---|---|
| Stock F&O — ITM | Compulsory physical delivery of underlying stock. Stocks credited T+1. Short delivery: up to T+2. |
| Stock F&O — OTM | Expire worthless — no obligation. |
| Index F&O | Cash-settled (no physical delivery). ITM auto-exercised. OTM/ATM expire worthless. |
| Margin increase | 4 days before expiry for ITM long options. Expiry day for futures/short options. |
| Fresh OTM long buy blocked | Last 2 days before expiry for stock options (physical settlement risk). |

**Physical delivery margin schedule (stock F&O expiry week):**

| Day | Margin Requirement |
|---|---|
| E-4 (Wednesday) | 10% of (VaR + ELM + Adhoc) |
| E-3 (Thursday) | 25% of (VaR + ELM + Adhoc) |
| E-2 (Friday) | 45% of (VaR + ELM + Adhoc) |
| E-1 (Monday) | 25% of contract value |
| Expiry day (Tuesday) | 50% of contract value |

This margin is blocked progressively for ITM stock options and futures positions approaching expiry. It can cause the available cash / fund balance to go negative if insufficient funds are available.

**Ledger verification:** If client reports negative balance near expiry, invoke `ledger_report` and check `remarks` for "Physical delivery margin blocked for long options in NSE F&O" with the corresponding `debit` entry to confirm delivery margin was the cause.

**Reference:** [Physical settlement policy](https://support.zerodha.com/category/trading-and-markets/trading-faqs/f-otrading/articles/policy-on-physical-settlement)

---

### A7 — Margin Shortfall & Penalty

**Causes:** Exiting hedge leg (remaining leg needs full margin), expiry of hedge leg, MTM loss exceeding 50% of funds, pledged stock value drop, haircut increase.

**Margin call:** SMS + email + voice message. Add funds by 11:59 PM same day (after hours) or immediately (before hours).

**Penalty rate:** 0.5% of shortfall (< ₹1L), 1% (≥ ₹1L). Up to 5% for 3+ instances/month.

**Snapshots:** 4 random intraday snapshots (all segments except commodity). 8 for commodity. Peak margin penalty if snapshot catches one leg open.

---

### A8 — Hedged Positions

- Cannot close hedge leg unless sufficient margin for remaining unhedged position.
- Hedged margin < unhedged margin. Closing low-risk leg increases margin requirement.
- Order sequence matters: buy hedge first → lower margin. Sell/short first → full margin until hedge placed.

---

### A9 — Circuit Limit Impact on MIS

| Scenario | Consequence |
|---|---|
| MIS sell + upper circuit | Cannot buy back → converts to delivery. No shares in demat → short delivery + auction penalty. |
| MIS buy + lower circuit | Cannot sell → converts to CNC. Must maintain margin for delivery. |

---

### A10 — Profit Availability

| Source | When Available |
|---|---|
| Delivery sale proceeds | 100% available for new trades same day (stocks or F&O) |
| NRI Non-PIS delivery sale | 75% same day; remaining 25% available T+1 |
| BTST (T1 holdings) sale | Proceeds available from next trading day only |
| Intraday profits (equity/F&O) | Not usable on T day. Available after T+1 settlement. |
| Options sold/exited | Usable only for buying options in same segment same day. Available for all trades from T+1. |

**Reference:** [Why are same-day profits not available for trading?](https://support.zerodha.com/category/trading-and-markets/margins/margin-leverage-and-product-and-order-types/articles/same-day-profits)

---

### A11 — Links

| Topic | URL |
|---|---|
| Short delivery info | https://support.zerodha.com/category/trading-and-markets/trading-faqs/general/articles/what-is-short-delivery-and-what-are-its-consequences |
| Margin calculator | https://zerodha.com/margin-calculator |
| Bulletin (restrictions) | https://zerodha.com/marketintel/bulletin |
| Approved securities | https://zerodha.com/approved-securities#tab-noncash_equity |
| Physical settlement policy | https://support.zerodha.com/category/trading-and-markets/trading-faqs/f-otrading/articles/policy-on-physical-settlement |
| Lot size revision bulletin | https://zerodha.com/marketintel/bulletin/429705/revision-in-lot-size-of-index-derivative-contracts-from-december-30-2025 |
| Options on expiry day | https://support.zerodha.com/category/trading-and-markets/trading-faqs/f-otrading/articles/options-on-expiry-day |
| Same-day profits | https://support.zerodha.com/category/trading-and-markets/margins/margin-leverage-and-product-and-order-types/articles/same-day-profits |

---

### A12 — Escalation Data Template

When escalating, always include: **client ID, instrument_name, product type, and specific issue.**

---

### A13 — Response Templates

**R1 — Profit when buy avg > LTP:**
"When you make multiple trades in the same stock during the day, Kite calculates buy average across ALL trades — not just your current position. Your realised profit from earlier trades is included, which can show overall profit even if the current position's entry price is above the market price."

**R2 — P&L changed after 3:30 PM / before market:**
"After 3:30 PM, equity P&L switches to the exchange closing price. For F&O, settlement prices update between 6:30–7:00 AM next day when the exchange sends the BHAVCOPY. This commonly causes P&L to shift."

**R3 — Positions P&L ≠ funds page:**
"The Positions page calculates P&L from your original entry price. The Funds page uses the MTM (Mark-to-Market) settlement price for futures and short options. These are different calculations — the funds page reflects what's actually settled in your account."

**R4 — Settlement price = 0:**
"A settlement price of 0 means your option expired OTM (Out of The Money). This is normal regardless of what the LTP was — the settlement price is based on the underlying's weighted average in the last 30 minutes."

**R5 — Net vs day positions:**
"Net position shows your actual current portfolio after combining overnight carry-forward and today's trades. Day position shows only today's trading activity. Example: if you carried forward 75 NIFTY FUT and squared off today — net shows 0 (current state), day shows -75 (today's sell action)."

**R6 — Auto square-off explanation:**
"Intraday positions are auto-squared off at [time per A4]. Auto square-off charge: ₹50 + GST per order. To avoid this, close intraday positions before the square-off time."

**R7 — Auto square-off failed (carried forward):**
"Auto square-off can fail due to: circuit limits hit, system issues, or connectivity problems. Your MIS position has been converted to [CNC for equity / NRML for F&O] and carried forward. You must close it yourself. Ensure sufficient margin is available — Zerodha may square off at its discretion."

**R8 — Circuit + MIS sell (upper circuit):**
"If your MIS sell position hits upper circuit — you can't buy back, so it converts to delivery. If you don't have shares in your demat, this results in short delivery and auction penalties."

**R9 — Circuit + MIS buy (lower circuit):**
"If your MIS buy position hits lower circuit — it converts to CNC and you must maintain delivery margin."

**R10 — Conversion guidance:**
"You can convert via Kite: Positions → tap/click on position → Convert Position. Requires sufficient margin for the target product type."

**R11 — CO cannot convert:**
"Cover Order positions cannot be converted to any other product type."

**R12 — Agricultural commodity restriction:**
"Agricultural commodity contracts (cardamom, mentha oil) cannot be converted to MIS one day before the tender period starts."

**R13 — Can't close hedge leg:**
"You need sufficient margin to cover the remaining unhedged position. Closing the hedge leg increases your margin requirement. Options: add funds first, or exit both legs simultaneously."

**R14 — Peak margin penalty from closing one leg:**
"Even if you close both legs, the exchange takes random intraday snapshots (4 for equity F&O, 8 for commodity). If a snapshot catches one leg open, you may face a penalty."

**R15 — Margin call received:**
"Add funds by 11:59 PM same day (if received after hours) or immediately (if before hours). If not resolved, Zerodha may square off positions at its discretion."

**R16 — Margin penalty charged:**
"Exchange imposes margin penalty when insufficient margin is detected during intraday snapshots or at end of day. Penalty: 0.5% for shortfall under ₹1 lakh, 1% for ₹1 lakh+, up to 5% for 3+ instances in a month."

**R17 — Shortfall despite positions closed:**
"Shortfall can occur from intraday snapshots taken while your position was still open. Even if you closed it later, the snapshot captured the shortfall at that moment."

**R18 — Stock F&O ITM expiry:**
"ITM stock options and futures result in compulsory physical delivery. You need full cash or shares. Stocks credited T+1 after expiry. Margins increase 4 days before expiry for ITM long options and on expiry day for futures/short options."

**R19 — Stock F&O OTM expiry:**
"OTM stock options expire worthless — no delivery obligation, no action needed."

**R20 — Index F&O expiry:**
"Index options and futures are cash-settled. ITM index options are auto-exercised; P&L settled in cash. OTM/ATM expire worthless."

**R21 — OTM buy blocked near expiry:**
"Fresh long OTM stock option positions are blocked in the last 2 days before expiry due to physical settlement risk."

**R22 — Higher margins near expiry:**
"Margin requirements increase as contracts approach expiry and physical delivery. The physical delivery margin schedule is: E-4 (Wed) 10% of VaR+ELM+Adhoc, E-3 (Thu) 25%, E-2 (Fri) 45%, E-1 (Mon) 25% of contract value, Expiry day (Tue) 50% of contract value. For more details: [Physical settlement policy](https://support.zerodha.com/category/trading-and-markets/trading-faqs/f-otrading/articles/policy-on-physical-settlement)"

**R23 — Sold holdings as negative positions:**
"When you sell shares from holdings during the trading day, they appear as a negative position tagged HOLDING in Positions. This is normal — allows intraday traders to buy back. If you don't intend to rebuy, ignore it. Shares debited from demat by end of day."

**R24 — Margin shown when exiting:**
"The margin shown when exiting a position reflects the increase in your utilised portfolio margin, not a charge. Your order will execute regardless."

**R25 — Balance negative due to physical delivery margin:**
"Your balance went negative because physical delivery margin has been blocked for your ITM stock option position approaching expiry. The margin increases progressively: E-4 (Wed) 10% of VaR+ELM+Adhoc, E-3 (Thu) 25%, E-2 (Fri) 45%, E-1 (Mon) 25% of contract value, Expiry day (Tue) 50% of contract value. For more details: [Physical settlement policy](https://support.zerodha.com/category/trading-and-markets/trading-faqs/f-otrading/articles/policy-on-physical-settlement)"

**R26 — Odd-lot quantity from lot size revision:**
"Due to SEBI's revised lot sizes for index derivative contracts effective December 30, 2025, your existing position has a residual quantity that does not match the current lot size. This odd-lot quantity cannot be traded on the exchange. You must hold this position until expiry, and it will be cash-settled based on the moneyness of the option at expiry. A 5% extra margin applies on odd lots. For details on the lot size revision: [Lot size revision bulletin](https://zerodha.com/marketintel/bulletin/429705/revision-in-lot-size-of-index-derivative-contracts-from-december-30-2025). For details on options settlement at expiry: [Options on expiry day](https://support.zerodha.com/category/trading-and-markets/trading-faqs/f-otrading/articles/options-on-expiry-day)"

---

## Section B: Decision Flow

---

### Preflight (run on every query)

```
1. Search kite_positions by instrument_name.
2. If found:
   └─ Note product, quantity, overnight_quantity, avg_price, pnl,
      buy_quantity, sell_quantity.
3. If NOT found + client says "I have a position":
   ├─ Check if already squared off today (quantity = 0 with buy/sell history)
   ├─ Or it's a holdings query → invoke kite_holdings
   └─ If client says positions/P&L are hidden or not visible on screen
      → Privacy Mode may be enabled. Steps: Click on user ID (top-right
        on Kite web, or profile icon on the app) → toggle Privacy Mode off.
```

### Route

```
Intent / Condition                                          → Rule
──────────────────────────────────────────────────────────────────────
P&L questions (unexpected profit, post-3:30, funds mismatch)→ Rule 1
Net vs day position confusion                               → Rule 2
Auto square-off query                                       → Rule 3
Product conversion query                                    → Rule 4
Hedged positions & margin                                   → Rule 5
Margin call / shortfall / penalty                           → Rule 6
F&O expiry & physical settlement                            → Rule 7
Sold holdings showing as negative positions                 → Rule 8
When are profits available                                  → Rule 9
Odd-lot quantity from lot size revision                     → Rule 10
```

### Scope

- Address the client's query about today's open trades — P&L, square-off, conversions, margins, and expiry.
- Use **A2** field rules and client-facing terminology in all client communication.
- For settled holdings queries, redirect to `kite_holdings`. For order-level details, redirect to `kite_orders`.

### Fallback

If no route matches, investigate using Section A reference data. If no root cause is found, escalate per **A12**.

---

## Section C: Rules

---

### Rule 1 — P&L Questions

1. Profit when buy avg > LTP → respond per **A13-R1**.
2. P&L changed after 3:30 PM / before market → respond per **A13-R2**. Timing per **A3**.
3. Positions P&L ≠ funds page → respond per **A13-R3**. If client wants funds breakdown → invoke `kite_margins`.
4. Settlement price = 0 for options → respond per **A13-R4**.

---

### Rule 2 — Net vs Day Positions

1. Respond per **A13-R5**.

---

### Rule 3 — Auto Square-Off

1. Position squared off → check `product` = MIS or CO. Respond per **A13-R6**. Times per **A4**. If client asks about the order → invoke `kite_orders`.
2. Position NOT squared off (carried forward) → respond per **A13-R7**. Invoke `kite_margins` to check margin sufficiency.
3. Circuit limit impact on MIS:
   a. Sell + upper circuit → respond per **A13-R8**. Short delivery risk per **A9**.
   b. Buy + lower circuit → respond per **A13-R9**. Per **A9**.
   c. If client asks about holdings for delivery → invoke `kite_holdings`.

---

### Rule 4 — Product Conversion

1. MIS ↔ CNC or MIS ↔ NRML → respond per **A13-R10**. Rules per **A5**. If margin insufficient → invoke `kite_margins`.
2. CO conversion → respond per **A13-R11**.
3. Agricultural commodity restriction → respond per **A13-R12**.

---

### Rule 5 — Hedged Positions & Margin

1. Can't close hedge leg → respond per **A13-R13**. Rules per **A8**. Invoke `kite_margins` to check available_margin and used_margin.
2. Peak margin penalty from exiting one leg → respond per **A13-R14**. Snapshot rules per **A7**.

---

### Rule 6 — Margin Call / Shortfall / Penalty

1. Margin call received → respond per **A13-R15**. Invoke `kite_margins` for current shortfall.
2. Margin penalty charged → respond per **A13-R16**. Rates per **A7**.
3. Shortfall despite positions closed → respond per **A13-R17**. Snapshot explanation per **A7**.

---

### Rule 7 — F&O Expiry & Physical Settlement

1. Stock F&O ITM → respond per **A13-R18**. Details per **A6**. If client asks about delivery shares → invoke `kite_holdings`.
2. Stock F&O OTM → respond per **A13-R19**.
3. Index F&O → respond per **A13-R20**.
4. OTM buy blocked near expiry → respond per **A13-R21**. Per **A6**.
5. Higher margins near expiry → respond per **A13-R22**. Margin schedule per **A6**. Invoke `kite_margins` for current delivery_margin.
6. Balance went negative due to physical delivery margin near expiry:
   a. Invoke `ledger_report` and check `remarks` for "Physical delivery margin blocked for long options in NSE F&O" with the corresponding `debit` entry.
   b. If found → respond per **A13-R25**. Share the debit amount from the ledger and the margin schedule from **A6**.
   c. If not found → invoke `kite_margins` to investigate other causes of negative balance.

---

### Rule 8 — Sold Holdings as Negative Positions

1. Respond per **A13-R23**.
2. If client asks about holdings status → invoke `kite_holdings`.

---

### Rule 9 — Profit Availability

1. Respond with the applicable row from **A10** based on the trade type. Intraday profits from equity and F&O trades are available only after T+1 settlement — they cannot be used for trading on the same day. Share the same-day profits link from **A11** if the client questions this.
2. If client asks why balance doesn't reflect profit → invoke `kite_margins` to show available_margin and explain T+1 settlement.
3. If client asks about order execution details → invoke `kite_orders`.
4. If client asks about historical trades → invoke `kite_order_history`.

---

### Rule 10 — Odd-Lot Quantity from Lot Size Revision

1. If client has a residual F&O quantity that does not match the current lot size and cannot be squared off (e.g., "invalid quantity" error, unable to exit remaining quantity after lot size revision):
   a. Respond per **A13-R26**.
   b. The odd-lot quantity must be held until contract expiry. It will be cash-settled based on the moneyness of the option at expiry.
   c. A 5% extra margin applies on odd-lot positions.
2. If client asks about margin for the odd-lot position → invoke `kite_margins`.
