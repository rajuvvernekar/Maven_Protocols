# e_mandate_schedule_report

## Description

WHEN TO USE:

When clients:
- Claim auto-debit did not happen (check if schedule exists)
- Ask about schedule creation, modification, or deletion
- Report error deleting a schedule
- Are confused about debit date vs credit date
- Ask why SIP failed when mandate is active (check if schedule is set up)
- Want to pause or stop auto-debit without cancelling mandate
- Report schedule dates changing unexpectedly

TRIGGER KEYWORDS: "schedule", "auto debit not happening", "debit date", "credit date", "delete schedule", "cancel schedule", "schedule error", "no debit", "SIP failed mandate active", "schedule not created", "stop auto debit"

## Protocol

# E MANDATE SCHEDULE REPORT PROTOCOL 


---

### A1 — Fundamentals

This tool shows **eMandate schedule configuration** — the amount, date, frequency, and status of auto-debit schedules that transfer funds from the client's bank to their Kite trading account.

Bank debits 1 working day before the scheduled credit date. If the credit date falls on a non-business day (weekend/holiday), the debit shifts to 1 day before the non-business day.

Failed debits are not retried — client must add funds manually. Mandate must be active before creating schedules.


### A2 — Field Usage Rules

**Shareable fields:**

`next_date` (communicate as "next credit date")

**Internal-only fields** (use for reasoning; communicate outcomes in plain language):

`name` | `creation` | `tag` | `start_date` | `schedule_date` | `next_debit_date` | `deactivation_date` | `active`

**Client-facing terminology:**

| Internal Term | Client-Facing Alternative |
|---|---|
| `next_date` | "next credit date" or "next scheduled date" |
| `next_debit_date` | (omit — internal; explain as "your bank debits 1 working day before the credit date") |
| `active` field value | (use for routing only — describe outcome, not the raw value) |


### A3 — Status Values

| Status | Meaning |
|---|---|
| Active | Schedule active — will trigger on `next_date` |
| Deleted | Deleted — no further debits |


### A4 — Key Limits & Rules

| Item | Detail |
|---|---|
| Max per schedule | ₹1 lakh |
| Max cumulative per day | ₹1 crore across multiple schedules |
| Cancellation advance notice | 3+ working days before next credit date (4 for SBI) |
| Post-cancel confirmed debit | Already-confirmed debit still executes; future ones stop. Funds can be withdrawn. |
| Failed debit | Not retried — add funds manually |


### A5 — Links

| Topic | URL |
|---|---|
| Mandate & schedule management | console.zerodha.com/funds/mandates |


### A6 — Escalation Data Template

When escalating, always include: **client ID, schedule details, and specific issue.**


---

### Preflight (run on every query)

```
1. Verify mandate is active first (via e_mandate_report)
   └─ If mandate not active → mandate issue, not schedule issue.
      Use e_mandate_report protocol.

2. Check if any active schedule exists for this client.
```

### Route

```
Intent / Condition                                          → Rule
──────────────────────────────────────────────────────────────────────
Auto-debit not happening + mandate active + no schedule     → Rule 1
Schedule status check (active / deleted)                    → Rule 2
Why was debit before scheduled date (date confusion)        → Rule 3
Scheduled date changed / shifted unexpectedly               → Rule 4
SIP failed despite active mandate + active schedule         → Rule 5
Error deleting schedule                                     → Rule 6
Cancelled schedule but bank still debited                   → Rule 7
```

### Scope

- Address the client's query about eMandate schedule configuration, timing, and deletion.
- Use **A2** field rules and client-facing terminology in all client communication.
- For mandate-level issues (activation, creation, cancellation), use `e_mandate_report` protocol. For debit transaction issues, use `auto_debit_payins` protocol.

### Fallback

If no route matches, check `e_mandate_report` and `auto_debit_payins` for additional context. If no root cause is found, escalate per **A6**.


---

### Rule 1 — No Schedule Exists

1. Client says auto-debit not happening AND mandate is active (verified via `e_mandate_report`).
2. No active schedule found in this tool.
3. Your eMandate is active, but no schedule has been created. To set up auto-debit, create a schedule at console.zerodha.com/funds/mandates — specify the tag name, credit date, frequency, and amount..


### Rule 2 — Schedule Status Check

1. Determine status (per **A3**):
   a. Active → Your schedule is active. The next fund credit to your Kite account is on [next_date]. Your bank will debit the amount 1 working day before this date..
   b. Deleted → This schedule has been cancelled. No further auto-debits will occur for this schedule. If you'd like to resume, create a new schedule at console.zerodha.com/funds/mandates..


### Rule 3 — Debit vs Credit Date Confusion

1. The date you set is the account credit date — when funds appear in your Kite account. Your bank debits the amount 1 working day before this date to allow processing time..


### Rule 4 — Schedule on Non-Business Day

1. If your scheduled credit date falls on a non-business day (weekend or holiday), the debit is triggered 1 day before the non-business day to ensure funds are available on the next working day..


### Rule 5 — SIP Failed (Schedule Timing Issue)

1. Check if `next_date` is after the SIP execution date.
2. If yes → Your eMandate schedule credit date is after your SIP date. The funds were not available in time. Schedule the eMandate credit date 2–3 days before your SIP date..
3. If `next_date` is before SIP date → check `auto_debit_payins` for the debit status. Apply that tool's protocol.


### Rule 6 — Error Deleting Schedule

1. Schedule deletions may fail if a debit is already being processed. Try again after the current processing cycle completes. If the error persists, try from a different browser or device..
2. If error persists → escalate per **A6**.


### Rule 7 — Cancelled Schedule But Still Debited

1. If you cancelled the schedule after an upcoming debit was already confirmed with your bank, that debit will still be processed. However, all future debits are cancelled. The debited funds will be credited to your Kite account and you can withdraw them if needed.. Post-cancel confirmed debit rules per **A4**.

