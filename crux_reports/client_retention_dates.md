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

TAGS: funds

## Protocol

# CLIENT RETENTION DATES PROTOCOL

---

## Section A: Reference Data

### A1 — Settlement Fundamentals

- Settlement happens separately for each segment: equity and F&O (under Zerodha), commodity (under Zerodha Commodities). Amounts and dates may differ per segment.
- If a client has positions across segments, check for entries under both Zerodha and Zerodha Commodities.
- Total QS payout = sum of releases across all segments.
- QS payouts are typically credited to the client's registered bank account within 1–2 working days of the settlement date.
- For QS schedule, opt-out rules, and LIQUIDCASE interaction → invoke `ledger_report`.

---

### A2 — Retention Reasons

| Retention Type | Field | What It Means |
|---|---|---|
| Margin retained | `margin` | Funds held for open F&O or commodity positions requiring margin |
| Pending obligation | `obligation` | Net amount due from or to the client for recent trades still in the settlement cycle (e.g., shares bought on the trading day before settlement — payment obligation pending until T+1) |
| Maximum retention amount | `max_retention_amount` | Total the broker can retain per SEBI regulations to cover open positions and pending obligations |

---

### A3 — Field Rules

**Shareable with client:**

| Field | Interpretation |
|---|---|
| `settlement_date` | Share as "settlement date" |
| `funds_released` | Share as "funds released to bank" |
| `max_retention_amount` | Share as "maximum retention amount" |
| `margin` | Share as "margin retained" |
| `obligation` | Share as "pending obligation" |

**Non-shareable:**

| Field | Interpretation |
|---|---|
| `client_id` | Internal client identifier |
| `company` | Entity — Zerodha (equity/F&O) or Zerodha Commodities (commodity); used to identify segment per A1 |
| `securities_released` | Value of securities released during settlement |
| `eq_margin` | Equity margin component |
| `turnover` | Total trade turnover for the settlement period |
| `previous_obligation` | Obligation carried over from the previous settlement cycle |
| `security_obligation` | Obligation related to securities settlement |
| `previous_security_obligation` | Security obligation from the previous cycle |
| `unencumbered_balance` | Balance not tied to any open position or obligation |
| `collateral_amount` | Value of collateral pledged |
| `mode_of_settlement` | Settlement mode (e.g., electronic, physical) |

---

### A4 — Escalation Triggers

Escalate when any of the following occur:
- Funds released > 0 but not credited to bank after 3 working days.
- Maximum retention amount seems incorrect — exceeds visible margin + obligations.
- No settlement entry exists for a QS date when client was eligible.

Include in escalation: client ID, settlement_date, funds_released, max_retention_amount, and the specific issue.

---

## Section B: Decision Flow

### Routing
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
├─ Client asks what "obligation" means
│  → Rule 6
│
└─ Data mismatch / no root cause found
   → Rule 7 (Escalation)

Note: If client has positions across multiple segments, apply Rule 5
in combination with any of the above routes.
```

### Fallback

If no root cause is identified after checking all relevant rules → ESCALATE TO HUMAN AGENT per Rule 7.

---

## Section C: Rules

### Rule 1 — QS Payout Breakdown

Use values from the report — `funds_released`, `margin`, `obligation`, and `max_retention_amount` (per A2 definitions). The `max_retention_amount` is what the broker can retain per SEBI regulations. The remaining balance is released to the client's registered bank account. Invoke `ledger_report` for the corresponding payout ledger entry.

---

### Rule 2 — Partial QS Payout

Not all funds are released during QS. Funds are retained for open F&O or commodity positions requiring margin (`margin`), pending trade obligations from recent settlements (`obligation`), and collateral adjustments. The actual payout is `funds_released`; the retained amount is `max_retention_amount`.

---

### Rule 3 — Zero Payout

`funds_released` = 0 for the settlement date. The entire balance was retained because margin required for open positions and pending obligations equal or exceed the available balance. Once positions are closed or obligations settled, funds become available.

---

### Rule 4 — QS Payout Not Received in Bank

`funds_released` > 0 but the client has not received the payout in their bank account. Credit timing is 1–2 working days per A1. If more than 3 working days have passed and the amount has not been credited → escalate to human agent per A4.

---

### Rule 5 — Multiple Segment Settlements

Client has positions across equity/F&O and commodity segments, resulting in entries under both Zerodha and Zerodha Commodities. Present the settlement breakdown for each segment separately. Total QS payout is the sum of `funds_released` across both segments.

---

### Rule 6 — Obligation Explanation

Apply A2.

---

### Rule 7 — Escalation

Any trigger in A4 is met, or no root cause identified after checking all relevant rules. Escalate to human agent. Include: client ID, settlement_date, funds_released, max_retention_amount, and the specific issue.
