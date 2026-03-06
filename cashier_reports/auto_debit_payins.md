# auto_debit_payins

## Description

WHEN TO USE:

- Customer asks about status of an auto-debit / eMandate fund transfer to Kite
- Customer says money was debited from bank via mandate but not reflecting in Kite
- Customer reports auto-debit failed or was not attempted
- Customer asks why funds were debited a day early
- Customer asks when auto-debit amount will appear in Kite balance
- Customer confused about SIP order failing despite having mandate set up

TRIGGER KEYWORDS: "auto debit", "mandate debit", "schedule debit", "funds not credited", "mandate debit delayed", "auto pay", "NACH debit", "emandate debit", "stock SIP funds", "mandate failed", "debit not reflecting"

## Protocol

# AUTO_DEBIT_PAYINS PROTOCOL

## Knowledge Base

<knowledge_base>
<facts>
- Console eMandate auto-debits fund the Kite trading account — not Coin MF mandates
- Bank debits 1 working day before scheduled credit date (NPCI settles end-of-day)
- Bank considers opening balance on debit date — same-day deposits may not count
- Failed auto-debit is NOT retried — client must transfer funds manually
- Max ₹1 lakh per schedule; multiple schedules up to ₹1 crore/day cumulative
- No Zerodha charges for eMandate registration or transactions
- Bank may charge penalty for failed debit (insufficient funds)
- Stock SIPs deduct from Kite balance, NOT directly from bank — eMandate funds Kite account
- Schedule eMandate 2-3 days before stock SIP date for fund availability
- Successful debit appears in ledger as "Funds added using auto debit"
</facts>

<field_usage>
  <share>amount</share>
  <banned>user_id | time_created | time_updated | transaction_date | provider | description | transaction_id | transaction_ref_id | bank_name | mandate_id | failure_reason | status</banned>
</field_usage>

<status_values>
  <success>Debited and credited to Kite. Verify via ledger "Funds added using auto debit". If ledger entry missing, wait until end of day.</success>
  <failed>Auto-debit failed. Likely insufficient opening balance or vendor issue. Not retried — add funds manually.</failed>
  <created>Debit request sent to bank (1 day prior). Funds credit next working day if bank debits successfully.</created>
</status_values>

<timelines>
  <debit_to_credit>1 working day</debit_to_credit>
  <created_to_credit>Next working day</created_to_credit>
</timelines>

<links>
  <mandate_console>console.zerodha.com/funds/mandates</mandate_console>
</links>
</knowledge_base>

---

## Business Rules

### Rule 0: Tool Scope Check
**if:** Query is about Coin/MF mandate, OR mandate creation/cancellation, OR schedule setup/deletion
**then:** This tool does not cover that. Use `e_mandate_report` for mandate status, `e_mandate_schedule_report` for schedule issues. Coin mandates are a separate system.

### Rule 1: Auto-Debit Successful
**if:** `status` = "success"
**then:** Check `ledger_report` for entry "Funds added using auto debit" matching the amount.
- If ledger entry found: "Your auto-debit of ₹[amount] has been successfully credited to your Kite account."
- If ledger entry NOT found: "Your auto-debit of ₹[amount] has been processed successfully. The funds should reflect in your Kite balance by end of day."

### Rule 2: Auto-Debit Failed
**if:** `status` = "failed"
**then:** "Your scheduled auto-debit of ₹[amount] could not be completed. This usually happens when the bank account did not have sufficient opening balance at the time of debit. The bank considers the opening balance on the debit date — funds added to your bank on the same day may not be considered. Failed auto-debits are not retried. You can add funds manually via Kite's 'Add Funds' option."

### Rule 3: Auto-Debit Created (Pending)
**if:** `status` = "created"
**then:** "The debit request for ₹[amount] has been sent to your bank. Your bank will debit the amount during banking hours, and the funds will be credited to your Kite account by the next working day."

### Rule 4: Money Debited But Not in Kite
**if:** Customer says bank debited but Kite balance not updated AND `status` = "success"
**then:** Apply Rule 1 (check ledger). If ledger entry missing, inform client funds reflect by end of day.

**if:** Customer says bank debited but Kite balance not updated AND `status` = "created"
**then:** Apply Rule 3.

**if:** No matching record found in auto_debit_payins
**then:** "I don't see a matching auto-debit record for this amount. Please confirm the debit is from the Console eMandate (not a Coin MF mandate or manual transfer). You can verify your active mandates at console.zerodha.com/funds/mandates."

### Rule 5: SIP Failed Due to Insufficient Funds
**if:** Customer reports stock SIP rejected + has mandate set up
**then:** "Stock SIPs deduct funds from your Kite account balance, not directly from your bank. The eMandate transfers funds from your bank to Kite in advance. If the eMandate debit was delayed or failed, your SIP may fail due to insufficient balance. To avoid this, schedule your eMandate credit date 2-3 days before your SIP date."

Check `auto_debit_payins` for latest debit status and respond per Rule 1/2/3.

### Rule 6: Early Debit Complaint
**if:** Customer asks why money was debited before the scheduled date
**then:** "Your bank debits the amount 1 working day before the scheduled credit date. This is because eMandate transfers take one working day to process — the NPCI confirms the transaction at end of day, and the funds appear in your Kite account on the scheduled date."

### Rule 7: Repeated Debit Delay Emails
**if:** Customer reports receiving "mandate debit delayed" emails repeatedly
**then:** Check `auto_debit_payins` for latest status:
- If `failed`: Apply Rule 2. Explain the debit was attempted but failed.
- If `created`: Apply Rule 3. The request is pending bank confirmation.
- If no record: Check `e_mandate_report` for mandate status (may be inactive/pending) and `e_mandate_schedule_report` for schedule status (may be deleted/not created).

### Rule 8: Double Debit Complaint
**if:** Customer reports being debited twice for the same mandate
**then:** Check `auto_debit_payins` for multiple records. If two successful debits exist for same period, ESCALATE. If one success + one failed, explain only the successful one was credited.

### Rule 9: Protect Internal Fields
**NEVER expose:** `status`, `user_id`, `time_created`, `time_updated`, `transaction_date`, `provider`, `description`, `transaction_id`, `transaction_ref_id`, `bank_name`, `mandate_id`, `failure_reason`
**Can share:** `amount` (when relevant to confirm transaction)
