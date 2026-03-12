# Proposed Changes: fund_allocation_report
Date: 2026-03-12
Feedback entries: 3 issues

## Issue #1: Facts — add settled_flag and allotment_flag definitions
**Problem**: Flag meanings not explicit in facts, causing potential misinterpretation.
**Current protocol** (exact section):
> ```
> <facts>
> - Shows payments reported to BSE StAR MF and mapping to orders
> - One UTR can map to multiple orders (bulk payment)
> - Unmapped payments refunded within 5-7 working days
> - settlement_number = exchange_order_id from mf_order_history
> - cashier_reference from mandate_debit_report = cfppg_bank_ref_no here
> - **CRITICAL: NEFT/RTGS/IMPS payments go directly to ICCL and will NOT appear in this report. Do NOT check this report for NEFT/RTGS/IMPS orders. If `fund_source` = neft-rtgs in mf_order_history, skip this tool entirely.**
> </facts>
> ```
**Proposed fix**:
```
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
```
**Root cause**: Missing data

---

## Issue #2: Rule 1 — split settled_flag=N into two cases
**Problem**: Maven was telling clients to "wait" indefinitely on orders that had already failed beyond T+2.
**Current protocol** (exact section):
> ```
>   - `settled_flag` = N → "Settlement pending. Allow T+1 business day."
> ```
**Proposed fix**:
```
  - `settled_flag` = N AND within T+1 business day of payment → "Your payment is pending settlement with the exchange. Allow one business day."
  - `settled_flag` = N AND beyond T+2 business days → payment has not been settled and the order will not be processed. Check `refund_utr`:
    - `refund_utr` populated → "Your payment could not be settled. A refund of ₹[refund_amount] has been processed. Use reference number [refund_utr] to track it with your bank."
    - `refund_utr` empty → "Your payment could not be settled and the order will not be processed. The debited amount will be refunded to your bank account within 5-7 working days (excluding weekends and holidays)."
```
**Root cause**: Missing rule

---

## Issue #3: Rule 2 — refund UTR response update
**Problem**: When refund_utr is populated, Maven should not add the 5-7 working day disclaimer since the refund is already initiated. Keep sharing date_of_refund if available, but do not hallucinate a date from order_timestamp.
**Current protocol** (exact section):
> ```
> - Populated → "Refund of ₹[refund_amount] was initiated on [date_of_refund]. Your refund reference number is [refund_utr] — you can use this to track the refund with your bank."
> - Empty → "Refund is being processed. Unmapped payments are refunded within 5-7 working days (excluding weekends and holidays)."
> ```
**Proposed fix**:
```
- `refund_utr` populated → "Your refund of ₹[refund_amount] has been processed on [date_of_refund]. Use reference number [refund_utr] to track it with your bank." Do NOT add the 5-7 working day disclaimer — the refund is already initiated. Only share `date_of_refund` if it is available in the report — NEVER infer or compute a refund date from order_timestamp or any other field.
- `refund_utr` empty → "Your refund is being processed and will be credited within 5-7 working days (excluding weekends and holidays)."
```
**Root cause**: Wrong logic
