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

## Protocol

# KITE MARGINS PROTOCOL

---

## Section A: Reference Data

---

### A1 — Tool Purpose & Fundamentals

This tool shows the client's **funds/margin page on Kite** — available margin, cash, collateral, used margin, and settlement details. Only the **Equity** category is relevant; ignore the Commodity category.

Available Cash on Kite is rounded to 1 decimal place for display; the full amount is withdrawable.

Positions P&L uses entry price; Funds page uses last MTM settlement price → may differ intraday. Overall P&L will be the same once positions are closed.

**Input:** Client ID.

---

### A2 — Field Usage Rules

**Shareable fields:**

`opening_balance` | `available_margin` | `used_margin` | `available_cash` | `payin` | `payout` | `span` | `delivery_margin` | `exposure_margin` | `option_premium` | `liquid_collateral` | `equity_collateral` | `total_collateral` | `m2m_realised`

**Internal-only fields** (use for reasoning only; communicate outcomes in plain language):

`m2m_unrealised`

Always use ₹ formatting for amounts.

---

### A3 — Field Definitions

| Field | Definition |
|---|---|
| Available Margin | Total funds for trading: cash + collateral + premium received + realised/unrealised P&L − used margin |
| Available Cash | Previous day closing balance + payin − payout ± day's settled activity. If negative → interest applies. |
| Opening Balance | Previous day's closing balance after reversing blocked margin |
| Used Margin | Margin blocked for open positions + open orders. Negative when selling holdings or closing long options. |
| Free Cash | Cash Margin Available + Pay In + Direct Collateral − Margin Used |
| Payin | Funds added during the day. Weekend payins appear on Monday. |
| Payout | Funds withdrawn during the day. |
| Total Collateral | Liquid Collateral + Equity Collateral |
| Liquid Collateral | Pledged LiquidBees/liquid MFs after haircut — treated as cash equivalent |
| Equity Collateral | Pledged stocks/ETFs/MFs after haircut |
| Option Premium | Premium paid (−ve for buying) or received (+ve for selling). Included in available cash, shown separately. |
| SPAN | Exchange-calculated risk margin for F&O. Revised throughout day. |
| Exposure | Margin over SPAN (index: 2% contract value; stock: 3.5% or 1.5 SD). |
| SPAN + Exposure | = Initial Margin |
| Delivery Margin | T1 sale proceeds + physical delivery margin for ITM stock options during expiry week + additional MCX margin near expiry. Physical delivery margin increases progressively from E-4 to expiry day — see **A12** for the full schedule. |
| M2M Realised | Realised MTM P&L from closed F&O positions |
| M2M Unrealised | Unrealised MTM P&L from open F&O positions (internal use only) |

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
| Negative balance + F&O orders | Brokerage: ₹40 per executed F&O order (instead of ₹20) |
| No funds added | Positions may be squared off without notice |

---

### A6 — Collateral Rules

| Rule | Detail |
|---|---|
| Cash requirement | 50% of F&O margin must be cash or cash-equivalent |
| Cash equivalent | LiquidBees ETF, liquid mutual funds (after haircut) |
| Non-cash shortfall charge | 0.035%/day (12.775% p.a.) |
| Usable for | Equity intraday, futures, options buying and writing |
| Not usable for | Equity delivery (CNC) purchases — cash or cash-equivalent margin is required for delivery buys |

---

### A7 — Margin Call Rules

| Timing | Action Required |
|---|---|
| Before market hours | Add funds immediately |
| After market hours | Add funds by 11:59 PM same day |
| No action taken | Positions squared off at Zerodha's discretion |

CC takes 4 random margin snapshots/day; peak used for shortfall calculation. Shortfall can occur even after closing positions if a snapshot was already captured.

---

### A8 — Settlement & Availability

| Source | When Available |
|---|---|
| Intraday/F&O profits | After T+1 settlement (next trading day). If T+1 is settlement holiday → additional day. |
| Sale proceeds from holdings | 100% available same day (effective Oct 7, 2024) |
| Unsettled funds | Pending T+1 settlement — cannot withdraw until complete |

---

### A9 — Links

| Topic | URL |
|---|---|
| Margin calculator | zerodha.com/margin-calculator |
| Intraday leverages | zerodha.com/marketintel/bulletin/249809/latest-intraday-leverages-mis-bo-co |
| Approved securities (pledge haircuts) | zerodha.com/approved-securities |
| Verify equity collateral | investorhelpline.nseindia.com/ClientCollateral/welcomeCLUser |
| Verify commodity collateral | clientreports.mcxccl.com |
| Physical settlement policy | https://support.zerodha.com/category/trading-and-markets/trading-faqs/f-otrading/articles/policy-on-physical-settlement |

---

### A10 — Escalation Data Template

When escalating, always include: **client ID, current margin values, and specific issue.**

---

### A11 — Response Templates

**R1 — Balance inquiry:**
Share: `available_margin` (₹), `available_cash` (₹), `opening_balance` (₹), `used_margin` (₹).

**R2 — Used margin negative:**
"Your used margin shows ₹[used_margin] (negative) because you have received credit from selling holdings or closing long option positions today. This credit is included in your available margin."

**R3 — Profit not in balance:**
"Intraday and F&O profits are available only after T+1 settlement (next trading day). Your current available margin of ₹[available_margin] does not include today's unsettled profits. These will reflect in your opening balance on the next trading day. If the next day is a settlement holiday, it takes an additional day."

**R4 — Negative available cash:**
"Your available cash is ₹[available_cash]. A negative cash balance attracts interest at 0.05% per day (18% p.a.). Please add funds to clear the negative balance. If no funds are added, open positions may be squared off."

**R5 — Collateral details:**
Share: `liquid_collateral` (₹), `equity_collateral` (₹), `total_collateral` (₹). Explain: liquid = cash equivalent (satisfies 50% cash requirement), equity = non-cash (attracts 0.035%/day if used beyond 50% cash limit). Usable for: equity intraday, futures, options buying and writing. For equity delivery (CNC) purchases, cash or cash-equivalent margin is required — collateral alone is not sufficient.

**R6 — Margin call / shortfall:**
"Please add funds to your Zerodha account to cover the shortfall.
- If margin call received before market hours → add funds immediately.
- If received after market hours → add by 11:59 PM same day.
- If funds are not added, positions may be squared off at Zerodha's discretion.

Note: The Clearing Corporation takes 4 random margin snapshots during the day. The peak requirement is used — so a shortfall can occur even after closing positions if a snapshot was already captured."

**R7 — Shortfall after closing positions:**
"The Clearing Corporation captures 4 random margin snapshots during the day and uses the peak margin requirement. Even if you've closed your positions, a shortfall can occur if a snapshot was already captured when your margin was at its peak. Please add the shortfall amount mentioned in the email by 11:59 PM today to avoid a margin penalty."

**R8 — Option premium:**
"The option premium field shows: positive (+ve) = premium received from selling/writing options; negative (−ve) = premium paid for buying options. This amount is included in your available cash and shown separately for visibility."

**R9 — SPAN / exposure / delivery margin:**
Share: `span` (₹), `exposure_margin` (₹), `delivery_margin` (₹). Explain: SPAN + Exposure = Initial Margin required by exchange for F&O. Delivery margin blocked for: T1 sale proceeds, ITM stock options during expiry week, MCX contracts near expiry. SPAN revised by exchanges throughout the day. For physical delivery margin schedule near expiry, refer to **A12**.

**R10 — Payin / payout:**
Share: `payin` (₹), `payout` (₹). Payin = funds added today. Payout = funds withdrawn today. Weekend payins appear on Monday.

**R11 — P&L mismatch (positions vs funds):**
"Kite positions calculates P&L based on your original entry price. The funds page uses the last Mark to Market (MTM) settlement price for open futures and short options positions. The overall P&L will be the same once positions are closed, but intraday values may differ due to this MTM adjustment."

**R12 — Opening balance mismatch:**
"Your opening balance of ₹[opening_balance] is the previous day's closing balance after reversing any blocked margin. Differences may occur due to: settlement of previous day's trades (T+1), MTM settlement on open F&O positions, charges/brokerage deducted, or settlement holiday delays."

**R13 — Sale proceeds availability:**
"As of October 7, 2024, 100% of the proceeds from selling your holdings are available on the same day for all trades, including stocks and F&O positions."

**R14 — Unsettled funds:**
"Unsettled funds are credits you expect from profits or sold holdings that are pending T+1 settlement. You cannot withdraw these until settlement is complete. If T+1 falls on a settlement holiday, it takes an additional day."

**R15 — Available cash rounding:**
"Available cash on Kite is rounded to 1 decimal place for display. For example, ₹1005.53 shows as ₹1005.5. The full amount is withdrawable."

**R16 — Market order caused negative balance:**
"Market orders are validated at the best available price but execution can occur at a different price — especially at market opening. This price difference can cause a negative balance. A negative cash balance attracts interest at 0.05%/day (18% p.a.), and a brokerage of ₹40 per executed F&O order applies. Please add funds to clear the negative balance."

**R17 — MTM explanation:**
"Mark to Market (MTM) is the daily revaluation of open futures positions by the exchange at the closing price. Profits or losses are settled to your account daily. Short options don't undergo daily MTM — instead, margin increases as they move in-the-money."

**R18 — Balance negative due to physical delivery margin:**
"Your balance went negative because physical delivery margin has been blocked for your ITM stock option position approaching expiry. This margin increases progressively as expiry approaches (schedule per **A12**). To confirm, invoke `ledger_report` and check remarks for 'Physical delivery margin blocked for long options in NSE F&O' with the corresponding debit entry. For more details: [Physical settlement policy](https://support.zerodha.com/category/trading-and-markets/trading-faqs/f-otrading/articles/policy-on-physical-settlement)"

---

### A12 — Physical Delivery Margin Schedule (Stock F&O Expiry Week)

| Day | Margin Requirement |
|---|---|
| E-4 (Wednesday) | 10% of (VaR + ELM + Adhoc) |
| E-3 (Thursday) | 25% of (VaR + ELM + Adhoc) |
| E-2 (Friday) | 45% of (VaR + ELM + Adhoc) |
| E-1 (Monday) | 25% of contract value |
| Expiry day (Tuesday) | 50% of contract value |

This margin is blocked progressively for ITM stock options and futures positions approaching expiry. It can cause the available cash / fund balance to go negative if insufficient funds are available.

**Ledger verification:** Invoke `ledger_report` and check `remarks` for "Physical delivery margin blocked for long options in NSE F&O" with the corresponding `debit` entry to confirm delivery margin was the cause of a negative balance.

**Reference:** [Physical settlement policy](https://support.zerodha.com/category/trading-and-markets/trading-faqs/f-otrading/articles/policy-on-physical-settlement)

---

## Section B: Decision Flow

---

### Preflight (run on every query)

```
1. Load margin data for the client.
2. Note: only Equity category is relevant — ignore Commodity.
```

### Route

```
Intent / Condition                                          → Rule
──────────────────────────────────────────────────────────────────────
Explain a specific funds page field                         → Rule 1
Balance / available margin / available cash inquiry          → Rule 2
Profit not showing in balance                               → Rule 3
Negative available cash                                     → Rule 4
Used margin negative (confusion)                            → Rule 5
Collateral query                                            → Rule 6
Margin call / shortfall                                     → Rule 7
Shortfall despite positions closed                          → Rule 8
Option premium field query                                  → Rule 9
SPAN / exposure / delivery margin query                     → Rule 10
Payin / payout query                                        → Rule 11
P&L mismatch — positions vs funds page                      → Rule 12
Opening balance mismatch                                    → Rule 13
Sale proceeds availability                                  → Rule 14
Unsettled funds query                                       → Rule 15
Decimal discrepancy on funds page                           → Rule 16
Negative balance after market order                         → Rule 17
MTM explanation                                             → Rule 18
Balance negative due to physical delivery margin near expiry → Rule 19
```

### Scope

- Address the client's query about their funds page, margin, cash balance, collateral, and settlement.
- Use **A2** field rules in all client communication. Always use ₹ formatting.
- `m2m_unrealised` is internal-only — use for reasoning, communicate the outcome.

### Fallback

If no route matches, explain from **A3** field definitions. If no root cause is found, escalate per **A10**.

---

## Section C: Rules

---

### Rule 1 — Explain Funds Page Field

1. Map customer language to field using **A4**.
2. Explain using **A3** definitions.

---

### Rule 2 — Balance Inquiry

1. Respond per **A11-R1**.
2. If `used_margin` is negative → also explain per **A11-R2**.
3. If client asks why margin is blocked or about a specific order → invoke `kite_orders`.

---

### Rule 3 — Profit Not Showing in Balance

1. Respond per **A11-R3**. Settlement per **A8**.
2. If client asks about specific position P&L → invoke `kite_positions`.

---

### Rule 4 — Negative Available Cash

1. `available_cash` < 0 → respond per **A11-R4**. Interest/consequences per **A5**.
2. If client has ITM stock option positions approaching expiry → check whether physical delivery margin is the cause. Invoke `ledger_report` and check remarks for "Physical delivery margin blocked for long options in NSE F&O". If found → respond per **A11-R18** with the margin schedule from **A12**. If not found → continue with standard negative cash handling.

---

### Rule 5 — Used Margin Negative

1. Respond per **A11-R2**.
2. If client asks which holdings were sold → invoke `kite_holdings`.

---

### Rule 6 — Collateral Query

1. Respond per **A11-R5**. Rules per **A6**.
2. Verification links per **A9** (equity collateral, commodity collateral).
3. Approved list and haircuts per **A9** (approved securities).

---

### Rule 7 — Margin Call / Shortfall

1. Respond per **A11-R6**. Timing per **A7**.
2. If client asks which positions caused shortfall → invoke `kite_positions`.

---

### Rule 8 — Shortfall After Closing Positions

1. Respond per **A11-R7**. Snapshot logic per **A7**.

---

### Rule 9 — Option Premium Field

1. Respond per **A11-R8**.

---

### Rule 10 — SPAN / Exposure / Delivery Margin

1. Respond per **A11-R9**. Definitions per **A3**. Margin calculator per **A9**.
2. If delivery margin is blocked and client has ITM stock options near expiry → share margin schedule from **A12**.
3. If client asks which position is blocking margin → invoke `kite_positions`.
4. If client asks about a specific order's margin requirement → invoke `kite_orders`.

---

### Rule 11 — Payin / Payout Query

1. Respond per **A11-R10**.

---

### Rule 12 — P&L Mismatch (Positions vs Funds)

1. Respond per **A11-R11**. Share `m2m_realised`.
2. If client wants position-level breakdown → invoke `kite_positions`.

---

### Rule 13 — Opening Balance Mismatch

1. Respond per **A11-R12**.
2. If client asks about specific charges or ledger entries → invoke `ledger_report`.

---

### Rule 14 — Sale Proceeds Availability

1. Respond per **A11-R13**. Per **A8**.
2. If client asks about specific holdings sold → invoke `kite_holdings`.

---

### Rule 15 — Unsettled Funds

1. Respond per **A11-R14**. Per **A8**.

---

### Rule 16 — Available Cash Rounding

1. Respond per **A11-R15**.

---

### Rule 17 — Negative Balance After Market Order

1. Respond per **A11-R16**. Consequences per **A5**.
2. If client asks about the specific order → invoke `kite_orders`.
3. If client asks about order history → invoke `kite_order_history`.

---

### Rule 18 — MTM Explanation

1. Respond per **A11-R17**. Share `m2m_realised`.
2. If client asks about specific position MTM → invoke `kite_positions`.

---

### Rule 19 — Balance Negative Due to Physical Delivery Margin

1. If client's fund balance went negative near F&O expiry and client holds ITM stock option positions:
   a. Invoke `ledger_report` and check `remarks` for "Physical delivery margin blocked for long options in NSE F&O" with the corresponding `debit` entry.
   b. If found → respond per **A11-R18**. Share the margin schedule from **A12** and the debit amount from the ledger. Link to physical settlement policy per **A9**.
   c. If not found → route to Rule 4 (standard negative cash handling).
2. If client asks about the position → invoke `kite_positions`.

