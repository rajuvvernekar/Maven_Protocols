# sip_modification_log

## Description

WHEN TO USE:

When need to:
- Verify when a SIP was paused, resumed, modified, or deleted
- Investigate SIP not triggering — check if modification near trigger date
- Confirm customer did/didn't make SIP changes
- SWP or STP modification verification

REQUIRES: SIP `public_id` from sip_report as input (mapped to `sip_id` here).

TRIGGER KEYWORDS: "modified SIP", "changed SIP date", "paused SIP", "who changed my SIP", "when was SIP cancelled", "coin"

## Protocol

# SIP MODIFICATION LOG PROTOCOL

## Knowledge Base

<knowledge_base>
<facts>
- Shows historical modifications for a specific SIP/SWP/STP
- REQUIRES public_id from sip_report as input (field here is `sip_id`, same value)
- type values: sip_edit, sip_delete, swp_edit, swp_delete, stp_edit, stp_delete
- Modification within 1-2 days of trigger date → current SIP order will not be placed, starts from next SIP date
- All modifications initiated from client's device (no system pauses except AMC SIP auto-cancel)
- **CRITICAL: This tool is the ONLY authoritative source for SIP pause/modify/delete dates. The `last_sip_at` field in sip_report is the date of the last SIP order execution, NOT the pause or modification date. NEVER use `last_sip_at` as the pause date.**
</facts>

<field_usage>
  <share>type (modification type) | modified_at (date of change) — in customer-friendly language</share>
  <internal>sip_id (= public_id from sip_report)</internal>
  <banned>client_id | status (null) | swp_status (null) | timestamp</banned>
</field_usage>
</knowledge_base>

---

## Business Rules

### Rule 0: Get public_id First
**if:** This tool invoked
**then:** Must have SIP `public_id` from **sip_report**. If not, check sip_report first.

### Rule 1: Modification Near Trigger
**if:** SIP didn't trigger AND modification found near preferred_date
**then:** "Your SIP was [modified/paused/deleted] on [modified_at], within 1-2 days of execution date. Your current SIP order will not be placed. It will start working from the next SIP date."

### Rule 2: Customer Claims No Change
**if:** Customer says they didn't modify
**then:** "Our records show this modification on [modified_at] from your account. SIP changes can only be made from Coin app or web." Never expose internal IDs.

### Rule 3: Cross-Tool
- Current SIP status → **sip_report**
- SIP order after modification → **mf_order_history**

### Rule 4: Date Accuracy
**CRITICAL:** When reading `modified_at`, verify the full date (day, month, year) carefully before sharing with the client. Common errors include confusing months (e.g., January vs February) or years. Always double-check the date value before including it in the response.
