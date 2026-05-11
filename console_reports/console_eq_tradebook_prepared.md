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

### A6 — Escalation Data

Include when escalating to human agent: client ID, trade_date (or date range), tradingsymbol, order_id (if specific), and specific issue.

---

### A7 — Links

| Topic | URL |
|---|---|
| Exchange toggle (NSE / BSE) | https://support.zerodha.com/category/trading-and-markets/general-kite/others-kite/articles/exchange-toggle |
| How to download trade and funds reports | https://support.zerodha.com/category/console/reports/other-queries/articles/how-to-download-trade-and-funds-reports-in-pdf |
| Where to see trades for a particular period | https://support.zerodha.com/category/console/reports/other-queries/articles/where-can-i-see-all-the-trades-i-ve-taken-for-a-particular-period |

---

### A8 — Order Execution & Pricing Mechanics

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
   └─ Report won't open / loading errors → Rule 12
```

### Fallback

- If no root cause is found → escalate to human agent.

---

## Section C: Rules

### Rule 1 — Trade Existence Verification

1. Trade found in the tradebook → share `trade_date`, `trade_type`, `quantity`, `price`, `exchange`, `order_id`, `trade_id` per A2.
2. If the client questions whether sale proceeds were credited → invoke `ledger_report` for corroboration.
3. Trade not in the tradebook → invoke `console_eq_external_trades` — may be an off-platform entry (IPO, transfer, buyback, gift, ESOP).
4. Still not found after all sources → escalate to human agent per A6.

---

### Rule 2 — Execution Price Verification

1. Apply order-type behavior per A8 (Market order vs Limit order).
2. Client says price differs from contract note → explain per A4 (tradebook = per-fill, contract note = weighted average).
3. Execution price materially differs from the client's stated limit price → escalate to human agent per A6.

---

### Rule 3 — Trade Series and T2T Behavior

- Apply A3 based on the `series` field.

---

### Rule 4 — Intraday vs Delivery Identification

- Apply A3 based on the `series` field.

---

### Rule 5 — Buy Average Verification via Tradebook

1. Direct client to Console for the full FIFO breakdown per A8 (Buy average calculation).
2. Do not list all individual trade entries in the response — there may be many.
3. For internal verification → invoke `console_eq_holdings_breakdown`; walk through FIFO entry by entry.

---

### Rule 6 — NSE vs BSE Price Difference

1. Explain NSE vs BSE pricing per A8.
2. If the client wants to trade on the other exchange → share the exchange toggle link from A7.

---

### Rule 7 — Contract Note Charges / Obligation Query

1. Charges and obligation data are out of scope per A1.
2. For charges and obligations, the client should refer to their contract note directly — available on Console → Reports → Contract Notes.
3. If the client believes there is a discrepancy in charges on the contract note → escalate to human agent per A6.

---

### Rule 8 — Duplicate Trade Entries

1. Same `order_id` with identical trade details appearing more than once → known system issue on specific dates.
2. Escalate to human agent per A6 with client ID, affected `trade_date`, `order_id`(s), and `tradingsymbol`(s).

---

### Rule 9 — Tradebook vs Tax P&L Value Difference

- Refer to A5 (Tradebook vs Tax P&L difference) for scenario context and interpretation.

---

### Rule 10 — Full Tradebook Request (Tax / Audit / Compliance)

1. Refer to A5 (Full tradebook request) for scenario context. Guide client to self-service download using links from A7.
2. If client specifically requests PDF format → same links from A7.

---

### Rule 11 — Closed Account Trade Data

- Escalate to human agent per A6.

---

### Rule 12 — Report Fails to Load / Times Out

1. Large date ranges with high trade volume may cause timeouts.
2. Narrow the date range (e.g., one financial year at a time) and retry.
3. If the issue persists → escalate to human agent per A6.
