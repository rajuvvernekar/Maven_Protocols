# auto_debit_payins

## Description

WHEN TO USE:

When clients:
- Ask about status of an auto-debit / eMandate fund transfer to Kite
- Report money debited from bank via mandate but not reflecting in Kite
- Report auto-debit failed or was not attempted
- Ask why funds were debited a day early
- Ask when auto-debit amount will appear in Kite balance
- Report SIP order failing despite having mandate set up

TRIGGER KEYWORDS: "auto debit", "mandate debit", "schedule debit", "funds not credited", "mandate debit delayed", "auto pay", "NACH debit", "emandate debit", "stock SIP funds", "mandate failed", "debit not reflecting"

TAGS: funds, investments

## Protocol

# AUTO DEBIT PAYINS PROTOCOL

## Section A: Reference Data

### A1 — Fundamentals

-Bank debits funds from the client's account 1 working day before the scheduled Kite credit date. NPCI settles at end-of-day — funds appear in Kite on the scheduled date, not the debit date. The bank considers the opening balance on the debit date — same-day deposits may not count.

-Failed auto-debits are not retried — client must transfer funds manually.

-Max ₹1 lakh per auto-debit schedule; multiple schedules up to ₹1 crore/day cumulative.

-No Zerodha charges for eMandate registration or transactions.

-Bank may charge a penalty for failed debit due to insufficient funds.

-Stock SIPs deduct from Kite balance, not directly from bank — eMandate funds the Kite account in advance.

### A2 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |
|---|---|
| `amount` | Auto-debit amount |

**Non-shareable:**

| Field | Interpretation |
|---|---|
| `status` | Internal debit status — drives diagnosis |
| `user_id` | Internal client identifier |
| `time_created` | Record creation timestamp |
| `time_updated` | Record last update timestamp |
| `transaction_date` | Internal transaction date |
| `provider` | Mandate provider |
| `description` | Internal description |
| `transaction_id` | Internal transaction id |
| `transaction_ref_id` | Internal reference id |
| `bank_name` | Bank name (internal) |
| `mandate_id` | Mandate identifier |
| `failure_reason` | Internal failure reason |

### A3 — Status Values

| Status | Meaning | Action |
|---|---|---|
| Success | Debited and credited to Kite | Invoke `ledger_report` and check `remarks` for "Funds added using auto debit." If ledger entry missing, wait until end of day. |
| Failed | Auto-debit failed — insufficient opening balance or vendor issue | Not retried. Client must add funds manually. |
| Created | Debit request sent to bank (1 day prior) | Funds credit next working day if bank debits successfully. |

### A4 — Timelines

| Event | Timeline |
|---|---|
| Bank debit to Kite credit | 1 working day |
| Created status to credit | Next working day |
| Recommended eMandate schedule before SIP date | 2–3 days before |

### A5 — Links

| Topic | URL |
|---|---|
| Active mandates on Console | console.zerodha.com/funds/mandates |
| How to create an eMandate schedule | https://support.zerodha.com/category/funds/mandate/how-to-set-up-emandates/articles/schedule-emandate-transactions |

### A6 — Escalation Triggers

When escalating, always include: client ID, amount, transaction date, and specific issue.

## Section B: Decision Flow

### Routing

```
Route by scenario
   ├─ Auto-debit status check / money debited but not in Kite → Rule 1
   ├─ SIP failed \+ has mandate set up → Rule 2
   ├─ Why was money debited before scheduled date → Rule 3
   ├─ Receiving "mandate debit delayed" emails repeatedly → Rule 4
   ├─ Double debit complaint → Rule 5
   └─ Coin/MF mandates, mandate creation/cancellation, or schedule setup → Rule 6
```

### Fallback

If no route matches, escalate to human agent per **A6**.

## Section C: Rules

### Rule 1 — Auto-Debit Status Check

1. Determine status per **A3**:
   a. Success → invoke `ledger_report` and check `remarks` for "Funds added using auto debit" matching the amount. If found, confirm credit. If missing, funds reflect by end of day.
   b. Failed → auto-debit could not be completed. Insufficient opening balance or vendor issue. Not retried — client must add funds manually.
   c. Created → debit request sent to bank. Funds credit to Kite by next working day per **A4**.
2. If no matching record:
   a. Invoke `e_mandate_report` — check if an active mandate exists.
   b. If active → invoke `e_mandate_schedule_report` — check if a schedule was created.
   c. If mandate is active but no schedule exists → suggest creating a schedule per **A5**.

### Rule 2 — SIP Failed Due to Insufficient Funds

1. Stock SIPs deduct from Kite balance per **A1**. If the eMandate debit was delayed or failed, the Kite balance may be insufficient when the SIP triggers.
2. Invoke `kite_order_history`, filter for SIP orders. If order status is rejected with reason "Insufficient funds," the SIP failed due to low Kite balance.
3. Check latest auto-debit status and apply Rule 1.
4. Recommend scheduling eMandate credit date 2–3 days before SIP date per **A4**.

### Rule 3 — Early Debit Complaint

1. Bank debits the amount 1 working day before the scheduled credit date per **A1**. NPCI confirms the transaction at end of day — funds appear in Kite on the scheduled date, not the debit date.

### Rule 4 — Repeated "Mandate Debit Delayed" Emails

1. Escalate to human agent per **A6**.

### Rule 5 — Double Debit Complaint

1. Check for multiple records with the same `transaction_id`. If the same `transaction_id` appears twice, it is a duplicate entry — escalate to human agent per **A6**.
2. If two records with different `transaction_id` values both show Success → escalate to human agent per **A6**.
3. If one Success \+ one Failed (different `transaction_id`) → only the successful debit was credited. The failed debit was not processed.

### Rule 6 — Out-of-Scope Redirect

1. For mandate status, creation, or cancellation → invoke `e_mandate_report`.
2. For schedule setup or deletion → invoke `e_mandate_schedule_report`.
3. For Coin/MF mandate queries → invoke `mandate_report`.
