# console_instant_pledge

## Description

WHEN TO USE:

- Client asks about the status of a pledge or unpledge request
- Client reports pledge request failed or showing as pending
- Agent needs to verify if a pledge/unpledge was processed successfully
- Client says pledged shares not showing collateral margin
- Client reports "Something went wrong" error while pledging
- Client asks about overdue pledge requests
- Agent needs to check pledge history for a specific security
- Client reports unpledge request rejected

TRIGGER KEYWORDS: "pledge status", "pledge failed", "pledge request", "unpledge status", "unpledge failed", "pledge pending", "pledge overdue", "collateral not showing", "pledge success", "pledge error", "something went wrong pledge", "pledge history", "re-pledge"

## Protocol

# CONSOLE INSTANT PLEDGE PROTOCOL

## PROTOCOL

<knowledge_base>

<facts>
- This tool shows instant pledge/unpledge request history — status, qty, date, security details
- Required input: Client ID only — returns all pledge requests
- pledge_type values: Pledge (new pledge), Unpledge (release pledge), Re-pledge (re-pledging previously unpledged)
- status values: Success (processed by CDSL), Failure (rejected by system or CDSL), Pending (awaiting CDSL confirmation)
- Pledging creates collateral margin — collateral reflected after CDSL confirmation (usually instant, can take up to 30 mins)
- Unpledge releases collateral — margin freed after CDSL confirmation
- Unpledge may be rejected if margin is already utilized against open positions ("Margin already utilized")
- Only approved securities can be pledged — unapproved stocks show error
- T1 holdings (bought today, not yet settled) cannot be pledged — must wait for T+1 settlement
- Pledge charges: typically ₹0 for pledge, ₹0 for unpledge via Zerodha (standard instant pledge)
- MTF shares are auto-pledged — separate from client-initiated pledges in this tool
- Overdue pledge: request submitted but CDSL confirmation pending beyond expected time
- previous_quantity shows pledged qty before this transaction — useful to track incremental pledges
</facts>

<field_usage>
  <share>pledge_date | tradingsymbol | isin | status | pledge_type | quantity | previous_quantity | pledge_creation</share>
  <banned>client_id | psn (internal depository reference) | uid (internal transaction ID) | psnstatus (internal depository status)</banned>
</field_usage>

<status_values>
  <success>Request processed by CDSL — collateral margin should be reflected</success>
  <failure>Request rejected — security not approved, insufficient qty, or CDSL rejection</failure>
  <pending>Awaiting CDSL confirmation — usually resolves within 30 mins</pending>
</status_values>

<common_failure_reasons>
  <not_approved>Security not in approved pledge list — "Something went wrong" or specific error</not_approved>
  <t1_holdings>Shares bought today (T1) — not yet settled, cannot pledge until T+1</t1_holdings>
  <insufficient_qty>Trying to pledge more qty than available free holdings</insufficient_qty>
  <margin_utilized>Unpledge rejected because collateral margin already used against open positions</margin_utilized>
  <overdue>CDSL confirmation delayed — request stuck in pending/overdue state</overdue>
</common_failure_reasons>

<cross_reference>
  <console_eq_holdings>Verify available qty for pledging. Pledged qty visible in holdings.</console_eq_holdings>
  <console_eq_pseudo_holdings>If holdings qty mismatch suspected, cross-check SOT data.</console_eq_pseudo_holdings>
</cross_reference>

<escalation_triggers>
  <pledge_success_no_margin>Status = Success but collateral margin not reflected after 30+ mins</pledge_success_no_margin>
  <persistent_failure>Pledge fails repeatedly for an approved security with sufficient qty</persistent_failure>
  <overdue_stuck>Overdue/Pending status not resolved within 24 hours</overdue_stuck>
  <holdings_missing_after_pledge>Holdings showing 0 in Kite after pledge but visible in Console</holdings_missing_after_pledge>
</escalation_triggers>

</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
**NEVER expose:** `client_id`, `psn`, `uid`, `psnstatus`
**ALWAYS share when relevant:** `pledge_date`, `tradingsymbol`, `isin`, `status`, `pledge_type`, `quantity`, `previous_quantity`, `pledge_creation`

### Rule 1: Pledge/Unpledge Status Verification
**if:** Client asks about pledge or unpledge request status
**then:** Look up by Client ID, find matching tradingsymbol and pledge_type.

"Your [pledge_type] request for [quantity] shares of [tradingsymbol] placed on [pledge_date]: Status — [status]."

- If status = Success → "Your request has been processed successfully. Collateral margin should be reflected in your account."
- If status = Failure → see Rule 3.
- If status = Pending → "Your request is awaiting confirmation from the depository. This usually completes within 30 minutes. If it remains pending beyond that, we'll investigate."

### Rule 2: Collateral Not Reflecting After Successful Pledge
**if:** status = Success but client says collateral margin not showing
**then:** Check timing — if pledge was within last 30 minutes → "Collateral margin can take up to 30 minutes to reflect after a successful pledge. Please check again shortly."

If more than 30 minutes since pledge_creation and still no collateral → escalate.

### Rule 3: Pledge Failed — Diagnose Reason
**if:** status = Failure
**then:** Check against common failure reasons:
- "Something went wrong" error → likely unapproved security. "The security [tradingsymbol] may not be in the approved pledge list. Only securities approved for margin are eligible for pledging."
- T1 shares → "If you purchased [tradingsymbol] today, the shares are not yet settled (T+1). You can pledge them from tomorrow."
- Insufficient qty → check `console_eq_holdings` for available qty. "You have [available qty] free shares of [tradingsymbol]. If you're trying to pledge more than this, the request will fail."
- If none of the above explains → escalate directly with: client ID, tradingsymbol, pledge_date, and status. Do not share a generic response to the client.

### Rule 4: Unpledge Rejected — Margin Utilized
**if:** pledge_type = Unpledge AND status = Failure AND client says "margin already utilized"
**then:** "Your unpledge request for [tradingsymbol] was rejected because the collateral margin from these pledged shares is currently being used against your open positions. To unpledge, you would need to either close the positions using this margin or add equivalent funds/margin from another source first."

### Rule 5: Overdue Pledge Request
**if:** Client reports pledge showing as overdue
**then:** Check status and pledge_creation timestamp.
- If pending/overdue < 30 mins → "Your request is being processed. Please wait up to 30 minutes for confirmation."
- If pending/overdue > 30 mins but < 24 hours → "Your pledge request is most likely going to fail as it has been pending for too long. We recommend placing a fresh pledge request on the next trading day, or you can try pledging a different approved security in the meantime."
- If pending/overdue > 24 hours → escalate.

### Rule 6: Holdings Showing Zero After Pledge
**if:** Client says Kite holdings show 0 qty but shares were pledged (not sold)
**then:** "Pledged shares may not appear in the standard holdings view on Kite. Your shares are safe — they are pledged as collateral. You can verify them on Console where pledged quantities are displayed."

Check `console_eq_holdings` to confirm qty is present. If qty = 0 in Console as well → escalate (may be safekeep or DP issue, not pledge-related).

### Rule 7: MTF Auto-Pledge vs Client Pledge
**if:** Client confused about pledge entries they didn't initiate
**then:** Check pledge_type and cross-reference with `console_mtf_holdings`.

"If you purchased shares under MTF (Margin Trading Facility), those shares are automatically pledged as collateral for the funded amount. These auto-pledge entries are separate from pledges you initiate manually. MTF auto-pledge details are covered under your MTF holdings."

### Rule 8: Escalation Criteria
**if:** Any of the following:
- Status = Success but collateral not reflected after 30+ mins (Rule 2)
- Pledge fails repeatedly for approved security with sufficient qty (Rule 3)
- Overdue/Pending not resolved within 24 hours (Rule 5)
- Holdings showing 0 in both Kite and Console after pledge (Rule 6)
**then:** Escalate with: client ID, tradingsymbol, pledge_type, status, pledge_date, and specific issue.
