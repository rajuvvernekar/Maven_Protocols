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

TAGS: charges, margins

## Protocol

# DELAYED PAYMENT CHARGES PROTOCOL

---

## Section A: Reference Data

### A1 — DPC Fundamentals

- DPC report provides a daily breakdown of interest calculation for a selected date range.  
- Three types of interest: debit balance interest, excess collateral interest, margin shortfall interest.  
- `interest_amount` = total daily interest = sum of `debit_balance_interest` \+ `margin_shortfall_interest` \+ `excess_collateral_interest`.  
- Interest calculated daily including weekends and holidays (based on position held, not trading days).  
- DPC debited to ledger monthly (typically first week of following month) as a lump sum.  
- A positive ledger balance does not mean zero DPC — if margin requirement exceeds cash, excess collateral is used and interest applies.  
- 50% of margin must come from cash; remaining 50% can come from collateral. If cash < 50% of margin, excess collateral interest applies.  
- Liquid collateral (LIQUIDBEES etc.) valued at 100% for margin; equity collateral valued at \~50% (haircut-dependent).

### A2 — Interest Rate Table

| Interest Type | Condition | Rate | Calculated On |  
|---|---|---|---|  
| Debit balance interest | `ledger_balance` < 0 (debit) | 0.05% per day (18.25% annualised) | abs(ledger_balance) |  
| Excess collateral interest | `ledger_balance` > 0 but margin exceeds cash → collateral covers gap | 0.035% per day | excess collateral utilised amount |  
| Margin shortfall interest | Total margin required exceeds cash \+ collateral combined | 0.05% per day (18.25% annualised) | shortfall amount |

### A3 — Field Rules

**Shareable with client:**

| Field | Interpretation |  
|---|---|  
| `interest_amount` | Total interest charged; client-facing label "interest charged" |  
| `excess_collateral_interest` | Excess collateral component; client-facing label "excess collateral utilisation interest" |  
| `margin_shortfall_interest` | Margin shortfall component; client-facing label "margin shortfall interest" |  
| `collateral_amount` | Total collateral value on the date; client-facing label "collateral amount" |  
| `liquidbees_collateral` | Liquid collateral component; client-facing label "liquid collateral" |

**Non-shareable:**

| Field | Interpretation |  
|---|---|  
| `client_id` | Internal client identifier |  
| `posting_date` | Internal posting date |  
| `company` | Internal company segment |  
| `ledger_balance` | Account ledger balance (used internally to dispatch debit balance scenario) |  
| `unapplied_interest` | Unapplied interest |  
| `margin_blocked` | Margin blocked |  
| `margin_after_collateral` | Margin after collateral |  
| `qs_payout_amount` | QS payout amount |  
| `debit_balance_interest` | Debit balance interest component (use `interest_amount` for the total) |  
| `excess_collateral_utilized` | Excess collateral utilised amount |  
| `remaining_collateral_amount` | Remaining collateral after utilisation |  
| `remaining_cash_collateral_amount` | Remaining cash collateral |

### A4 — Interest Type Mechanics

| Type | Mechanic |  
|---|---|  
| Debit balance | Charged when account is in debit balance during the period. |  
| Excess collateral | Charged when margin requirement exceeds available cash and pledged collateral covers the gap. |  
| Margin shortfall | Charged when total available margin (cash \+ collateral) falls below required margin. |

### A5 — How to Avoid DPC

| Type | Avoidance Guidance |  
|---|---|  
| Debit balance | Maintain a positive cash balance by adding funds before charges or obligations are debited. |  
| Excess collateral | Ensure at least 50% of margin requirement is covered by cash (not just collateral). Add funds or reduce F&O positions. |  
| Margin shortfall | Ensure total margin (cash \+ collateral) covers position requirements. Add funds or pledge additional approved securities. |

### A6 — DPC vs MTF Interest Distinction

| | DPC | MTF Interest |  
|---|---|---|  
| What it covers | Debit balances, margin shortfalls, excess collateral utilisation in the trading account | Funded amount for shares bought under Margin Trading Facility |  
| Rate | 0.05% per day (debit balance), 0.035% per day (excess collateral) | 0.04% per day |  
| Where to check | DPC report on Console | MTF Interest Statement on Console |

### A7 — Cross-Reference Protocols

| Topic | Refer to |  
|---|---|  
| DPC debit entry on ledger (actual posting) | Ledger Report protocol |  
| Collateral holdings verification (if client disputes collateral in DPC) | Pledge Request Report protocol |

### A8 — Escalation Triggers

Escalate to human agent when any of the following occur:  
- DPC report values don't match ledger debit entry amount for the same period.  
- Collateral amount in DPC report differs significantly from pledged holdings for the same date.  
- Margin blocked in DPC report doesn't match `ledger_report` "With Margin" margin entries.  
- Client provides a valid calculation showing a different amount from the report, and report values themselves appear incorrect after verification.  
- Client requests a waiver, reversal, or reimbursement of DPC for any reason (including AMC-induced debit, lack of notification, or account inactivity).

Include when escalating to human agent: client ID, date range, specific discrepancy (or client's stated reason for dispute), DPC report values, and interest amounts.

---

## Section B: Decision Flow

### Routing

```  
Route by scenario  
   ├─ Why interest was charged  
   │    ├─ ledger_balance < 0 → Rule 1 (Debit balance)  
   │    ├─ ledger_balance > 0 \+ excess_collateral_interest > 0 → Rule 2 (Excess collateral)  
   │    └─ margin_shortfall_interest > 0 → Rule 3 (Margin shortfall)  
   ├─ Detailed calculation / amount doesn't match → Rule 4  
   ├─ Weekend/holiday interest → Rule 5  
   ├─ How to avoid DPC → Rule 6  
   ├─ DPC vs MTF interest confusion → Rule 7  
   ├─ When DPC is debited / lump sum interest on ledger → Rule 8  
   └─ Disputes collateral sufficiency → Rule 9  
```

### Fallback

If no root cause is identified after checking all relevant rules → escalate to human agent per A8.

---

## Section C: Rules

### Rule 1 — Debit Balance Interest Explanation

1. Confirm `ledger_balance` < 0 for the period.  
2. Explain the debit balance mechanic per A4 and the rate per A2.  
3. Add avoidance guidance per A5 (debit balance row).

### Rule 2 — Excess Collateral Interest Explanation

1. Confirm `ledger_balance` > 0 and `excess_collateral_interest` > 0.  
2. Explain the excess collateral mechanic per A4 and the rate per A2.  
3. Add avoidance guidance per A5 (excess collateral row).

### Rule 3 — Margin Shortfall Interest Explanation

1. Confirm `margin_shortfall_interest` > 0.  
2. Explain the margin shortfall mechanic per A4 and the rate per A2.  
3. Add avoidance guidance per A5 (margin shortfall row).

### Rule 4 — DPC Calculation Breakdown

1. Provide a summary:  
   - Total interest charged: sum of `interest_amount` across days.  
   - Which interest type(s) apply (debit balance / excess collateral / margin shortfall).  
   - Interest is calculated daily (including weekends and holidays when positions are held) and debited to ledger monthly per A1.  
2. If client provides their own calculation and it differs:  
   - Verify daily values from the report against rates in A2.  
   - If report values are correct per the rate → explain weekend/holiday accrual per Rule 5.  
   - If report values themselves appear incorrect → escalate to human agent per A8.

### Rule 5 — Weekend/Holiday Interest

1. Explain that interest accrues for every calendar day, including weekends and market holidays, per A1.

### Rule 6 — How to Avoid DPC

1. Identify which interest type(s) apply.  
2. Provide the relevant avoidance guidance from A5 for each applicable type.

### Rule 7 — DPC vs MTF Interest

1. Explain the distinction per A6.  
2. For MTF-specific details, redirect client to MTF Interest Statement on Console.

### Rule 8 — Monthly DPC Debit on Ledger

1. Explain monthly debit timing per A1.  
2. For the actual ledger entry, use the Ledger Report protocol per A7.

### Rule 9 — Collateral Amount Dispute

1. Share `collateral_amount` and `liquidbees_collateral` (these fields are only relevant for collateral disputes).  
2. Explain the 50% cash-vs-collateral rule per A1.  
3. If client still disputes → compare with Pledge Request Report per A7 for the same dates.  
4. If mismatch between DPC collateral and Pledge Request Report → escalate to human agent per A8.
