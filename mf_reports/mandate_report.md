# mandate_report

## Description

WHEN TO USE:

When clients:
- Ask about mandate status (created/pending/active/failed/cancelled)
- Report mandate not activating or stuck
- Ask about mandate activation timeline
- Ask which bank mandate is linked to

TRIGGER KEYWORDS: "mandate status", "mandate pending", "mandate failed", "eNACH", "autopay setup", "coin"

TAGS: investments, funds

## Protocol

# MANDATE REPORT PROTOCOL

---

## Section A: Reference Data

### A1 — Mandate Fundamentals

-A Coin mandate must be linked to a SIP for auto-debit to work. The mandate limit (typically ₹1,00,000 for UPI autopay, ₹1,00,00,000 for eNACH) is the maximum permissible debit per transaction — not the actual debit amount. The actual debit equals the sum of linked SIP instalments for that cycle.

-To delete a Coin mandate, all active or paused SIPs linked to it must be unlinked first. See A5 for the full deletion process.

---

### A2 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |  
|---|---|  
| `status` | Mandate status — translate per A3 |  
| `created_at` | Mandate creation date |  
| `name` | Mandate name |  
| `amount` | Maximum debit limit per transaction |  
| `bank_name` | Name of the linked bank |  
| `bank_account_number` | Linked bank account number |

**Non-shareable:**

| Field | Interpretation |  
|---|---|  
| `client_id` | Internal client identifier |  
| `id` | Internal mandate identifier |  
| `umrn` | Bank-assigned registration number for the mandate |  
| `merchant` | Mandate issuer entity (Coin/Zerodha) |  
| `type` | Mandate type — `autopay` (UPI) or `enach`; used with `provider` for type identification per A4 |  
| `provider` | Mandate provider — `ybl` (UPI autopay) or `digio` (eNACH); used with `type` for type identification per A4 |  
| `provider_id` | Provider-assigned mandate identifier |  
| `bank_ifsc` | IFSC code of the linked bank account |  
| `bank_account_type` | Account type (savings, current); used for current account restriction check per A6 |  
| `cancellation_requested_at` | When cancellation was requested |  
| `verified_at` | Timestamp when the mandate was activated |  
| `valid_until` | Mandate expiry date |  
| `cancelled_at` | Timestamp when cancellation completed |

---

### A3 — Status Values

| Status | Meaning |  
|---|---|  
| success | Mandate is active and ready for scheduled debits |  
| pending | Awaiting bank approval or activation |  
| failed | Creation or registration failed |  
| cancelled | Cancelled |

---

### A4 — Mandate Type Comparison

Identify type using the `type` and `provider` fields:

| Feature | UPI Autopay (`type` = `autopay`, `provider` = `ybl`) | eNACH (`type` = `enach`, `provider` = `digio`) |  
|---|---|---|  
| Activation time | Within 2 minutes of UPI PIN confirmation | Up to 3 working days (may take up to 5) |  
| Activation requirement | Client must complete UPI PIN confirmation | Bank approval |  
| If not activated | Auto-cancelled by 11 PM same day if PIN not completed | Pending until bank approves or rejects |  
| Escalation timeline | — | If pending more than 5 working days, escalate |

---

### A5 — Mandate Deletion Process (Coin)

-Before deleting a Coin mandate, all active or paused SIPs linked to it must be unlinked. Deleting a mandate with linked SIPs will cause those SIPs to fail in future cycles.

-To unlink and delete the mandate: Coin → Account → Mandates → Select the Mandate → Unlink the SIPs linked (Click on “Unlink” mentioned below the fund name) → Delete the mandate once the SIPs are unlinked by choosing the “Delete Mandate”. 

-If no SIPs are linked: delete directly from Coin → Mandates.

-Deleting a mandate does not cancel the SIPs themselves. The SIPs remain active but will require a new mandate or manual payment going forward.

-For full reference, share the Coin mandate management link from A8.

---

### A6 — Account Restrictions

| Account type | Restriction | Alternative for SIP payments |  
|---|---|---|  
| Current account | Most banks do not permit eNACH or UPI autopay mandates from current accounts | Place manual lumpsum orders per SIP cycle |  
| Joint account | Some banks do not support mandates for joint accounts | Place manual lumpsum orders per SIP cycle |  
| NRE-PIS | Cannot create mandate | NEFT/RTGS to the ICCL account unique to the client per SIP cycle |

Other NRI account types (NRO PIS, NRO non-PIS, NRE non-PIS) can create mandates normally.

---

### A7 — Timelines

| Event | Timeline |  
|---|---|  
| eNACH bank activation | Up to 3 working days (may take up to 5) |  
| UPI autopay activation | Within 2 minutes of PIN confirmation |  
| Mandate deletion | Up to 5 working days |

---

### A8 — Links

| Topic | URL |  
|---|---|  
| Coin mandate management (creation, linkage, deletion) | https://support.zerodha.com/category/mutual-funds/payments-and-orders/coin-mandates/articles/sip-mandate-on-coin |

---

### A9 — Escalation Triggers

Escalate to human agent when any of the following apply:

- eNACH mandate pending more than 5 working days.  
- Old mandate stuck in pending or being-cancelled state for more than 5 working days, blocking new mandate creation.  
- Mandate deletion not completing within the timeline in A7.

Include in escalation: client ID, mandate type (UPI autopay or eNACH), bank, creation date, and the specific issue.

---

## Section B: Decision Flow

### Routing

```  
Route by scenario  
   ├─ Mandate status check (active / pending / failed / cancelled) → Rule 1  
   ├─ Cannot create mandate — account type restriction → Rule 2  
   ├─ Old pending mandate blocking new creation → Rule 3  
   ├─ Active mandate but SIP not debiting → Rule 4  
   └─ How to delete a mandate → Rule 5  
```

### Fallback

If no rule matches and no root cause is identified after checks → escalate to human agent per A9.

---

## Section C: Rules

### Rule 1 — Mandate Status Check

Apply the status meaning per A3. Communicate the current state to the client.

For pending status, branch by mandate type per A4:

- **eNACH** (`type` = `enach`): calculate working days since `created_at`. If 5 working days or fewer → communicate that eNACH activation takes up to 3 working days. If more than 5 working days → communicate that the mandate has been pending beyond the normal window; banks sometimes delay confirmation. Escalate per A9.  
- **UPI autopay** (`type` = `autopay`): check time elapsed since `created_at`. If within 2 minutes → mandate is still being activated; communicate to wait. If more than 2 minutes → the UPI PIN confirmation step was likely not completed. Communicate that the mandate will be auto-cancelled by 11 PM the same day, and advise creating a new mandate with the PIN confirmation step completed.

-For failed status, communicate that the mandate registration could not be completed. Suggest creating a new mandate; UPI autopay activates within 2 minutes if the client wants faster activation.

-For cancelled status, communicate the cancellation. Share the Coin mandate management link from A8.

---

### Rule 2 — Cannot Create Mandate (Account Restrictions)

Determine the restriction type using account data:

**Current account check:**

The `bank_account_number` on this protocol's data identifies the bank account in question. From `get_all_client_data`, match it against `bank_1_account_number`, `bank_2_account_number`, or `bank_3_account_number`. If the corresponding `bank_*_account_type` = "Current" → current account restriction applies (per A6). Communicate the restriction and the alternative (standing instructions via netbanking).

**Joint account check:**

From `get_all_client_data`, if `primary_dp_joint_account` = "YES" → joint account. Some banks do not support mandates for joint accounts (per A6). Communicate the restriction and the alternative.

**NRI PIS check:**

From `get_all_client_data`, confirm NRI PIS account. All three conditions must match:  
- `client_acc_type` is one of NRO, NRE, or NRI  
- `bo_sub_status` contains "RepatriableWith" (NRE)  
- `pis_bank_1_name` or `pis_bank_2_name` is populated (PIS)

If all three match → NRE-PIS account confirmed. Communicate the restriction per A6.

If the client has an NRI account but is not NRE-PIS → mandates can be created normally per A6. Proceed with standard mandate handling.

---

### Rule 3 — Old Pending Mandate Blocking New Creation

A new mandate cannot be created while an existing one is still pending or being cancelled. Communicate this and the deletion timeline per A7 (up to 5 working days).

If the old mandate has been pending for more than 5 working days → escalate per A9.

---

### Rule 4 — Active Mandate But SIP Not Debiting

Confirm: mandate `status` = `success`.

The SIP-mandate linkage check is handled by `sip_report` — the `fund_source` field on each SIP record is the authoritative source for linkage. Route to `sip_report` for the linkage check and downstream diagnosis.

---

### Rule 5 — Mandate Deletion

Apply the deletion process per A5. If the client has linked SIPs, walk them through the unlink-then-delete sequence. If they have no linked SIPs, direct them to Coin → Mandates → Delete.

Share the Coin mandate management link from A8.
