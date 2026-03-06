# pledge_request_report

## Description

WHEN TO USE:

- Agent needs to check older pledge/unpledge request history (more than 30 days old)
- Client asks about a specific pledge or unpledge request status from weeks/months ago
- Client reports collateral margin reduced and agent needs to trace which unpledge caused it
- Agent needs to verify pledge/unpledge history for a date range (e.g., for DPC dispute or margin audit)
- Client disputes collateral amount shown in DPC report — need to verify what was pledged on specific dates
- Agent needs to check Pledged Holdings snapshot (current pledged securities, qty, value, collateral margin)
- Client asks why collateral margin value changed — need to check current pledged holdings breakdown
- Client reports pledged shares not showing collateral — need to verify pledge status in historical records

TRIGGER KEYWORDS: "pledge history", "old pledge request", "unpledge history", "pledge last month", "collateral reduced why", "pledged holdings", "collateral value", "collateral margin breakdown", "pledge charges history", "pledge from [date]", "what is pledged currently", "pledged securities list"

## Protocol

# PLEDGE REQUEST REPORT PROTOCOL

## PROTOCOL

<knowledge_base>

<facts>
- This tool has TWO modes accessed via a dropdown:
  1. Pledge Request Report: historical pledge/unpledge requests for a date range
  2. Pledged Holdings Report: snapshot of currently pledged securities with value and collateral margin
- Pledge Request Report: shows each pledge/unpledge request with status, qty, security, date
- Pledged Holdings Report: shows current pledged qty, market value, and collateral margin per security
- Use Pledge Request Report for historical investigations; Pledged Holdings for current state
- Status values (Pledge Request): Processed (successful), Pending (awaiting CDSL), Rejected/Failed
- Pending status: if pledge → collateral not yet reflected; if unpledge → shares not yet released
- Pledge charges: ₹0 standard — but Journal Entry appears on ledger for specific pledge types (some instruments)
- Collateral margin = market value × (1 − haircut%). Haircut varies by security — typically 50% for equity, ~10% for liquid ETFs/LIQUIDBEES
- NEVER share breakup of collateral holdings with client — use Pledged Holdings only when client complains about reduction in collateral amount on margins page
- Collateral value changes daily based on market price and haircut updates
- MF pledge/unpledge: handled via Coin — same status tracking but different flow
</facts>

<field_usage>
  <pledge_request>
    <share>pledge_date (if asked) | tradingsymbol (if asked) | quantity (if asked) | status (translated)</share>
    <banned>pledge_time | client_id | isin | previous_quantity | pledge_type (use internally) | remarks | cdsl_status | pledge_verification_date</banned>
  </pledge_request>
  <pledged_holdings>
    <share>tradingsymbol | quantity | value | collateral_margin (only if client complains about collateral reduction)</share>
    <banned>pledge_date | client_id | isin | status | creation</banned>
  </pledged_holdings>
</field_usage>

<cross_reference>
  <console_instant_pledge>Recent pledge requests (last 30 days) — use instead of this tool for recent data</console_instant_pledge>
  <delayed_payment_charges>DPC report uses collateral values — verify here if client disputes DPC collateral</delayed_payment_charges>
  <ledger_report>Pledge/unpledge charge entries appear on ledger</ledger_report>
  <console_eq_holdings>Verify if pledged shares still appear in holdings (pledged qty vs free qty)</console_eq_holdings>
</cross_reference>

<escalation_triggers>
  <pledge_processed_no_collateral>Pledge Request status = Processed but collateral margin not reflected after 24+ hours</pledge_processed_no_collateral>
  <pledged_qty_mismatch>Pledged Holdings qty differs from what client actually pledged per request history</pledged_qty_mismatch>
  <collateral_value_wrong>Collateral margin in Pledged Holdings significantly differs from expected (market value × expected haircut)</collateral_value_wrong>
  <external_pledge_stuck>Client pledged externally (with another institution) but shares still showing in Console</external_pledge_stuck>
</escalation_triggers>

</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
**Pledge Request Report — NEVER expose:** `pledge_time`, `client_id`, `isin`, `previous_quantity`, `pledge_type` (use internally only), `remarks`, `cdsl_status`, `pledge_verification_date`
**Pledged Holdings Report — NEVER expose:** `pledge_date`, `client_id`, `isin`, `status`, `creation`

**CRITICAL:** Never share the full breakup of collateral holdings with the client proactively. Use Pledged Holdings data ONLY when the client specifically complains about collateral amount reduction.

### Rule 1: Historical Pledge/Unpledge Status
**if:** Client asks about a specific pledge or unpledge request from more than 30 days ago
**then:** Look up Pledge Request Report for the date range. Find matching tradingsymbol.

"Your [pledge/unpledge] request for [quantity] shares of [tradingsymbol] on [pledge_date]: Status — [Processed/Pending/Rejected].

- Processed: The request was completed successfully.
- If still showing Pending for a request older than 30 days → this is unusual. Let me investigate further." (Escalate)

### Rule 2: Collateral Reduced — Trace Cause
**if:** Client reports collateral margin reduced and wants to know why
**then:** Check BOTH reports:
1. Pledged Holdings: current pledged qty and collateral_margin per security
2. Pledge Request Report: look for recent unpledge requests

Possible causes (check in order):
- Unpledge processed → "An unpledge of [qty] shares of [tradingsymbol] was processed on [date], which reduced your collateral."
- Market price drop → "The market value of your pledged securities has decreased, which reduced the collateral margin."
- Haircut change → "The haircut percentage for [tradingsymbol] may have been updated, affecting collateral value."
- Stock removed from approved list → "If [tradingsymbol] was removed from the approved pledge list, it would no longer count as collateral."

Share the specific security and reduction amount ONLY when client asks.

### Rule 3: Pledged Holdings Snapshot
**if:** Client asks what is currently pledged or total collateral value
**then:** Use Pledged Holdings Report. Share summary only — not full breakup.

"Your total collateral margin from pledged securities is ₹[sum of collateral_margin]. This is based on [N] pledged securities."

Only share per-security details if client specifically asks about a particular stock's collateral value. Never volunteer the full list.

### Rule 4: Collateral Margin Calculation
**if:** Client asks why collateral margin is less than market value of pledged shares
**then:** "The collateral margin is the market value of your pledged shares minus a haircut percentage. The haircut varies by security:
- Liquid ETFs (LIQUIDBEES, LIQUIDCASE etc.): ~10% haircut
- Large-cap equity: ~50% haircut (varies)
- Mid/small-cap: higher haircut

So if you pledged shares worth ₹1,00,000 with a 50% haircut, your collateral margin would be approximately ₹50,000."

### Rule 5: MF Pledge/Unpledge via Coin
**if:** Client asks about mutual fund pledge or reports MF pledge issue
**then:** Escalate directly. MF pledge/unpledge is handled through Coin (Zerodha's MF platform) and this tool does not cover MF pledge details. Escalate with: client ID, MF scheme name if provided, and the specific issue.

### Rule 6: Pledge Not Allowed Error
**if:** Client reports "Pledging is not allowed" or "Something went wrong" error
**then:** Check if the security is in the approved pledge list.
"Some securities are not approved for pledging. If [tradingsymbol] is not on the approved list, the pledge request will fail. You can check the list of approved securities on Zerodha's pledge page.

Other reasons for failure: T1 holdings (bought today, not settled), insufficient free qty, or technical issue. If the security is approved and you have sufficient free qty, try re-logging and placing the request again."

If issue persists after basic troubleshooting → escalate.

### Rule 7: Unpledge Rejected — Margin Utilized
**if:** Unpledge request rejected with "Margin already utilized"
**then:** "Your unpledge request for [tradingsymbol] was rejected because the collateral margin from these pledged shares is currently being used against your open positions. To unpledge, you would need to either close positions using this margin or add equivalent funds first."

### Rule 8: External Pledge (Pledged with Another Institution)
**if:** Client pledged shares externally (not through Zerodha) but shares still show in Console
**then:** "If you pledged your shares with another institution (external pledge), the shares may still appear in Console as holdings. However, they are encumbered and cannot be traded or transferred. For external pledge-related queries, please check with the DP team."

Escalate if client needs the external pledge shares removed from Console view.

### Rule 9: Escalation Criteria
**if:** Any of the following:
- Pledge shows Processed but collateral not reflected after 24+ hours (KB trigger)
- Pledged Holdings qty doesn't match pledge request history (KB trigger)
- Collateral margin significantly wrong compared to market value × expected haircut (KB trigger)
- Pledge/unpledge page persistently failing for approved security with free qty (Rule 6)
- Pending status stuck for >30 days (Rule 1)
- External pledge shares stuck in Console (Rule 8)
**then:** Escalate with: client ID, tradingsymbol, pledge_date, status, and specific issue.
