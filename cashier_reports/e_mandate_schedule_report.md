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

TAGS: funds, investments

## Protocol

# E MANDATE SCHEDULE REPORT PROTOCOL

## Section A: Reference Data

### A1 — Fundamentals

- Bank debits 1 working day before the scheduled credit date. If the credit date falls on a non-business day (weekend/holiday), the debit shifts to 1 day before the non-business day.  
- Failed debits are not retried — client must add funds manually. Mandate must be active before creating schedules.  
- Stock SIPs deduct from Kite balance, not directly from bank — eMandate funds the Kite account in advance.

### A2 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |  
|---|---|  
| `next_date` | Next credit date — communicate as "next credit date" or "next scheduled date" |  
| `next_debit_date` | Internal — explain to client as "your bank debits 1 working day before the credit date" |  
| `active` | Use for routing only — describe outcome, not the raw value |

**Non-shareable:**

| Field | Interpretation |  
|---|---|  
| `name` | Internal schedule name |  
| `creation` | Schedule creation timestamp |  
| `tag` | Schedule tag |  
| `start_date` | Internal start date |  
| `schedule_date` | Internal schedule date |  
| `deactivation_date` | Internal deactivation date |

### A3 — Status Values

| Status | Meaning |  
|---|---|  
| Active | Schedule active — will trigger on `next_date` |  
| Deleted | Deleted — no further debits |  
| Other | Deletion or state change in progress |

### A4 — Key Limits & Rules

| Item | Detail |  
|---|---|  
| Max per schedule | ₹1 lakh |  
| Max cumulative per day | ₹1 crore across multiple schedules |  
| Cancellation advance notice | 3+ working days before ‘next_date’ (4 for SBI) |  
| Post-cancel confirmed debit | Already-confirmed debit still executes; future ones stop. Funds can be withdrawn. |  
| Failed debit | Not retried — add funds manually |  
| Recommended eMandate credit date before SIP | 2–3 days before SIP date |

### A5 — Links

| Topic | URL |  
|---|---|  
| Mandate & schedule management | console.zerodha.com/funds/mandates |  
| How to create an eMandate schedule | https://support.zerodha.com/category/funds/mandate/how-to-set-up-emandates/articles/schedule-emandate-transactions |

### A6 — Escalation Triggers

When escalating, always include: client ID, schedule details, and specific issue.

## Section B: Decision Flow

### Routing

```  
Route by scenario  
   ├─ Auto-debit not happening \+ mandate active \+ no active schedule → Rule 1  
   ├─ Schedule status check (active / deleted) → Rule 2  
   ├─ SIP failed despite active mandate \+ active schedule → Rule 3  
   ├─ Error deleting schedule → Rule 4  
   └─ Cancelled schedule but bank still debited → Rule 5  
```

### Fallback

If no route matches, escalate to human agent per **A6**.

## Section C: Rules

### Rule 1 — No Schedule Exists

1. If no records exist (count = 0) → no schedule has been created. Direct client to create a schedule per **A5**.  
2. If `active` = "Deleted" → schedule has been cancelled and is no longer active. Direct to **A5** to create a new schedule.

### Rule 2 — Schedule Status Check

1. Determine status per **A3**:  
   a. Active → confirm next credit to Kite is on `next_date`. Bank debits 1 working day before this date per **A1**.  
   b. Deleted → schedule cancelled; no further auto-debits. Direct to **A5** to create a new schedule if needed.

### Rule 3 — SIP Failed (Insufficient Kite Balance)

1. Stock SIPs deduct from Kite balance per **A1**. If the eMandate debit was delayed or failed, the Kite balance may be insufficient when the SIP triggers.  
2. Invoke `kite_order_history`, filter for SIP orders. If order status is rejected with reason "Insufficient funds," the SIP failed due to low Kite balance.  
3. Invoke `auto_debit_payins` to check the latest auto-debit status.  
4. Recommend scheduling eMandate credit date 2–3 days before SIP date per **A4**.

### Rule 4 — Error Deleting Schedule

1. Check `active`. If value is other than "Active" or "Deleted" per **A3** → deletion is in progress; inform client to wait.  
2. If `active` = "Active" → deletion may have failed because a debit is already being processed. Suggest retry after the current processing cycle completes, or from a different browser/device.  
3. If error persists → escalate to human agent per **A6**.

### Rule 5 — Cancelled Schedule But Still Debited

1. Check `deactivation_date` against `next_debit_date`. If the schedule was cancelled after the bank had already initiated the debit, that debit will still execute per **A4**.  
2. Future debits are cancelled. Debited funds will be credited to Kite and can be withdrawn.
