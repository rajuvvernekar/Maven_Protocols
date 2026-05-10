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

TAGS: investments, funds

## Protocol

# MF FUND ALLOCATION REPORT PROTOCOL

---

## Section A: Reference Data

### A1 — Scope

- Shows payments reported to BSE STAR MF and their mapping to orders.  
- One UTR can map to multiple orders (bulk payment).

---

### A2 — NEFT/RTGS/IMPS Exclusion

NEFT/RTGS/IMPS payments go directly to ICCL and do not appear in this report — for these queries, invoke `mf_order_history`.

---

### A3 — Redemption (SELL) Exclusion

This report covers BUY-side payments only — redemption proceeds are credited directly to the client's bank account and are not tracked here. For redemption/sell order details, invoke `mf_order_history`.

---

### A4 — Settlement & Allotment Flag Meanings

| `settled_flag` | `allotment_flag` | Meaning |  
|---|---|---|  
| Y | Y | Payment settled, units allotted. |  
| Y | N | Payment settled, allotment pending from the AMC. |  
| N | — (within T+1 of payment) | Payment received; exchange settlement in progress. Allotment pending — allow one working day. |  
| N | — (beyond T+2) | Payment received but exchange settlement not completed. Order will not process; refund per A5. |

---

### A5 — Refund Status

Standard refund language: "The debited amount will be refunded by BSE STAR MF to your source bank account within 5–7 working days (excluding weekends and holidays)."

| Condition | Communicate |  
|---|---|  
| `refund_utr` populated | Refund processed. Share `refund_amount`, `date_of_refund` (only if present in the report), and `refund_utr`. Direct client to track with their bank using `refund_utr`. |  
| `refund_utr` empty | Apply standard refund language. |

---

### A6 — Field Rules

**Shareable with client:**

| Field | Interpretation |  
|---|---|  
| `order_number` | Order number for the application |  
| `utr_no` | Unique Transaction Reference number for the payment |  
| `payment_date` | Date the payment was made |  
| `total_allocated_amount` | Total amount allocated |  
| `total_settlement_amount` | Total amount settled with the exchange |  
| `total_allotment_amount` | Total amount allotted |  
| `refund_amount` | Refund amount — share only if present |  
| `date_of_refund` | Date the refund was processed — share only if present |  
| `refund_utr` | UTR number for the refund — share only if present |

**Non-shareable:**

| Field | Interpretation |  
|---|---|  
| `settled_flag` | Y = payment settled with exchange; N = not settled |  
| `allotment_flag` | Y = units allotted; N = allotment not yet done |  
| `settlement_number` | Maps to `settlement_id` in `mf_order_history` for cross-referencing |  
| `remitter_acct_no` | Client's bank account used for payment |  
| `error_remarks` | Rejection reason — check for "INVALID BANK ACCOUNT DETAIL" |  
| `cfppg_bank_ref_no` | Maps to `cashier_reference` in `mandate_debit_report` for mandate payment cross-referencing |

---

## Section B: Decision Flow

### Routing

```  
Query relates to MF payment / fund allocation →  
│  
├─ Payment debited but order not allotted / units not showing → Rule 1  
└─ Refund status or refund UTR query → Rule 2  
```

### Fallback

If no root cause is identified → escalate to a human agent with the UTR, payment date, and the specific issue.

---

## Section C: Rules

### Rule 1 — Payment & Allotment Status

Find the row by payment date or UTR. Invoke `mf_order_history` using `order_number` = `exchange_order_id` and `settlement_number` = `settlement_id` to cross-reference the order.

If `error_remarks` contains "INVALID BANK ACCOUNT DETAIL" → escalate to a human agent.

If both `order_number` AND `settlement_number` are null or empty → unmapped payment. Apply A5 refund language.

Check `settled_flag` and `allotment_flag` per A4:

- `settled_flag` = N, within T+1 working day of payment → communicate: payment pending settlement. Allow one working day.  
- `settled_flag` = N, beyond T+2 → order will not process. Apply A5 refund status logic.  
- `settled_flag` = Y, `allotment_flag` = N → communicate: payment settled, allotment pending from the AMC.  
- `settled_flag` = Y, `allotment_flag` = Y → check order status in `mf_order_history`. If status shows Processing → within T+3 working days from `exchange_timestamp` (excluding weekends and trading/settlement holidays) → late delivery of units. Communicate that payment is settled, units are allotted, and holdings will be credited. Beyond T+3 → escalate to a human agent.

---

### Rule 2 — Refund Status

Find the row by payment date or UTR. Check `refund_utr` per A5:

- `refund_utr` populated → share `refund_amount`, `date_of_refund` (only if present in the report), and `refund_utr`. Direct client to track with their bank.  
- `refund_utr` empty → apply A5 refund language.
