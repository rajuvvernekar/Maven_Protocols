# e_mandate_report

## Description

WHEN TO USE:

- Customer asks about eMandate creation/activation status
- Customer reports mandate stuck in "pending" or "processing"
- Customer says mandate creation failed or was rejected
- Customer wants to cancel/delete an eMandate
- Customer reports cancellation is stuck in "pending cancellation"
- Customer asks why they can't create a mandate (current account, joint account, NRI, iOS)
- Customer asks about mandate charges or supported banks

TRIGGER KEYWORDS: "emandate status", "mandate pending", "mandate failed", "mandate rejected", "cancel mandate", "delete mandate", "mandate not active", "mandate processing", "create mandate", "mandate error", "mandate registration", "pending cancellation"

## Protocol

# E_MANDATE_REPORT PROTOCOL

## Knowledge Base

<knowledge_base>
<facts>
- eMandate enables automatic transfer up to ₹1 crore/day from bank to Zerodha
- Cannot use current accounts, NRE-PIS accounts for eMandate creation
- Joint accounts: some banks don't support — use standing instructions instead
- Bank takes up to 5 working days to activate mandate
- iOS pop-up blocker may prevent creation — enable "Always show" in browser
- No Zerodha charges; bank may charge verification fee + penalty for failed debits
- Failed creation = authentication unsuccessful at bank (closed window, wrong credentials)
- Zerodha cannot determine specific bank-side failure reason
- Schedule cancellation: 3 working days advance (4 for SBI)
- Mandate deletion: up to 5 working days
- Coin/MF mandates are separate — this covers Console mandates only
</facts>

<field_usage>
  <share>bank_account_number (if asked) | remark (customer-friendly language)</share>
  <banned>client_id | name | destination_bank_name | mandate_reference_id | umrn | registered_date | provider</banned>
</field_usage>

<status_values>
  <active>Active — ready for scheduled debits</active>
  <pending>Awaiting bank activation — up to 5 working days. ESCALATE if >5 working days from creation.</pending>
  <failed>Creation failed — bank authentication unsuccessful</failed>
  <cancelled>Cancelled by client</cancelled>
  <pending_cancellation>Cancellation in progress — ESCALATE if >5 working days from cancellation_date</pending_cancellation>
  <cancellation_failed>Cancellation failed — mandate likely inactive (rare)</cancellation_failed>
</status_values>

<timelines>
  <bank_activation>Up to 5 working days</bank_activation>
  <mandate_deletion>Up to 5 working days</mandate_deletion>
</timelines>

<account_restrictions>
  <current_account>Cannot create eMandate — use standing instructions via netbanking</current_account>
  <joint_account>Some banks don't support — use standing instructions</joint_account>
  <nre_pis>Cannot create eMandate</nre_pis>
</account_restrictions>

<links>
  <mandate_console>console.zerodha.com/funds/mandates</mandate_console>
</links>
</knowledge_base>

---

## Business Rules

### Rule 0: Scope Check — Console vs Coin Mandate
**if:** Query is about Coin MF mandate or UPI autopay mandate
**then:** This tool covers only Console mandates (for Kite fund transfers / Stock SIPs). Coin MF mandates are managed separately.

### Rule 1: Mandate Active
**if:** `status` = "active"
**then:** "Your eMandate is active. You can create or manage schedules at console.zerodha.com/funds/mandates."

### Rule 2: Mandate Pending
**if:** `status` = "pending"
**then:** Calculate working days since `creation` date.
- If ≤5 working days: "Your eMandate was initiated on [creation date] and is awaiting activation from your bank. This can take up to 5 working days."
- If >5 working days: "Your eMandate has been pending for more than 5 working days. Sometimes banks delay sending confirmation. We periodically follow up with banks, but cannot provide an exact timeline. If you need funds urgently, you can add funds manually via Kite." ESCALATE with mandate details.

### Rule 3: Mandate Failed
**if:** `status` = "failed"
**then:** "Your eMandate registration could not be completed. This typically happens when the bank authentication was not successful — for example, if the authentication window was closed before completion or incorrect credentials were entered. You can create a new mandate at console.zerodha.com/funds/mandates."

If `remark` contains useful info, share in customer-friendly language.

### Rule 4: Mandate Cancelled
**if:** `status` = "cancelled"
**then:** "Your eMandate has been cancelled. If you'd like to set up auto-debit again, you can create a new mandate at console.zerodha.com/funds/mandates."

### Rule 5: Pending Cancellation
**if:** `status` = "pending_cancellation"
**then:** Check `cancellation_date`.
- If ≤5 working days: "Your eMandate cancellation is being processed. This may take up to 5 working days."
- If >5 working days: ESCALATE with mandate details.

### Rule 6: Cancellation Failed
**if:** `status` = "cancellation_failed"
**then:** "The cancellation attempt for your eMandate did not go through. The mandate is likely not active. You can verify and retry at console.zerodha.com/funds/mandates." If customer insists mandate is still debiting, ESCALATE.

### Rule 7: Cannot Create Mandate — Account Restrictions
**if:** Customer unable to create mandate AND account type is current/joint/NRE-PIS
**then:** Check `<account_restrictions>` and respond:
- Current account: "eMandates cannot be created with current bank accounts. You can set up standing instructions through your bank's netbanking portal by adding Zerodha as a beneficiary."
- Joint account: "Some banks do not support eMandates for joint accounts. You can set up standing instructions via your bank's netbanking instead."
- NRE-PIS: "eMandates are not supported for NRE-PIS accounts."

### Rule 8: iOS Creation Issue
**if:** Customer reports mandate creation not proceeding on iPhone/iPad
**then:** "This usually happens when your browser blocks pop-ups. Go to your iOS browser settings and enable 'Always show' for pop-ups, then retry at console.zerodha.com/funds/mandates."

### Rule 9: Existing Pending Mandate Blocking New Creation
**if:** Customer says cannot create new mandate because old one is pending/pending_cancellation
**then:** "You cannot create a new eMandate while an existing one is still pending or being cancelled. The old mandate must be fully deleted first, which takes up to 5 working days." If old mandate has been pending_cancellation >5 working days, ESCALATE.

### Rule 10: Protect Internal Fields
**NEVER expose:** `client_id`, `name`, `destination_bank_name`, `mandate_reference_id`, `umrn`, `registered_date`, `provider`, `status` (raw value), `cancellation_date` (unless asked)
