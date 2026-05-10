# mandate_debit_report

## Description

WHEN TO USE:

When clients:
- Report SIP auto-debit didn't happen (verify debit instruction)
- Ask about bank debit status for SIP
- Report mandate debit failed (need failure reason)
- Report bank debited but order not processed (trace debit to order)

TRIGGER KEYWORDS: "auto-debit failed", "bank not debited", "SIP not deducted from bank", "mandate debit failed", "coin"

TAGS: investments, funds

## Protocol

# MANDATE DEBIT REPORT PROTOCOL

---

## Section A: Reference Data

---

### A1 — Fundamentals

-Failed debits are not retried automatically — the client must add funds manually for that cycle. The mandate must be active before debits can be processed.

-`order_id` on this protocol's data maps to `cashier_reference` in `fund_allocation_report`.

-For Zerodha SIPs, a missed or failed debit can be covered by placing a manual lumpsum order. AMC SIPs cannot have manual lumpsum orders placed against them.

---

### A2 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |  
|---|---|  
| `amount` | Debit amount |  
| `status` | Debit status — translate per A3 |  
| `remark` | Debit remark — communicate in plain language per A4 |

**Non-shareable:**

| Field | Interpretation |  
|---|---|  
| `created_at` | Record creation timestamp |  
| `transaction_timestamp` | Timestamp of the actual debit attempt |  
| `order_id` | Maps to `cashier_reference` in `fund_allocation_report` per A1 |  
| `order_type` | Type of SIP order associated with the debit |  
| `mandate_id` | Internal identifier linking to the associated mandate record |  
| `umrn` | Bank-assigned mandate registration number |  
| `transaction_id` | Internal transaction identifier |  
| `provider_transaction_id` | Payment provider's transaction identifier |  
| `bank_reference` | Bank-assigned reference for the debit transaction |  
| `tag` | Internal tag |  
| `merchant` | Mandate issuer entity (Coin/Zerodha) |  
| `type` | Mandate type — `autopay` (UPI) or `enach` |  
| `provider` | Mandate provider — `ybl` (UPI autopay) or `digio` (eNACH) |

### A3 — Debit Status Values

| Status | Meaning |  
|---|---|  
| draft | Debit request created, scheduled for debit on the scheduled date |  
| success | Bank debited successfully — payment will be mapped to the order |  
| pending | Debit request has an issue or execution is pending — `remark` carries the cause |  
| failed | Bank rejected the debit — order will not process this cycle |

---

### A4 — Remark Meanings

When `status` = `pending` or `failed`, the `remark` field carries the cause:

| Remark value | Meaning |  
|---|---|  
| Insufficient balance / Balance Insufficient | Insufficient funds in the client's bank account at debit time |  
| Maximum limit exceeded | UPI transaction limit was exceeded |  
| KYC-related issue | KYC issue with the client's bank account |  
| A/c closed | Linked bank account is closed |  
| Unable to Notify the Customer / Mandate notification pending / Mandate notification failed | Network error at the client's bank blocked the debit notification — temporary bank-side issue |  
| SeqNum Mismatch (Remitter) | Technical issue at the client's bank — temporary bank-side issue |

---

### A5 — Juspay Mandate Detection

If `transaction_id` is null or empty in the debit record → the mandate is serviced by Juspay (UPI autopay via Juspay).

Juspay-based mandates do not auto-debit. A payment approval request is sent to the client's UPI app on the scheduled date, and the client must manually approve it. If the approval is missed, no debit happens for that cycle.

---

### A6 — Links

| Topic | URL |  
|---|---|  
| Coin mandate management (creation, linkage, deletion) | https://support.zerodha.com/category/mutual-funds/payments-and-orders/coin-mandates/articles/sip-mandate-on-coin |

---

### A7 — Escalation Triggers

Escalate to human agent when any of the following apply:

- Draft status persists beyond T+2 from `created_at` and the cause is unclear after checking mandate status.  
- Any debit issue with no clear root cause after applying the relevant rules.

Include in escalation: client ID, debit details (date, amount, status, remark), and the specific issue.

---

## Section B: Decision Flow

### Routing

```  
Route by scenario  
   ├─ No debit record for expected date → Rule 1  
   ├─ Debit status = draft → Rule 2  
   ├─ Debit status = success → Rule 3  
   ├─ Debit status = pending → Rule 4  
   ├─ Debit status = failed → Rule 5  
   └─ How to delete a mandate (Coin) → Rule 6  
```

### Fallback

If no debit record exists and SIP-level checks are inconclusive → escalate per A7.

---

## Section C: Rules

---

### Rule 1 — Debit Not Initiated

When no debit record is found for the expected date:

1. Invoke `sip_report` to confirm the SIP is active and check `fund_source` for mandate linkage.  
2. Use `public_id` from `sip_report` as the `sip_id` input. Invoke `sip_modification_log` to check whether the SIP was modified near the trigger date — a recent modification can explain the missing debit.  
3. If neither check explains the missing debit → communicate that there was a technical issue with the auto-debit for this cycle.  
4. For Zerodha SIPs (`sip_type` = `sip` in `sip_report`), advise placing a manual lumpsum order to cover the missed cycle. For AMC SIPs (`sip_type` = `amc_sip`), the next AMC SIP cycle will retry automatically per A1.

---

### Rule 2 — Draft Status

Compare today's date to the scheduled date and `created_at`:

**Scheduled date not yet passed:**

-Communicate that the debit instruction has been sent to the bank and funds will be debited on the scheduled date. Once debited, the order will be processed automatically.

**Scheduled date passed, draft persists beyond T+2 from `created_at`:**

-This typically indicates the mandate was revoked or cancelled from the client's UPI app or bank portal. Communicate this and advise checking mandate status in `mandate_report`; if no active mandate exists, advise creating a new one. Share the relevant link from A6.

**Scheduled date passed, within T+2 window:**

-Check `transaction_id` per A5. If null or empty → Juspay mandate. Communicate the Juspay manual-approval mechanic per A5; if the client missed the approval, no debit happened this cycle. Suggest creating an eNACH mandate as an alternative for fully automatic debits.

-If `transaction_id` is populated → check `sip_type` from `sip_report`. For Zerodha SIPs, communicate that the auto-debit was not processed for this cycle and advise placing a manual lumpsum order. For AMC SIPs, communicate that the auto-debit was not processed; the next cycle will retry automatically.

---

### Rule 3 — Success

Confirm `status` = `success`. Communicate that the bank has been debited successfully.

If the client reports the order has not been allotted yet:

1. Use `order_id` to look up `cashier_reference` in `fund_allocation_report` for payment mapping.  
2. If payment is mapped → invoke `mf_order_history` for the corresponding order status. Communicate the order status.  
3. If payment is not yet mapped → communicate that payment mapping takes T+1 to T+2 business days.

---

### Rule 4 — Pending or Failed Status

-Check `transaction_id` per A5. If null or empty → Juspay mandate. Communicate the Juspay manual-approval mechanic per A5.

-If `transaction_id` is populated → use the `remark` value with A4 to identify the cause. Communicate the cause to the client in plain language.

-For Zerodha SIPs, advise placing a manual lumpsum order to cover the missed cycle. For AMC SIPs, the next cycle will retry automatically.

---

### Rule 6 — Mandate Deletion (Coin)

The mandate deletion process is handled by `mandate_report`. Invoke `mandate_report` for the full deletion process and any follow-up.
