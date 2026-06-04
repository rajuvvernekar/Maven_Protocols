# console_eq_tradebook_prepared

## Description

WHEN TO USE:

When clients:
- Ask about equity trade history, execution details, or trade confirmation
- Report a trade missing from their tradebook
- Question execution price, quantity, or trade timing
- Ask to verify buy/sell trades for a specific stock or date range
- Ask about tradebook data for any period (recent or older)
- Question why P&L or buy average seems wrong (need to verify underlying trades)
- Ask about contract note charges, MTM, or obligation details (requires manual handling)
- Ask if a trade was executed on NSE or BSE
- Ask about trade series (EQ, BE/T2T, etc.) for FIFO or settlement queries
- Need full tradebook for tax filing, audit, employer compliance, or legal purposes
- Request tradebook since account inception or for a past financial year
- Question tax P&L values and need to verify old trades
- Have a closed account and request historical trade data

TRIGGER KEYWORDS: "tradebook", "trade history", "trade details", "execution price", "trade missing", "order id", "trade id", "trade date", "buy trade", "sell trade", "contract note", "execution time", "T2T", "series", "trade confirmation", "old trades", "last year trades", "since inception", "full tradebook", "historical trades", "closed account tradebook", "tax filing tradebook", "audit", "old tradebook"

TAGS: orders, reports

## Protocol

# CONSOLE EQ TRADEBOOK PREPARED PROTOCOL

---

## Section A: Reference Data

### A1 — Fundamentals

- Intraday vs delivery is not a stored field — it is inferred from trade patterns per A3.
- **Product type (CNC / MIS / MTF / NRML / CO / BO) is not stored in the tradebook.** To identify the product type or order source (e.g., RMS auto-square-off), invoke `kite_order_history` for the trade date and match by `order_id`.

---

### A2 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |
|---|---|
| `trade_date` | Date the trade was executed |
| `order_execution_time` | Exact timestamp of trade execution |
| `tradingsymbol` | Exchange trading symbol of the instrument |
| `exchange` | Exchange on which the trade was executed (NSE / BSE) |
| `order_id` | Unique identifier for the order |
| `trade_id` | Unique identifier for the individual trade fill |
| `trade_type` | Buy or Sell |
| `quantity` | Number of shares traded |
| `price` | Execution price per share |
| `isin` | ISIN code of the instrument |
| `series` | Exchange series of the instrument (EQ, BE, BT, BZ) |

**Non-shareable:**

| Field | Interpretation |
|---|---|
| `instrument_id` | Internal instrument mapping identifier |
| `settlement_type` | Internal settlement classification |
| `client_id` | Internal client identifier |

---

### A3 — Series and Settlement Behavior

| Series | Category | Intraday Allowed? | Same-Day Buy+Sell Treatment | Buy Average Impact |
|---|---|---|---|---|
| EQ | Standard equity | Yes | Net position = 0 at EOD → intraday (speculative); shares still held → buy treated as delivery | Standard FIFO; intraday trades do not affect holdings buy average |
| BE / BT / BZ | Trade-to-Trade (T2T) | No — compulsory delivery | Both trades are separate delivery trades; no intraday exception | FIFO; same-day buy+sell impacts buy average (delivery, not speculative) |

---

### A4 — Order vs Trade Distinction

- An **order** is the instruction placed by the client. One order can result in multiple trade fills if executed in parts.
- A **trade** is a single fill — one row in the tradebook.
- The tradebook shows individual fills (`trade_id`). The contract note shows the aggregated obligation across all fills for an order.
- A client may see a different price on their contract note vs tradebook if their order was partially filled at different prices — both are correct.

---

### A5 — Scenarios and Interpretations

- **Full tradebook request (active account):** Active accounts can self-serve the full tradebook directly from Console.

- **Tradebook vs Tax P&L difference:** Tradebook shows gross trade values (`price` × `quantity`) per individual fill. Tax P&L applies FIFO matching across financial years and may exclude intraday trades from delivery P&L — both are correct for their respective purposes. Tax P&L is the authoritative report for income tax filing.

- **P&L report charges are period-level, not per-scrip:** Filtering by one stock shows that stock's P&L but period-wide charges.

---

### A6 — Links

| Topic | URL |
|---|---|
| Exchange toggle (NSE / BSE) | https://support.zerodha.com/category/trading-and-markets/general-kite/others-kite/articles/exchange-toggle |
| How to download trade and funds reports | https://support.zerodha.com/category/console/reports/other-queries/articles/how-to-download-trade-and-funds-reports-in-pdf |
| Where to see trades for a particular period | https://support.zerodha.com/category/console/reports/other-queries/articles/where-can-i-see-all-the-trades-i-ve-taken-for-a-particular-period |
| SOT / SOH (Statement of Transactions / Statement of Holdings) | https://support.zerodha.com/category/your-zerodha-account/transfer-of-shares-and-conversion-of-shares/cdsl-easi-easiest/articles/will-zerodha-send-me-holding-statements-for-my-investments |
| Auto Square-Off | https://support.zerodha.com/category/account-opening/resident-individual/ri-charges/articles/auto-square-off |

---

### A7 — Order Execution & Pricing Mechanics

- **Market order:** execution price is the best available price at time of execution; may differ from the last traded price the client saw before placing the order.
- **Limit order:** execution price is at or better than the limit price placed.
- **NSE vs BSE pricing:** NSE and BSE maintain independent order books — prices can differ for the same stock at the same time. The execution price is correct for the exchange on which the order was placed.
- **Buy average calculation:** FIFO basis. Full breakdown of contributing entries available on Console → Portfolio → Holdings → select stock → View breakdown.

---

### A8 — MTF Brokerage

- MTF orders: brokerage = lower of **₹20** or **0.3% of order value**, per executed order — same for intraday and delivery.

---

## Section B: Decision Flow

### Routing

```
Route by scenario
   ├─ Trade existence / detail; bought but not in holdings; sold but no funds; offsetting trade client didn't place → Rule 1
   ├─ Execution price questioned → Rule 2
   ├─ Series-related query (T2T / compulsory delivery) → Rule 3
   ├─ "Was this trade intraday or delivery?" → Rule 3
   ├─ Buy average verification (tradebook-based) → Rule 4
   ├─ Price differs between NSE and BSE → Rule 5
   ├─ Charges / brokerage queried from tradebook (incl. MTF brokerage, charged more brokerage for a stock, P&L charges high for one stock) → Rule 6
   ├─ Duplicate trade entries for the same order → Rule 7
   ├─ Tax P&L numbers don't match the tradebook → Rule 8
   ├─ Need all trades for tax filing / audit / compliance → Rule 9
   ├─ Closed account — historical trade data needed → Rule 10
   ├─ Report won't open / loading errors → Rule 11
   ├─ SOT / SOH (Statement of Transactions / Holdings) download request → Rule 12
   └─ Trade was sold / squared-off by RMS (not by the client) → Rule 13
```

### Fallback

- If no root cause is found → escalate.

---

## Section C: Rules

### Rule 1 — Trade Existence Verification

1. Trade found in the tradebook → share `trade_date`, `trade_type`, `quantity`, `price`, `exchange`, `order_id`, `trade_id` per A2.
2. **Shares bought but not in holdings / sold but no funds / an offsetting trade the client didn't place** → invoke `kite_order_history` and check `product` (not stored in tradebook, per A1):
   - **MIS / CO / BO (intraday):** position auto-squared-off at the intraday cutoff (equity 3:20 PM). An MIS buy never settles to demat (won't appear in holdings); the square-off is the offsetting trade the client didn't place → apply Rule 13.
   - **CNC / NRML / MTF (delivery):** not intraday. "Not in holdings" → route to holdings protocol (settlement / T1). "Sold but no funds" → invoke `ledger_report` and route to ledger protocol (T+1 settlement).
3. Trade not in the tradebook → invoke `console_eq_external_trades` — may be an off-platform entry (IPO, transfer, buyback, gift, ESOP).
4. Still not found after all sources → escalate.

---

### Rule 2 — Execution Price Verification

1. Apply order-type behavior per A7 (Market order vs Limit order).
2. Client says price differs from contract note → explain per A4 (tradebook = per-fill, contract note = weighted average).
3. Execution price materially differs from the client's stated limit price → escalate.

---

### Rule 3 — Trade Series, T2T & Intraday vs Delivery Identification

1. Series-related / T2T / compulsory-delivery query → apply A3 based on the `series` field (EQ standard equity vs BE / BT / BZ Trade-to-Trade).
2. "Was this trade intraday or delivery?" → apply the A3 same-day buy+sell treatment:
   - **EQ:** same-day buy and sell that net the position to 0 at EOD → intraday (speculative); if shares are still held → buy treated as delivery.
   - **BE / BT / BZ (T2T):** no intraday exception — both legs are separate delivery trades.

---

### Rule 4 — Buy Average Verification via Tradebook

1. Direct client to Console for the full FIFO breakdown per A7 (Buy average calculation).
2. Do not list all individual trade entries in the response — there may be many.
3. For internal verification → invoke `console_eq_holdings_breakdown`; walk through FIFO entry by entry.

---

### Rule 5 — NSE vs BSE Price Difference

1. Explain NSE vs BSE pricing per A7.
2. If the client wants to trade on the other exchange → share the exchange toggle link from A6.

---

### Rule 6 — Charges / Obligation Query

1. **Charged more brokerage for a stock / P&L charges high for one stock:** per A5, the filtered P&L report shows period-wide charges, not per-scrip.
2. **MTF trade brokerage:** confirm the order's product = MTF via `kite_order_history` (A1), then brokerage = lower of ₹20 or 0.3% of order value, per executed order (A8).
3. Other charges queries → `ledger_report_protocol`.
4. Genuine discrepancy after this → escalate.

---

### Rule 7 — Duplicate Trade Entries

1. Same `order_id` with identical trade details appearing more than once → known system issue on specific dates.
2. escalate.

---

### Rule 8 — Tradebook vs Tax P&L Value Difference

- Refer to A5 (Tradebook vs Tax P&L difference) for scenario context and interpretation.

---

### Rule 9 — Full Tradebook Request (Tax / Audit / Compliance)

1. Refer to A5 (Full tradebook request) for scenario context. Guide client to self-service download using links from A6.
2. If client specifically requests PDF format → same links from A6.

---

### Rule 10 — Closed Account Trade Data

- escalate.

---

### Rule 11 — Report Fails to Load / Times Out

1. Large date ranges with high trade volume may cause timeouts.
2. Narrow the date range (e.g., one financial year at a time) and retry.
3. If the issue persists → escalate.

---

### Rule 12 — SOT / SOH Download Request

- Share the SOT / SOH article from A6 — guides the client on downloading the Statement of Transactions / Statement of Holdings directly.

---

### Rule 13 — RMS Auto-Square-Off Identification

Applies when the client says a trade was sold / squared-off by the system rather than by them.

1. Identify the buy and sell trades from the tradebook per Rule 1.
2. Invoke `kite_order_history` for the trade date. Match the buy and sell `order_id` from the tradebook to the order book to obtain the `product` and `placed_by` fields.
3. Check the `placed_by` field on the order. If `placed_by` = `ADMINSQF` or `RMS<number>` → the order was closed by the RMS team. Reasons:
   - MIS / intraday position (incl. CO / BO) squared off at end of day (intraday cutoff 3:20 PM for equity), or
   - Position closed due to margin shortfall (client would have already received a margin call), or
   - Pending MIS order cancelled from Zerodha's end.
4. Confirm to the client that the position was auto-squared-off / the order was cancelled by RMS per the applicable reason above.
5. Inform the client that a **Call and Trade / Auto Square-Off charge of ₹59 (₹50 + 18% GST) per square-off** is debited to the ledger (cross-reference: Ledger Report Protocol — A5 Call and Trade row, Standard Transaction Inquiry rule's Call and Trade cross-reference).
6. Share the Auto Square-Off article from A6.
