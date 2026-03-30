# console_eq_tradebook_prepared

## Description

WHEN TO USE:

When clients:
- Ask about equity trade history older than 100 days
- Need full tradebook for tax filing, audit, employer compliance, or legal purposes
- Request tradebook since account inception or for a past financial year
- Question tax P&L values and need to verify old trades beyond 100-day window
- Have a closed account and request historical trade data

TRIGGER KEYWORDS: "old trades", "last year trades", "FY 2023-24", "FY 2024-25", "since inception", "full tradebook", "trade history more than 100 days", "historical trades", "closed account tradebook", "tax filing tradebook", "audit", "old tradebook"

## Protocol

# CONSOLE EQ TRADEBOOK PREPARED PROTOCOL 

---

## Section A: Reference Data

---

### A1 — Tool Purpose & Fundamentals

This tool fetches a client's equity tradebook with **no date range limitation** — it can retrieve trades since account inception. It has identical schema and data as `console_eq_tradebook` (same fields, same data source).

Use this tool only when the date range exceeds 100 days or the client needs full history. For recent trades (last 100 days), use `console_eq_tradebook` — it is faster and returns the same data.

For closed accounts, escalate to support agent for historical trade data retrieval.

All facts about series, T2T, FIFO, and contract notes from `console_eq_tradebook` apply here equally.

**Input:** Client ID + From Date + To Date.

---

### A2 — Field Usage Rules

**Shareable fields:**

`trade_date` | `order_execution_time` | `tradingsymbol` | `exchange` | `order_id` | `trade_id` | `trade_type` | `quantity` | `price` | `isin` | `series`

**Internal-only fields** (use for reasoning; communicate outcomes in plain language):

`instrument_id` | `settlement_type` | `client_id`

---

### A3 — Cross-Reference Tools

| Tool | When to Use |
|---|---|
| `console_eq_tradebook` | Same schema, limited to last 100 days. Use for recent trade queries. |
| `console_eq_external_trades` | Off-platform trades. If trade not found here, check external trades. |
| `console_eq_pnl` | Realized P&L computed from tradebook FIFO. |

---

### A4 — Self-Service Download Links

| Topic | URL |
|---|---|
| How to download trade and funds reports | https://support.zerodha.com/category/console/reports/other-queries/articles/how-to-download-trade-and-funds-reports-in-pdf |
| Where to see trades for a particular period | https://support.zerodha.com/category/console/reports/other-queries/articles/where-can-i-see-all-the-trades-i-ve-taken-for-a-particular-period |

---

### A5 — Escalation Data Template

When escalating, always include: **client ID, date range requested, tradingsymbol (if specific), and error details.**

---

### A6 — Response Templates

**R1 — Self-service download guidance (active account):**
"You can download your tradebook and other reports from Console. Here are the guides:
- How to download trade and funds reports: https://support.zerodha.com/category/console/reports/other-queries/articles/how-to-download-trade-and-funds-reports-in-pdf
- Where to see trades for a particular period: https://support.zerodha.com/category/console/reports/other-queries/articles/where-can-i-see-all-the-trades-i-ve-taken-for-a-particular-period"

**R2 — Tradebook vs Tax P&L difference:**
"The tradebook shows gross trade values for each individual trade. The Tax P&L applies FIFO matching across financial years and may exclude intraday trades from delivery P&L. Both reports are correct for their respective purposes. The Tax P&L is the report to use for income tax filing."

---

## Section B: Decision Flow

---

### Preflight (run on every query)

```
1. Check if requested date range is within last 100 days
   └─ If yes → use console_eq_tradebook instead (per A3).

2. If date range exceeds 100 days OR full history needed → proceed.
```

### Route

```
Intent / Condition                                          → Rule
──────────────────────────────────────────────────────────────────────
Full tradebook request (tax/audit/compliance, active acct)  → Rule 1
Closed account — need historical trade data                 → Rule 2
Trade verification for old dates                            → Rule 3
Tradebook vs Tax P&L difference                             → Rule 4
Report fails to load / times out                            → Rule 5
```

### Scope

- Address the client's query about historical trade data beyond the 100-day window.
- Use **A2** field rules in all client communication.
- All business rules from `console_eq_tradebook` protocol apply identically here.

### Fallback

If no route matches, cross-reference with **A3** tools for additional context. If no root cause is found, escalate per **A5**.

---

## Section C: Rules

---

### Rule 1 — Full Tradebook Request (Tax / Audit / Compliance)

1. If client's account is active → guide client to self-service download. Respond per **A6-R1**.
2. If client asks for tradebook in PDF format → share the same links per **A4**.

---

### Rule 2 — Closed Account Trade Data

1. Client's account is closed and they need historical trade data.
2. Escalate to support agent.

---

### Rule 3 — Trade Verification for Old Dates

1. Same rules as `console_eq_tradebook` protocol — verify trade existence, check series for T2T, explain FIFO.
2. All business rules from `console_eq_tradebook` (Rules 1–9 in that protocol's v2) apply identically here.
3. If trade not found → check `console_eq_external_trades` (per **A3**). If still not found → escalate per **A5**.

---

### Rule 4 — Tradebook vs Tax P&L Difference

1. Respond per **A6-R2**.

---

### Rule 5 — Report Fails to Load / Times Out

1. Large date ranges with high trade volume may cause timeouts.
2. Try narrowing the date range (e.g., one financial year at a time).
3. If the issue persists → escalate per **A5**.
