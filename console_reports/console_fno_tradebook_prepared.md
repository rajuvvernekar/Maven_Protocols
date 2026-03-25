# console_fno_tradebook_prepared

## Description

WHEN TO USE:

When clients:
- Ask about F&O trade history older than 100 days
- Need full F&O tradebook for tax filing, audit, or compliance
- Request F&O tradebook since account inception or for a past financial year
- Ask about old F&O trades to understand historical P&L or position
- Have a closed account and request historical F&O trade data

TRIGGER KEYWORDS: "old F&O trades", "last year F&O", "FY F&O tradebook", "historical F&O trades", "F&O since inception", "full derivative tradebook", "closed account F&O"

## Protocol

# CONSOLE FNO TRADEBOOK PREPARED PROTOCOL 

---

## Section A: Reference Data

---

### A1 — Tool Purpose & Fundamentals

This tool fetches a client's F&O tradebook with **no date range limitation** — it can retrieve trades since account inception. It has identical schema and data as `console_fno_tradebook` (same fields, same data source).

Use this tool only when the date range exceeds 100 days or the client needs full F&O history. For recent trades (last 100 days), use `console_fno_tradebook` — it is faster and returns the same data.

For closed accounts, **ESCALATE** — agent review needed for historical F&O trade data retrieval.

All business rules from `console_fno_tradebook` apply here equally.

**Input:** Client ID + From Date + To Date + Segment (FO/CDS/COM).

---

### A2 — Field Usage Rules

**Shareable fields:**

`trade_date` | `order_execution_time` | `tradingsymbol` | `exchange` | `segment` | `trade_type` | `quantity` | `price` | `order_id` | `trade_id` | `strike` | `expiry_date` | `instrument_type`

**Internal-only fields** (use for reasoning; communicate outcomes in plain language):

`client_id`

---

### A3 — Cross-Reference Tools

| Tool | When to Use |
|---|---|
| `console_fno_tradebook` | Same schema, limited to last 100 days. Use for recent F&O trades. |
| `console_fno_pnl` | Realized P&L computed from tradebook entries. |

---

### A4 — Self-Service Download Links

| Topic | URL |
|---|---|
| How to download trade and funds reports | https://support.zerodha.com/category/console/reports/other-queries/articles/how-to-download-trade-and-funds-reports-in-pdf |
| Where to see trades for a particular period | https://support.zerodha.com/category/console/reports/other-queries/articles/where-can-i-see-all-the-trades-i-ve-taken-for-a-particular-period |

---

### A5 — Escalation Data Template

When escalating, always include: **client ID, date range, segment, tradingsymbol (if specific), and error details.**

---

### A6 — Response Templates

**R1 — Redirect to console_fno_tradebook:**
"This date range is within the last 100 days, so I'll use the standard F&O tradebook tool for faster results."

**R2 — Self-service download guidance (active account):**
"You can download your F&O tradebook and other reports from Console. Here are the guides:
- How to download trade and funds reports: https://support.zerodha.com/category/console/reports/other-queries/articles/how-to-download-trade-and-funds-reports-in-pdf
- Where to see trades for a particular period: https://support.zerodha.com/category/console/reports/other-queries/articles/where-can-i-see-all-the-trades-i-ve-taken-for-a-particular-period"

---

**Escalation behavior:** When any rule in this protocol says **ESCALATE**, do not draft a customer-facing response. Instead, output only: **HUMAN AGENT ACTION REQUIRED** — followed by the reason from the rule. The human agent will handle the query manually.

## Section B: Decision Flow

---

### Preflight (run on every query)

```
1. Check if requested date range is within last 100 days
   └─ If yes → use console_fno_tradebook instead (per A3).
      Respond per A6-R1.

2. If date range exceeds 100 days OR full history needed → proceed.
```

### Route

```
Intent / Condition                                          → Rule
──────────────────────────────────────────────────────────────────────
Full F&O tradebook request (tax/audit/compliance, active)   → Rule 1
Closed account — need historical F&O trade data             → Rule 2
Trade verification for old dates                            → Rule 3
Report fails to load / times out                            → Rule 4
```

### Scope

- Address the client's query about historical F&O trade data beyond the 100-day window.
- Use **A2** field rules in all client communication.
- All business rules from `console_fno_tradebook` protocol (trade verification, multiple fills, CA adjustments, contract identification) apply identically here.

### Fallback

If no route matches, cross-reference with **A3** tools for additional context. If no root cause is found, **ESCALATE** per **A5**.

---

## Section C: Rules

---

### Rule 1 — Full F&O Tradebook Request (Tax / Audit / Compliance)

1. If client's account is active → guide client to self-service download. Respond per **A6-R2**.
2. If client asks for formatted PDF → share the same links per **A4**.

---

### Rule 2 — Closed Account F&O Trade Data

1. Client's account is closed and they need historical F&O trade data.
2. **ESCALATE** — agent review needed.

---

### Rule 3 — Trade Verification for Old Dates

1. Same rules as `console_fno_tradebook` protocol — verify trade existence, check segment, explain CA adjustments, identify contract details.
2. All business rules from `console_fno_tradebook` (Rules 1–6 in that protocol's v2) apply identically here.
3. If trade not found → check `console_fno_tradebook` as well (per **A3**). If still not found → **ESCALATE** per **A5**.

---

### Rule 4 — Report Fails to Load / Times Out

1. Large date ranges with high trade volume may cause timeouts.
2. Try narrowing the date range (e.g., one financial year at a time) or filtering by segment.
3. If the issue persists → **ESCALATE** per **A5**.

---

## Section D: General Notes

- This tool has no date range limitation — use it only when `console_fno_tradebook` (100-day limit) is insufficient.
- Identical schema and data source as `console_fno_tradebook`. All trade verification, multiple fills, CA adjustment, and contract identification rules from that protocol apply equally.
- For active accounts, guide clients to download reports themselves via Console (per **A4** links). For closed accounts, **ESCALATE** — agent review needed.
