# delayed_payment_charges

## Description

WHEN TO USE:

Customer asks about:
- Delayed payment charges (DPC) or interest debited from their account
- Why interest was charged despite having a positive balance (excess collateral scenario)
- Breakdown of how DPC was calculated for a specific period
- Debit balance interest, margin shortfall interest, or excess collateral interest verification
- DPC amount not matching their own calculation
- 0.05% per day or interest rate on debit balance
- How to avoid delayed payment charges
- Disputing DPC, claiming sufficient collateral/liquid holdings

TRIGGER KEYWORDS: "delayed payment charges", "DPC", "interest charges", "debit balance interest", "margin shortfall interest", "excess collateral interest", "collateral interest", "0.05% per day", "interest deducted", "why interest charged", "penalty interest", "shortfall charge", "how to avoid interest"

## Protocol

# DELAYED PAYMENT CHARGES (DPC) PROTOCOL

---

## Section A: Reference Data

All rules reference these blocks as single sources of truth.

### A1 — DPC Fundamentals

- DPC report provides a daily breakdown of interest calculation for a selected date range.
- Three types of interest: debit balance interest, excess collateral interest, margin shortfall interest.
- `interest_amount` = total daily interest = sum of `debit_balance_interest` + `margin_shortfall_interest` + `excess_collateral_interest`.
- Interest calculated daily including weekends and holidays (based on position held, not trading days).
- DPC debited to ledger monthly (typically first week of following month) as a lump sum.
- A positive ledger balance does not mean zero DPC — if margin requirement exceeds cash, excess collateral is used and interest applies.
- 50% of margin must come from cash; remaining 50% can come from collateral. If cash < 50% of margin, excess collateral interest applies.
- Liquid collateral (LIQUIDBEES etc.) valued at 100% for margin; equity collateral valued at ~50% (haircut-dependent).

### A2 — Interest Rate Table

| Interest Type | Condition | Rate | Calculated On |
|---|---|---|---|
| Debit balance interest | `ledger_balance` < 0 (debit) | 0.05% per day (18.25% annualized) | abs(ledger_balance) |
| Excess collateral interest | `ledger_balance` > 0 but margin exceeds cash → collateral covers gap | 0.035% per day | excess collateral utilized amount |
| Margin shortfall interest | Total margin required exceeds cash + collateral combined | Charged on shortfall amount | shortfall amount |

### A3 — Field Rules

**Shareable with client (use these client-facing names):**

| Internal Field | Client-Facing Name | Condition |
|---|---|---|
| `interest_amount` | "interest charged" | Always (as the total) |
| `excess_collateral_interest` | "excess collateral utilization interest" | Always when applicable |
| `margin_shortfall_interest` | "margin shortfall interest" | Always when applicable |
| `collateral_amount` | "collateral amount" | Only if client specifically asks about collateral |
| `liquidbees_collateral` | "liquid collateral" | Only if client specifically asks about collateral |

**Internal reasoning only (never share with client):** `client_id`, `posting_date`, `company`, `ledger_balance`, `unapplied_interest`, `margin_blocked`, `margin_after_collateral`, `qs_payout_amount`, `debit_balance_interest`, `excess_collateral_utilized`, `remaining_collateral_amount`, `remaining_cash_collateral_amount`.

When sharing interest charged with the client, use `interest_amount` as the total. The `debit_balance_interest` field value is for internal reasoning only — use `excess_collateral_interest` for the client-facing breakdown when applicable, and `interest_amount` for the overall total.

### A4 — Client-Facing Interest Explanations

| Type | Explanation Template |
|---|---|
| Debit balance | "Interest was charged because your account had a debit balance during this period. Interest is calculated at 0.05% per day on the debit balance amount. The total interest for [period] was ₹[interest_amount]." |
| Excess collateral | "Even though your account had a positive cash balance, interest was charged because your margin requirement exceeded your available cash. Your pledged collateral was used to cover the additional margin, and interest of ₹[excess_collateral_interest] was charged on the collateral amount utilized beyond your cash balance. This happens when less than 50% of your total margin requirement is covered by cash. The interest rate is 0.035% per day on the excess collateral utilized." |
| Margin shortfall | "A margin shortfall was detected — your total available margin (cash + collateral) was less than the required margin for your positions. Interest of ₹[margin_shortfall_interest] was charged on the shortfall amount." |

### A5 — How to Avoid DPC (by type)

| Type | Avoidance Guidance |
|---|---|
| Debit balance | "Maintain a positive cash balance by adding funds before charges or obligations are debited." |
| Excess collateral | "Ensure at least 50% of your margin requirement is covered by cash (not just collateral). You can add funds or reduce your F&O positions to lower margin requirements." |
| Margin shortfall | "Ensure total margin (cash + collateral) covers your position requirements. Add funds or pledge additional approved securities." |

### A6 — DPC vs MTF Interest Distinction

| | DPC | MTF Interest |
|---|---|---|
| What it covers | Debit balances, margin shortfalls, excess collateral utilization in the trading account | Funded amount for shares bought under Margin Trading Facility |
| Rate | 0.05% per day (debit balance), 0.035% per day (excess collateral) | 0.04% per day |
| Where to check | DPC report on Console | MTF Interest Statement on Console |

### A7 — Cross-Reference Protocols

| Topic | Refer to |
|---|---|
| DPC debit entry on ledger (actual posting) | Ledger Report protocol |
| Collateral holdings verification (if client disputes collateral in DPC) | Pledge Request Report protocol |

### A8 — Escalation Triggers (Consolidated)

Escalate when any of the following occur:
- DPC report values don't match ledger debit entry amount for the same period.
- Collateral amount in DPC report differs significantly from pledged holdings for the same date.
- Margin blocked in DPC report doesn't match ledger_report "With Margin" margin entries.
- Client provides a valid calculation showing a different amount from the report, and the report values themselves appear incorrect after verification.
- Client requests a waiver, reversal, or reimbursement of DPC for any reason (including AMC-induced debit, lack of notification, or account inactivity).

Include in escalation: client ID, date range, specific discrepancy (or client's stated reason for dispute), DPC report values, and interest amounts.

**Escalation behavior:** When any rule in this protocol says **ESCALATE**, do not draft a customer-facing response. Instead, output only: **HUMAN AGENT ACTION REQUIRED** — followed by the reason from the rule. The human agent will handle the query manually.

---

## Section B: Decision Flow

### Preflight (run on every query)

1. Fetch the DPC report for the client's relevant date range.
2. Apply field protection (**A3**) — identify which fields are shareable and which are internal only.
3. Format all amounts with ₹ and Indian comma notation. Format dates as DD MMM YYYY.
4. Determine which interest type(s) apply: check `debit_balance_interest`, `excess_collateral_interest`, and `margin_shortfall_interest` values.

### Routing Tree

```
Query relates to DPC / interest charges →
│
├─ Client asks why interest was charged
│  ├─ ledger_balance < 0 → Rule 1 (Debit balance)
│  ├─ ledger_balance > 0 but excess_collateral_interest > 0 → Rule 2 (Excess collateral)
│  └─ margin_shortfall_interest > 0 → Rule 3 (Margin shortfall)
│
├─ Client asks for detailed calculation / says amount doesn't match
│  → Rule 4
│
├─ Client asks about weekend/holiday interest
│  → Rule 5
│
├─ Client asks how to avoid DPC
│  → Rule 6
│
├─ Client confuses DPC with MTF interest
│  → Rule 7
│
├─ Client asks when DPC is debited / sees lump sum interest on ledger
│  → Rule 8
│
├─ Client disputes collateral sufficiency
│  → Rule 9
│
├─ Client requests waiver / reversal / reimbursement
│  → Rule 10 (Escalate)
│
└─ Data mismatch / no root cause found
   → Rule 10 (Escalate)
```

### Scope

- Address: DPC report entries, interest explanations, calculation breakdowns, avoidance guidance, and collateral-related DPC queries.
- Do not volunteer: internal field values (per **A3**), MTF interest details beyond the distinction in **A6**, or information the client hasn't asked about.

### Fallback

If no root cause is identified after checking all relevant rules → **ESCALATE** per Rule 10.

---

## Section C: Rules

Rules reference Section A blocks. They do not redefine what is already defined there.

### Rule 1 — Debit Balance Interest Explanation

1. Confirm: balance in `ledger_report` < 0 for the period (internal check only — do not share  balance in `ledger_report`).
2. Respond using the debit balance template from **A4**.
3. Add avoidance guidance from **A5** (debit balance row): "To avoid debit balance interest, ensure your account maintains a positive cash balance by adding funds or reducing positions."

### Rule 2 — Excess Collateral Interest Explanation

1. Confirm: balance in `ledger_report` > 0 but `excess_collateral_interest` > 0 (internal check only).
2. Respond using the excess collateral template from **A4**.
3. Add avoidance guidance from **A5** (excess collateral row).

### Rule 3 — Margin Shortfall Interest Explanation

1. Confirm: `margin_shortfall_interest` > 0.
2. Respond using the margin shortfall template from **A4**.
3. Add avoidance guidance from **A5** (margin shortfall row): "To avoid this, ensure sufficient funds or pledged collateral to cover your position margins."

### Rule 4 — DPC Calculation Breakdown

1. Provide a summary:
   "Your interest charges for [period]:
   - Total interest charged: ₹[sum of interest_amount across days]
   - This includes [debit balance interest / excess collateral utilization interest / margin shortfall interest — whichever applies]

   Interest is calculated daily (including weekends and holidays when positions are held) and debited to your ledger monthly."

2. If the client provides their own calculation and it differs:
   - Verify daily values from the report against the calculation formula in **A2**.
   - If report values are correct per the formula → explain that interest accrues on weekends/holidays too (per Rule 5).
   - If report values themselves appear incorrect → **ESCALATE** per Rule 10.

### Rule 5 — Weekend/Holiday Interest

1. Respond: "Interest on debit balances, margin shortfalls, and excess collateral utilization is calculated for every calendar day, including weekends and market holidays. This is because your positions and margin obligations continue to exist even when markets are closed."

### Rule 6 — How to Avoid DPC

1. Identify which interest type(s) apply to the client.
2. Provide the relevant avoidance guidance from **A5** for each applicable type.

### Rule 7 — DPC vs MTF Interest

1. Respond using the distinction from **A6**:
   "Delayed payment charges and MTF interest are different:
   - DPC is charged on debit balances, margin shortfalls, or excess collateral utilization in your trading account (0.05% per day on debit balance, 0.035% on excess collateral).
   - MTF interest is charged on the funded amount for shares bought under Margin Trading Facility (0.04% per day).

   Your MTF interest details are available in the MTF Interest Statement on Console."

### Rule 8 — Monthly DPC Debit on Ledger

1. Respond: "Delayed payment charges are calculated daily but debited to your ledger as a monthly total, typically in the first week of the following month. The entry will appear in your ledger as an interest charge."
2. For the ledger entry → use the Ledger Report protocol (per **A7**) to show the actual debit posting.

### Rule 9 — Collateral Amount Dispute

1. Check `collateral_amount` and `liquidbees_collateral` values.
2. Respond: "Your total collateral on that date was ₹[collateral_amount] (including ₹[liquidbees_collateral] in liquid collateral). However, only up to 50% of margin can be covered by equity collateral — the remaining must come from cash or liquid collateral. If your cash was insufficient to cover the remaining 50%, excess collateral interest applies."
3. If the client still disputes → compare with Pledge Request Report (per **A7**) for the same dates.
4. If mismatch between DPC collateral and pledge report → **ESCALATE** — agent review needed, as per Rule 10.

### Rule 10 — Escalation

Escalate when any trigger in **A8** is met.

For waiver/reversal/reimbursement requests: **ESCALATE** — agent review needed. The support agent handles all approval, denial, and reversal calculations. Include: client ID, charge dates, interest amounts, and client's stated reason for dispute.

For data mismatches: include client ID, date range, specific discrepancy, and DPC report values.

---

## Section D: General Notes

1. Multiple interest types can apply on the same day — a client may have both debit balance interest and margin shortfall interest simultaneously. Always check all three fields.
2. The DPC report is the source of truth for daily interest breakdowns. The ledger shows only the monthly lump sum debit.
3. When explaining why DPC was charged despite a positive balance, always lead with the 50% cash requirement for margin — this is the most common source of confusion.
