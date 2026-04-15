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

## Protocol

# AUTO DEBIT PAYINS PROTOCOL 

---

## Section A: Reference Data

---

### A1 — Fundamentals

This tool shows **Console eMandate auto-debit transactions** that fund the Kite trading account. This is not for Coin/MF mandates — those are a separate system.

Bank debits 1 working day before the scheduled credit date (NPCI settles end-of-day). The bank considers the **opening balance** on the debit date — same-day deposits may not count.

Failed auto-debits are **not retried** — the client must transfer funds manually.


---

### A2 — Field Usage Rules

**Shareable fields:**

`amount`

**Internal-only fields** (use for reasoning; communicate outcomes in plain language):

`status` | `user_id` | `time_created` | `time_updated` | `transaction_date` | `provider` | `description` | `transaction_id` | `transaction_ref_id` | `bank_name` | `mandate_id` | `failure_reason`

All fields except `amount` are internal-only. Use them to diagnose and determine the correct response, but communicate the outcome in plain language without referencing field names or values.

---

### A3 — Status Values

| Status | Meaning | Action |
|---|---|---|
| Success | Debited and credited to Kite | Verify via ledger: "Funds added using auto debit." If ledger entry missing, wait until end of day. |
| Failed | Auto-debit failed — insufficient opening balance or vendor issue | Not retried. Client must add funds manually. |
| Created | Debit request sent to bank (1 day prior) | Funds credit next working day if bank debits successfully. |

---

### A4 — Timelines

| Event | Timeline |
|---|---|
| Bank debit to Kite credit | 1 working day |
| Created status to credit | Next working day |
| Recommended eMandate schedule before SIP date | 2–3 days before |

---

### A5 — Key Facts

- Max ₹1 lakh per schedule; multiple schedules up to ₹1 crore/day cumulative.
- No Zerodha charges for eMandate registration or transactions.
- Bank may charge penalty for failed debit (insufficient funds).
- Stock SIPs deduct from Kite balance, not directly from bank — eMandate funds the Kite account.
- Successful debit appears in ledger as "Funds added using auto debit."

---

### A6 — Related Tools (Out of Scope for This Tool)

| Query Type | Correct Tool |
|---|---|
| Mandate status / creation / cancellation | `e_mandate_report` |
| Schedule setup / deletion | `e_mandate_schedule_report` |
| Coin / MF mandates | Separate system — not covered by this tool or the above |

---

### A7 — Links

| Topic | URL |
|---|---|
| Active mandates on Console | console.zerodha.com/funds/mandates |

---

### A8 — Escalation Data Template

When escalating, always include: **client ID, amount, transaction date, and specific issue.**

---

## Section B: Decision Flow

---

### Preflight (run on every query)

```
1. Determine if query is about Console eMandate auto-debits
   └─ If about Coin/MF mandates, mandate creation/cancellation,
      or schedule setup/deletion → redirect to correct tool per A6.
```

### Route

```
Intent / Condition                                          → Rule
──────────────────────────────────────────────────────────────────────
Auto-debit status check (success/failed/created)            → Rule 1
Money debited from bank but not in Kite                     → Rule 2
SIP failed + has mandate set up                             → Rule 3
Why was money debited before scheduled date                 → Rule 4
Receiving "mandate debit delayed" emails repeatedly         → Rule 5
Double debit complaint                                      → Rule 6
```

### Scope

- Address the client's query about Console eMandate auto-debit transactions only.
- Use **A2** field rules in all client communication — only `amount` is shareable; all other fields are for internal reasoning.
- Redirect Coin/MF mandate and schedule queries to the correct tools per **A6**.

### Fallback

If no route matches, check `e_mandate_report` and `e_mandate_schedule_report` (per **A6**) for additional context. If no root cause is found, escalate per **A8**.

---

## Section C: Rules

---

### Rule 1 — Auto-Debit Status Check

1. Determine status (per **A3**):
   a. Success → check `ledger_report` for entry "Funds added using auto debit" matching the amount.
      - Ledger entry found → Your auto-debit of ₹[amount] has been successfully credited to your Kite account..
      - Ledger entry not found → Your auto-debit of ₹[amount] has been processed successfully. The funds should reflect in your Kite balance by end of day..
   b. Failed → Your scheduled auto-debit of ₹[amount] could not be completed. This usually happens when the bank account did not have sufficient opening balance at the time of debit. The bank considers the opening balance on the debit date — funds added to your bank on the same day may not be considered. Failed auto-debits are not retried. You can add funds manually via Kite's 'Add Funds' option..
   c. Created → The debit request for ₹[amount] has been sent to your bank. Your bank will debit the amount during banking hours, and the funds will be credited to your Kite account by the next working day..

---

### Rule 2 — Money Debited but Not in Kite

1. If status = Success → apply Rule 1 step 1a (check ledger). If missing, funds reflect by end of day.
2. If status = Created → The debit request for ₹[amount] has been sent to your bank. Your bank will debit the amount during banking hours, and the funds will be credited to your Kite account by the next working day.. Timeline per **A4**.
3. If no matching record found → I don't see a matching auto-debit record for this amount. Please confirm the debit is from the Console eMandate (not a Coin MF mandate or manual transfer). You can verify your active mandates at console.zerodha.com/funds/mandates..

---

### Rule 3 — SIP Failed Due to Insufficient Funds

1. Stock SIPs deduct funds from your Kite account balance, not directly from your bank. The eMandate transfers funds from your bank to Kite in advance. If the eMandate debit was delayed or failed, your SIP may fail due to insufficient balance. To avoid this, schedule your eMandate credit date 2–3 days before your SIP date.. Timing recommendation per **A4**.
2. Check latest auto-debit status and apply Rule 1 to inform client of the debit outcome.

---

### Rule 4 — Early Debit Complaint

1. Your bank debits the amount 1 working day before the scheduled credit date. This is because eMandate transfers take one working day to process — the NPCI confirms the transaction at end of day, and the funds appear in your Kite account on the scheduled date.. Timeline per **A4**.

---

### Rule 5 — Repeated "Mandate Debit Delayed" Emails

1. Check latest status in this tool:
   a. Failed → apply Rule 1 step 1b (**A9-R3**).
   b. Created → apply Rule 1 step 1c (**A9-R4**).
   c. No record → check `e_mandate_report` for mandate status (may be inactive/pending) and `e_mandate_schedule_report` for schedule status (may be deleted/not created). Redirect per **A6**.

---

### Rule 6 — Double Debit Complaint

1. Check for multiple records in this tool.
2. If two successful debits exist for the same period → escalate per **A8**.
3. If one success + one failed → explain only the successful one was credited. The failed debit was not processed.

