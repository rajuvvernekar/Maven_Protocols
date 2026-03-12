# fund_allocation_report

## Description

WHEN TO USE:

When customer asks about:
- Money debited but order not allotted — payment mapping
- Refund status or refund UTR
- Payment mapped to different order
- Bulk payment order mapping
- NAV dispute (cross-check with MF Order History payment_updated_at)

TRIGGER KEYWORDS: "money deducted but not invested", "refund UTR", "payment mapped", "refund status", "double debit", "coin"

## Protocol

# MF FUND ALLOCATION REPORT PROTOCOL

## Knowledge Base

<knowledge_base>
<facts>
- Shows payments reported to BSE StAR MF and mapping to orders
- One UTR can map to multiple orders (bulk payment)
- Unmapped payments refunded within 5-7 working days
- settlement_number = exchange_order_id from mf_order_history
- cashier_reference from mandate_debit_report = cfppg_bank_ref_no here
- **CRITICAL: NEFT/RTGS/IMPS payments go directly to ICCL and will NOT appear in this report. Do NOT check this report for NEFT/RTGS/IMPS orders. If `fund_source` = neft-rtgs in mf_order_history, skip this tool entirely.**
- settled_flag = Y means payment has been settled with the exchange. settled_flag = N means payment has NOT been settled — the order will not be processed.
- allotment_flag = Y means units have been allotted. allotment_flag = N means allotment has NOT happened yet.
</facts>
<field_usage>
  <share>order_number | utr_no | payment_date | total_allocated_amount | total_settlement_amount | total_allotment_amount | refund_amount (if entry exists) | date_of_refund (if entry exists) | refund_utr (if entry exists)</share>
  <internal>settled_flag (Y/N) | allotment_flag (Y/N) | settlement_number (= exchange_order_id) | remitter_acct_no | error_remarks | cfppg_bank_ref_no</internal>
  <banned>order_process_duplicate_pg_bank | duplicate_pg_bank | import_filename | total_amount | remaining_amount | remaining_amount_settlement | remaining_amount_allotment | cm_bankname | ifsc_code | cm_tax_status | account_type | payment_mode | id | starmf_id</banned>
</field_usage>
</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
Never share `<banned>` fields. Use `<internal>` fields for reasoning only. NEVER mention field names like "Settled Flag", "Allotment Flag", or any internal field names/values to the customer. Use plain language: "Payment settled" not "Settled Flag = Y".

### Rule 0.5: NEFT/RTGS/IMPS — Do Not Use
**if:** `fund_source` = neft-rtgs in **mf_order_history**, OR client mentions NEFT/RTGS/IMPS payment
**then:** Do NOT check this report. NEFT/RTGS/IMPS payments go directly to ICCL and will not appear here. Refer to **mf_order_history** Rule 7 for NEFT/RTGS/IMPS handling.

### Rule 1: Payment Debited But Not Allotted
**if:** Customer says money debited, order not allotted
**then:** Find payment by date/UTR. IMMEDIATELY check `error_remarks` first:
- `error_remarks` contains "INVALID BANK ACCOUNT DETAIL" → **ESCALATE TO AGENT immediately.** Typically occurs after a bank modification. Do not continue to further checks.
- Then check `settled_flag` and `allotment_flag`:
  - `settled_flag` = Y AND `allotment_flag` = Y → incremental file sync delay. Say: "Your payment has been settled and units allotted by the exchange. There is a short delay in the update reflecting on Coin due to a file sync. Your holdings will update automatically — no action required."
  - `settled_flag` = Y AND `allotment_flag` = N → "Payment settled. Allotment pending from AMC."
  - `settled_flag` = N AND within T+1 business day of payment → "Your payment is pending settlement with the exchange. Allow one business day."
  - `settled_flag` = N AND beyond T+2 business days → payment has not been settled and the order will not be processed. Check `refund_utr`:
    - `refund_utr` populated → "Your payment could not be settled. A refund of ₹[refund_amount] has been processed. Use reference number [refund_utr] to track it with your bank."
    - `refund_utr` empty → "Your payment could not be settled and the order will not be processed. The debited amount will be refunded to your bank account within 5-7 working days (excluding weekends and holidays)."
- No entry → "Payment not yet reflected. Allow 24h. If not visible, refund within 5-7 working days (excluding weekends and holidays)."

### Rule 2: Refund Status
**if:** Customer asks about refund
**then:** Check `refund_amount`, `date_of_refund`, `refund_utr`:
- `refund_utr` populated → "Your refund of ₹[refund_amount] has been processed on [date_of_refund]. Use reference number [refund_utr] to track it with your bank." Do NOT add the 5-7 working day disclaimer — the refund is already initiated. Only share `date_of_refund` if it is available in the report — NEVER infer or compute a refund date from order_timestamp or any other field.
- `refund_utr` empty → "Your refund is being processed and will be credited within 5-7 working days (excluding weekends and holidays)."
**CRITICAL — REFUND DATE:** NEVER compute or commit to a specific refund credit date. Always give the range only. Do not say "you will receive the refund by [date]."
