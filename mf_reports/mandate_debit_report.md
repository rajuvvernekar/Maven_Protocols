# mandate_debit_report

## Description

WHEN TO USE:

When customer asks about:
- SIP auto-debit didn't happen — verify debit instruction
- Bank debit status for SIP
- Mandate debit failed — need failure reason
- Bank debited but order not processed — trace debit to order

TRIGGER KEYWORDS: "auto-debit failed", "bank not debited", "SIP not deducted from bank", "mandate debit failed", "coin"

## Protocol

# MANDATE DEBIT REPORT PROTOCOL

## Knowledge Base

<knowledge_base>
<facts>
- Mandate debit schedule with transaction status for SIP auto-debits
- Status: Created (instruction sent, bank confirmation pending), Success (bank debited), Failed (bank rejected)
- cashier_reference links to cfppg_bank_ref_no in fund_allocation_report
- If status = Success → bank debited; SIP will process based on ICCL receipt
- If status = Created AND SIP date has passed → debit was not processed; client must place manual order
- If status = Failed → order won't process; client must place manual order
- Do NOT suggest manual order for AMC SIPs — check `sip_type` in sip_report first
</facts>

<field_usage>
  <share>amount | status (as friendly phrase)</share>
  <internal>cashier_reference (cross-ref with fund_allocation_report cfppg_bank_ref_no) | transaction_date | updated_at | created_at</internal>
  <banned>mandate_id | transaction_id | all other fields</banned>
</field_usage>

<debit_status_values>
  <created>Debit instruction sent to bank — pending bank confirmation. Bank has NOT debited yet.</created>
  <success>Bank debited successfully — payment will be mapped to order</success>
  <failed>Bank rejected debit — order will not process this cycle</failed>
</debit_status_values>
</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
Never share `<banned>` fields. Use `<internal>` fields for reasoning only.

### Rule 1: Debit Not Initiated
**if:** No debit record for expected SIP date
**then:** Check **sip_report** (active? mandate linked? get `public_id`) → pass `public_id` as `sip_id` to **sip_modification_log** (modified near trigger?) → If no debit record at all → "Technical issue. Place manual lumpsum order."

### Rule 2: Debit Status Handling
**if:** Checking debit status for a SIP
**Status = Created:**
- SIP `preferred_date` NOT yet passed → "The debit instruction has been sent to your bank. Your funds will be debited on your SIP date. Once debited, the order will be processed automatically."
- SIP `preferred_date` HAS passed → "Your auto-debit was not processed for this SIP cycle. Please place a manual lumpsum order to ensure your investment is not missed."
  - **CRITICAL:** Check `sip_type` in **sip_report** first. Do NOT suggest manual order for AMC SIPs.
**Status = Failed:**
- "Your auto-debit was rejected by your bank for this SIP cycle, likely due to insufficient funds. Please ensure sufficient balance is available before your next SIP date. To invest for this month, please place a manual lumpsum order."
  - **CRITICAL:** Check `sip_type` in **sip_report** first. Do NOT suggest manual order for AMC SIPs.
**Status = Success:**
- Bank debited successfully. Route to Rule 3.

### Rule 3: Success But Order Not Processed
**if:** `status` = Success AND order not allotted
**then:** Use `cashier_reference` → check **fund_allocation_report** (`cfppg_bank_ref_no`). Say: "Your bank has been debited. The payment is being mapped to your order. Allow T+1 to T+2 business days."

### Rule 4: Mandate Deletion
**if:** Client asks how to delete a mandate
**then:**
1. "Before deleting a mandate, you must first unlink it from all active or paused SIPs. Deleting a mandate with linked SIPs will cause those SIPs to fail for future cycles."
2. Steps to unlink: Coin → SIPs → [each SIP] → Unlink mandate. Once all SIPs are unlinked → Coin → Mandates → [mandate] → Delete.
3. If client has no SIPs linked → they can delete directly from Coin → Mandates.
4. Note: Deleting a mandate does NOT cancel your SIPs — SIPs remain active but will require a new mandate or manual payment going forward.
