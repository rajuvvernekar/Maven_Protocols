# console_eq_pnl

## Description

WHEN TO USE:

When clients:
- Ask about realized equity P&L (profit or loss from sold shares)
- Report P&L values (buy value, sell value, profit) appearing wrong for a stock
- Ask why a stock shows profit when they expected loss, or vice versa
- Ask about FIFO impact on P&L (e.g., sold newer shares but FIFO used older cost)
- Report P&L mismatch between Console and Kite
- Ask about intraday vs delivery P&L classification
- Ask about P&L impact from corporate actions (bonus, split, demerger, merger)
- Question Tax P&L values vs Console P&L (different reports, different purposes)
- Ask about unrealized P&L discrepancy between Console and Kite

TRIGGER KEYWORDS: "P&L", "profit and loss", "realized profit", "realized loss", "buy value", "sell value", "PnL report", "PnL wrong", "showing profit", "showing loss", "capital gain", "STCG", "LTCG", "tax P&L", "intraday P&L", "speculative", "delivery P&L", "unrealized P&L"

## Protocol

# CONSOLE EQ P&L PROTOCOL

---

## Section A: Reference Data

---

### A1 — Tool Purpose & Fundamentals

This tool looks up a client's realized equity P&L. Realized P&L = sell_value − buy_value (per FIFO matching of sell qty against oldest buys). Only shows P&L for stocks that have been **sold** — no P&L for holdings still held.

**FIFO:** When a client sells, the oldest buy is consumed first — this affects which cost price is used. FIFO applies across all product types combined (CNC + MTF); Console P&L does not separate MTF and CNC.

**Intraday trades** (buy + sell same stock same day) are classified as speculative — separate from delivery P&L. Product type (CNC/MIS) does not determine classification — what matters is whether offsetting trades exist on the same day in EQ series. **Exception:** T2T stocks (series BE/BT/BZ) — same-day buy + sell treated as delivery, not speculative.

**P&L affected by missing/wrong external trade entries:** If discrepant shares are sold without a buy entry, cost = ₹0 → inflated profit.

---

### A2 — Field Usage Rules

**Shareable fields:**

`tradingsymbol` | `isin` | `quantity` | `buy_value` | `sell_value` | `profit`

**Internal-only fields** (use for reasoning; communicate outcomes in plain language):

`name` | `client_id` | `instrument_id`

---

### A3 — P&L Calculations

| Calculation | Formula | Notes |
|---|---|---|
| Realized P&L | `profit` = `sell_value` − `buy_value` | Positive = profit, Negative = loss |
| Buy value source | FIFO matched | Oldest buy entries consumed first regardless of product type (CNC/MTF/MIS) |
| Unrealized (Console) | (closing price − buy avg) × qty | Uses previous day's closing price |
| Unrealized (Kite) | (LTP − buy avg) × qty | Uses live last traded price |

---

### A4 — Tax P&L vs Console P&L

| Aspect | Console P&L | Tax P&L |
|---|---|---|
| Purpose | Realized P&L per FIFO for selected date range | Classified for ITR filing |
| Classification | No STCG/LTCG classification | Delivery STCG, delivery LTCG, speculative (intraday), and charges |
| Differences | Aggregate view | Excludes intraday from delivery section; turnover = absolute P&L for speculative; editable for cost adjustments (gifts, transfers) |
| Editability | Not editable | Editable on Console (Reports → Tax P&L → Edit) for gift shares, cost basis adjustments |

**Verified P&L:** console.zerodha.com/verified — third-party verified report for ITR filing.

---

### A5 — Corporate Action P&L Impact

| CA Type | P&L Impact |
|---|---|
| Bonus | Bonus shares credited at ₹0 cost. Selling bonus shares shows full sell value as profit (correct per FIFO). When all originally purchased shares are sold via FIFO and only bonus shares remain, buy price in Tax P&L shows ₹0 — this is correct because bonus shares have zero cost of acquisition. The trade date for bonus shares is recorded as the ex-date. |
| Split | Adjusts qty + price proportionally → P&L unchanged. |
| Demerger | Cost split per COA ratio announced by company. P&L may appear incorrect temporarily until ratio applied. |
| Merger | Shares swapped at defined ratio. P&L uses original acquisition cost carried over to new shares. |
| Fractional shares (any CA) | Settled in cash → appears as a realized P&L entry for the fractional quantity. |

---

### A6 — Cross-Reference Tools

| Tool | When to Use |
|---|---|
| `console_eq_holdings` | Current buy avg and holdings qty. If buy avg wrong → P&L will also be wrong. |
| `console_eq_tradebook` | Verify actual trade prices and dates feeding into P&L. |
| `console_eq_holdings_breakdown` | Walk through FIFO entry by entry to explain P&L calculation. |
| `console_eq_external_trades` | Missing external entries cause wrong P&L (cost = ₹0 for discrepant shares). |

---

### A7 — Escalation Data Template

When escalating, always include: **client ID, tradingsymbol, ISIN, expected vs actual P&L values, and date range.**

---

### A8 — Response Templates

**R1 — Realized P&L verification:**
"Your realized P&L for [tradingsymbol]: you sold [quantity] shares with a total buy value (cost of acquisition) of ₹[buy_value] and total sell value (sale proceeds) of ₹[sell_value], resulting in a [profit > 0 ? 'profit' : 'loss'] of ₹[profit].

This is calculated using the FIFO method — when you sold, the cost of the oldest purchased shares was used as the buy value."

**R2 — FIFO causing unexpected P&L:**
"Your P&L is calculated using FIFO (First In, First Out). The buy value used is not necessarily your most recent purchase price — it's the cost of the oldest shares you held at the time of selling.

If you had older shares bought at a different price, FIFO consumes those first. You can verify the exact FIFO matching in the holdings breakdown on Console or Kite (View breakdown)."

**R3 — Discrepant shares causing inflated profit:**
"The P&L for [tradingsymbol] may appear inflated because the shares were recorded without a purchase entry (discrepant). When discrepant shares are sold, the system uses ₹0 as the buy value since no cost of acquisition is available, which makes the entire sell value appear as profit.

To correct this, the original purchase details need to be added. If the shares have already been sold, the buy average cannot be updated from your end — we'll need to investigate this further."

**R4 — Console vs Kite unrealized P&L difference:**
"Console uses the previous day's closing price to calculate unrealized P&L, while Kite uses the live last traded price (LTP). This is why the values differ during and after market hours."

**R5 — MTF P&L not separate:**
"Console does not calculate P&L separately for MTF and CNC positions. FIFO is applied across all your holdings of [tradingsymbol] regardless of whether shares were bought under MTF or regular delivery. This means the buy value used in P&L may include both MTF and CNC purchase prices.

Your MTF ledger settlements (net settlement entries) reflect the MTF-specific funding and margin — these are separate from the FIFO-based P&L shown on Console."

**R6 — Intraday (speculative) classification:**
"Same-day buy and sell of [tradingsymbol] in EQ series is treated as an intraday (speculative) trade, regardless of the product type used (CNC, MIS, or any other). The product type label does not determine the classification — what matters is whether offsetting buy and sell trades exist for the same stock on the same day. It will appear under the speculative section in Tax P&L, separate from delivery P&L."

**R7 — T2T delivery classification:**
"Since [tradingsymbol] is in the Trade-to-Trade category, same-day buy and sell is treated as a delivery trade, not intraday. Both transactions are considered separate delivery trades."

**R8 — Tax P&L vs Console P&L explanation:**
"The Tax P&L report and Console P&L serve different purposes:
- Console P&L shows aggregate realized P&L per stock for the selected date range
- Tax P&L classifies trades into delivery STCG, delivery LTCG, and speculative (intraday) with applicable charges

The values may differ because Tax P&L separates intraday trades from delivery, applies holding period classification, and includes charges. For income tax filing, please use the Tax P&L report."

**R9 — Tax P&L editable:**
"You can edit the Tax P&L report on Console (Reports → Tax P&L → Edit) to adjust cost of acquisition for gifted shares, transferred shares, or other special cases."

**R10 — Bonus P&L:**
"After a bonus issue, the bonus shares are credited at ₹0 cost. If you sell bonus shares, FIFO may consume these zero-cost entries, showing the entire sell value as profit. This is correct per FIFO accounting."

**R11 — Split P&L:**
"A stock split adjusts quantity and price proportionally — your total investment value and P&L remain unchanged."

**R12 — Demerger P&L:**
"After a demerger, the cost of acquisition is split between the original and new entity per the COA ratio announced by the company. P&L is calculated based on this split cost. If the ratio has not been applied yet, P&L may appear incorrect temporarily."

**R13 — Merger P&L:**
"After a merger, shares are swapped at the defined ratio. P&L is calculated using the original acquisition cost carried over to the new shares."

**R14 — Fractional share P&L:**
"Fractional shares from the corporate action were settled in cash. This appears as a realized P&L entry for the fractional quantity."

**R15 — Orphan unrealized entry:**
"We've identified that [tradingsymbol] is appearing in your unrealized P&L despite no active holdings. This is a data issue and we'll have it corrected."

**R16 — Bonus shares buy price ₹0 in Tax P&L:**
"The buy price of ₹0 for your [tradingsymbol] shares in the Tax P&L is correct. This is because all your originally purchased shares have been sold via FIFO, and only bonus shares remain (or were sold). Bonus shares are credited at zero cost of acquisition, so the system correctly records the buy price as ₹0.

You can verify this by checking the holdings breakdown on Console or Kite — the remaining shares will show as bonus credits with ₹0 entry price. The trade date for bonus shares is recorded as the ex-date of the bonus issue."

---

## Section B: Decision Flow

---

### Preflight (run on every query)

```
1. Identify the stock (tradingsymbol / ISIN) and the P&L concern
   (wrong realized, wrong unrealized, mismatch between platforms,
    CA impact, tax P&L difference, etc.)

2. If the issue involves buy average or holdings qty:
   └─ Cross-reference console_eq_holdings first (per A6).
      If buy avg is wrong → P&L will also be wrong.
      Route to console_eq_holdings protocol for avg resolution.
```

### Route

```
Intent / Condition                                          → Rule
──────────────────────────────────────────────────────────────────────
Client questions realized P&L for a stock                   → Rule 1
P&L doesn't match expected buy/sell prices (FIFO confusion) → Rule 2
Unexpectedly high profit (discrepant shares)                → Rule 3
P&L differs between Console and Kite                        → Rule 4
MTF-specific P&L query                                      → Rule 5
Same-day buy+sell classification (intraday vs delivery)     → Rule 6
P&L after bonus / split / demerger / merger / fractional    → Rule 7
Tax P&L vs Console P&L values differ                        → Rule 8
Stock in unrealized P&L despite all shares sold             → Rule 9
```

### Scope

- Address the client's query about equity P&L calculations, FIFO impact, CA adjustments, and platform differences.
- Use **A2** field rules in all client communication.

### Fallback

If no route matches, use **A6** to cross-reference other tools for additional context. If no root cause is found, escalate per **A7**.

---

## Section C: Rules

---

### Rule 1 — P&L Verification

1. Respond per **A8-R1** — share realized P&L details with FIFO context.

---

### Rule 2 — FIFO Causing Unexpected P&L

1. Respond per **A8-R2**.
2. If agent needs to prove the calculation → use `console_eq_holdings_breakdown` (per **A6**) to walk through entries.

---

### Rule 3 — Discrepant Shares Causing Inflated Profit

1. Check `console_eq_holdings` — verify if `discrepant` > 0 for that stock (or was > 0 before selling).
2. Also check `console_eq_external_trades` for missing buy entries (per **A6**).
3. Respond per **A8-R3**.
4. If shares already sold with ₹0 cost → escalate per **A7**. Backend correction needed.

---

### Rule 4 — Console P&L vs Kite P&L

1. Determine if client is comparing realized or unrealized P&L.
2. **Realized:** Should match. If different → check date range used. Console P&L requires specific date range; Kite shows current FY by default.
3. **Unrealized:** Respond per **A8-R4**. Calculation details per **A3**.

---

### Rule 5 — MTF P&L (No Separate Calculation)

1. Respond per **A8-R5**.

---

### Rule 6 — Intraday vs Delivery P&L Classification

Product type (CNC, MIS, Long-term, etc.) does not determine classification. Even if a client used CNC/Long-term product type, same-day buy + sell of the same stock in EQ series is treated as intraday (speculative), as long as the share does not belong to the BE (Trade-to-Trade) category. The product type label is irrelevant for tax classification — what matters is whether offsetting trades exist on the same day.

1. Check series field in tradebook (via `console_eq_tradebook` per **A6**).
2. Series EQ + same-day buy and sell exists → respond per **A8-R6**. This is intraday (speculative), not delivery — regardless of whether the client used CNC product type.
3. Series BE/BT/BZ (T2T) → respond per **A8-R7**. Same-day buy + sell in T2T is always delivery.

Example: Client buys 100 shares of CDSL using CNC on 30 March and sells 100 shares of CDSL using CNC on 30 March → this is an intraday trade, classified as speculative, not delivery.

For more details: https://support.zerodha.com/category/trading-and-markets/charts-and-orders/order/articles/what-does-cnc-mis-and-nrml-mean

---

### Rule 7 — Corporate Action Impact on P&L

1. Identify the CA type and respond with the applicable template:
   - Bonus → **A8-R10**. Impact per **A5**.
   - **Bonus shares — buy price ₹0 in Tax P&L:** If a client reports buy price showing ₹0 in Tax P&L after selling shares of a stock that had a bonus issue, check via `console_eq_holdings_breakdown` whether the remaining shares (or sold shares) are entirely bonus shares. If all originally purchased shares were sold via FIFO and only bonus shares remain (or were sold), the buy price of ₹0 is correct. Respond per **A8-R16**.
   - Split → **A8-R11**. Impact per **A5**.
   - Demerger → **A8-R12**. Impact per **A5**.
   - Merger → **A8-R13**. Impact per **A5**.
   - Fractional shares → **A8-R14**. Impact per **A5**.
2. If CA was 3+ weeks ago and P&L still appears wrong → escalate per **A7**.

---

### Rule 8 — Tax P&L vs Console P&L

1. Respond per **A8-R8**. Differences per **A4**.
2. If client wants to edit Tax P&L → respond per **A8-R9**. Edit path per **A4**.

---

### Rule 9 — Unrealized P&L Orphan Entry

1. Check `console_eq_holdings` for that stock.
2. If no holdings found but P&L still shows unrealized entry → respond per **A8-R15**. Escalate per **A7** as orphan lot.
