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

## Section B: Decision Flow

### Routing

```
Route by scenario
   ├─ Trade existence / trade detail query → Rule 1
   ├─ Execution price questioned → Rule 2
   ├─ Series-related query (T2T / compulsory delivery) → Rule 3
   ├─ "Was this trade intraday or delivery?" → Rule 4
   ├─ Buy average verification (tradebook-based) → Rule 5
   ├─ Price differs between NSE and BSE → Rule 6
   ├─ Charges, brokerage, or obligations queried from tradebook → Rule 7
   ├─ Duplicate trade entries for the same order → Rule 8
   ├─ Tax P&L numbers don't match the tradebook → Rule 9
   ├─ Need all trades for tax filing / audit / compliance → Rule 10
   ├─ Closed account — historical trade data needed → Rule 11
   ├─ Report won't open / loading errors → Rule 12
   ├─ SOT / SOH (Statement of Transactions / Holdings) download request → Rule 13
   └─ Trade was sold / squared-off by RMS (not by the client) → Rule 14
```

### Fallback

- If no root cause is found → escalate.

---

## Section C: Rules

### Rule 1 — Trade Existence Verification

1. Trade found in the tradebook → share `trade_date`, `trade_type`, `quantity`, `price`, `exchange`, `order_id`, `trade_id` per A2.
2. If the client questions whether sale proceeds were credited → invoke `ledger_report` for corroboration.
3. Trade not in the tradebook → invoke `console_eq_external_trades` — may be an off-platform entry (IPO, transfer, buyback, gift, ESOP).
4. Still not found after all sources → escalate.

---

### Rule 2 — Execution Price Verification

1. Apply order-type behavior per A7 (Market order vs Limit order).
2. Client says price differs from contract note → explain per A4 (tradebook = per-fill, contract note = weighted average).
3. Execution price materially differs from the client's stated limit price → escalate.

---

### Rule 3 — Trade Series and T2T Behavior

- Apply A3 based on the `series` field.

---

### Rule 4 — Intraday vs Delivery Identification

- Apply A3 based on the `series` field.

---

### Rule 5 — Buy Average Verification via Tradebook

1. Direct client to Console for the full FIFO breakdown per A7 (Buy average calculation).
2. Do not list all individual trade entries in the response — there may be many.
3. For internal verification → invoke `console_eq_holdings_breakdown`; walk through FIFO entry by entry.

---

### Rule 6 — NSE vs BSE Price Difference

1. Explain NSE vs BSE pricing per A7.
2. If the client wants to trade on the other exchange → share the exchange toggle link from A6.

---

### Rule 7 — Charges / Obligation Query

1. Any charges query → route to `ledger_report_protocol` for handling.
2. If the client believes there is a discrepancy in charges → escalate.

---

### Rule 8 — Duplicate Trade Entries

1. Same `order_id` with identical trade details appearing more than once → known system issue on specific dates.
2. Escalate.

---

### Rule 9 — Tradebook vs Tax P&L Value Difference

- Refer to A5 (Tradebook vs Tax P&L difference) for scenario context and interpretation.

---

### Rule 10 — Full Tradebook Request (Tax / Audit / Compliance)

1. Refer to A5 (Full tradebook request) for scenario context. Guide client to self-service download using links from A6.
2. If client specifically requests PDF format → same links from A6.

---

### Rule 11 — Closed Account Trade Data

- Escalate.

---

### Rule 12 — Report Fails to Load / Times Out

1. Large date ranges with high trade volume may cause timeouts.
2. Narrow the date range (e.g., one financial year at a time) and retry.
3. If the issue persists → escalate.

---

### Rule 13 — SOT / SOH Download Request

- Share the SOT / SOH article from A6 — guides the client on downloading the Statement of Transactions / Statement of Holdings directly.

---

### Rule 14 — RMS Auto-Square-Off Identification

Applies when the client says a trade was sold / squared-off by the system rather than by them.

1. Identify the buy and sell trades from the tradebook per Rule 1.
2. Invoke `kite_order_history` for the trade date. Match the buy and sell `order_id` from the tradebook to the order book to obtain the `product` field and order source.
3. Check the buy order's `product`:
   - **MIS (Margin Intraday Square-off):** intraday product; position must be closed by the client before the intraday cutoff (3:20 PM for equity). If not closed, RMS auto-squares-off.
   - **CO / BO:** similar intraday-only behavior.
4. Check the sell order:
   - Sell order source = RMS / Auto-square-off → confirm to client that the position was auto-squared-off per intraday product rules.
5. Inform the client that a **Call and Trade / Auto Square-Off charge of ₹59 (₹50 + 18% GST) per square-off** is debited to the ledger (cross-reference: Ledger Report Protocol — A5 Call and Trade row, Rule 3 Call and Trade cross-reference).
6. Share the Auto Square-Off article from A6.
