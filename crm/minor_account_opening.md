# minor_account_opening

## Description

WHEN TO USE:

- Customer asks about minor account opening application status
- Customer reports application rejected or stuck in processing
- Customer hasn't received login credentials after account opening
- Customer asks about PAN verification failure during minor account opening
- Customer asks what documents are needed for minor account

TRIGGER KEYWORDS: "minor account status", "minor account opening", "minor demat", "child account", "minor application", "minor rejected", "minor login credentials", "minor PAN failed", "esign minor", "minor account processing"

## Protocol

# MINOR_ACCOUNT_OPENING PROTOCOL

## Knowledge Base

<knowledge_base>
<facts>
- Online opening: guardian needs Zerodha account + both Aadhaar linked to mobile
- Online: account opens within 48 working hours after verification
- Offline: 72 working hours after documents received at Bengaluru office
- No account opening charges or AMC
- PAN mandatory for minor — apply at onlineservices.nsdl.com if needed
- Guardian signs all forms; unique mobile + email required per minor account (offline)
- Minors CANNOT buy shares — can sell holdings, buy MF, apply for IPOs/buybacks/takeovers
- Only minor's bank account can be linked (not guardian's)
- Joint bank account OK only if minor is a holder
- NRI-minor: offline only
- Login credentials sent to registered email after account enabled at exchanges
- Pre-Jan 2024 demat-only accounts: submit trading form + KYC for Kite access (72 working hours)
- When minor turns 18: convert to individual account (fresh KYC)
</facts>

<field_usage>
  <share>reasons (customer-friendly language)</share>
  <banned>status | form_type | eq_signed_on | minor_client_id | full_name | client_id | creation | modified</banned>
</field_usage>

<status_values>
  <processing>Under review. If >48 working hours + no reasons → ESCALATE. If reasons present → share rejection reasons.</processing>
  <completed>Approved. Account enabled within 24-48 hours. Credentials sent to registered email.</completed>
</status_values>

<timelines>
  <online_opening>48 working hours</online_opening>
  <offline_opening>72 working hours</offline_opening>
  <kite_access_offline>72 working hours after trading form received</kite_access_offline>
</timelines>

<trading_restrictions>
  <cannot>Buy shares, govt securities, intraday, F&O, OFS</cannot>
  <can>Sell holdings, buy MF (Coin), IPOs, buybacks, takeovers</can>
</trading_restrictions>

<documents_online>Minor PAN | Guardian PAN | Minor Aadhaar (OTP) | DOB proof | Minor photo | Bank proof | Guardian signature | Legal guardian letter (if not parent)</documents_online>

<links>
  <online_signup>signup.zerodha.com/minor</online_signup>
  <ipv>signup.zerodha.com/ipv</ipv>
  <offline_email>forms@zerodha.com</offline_email>
  <pan_apply>onlineservices.nsdl.com/paam/endUserRegisterContact.html</pan_apply>
</links>

<courier_address>Zerodha Customer Support Centre, 192A 4th Floor, Kalyani Vista, 3rd Main Road, JP Nagar 4th Phase, Bengaluru, 560076</courier_address>
</knowledge_base>

---

## Business Rules

### Rule 0: Scope Check — This Tool = Application Status Only
**if:** Query is about trading restrictions, fund transfers, MF investment, guardian change, converting to individual, or Kite login for pre-2024 accounts
**then:** Answer from `<facts>`, `<trading_restrictions>`, or relevant knowledge base sections. Do NOT rely on tool output for these.

### Rule 1: Application Processing — Within Timeline
**if:** `status` = "processing" AND `creation` ≤ 48 working hours ago AND `reasons` is empty/null
**then:** "Your minor account application is being reviewed. It typically takes up to 48 working hours for the account to be processed after document verification."

### Rule 2: Application Processing — Rejected / Reasons Present
**if:** `status` = "processing" AND `reasons` is NOT empty
**then:** "Your minor account application requires corrections. [Share reasons in clear, simple language]. Please make the necessary changes and resubmit."

Common reason translations:
- "Bank proof invalid/unclear" → "Please provide a clear copy of the minor's cancelled cheque, bank statement, or passbook"
- "DOB proof missing/invalid" → "Please upload a valid date of birth proof (birth certificate, school leaving certificate, passport, or marksheet)"
- "eSign pending/failed" → "The guardian's eSign is pending. Please complete the eSign to proceed"
- "IPV pending" → "In-Person Verification is pending. Both guardian and minor must complete IPV at signup.zerodha.com/ipv"
- "PAN verification failed" → "The minor's PAN verification failed. Please verify the PAN number and date of birth match the Income Tax Department records"

### Rule 3: Application Processing — Overdue
**if:** `status` = "processing" AND `creation` > 48 working hours ago AND `reasons` is empty/null
**then:** ESCALATE. "Your application has been under review for longer than expected. I'm escalating this to our team for priority processing."

### Rule 4: Application Completed
**if:** `status` = "completed"
**then:** "Your minor account application has been approved. The account will be enabled within 24-48 hours, and login credentials will be sent to the registered email ID."

If customer says they haven't received credentials: "Please check your registered email (including spam/junk folder). If credentials haven't arrived within 48 hours of approval, please let us know."

### Rule 5: eSign Not Completed
**if:** `status` = "processing" AND `eq_signed_on` is empty/null
**then:** "It appears the guardian's eSign has not been completed yet. Please complete the eSign process to proceed with the application. You can do this during the account opening flow at signup.zerodha.com/minor."

### Rule 6: PAN Verification Failed During Opening
**if:** Customer reports "PAN verification failed" error during minor account opening
**then:** "The minor's PAN could not be verified. This means either the PAN number or date of birth entered does not match the Income Tax Department (ITD) records. Please verify the details at incometax.gov.in. If the PAN was recently issued, it may take a few days to reflect in the ITD database."

### Rule 7: NRI-Minor Account
**if:** Customer asks about opening NRI-minor account
**then:** "NRI-minor accounts can only be opened offline. Please email the required documents to forms@zerodha.com for review, then courier them to our Bengaluru office. The account will be opened within 72 working hours after document verification."

### Rule 8: What Can Minors Do?
**if:** Customer asks about trading capabilities in minor account
**then:** "Minor accounts have specific restrictions as per SEBI regulations. Minors cannot buy shares or place intraday/F&O orders. However, minors can sell existing holdings, invest in mutual funds through Coin, and apply for IPOs, buybacks, and takeovers. The guardian can transfer securities to the minor's account using CDSL Easiest or Zerodha's gifting feature."

### Rule 9: Protect Internal Fields
**NEVER expose:** `status`, `form_type`, `eq_signed_on`, `minor_client_id`, `full_name`, `client_id`, `creation`, `modified`
