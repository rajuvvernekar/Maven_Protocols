# get_all_client_data

## Description

WHEN TO USE:

- To look up client profile, account status, PAN, DOB, category
- To determine account type: NRI (NRE/NRO), PIS/Non-PIS, joint, minor, non-individual
- To check bank details, segment status, dormancy, DDPI/POA, nominees, account blocks
- To detect name/DOB mismatch before calling pan_status tool
- To check if an account is BSDA
- To provide client context for: account_modification_report, cashier_payins, withdrawal_request, crux_qs_payouts

## Protocol

# GET ALL CLIENT DATA PROTOCOL

## Knowledge Base

<knowledge_base>

<facts>
- Internal data-lookup tool — interpretation only, business logic in downstream tools
- Interactions/Communications tabs: never access or surface
- Documents tab: only if explicitly requested + agent has "Client Documents Viewer" role
- `account_blocks` non-empty → ESCALATE TO SM immediately
- Bank account numbers: mask all except last 4 before sharing
- `*_soft_enable`: 0 = kill switch ON (segment disabled by client), 1 = OFF
- `custodial_participant_code` has value → Orbis (NRI custodial)
- `zbl_mcx_status` Active → single ledger; withdrawal: weekdays 11:59 PM, Saturday 4:30 PM
- `idfc_3_in_1_status` = Yes → IDFC 3-in-1 account active
- `bsda_flag` = YES → Basic Services Demat Account benefits active
- `rekyc_flag` = True → ReKYC completed; `rekyc_date` = date of completion
- NRE PIS accounts cannot withdraw
- Max 3 banks: 1 primary (payin + withdrawal) + 2 secondary (payin only)
- Primary bank change online: Individual and NRO Non-PIS only
<!-- TODO: settlement_preference (Monthly/Quarterly) not yet exposed. Consumed by crux_qs_payouts. -->
<!-- TODO: MTF segment status not yet exposed. -->
</facts>

<field_usage>
  <share>client_name | status | dob | pan | client_acc_type | category | gender | gross_annual_income | gross_annual_income_date | bo_sub_status | bsda_flag | country_list_iso_3166 | nationality | rekyc_flag | rekyc_date | idfc_3_in_1_status | bank_N_name | bank_N_ifsc_code | bank_N_account_type | pis_bank_N_name | pis_bank_N_ifsc_code | nominee_N_first_name | nominee_N_last_name | nominee_N_percentage_of_shares | primary_dp_status | primary_dp_activation_date | primary_dp_joint_account | primary_ddpi_flag | primary_ddpi_agreement_date | poa_consent | all *_status and *_remarks fields | zbl_mcx_status</share>
  <banned>owner | modified_by | broker_code | support_code | support_code_masked | email_masked | mobile_masked | primary_dp_id | primary_dp_account_no | secondary_dp_id | secondary_dp_account_no | tertiary_dp_id | tertiary_dp_account_no | all *_soft_enable fields | bank_N_account_number (raw) | bank_N_micr_code | bank_N_poa | pis_bank_N_account_number | pis_bank_N_micr_code | docstatus | idx | doctype | creation | modified | acc_open_flag | eq_sign | eq_signed_on | comm_sign | comm_signed_on | tags | holdings_as_on_date | poa_details | address_details | bank_details | dp_details | segment_details | client_documents | uid_meta</banned>
  <mask>bank_N_account_number, pis_bank_N_account_number → last 4 only (****1234)</mask>
</field_usage>

<account_type_detection>
  <individual>`category` = "Individual" AND `client_acc_type` = "Individual"</individual>
  <joint>`primary_dp_joint_account` = "YES"</joint>
  <minor>`bo_sub_status` contains "Minor"</minor>
  <nri>`client_acc_type` IN ("NRO", "NRE", "NRI")</nri>
  <nre>`bo_sub_status` contains "RepatriableWith"</nre>
  <nro>`bo_sub_status` contains "NonRepatriableWith"</nro>
  <pis>`pis_bank_1_name` OR `pis_bank_2_name` NOT None</pis>
  <non_pis>Both `pis_bank_*_name` = None</non_pis>
  <non_individual>`category` = "Non-Individual"</non_individual>
  <orbis>`custodial_participant_code` NOT None</orbis>
  <nri_resolution>If `client_acc_type` = "NRI" → NRE/NRO via `bo_sub_status` → PIS via `pis_bank_*`</nri_resolution>
</account_type_detection>

<account_statuses>
  <approved>Active</approved>
  <deactivated>Closed permanently</deactivated>
  <inactivated>Soft-closed / voluntarily deactivated</inactivated>
</account_statuses>

<segment_statuses>
  <activated>Active — if `*_update_on` &lt; 24h and orders rejected → exchange pending, wait. If > 24h → ESCALATE</activated>
  <segment_not_active>Not activated</segment_not_active>
  <dormant>No trading 24+ months — requires ReKYC</dormant>
  <pending>In progress — if approved in account_modification_report and > 48h → ESCALATE</pending>
  <activation_pending>Same as Pending</activation_pending>
  <activation_rejected>ESCALATE</activation_rejected>
  <blocked>ESCALATE</blocked>
  <inactivated>Disabled by Zerodha — fresh request needed</inactivated>
</segment_statuses>

<segment_field_mapping>
  <nse_eq>NSE Equity</nse_eq>
  <bse_eq>BSE Equity</bse_eq>
  <nse_fo>NSE F&amp;O</nse_fo>
  <bse_fo>BSE F&amp;O</bse_fo>
  <nse_cfx>NSE Currency Derivatives</nse_cfx>
  <bse_cds>BSE Currency Derivatives</bse_cds>
  <nse_com>NSE Commodity</nse_com>
  <mcx>MCX Commodity (legacy)</mcx>
  <starmf>Mutual Funds (Coin)</starmf>
  <nse_slb>NSE SLB</nse_slb>
  <bse_slb>BSE SLB</bse_slb>
  <cdsl>Demat (CDSL)</cdsl>
  <kra>KYC Registration Agency</kra>
  <ckyc>Central KYC</ckyc>
  <itd>Income Tax Department</itd>
  <zbl_mcx>Single Ledger MCX</zbl_mcx>
  <!-- TODO: mtf — not yet exposed -->
</segment_field_mapping>

<bank_structure>
  <primary>bank_1_* → payin + withdrawal</primary>
  <secondary>bank_2_* → payin only</secondary>
  <tertiary>bank_3_* → payin only</tertiary>
  <pis>pis_bank_1_*, pis_bank_2_* → NRI PIS only</pis>
</bank_structure>

<pan_mismatch_response>As per the regulations, to carry out any transactions in the account, the name on the Income tax database (ITD), Exchange (NSE, BSE, MCX), and Depository (CDSL) and KRA records should match. Since your name doesn't match the intermediary records, we request you update your name and verify the correct date of birth (DOB) as soon as possible by following the instructions mentioned below.

Check the name and DOB as per ITD by logging in to the Income Tax Department portal.
Check the name as per Zerodha records on the Console by downloading the CMR copy.
To know the documents required and the process to update your name, please visit here.
Note:
Please send the scanned copies of the documents for verification by creating a ticket here before sending them via courier.
It may take up to 7 working days after the documents are received. You can only carry out the transactions on your Zerodha account once your records are updated.</pan_mismatch_response>

<links>
  <bsda_info>https://support.zerodha.com/category/account-opening/resident-individual/ri-online/articles/how-to-open-a-basic-service-demat-account-at-zerodha</bsda_info>
  <withdrawal_timeline>https://support.zerodha.com/category/funds/fund-withdrawal/withdrawal-timeline/articles/how-much-time-does-it-take-to-process-a-withdrawal-request</withdrawal_timeline>
</links>

</knowledge_base>

---

## Business Rules

### Rule 0: Account Blocks (MANDATORY FIRST)
**if:** `account_blocks` non-empty
**then:** ESCALATE TO SM BECAUSE OF [value]. Stop all further interpretation.

### Rule 1: Dormancy (GLOBAL — every call)
**if:** `nse_eq_status` OR `bse_eq_status` = "Dormant"
**then:** "As you have not traded in your account in 2 years, you must complete your Re-KYC online. Our team will validate the details entered, and the IPV captured and your account status will be marked as Active within 24-48 working hours and we request your patience in this."

**if:** Other segments show "Dormant" → same ReKYC message, name the segment via `<segment_field_mapping>`.

### Rule 2: Account Type Resolution
**if:** `client_acc_type` = "NRI" → resolve NRE/NRO via `bo_sub_status`, then PIS via `pis_bank_*` [refer `<account_type_detection>`]
**Flags to set:**
- Joint (`primary_dp_joint_account` = "YES") → DDPI offline only, IMPS/NEFT/RTGS auto-reversed if bank linked to multiple Zerodha accounts
- Minor (`bo_sub_status` contains "Minor") → F&O blocked
- Non-individual (`category` = "Non-Individual") → F&O offline only, DDPI offline only, ReKYC can be done online

### Rule 3: Segment Status
Interpret `[segment]_status` per `<segment_statuses>`. For `*_soft_enable` = 0 → kill switch enabled.

### Rule 4: PAN / Name / DOB Mismatch
**if:** Client reports name/DOB mismatch
**then:**
1. Extract `pan`, `client_name`, `dob` from response
2. Call `pan_status` tool with those fields
3. PAN: "E" = valid | else = invalid. Name/DOB: "Y" = match | "N" = mismatch. Aadhaar-PAN: "Y" = linked | "R"/"N" = not linked | "NA" = exempt (NRI, non-citizen, age >80, Assam/Meghalaya/J&K)
4. If Name OR DOB = "N" → respond with `<pan_mismatch_response>`

### Rule 5: DDPI / POA
**if:** `primary_ddpi_flag` = "Yes" → DDPI active, no TPIN needed
**if:** `poa_consent` = "YES" AND `primary_poa_for_securities` NOT IN ("NO", "PENDING") → POA active (legacy)
**if:** Neither → client must use CDSL TPIN/OTP
**Online DDPI eligibility:** Individual + Aadhaar-linked mobile. NOT: joint, non-individual, Orbis NRI.

### Rule 6: Bank Details
Mask `bank_N_account_number` and `pis_bank_N_account_number` → last 4 only.
`bank_N_account_type` = "Saving -OD" → overdraft, not allowed.
NRE PIS + withdrawal query → cannot withdraw.

### Rule 7: Withdrawal Timing
`zbl_mcx_status` Active → weekdays 11:59 PM, Saturday 4:30 PM. Else → standard timelines. [Consumed by withdrawal_request]

### Rule 8: Nominees
`nominee_1_first_name` None → no nominees. Share: first name, last name, percentage only. Guardian fields only if asked about minor nominees.

### Rule 9: Protect Internal Fields
**NEVER expose** fields in `<field_usage><banned>`.
Email/mobile requests → "For security, we cannot share contact details. Please check your registered email/mobile in the Kite app under Profile."
