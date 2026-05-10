# kite_margins

## Description

WHEN TO USE:

When clients:
- Ask about available margin, available cash, used margin, or opening balance values
- Ask what any field on the Kite funds page means (payin, payout, SPAN, exposure, delivery margin, option premium, collateral, M2M)
- Report balance seeming wrong, not matching, or showing an unexpected amount
- Ask why profits from today or yesterday are not reflecting in the balance (T+1 settlement)
- Report account in negative balance or debit (interest charges, consequences, how to resolve)
- Ask about margin shortfall, margin call, or how to avoid margin penalty (CC snapshots, deadline to add funds)
- Ask why margin shortfall exists even after closing positions (peak snapshot already captured)
- Ask about collateral margin (liquid collateral, equity collateral, total collateral, 50% cash requirement for F&O)
- Ask about unsettled funds or when profits will be available for trading/withdrawal
- Report used margin showing negative (credit from selling holdings or closing long options)
- Ask about MTM (Mark to Market) — how M2M realised works, daily revaluation of futures, short options margin behavior
- Ask about option premium field showing positive (sold) or negative (bought)
- Ask about free cash calculation or how available margin is computed
- Report difference between Kite positions P&L and funds page P&L (entry price vs MTM settlement price)
- Report opening balance not matching expected amount (T+1 settlement, MTM, charges, holidays)
- Ask about sale proceeds availability (100% same day for holdings since Oct 2024)
- Report available cash rounding on Kite (1 decimal display, full amount withdrawable)
- Report market order causing negative balance (validation vs execution price difference)
- Ask about weekend or holiday payin visibility (appears on Monday)

TRIGGER KEYWORDS: "available margin", "available cash", "opening balance", "used margin", "fund balance", "funds page", "funds tab", "collateral", "SPAN", "exposure margin", "delivery margin", "option premium", "free cash", "negative balance", "debit balance", "margin shortfall", "margin call", "margin penalty", "MTM", "mark to market", "M2M", "unsettled funds", "profit not showing", "yesterday profit", "payin", "payout", "balance incorrect", "balance wrong", "balance mismatch", "margin blocked", "sale proceeds", "interest on negative", "opening balance wrong"

TAGS: margins

## Protocol

# KITE MARGINS PROTOCOL

---

## Section A: Reference Data

---

### A1 — Fundamentals

Positions P&L uses entry price; Funds page uses last MTM settlement price — these may differ intraday. Overall P&L will be the same once positions are closed.

---

### A2 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |  
|---|---|  
| `opening_balance` | Opening balance for the trading day |  
| `available_margin` | Total margin currently available for trading |  
| `used_margin` | Margin blocked against open positions and orders |  
| `available_cash` | Cash component of available margin |  
| `payin` | Funds added to the account today |  
| `payout` | Funds withdrawn from the account today |  
| `span` | SPAN margin requirement for F&O positions |  
| `delivery_margin` | Margin blocked for delivery settlement obligations |  
| `exposure_margin` | Exposure margin requirement for F&O positions |  
| `option_premium` | Net option premium paid or received |  
| `liquid_collateral` | Collateral value from liquid mutual fund pledges |  
| `equity_collateral` | Collateral value from equity share pledges |  
| `total_collateral` | Total collateral value (liquid \+ equity) |  
| `m2m_realised` | Realised MTM P&L for the day from closed positions |

**Non-shareable:**

| Field | Interpretation |  
|---|---|  
| `m2m_unrealised` | Unrealised MTM P&L on open positions — fluctuates intraday until positions are closed |

---

### A3 — Field Definitions

| Field | Definition |  
|---|---|  
| Available Margin | Total funds for trading: cash \+ payin \+ collateral \+ premium received \+ realised P&L − unrealised losses − used margin |  
| Available Cash | Previous day closing balance \+ payin − payout ± day's settled activity. If negative → interest applies per **A5**. Rounded to 1 decimal place on Kite for display; the full amount is withdrawable. |  
| Opening Balance | Previous day's closing balance after reversing blocked margin. Differences from previous close can occur due to: settlement of previous day's trades (T+1), MTM settlement on open F&O positions, charges/brokerage deducted, or settlement holiday delays. |  
| Used Margin | Margin blocked for open positions and orders (pending and executed). Negative when selling holdings or closing long options — the credit received is included in available margin. |  
| Free Cash | Cash Margin Available \+ Pay In \+ Direct Collateral − Margin Used |  
| Payin | Funds added during the day. Weekend payins appear on Monday. |  
| Payout | Funds withdrawn during the day. |  
| Total Collateral | Liquid Collateral \+ Equity Collateral |  
| Liquid Collateral | Pledged LiquidBees/liquid MFs after haircut — treated as cash equivalent. Satisfies the 50% cash requirement per **A6**. |  
| Equity Collateral | Pledged stocks/ETFs/MFs after haircut. Non-cash — attracts 0.035%/day if used beyond the 50% cash limit per **A6**. |  
| Option Premium | Negative when premium is received from selling/writing options; positive when premium is paid for buying. Included in available cash. |  
| SPAN | Margins blocked for F&O portfolios. Exchanges use Standard Portfolio Analysis of Risk (SPAN) to calculate risk. |  
| Exposure | Margin charged over and above SPAN to cover risks that SPAN may not account for (index: 2% of contract value; stock: 3.5% or 1.5 SD). |  
| SPAN \+ Exposure | Initial Margin required by exchange for F&O. |  
| Delivery Margin | T1 sale proceeds \+ physical delivery margin for ITM stock options during expiry week \+ additional MCX margin near expiry. Physical delivery margin increases progressively from 4 days before expiry to expiry day — see **A10** for the full schedule. |  
| M2M Realised | Realised MTM P&L from closed F&O positions. Mark to Market is the daily revaluation of open futures positions at the closing price — profits or losses are settled to the client's account daily. Options do not have MTM settlement. |  
| M2M Unrealised | Unrealised MTM P&L from open F&O positions (internal use only). |

---

### A4 — Customer Language → Field Mapping

| Customer Says | Maps To |  
|---|---|  
| "balance" / "available balance" | `available_margin` or `available_cash` |  
| "margin used" / "blocked margin" | `used_margin` |  
| "collateral" | `liquid_collateral`, `equity_collateral`, or `total_collateral` |  
| "premium" | `option_premium` |  
| "SPAN" / "exposure" | `span`, `exposure_margin` |  
| "delivery margin" | `delivery_margin` |  
| "opening balance" | `opening_balance` |  
| "payin" / "funds added" | `payin` |  
| "payout" / "withdrawal" | `payout` |  
| "MTM" / "M2M" | `m2m_realised` (internal only for unrealised) |

---

### A5 — Negative Balance Rules

| Condition | Consequence |  
|---|---|  
| Negative available cash | Interest: 0.05%/day (18% p.a.) |  
| Negative balance \+ F&O orders | Brokerage: ₹40 per executed F&O order (instead of ₹20) |  
| No funds added / insufficient margins | Positions may be squared off |

---

### A6 — Collateral Rules

| Rule | Detail |  
|---|---|  
| Cash requirement | 50% of F&O margin must be cash or cash-equivalent |  
| Non-cash shortfall charge | 0.035%/day (12.775% p.a.) |  
| Usable for | Equity intraday, futures, options buying and writing |  
| Not usable for | Equity delivery (CNC) purchases |

---

### A7 — Settlement & Availability

| Source | When Available |  
|---|---|  
| Intraday/F&O profits | After T+1 settlement (next trading day). If the next trading/settlement day is a holiday, funds are available the following trading day. |  
| Sale proceeds from holdings (normal CNC) | 100% available same day for all trades (effective Oct 7, 2024) |  
| BTST sale | Funds available from T+1 (next trading day). |

---

### A8 — Links

| Topic | URL |  
|---|---|  
| Margin calculator | https://zerodha.com/margin-calculator |  
| Intraday leverages | https://zerodha.com/marketintel/bulletin/249809/latest-intraday-leverages-mis-bo-co |  
| Approved securities (pledge haircuts) | https://zerodha.com/approved-securities |  
| Physical settlement policy | https://support.zerodha.com/category/trading-and-markets/trading-faqs/f-otrading/articles/policy-on-physical-settlement |

---

### A9 — Escalation Data Template

Escalate to a human agent. Always include: **client ID, current margin values, and specific issue.**

---

### A10 — Physical Delivery Margin Schedule (Stock F&O Expiry Week)

| Day | Margin Requirement |  
|---|---|  
| 4 days before expiry — Wednesday (E-4) | 10% of (VaR \+ ELM \+ Adhoc) |  
| 3 days before expiry — Thursday (E-3) | 25% of (VaR \+ ELM \+ Adhoc) |  
| 2 days before expiry — Friday (E-2) | 45% of (VaR \+ ELM \+ Adhoc) |  
| 1 day before expiry — Monday (E-1) | 25% of contract value |  
| Expiry day — Tuesday | 50% of contract value |

This margin is blocked progressively for ITM stock options and futures positions approaching expiry. It can cause the available cash balance to go negative if insufficient funds are available.

Ledger entry: "Physical delivery margin blocked for long options in NSE F&O"

**Reference:** Physical settlement policy per **A8**.

---

## Section B: Decision Flow

---

### Routing 

```  
Route by scenario  
   ├─ Balance / available margin / cash / option premium inquiry → Rule 1  
   ├─ used_margin < 0 (credit from selling holdings or closing long options) → Rule 1  
   ├─ Profit not showing in balance → Rule 2  
   ├─ available_cash < 0 (negative cash) → Rule 3  
   ├─ Collateral / liquid vs equity / CNC usability → Rule 4  
   ├─ SPAN / exposure / delivery margin query → Rule 5  
   ├─ Payin / payout inquiry → Rule 6  
   ├─ P&L mismatch — positions page vs funds page → Rule 7  
   ├─ Opening balance mismatch → Rule 8  
   ├─ Sale proceeds availability / BTST / same-day trading → Rule 9  
   ├─ Negative balance after market order → Rule 10  
   ├─ MTM explanation → Rule 11  
   └─ Balance negative \+ ITM stock options near expiry → Rule 12  
```

### Fallback

If no root cause is found, escalate to a human agent per **A9**.

---

## Section C: Rules

---

### Rule 1 — Balance Inquiry

1. Share `available_margin`, `available_cash`, `opening_balance`, `used_margin`.  
2. If `option_premium` is non-zero or client asks about it → explain per **A3**.  
3. If `opening_balance` is negative → a negative opening balance blocks all fresh positions. Advise adding funds to clear the deficit. Interest and brokerage consequences per **A5**.  
4. If `used_margin` is negative → the client received credit from selling holdings or closing long options today; the credit is included in available margin.  
   - To confirm holdings sale: invoke `kite_orders` for orders where `type` = SELL and `product` = CNC.  
   - To confirm long option closure: invoke `console_fno_positions`. If `open_quantity` is positive, it was a long position. Then invoke `kite_positions` — if `quantity` = 0 and `overnight_quantity` matches the previous day's `open_quantity`, the long position was closed today.  
5. If client asks why margin is blocked or about a specific order → invoke `kite_orders` and check `filled_quantity` and `average_price` for orders with `order_status` = COMPLETE or OPEN. `filled_quantity × average_price` gives the funds required, which should match `used_margin`.

---

### Rule 2 — Profit Not Showing in Balance

1. Intraday and F&O profits are available only after T+1 settlement per **A7**. The current available margin does not include today's unsettled profits. These will reflect in the opening balance on the next trading day.  
2. To determine if the client made an intraday trade:  
   - Invoke `kite_orders` (filter `order_status` = COMPLETE): if the same instrument has both BUY and SELL orders with matching quantities, it is intraday.  
   - For F&O: invoke `console_fno_positions`. Any quantity in `open_quantity` from the previous day was carried overnight — everything bought and sold beyond that today is intraday.  
   - If `product` = MIS: if total buy quantity equals total sell quantity for the same instrument, it is intraday.  
3. If client asks about a specific position P&L → invoke `kite_positions` and sum the `pnl` values for total P&L.

---

### Rule 3 — Negative Available Cash

1. `available_cash` < 0 → negative cash attracts interest at 0.05%/day (18% p.a.) per **A5**. Advise adding funds to clear the deficit. If not cleared, open positions may be squared off.  
2. If client holds ITM stock option positions approaching expiry → invoke `ledger_report` and check `remarks` for the ledger entry in **A10**. If found → route to Rule 12. If not found → continue with step 1 above — explain interest charge and advise adding funds.

---

### Rule 4 — Collateral Query

1. Per **A3** and **A6**:  
   - Liquid collateral is cash-equivalent and satisfies the 50% cash requirement.  
   - Equity collateral is non-cash and attracts 0.035%/day if used beyond the 50% cash limit.  
   - Usable for: equity intraday, futures, options buying and writing.  
   - Not usable for equity delivery (CNC) purchases.  
2. Approved list and haircuts per **A8** (approved securities).

---

### Rule 5 — SPAN / Exposure / Delivery Margin

1. Per **A3**: SPAN \+ Exposure = Initial Margin required by exchange for F&O.  
2. For physical delivery margin near expiry → share **A10** schedule. Margin calculator per **A8**.  
3. If client asks which position is blocking margin → invoke `kite_positions`.  
4. If client asks about a specific order's margin requirement → invoke `kite_orders` and check `filled_quantity` and `average_price` for OPEN and COMPLETE orders.

---

### Rule 6 — Payin / Payout Query

1. Weekend payins appear on Monday.  
2. For payin verification → invoke `cashier_payins` and check for the funds added. If funds were added on a weekend, they will appear on Monday.  
3. For payout verification → invoke `withdrawal_request` and check for entries where `payout_date` = today with the matching amount.

---

### Rule 7 — P&L Mismatch

1. The Positions page calculates P&L from the original entry price; the Funds page uses the MTM settlement price for futures. The funds page reflects what is actually settled in the account. Overall P&L will be the same once positions are closed.  
2. If client wants position-level breakdown → invoke `kite_positions` and sum the `pnl` across positions.

---

### Rule 8 — Opening Balance Mismatch

1. Opening balance is the previous day's closing balance after reversing blocked margin per **A3**. Differences can occur due to T+1 settlement of previous day's trades, MTM settlement on open F&O positions, charges/brokerage deducted, or settlement holiday delays.  
2. If client asks about specific charges or ledger entries → invoke `ledger_report`.

---

### Rule 9 — Sale Proceeds Availability

**BTST detection:**  
1. Invoke `kite_order_history` for the sell date and the previous trading day (accounting for holidays).  
2. If the stock was bought on the previous trading day and sold today → BTST trade. Funds are available from T+1 only.  
3. For additional confirmation, invoke `console_eq_holdings` for the sell date. Only quantity under `t1` is BTST — remaining quantity is from older settled holdings.  
4. Blocked value for BTST = `filled_quantity × average_price` from the sell order.

**Normal CNC sale (non-BTST):**  
100% of proceeds are available same day for all trades (effective Oct 7, 2024) per **A7**.

-If client asks about specific holdings sold → invoke `kite_holdings`.

---

### Rule 10 — Negative Balance After Market Order

1. Market orders are validated at the best available price but may execute at a different price, especially at market open. This price difference can cause a negative balance. Consequences per **A5**.  
2. If client asks about the specific order → invoke `kite_orders`. Check if `order_type` = MARKET and `order_status` = COMPLETE. Multiply `filled_quantity` × `price` to determine total funds required.  
3. If client asks about order history → invoke `kite_order_history` and apply the same check.

---

### Rule 11 — MTM Explanation

1. Mark to Market (MTM) is the daily revaluation of open futures positions at the closing price — profits or losses are settled to the client's account daily. Options do not have MTM settlement — for short options, margin increases as they move in-the-money.  
2. If client asks about a specific position's MTM → invoke `kite_positions`.

---

### Rule 12 — Balance Negative Due to Physical Delivery Margin

1. If the client's fund balance went negative near F&O expiry and client holds ITM stock option positions:  
   a. Invoke `ledger_report` and check `remarks` for the ledger entry in **A10** with a corresponding `debit` entry.  
   b. If found → physical delivery margin has been blocked for the ITM stock option position approaching expiry. Share the margin schedule from **A10** and the debit amount from the ledger. Physical settlement policy per **A8**.  
   c. If not found → route to Rule 3.  
2. If client asks about the position → invoke `kite_positions`.
