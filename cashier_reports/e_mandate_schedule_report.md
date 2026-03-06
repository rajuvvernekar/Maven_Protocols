# e_mandate_schedule_report

## Description

WHEN TO USE:

- Customer claims auto-debit did not happen — check if schedule exists
- Customer asks about schedule creation, modification, or deletion
- Customer reports error deleting a schedule
- Customer confused about debit date vs credit date
- Customer asks why SIP failed when mandate is active — check if schedule is set up
- Customer wants to pause or stop auto-debit without cancelling mandate
- Customer asks about schedule dates changing unexpectedly

TRIGGER KEYWORDS: "schedule", "auto debit not happening", "debit date", "credit date", "delete schedule", "cancel schedule", "schedule error", "no debit", "SIP failed mandate active", "schedule not created", "stop auto debit"

## Protocol

# E_MANDATE_SCHEDULE_REPORT PROTOCOL

## Knowledge Base

<knowledge_base>
<facts>
- Schedule defines amount, date, frequency for auto-debit from bank to Kite
- Max ₹1 lakh per schedule; cumulative ₹1 crore/day across multiple schedules
- Bank debits 1 working day before scheduled credit date
- Non-business day: debit shifts to 1 day before
- Failed debit NOT retried — add funds manually
- Cancel schedules 3+ working days before next credit date (4 for SBI)
- Post-cancel confirmed debit: that debit still executes, future ones stop; funds can be withdrawn
- Mandate must be active before creating schedules
</facts>

<field_usage>
  <share>next_date (as "next credit date")</share>
  <banned>name | creation | tag | start_date | schedule_date | next_debit_date | deactivation_date</banned>
</field_usage>

<status_values>
  <active>Schedule active — will trigger on next_date</active>
  <deleted>Deleted — no further debits</deleted>
</status_values>

<links>
  <mandate_console>console.zerodha.com/funds/mandates</mandate_console>
</links>
</knowledge_base>

---

## Business Rules

### Rule 0: First Check — Does a Schedule Exist?
**if:** Customer says auto-debit not happening AND mandate is active (verified via e_mandate_report)
**then:** Check e_mandate_schedule_report. If no active schedule found: "Your eMandate is active, but no schedule has been created. To set up auto-debit, create a schedule at console.zerodha.com/funds/mandates — specify the tag name, credit date, frequency, and amount."

### Rule 1: Schedule Active
**if:** `active` = "Active"
**then:** "Your schedule is active. The next fund credit to your Kite account is on [next_date]. Your bank will debit the amount 1 working day before this date."

### Rule 2: Schedule Deleted
**if:** `active` = "Deleted"
**then:** "This schedule has been cancelled. No further auto-debits will occur for this schedule. If you'd like to resume, create a new schedule at console.zerodha.com/funds/mandates."

### Rule 3: Date Confusion (Debit vs Credit)
**if:** Customer asks why debit happened before scheduled date
**then:** "The date you set is the account credit date — when funds appear in your Kite account. Your bank debits the amount 1 working day before this date to allow processing time."

### Rule 4: Schedule on Non-Business Day
**if:** Customer reports date changed or shifted unexpectedly
**then:** "If your scheduled credit date falls on a non-business day (weekend or holiday), the debit is triggered 1 day before the non-business day to ensure funds are available on the next working day."

### Rule 5: SIP Failed — Schedule Timing Issue
**if:** Customer says SIP failed despite active mandate + active schedule
**then:** Check if `next_date` is AFTER the SIP execution date. If so: "Your eMandate schedule credit date is after your SIP date. The funds were not available in time. Schedule the eMandate credit date 2-3 days before your SIP date."

If `next_date` is before SIP date, check `auto_debit_payins` for the debit status.

### Rule 6: Error Deleting Schedule
**if:** Customer reports error when trying to delete schedule
**then:** "Schedule deletions may fail if a debit is already being processed. Try again after the current processing cycle completes. If the error persists, try from a different browser or device." If persistent, ESCALATE.

### Rule 7: Cancelled Schedule But Still Getting Debited
**if:** Customer deleted schedule but bank still debited
**then:** "If you cancelled the schedule after an upcoming debit was already confirmed with your bank, that debit will still be processed. However, all future debits are cancelled. The debited funds will be credited to your Kite account and you can withdraw them if needed."

### Rule 8: Protect Internal Fields
**NEVER expose:** `name`, `creation`, `tag`, `start_date`, `schedule_date`, `next_debit_date`, `deactivation_date`, `active` (raw value)
