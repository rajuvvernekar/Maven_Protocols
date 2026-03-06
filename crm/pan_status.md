# pan_status

## Description

WHEN TO USE:

- Account blocked due to name mismatch or PAN verification failure
- Segment activation rejected with "PAN Verification Failed" remark
- Client reports "name and/or date of birth do not match income tax database" error
- Client asks how to update name/DOB to match PAN
- DOB/Name mismatch flagged on account_modification_report
- Single ledger activation error due to name/DOB mismatch
- Minor account opening fails with "PAN verification failed" (for the minor's PAN)

TRIGGER KEYWORDS: "PAN verification failed", "name mismatch", "DOB mismatch", "name not matching", "income tax database", "ITD mismatch", "change name", "update name", "PAN blocked", "PAN invalid", "segment rejected name"

PREREQUISITE: Always run get_all_client_data FIRST to obtain client_name, pan, dob before checking pan_status.

## Protocol

# PAN_STATUS PROTOCOL

## Knowledge Base

<knowledge_base>
<facts>
- PAN verification checks validity + name/DOB match across ITD, Exchange, Depository, KRA
- All intermediary records must match for trading — SEBI requirement
- Zerodha name sourced from ITD, not submitted documents — may differ
- Name/DOB mismatch blocks transactions until resolved
- Online fix: re-KYC at account.zerodha.com (needs Aadhaar linked to mobile)
- Offline fix: courier documents to Zerodha, ₹25 + GST, updated within 72 working hours
- Resolution may take up to 7 working days after documents received
- Cross-reference get_all_client_data for client_name, pan, dob BEFORE checking pan_status
</facts>

<field_usage>
  <share>NONE — all fields are for agent reference only</share>
  <banned>All raw field values (pan_valid_status, name_match, dob_match, aadhaar_pan_seeding)</banned>
</field_usage>

<pan_valid_status>
  <e>Valid</e>
  <other>Invalid/deactivated/blocked → ESCALATE</other>
</pan_valid_status>

<name_dob_match>
  <y>Matches ITD</y>
  <n>Mismatch — resolution required</n>
</name_dob_match>

<name_change_categories>
  <minor_change>Spelling, interchange, middle name, initials → Online + Offline</minor_change>
  <parent_name>Father's/mother's name → Online + Offline</parent_name>
  <marriage_divorce>Marriage/divorce → Offline only</marriage_divorce>
  <other_reason>Personal preference → Offline only</other_reason>
  <removal>Removing middle/last name → Offline only</removal>
</name_change_categories>

<links>
  <rekyc>account.zerodha.com</rekyc>
  <itd_portal>incometax.gov.in</itd_portal>
  <name_change_article>How to change the name in my Zerodha account?</name_change_article>
</links>

<courier_address>Zerodha Customer Support Centre, 192A 4th Floor, Kalyani Vista, 3rd Main Road, JP Nagar 4th Phase, Bengaluru, 560076</courier_address>
</knowledge_base>

---

## Business Rules

### Rule 0: Prerequisite — Cross-Reference get_all_client_data
**if:** pan_status is being checked
**then:** ALWAYS first retrieve `client_name`, `pan`, `dob` from `get_all_client_data`. These are needed to interpret pan_status results.

### Rule 1: PAN Invalid / Not "E"
**if:** PAN validity status is anything other than "E"
**then:** ESCALATE. "There appears to be a regulatory issue with your PAN. Our team will investigate and get back to you."
Do NOT share the specific PAN status code with the customer.

### Rule 2: Name and/or DOB Mismatch
**if:** Name match = "N" OR DOB match = "N"
**then:** Respond with:

"As per regulations, the name and date of birth on the Income Tax Department (ITD), Exchange, and Depository records must match to carry out transactions. Your records currently show a mismatch.

To resolve this:
1. Check your name and DOB as per ITD by logging into the Income Tax Department portal at incometax.gov.in
2. Check your name as per Zerodha records by downloading the CMR copy from Console
3. If your name needs to be updated, first update it with the ITD, then follow the name change process — visit: How to change the name in my Zerodha account?

For an online fix, visit account.zerodha.com and complete the re-KYC process (Aadhaar must be linked to your mobile number).

Please note: It may take up to 7 working days after documents are received for the update to take effect. Transactions will be enabled once records are updated."

### Rule 3: Name and DOB Both Match
**if:** Name match = "Y" AND DOB match = "Y" AND PAN valid = "E"
**then:** "Your PAN verification is successful — your name and date of birth match the Income Tax Department records." If the customer still faces issues (segment rejection, block), check `get_all_client_data` for other remarks or blocks.

### Rule 4: Minor Account PAN Verification Failed
**if:** Query is about minor account opening + PAN verification failed
**then:** "The minor's PAN verification has failed. This means the PAN number or date of birth entered does not match the Income Tax Department records. Please verify the minor's PAN details and date of birth on the ITD portal at incometax.gov.in, and retry. If the PAN was recently issued, it may take a few days to reflect in the ITD database."

### Rule 5: Single Ledger Activation Error
**if:** Customer reports "name and/or date of birth do not match" error during single ledger activation
**then:** Apply Rule 2. The mismatch must be resolved before single ledger can be enabled.

### Rule 6: Protect All Fields
**NEVER expose:** Any raw pan_status field values. Use only for internal decision-making.
