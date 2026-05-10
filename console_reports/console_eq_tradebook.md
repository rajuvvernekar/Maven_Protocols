# console_eq_tradebook

> **DEPRECATED (2026-05-10).** Maven now uses `console_eq_tradebook_prepared` for all date ranges. This tool is no longer wired into Maven and has been removed from `tool_registry.md`. File retained in repo for git history.

## Description

WHEN TO USE:

When clients:
- Ask about equity trade history, execution details, or trade confirmation
- Report a trade missing from their tradebook
- Question execution price, quantity, or trade timing
- Ask to verify buy/sell trades for a specific stock or date range
- Ask about tradebook data for a period within the last 100 days
- Question why P&L or buy average seems wrong (need to verify underlying trades)
- Ask about contract note charges, MTM, or obligation details (requires manual handling)
- Ask if a trade was executed on NSE or BSE
- Ask about trade series (EQ, BE/T2T, etc.) for FIFO or settlement queries

TRIGGER KEYWORDS: "tradebook", "trade history", "trade details", "execution price", "trade missing", "order id", "trade id", "trade date", "buy trade", "sell trade", "contract note", "execution time", "T2T", "series", "trade confirmation"

## Protocol


---

### A1 — Fundamentals

This tool looks up a client's equity tradebook — individual trade execution records. It covers the **last 100 days** of trades. For older trade history, use `console_eq_tradebook_prepared` which supports any date range.

Tradebook provides trade-level execution data only (price, qty, date, exchange). It does not contain charge, obligation, or contract note data.

Tradebook does not have a product type (CNC/MIS) field. For EQ series, intraday vs delivery must be inferred from whether offsetting trades exist on the same day. For T2T series, all trades are always delivery.


### A2 — Field Usage Rules

**Shareable fields:**

`trade_date` | `order_execution_time` | `tradingsymbol` | `exchange` | `order_id` | `trade_id` | `trade_type` | `quantity` | `price` | `isin` | `series`

**Internal-only fields** (use for reasoning; communicate outcomes in plain language):

`instrument_id` | `settlement_type` | `client_id`


### A3 — Series Identification & Impact

| Series | Category | Intraday Allowed? | Same-Day Buy+Sell Treatment | Buy Average Impact |
|---|---|---|---|---|
| EQ | Standard equity | Yes | If net position = 0 at EOD → intraday (speculative). If shares still held → delivery. | Standard FIFO |
| BE / BT / BZ | Trade-to-Trade (T2T) | No — compulsory delivery | Both trades treated as separate delivery trades, not intraday | Pure FIFO; same-day buy+sell impacts buy average (delivery, not speculative) |


### A4 — Cross-Reference Tools

| Tool | When to Use |
|---|---|
| `console_eq_external_trades` | If trade not found in tradebook — may be an off-platform entry (IPO, transfer, buyback, gift, ESOP). |
| `console_eq_tradebook_prepared` | For trade data older than 100 days. Supports any date range. Call immediately when this tool returns an error or when the requested date range falls outside the last 100 days. |
| `console_eq_holdings_breakdown` | Walk through FIFO entry by entry to verify buy average. |


### A5 — Escalation Data Template

When escalating, always include: **client ID, trade_date, tradingsymbol, order_id, and specific discrepancy details.**


---

### Preflight (run on every query)

```
1. TOOL ERROR HANDLING — if this tool returns an error or empty results
   for the requested date range:
   └─ Call console_eq_tradebook_prepared immediately with the same
      parameters (per A4). Do not escalate or ask the client for
      more information — the error means the date range exceeded
      this tool's 100-day limit.
```

### Route

```
Intent / Condition                                          → Rule
──────────────────────────────────────────────────────────────────────
Trade missing from tradebook                                → Rule 1
Execution price query                                       → Rule 2
Trade series / T2T behavior                                 → Rule 3
Buy average verification via tradebook                      → Rule 4
Intraday vs delivery identification                         → Rule 5
NSE vs BSE price difference                                 → Rule 6
Contract note charges / obligation query                    → Rule 7
Duplicate trade entries                                     → Rule 8
Tradebook vs Tax P&L value difference                       → Rule 9
```

### Scope

- Address the client's query about trade execution records, prices, series, and trade classification.
- Use **A2** field rules in all client communication.

### Fallback

If no route matches, cross-reference with **A4** tools for additional context. If no root cause is found, escalate per **A5**.


---

### Rule 1 — Verify Trade Existence

1. If the client describes a past trade event (e.g., "I sold recently", "I sold prematurely", "I redeemed last month"), search the tradebook for the last 90 days for any matching sell/buy entry for that instrument. Anchor the search to the client's described timeframe — do not default to only recent dates. Also check the `ledger_report` for corresponding sale proceeds or credit entries.
2. Search by tradingsymbol and date range.
3. If found → Share: `trade_date`, `trade_type`, `quantity`, `price`, `exchange`, `order_id`, `trade_id`. (share trade details). If sale proceeds were already credited per ledger, inform the client.
4. If not found in tradebook → check `console_eq_external_trades` (per **A4**) — may be an off-platform entry (IPO, transfer, buyback).
5. If not found in external trades → call `console_eq_tradebook_prepared` (per **A4**) to search the full trade history beyond 100 days.
6. If still not found after checking all sources → escalate per **A5**.


### Rule 2 — Execution Price Verification

1. Your [trade_type] order for [quantity] shares of [tradingsymbol] was executed at ₹[price] per share on [exchange] at [order_execution_time].

If you placed a market order, the execution price is the best available price at the time of execution, which may differ from the last traded price you saw. If you placed a limit order, the execution price will be at or better than your limit price..
2. If client says price differs from contract note → The tradebook shows the execution price per trade. The contract note may show a weighted average if your order was executed in multiple parts. Both are correct — the tradebook shows individual fills while the CN shows the aggregated obligation..
3. If execution price materially differs from limit order price placed by client → escalate per **A5**.


### Rule 3 — Trade Series and T2T

1. Check the `series` field. Identify per **A3**.
2. Series BE/BT/BZ (T2T) → This stock ([tradingsymbol]) is in the Trade-to-Trade (T2T) category. T2T stocks require compulsory delivery — intraday trading is not allowed. If you bought and sold on the same day, both are treated as separate delivery trades, not intraday. Pure FIFO applies to T2T stocks — the key difference from regular EQ stocks is that same-day buy+sell is treated as delivery (not speculative), so it impacts your buy average..
3. Series EQ → standard FIFO rules apply.


### Rule 4 — Buy Average Verification via Tradebook

1. Buy average is calculated using FIFO (First In, First Out). You can check the detailed breakdown of your [tradingsymbol] holdings on Console → Portfolio → Holdings → select the stock → View breakdown. This shows every entry that contributes to your current buy average. — direct client to Console breakdown view.
2. Do not list all individual trade entries in the response — there may be many.
3. If needs to verify internally → use `console_eq_holdings_breakdown` (per **A4**) to walk through FIFO.


### Rule 5 — Intraday vs Delivery Identification

1. Check `series` field first (per **A3**):
   a. Series BE/BT/BZ (T2T) → This stock is in the T2T category — all trades are treated as delivery, even if you bought and sold on the same day.. All trades are compulsory delivery.
   b. Series EQ → check tradebook for same-day buy AND sell entries for the same tradingsymbol:
      - Both buy and sell on same date → You had both a buy and sell trade for [tradingsymbol] on [trade_date]. If the net position at end of day was zero, these were intraday trades. If you still hold shares, the buy was delivery..
      - Only buy OR only sell on that date → delivery trade (per **A6-R10**).


### Rule 6 — NSE vs BSE Price Difference

1. Your trade was executed on [exchange]. Prices on NSE and BSE can differ slightly for the same stock at the same time. The execution price of ₹[price] is correct as per the [exchange] order book at the time of execution..


### Rule 7 — Duplicate Trade Entries

1. Same `order_id` with same trade details appearing twice → known system issue on specific dates.
2. Escalate per **A5** with: client ID, affected trade_date, order_id(s), tradingsymbol(s).
3. Escalate to Support agent. The Console team handles duplicate entry corrections.


### Rule 8 — Tradebook vs Tax P&L Value Difference

1. The tradebook shows gross trade values (price × quantity) for each individual trade. The Tax P&L report may show different values because it applies FIFO matching — the sell value is matched against the corresponding buy entries, and the calculation may span different financial years or exclude intraday trades. Both reports are correct for their respective purposes..
