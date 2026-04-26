# fund_allocation_report

## Description

WHEN TO USE:

When clients:
- Report money debited but order not allotted (payment mapping)
- Ask about refund status or refund UTR
- Report payment mapped to different order
- Ask about bulk payment order mapping
- Dispute NAV (cross-check with MF Order History payment_updated_at)

TRIGGER KEYWORDS: "money deducted but not invested", "refund UTR", "payment mapped", "refund status", "double debit", "coin"

## Protocol


### A1 — Tool Purpose & Scope

- Shows payments reported to BSE StAR MF and their mapping to orders.
- One UTR can map to multiple orders (bulk payment).
- Unmapped payments are refunded within 5–7 working days (excluding weekends and holidays).
- Key cross-reference fields: `settlement_number` = `settlement_id` from mf_order_history. `cashier_reference` from mandate_debit_report = `cfppg_bank_ref_no` here.

### A2 — NEFT/RTGS/IMPS Exclusion

NEFT/RTGS/IMPS payments go directly to ICCL and will not appear in this report. If `fund_source` = neft-rtgs in mf_order_history, or client mentions NEFT/RTGS/IMPS payment, do not check this report. Refer to mf_order_history Rule 7 for NEFT/RTGS/IMPS handling.

### A3 — Settlement & Allotment Flags

| settled_flag | allotment_flag | Meaning | Client-Facing Communication |
|---|---|---|---|
| Y | Y | Payment settled, units allotted | "Your payment has been settled and units allotted by the exchange. There is a short delay in the update reflecting on Coin due to a file sync. Your holdings will update automatically — no action required." |
| Y | N | Payment settled, allotment pending | "Your payment has been settled. Allotment is pending from the AMC." |
| N | — (within T+1 of payment) | Payment pending settlement | "Your payment is pending settlement with the exchange. Allow one business day." |
| N | — (beyond T+2) | Payment not settled, order will not process | Check refund status per **A4** |

### A4 — Refund Status Logic

| Condition | Client-Facing Communication |
|---|---|
| `refund_utr` populated | "Your refund of ₹[refund_amount] has been processed on [date_of_refund]. Use reference number [refund_utr] to track it with your bank." The refund has already been initiated — share the refund amount, date_of_refund (if available in the report), and refund_utr. Direct the client to track with their bank using the reference number. Only share `date_of_refund` if available in the report — never infer or compute from other fields. |
| `refund_utr` empty | "Your payment could not be settled and the order will not be processed. The debited amount will be refunded to your bank account within 5–7 working days (excluding weekends and holidays)." |
| No entry at all | "Payment not yet reflected. Allow 24 hours. If not visible, the amount will be refunded within 5–7 working days (excluding weekends and holidays)." |

Always provide the 5–7 working day range for refund timelines. Specific refund credit dates are not available — only the range is accurate.

### A5 — Error Remarks Escalation

If `error_remarks` contains "INVALID BANK ACCOUNT DETAIL" → escalate to support agent immediately. Typically occurs after a bank modification. Do not continue to further checks.

### A6 — Field Rules

**Shareable with client:** `order_number`, `utr_no`, `payment_date`, `total_allocated_amount`, `total_settlement_amount`, `total_allotment_amount`, `refund_amount` (if entry exists), `date_of_refund` (if entry exists), `refund_utr` (if entry exists).

**Internal reasoning only (use for analysis, do not share):** `settled_flag` (Y/N), `allotment_flag` (Y/N), `settlement_number` (= settlement_id), `remitter_acct_no`, `error_remarks`, `cfppg_bank_ref_no`.

**Suppress (no client use):** `order_process_duplicate_pg_bank`, `duplicate_pg_bank`, `import_filename`, `total_amount`, `remaining_amount`, `remaining_amount_settlement`, `remaining_amount_allotment`, `cm_bankname`, `ifsc_code`, `cm_tax_status`, `account_type`, `payment_mode`, `id`, `starmf_id`.

**Communication rule:** Use plain language for all field values in client responses. Say "Payment settled" instead of "Settled Flag = Y". Describe outcomes, not field names.

### A7 — Cross-Reference Protocols

| Topic | Refer to |
|---|---|
| Order status / settlement_id matching | mf_order_history (settlement_number = exchange_order_id) |
| Mandate debit cross-reference | mandate_debit_report (cashier_reference = cfppg_bank_ref_no) |
| NEFT/RTGS/IMPS payment handling | mf_order_history Rule 7 |

### Preflight (run on every query)

1. **NEFT/RTGS/IMPS gate:** Check if payment method is NEFT/RTGS/IMPS per **A2**. If yes → do not use this tool. Route to mf_order_history.
2. Fetch the fund allocation report for the client's payment/date/UTR.
3. Apply field protection per **A6** — identify shareable, internal, and banned fields.
4. Check `error_remarks` immediately per **A5** — if "INVALID BANK ACCOUNT DETAIL" → escalate before any other processing.
5. Format amounts with ₹ and Indian comma notation. Format dates as DD MMM YYYY.

### Routing Tree

```
Query relates to MF payment / fund allocation →
│
├─ Preflight: NEFT/RTGS/IMPS payment?
│  → Do NOT use this tool. Route to mf_order_history (STOP)
│
├─ Preflight: error_remarks = "INVALID BANK ACCOUNT DETAIL"?
│  → escalate immediately (STOP)
│
├─ Payment debited but order not allotted
│  → Rule 1
│
├─ Client asks about refund status
│  → Rule 2
│
└─ No matching entry
   → "Payment not yet reflected. Allow 24 hours." (per A4)
```

### Scope

- Address: payment-to-order mapping, settlement/allotment status, and refund tracking.

### Fallback

If no entry found and payment is beyond 24 hours → advise 5–7 working day refund timeline per **A4**.


### Rule 1 — Payment Debited But Not Allotted

1. Find the payment by date/UTR.
2. Check `error_remarks` first per **A5**. If "INVALID BANK ACCOUNT DETAIL" → escalate immediately. Do not continue.
3. Check `settled_flag` and `allotment_flag` and respond using the matching row from **A3**.
4. If `settled_flag` = N and beyond T+2 → check refund status per **A4**:
   - `refund_utr` populated → share refund details per **A4**.
   - `refund_utr` empty → "Refund will be credited within 5–7 working days."
5. If no entry found → "Payment not yet reflected. Allow 24 hours. If not visible, refund within 5–7 working days (excluding weekends and holidays)." (Per **A4**.)

### Rule 2 — Refund Status

1. Check `refund_amount`, `date_of_refund`, and `refund_utr`.
2. Respond using the matching condition from **A4**.
3. If `refund_utr` is populated → share amount, date (if available), and reference number. The refund has already been initiated — only the reference details are needed.
4. If `refund_utr` is empty → "Your refund is being processed and will be credited within 5–7 working days (excluding weekends and holidays)."
5. Always provide the range only — specific refund credit dates are not available (per **A4**).
