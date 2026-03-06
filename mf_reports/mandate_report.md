# mandate_report

## Description

WHEN TO USE:

When customer asks about:
- Mandate status (created/pending/active/failed/cancelled)
- Mandate not activating or stuck
- Mandate activation timeline
- Which bank mandate is linked to

TRIGGER KEYWORDS: "mandate status", "mandate pending", "mandate failed", "eNACH", "autopay setup", "coin"

## Protocol

# MANDATE REPORT PROTOCOL

## Knowledge Base

<knowledge_base>
<facts>
- All MF/Coin mandates with current status
- **CRITICAL: This report is for MF/Coin mandates ONLY. Console/equity mandates are a SEPARATE report and NOT interchangeable. If client asks about a mandate for SIP/Coin, always use THIS tool, not Console eMandate.**
- mandate_id prefix: ZERODHA* = UPI autopay; ENA* = Digio eNACH
- eNACH activation: 3 working days (up to 5); UPI autopay: activates within 2 minutes of PIN confirmation
- UPI mandate requires client to complete UPI PIN confirmation to activate. If PIN not completed, mandate stays in pending/created and is auto-cancelled by 11 PM on the same day.
- Mandate must be linked to SIP for auto-debit
- To delete mandate: unlink all active/paused SIPs first
- Coin mandates ≠ Console mandates (not interchangeable)
</facts>

<field_usage>
  <share>status (as friendly phrase) | time_created</share>
  <internal>mandate_id (type identification: ZERODHA*/ENA*) | time_updated | bank_name</internal>
  <banned>client_id | umrn | merchant_name | bank_account_number | bank_ifsc_code | verification_date | cancellation_date</banned>
</field_usage>

<status_values>
  <created>Creation initiated, pending verification</created>
  <pending>Awaiting bank approval</pending>
  <success>Active — ready for auto-debit</success>
  <register_success>Registered at bank</register_success>
  <failed>Creation/registration failed</failed>
  <register_failed>Registration failed at bank</register_failed>
  <pending_cancellation>Cancellation in progress</pending_cancellation>
  <waiting_confirm_cancellation>Awaiting bank cancellation confirmation</waiting_confirm_cancellation>
  <cancelled>Cancelled</cancelled>
  <paused>Paused</paused>
</status_values>
</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
Never share `<banned>` fields. Use `<internal>` fields for reasoning only.

### Rule 0.5: Tool Routing
**CRITICAL:** Always identify mandate context before selecting tool:
- Client asks about mandate for SIP, Coin, or mutual fund → use THIS tool (MF Mandate Report). NEVER use Console eMandate report.
- Client asks about mandate for equity, F&O, or Console trading → use Console eMandate report, NOT this tool.
- If unclear → default to THIS tool and verify using `mandate_id` prefix: ZERODHA* or ENA* = Coin/MF mandate; other prefixes = Console mandate.

### Rule 1: Activation Status
**if:** Customer asks when mandate activates
**then:** Check `status` + `mandate_id` prefix:
- created/pending + ENA* → "eNACH takes up to 3 working days. Created on [time_created]."
- created/pending + ZERODHA* → Check `time_created`:
  - Created within last 2 minutes → "Your UPI mandate is being activated. Please wait a moment and check again."
  - Created more than 2 minutes ago → "UPI mandate activation requires completing the UPI PIN confirmation. If you did not complete the PIN step, the mandate will be auto-cancelled by 11 PM today. Please create a new mandate and ensure you complete the UPI PIN confirmation to activate it."
- success/register_success → "Mandate is active."
- failed/register_failed → "Mandate failed. Please create a new one. Try UPI autopay for faster activation — it activates within 2 minutes of PIN confirmation."
- eNACH pending > 5 working days → escalate.

### Rule 2: Active But SIP Not Debiting
**if:** Mandate success but SIP not debiting
**then:** Check **sip_report** `fund_source`. If blank/pool → mandate not linked to SIP. → Check **mandate_debit_report** for debit attempt.
