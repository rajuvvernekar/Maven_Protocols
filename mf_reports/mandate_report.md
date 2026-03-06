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
- eNACH activation: 3 working days (up to 5); UPI autopay: immediate
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
**if:** Client asks about mandate for SIP, Coin, or mutual fund
**then:** Use THIS tool (MF Mandate Report). Do NOT use Console eMandate report.
**if:** Client asks about mandate for equity, F&O, or Console
**then:** Use Console eMandate report, NOT this tool.

### Rule 1: Activation Status
**if:** Customer asks when mandate activates
**then:** Check `status` + `mandate_id` prefix:
- created/pending + ENA* → "eNACH takes up to 3 working days. Created on [time_created]."
- created/pending + ZERODHA* → "UPI mandate should activate immediately. If still pending, create new one."
- success/register_success → "Mandate is active."
- failed/register_failed → "Mandate failed. Create new one. Try UPI autopay for instant activation."
- eNACH pending > 5 working days → escalate

### Rule 2: Active But SIP Not Debiting
**if:** Mandate success but SIP not debiting
**then:** Check **sip_report** `fund_source`. If blank/pool → mandate not linked to SIP. → Check **mandate_debit_report** for debit attempt.

### Rule 3: Cross-Tool
- SIP mandate linkage → **sip_report** (`fund_source`)
- Debit execution status → **mandate_debit_report**
