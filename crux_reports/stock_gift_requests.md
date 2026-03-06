# stock_gift_requests

## Description

WHEN TO USE:

- Client asks about the status of a stock gift request (sending or receiving)
- Client reports gift request failed and wants to know why
- Agent needs to trace the lifecycle of a gift (created → accepted → approved → processing → transferred/failed)
- Client says they didn't receive CDSL email for beneficiary verification or OTP
- Client reports gifted stocks not visible in receiver's holdings
- Client asks why gift shows as "Failed" or "Cancelled"
- Client asks about buy average not updated for received gift stocks
- Client reports discrepancy mark on gifted stocks in holdings
- Agent needs to verify gift request timeline (creation, approval, transfer)

TRIGGER KEYWORDS: "gift stock", "gift request", "gift status", "gift failed", "gift cancelled", "gifted shares", "stock transfer gift", "gift not received", "accept gift", "approve gift", "beneficiary gift", "CDSL OTP gift", "gift processing", "gift buy average", "discrepant gifted stock", "stocks transferred gift"

## Protocol

# STOCK GIFT REQUESTS PROTOCOL

## PROTOCOL

<knowledge_base>

<facts>
- Gift flow: Sender creates → Receiver gets SMS/email → Receiver accepts → Sender approves with TPIN → Beneficiary addition on CDSL → CDSL sets up off-market transfer → Sender completes OTP verification → Stocks transferred
- Required input: Gifted By (sender Client ID) or Claimed By (receiver Client ID) — at least one. Optional: From/To Date.
- Stocks, ETFs, MF, and gold bonds between two Zerodha accounts can be gifted
- MF gifting: done via console.zerodha.com/gift (separate from Kite stock gifting)
- Gift charges: ₹25 per security per transaction + 18% GST (standard off-market transfer charges)
- Charges debited from sender's trading account — gift won't process if sender has negative balance
- Buy average for receiver: updated within 3 working days. Entry price = closing price on transfer date.
- For sender: exit price = closing price on transfer date (for tracking/reporting)
- Unsettled shares cannot be gifted
- Dormant account cannot gift — must complete re-KYC first
- Gift request expires if receiver doesn't accept within 7 days
</facts>

<status_flow>
  <created>Sender created gift request — pending receiver acceptance</created>
  <accepted>Receiver accepted — pending sender TPIN approval</accepted>
  <approved>Sender approved with TPIN — beneficiary addition initiated. Modified timestamp important: if after 2 PM, CDSL email for beneficiary comes next trading day.</approved>
  <processing>After Approved, auto-converts to Processing at ~2 PM. Beneficiary addition and CDSL OTP pending.</processing>
  <failed>Client didn't complete either beneficiary addition OR OTP verification by 8 PM deadline</failed>
  <cancelled>Client cancelled the request manually</cancelled>
  <stocks_transferred>Successfully transferred — stocks available in receiver's demat next trading day</stocks_transferred>
</status_flow>

<critical_timelines>
  <beneficiary_email>CDSL sends beneficiary verification email between 3 PM and 5 PM on trading days</beneficiary_email>
  <otp_email>CDSL sends OTP verification email/SMS at 5 PM on same trading day</otp_email>
  <otp_deadline>OTP must be completed by 8 PM same day — if missed, entire process must restart</otp_deadline>
  <approval_cutoff>If sender approves after 2 PM, CDSL email comes next trading day</approval_cutoff>
  <receiver_deadline>Receiver must accept within 7 days of gift creation</receiver_deadline>
</critical_timelines>

<field_usage>
  <share>creation (as date/time) | status | items (stock names/qty)</share>
  <banned>modified (use internally for timeline analysis) | sender_fullname | gifted_by | receiver_fullname | receiver_email | receiver_phone_number | claimer_fullname | claimed_by</banned>
</field_usage>

<cross_reference>
  <console_eq_holdings>Verify if gifted stocks visible in receiver's holdings (may show discrepancy mark initially)</console_eq_holdings>
  <console_eq_external_trades>Gift entry appears as external trade for buy avg update</console_eq_external_trades>
</cross_reference>

<escalation_triggers>
  <stocks_transferred_not_visible>Status = Stocks Transferred but receiver cannot see shares after 2 trading days</stocks_transferred_not_visible>
  <buy_avg_not_updated>Stocks transferred but buy average not updated after 3+ working days</buy_avg_not_updated>
  <repeated_failure>Gift request fails repeatedly despite completing all steps correctly</repeated_failure>
</escalation_triggers>

</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
**NEVER expose:** `modified` (use internally), `sender_fullname`, `gifted_by`, `receiver_fullname`, `receiver_email`, `receiver_phone_number`, `claimer_fullname`, `claimed_by`
**Share:** `creation` (as date/time), `status` (translated to client-friendly language), `items` (stock names and quantities)

### Rule 1: Gift Status Check
**if:** Client asks about gift request status
**then:** Look up by sender or receiver Client ID. Find matching request.

Report status using `<status_flow>` translations:
- Created → "Your gift request was created on [creation date]. It's waiting for the receiver to accept it. The receiver has 7 days to accept."
- Accepted → "The receiver has accepted the gift. The sender now needs to approve it using CDSL TPIN."
- Approved → "The sender has approved the gift. Beneficiary addition and CDSL verification are in progress." Check modified timestamp (internally) for timeline guidance.
- Processing → "The gift is being processed. The sender needs to complete CDSL OTP verification by 8 PM today."
- Failed → see Rule 2.
- Cancelled → "The gift request was cancelled."
- Stocks Transferred → "The gift has been successfully transferred. The stocks will be visible in the receiver's holdings by the next trading day."

### Rule 2: Gift Failed — Diagnose
**if:** status = Failed
**then:** "Your gift request for [items] created on [creation date] has failed. This typically happens when:
- The beneficiary was not added on CDSL, or the verification email was not completed between 3 PM and 5 PM.
- The CDSL OTP verification was not completed by 8 PM on the same day.

To retry: Place a fresh gift request on Console. If you don't receive the CDSL beneficiary email, use this link between 3 PM and 5 PM: https://www.cdslindia.com/Authentication/OTP.aspx?id=B to validate the beneficiary. Once added, complete the OTP verification between 5 PM and 8 PM."

### Rule 3: CDSL Email Not Received
**if:** Client says they didn't receive CDSL beneficiary or OTP email
**then:** Check modified timestamp (internally):
- If approval (Approved status) was after 2 PM → "Since the gift was approved after 2 PM, the CDSL email will be sent on the next trading day."
- If before 2 PM and no email by 5 PM → "If you haven't received the beneficiary verification email from CDSL by 5 PM, you can manually add the beneficiary using: https://www.cdslindia.com/Authentication/OTP.aspx?id=B

Once the beneficiary is added, you'll receive the OTP verification at 5 PM. Complete it before 8 PM."

### Rule 4: Beneficiary Already Added
**if:** Client says beneficiary was already added from a previous gift
**then:** "If the receiver's demat account was already added as a beneficiary from a previous transfer, you can skip the beneficiary addition step. The CDSL OTP verification email will be sent at 5 PM. Complete it by 8 PM."

### Rule 5: Gifted Stocks Not Visible in Holdings
**if:** Status = Stocks Transferred but receiver says stocks not visible
**then:** "Gifted stocks become visible in the receiver's holdings on the next trading day after the transfer is completed. If it's been more than 2 trading days since the status changed to 'Stocks Transferred' and the stocks are still not visible, we'll investigate." (Escalate after 2 trading days)

### Rule 6: Discrepancy on Gifted Stocks
**if:** Receiver sees red exclamation / discrepancy mark on gifted stocks
**then:** "This is normal for recently gifted stocks. The discrepancy appears because the buy average hasn't been updated yet. The buy average (based on the closing price on the transfer date) will be updated within 3 working days.

If the discrepancy persists after 3 working days, please let us know and we'll investigate."

### Rule 7: Buy Average Not Updated
**if:** Receiver says buy average shows N/A or wrong for gifted stocks after 3+ working days
**then:** "The buy average for gifted stocks should be updated within 3 working days of the transfer. If it's still showing as N/A or incorrect after 3 working days, we'll look into this." Escalate.

### Rule 8: Gift Charges
**if:** Client asks about gift charges or sees unexpected charge
**then:** "Standard off-market transfer charges apply: ₹25 per security per transaction + 18% GST. These are debited from the sender's trading account. If you gifted 3 different stocks in one transaction, the charges would be ₹75 + 18% GST."

Note: Gift won't process if sender's trading account balance is negative.

### Rule 9: Sender Balance Negative — Gift Won't Process
**if:** Gift not processing and sender has negative balance
**then:** "The gift request cannot be processed because the sender's trading account has a negative balance. The sender needs to add funds to cover the transfer charges (₹25 + 18% GST per security). Once funds are added, the balance updates the next day, and the gift can be processed."

### Rule 10: Escalation Criteria
**if:** Any of the following:
- Stocks Transferred but not visible after 2+ trading days (Rule 5)
- Buy average not updated after 3+ working days (Rule 7)
- Gift fails repeatedly despite all steps completed correctly (KB trigger)
**then:** Escalate with: client ID (sender/receiver), creation date, status, items, and specific issue.
