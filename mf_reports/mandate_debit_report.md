# mandate_debit_report

## Description

WHEN TO USE:

When clients:
- Report SIP auto-debit didn't happen (verify debit instruction)
- Ask about bank debit status for SIP
- Report mandate debit failed (need failure reason)
- Report bank debited but order not processed (trace debit to order)

TRIGGER KEYWORDS: "auto-debit failed", "bank not debited", "SIP not deducted from bank", "mandate debit failed", "coin"

## Protocol

# MANDATE DEBIT REPORT PROTOCOL

---

## Section A: Reference Data

### A1 — Tool Purpose & Scope

- This report shows the mandate debit schedule with transaction status for SIP auto-debits.
- `cashier_reference` links to `cfppg_bank_ref_no` in fund_allocation_report — use for cross-referencing payment mapping.

### A2 — Debit Status Translations

| Internal Status | Meaning | Client-Facing Communication |
|---|---|---|
| Created | Debit instruction sent to bank — pending bank confirmation. Bank has NOT debited yet. | If SIP date not passed: "The debit instruction has been sent to your bank. Your funds will be debited on your SIP date. Once debited, the order will be processed automatically." If SIP date passed: "Your auto-debit was not processed for this SIP cycle." |
| Success | Bank debited successfully — payment will be mapped to order | "Your bank has been debited successfully." → Route to Rule 3 for order status. |
| Failed | Bank rejected debit — order will not process this cycle | "Your auto-debit was rejected by your bank for this SIP cycle, likely due to insufficient funds. Please ensure sufficient balance is available before your next SIP date." |

### A2a — Juspay Mandate Detection

**How to identify:** If `transaction_id` is null/empty in the mandate debit record, the mandate is serviced by Juspay (UPI autopay via Juspay).

**Behavior:** Juspay-based mandates do not auto-debit. Instead, a payment approval request is sent to the client's UPI application on the SIP date. The client must manually approve the payment on the UPI app.

**Applies when status = Created (SIP date passed) or Failed:**
- "Your SIP mandate is processed via UPI autopay (Juspay). Unlike eNACH, this does not auto-debit your bank account. A payment approval request is sent to your UPI app on the SIP date — you need to manually approve it. If you missed the approval, the debit will not be processed for this cycle. You may also consider creating an eNACH mandate instead of UPI autopay to enable fully automatic debits."

### A3 — AMC SIP Manual Order Restriction

When debit status = Created (SIP date passed) or Failed, check `sip_type` in sip_report before suggesting any action. Do not suggest placing a manual lumpsum order for AMC SIPs (`sip_type` = amc_sip). AMC SIP orders are placed by the AMC — the client cannot place manual orders for these.

For Zerodha SIPs (`sip_type` = sip): "To invest for this month, please place a manual lumpsum order."

### A4 — Field Rules

**Shareable with client:** `amount`, `status` (translated per **A2** — use friendly phrases only).

**Internal reasoning only (use for analysis, never share):** `cashier_reference` (cross-reference with fund_allocation_report `cfppg_bank_ref_no`), `transaction_date`, `updated_at`, `created_at`.

**No client use and only reasoning purpose:** `mandate_id`, `transaction_id`, all other fields.

### A5 — Mandate Deletion Process

1. Before deleting a mandate, unlink it from all active or paused SIPs. Deleting a mandate with linked SIPs will cause those SIPs to fail for future cycles.
2. Steps to unlink: Coin → SIPs → [each SIP] → Unlink mandate.
3. Once all SIPs are unlinked: Coin → Mandates → [mandate] → Delete.
4. If client has no SIPs linked → they can delete directly from Coin → Mandates.
5. Deleting a mandate does not cancel SIPs — SIPs remain active but will require a new mandate or manual payment going forward.

### A6 — Cross-Reference Protocols

| Topic | Refer to |
|---|---|
| Payment mapping (cashier_reference → cfppg_bank_ref_no) | fund_allocation_report |
| Order status after debit success | mf_order_history |
| SIP type, mandate linkage, SIP status | sip_report |
| SIP modification near trigger date | sip_modification_log (via public_id from sip_report) |

### A7 — Bank Penalty Charges

Zerodha does not charge for Coin mandate registrations at present. However, the client's bank may charge penalties for failed transactions due to insufficient funds and mandate verification charges. These charges are applied by the bank — not by Zerodha or BSE STAR MF.

Reference: [What are the charges for Coin mandates?](https://support.zerodha.com/category/mutual-funds/coin-web-app/articles/charges-for-coin-mandates)

## Section B: Decision Flow

### Preflight (run on every query)

1. Fetch the mandate debit report for the client and relevant SIP/date.
2. Apply field protection per **A4** — identify shareable, internal, and banned fields.
3. Identify the debit status and translate per **A2**.
4. If debit status requires suggesting manual order → check `sip_type` in sip_report per **A3** before responding.
5. Format amounts with ₹ and Indian comma notation.

### Routing Tree

```
Query relates to mandate debit →
│
├─ No debit record for expected SIP date
│  → Rule 1
│
├─ Debit status check
│  ├─ Created (SIP date not passed) → Rule 2a
│  ├─ Created (SIP date passed) → Rule 2b (check A2a for Juspay first, then A3)
│  ├─ Failed → Rule 2c (check A2a for Juspay first, then A3)
│  └─ Success → Rule 3
│
├─ Success but order not processed / not allotted
│  → Rule 3
│
├─ Client asks how to delete a mandate
│  → Rule 4
│
├─ Client reports bank-applied charges alongside a failed/cancelled debit
│  → Rule 5
│
└─ No matching scenario
   → Check sip_report for SIP-level diagnosis
```

### Scope

- Address: debit status, payment processing, manual order guidance (with AMC SIP check), mandate deletion, and bank-applied penalty charges.
- Internal field values: Transaction IDs and internal field values (per **A4**) are not part of client-facing responses.

### Fallback

If no debit record exists and SIP-level checks are inconclusive → advise manual order (after AMC SIP check per **A3**) and escalate if issue persists.

---

## Section C: Rules

### Rule 1 — Debit Not Initiated

1. No debit record found for the expected SIP date.
2. Check sip_report (per **A6**): is the SIP active? Is a mandate linked (`fund_source` check)?
3. Get `public_id` from sip_report → pass as `sip_id` to sip_modification_log (per **A6**): was the SIP modified near the trigger date?
4. If no debit record and no modification explains it → "There was a technical issue with the auto-debit for this cycle."
5. Check **A3** for SIP type, then advise: "Please place a manual lumpsum order to ensure your investment is not missed." (Zerodha SIP only.)

### Rule 2 — Debit Status Handling

**2a — Created, SIP date not yet passed:**
Respond per **A2**: "The debit instruction has been sent to your bank. Your funds will be debited on your SIP date. Once debited, the order will be processed automatically."

**2b — Created, SIP date has passed:**
First check `transaction_id` per **A2a**: if null/empty → Juspay mandate. Respond with Juspay guidance from **A2a** (manual UPI approval required, suggest eNACH alternative).
Otherwise, check `sip_type` per **A3** before responding.
- Zerodha SIP: "Your auto-debit was not processed for this SIP cycle. Please place a manual lumpsum order to ensure your investment is not missed."
- AMC SIP: "Your auto-debit was not processed for this SIP cycle." (Do not suggest manual order.)

**2c — Failed:**
First check `transaction_id` per **A2a**: if null/empty → Juspay mandate. Respond with Juspay guidance from **A2a** (manual UPI approval required, suggest eNACH alternative).
Otherwise, check `sip_type` per **A3** before responding.
- Zerodha SIP: "Your auto-debit was rejected by your bank for this SIP cycle, likely due to insufficient funds. Please ensure sufficient balance is available before your next SIP date. To invest for this month, please place a manual lumpsum order."
- AMC SIP: "Your auto-debit was rejected by your bank for this SIP cycle, likely due to insufficient funds. Please ensure sufficient balance is available before your next SIP date." (Do not suggest manual order.)

### Rule 3 — Success But Order Not Processed

1. Confirm: `status` = Success but order is not yet allotted.
2. Use `cashier_reference` → check fund_allocation_report for `cfppg_bank_ref_no` match (per **A6**).
3. If payment mapped → check mf_order_history (per **A6**) for the corresponding order status.
4. Respond: "Your bank has been debited. The payment is being mapped to your order. Allow T+1 to T+2 business days."

### Rule 4 — Mandate Deletion

1. Respond using the process from **A5**:
   - "Before deleting a mandate, you must first unlink it from all active or paused SIPs. Deleting a mandate with linked SIPs will cause those SIPs to fail for future cycles."
   - Steps to unlink: "Coin → SIPs → [each SIP] → Unlink mandate."
   - Once all SIPs unlinked: "Coin → Mandates → [mandate] → Delete."
2. If client has no SIPs linked → they can delete directly from Coin → Mandates.
3. Add: "Deleting a mandate does not cancel your SIPs — SIPs remain active but will require a new mandate or manual payment going forward."

### Rule 5 — Bank-Applied Penalty Charges

1. Triggered when: client reports charges from their bank in the context of a failed or cancelled mandate debit.
2. Confirm the charges are applied by the client's bank — not by Zerodha or BSE STAR MF (per **A7**).
3. Respond: "Zerodha does not charge for Coin mandate registrations at present. However, your bank may charge penalties for failed transactions due to insufficient funds and mandate verification charges. For details on the specific charges, please check with your bank." Share link from **A7**.


---
---
