# account_modification_report

## Description

WHEN TO USE:

- Customer wants to activate a segment or exchange (NSE, BSE, MCX, etc.) on their inactive account
- Customer wants to activate Coin or enable trading on their account
- Customer wants to change their primary or secondary bank account
- Customer wants to activate MTF (Margin Trading Facility) or DDPI features
- Customer wants to update their address using Aadhar verification
- Customer wants to update DOB, gender, marital status, occupation, or PEP status
- Customer wants to add, update, remove, or manage their nominee details
- Customer wants to change or update their registered mobile number
- Customer wants to change or update their registered email address
- Customer wants to update their income proof or income details
- Customer wants to open, activate, or check status of a secondary DEMAT account
- Customer wants to close, deactivate, or initiate closure of their trading account
- Customer wants to cancel an account closure request that was submitted by mistake
- Customer wants to check the status of an ongoing account closure process
- Customer wants to know about open positions before closing their account
- Customer asks for status of a pending account modification request
- Customer reports an invalid IFSC code error while adding or changing a bank account

TRIGGER KEYWORDS: "activate", "segment activation", "Coin", "bank account", "change bank", "modify bank", "DDPI", "MTF", "margin", "address update", "Aadhar", "status of request", "DOB", "date of birth", "gender", "marital status", "occupation", "PEP", "politically exposed", "nominee", "add nominee", "change nominee", "update nominee", "remove nominee", "nominee details", "nominee percentage", "nominee address", "mobile number", "change mobile", "update mobile", "unable to change mobile", "already registered mobile", "email", "change email", "update email", "email address", "email-id", "income proof", "income details", "update income", "secondary demat", "secondary account", "open secondary demat", "secondary account opening", "secondary account rejected", "secondary account status", "secondary account on hold", "contact details", "CERSAI", "close account", "close demat", "account closure", "close trading account", "deactivate account", "submit account closure", "cancel closure request", "closure request submitted by mistake", "open positions", "account closure status", "closure process", "invalid IFSC", "IFSC code error", "IFSC not working", "wrong IFSC"

## Protocol

# ACCOUNT MODIFICATION PROTOCOL

## Knowledge Base

<knowledge_base>
<facts>
- ReKYC reactivates dormant accounts and previously held segments
- Active accounts add new segments without ReKYC
- Name/PAN updates: NOT this tool — escalate
- DDPI replaced POA (Nov 2022); optional — CDSL TPIN usable instead
- Secondary demat: resident individuals only, free
- PayTM Payments Bank cannot be linked
- Max 3 bank accounts: 1 primary (payin + withdrawal) + 2 secondary (payin only)
- Overdraft accounts not allowed
- IL&FS queries: specialised handling required
- Account closure blocked if: negative balance, open positions, unlisted securities, pending corporate actions
- Cannot reopen same account/user ID after closure
- All segment activations (F&O, Currency, MCX/Commodity) require both trading AND demat accounts to be active
</facts>

<timelines>
<processing>24–72 working hours</processing>
<activation>24 working hours after approval</activation>
<fo_activation>Up to 72 working hours</fo_activation>
<bank_secondary_update>48 working hours</bank_secondary_update>
<account_closure>2 working days</account_closure>
<ddpi_offline>24 working hours</ddpi_offline>
<secondary_demat>72 working hours</secondary_demat>
<deactivated_reactivation>7 working days</deactivated_reactivation>
<poa_ddpi_revocation>Up to 5 working days</poa_ddpi_revocation>
</timelines>

<charges>
<modification_standard>₹25 + 18% GST</modification_standard>
<ddpi_offline>₹100 + 18% GST</ddpi_offline>
<secondary_demat_transfer>₹13 + 18% GST per transaction</secondary_demat_transfer>
<secondary_demat_amc>₹300 + 18% GST per account</secondary_demat_amc>
</charges>

<common_requirements>
<aadhaar_linked>Mobile number must be linked to Aadhaar</aadhaar_linked>
<income_proof_options>Bank statement (6 months, avg ₹10k+) | Salary slip (gross monthly ₹15k+) | ITR (gross annual ₹1.2L+) | Form 16 (gross annual ₹1.2L+) | Net worth certificate (₹10L+) | Demat holdings (₹10k+, unpledged) | FD receipt (₹1L+)</income_proof_options>
<bank_proof_options>Personalised cancelled cheque (name printed) | Self-attested bank statement (IFSC/MICR visible) | Self-attested passbook</bank_proof_options>
<address_proof_options>Driving Licence | Voter ID | Passport | Masked Aadhaar | NREA job card | NPR letter</address_proof_options>
<file_requirements>PDF | Under 5 MB | Logo and seal of authority</file_requirements>
<offline_courier_address>Zerodha Customer Support Centre, 192A 4th Floor, Kalyani Vista, 3rd Main Road, JP Nagar 4th Phase, Bengaluru, 560076</offline_courier_address>
</common_requirements>

<form_mapping>
<segment_activation>form_type: rekyc + segment_addition</segment_activation>
<coin_activation>form_type: rekyc</coin_activation>
</form_mapping>

<account_modification>

<address_change_offline>
<required_documents>Modification + KYC forms | Self-attested PAN | Address proof [refer to common_requirements:address_proof_options]</required_documents>
<charges>Refer to charges:modification_standard</charges>
<processing_time>Refer to timelines:processing</processing_time>
<validity>Forms valid 30 days from submission</validity>
<conditions>Signature must match account opening | NRI: notarised address proof | Online available if [refer to common_requirements:aadhaar_linked]</conditions>
<courier_address>Refer to common_requirements:offline_courier_address</courier_address>
</address_change_offline>

<address_change_online>
<eligibility>Refer to common_requirements:aadhaar_linked</eligibility>
<ineligible>Joint accounts | Mobile not linked to Aadhaar</ineligible>
<process_url>account.zerodha.com/account</process_url>
<charges>Refer to charges:modification_standard</charges>
<processing_time>Refer to timelines:processing</processing_time>
<requirements>Name on Aadhaar must match e-sign name | Minor: Minor's Aadhaar for address; guardian's Aadhaar for e-sign</requirements>
</address_change_online>

<contact_details_change>
<support_article>[How to change the registered email ID and mobile number with Zerodha?](https://support.zerodha.com/category/your-zerodha-account/account-modification-and-segment-addition/account-modification/articles/change-contact-details) — share this instead of listing steps</support_article>
<online>Platform: Kite app/web | Eligibility: Indian mobile, [refer to common_requirements:aadhaar_linked], IPV, e-sign | Processing: Refer to timelines:activation | Ineligible: international mobile, non-individual, joint accounts</online>
<offline>Courier to [refer to common_requirements:offline_courier_address] | Docs: modification form + IPV | Processing: Refer to timelines:activation | No charges | Mandatory for non-individual; optional for individual</offline>
<international_mobile_nri>eSign and attach to ticket, or courier | Include masked Aadhaar if mentioned</international_mobile_nri>
<no_access_to_contact_details>Client has no access to registered mobile AND email → refer to [How do I reset my Zerodha password if I can't access my registered phone number or email?](https://support.zerodha.com/category/console/profile/account/articles/reset-password-new-contact-details)</no_access_to_contact_details>
<contact_modification_error>Mobile/email already linked to another account → ESCALATE TO SUPPORT MANAGER</contact_modification_error>
</contact_details_change>

<dob_gender_marital_occupation_pep_update>
<online>Condition: correct on Aadhaar + ITD | Process: account.zerodha.com/account → ReKYC → Update profile → IPV → e-sign</online>
<offline>Condition: Aadhaar not linked OR joint account | Docs: modification form, self-attested PAN, address proof [refer to common_requirements:address_proof_options] | Charges: Refer to charges:modification_standard | Processing: Refer to timelines:processing | Courier: Refer to common_requirements:offline_courier_address</offline>
</dob_gender_marital_occupation_pep_update>

<financial_proof_update>
<process_url>signup.zerodha.com/rekyc</process_url>
<processing_time>Refer to timelines:processing</processing_time>
<acceptable_proofs>Refer to common_requirements:income_proof_options</acceptable_proofs>
<file_requirements>Refer to common_requirements:file_requirements</file_requirements>
</financial_proof_update>

<account_deactivation>
<method>Kill Switch feature</method>
<effects>Trading deactivated, demat frozen | No Kite/Console access | AMC continues | Periodic emails continue</effects>
<deactivation>Online: eSign deactivation form and attach to ticket | Offline: Courier deactivation form to [refer to common_requirements:offline_courier_address]</deactivation>
<reactivation>Docs: reactivation letter, self-attested PAN, address proof [refer to common_requirements:address_proof_options] | Processing: Refer to timelines:processing | Courier: Refer to common_requirements:offline_courier_address</reactivation>
</account_deactivation>

<modification_cancellation>
<condition>Client requests cancellation of a pending modification (any type) where eSign not yet completed</condition>
<resolution>Acknowledge cancellation request → ESCALATE TO ACCOUNT MODIFICATION TEAM</resolution>
</modification_cancellation>

</account_modification>

<bank_accounts>

<primary_bank_change_online>
<eligibility>Individual accounts, NRO Non-PIS</eligibility>
<process>Console → Account → Bank → Modify → Details → E-sign</process>
<verification>Test transfer to verify</verification>
<charges>Refer to charges:modification_standard</charges>
<processing_time>Refer to timelines:processing</processing_time>
<joint_bank_account>Primary holder of bank and demat must match | If different: offline with modification form + bank proof [refer to common_requirements:bank_proof_options]</joint_bank_account>
<minor_accounts>Online; guardian e-signs | Bank details must be for minor</minor_accounts>
</primary_bank_change_online>

<secondary_bank_add>
<eligibility>Resident individual or non-individual</eligibility>
<process>Console → Account → Bank → Add → Details → OTP → Verify</process>
<processing_time>Refer to timelines:bank_secondary_update</processing_time>
<note>Deposits only, no withdrawals</note>
<joint_account_secondary>If not first holder: attach self-attested bank proof [refer to common_requirements:bank_proof_options] to ticket</joint_account_secondary>
</secondary_bank_add>

<secondary_bank_change>
<process>Console → Account → Bank → Modify → Details → OTP → Verify</process>
<verification>Test transfer</verification>
<processing_time>Refer to timelines:bank_secondary_update</processing_time>
<charges>No charges</charges>
<failure_handling>If verification fails or joint account: attach bank proof [refer to common_requirements:bank_proof_options] to ticket</failure_handling>
</secondary_bank_change>

<secondary_to_primary_conversion>
<eligibility>Refer to common_requirements:aadhaar_linked</eligibility>
<process>Console → Account → Bank → Set as primary → E-sign</process>
<processing_time>Refer to timelines:processing</processing_time>
<charges>Refer to charges:modification_standard</charges>
<effect>Current primary becomes secondary</effect>
<note>During processing, withdrawals go to old primary</note>
</secondary_to_primary_conversion>

<secondary_bank_remove>
<process>Console → Account → Bank → Delete → OTP → Verify</process>
<processing>Instant</processing>
</secondary_bank_remove>

<bank_account_types_allowed>
<allowed>Savings | Current | Cash Credit</allowed>
<not_allowed>Overdraft (OD)</not_allowed>
</bank_account_types_allowed>

<current_account_linking>
<allowed>Yes, as primary or secondary</allowed>
<condition>Names match across Zerodha/PAN/bank</condition>
<primary_documents>Modification form, cancelled cheque/statement, banker letter</primary_documents>
<secondary_documents>Update Console, then attach banker letter to ticket</secondary_documents>
<banker_letter_requirement>States account holder solely runs business and makes all transactions</banker_letter_requirement>
<processing_time>Refer to timelines:bank_secondary_update</processing_time>
<charges_primary>Refer to charges:modification_standard</charges_primary>
<courier_address>Refer to common_requirements:offline_courier_address</courier_address>
</current_account_linking>

<joint_bank_accounts>
<allowed>Yes, if joint holder</allowed>
<process>Same as single-holder</process>
<restriction>If linked to multiple Zerodha accounts: UPI/gateway only | IMPS/NEFT/RTGS reversed</restriction>
</joint_bank_accounts>

<bank_details_update_failure>
<causes>Incorrect IFSC (O vs 0 confusion) | Branch/IFSC not recognised by CDSL | System throws "invalid IFSC" error</causes>
<resolution>ESCALATE TO SUPPORT MANAGER. Do NOT ask client for bank proof or attempt to resolve IFSC errors directly.</resolution>
</bank_details_update_failure>

<primary_bank_penny_drop_failure>
<condition>bank_type = "Primary" AND request_type = "update" AND error = bank validation failed</condition>
<resolution>Direct to ReKYC flow at account.zerodha.com | Client uploads bank statement, cheque, or passbook within the ReKYC flow | Do NOT ask client to share bank proof on ticket | Do NOT direct to offline courier process</resolution>
</primary_bank_penny_drop_failure>

<relative_bank_account>
<allowed>No</allowed>
<requirement>SEBI mandates bank in client's name only</requirement>
</relative_bank_account>

</bank_accounts>

<account_closure>
<methods>Online: resident Indians, NRIs, minors with Kite | Offline: non-individual only</methods>
<processing_time>Refer to timelines:account_closure</processing_time>
<pre_closure_requirements>Clear negative balance | Square off positions, sell/transfer holdings | Delete SIPs and mandates | Download reports (inaccessible after closure)</pre_closure_requirements>
<closure_cum_transfer>Transfer holdings to another demat while closing | No additional charges | Refer to [SOP](https://s3.ap-south-1.amazonaws.com/staticassets.zerodha.net/support-portal/2025/06/24/Article/FZUJ7VWF_E6T6ngib3xeSu0JR1750748598.pdf)</closure_cum_transfer>
<online_closure_process>Console → Account → Segments → Account closure | Options: Sell holdings (Kite redirect) OR Transfer holdings (demat in your name only) | Accept terms → eSign with Aadhaar</online_closure_process>
<amc_after_closure>Not charged from day closure is processed</amc_after_closure>
</account_closure>

<demat>

<ddpi>
<definition>Document allowing broker to debit securities</definition>
<benefit>No CDSL TPIN/OTP required for selling</benefit>
<sebi_restriction>Debits only for client-placed sell trades</sebi_restriction>
<optional>Yes — can use CDSL TPIN instead</optional>
</ddpi>

<ddpi_activation_online>
<process>Console → Account → Demat → Enable DDPI → Accept → E-sign with Aadhaar</process>
<minor_accounts>Guardian's Aadhaar required</minor_accounts>
</ddpi_activation_online>

<ddpi_activation_offline>
<applies_to>NRI using Orbis | Joint accounts | Non-individual</applies_to>
<documents>DDPI form (signature must match account opening)</documents>
<courier_address>Refer to common_requirements:offline_courier_address</courier_address>
<charges>Refer to charges:ddpi_offline</charges>
<requirement>Sufficient balance for charge deduction</requirement>
<processing_time>Refer to timelines:ddpi_offline</processing_time>
</ddpi_activation_offline>

<poa_ddpi_status_check>
<kite_app>User ID → Profile</kite_app>
<kite_web>Client ID → My Profile</kite_web>
<alternative>CDSL TPIN if no POA/DDPI</alternative>
</poa_ddpi_status_check>

<poa_ddpi_revocation>
<online>Eligibility: individual, [refer to common_requirements:aadhaar_linked] | Process: Print → Fill → Sign → Scan → eSign → Attach to ticket</online>
<offline>Applies to: non-individual, joint, individual with no Aadhaar link | Process: Print → Fill → Courier to [refer to common_requirements:offline_courier_address]</offline>
<processing_time>Refer to timelines:poa_ddpi_revocation</processing_time>
<post_revocation>Must use CDSL TPIN to sell</post_revocation>
</poa_ddpi_revocation>

<secondary_demat_account>
<availability>Free, online</availability>
<eligibility>Refer to common_requirements:aadhaar_linked | Resident individual only</eligibility>
<process>Kite → User ID → Profile → Demat → Secondary → Nominee → IPV → E-sign</process>
<processing_time>Refer to timelines:secondary_demat</processing_time>
<visibility>Console only (not Kite)</visibility>
<closure>Offline only</closure>
</secondary_demat_account>

</demat>

<segments>

<fo_activation>
<requirement>Equity segment must be active</requirement>
<demat_prerequisite>Refer to Rule 9 — `primary_dp_status` must be "Active" before ANY segment activation</demat_prerequisite>
<online_eligibility>Refer to common_requirements:aadhaar_linked</online_eligibility>
<offline_only>Non-individual accounts</offline_only>
<process>Kite/Console → User ID → Profile → Segments → Activate</process>
<required_info>Income range and proof | Trading experience | Commodity classification (for commodities)</required_info>
<processing_time>Refer to timelines:fo_activation</processing_time>
<income_proof_options>Refer to common_requirements:income_proof_options</income_proof_options>
<file_requirements>Refer to common_requirements:file_requirements</file_requirements>
<commodity_classification>Farmers/FPO: Farmer, cooperatives, FPOs | VCP: Processor, commercial user, importer, exporter, trader, stockist, producer, SME/MSME, wholesaler | Others: MCX traders not in above</commodity_classification>
<restrictions>Sikkim: domicile certificate for commodities | Minors: cannot enable F&O</restrictions>
<currency_fo>RBI declaration form eSign required</currency_fo>
</fo_activation>

<active_segments_check>
<kite_app>Client ID → Profile</kite_app>
<kite_web>Client ID → Name</kite_web>
<action>Click segment → Console redirect for Kill Switch</action>
</active_segments_check>

</segments>

<nomination>
<verification>Console → Account → Nominees | CMR copy</verification>
<inactivity_alert>Condition: no trading for 24 months → deactivated/dormant | If not reactivated within 30 days → nominee notified</inactivity_alert>
</nomination>

<kyc>

<deactivated_account_reactivation>
<applies_to>Voluntarily deactivated only</applies_to>
<dormant_accounts>Complete Re-KYC instead</dormant_accounts>
<online_reactivation>Eligibility: Refer to common_requirements:aadhaar_linked | Method: Attach eSigned reactivation letter to ticket</online_reactivation>
<offline_reactivation>Docs: signed reactivation letter, self-attested PAN, address proof [refer to common_requirements:address_proof_options] | Courier: Refer to common_requirements:offline_courier_address</offline_reactivation>
<processing_time>Refer to timelines:deactivated_reactivation</processing_time>
<result>Same client ID, new password</result>
<demat_closed>Submit demat application</demat_closed>
<account_closed>Complete new account opening</account_closed>
</deactivated_account_reactivation>

<additional_documents_request>
<reason>SEBI requires valid, current documents</reason>
<father_name_rekyc_note>If father/spouse name mismatch is flagged during ReKYC flow, client CANNOT skip this field. Must follow offline process — refer to rejection_reasons:father_name_mismatch below</father_name_rekyc_note>
<rejection_reasons>
PAN not clear → attach clear self-attested PAN |
Minor PAN → attach major PAN |
Father name mismatch → refer to [How to change the name in my Zerodha account?](https://support.zerodha.com/category/your-zerodha-account/your-profile/general-profile-questions/articles/why-is-the-name-on-my-zerodha-account-different-than-on-the-documents-i-ve-submitted); courier completed forms + self-attested PAN + address proof [refer to common_requirements:address_proof_options] to [refer to common_requirements:offline_courier_address]; do NOT reference Console for form downloads |
Signature not clear → attach clear self-attested signature |
Name confirmation → attach government ID proof |
Proprietor bank → attach banker letter |
Invalid bank proof → update correct bank details on Console |
Bank not in name → attach self-attested bank proof to ticket or update Console |
Invalid IPV → complete Re-KYC
</rejection_reasons>
</additional_documents_request>

</kyc>

<utilities>
<password_removal_from_pdf>Open PDF → Menu → Print → Print to PDF → Save</password_removal_from_pdf>
<esign_documents>Platform: digilocker.gov.in | Requires: [refer to common_requirements:aadhaar_linked] | Cost: free | Steps: Login → Drive → Documents → Upload → Sign → Enter Aadhaar → OTP → Download</esign_documents>
<trade_alerts_not_received>Cause: incorrect contact details | Resolution: update contact online or offline | If contact correct but no alerts → contact exchanges directly: NSE: nseindia.com/contact/corporate-office | BSE: bseindia.com/static/about/contact_us.aspx | MCX: mcxindia.com/contact-us/department-contacts | Note: DND may block alerts</trade_alerts_not_received>
</utilities>

</knowledge_base>

---

## Business Rules

### Rule 0: Fetch Client Context (MANDATORY FIRST)
**if:** Any account modification query
**then:** Call `get_all_client_data`. Extract and hold:

| Context | Field(s) |
|---|---|
| Account type | `client_acc_type`, `category` |
| Joint | `primary_dp_joint_account` |
| Minor | `bo_sub_status` contains "Minor" |
| NRI subtype | `bo_sub_status` → NRE ("RepatriableWith") / NRO ("NonRepatriableWith") |
| PIS | `pis_bank_1_name`, `pis_bank_2_name` (NOT None = PIS) |
| Orbis | `custodial_participant_code` (NOT None = Orbis) |
| Account status | `status` |
| DDPI/POA | `primary_ddpi_flag`, `poa_consent`, `primary_poa_for_securities` |
| PAN/Name/DOB | `pan`, `client_name`, `dob` |
| Demat status | `primary_dp_status` |

**if:** `account_blocks` non-empty → ESCALATE TO SM BECAUSE OF [value]. Stop.

Check modification report rules first. Then:

**if:** `nse_eq_status` OR `bse_eq_status` = "Dormant" → apply Rule 7 Dormancy Rule.

### Rule 1: Name/DOB/PAN Updates
**if:** Query mentions name change OR DOB mismatch OR PAN correction
**then:** ESCALATE TO SUPPORT MANAGER.

### Rule 2: Form Lookup
**if:** Segment activation query → query form_type IN (rekyc, segment_addition), most recent within 3 months
**if:** Coin/MF query → query form_type = rekyc, most recent within 3 months
**if:** No request found OR last request > 3 months → "Your last request from [date] is closed. Submit new request at account.zerodha.com/account"

### Rule 3: Status-Based Responses
**CRITICAL**: Read the EXACT value of the status field. Do NOT infer or assume status — match ONLY the literal value returned by the tool. Cross-check against the submission date: if a request was submitted today or recently, it is almost certainly NOT yet Approved.

**if:** status = Request_pending / Processing → "Your [modification_type] request was received on [submission_date]. It will be processed within [refer to timelines — use the specific timeline for the modification type, e.g., fo_activation for F&O]. You will receive an email confirmation once complete."
**if:** status = Pending_eSign → "[modification_type] pending eSign — complete on Console to proceed"
**if:** status = Approved → Verify submission_date is at least [relevant timeline] before the current date. Then: "[modification_type] approved on [date]; active within [refer to timelines:activation]"
**if:** status = Rejected → "[modification_type] rejected: [rejection_reason]. Resolve and resubmit."

### Rule 4: ReKYC
**if:** form_type = rekyc
**then:** Visit account.zerodha.com/account → complete ReKYC with Aadhaar eSign | Requires: [refer to common_requirements:aadhaar_linked]
**Charges:** [refer to charges:modification_standard] — applicable ONLY if client selects "Update as per Aadhaar" during ReKYC. Do NOT mention charges otherwise.

### Rule 5: Account Closure
**if:** Query mentions "secondary demat" / "employer policy" / "employer restriction" / "empanelment" / "company policy" / "IL&FS" / "ILFS" / "closure cum transfer" → ESCALATE TO RELEVANT TEAM.

| Status | Response |
|---|---|
| blank / Request_pending / Processing | Express regret; offer Kill Switch alternative; invite feedback call |
| Pending_eSign | Complete eSign on Console to proceed; invite feedback call |
| Rejected | State rejection reason; invite feedback call |
| Approved | Completed within [refer to timelines:account_closure]; invite feedback call |
| No match | ESCALATE TO SUPPORT MANAGER |

### Rule 6: Protect Internal Fields
**NEVER expose:** `form_type`, `description`, `client_id`, `bank_name`, `account_number`, `request_type`, `income_proof`, `new_email`, `new_mobile`, `signer_name`, `notary_id`, `bank_order`, `kyc_field_type`, `STARMF`, `primary_ddpi_flag`, `primary_ddpi_agreement_date`, `poa_consent`, `primary_poa_for_securities`, `primary_dp_status`, **or any raw status value**

**Instead use:** "segment activation" / "bank modification" / "ReKYC" / "primary bank" / "secondary bank" / "DDPI is active" | STARMF → "Your mutual funds are now active and you can start investing on Coin"

### Rule 7: Segment & Account Status Translations

| Raw Status | Response |
|---|---|
| `Reactivation_pending` | Check timestamp of request against current time. If within 24 working hours → "[segment/account] being processed; active within 24 working hours of submission." If 24 working hours have already elapsed → ESCALATE TO SUPPORT MANAGER. |
| `Request_pending` | Same as Reactivation_pending. Cross-check: ReKYC query → verify rekyc form status; segment query → verify segment_addition form status (Rule 2) |
| `Blocked` | Rewrite `remarks` field conversationally. Never copy raw remarks text. |
| `Activated` | "[segment] is active." If client reports unable to place orders: check activation timestamp → if within 24 hours → "activated recently; orders available within 24 working hours of activation" |
| `Dormant` | Apply Dormancy Rule ↓ |

**Dormancy Rule** (triggered when `nse_eq_status` OR `bse_eq_status` = "Dormant"):
1. "Account inactive due to inactivity; trading requires ReKYC."
2. Check `get_all_client_data` for existing ReKYC request:
   - Found + in progress (Request_pending / Processing / Reactivation_pending) → "ReKYC received and being processed; account reactivated within 24–48 working hours"
   - Not found OR > 3 months old → "Complete ReKYC at account.zerodha.com/account"
3. Dormant F&O/commodity segments → after equity reactivation, guide to Console → Account → Segment Activation
4. Do NOT mention dormancy date/year unless asked
5. Do NOT repeat "dormant" more than once

### Rule 8: Segment Rejection — PAN Verification Cross-Check
**if:** Any segment (`nse_eq_status`, `bse_eq_status`, `mcx_status`, etc.) shows as Rejected or Deactivated AND remarks contain "PAN Verification Failed"
**then:**
1. Call `pan_status` tool to retrieve the specific rejection reason.
2. Respond based on the `pan_status` result — follow the pan_status tool's protocol for resolution guidance.
3. Do NOT guess the rejection reason from `get_all_client_data` alone.

### Rule 9: Demat Prerequisite for Segment Activation
**if:** Any segment activation query (F&O, Currency, MCX/Commodity)
**then:** Check `primary_dp_status` from `get_all_client_data`.

**if:** `primary_dp_status` ≠ "Active"
**then:** "To activate any segment, both trading and Demat accounts must be active. You can open a Demat account linked to your existing trading account by following the steps here: [Can I open a demat account if I already have a trading or commodity account?](https://support.zerodha.com/category/your-zerodha-account/account-opening/online-account-opening/articles/open-demat-with-existing-trading-commodity). Once your Demat account is active, you can enable segments under the single ledger facility: [What is the single ledger facility?](https://support.zerodha.com/category/your-zerodha-account/account-opening/online-account-opening/articles/what-is-the-single-ledger-facility)."

**NEVER** promise to activate segments "from the backend." If the system blocks activation, there is always a reason — investigate before responding.

### Rule 10: Nominee Request Rejection — Escalation
**if:** Query mentions nominee modification/request AND customer reports rejection
**then:** 
1. Check `account_modification` form where `form_type` = "nominee_addition"
2. **if:** status = Rejected
   **then:** "Your nominee request was rejected: [rejection_reason]. Our team will investigate this and get back to you shortly." ESCALATE TO ACCOUNT MODIFICATION TEAM with the rejection reason.
3. **if:** status ≠ Rejected
   **then:** Proceed with standard nominee status guidance per Rule 3 (Status-Based Responses)
