# stock_transfers

## Description

WHEN TO USE:

- Client asks about the status of a stock transfer between primary and secondary demat accounts
- Client reports transfer failed and wants to know why
- Agent needs to verify transfer history (which stocks, when, direction, status)
- Client says transferred stocks not visible in target account
- Client reports buy average wrong after transferring stocks back from secondary to primary
- Client asks about pending transfer or execution date
- Agent needs to check if a transfer was successfully completed

TRIGGER KEYWORDS: "primary to secondary transfer", "secondary to primary transfer", "stock transfer status", "transfer failed", "transfer pending", "inter-account transfer", "secondary demat transfer", "transfer request status", "stocks transferred between accounts", "transfer not showing"

## Protocol

<knowledge_base>

<facts>
- Report tracks transfers between client's own primary and secondary Zerodha demat accounts only
- Required: Client ID. Optional: From/To Date, Transaction Type (Primary to Secondary / Secondary to Primary).
- Status values: Pending (awaiting execution), Stocks Transferred (completed), Failed (rejected/expired)
- Transfer requires CDSL TPIN authorization and OTP verification
- CDSL sends verification email between 3 PM and 5 PM on trading days; OTP must be completed by 8 PM
- If submitted before 6 PM on trading day → processed same day; after 6 PM → execution date must be next working day
- Transfer charges: ₹13 + 18% GST = ₹15.34 per transfer transaction (regardless of qty or number of securities)
- Buy average auto-updated within 3 working days for stocks transferred between primary and secondary accounts
- Stocks under lock-in, pledge, or frozen status cannot be transferred
- Stocks may show as discrepant in target account until buy average is updated
- Cannot transfer if trading account balance is negative or account is dormant
</facts>

<field_usage>
  <share>creation (as date) | transaction_type (as "direction") | status | execution_date | items (stocks and qty)</share>
  <banned>modified | name (transfer ID) | client_id | secondary_client_id | from_account | to_account | remarks</banned>
</field_usage>

<cross_reference>
  <console_eq_holdings>Verify if transferred stocks visible in target account — may show discrepancy initially</console_eq_holdings>
  <console_eq_external_trades>Transfer entries appear here for buy avg calculation</console_eq_external_trades>
</cross_reference>

<escalation_triggers>
  <transferred_not_visible>Status = Stocks Transferred but not visible in target account after 24 hours</transferred_not_visible>
  <buy_avg_wrong>Buy average not updated or incorrect after 3+ working days post-transfer</buy_avg_wrong>
  <failed_with_otp_done>Transfer failed despite client completing OTP verification</failed_with_otp_done>
</escalation_triggers>

</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
**NEVER expose:** `modified`, `name` (transfer ID), `client_id`, `secondary_client_id`, `from_account`, `to_account`, `remarks`
**Share:** `creation`, `transaction_type` (as direction), `status`, `execution_date`, `items`

### Rule 1: Transfer Status Check
**if:** Client asks about a stock transfer request status
**then:** Look up by Client ID and optional date range.

- Pending → "Your transfer request from [creation date] is pending execution. Transfers submitted before 6 PM are processed the same trading day. If submitted after 6 PM, the execution date will be the next working day."
- Stocks Transferred → "Your transfer of [items] from [direction] was completed on [execution_date]. The stocks will be visible in the target account within 24 hours."
- Failed → see Rule 2.

### Rule 2: Transfer Failed
**if:** status = Failed
**then:** "Your stock transfer request from [creation date] has failed. Common reasons:
- CDSL OTP verification was not completed by 8 PM deadline
- Stocks are under lock-in, pledge, or frozen status
- Trading account has negative or zero balance
- Account is in dormant status

To retry, place a new transfer request on Kite and ensure OTP verification is completed by 8 PM."

If client confirms they completed OTP and balance was sufficient → escalate.

### Rule 3: Transferred Stocks Not Visible
**if:** Status = Stocks Transferred but client says stocks not showing in target account
**then:** "Transferred stocks should be visible within 24 hours of completion. If the transfer was completed today, please check again tomorrow.

If it's been more than 24 hours and the stocks are still not visible, we'll investigate." (Escalate after 24 hours)

### Rule 4: Buy Average After Transfer
**if:** Client reports buy average wrong or showing discrepancy after transfer
**then:** "The buy average for stocks transferred between primary and secondary accounts is automatically updated within 3 working days. During this period, the stocks may show a discrepancy mark or incorrect buy average.

If the buy average is still incorrect after 3 working days, please let us know with the specific stocks and expected buy average." (Escalate after 3 working days → `console_eq_external_trades` for entry correction)

### Rule 5: Transfer Charges
**if:** Client asks about transfer charges
**then:** "The transfer charge is ₹13 + 18% GST = ₹15.34 per transfer transaction between your primary and secondary demat accounts. This charge applies per transaction regardless of the number of shares or stock value being transferred."

### Rule 6: Escalation Criteria
**if:** Any of the following:
- Stocks Transferred but not visible after 24 hours (Rule 3)
- Buy average wrong after 3+ working days (Rule 4)
- Transfer failed despite OTP completion and sufficient balance (Rule 2)
**then:** Escalate with: client ID, creation date, direction, status, items, and specific issue.
