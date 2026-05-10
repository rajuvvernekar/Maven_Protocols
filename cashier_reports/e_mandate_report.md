# e_mandate_report

## Description

WHEN TO USE:

When clients:
- Ask about eMandate creation/activation status
- Report mandate stuck in "pending" or "processing"
- Report mandate creation failed or was rejected
- Want to cancel/delete an eMandate
- Report cancellation stuck in "pending cancellation"
- Ask why they can't create a mandate (current account, joint account, NRI, iOS)
- Ask about mandate charges or supported banks

TRIGGER KEYWORDS: "emandate status", "mandate pending", "mandate failed", "mandate rejected", "cancel mandate", "delete mandate", "mandate not active", "mandate processing", "create mandate", "mandate error", "mandate registration", "pending cancellation"

TAGS: funds

## Protocol

# E MANDATE REPORT PROTOCOL

## Section A: Reference Data

### A1 — Fundamentals

- eMandate enables automatic transfer up to ₹1 crore/day from bank to Zerodha. No Zerodha charges; bank may charge verification fee + penalty for failed debits.

### A2 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |
|---|---|
| `bank_account_number` | Share if asked |
| `created` | Mandate creation date |
| `remark` | Failure remark from the bank |
| `status` | Use for routing/diagnosis only — communicate the outcome, not the raw value |
| `cancellation_date` | Share only if client specifically asks when they cancelled |

**Non-shareable:**

| Field | Interpretation |
|---|---|
| `client_id` | Internal client identifier |
| `name` | Internal record name |
| `destination_bank_name` | Bank name — internal |
| `mandate_reference_id` | Internal mandate reference |
| `umrn` | Unique mandate reference number — internal |
| `registered_date` | Internal registration date |
| `provider` | Mandate provider |

### A3 — Status Values

| Status | Meaning | Action |
|---|---|---|
| Active | Ready for scheduled debits | Confirm active, direct to Console for schedule management. |
| Pending | Awaiting bank activation | ≤5 working days from `creation` → inform client to wait. >5 working days → escalate to human agent per **A7**. |
| Failed | Creation failed — bank authentication unsuccessful | Guide to retry. Share `remark`. |
| Cancelled | Cancelled by client | Confirm cancelled, offer to create new mandate. |
| Pending Cancellation | Cancellation in progress | Check `cancellation_date`. ≤5 working days → inform processing. >5 working days → escalate to human agent per **A7**. |
| Cancellation Failed | Cancellation did not go through — mandate likely not active (rare) | Guide to verify/retry. If still debiting → escalate to human agent per **A7**. |

### A4 — Account Restrictions

| Account Type | Restriction | Alternative |
|---|---|---|
| Current account | Cannot create eMandate | Set up standing instructions through bank's netbanking portal (add Zerodha as beneficiary) |
| Joint account | Some banks do not support eMandates | Set up standing instructions via bank's netbanking |
| NRE-PIS | Cannot create eMandate | Not supported |

### A5 — Timelines

| Event | Timeline |
|---|---|
| Bank activation of mandate | Up to 5 working days |
| Mandate deletion | Up to 5 working days |
| Schedule cancellation advance notice | 3 working days (4 for SBI) |

### A6 — Links

| Topic | URL |
|---|---|
| Mandate management on Console | console.zerodha.com/funds/mandates |

### A7 — Escalation Triggers

When escalating, always include: client ID, mandate details (bank, creation/cancellation date), and specific issue.

## Section B: Decision Flow

### Routing

```
Route by scenario
   ├─ Mandate status check (active/pending/failed/cancelled) → Rule 1
   ├─ Cannot create mandate — account type restriction → Rule 2
   ├─ Mandate creation not proceeding on iOS → Rule 3
   ├─ Old pending mandate blocking new creation → Rule 4
   └─ Coin/MF mandate queries → Rule 5
```

### Fallback

If no route matches, escalate to human agent per **A7**.

## Section C: Rules

### Rule 1 — Mandate Status Check

1. Determine status per **A3**:
   a. Active → confirm active and direct to Console per **A6** for schedule management.
   b. Pending → calculate working days since `created`. ≤5 working days → inform client mandate is awaiting bank activation, can take up to 5 working days. >5 working days → inform client banks sometimes delay confirmation, follow-up in progress, no exact timeline; suggest manual fund add via Kite. Escalate to human agent per **A7**.
   c. Failed → bank authentication was unsuccessful (e.g., authentication window closed, incorrect credentials). Direct to create new mandate per **A6**. If `remark` contains useful info, share with client.
   d. Cancelled → confirm cancellation; offer to create new mandate per **A6**.
   e. Pending Cancellation → check `cancellation_date`. ≤5 working days → cancellation is being processed (up to 5 working days). >5 working days → escalate to human agent per **A7**.
   f. Cancellation Failed → mandate likely not active. Direct to verify/retry per **A6**. If client insists mandate is still debiting → escalate to human agent per **A7**.

### Rule 2 — Cannot Create Mandate (Account Restrictions)

Check `get_all_client_data`:

1. **Current account:**
   If `bank_1_account_type`, `bank_2_account_type`, or `bank_3_account_type` is "Current" → cannot create eMandate per **A4**.

2. **Joint account:**
   If `primary_dp_status` = "YES" → eMandates may not be supported per **A4**.

3. **NRE-PIS account:**
   If all three conditions match:
   - `client_acc_type` is one of NRO, NRE, or NRI
   - `bo_sub_status` contains "RepatriableWith"
   - `pis_bank_1_name` or `pis_bank_2_name` is populated
   → eMandates not supported per **A4**.

### Rule 3 — iOS Creation Issue

1. iOS browser may be blocking pop-ups. Direct client to enable "Always show" for pop-ups in iOS browser settings, then retry per **A6**.

### Rule 4 — Old Pending Mandate Blocking New Creation

1. Check `status` of all existing mandates. If any mandate has status Pending or Pending Cancellation, a new mandate cannot be created until that mandate is resolved.
2. For resolution timelines and escalation, apply Rule 1.

### Rule 5 — Out-of-Scope Redirect

- Coin/MF mandate queries → invoke `mandate_report`.
