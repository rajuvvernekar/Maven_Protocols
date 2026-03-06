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
- Status: Created (instruction sent), Success (bank debited), Failed (bank rejected)
- cashier_reference links to cfppg_bank_ref_no in fund_allocation_report
- If status = Created/Success and client claims debited → SIP will process based on ICCL receipt
- If status = Failed → order won't process; client must place manual order
</facts>

<field_usage>
  <share>amount | status (as friendly phrase)</share>
  <internal>cashier_reference (cross-ref with fund_allocation_report cfppg_bank_ref_no) | transaction_date | updated_at | created_at</internal>
  <banned>mandate_id | transaction_id | all other fields</banned>
</field_usage>

<debit_status_values>
  <created>Debit instruction sent to bank — pending</created>
  <success>Bank debited successfully — payment will be mapped</success>
  <failed>Bank rejected — insufficient funds, revoked mandate, or bank error</failed>
</debit_status_values>
</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
Never share `<banned>` fields. Use `<internal>` fields for reasoning only.

### Rule 1: Debit Not Initiated
**if:** No debit record for expected SIP date
**then:** Check **sip_report** (active? mandate linked?) → **sip_modification_log** (modified near trigger?) → If no debit record at all → "Technical issue. Place manual lumpsum order."

### Rule 2: Debit Failed
**if:** `status` = Failed
**then:** Common causes:
- Insufficient funds → "Ensure sufficient balance before SIP date."
- Mandate revoked → "Bank revoked mandate. Create new one."
- Bank rejected → "Check with bank if auto-debit is enabled."
"For this month, place a manual lumpsum order."

### Rule 3: Success But Order Not Processed
**if:** `status` = Success AND order not allotted
**then:** Use `cashier_reference` → check **fund_allocation_report** (`cfppg_bank_ref_no`). "Bank debited. Payment being mapped. Allow T+1 to T+2 business days."

### Rule 4: Cross-Tool
- SIP config/status → **sip_report**
- SIP modification near trigger → **sip_modification_log**
- Payment-to-order mapping → **fund_allocation_report** (match `cashier_reference` = `cfppg_bank_ref_no`)
- Order status after mapping → **mf_order_history**
