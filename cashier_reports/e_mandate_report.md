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

## Protocol

# E MANDATE REPORT PROTOCOL 

---

## Section A: Reference Data

---

### A1 — Tool Purpose & Fundamentals

This tool shows **Console eMandate status** — for automatic fund transfers from bank to Zerodha (Kite trading account / Stock SIPs). This does not cover Coin/MF mandates or UPI autopay mandates — those are separate systems.

eMandate enables automatic transfer up to ₹1 crore/day from bank to Zerodha. No Zerodha charges; bank may charge verification fee + penalty for failed debits.

**Input:** Client ID — returns mandate records.

---

### A2 — Field Usage Rules

**Shareable fields:**

`bank_account_number` (if asked) | `remark` (in customer-friendly language)

**Internal-only fields** (use for reasoning; communicate outcomes in plain language):

`client_id` | `name` | `destination_bank_name` | `mandate_reference_id` | `umrn` | `registered_date` | `provider` | `status` | `cancellation_date`

`cancellation_date`: share only if the client specifically asks when they cancelled. `status`: use for routing/diagnosis only — communicate the outcome, not the raw value.

---

### A3 — Status Values

| Status | Meaning | Action |
|---|---|---|
| Active | Ready for scheduled debits | Confirm active, direct to Console for schedule management. |
| Pending | Awaiting bank activation | ≤5 working days from creation → inform client to wait. >5 working days → escalate. |
| Failed | Creation failed — bank authentication unsuccessful | Guide to retry. Share `remark` if useful. |
| Cancelled | Cancelled by client | Confirm cancelled, offer to create new mandate. |
| Pending Cancellation | Cancellation in progress | ≤5 working days from cancellation → inform processing. >5 working days → escalate. |
| Cancellation Failed | Cancellation did not go through — mandate likely not active (rare) | Guide to verify/retry. If still debiting → escalate. |

---

### A4 — Account Restrictions

| Account Type | Restriction | Alternative |
|---|---|---|
| Current account | Cannot create eMandate | Set up standing instructions through bank's netbanking portal (add Zerodha as beneficiary) |
| Joint account | Some banks do not support eMandates | Set up standing instructions via bank's netbanking |
| NRE-PIS | Cannot create eMandate | Not supported |

---

### A5 — Timelines

| Event | Timeline |
|---|---|
| Bank activation of mandate | Up to 5 working days |
| Mandate deletion | Up to 5 working days |
| Schedule cancellation advance notice | 3 working days (4 for SBI) |

---

### A6 — Links

| Topic | URL |
|---|---|
| Mandate management on Console | console.zerodha.com/funds/mandates |

---

### A7 — Escalation Data Template

When escalating, always include: **client ID, mandate details (bank, creation/cancellation date), and specific issue.**

---

### A8 — Response Templates

**R1 — Active:**
"Your eMandate is active. You can create or manage schedules at console.zerodha.com/funds/mandates."

**R2 — Pending (≤5 working days):**
"Your eMandate was initiated on [creation date] and is awaiting activation from your bank. This can take up to 5 working days."

**R3 — Pending (>5 working days):**
"Your eMandate has been pending for more than 5 working days. Sometimes banks delay sending confirmation. We periodically follow up with banks, but cannot provide an exact timeline. If you need funds urgently, you can add funds manually via Kite."

**R4 — Failed:**
"Your eMandate registration could not be completed. This typically happens when the bank authentication was not successful — for example, if the authentication window was closed before completion or incorrect credentials were entered. You can create a new mandate at console.zerodha.com/funds/mandates."

**R5 — Cancelled:**
"Your eMandate has been cancelled. If you'd like to set up auto-debit again, you can create a new mandate at console.zerodha.com/funds/mandates."

**R6 — Pending cancellation (≤5 working days):**
"Your eMandate cancellation is being processed. This may take up to 5 working days."

**R7 — Cancellation failed:**
"The cancellation attempt for your eMandate did not go through. The mandate is likely not active. You can verify and retry at console.zerodha.com/funds/mandates."

**R8 — Current account restriction:**
"eMandates cannot be created with current bank accounts. You can set up standing instructions through your bank's netbanking portal by adding Zerodha as a beneficiary."

**R9 — Joint account restriction:**
"Some banks do not support eMandates for joint accounts. You can set up standing instructions via your bank's netbanking instead."

**R10 — NRE-PIS restriction:**
"eMandates are not supported for NRE-PIS accounts."

**R11 — iOS pop-up issue:**
"This usually happens when your browser blocks pop-ups. Go to your iOS browser settings and enable 'Always show' for pop-ups, then retry at console.zerodha.com/funds/mandates."

**R12 — Old mandate blocking new creation:**
"You cannot create a new eMandate while an existing one is still pending or being cancelled. The old mandate must be fully deleted first, which takes up to 5 working days."

---

**Escalation behavior:** When any rule in this protocol says **ESCALATE**, do not draft a customer-facing response. Instead, output only: **HUMAN AGENT ACTION REQUIRED** — followed by the reason from the rule. The human agent will handle the query manually.

## Section B: Decision Flow

---

### Preflight (run on every query)

```
1. Determine if query is about Console eMandate
   └─ If about Coin/MF mandate or UPI autopay → this tool does not cover those.
      Redirect accordingly.
```

### Route

```
Intent / Condition                                          → Rule
──────────────────────────────────────────────────────────────────────
Mandate status check (active/pending/failed/cancelled)      → Rule 1
Cannot create mandate — account type restriction            → Rule 2
Mandate creation not proceeding on iOS                      → Rule 3
Old pending mandate blocking new creation                   → Rule 4
```

### Scope

- Address the client's query about Console eMandate status, creation issues, and cancellation.
- Use **A2** field rules in all client communication — only `bank_account_number` (if asked) and `remark` (in friendly language) are shareable.
- Redirect Coin/MF and UPI autopay mandate queries — this tool does not cover them.

### Fallback

If no route matches, check `e_mandate_schedule_report` and `auto_debit_payins` for related context. If no root cause is found, **ESCALATE** per **A7**.

---

## Section C: Rules

---

### Rule 1 — Mandate Status Check

1. Determine status (per **A3**) and respond:
   a. Active → respond per **A8-R1**.
   b. Pending:
      - Calculate working days since creation date.
      - ≤5 working days → respond per **A8-R2**.
      - >5 working days → respond per **A8-R3**. **ESCALATE** per **A7**.
   c. Failed → respond per **A8-R4**. If `remark` contains useful info, share in customer-friendly language.
   d. Cancelled → respond per **A8-R5**.
   e. Pending Cancellation:
      - Check `cancellation_date`.
      - ≤5 working days → respond per **A8-R6**.
      - >5 working days → **ESCALATE** per **A7**.
   f. Cancellation Failed → respond per **A8-R7**. If client insists mandate is still debiting → **ESCALATE** per **A7**.

---

### Rule 2 — Cannot Create Mandate (Account Restrictions)

1. Check account type against **A4**:
   a. Current account → respond per **A8-R8**.
   b. Joint account → respond per **A8-R9**.
   c. NRE-PIS → respond per **A8-R10**.

---

### Rule 3 — iOS Creation Issue

1. Respond per **A8-R11**.

---

### Rule 4 — Old Pending Mandate Blocking New Creation

1. Respond per **A8-R12**. Deletion timeline per **A5**.
2. If old mandate has been in pending_cancellation for >5 working days → **ESCALATE** per **A7**.

---

## Section D: General Notes

- This tool covers Console eMandates only. Coin/MF mandates and UPI autopay mandates are separate systems.
- eMandate enables up to ₹1 crore/day automatic transfer. No Zerodha charges; bank may charge verification fee + penalty for failed debits.
- Bank activation takes up to 5 working days. Mandate deletion also takes up to 5 working days.
- Schedule cancellation requires 3 working days advance notice (4 for SBI).
- Failed mandate creation means bank authentication was unsuccessful — Zerodha cannot determine specific bank-side failure reason.
- Current accounts, NRE-PIS accounts cannot create eMandates. Joint accounts may not be supported by some banks. Standing instructions via netbanking are the alternative.
- iOS pop-up blocker can prevent mandate creation — enable "Always show" in browser settings.
