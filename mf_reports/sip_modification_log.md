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
- type values: sip_edit, sip_delete, swp_edit, swp_delete, stp_edit, stp_delete — always translate to plain language, never share raw values
- Modification within 1-2 days of trigger date → current SIP order will not be placed, starts from next SIP date
- All modifications initiated from client's device (no system pauses except AMC SIP auto-cancel)
- **CRITICAL: This tool is the ONLY authoritative source for SIP pause/modify/delete dates. The `last_sip_at` field in sip_report is the date of the last SIP order execution, NOT the pause or modification date. NEVER use `last_sip_at` as the pause date.**
</facts>

<field_usage>
  <share>type (as plain language — see Rule 1) | modified_at (date of change) — in customer-friendly language</share>
  <internal>sip_id (= public_id from sip_report)</internal>
  <banned>client_id | status (null) | swp_status (null) | timestamp</banned>
</field_usage>
</knowledge_base>

---

## Business Rules

### Rule 0: Get public_id First — HARD BLOCK
**if:** This tool invoked
**then:** STOP. Verify `public_id` is available from **sip_report** before querying this tool.
- `public_id` available → proceed.
- `public_id` NOT available → fetch **sip_report** first to retrieve `public_id`. Do NOT query this tool without it — results will be incorrect or empty.

### Rule 0.5: last_sip_at Is NOT the Modification Date
**CRITICAL:** NEVER use `last_sip_at` from sip_report as the SIP pause, modification, or deletion date. `last_sip_at` is the date of the last SIP order execution only.
- To find when a SIP was paused/modified/deleted → use `modified_at` from THIS tool only.
- If this tool shows no modification entries → the SIP was not paused or modified. Do not infer a pause date from any other field.

### Rule 1: Modification Near Trigger
**if:** SIP didn't trigger AND modification found near preferred_date
**then:** Translate `type` to plain language before sharing — never share raw values:
- edit types (sip_edit, swp_edit, stp_edit) → "Your SIP/SWP/STP was modified"
- delete types (sip_delete, swp_delete, stp_delete) → "Your SIP/SWP/STP was deleted/cancelled"
Say: "Your [SIP/SWP/STP] was [modified/deleted] on [modified_at], within 1-2 days of the execution date. Your current instalment will not be placed. It will start from the next cycle."

### Rule 2: Customer Claims No Change
**if:** Customer says they didn't modify
**then:** "Our records show a change was made to your SIP on [modified_at] from your account. SIP changes can only be made from the Coin app or web." Never expose internal IDs or raw field values.

### Rule 4: Date Accuracy
**CRITICAL:** When reading `modified_at`, verify the full date (day, month, year) carefully before sharing with the client. Common errors include confusing months (e.g., January vs February) or years. Always double-check the date value before including it in the response.

### Rule 5: No Modification Found
**if:** No entries found in sip_modification_log for this SIP/SWP/STP
**then:** "Our records show no modifications, pauses, or cancellations were made to this SIP."
- If investigating SIP-not-triggered → route back to **sip_report** Rule 1 sequential check to continue diagnosis (mandate, order status, etc.).
- Do NOT infer a modification from any other field (e.g. `last_sip_at`, `next_sip_date`).
