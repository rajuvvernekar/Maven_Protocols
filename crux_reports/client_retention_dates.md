# client_retention_dates

## Description

WHEN TO USE:

When clients:
- Ask why funds were transferred out during quarterly settlement (QS) and want breakdown
- Report QS amount doesn't match their expected balance
- Ask what "max retention amount" means or why some funds were retained
- Ask about obligations or margin retained during settlement
- Dispute partial QS payout — expected full balance but only received partial amount
- Ask about settlement for different companies (Zerodha, Zerodha Securities, Zerodha Commodities)

TRIGGER KEYWORDS: "quarterly settlement breakdown", "settlement payout details", "retention amount", "funds retained", "why partial settlement", "settlement breakdown", "max retention", "settlement obligation", "funds released amount", "QS payout amount", "settlement history", "settlement cycle details"

## Protocol

# CLIENT RETENTION DATES PROTOCOL


### A1 — Settlement Fundamentals

- This report shows how much was released and retained during each quarterly settlement (QS).
- Settlement happens separately for each segment: equity and F&O (under Zerodha), commodity (under Zerodha Commodities). Amounts and dates may differ per segment.
- Total QS payout = sum of releases across all segments.
- QS payouts are typically credited to the client's registered bank account within 1–2 working days of the settlement date.

### A2 — Retention Reasons

| Retention Type | Field | What It Means |
|---|---|---|
| Margin retained | `margin` | Funds held for open F&O or commodity positions requiring margin |
| Pending obligation | `obligation` | Net amount due from or to the client for recent trades still in the settlement cycle (e.g., shares bought on the trading day before settlement — payment obligation pending until T+1) |
| Maximum retention amount | `max_retention_amount` | Total the broker can retain per SEBI regulations to cover open positions and pending obligations |

### A3 — Field Rules

**Shareable with client (use these client-facing names):**

| Internal Field | Client-Facing Name |
|---|---|
| `settlement_date` | settlement date |
| `funds_released` | funds released to bank |
| `max_retention_amount` | maximum retention amount |
| `margin` | margin retained |
| `obligation` | pending obligation |

**Internal reasoning only (never share with client):** `client_id`, `company`, `securities_released`, `eq_margin`, `turnover`, `previous_obligation`, `security_obligation`, `previous_security_obligation`, `unencumbered_balance`, `collateral_amount`, `mode_of_settlement`.

### A4 — Cross-Reference Protocols

| Topic | Refer to |
|---|---|
| QS payout entry on ledger | Ledger Report protocol |
| QS schedule, opt-out rules, LIQUIDCASE interaction | Ledger Report protocol — A4 (QS Facts) |

### A5 — Escalation Triggers (Consolidated)

Escalate when any of the following occur:
- Funds released > 0 but not credited to bank after 3 working days.
- Maximum retention amount seems incorrect — exceeds visible margin + obligations.
- No settlement entry exists for a QS date when client was eligible.

Include in escalation: client ID, settlement_date, funds_released, max_retention_amount, and the specific issue.


### Preflight (run on every query)

1. Fetch the client retention dates report for the relevant settlement period.
2. Apply field protection per **A3** — identify shareable vs internal-only fields.
3. If client has positions across segments, check for entries under both Zerodha and Zerodha Commodities.
4. Format all amounts with ₹ and Indian comma notation. Format dates as DD MMM YYYY.

### Routing Tree

```
Query relates to QS payout / client retention →
│
├─ Client asks how much was paid out and why
│  → Rule 1
│
├─ Client expected full balance but received less
│  → Rule 2
│
├─ Zero payout (funds_released = 0)
│  → Rule 3
│
├─ QS funds not received in bank
│  → Rule 4
│
├─ Client has positions across multiple segments
│  → Rule 5
│
├─ Client asks what "obligation" means
│  → Rule 6
│
└─ Data mismatch / no root cause found
   → Rule 7 (Escalation)
```

### Scope

- Address: QS payout breakdowns, retention reasons, bank credit timing, and multi-segment settlements.

### Fallback

If no root cause is identified after checking all relevant rules → escalate per Rule 7.


### Rule 1 — QS Payout Breakdown

1. Respond using values from the report and retention types from **A2**:
   "Here's the breakdown for the settlement on [settlement_date]:
   - Funds released to your bank: ₹[funds_released]
   - Margin retained for open positions: ₹[margin]
   - Pending obligations: ₹[obligation]
   - Maximum retention amount: ₹[max_retention_amount]

   The maximum retention amount is the total your broker can retain per SEBI regulations to cover your open positions and pending obligations. The remaining balance was released to your registered bank account."

### Rule 2 — Partial QS Payout

1. Respond: "Not all funds may be released during quarterly settlement. Funds are retained for:
   - Open F&O or commodity positions requiring margin (₹[margin] retained)
   - Pending trade obligations from recent settlements (₹[obligation] pending)
   - Collateral adjustments

   Your actual payout was ₹[funds_released]. The retained amount of ₹[max_retention_amount] covers your current margin and obligation requirements."

### Rule 3 — Zero Payout

1. Confirm: `funds_released` = 0 for the settlement date.
2. Respond: "No funds were released during the [settlement_date] quarterly settlement. Your entire balance was retained because:
   - Margin required for open positions: ₹[margin]
   - Pending obligations: ₹[obligation]

   These amounts exceed or equal your available balance, so there were no free funds to release. Once your positions are closed or obligations settled, the funds become available."

### Rule 4 — QS Payout Not Received in Bank

1. Confirm: `funds_released` > 0 for the settlement date.
2. Respond: "The settlement report shows ₹[funds_released] was released on [settlement_date]. QS payouts are typically credited to your registered bank account within 1–2 working days of the settlement date."
3. If more than 3 working days have passed: "If it has been more than 3 working days and the amount has not been credited, please check with your bank. If still not received, we'll investigate further."
4. If still not received after bank check → escalate per Rule 7.

### Rule 5 — Multiple Segment Settlements

1. Check for entries under both company values (Zerodha and Zerodha Commodities) in the report.
2. Respond: "Settlement happens separately for each segment:
   - Equity and F&O: processed under Zerodha
   - Commodity: processed under Zerodha Commodities

   The settlement amounts and dates may differ per segment. Your total QS payout is the sum of releases across all segments."
3. Present the breakdown for each segment separately if both exist.

### Rule 6 — Obligation Explanation

1. Respond using the definition from **A2** (obligation row): "Obligation is the net amount due from or to you for recent trades that are in the settlement cycle. For example, if you bought shares on the trading day before settlement, the payment obligation for those shares is still pending. This amount is retained until the trade settles (T+1)."

### Rule 7 — Escalation

Escalate when any trigger in **A5** is met.

Include in escalation: client ID, settlement_date, funds_released, max_retention_amount, and the specific issue.

