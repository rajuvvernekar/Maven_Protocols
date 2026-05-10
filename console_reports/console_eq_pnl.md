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

TAGS: reports, holdings

## Protocol

# CONSOLE EQ P&L PROTOCOL

---

## Section A: Reference Data

---

### A1 — Fundamentals

- Realized P&L = sell_value − buy_value (per FIFO matching of sell qty against oldest buys). Only shows P&L for stocks that have been sold — no P&L for holdings still held.

- **FIFO:** When a client sells, the oldest buy is consumed first — this affects which cost price is used. FIFO applies across all product types combined (CNC \+ MTF); Console P&L does not separate MTF and CNC.

- **Intraday trades** (buy \+ sell same stock same day) are classified as speculative — separate from delivery P&L. Product type (CNC/MIS) does not determine classification — what matters is whether offsetting trades exist on the same day in EQ series. **Exception:** T2T stocks (series BE/BT/BZ) — same-day buy \+ sell treated as delivery, not speculative.

- **P&L affected by missing/wrong external trade entries:** If discrepant shares are sold without a buy entry, cost = ₹0 → inflated profit.

---

### A2 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |    
|---|---|    
| `tradingsymbol` | Trading symbol of the instrument |    
| `isin` | ISIN code of the instrument |    
| `quantity` | Number of shares traded |    
| `buy_value` | Total buy value |    
| `sell_value` | Total sell value |    
| `profit` | Realized profit or loss |

**Non-shareable:**

| Field | Interpretation |    
|---|---|    
| `name` | Internal instrument name |    
| `instrument_id` | Internal instrument identifier |    
| `client_id` | Internal client identifier |

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

Verified P&L report for ITR filing: see A8.

---

### A5 — Corporate Action P&L Impact

| CA Type | P&L Impact |  
|---|---|  
| Bonus | Bonus shares credited at ₹0 cost. Selling bonus shares shows full sell value as profit (correct per FIFO). When all originally purchased shares are sold via FIFO and only bonus shares remain, buy price in Tax P&L shows ₹0 — this is correct because bonus shares have zero cost of acquisition. The trade date for bonus shares is recorded as the ex-date. |  
| Split | Adjusts qty \+ price proportionally → P&L unchanged. |  
| Demerger | Cost split per COA ratio announced by company. P&L may appear incorrect temporarily until ratio is applied. |  
| Merger | Shares swapped at defined ratio. P&L uses original acquisition cost carried over to new shares. |  
| Fractional shares (any CA) | Settled in cash → appears as a realized P&L entry for the fractional quantity. |

---

### A6 — Escalation Data

**Required fields when escalating to human agent:** client ID, tradingsymbol, ISIN, expected vs actual P&L values, date range.

---

### A7 — Scenarios & Interpretations

**S1 — FIFO Causing Unexpected P&L:**  
Client's expected P&L doesn't match because they're comparing against a recent purchase price, but FIFO consumed older shares (at a different cost) first. The discrepancy is expected and correct. The buy value used is not the most recent purchase — it is the cost of the oldest shares held at the time of the sale.

**S2 — Discrepant Shares Causing Inflated Profit:**  
Shares were credited without a corresponding buy entry (discrepant). When sold, the system assigns ₹0 as cost of acquisition, making the entire sell value appear as profit. This is a data issue — the buy entry is missing, not an error in the P&L calculation logic itself.

**S3 — Console vs Kite Unrealized P&L Difference:**  
Console calculates unrealized P&L using the previous day's closing price; Kite uses live LTP. The difference is by design and expected during and after market hours. Not a discrepancy — two different price references.

**S4 — Intraday (Speculative) Classification:**  
Same-day buy and sell of a stock in EQ series = speculative income, not delivery. Product type (CNC, MIS, etc.) is irrelevant to classification — what matters is whether offsetting buy and sell trades exist on the same day for the same stock. This affects how the trade is classified in Tax P&L.

**S5 — T2T Delivery Classification:**  
For T2T stocks (BE/BT/BZ series), same-day buy and sell is treated as delivery, not intraday — unlike regular EQ series stocks. Both transactions are considered separate delivery trades.

**S6 — Tax P&L vs Console P&L Difference:**  
The two reports serve different purposes. Console P&L is an aggregate realized P&L view for a selected date range. Tax P&L classifies trades for ITR (STCG, LTCG, speculative) and includes charges. Differences between the two are expected and by design — they are not the same report.

**S7 — Tax P&L Editable:**  
Tax P&L allows manual cost basis adjustments for gifted shares, transferred shares, or other special cases where the system-recorded cost of acquisition is not accurate. Edit path: Console → Reports → Tax P&L → Edit.

**S8 — Bonus P&L:**  
Bonus shares are credited at ₹0 cost. When FIFO consumes bonus shares on a sale, the entire sell value appears as profit — this is correct accounting behavior, not an error. The client's actual investment is recovered through FIFO consumption of the originally purchased shares.

**S9 — Split P&L:**  
A stock split adjusts both quantity and price proportionally, leaving total investment value and P&L unchanged. No distortion occurs — the numbers simply reflect the post-split adjusted figures.

**S10 — Demerger P&L:**  
Post-demerger, cost of acquisition is split between original and new entity per the COA ratio announced by the company. Until the ratio is applied in the system, P&L may appear incorrect — this is temporary and expected.

**S11 — Merger P&L:**  
Post-merger, shares swap at the defined ratio and the original acquisition cost carries over to the new shares. P&L is calculated on this carried-over cost, not on the merger swap price.

**S12 — Fractional Share P&L:**  
Fractional shares arising from a corporate action are settled in cash and show up as a small realized P&L entry for the fractional quantity. This is correct and expected behavior.

**S13 — Orphan Unrealized Entry:**  
A stock appears in unrealized P&L but no active holdings exist for it. This is a system/data error — an orphan lot that has not been cleaned up. Needs backend correction.

**S14 — Bonus Shares ₹0 Buy Price in Tax P&L:**  
When all originally purchased shares have been sold via FIFO and the remaining or sold shares are entirely bonus shares, the buy price correctly shows ₹0. Bonus shares have zero cost of acquisition by definition. This is not an error — it is the correct FIFO outcome when only bonus shares remain.

---

### A8 — Links

| Purpose | URL |  
|---|---|  
| Verified P&L report (third-party verified, for ITR filing) | https://console.zerodha.com/verified |  
| What CNC, MIS, and NRML mean | https://support.zerodha.com/category/trading-and-markets/charts-and-orders/order/articles/what-does-cnc-mis-and-nrml-mean |

---

## Section B: Decision Flow

### Routing

```  
Query relates to equity P&L →  
│  
├─ Buy average or holdings qty issue is the underlying cause → invoke  
│  `console_eq_holdings` first; P&L will follow once avg is corrected  
├─ Client questions realized P&L for a stock → Rule 1  
├─ P&L doesn't match expected buy/sell prices (FIFO confusion) → Rule 2  
├─ Unexpectedly high profit (discrepant shares, ₹0 cost) → Rule 3  
├─ P&L differs between Console and Kite → Rule 4  
├─ MTF-specific P&L query → Rule 5  
├─ Same-day buy \+ sell classification (intraday vs delivery) → Rule 6  
├─ P&L after bonus / split / demerger / merger / fractional shares → Rule 7  
├─ Tax P&L vs Console P&L values differ → Rule 8  
└─ Stock in unrealized P&L despite all shares sold → Rule 9  
```

### Fallback

If no route matches, invoke relevant tools for additional context. If no root cause is found, escalate to human agent.

---

## Section C: Rules

---

### Rule 1 — P&L Verification

- Share the realized P&L details: sell_value, buy_value, profit, and quantity. Communicate that FIFO was applied — the buy value reflects the cost of the oldest shares held at the time of selling.

---

### Rule 2 — FIFO Causing Unexpected P&L

1. Explain that the buy value in P&L is not necessarily the most recent purchase price — FIFO consumes the oldest shares first, which may be at a different cost. See A7-S1.  
2. If the calculation needs to be proven step by step → invoke `console_eq_holdings_breakdown` to walk through FIFO entries.

---

### Rule 3 — Discrepant Shares Causing Inflated Profit

1. Invoke `console_eq_holdings` — verify if `discrepant` > 0 for that stock (or was > 0 before selling).  
2. Invoke `console_eq_external_trades` to check for missing buy entries.  
3. Communicate that the inflated profit is due to ₹0 cost assigned to discrepant shares — the buy entry is missing. See A7-S2.  
4. If shares already sold with ₹0 cost → escalate to human agent. Backend correction required.

---

### Rule 4 — Console P&L vs Kite P&L

1. Determine whether the client is comparing realized or unrealized P&L.  
2. **Realized:** Should match. If values differ → check the date range used. Console P&L requires a specific date range; Kite shows current FY by default.  
3. **Unrealized:** Console uses previous day's closing price; Kite uses live LTP — difference is by design. See A7-S3 and A3 for calculation details.

---

### Rule 5 — MTF P&L (No Separate Calculation)

- Communicate that Console does not calculate MTF and CNC P&L separately — FIFO runs across all holdings regardless of product type.

---

### Rule 6 — Intraday vs Delivery Classification

Product type (CNC, MIS, Long-term, etc.) does not determine tax classification. Even if a client used CNC, same-day buy \+ sell of the same stock in EQ series is treated as intraday (speculative). What matters is whether offsetting trades exist on the same day — not the product type label. See A8 for the CNC/MIS/NRML explainer link.

1. Invoke `console_eq_tradebook` to check the `series` field.  
2. **Series EQ \+ same-day buy and sell** → classified as intraday (speculative), not delivery, regardless of product type used. See A7-S4.  
3. **Series BE / BT / BZ (T2T)** → same-day buy \+ sell in T2T is always delivery. See A7-S5.

Example: Client buys 100 shares of CDSL using CNC on 30 March and sells 100 shares of CDSL using CNC on 30 March → intraday trade, classified as speculative, not delivery.

---

### Rule 7 — Corporate Action Impact on P&L

1. Identify the CA type from the client's query and apply the relevant interpretation:  
   - **Bonus** → See A7-S8 and A5 for impact details.  
   - **Bonus shares showing ₹0 buy price in Tax P&L** → invoke `console_eq_holdings_breakdown` to check whether remaining or sold shares are entirely bonus shares. If all originally purchased shares were sold via FIFO and only bonus shares remain or were sold, the ₹0 buy price is correct. See A7-S14.  
   - **Split** → See A7-S9 and A5 for impact details.  
   - **Demerger** → See A7-S10 and A5 for impact details.  
   - **Merger** → See A7-S11 and A5 for impact details.  
   - **Fractional shares** → See A7-S12 and A5 for impact details.  
2. If the CA occurred 3+ weeks ago and P&L still appears wrong → escalate to human agent.

---

### Rule 8 — Tax P&L vs Console P&L

1. Explain the difference: Console P&L is aggregate realized P&L; Tax P&L classifies for ITR with STCG/LTCG/speculative and charges. See A7-S6 and A4 for full comparison.  
2. If client wants to edit Tax P&L → edit path is Console → Reports → Tax P&L → Edit. See A7-S7 and A4.

---

### Rule 9 — Unrealized P&L Orphan Entry

1. Invoke `console_eq_holdings` for that stock.  
2. If no holdings found but unrealized P&L still shows an entry → this is a data error (orphan lot). See A7-S13. escalate to human agent.
