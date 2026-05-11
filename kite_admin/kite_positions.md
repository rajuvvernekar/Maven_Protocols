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

TAGS: holdings, margins

## Protocol

# KITE POSITIONS PROTOCOL

## Section A: Reference Data

### A1 — Fundamentals

-CNC buy on the same day appears in Positions → moves to Holdings on T+1.

-Net position = actual current portfolio (overnight + today's trades). Day position = only today's trading activity.

-P&L in positions includes both realised (closed trades) and unrealised (open trades), calculated from original entry price. Multiple trades in same instrument same day: buy avg calculated across ALL trades, not just current position — can show profit even if current buy avg > LTP.

-Zerodha does not square off for freak trades — unrealised loss lasts only a fraction of a second.

### A2 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |
|---|---|
| `instrument_name` | Tradingsymbol |
| `product` | CNC/MIS/NRML/MTF/CO |
| `exchange` | Exchange |
| `quantity` | Quantity |
| `overnight_quantity` | Carry-forward qty |
| `avg_price` | Position avg price |
| `pnl` | P&L |
| `buy_quantity` | Buy quantity |
| `buy_value` | Buy value |
| `buy_average_price` | Buy avg |
| `sell_quantity` | Sell quantity |
| `sell_value` | Sell value |
| `sell_average_price` | Sell avg |
| `last_close_price` | Previous close |
| `net_change_percentage` | Net % change |
| `ltp` | Current market price |

**Non-shareable:**

| Field | Interpretation |
|---|---|
| `day_buy_quantity` | Internal — describe outcomes in plain language |
| `day_buy_price` | Internal |
| `day_sell_quantity` | Internal |
| `day_sell_price` | Internal |
| `day_sell_value` | Internal |

### A3 — P&L Timing Rules

| Time Window | Equity P&L Source | F&O P&L Source |
|---|---|---|
| Market hours (9:15 AM – 3:30 PM) | LTP | LTP |
| After 3:30 PM | Exchange closing price | LTP at 3:30 PM |
| Next day before 9:15 AM | Previous close | Previous close |
| 6:30–7:00 AM (F&O only) | — | Settlement prices update (BHAVCOPY from NSE) |

-Settlement price = 0 for OTM options regardless of LTP — this is normal.

-Funds page uses MTM settlement price for futures/short options — will differ from positions P&L.

### A4 — Auto Square-Off

| Segment | Time |
|---|---|
| Equity | 3:25 PM |
| Equity F&O | 3:26 PM |
| MCX | 10 min before market close (Nov–Mar: 11:55 PM; Mar–Nov: 11:30 PM — shifts with US DST) |

-Charge: ₹50 + 18% GST per order squared off.

-Failure reasons: System/link failure, stock at circuit limit, connectivity issues.

-Failure consequence: MIS converts to CNC (equity) or NRML (F&O). Client responsible for closing. Zerodha may square off at discretion without margin call.

### A5 — Product Conversion Rules

| Conversion | Allowed? | Notes |
|---|---|---|
| MIS ↔ CNC (equity) | Yes | Requires sufficient margin. Sell MIS→CNC also requires holdings. |
| MIS ↔ NRML (F&O/commodity) | Yes | Requires sufficient margin. |
| CNC ↔ NRML | N/A | Not applicable. |
| CO → anything | No | Cover Order positions cannot be converted. |
| Agricultural commodity → MIS | No | Blocked 1 day before tender period (cardamom, mentha oil). |

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

-This margin is blocked progressively for ITM stock options and futures positions approaching expiry. It can cause the available cash / fund balance to go negative.

### A7 — Margin Shortfall & Penalty

- Causes: Exiting hedge leg (remaining leg needs full margin), expiry of hedge leg, MTM loss exceeding 50% of funds, pledged stock value drop, haircut increase.
- Margin call: SMS + email + voice message. Add funds by 11:59 PM same day (after hours) or immediately (before hours).
- Penalty rate: 0.5% of shortfall (< ₹1L), 1% (≥ ₹1L). Up to 5% for 3+ instances/month.
- Snapshots: 4 random intraday snapshots (all segments except commodity). 8 for commodity. Peak margin penalty if snapshot catches one leg open.

### A8 — Hedged Positions

- Cannot close hedge leg unless sufficient margin for remaining unhedged position.
- Hedged margin < unhedged margin. Closing low-risk leg increases margin requirement.
- Order sequence matters: buy hedge first → lower margin. Sell/short first → full margin until hedge placed.

### A9 — Circuit Limit Impact on MIS

| Scenario | Consequence |
|---|---|
| MIS sell + upper circuit | Cannot buy back → converts to delivery. No shares in demat → short delivery + auction penalty. |
| MIS buy + lower circuit | Cannot sell → converts to CNC. Must maintain margin for delivery. |

### A10 — Profit Availability

| Source | When Available |
|---|---|
| Delivery sale proceeds | 100% available for new trades same day (stocks or F&O) |
| NRI Non-PIS delivery sale | 75% same day; remaining 25% available T+1 |
| BTST (T1 holdings) sale | Proceeds available from next trading day only |
| Intraday profits (equity/F&O) | Not usable on T day. Available after T+1 settlement. |
| Options sold/exited | Usable only for buying options in same segment same day. Available for all trades from T+1. |

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

### A12 — Escalation Data

-Include when escalating to human agent: client ID, instrument_name, product type, and specific issue.

### A13 — F&O Ban Period Delta Rules

When a stock enters F&O ban period, fresh positions that increase net delta exposure are blocked. Positions that reduce or offset delta exposure are permitted. Exit of existing positions is always allowed.

| Position Held | Allowed (Reduces Delta) | Blocked (Increases Delta) |
|---|---|---|
| Long calls | Sell calls, buy puts | Buy more calls, sell puts |
| Long puts | Sell puts, buy calls | Buy more puts, sell calls |
| Short calls | Buy calls, sell puts | Sell more calls, buy puts |
| Short puts | Sell puts, buy calls | Buy more puts, sell calls |
| Long futures | Sell futures, buy puts, sell calls | Buy more futures, buy calls, sell puts |
| Short futures | Buy futures, buy calls, sell puts | Sell more futures, sell calls, buy puts |

## Section B: Decision Flow

### Routing

```
Route by scenario
   ├─ P&L questions (unexpected profit, post-3:30, funds mismatch) → Rule 1
   ├─ Net vs day position confusion → Rule 2
   ├─ Auto square-off query → Rule 3
   ├─ Product conversion query → Rule 4
   ├─ Hedged positions & margin → Rule 5
   ├─ Margin call / shortfall / penalty → Rule 6
   ├─ F&O expiry & physical settlement → Rule 7
   ├─ Sold holdings showing as negative positions → Rule 8
   ├─ When are profits available → Rule 9
   ├─ Odd-lot quantity from lot size revision → Rule 10
   ├─ F&O ban period — what trades are allowed → Rule 11
   ├─ Position not found → Rule 12
   └─ Client references previous-day trades → Rule 12
```

### Fallback

If no root cause found after completing all diagnostic steps → escalate to human agent per **A12**.

## Section C: Rules

### Rule 1 — P&L Questions

1. Profit when buy avg > LTP → Per **A1**, buy average spans all same-day trades in the instrument — realised profit from earlier trades is included.
2. P&L changed after 3:30 PM / before market → Per **A3**, P&L source changes after 3:30 PM and again when BHAVCOPY arrives.
3. Positions P&L ≠ funds page → Per **A3**, positions and funds page use different P&L calculations. If client wants funds breakdown → invoke `kite_margins`.
4. Settlement price = 0 for options → option expired OTM. Per **A3**, settlement price = 0 is normal. Settlement price is based on the underlying's weighted average in the last 30 minutes.

### Rule 2 — Net vs Day Positions

1. Per **A1**, net includes carry-forward + today's trades; day = today's activity only. Example: carried forward 75 NIFTY FUT and squared off today → net shows 0, day shows -75.

### Rule 3 — Auto Square-Off

1. Position squared off → check `product` = MIS or CO. Intraday positions auto-squared off per **A4**. Invoke `kite_orders` to show the order. To avoid, close intraday positions before square-off time.
2. Position NOT squared off (carried forward) → Per **A4**, MIS can fail to square off and carry forward — client responsible for closing. Invoke `kite_margins` to check margin sufficiency.
3. Circuit limit impact on MIS:
   a. Sell + upper circuit → MIS sell at upper circuit cannot buy back → converts to delivery. If no shares in demat, short delivery and auction penalties per **A9**.
   b. Buy + lower circuit → MIS buy at lower circuit converts to CNC; must maintain delivery margin per **A9**.
   c. If client asks about holdings for delivery → invoke `kite_holdings`.

### Rule 4 — Product Conversion

1. MIS ↔ CNC or MIS ↔ NRML → convert via Kite: Positions → tap/click on position → Convert Position. Requires sufficient margin per **A5**. If margin insufficient → invoke `kite_margins`.
2. CO conversion → Per **A5**, CO cannot be converted — communicate.
3. Agricultural commodity restriction → Per **A5**, communicate restriction.

### Rule 5 — Hedged Positions & Margin

1. Can't close hedge leg → need sufficient margin to cover remaining unhedged position. Closing hedge leg increases margin requirement per **A8**. Options: add funds first, or exit both legs simultaneously. Invoke `kite_margins` to check `available_margin` and `used_margin`.
2. Peak margin penalty from exiting one leg → Per **A7**, peak margin penalty may apply from snapshot timing.

### Rule 6 — Margin Call / Shortfall / Penalty

1. Margin call received → Per **A7**, communicate deadline. Invoke `kite_margins` for current shortfall.
2. Margin penalty charged → Per **A7**, communicate penalty rate.
3. Shortfall despite positions closed → Per **A7**, snapshot captured shortfall at that moment — closure after snapshot does not remove the penalty.

### Rule 7 — F&O Expiry & Physical Settlement

1. Check whether instrument is index or stock F&O. NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, SENSEX, or any index → cash-settled. ITM index options auto-exercised; P&L settled in cash. OTM/ATM expire worthless. Physical delivery rules (Steps 2, 3, 5, 6, 7) apply only to stock F&O.
2. Stock F&O ITM → compulsory physical delivery. Need full cash or shares. Stocks credited T+1 after expiry. If client asks about delivery shares → invoke `kite_holdings`.
3. Stock F&O OTM → expires worthless. No delivery obligation, no action needed.
4. Index F&O → cash-settled. ITM auto-exercised; P&L settled in cash. OTM/ATM expire worthless.
5. OTM buy blocked near expiry → Per **A6**, fresh long OTM stock option positions blocked — communicate.
6. Higher margins near expiry → Per **A6**, share delivery margin schedule. Reference physical settlement policy per **A11**. Invoke `kite_margins` for current `delivery_margin`.
7. Balance went negative due to physical delivery margin near expiry:
   a. Invoke `ledger_report` and check `remarks` for "Physical delivery margin blocked for long options in NSE F&O" with corresponding `debit` to confirm delivery margin was the cause.
   b. If found → physical delivery margin blocked for ITM stock option position approaching expiry. Share margin schedule from **A6** and the debit amount. Reference physical settlement policy per **A11**.
   c. If not found → invoke `kite_margins` to investigate other causes of negative balance. If no cause identified → escalate to human agent per **A12**.

### Rule 8 — Sold Holdings as Negative Positions

1. Selling shares from holdings during the day shows as a negative position tagged HOLDING in Positions. Normal. Allows intraday traders to buy back. If no rebuy, ignore. Shares debited from demat by EOD per **A1**.
2. If client asks about holdings status → invoke `kite_holdings`.

### Rule 9 — Profit Availability

1. Check `client_acc_type`, `pis_bank_1_name`, `pis_bank_2_name`, `pis_bank_3_name` from `get_all_client_data` — if NRI non-PIS per **A10**, apply NRI Non-PIS row from **A10**.
2. Apply applicable row from **A10** based on trade type. Intraday profits from equity and F&O are available only after T+1 settlement — cannot be used same day. Share same-day profits link from **A11** if questioned.
3. If client asks why balance doesn't reflect profit → invoke `kite_margins` to show `available_margin` and explain T+1 settlement.

### Rule 10 — Odd-Lot Quantity from Lot Size Revision

1. If client has residual F&O quantity that does not match current lot size and cannot be squared off (e.g., "invalid quantity", unable to exit remaining quantity after lot size revision):
   a. Per SEBI's revised lot sizes for index derivative contracts effective December 30, 2025, the existing position has a residual quantity that does not match the current lot size. Odd-lot quantity cannot be traded on exchange. Hold until expiry — cash-settled based on moneyness. 5% extra margin applies on odd lots. Lot size revision and options-on-expiry-day links per **A11**.
   b. Odd-lot quantity must be held until contract expiry; cash-settled based on moneyness.
   c. 5% extra margin applies on odd-lot positions.
2. If client asks about margin for odd-lot position → invoke `kite_margins`.

### Rule 11 — F&O Ban Period (Delta Exposure Rules)

1. If client holds F&O position in a stock in ban period and asks what trades are permitted:
   a. Identify position type (long/short calls/puts/futures) from `kite_positions`.
   b. Per **A13**, tailor permitted/blocked trades to actual position held. Once OI falls below 80% of market-wide limit, all trades will be allowed again.
2. If order rejected due to ban period → invoke `kite_orders` to confirm rejection reason. Apply **A13** delta context.
3. If client asks when ban will lift → OI must fall below 80% of market-wide position limit. Direct client to bulletin per **A11** for current ban list.

### Rule 12 — Position or Order Not Found

1. Invoke `kite_order_history` — check if position was squared off today, or locate previous-day trade records.
2. Invoke `kite_holdings` — check if CNC position moved to holdings.
3. If still not found: confirm Privacy Mode is off in Kite settings.
4. If still not found after steps 1–3 → escalate to human agent per **A12**.
