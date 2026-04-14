# account_modification_report

## Description

WHEN TO USE:

When clients:
- Want to activate a segment or exchange (NSE, BSE, MCX, etc.) on their inactive account
- Want to activate Coin or enable trading on their account
- Want to change their primary or secondary bank account
- Want to activate MTF (Margin Trading Facility) or DDPI features
- Want to update their address using Aadhar verification
- Want to update DOB, gender, marital status, occupation, or PEP status
- Want to add, update, remove, or manage their nominee details
- Want to change or update their registered mobile number
- Want to change or update their registered email address
- Want to update their income proof or income details
- Want to open, activate, or check status of a secondary DEMAT account
- Want to close, deactivate, or initiate closure of their trading account
- Want to cancel an account closure request that was submitted by mistake
- Want to check the status of an ongoing account closure process
- Ask about open positions before closing their account
- Ask about status of a pending account modification request
- Report an invalid IFSC code error while adding or changing a bank account

TRIGGER KEYWORDS: "activate", "segment activation", "Coin", "bank account", "change bank", "modify bank", "DDPI", "MTF", "margin", "address update", "Aadhar", "status of request", "DOB", "date of birth", "gender", "marital status", "occupation", "PEP", "politically exposed", "nominee", "add nominee", "change nominee", "update nominee", "remove nominee", "nominee details", "nominee percentage", "nominee address", "mobile number", "change mobile", "update mobile", "unable to change mobile", "already registered mobile", "email", "change email", "update email", "email address", "email-id", "income proof", "income details", "update income", "secondary demat", "secondary account", "open secondary demat", "secondary account opening", "secondary account rejected", "secondary account status", "secondary account on hold", "contact details", "CERSAI", "close account", "close demat", "account closure", "close trading account", "deactivate account", "submit account closure", "cancel closure request", "closure request submitted by mistake", "open positions", "account closure status", "closure process", "invalid IFSC", "IFSC code error", "IFSC not working", "wrong IFSC", "KYC", "ReKYC", "dormant", "no activity", "inactivity"

## Protocol

# ACCOUNT MODIFICATION REPORT PROTOCOL

---

## Section A: Reference Data

---

### A1: Timelines

| Action | Timeline |
|---|---|
| General modification processing | 24–72 working hours |
| Segment activation (after approval) | 24 working hours |
| F&O activation | Up to 72 working hours |
| Contact detail changes (mobile/email) | 24 working hours |
| Secondary bank add/change | 48 working hours |
| Account closure | 2 working days |
| DDPI offline activation | 24 working hours |
| Secondary demat | 72 working hours |
| Deactivated account reactivation | 7 working days |
| POA/DDPI revocation | Up to 5 working days |
| Segment deactivation | 24–72 working hours |

---

### A2: Charges

| Action | Charge |
|---|---|
| Standard modification | ₹25 + 18% GST |
| DDPI activation (online and offline) | ₹100 + 18% GST |
| Secondary demat transfer | ₹13 + 18% GST per transaction |
| Secondary demat AMC | ₹300 + 18% GST per account |

---

### A3: Common Requirements

**Aadhaar-linked mobile:** Mobile number must be linked to Aadhaar (required for most online processes).

**Income proof (any one):** Bank statement (6 months, avg ₹10k+) | Salary slip (gross monthly ₹15k+) | ITR (gross annual ₹1.2L+) | Form 16 (gross annual ₹1.2L+) | Net worth certificate (₹10L+) | Demat holdings (₹10k+, unpledged) | FD receipt (₹1L+)

**Bank proof (any one):** Personalised cancelled cheque (name printed) | Self-attested bank statement (IFSC/MICR visible) | Self-attested passbook

**Address proof (any one):** Driving Licence | Voter ID | Passport | Masked Aadhaar | NREA job card | NPR letter

**File requirements:** PDF, under 5 MB, logo and seal of authority.

**Courier address:** Zerodha Customer Support Centre, 192A 4th Floor, Kalyani Vista, 3rd Main Road, JP Nagar 4th Phase, Bengaluru, 560076

---

### A4: Field Rules

**Internal reasoning only (use for analysis, communicate in plain language):**
`form_type`, `description`, `client_id`, `bank_name`, `account_number`, `request_type`, `income_proof`, `new_email`, `new_mobile`, `signer_name`, `notary_id`, `bank_order`, `kyc_field_type`, `STARMF`, `primary_ddpi_flag`, `primary_ddpi_agreement_date`, `poa_consent`, `primary_poa_for_securities`, `primary_dp_status`, `third_party_demat`, raw segment identifiers (e.g. `NSE_COM`, `NSE_FO`, `BSE_EQ`, `MCX_FO`), raw status values

**Client-friendly translations:**
- `form_type` values → "segment activation" / "bank modification" / "ReKYC" / "primary bank" / "secondary bank"
- `form_type = rekyc` → ReKYC for equity and mutual fund segments
- `form_type = rekyc_fno` → ReKYC for F&O, currency, and commodity segments
- STARMF → "Your mutual funds are now active and you can start investing on Coin"
- NSE_COM → "NSE Commodity"
- `primary_ddpi_flag` active → "DDPI is active"
- Segment `remarks` field → rewrite conversationally. The only exception: `Blocked` status — rewrite `remarks` conversationally for that status only. For all other statuses, use only: "[Segment name] is not currently active on your account."

**Segment status and remarks field pairs:**

| Segment | Status Field | Remarks Field | Client-Facing Name |
|---|---|---|---|
| NSE Equity | `nse_eq_status` | `nse_eq_remarks` | NSE Equity |
| BSE Equity | `bse_eq_status` | `bse_eq_remarks` | BSE Equity |
| NSE F&O | `nse_fo_status` | `nse_fo_remarks` | NSE F&O |
| BSE F&O | `bse_fo_status` | `bse_fo_remarks` | BSE F&O |
| NSE Currency | `nse_cfx_status` | `nse_cfx_remarks` | NSE Currency |
| BSE Currency | `bse_cds_status` | `bse_cds_remarks` | BSE Currency |
| MCX (Commodity) | `mcx_status` | `mcx_remarks` | MCX Commodity |
| NSE Commodity | `nse_com_status` | `nse_com_remarks` | NSE Commodity |
| BSE Commodity | `bse_com_status` | `bse_com_remarks` | BSE Commodity |
| STARMF (Coin/MF) | `starmf_status` | `starmf_remarks` | Coin / Mutual Funds |
| CDSL | `cdsl_status` | `cdsl_remarks` | (internal — demat depository) |
| CKYC | `ckyc_status` | `ckyc_remarks` | (internal — KYC registry) |
| KRA | `kra_status` | `kra_remarks` | (internal — KYC registration) |
| ITD | `itd_status` | `itd_remarks` | (internal — income tax) |
| POA | `poa_status` | `poa_remarks` | (internal — power of attorney) |
| NSE SLB | `nse_slb_status` | `nse_slb_remarks` | Securities Lending and Borrowing (SLB) |
| BSE SLB | `bse_slb_status` | `bse_slb_remarks` | Securities Lending and Borrowing (SLB) |
| ZBL MCX | `zbl_mcx_status` | `zbl_mcx_remark` | Commodity segment — Single Ledger activated |

When checking segment status for a client query, use the relevant status field from this table. When status = Rejected or Activation_rejected, check the corresponding remarks field for the rejection reason.

**Commodity segment cross-check:** When a client queries about commodity trading (MCX, CRUDEOILM, commodity options, or any commodity product), check both `zbl_mcx_status` and `nse_com_status`. Report the status of each segment that is not fully active. Both segments may need to be active depending on the product the client wants to trade.

---

### A5: Account Context Extraction

On every query, call `get_all_client_data` and extract:

| Context | Field(s) |
|---|---|
| Account type | `client_acc_type`, `category` |
| Joint | `primary_dp_joint_account` |
| Minor | `bo_sub_status` contains "Minor" |
| NRI subtype | `bo_sub_status` → NRE ("RepatriableWith") / NRO ("NonRepatriableWith") |
| PIS | `pis_bank_1_name`, `pis_bank_2_name` (value present = PIS) |
| Orbis | `custodial_participant_code` (value present = Orbis) |
| Account status | `status` |
| DDPI/POA | `primary_ddpi_flag`, `poa_consent`, `primary_poa_for_securities` |
| PAN/Name/DOB | `pan`, `client_name`, `dob` |
| Demat status | `primary_dp_status` |
| Third-party demat | `third_party_demat` |

---

### A6: Modification Processes

#### Address Change

**Online:** Eligibility: Aadhaar-linked mobile (see **A3**). Ineligible: joint accounts, mobile not linked to Aadhaar. Process: account.zerodha.com/account. Charges: **A2** standard. Timeline: **A1** general processing. Requirements: Name on Aadhaar must match e-sign name. Minor: minor's Aadhaar for address, guardian's Aadhaar for e-sign.

**Offline:** Documents: modification + KYC forms, self-attested PAN, address proof (see **A3**). Charges: **A2** standard. Timeline: **A1** general processing. Validity: forms valid 30 days from submission. Conditions: signature must match account opening. NRI: notarised address proof. Courier: **A3** address.

#### Contact Details Change

Share this article instead of listing steps: [How to change the registered email ID and mobile number with Zerodha?](https://support.zerodha.com/category/your-zerodha-account/account-modification-and-segment-addition/account-modification/articles/change-contact-details)

**Online:** Platform: Kite app/web. Eligibility: Indian mobile, Aadhaar-linked mobile (see **A3**), IPV, e-sign. Timeline: **A1** contact detail changes (24 working hours). Ineligible: international mobile, non-individual, joint accounts.

**Offline:** Courier to **A3** address. Documents: modification form + IPV. Timeline: **A1** contact detail changes. No charges. Mandatory for non-individual; optional for individual.

**International mobile / NRI:** eSign and attach to ticket, or courier. Include masked Aadhaar if mentioned.

**No access to registered mobile AND email:** Refer to [How do I reset my Zerodha password if I can't access my registered phone number or email?](https://support.zerodha.com/category/your-zerodha-account/your-profile/account/articles/reset-password-new-contact-details)

**Mobile/email already linked to another account:** **ESCALATE** — support manager review needed.

#### DOB / Gender / Marital / Occupation / PEP Update

**Online:** Condition: correct on Aadhaar + ITD. Process: account.zerodha.com/account → ReKYC → Update profile → IPV → e-sign.

**Offline:** Condition: Aadhaar not linked OR joint account. Documents: modification form, self-attested PAN, address proof (see **A3**). Charges: **A2** standard. Timeline: **A1** general processing. Courier: **A3** address.

#### Financial Proof Update

Process: signup.zerodha.com/rekyc. Timeline: **A1** general processing. Acceptable proofs: **A3** income proof. File requirements: **A3** file requirements.

#### Account Deactivation

**Method:** Kill Switch feature.
**Effects:** Trading deactivated, demat frozen. No Kite/Console access. AMC continues. Periodic emails continue.
**Re-enable restriction:** Once disabled via Kill Switch, the segment can only be re-enabled after 12 hours.
**Deactivation:** Online: eSign deactivation form and attach to ticket. Offline: courier deactivation form to **A3** address.
**Reactivation:** Documents: reactivation letter, self-attested PAN, address proof (see **A3**). Timeline: **A1** general processing. Courier: **A3** address.

#### Modification Cancellation

If client requests cancellation of a pending modification (any type) where eSign not yet completed → acknowledge cancellation request → **ESCALATE** — account modification team review needed.

---

### A7: Bank Account Processes

**Limits:** Max 3 accounts: 1 primary (payin + withdrawal) + 2 secondary (payin + withdrawal). All linked bank accounts support both deposits and withdrawals once verified.

**Pending verification:** If a secondary/tertiary bank account is pending penny drop verification, withdrawals to that account will be available once verification completes (typically within 48 working hours of approval). No charges apply for penny drop verification.

**Allowed account types:** Savings, Current, Cash Credit. Overdraft (OD) accounts are not allowed. PayTM Payments Bank cannot be linked.

**Relative's bank account:** Not allowed. SEBI mandates bank in client's name only.

#### Primary Bank Change (Online)

Eligibility: Individual accounts, NRO Non-PIS. Process: Console → Account → Bank → Modify → Details → E-sign. Verification: test transfer. Charges: **A2** standard. Timeline: **A1** general processing.

**Joint bank account:** Primary holder of bank and demat must match. If different: offline with modification form + bank proof (see **A3**).

**Minor accounts:** Online; guardian e-signs. Bank details must be for minor.

#### Secondary Bank Add

Eligibility: Resident individual or non-individual. Process: Console → Account → Bank → Add → Details → OTP → Verify. Timeline: **A1** secondary bank. Withdrawals available once penny drop verification completes.

**Joint account secondary:** If not first holder: attach self-attested bank proof (see **A3**) to ticket.

#### Secondary Bank Change

Process: Console → Account → Bank → Modify → Details → OTP → Verify. Verification: test transfer. Timeline: **A1** secondary bank. No charges.

**If verification fails or joint account:** Attach bank proof (see **A3**) to ticket.

#### Secondary to Primary Conversion

Eligibility: Aadhaar-linked mobile (see **A3**). Process: Console → Account → Bank → Set as primary → E-sign. Timeline: **A1** general processing. Charges: **A2** standard. Effect: current primary becomes secondary. Note: during processing, withdrawals go to old primary.

#### Secondary Bank Remove

Process: Console → Account → Bank → Delete → OTP → Verify. Processing: instant.

#### Current Account Linking

Allowed as primary or secondary. Condition: names match across Zerodha/PAN/bank.
- **Primary:** Documents: modification form, cancelled cheque/statement, banker letter. Charges: **A2** standard. Courier: **A3** address.
- **Secondary:** Update Console, then attach banker letter to ticket.
- **Banker letter requirement:** States account holder solely runs business and makes all transactions.
- Timeline: **A1** secondary bank.

#### Joint Bank Accounts

Allowed if joint holder. Same process as single-holder. Restriction: if linked to multiple Zerodha accounts → UPI/gateway only; IMPS/NEFT/RTGS reversed.

#### Bank Details Update Failure

Causes: incorrect IFSC (O vs 0 confusion), branch/IFSC not recognised by CDSL, "invalid IFSC" error. Resolution: **ESCALATE** — support manager review needed. Do not request bank proof or attempt to resolve IFSC errors directly.

#### Primary Bank Penny Drop Failure

Condition: bank_type = "Primary" AND request_type = "update" AND bank validation failed. Resolution: direct to ReKYC flow at account.zerodha.com. Client uploads bank statement, cheque, or passbook within the ReKYC flow. Do not direct to offline courier process.

#### RTA / Unpaid Dividend — Bank Details Query

When a client asks about unpaid dividends held by an RTA (e.g., KFin Technologies, CAMS) or requests that Zerodha share an updated CML with an RTA:

1. Check `bank_details` in `get_all_client_data` — confirm the bank account is active and the dividend field = YES.
2. **Bank details correct and dividend-enabled:** Respond per A7-RTA-R1.
3. **Bank details missing, incorrect, or dividend ≠ YES:** Guide the client to update bank details per A7 Primary Bank Change process. Confirm that the updated CML will be shared with CDSL after the change is processed.

**A7-RTA-R1 (Response Template):**
"Dividend-related issues typically arise when the bank details registered with the depository do not match what the RTA has on file. We have verified your bank details — they are correctly updated on your account. Zerodha shares updated CML data with CDSL, and CDSL forwards it to RTAs as part of their regular update cycle. The RTA typically receives the update within a few business days. If the dividend is not credited within 10 business days, please follow up with the RTA directly. If your bank details need to be updated, you can do so by following the steps here: [How to change my primary bank account?](https://support.zerodha.com/category/your-zerodha-account/account-modification-and-segment-addition/account-modification/articles/change-primary-bank-account). A charge of ₹25 + GST applies for changing the primary bank account. If your bank details are already correct and the issue persists, please let us know so we can assist further."

---

### A8: Account Closure

**Methods:** Online: resident Indians, NRIs, minors with Kite. Offline: non-individual only.
**Timeline:** **A1** account closure.
**Pre-closure requirements:** Clear negative balance, square off positions, sell/transfer holdings, delete SIPs and mandates, download reports (inaccessible after closure).

**Closure cum transfer:** Transfer holdings to another demat while closing. No additional charges. Refer to [SOP](https://s3.ap-south-1.amazonaws.com/staticassets.zerodha.net/support-portal/2025/06/24/Article/FZUJ7VWF_E6T6ngib3xeSu0JR1750748598.pdf).

**Online process:** Console → Account → Segments → Account closure. Options: sell holdings (Kite redirect) OR transfer holdings (demat in your name only). Accept terms → eSign with Aadhaar.

**Demat closure:** When a trading account is closed, the linked CDSL demat account is also closed as part of the same process. The client does not need to submit a separate demat closure request to CDSL.

**AMC after closure:** Not charged from day closure is processed.

**Post-closure new account error:** If client reports error opening new account after closure → **ESCALATE** — agent review needed.

**Blocked closure causes:** Negative balance, open positions, unlisted securities, pending corporate actions. Cannot reopen same account/user ID after closure.

---

### A9: Demat (DDPI / POA / Secondary Demat)

#### DDPI

Definition: Document allowing broker to debit securities. Benefit: no CDSL TPIN/OTP required for selling. SEBI restriction: debits only for client-placed sell trades. Optional — can use CDSL TPIN instead. Replaced POA (Nov 2022).

**Online activation:** Console → Account → Demat → Enable DDPI → Accept → E-sign with Aadhaar. Minor accounts: guardian's Aadhaar required. Charges: **A2** DDPI activation.

**Offline activation:** Applies to: NRI using Orbis, joint accounts, non-individual. Documents: DDPI form (signature must match account opening). Courier: **A3** address. Charges: **A2** DDPI activation. Requirement: sufficient balance for charge deduction. Timeline: **A1** DDPI offline.

**Status check:** Kite app: User ID → Profile. Kite web: Client ID → My Profile. Alternative: CDSL TPIN if no POA/DDPI.

#### POA/DDPI Revocation

**Online:** Eligibility: individual, Aadhaar-linked mobile (see **A3**). Process: print → fill → sign → scan → eSign → attach to ticket.
**Offline:** Applies to: non-individual, joint, individual with no Aadhaar link. Process: print → fill → courier to **A3** address.
Timeline: **A1** POA/DDPI revocation. Post-revocation: must use CDSL TPIN to sell.

#### Secondary Demat Account

Availability: free, online. Eligibility: Aadhaar-linked mobile (see **A3**), resident individual only. Process: Kite → User ID → Profile → Demat → Secondary → Nominee → IPV → E-sign. Timeline: **A1** secondary demat. Visibility: Console only (not Kite). Closure: offline only.

**Pending eSign troubleshooting:** If the client reports that the eSign link is not appearing or the status shows "pending eSign," advise the client to perform a hard refresh in the browser (Ctrl + Refresh or F5) and retry. If the issue persists after hard refresh, apply Rule 10 troubleshooting steps.

---

### A10: Segments

#### F&O / Currency / Commodity Activation

Prerequisite: equity segment must be active. Demat prerequisite: `primary_dp_status` must be "Active" (see Rule 8).

**Online eligibility:** Aadhaar-linked mobile (see **A3**). Offline only: non-individual accounts.
**Process:** Kite/Console → User ID → Profile → Segments → Activate.
**Required info:** Income range and proof, trading experience, commodity classification (for commodities).
**Timeline:** **A1** F&O activation.
**Income proof:** See **A3**.
**File requirements:** See **A3**.

**Commodity classification:** Farmers/FPO: farmer, cooperatives, FPOs. VCP: processor, commercial user, importer, exporter, trader, stockist, producer, SME/MSME, wholesaler. Others: MCX traders not in above.

**Restrictions:** Sikkim: domicile certificate for commodities. Minors: cannot enable F&O.

**Currency F&O:** RBI declaration form eSign required.

#### F&O / Currency / Commodity Deactivation

**Temporary (Kill Switch):** Disables the segment until the client chooses to re-enable. Ensure no open orders or positions before disabling. Once disabled, the segment can only be re-enabled after 12 hours. Process: Kite/Console → User ID → Profile → Segments → Kill Switch.

**Permanent deactivation:** Requires submission of an account modification form. Applicable to F&O, Currency, and Commodity segments.
Process:
1. Download and fill the [account modification form](https://zerodha-common.s3.ap-south-1.amazonaws.com/Downloads-and-resources/AccountDetailsModificationDeletionForm.pdf) — specify the segment(s) to be permanently deactivated.
2. eSign the form via [Digilocker](https://support.zerodha.com/category/your-zerodha-account/account-modification-and-segment-addition/account-modification/articles/esign-via-digilocker).
3. Submit the eSigned form in the same support ticket.

Timeline: **A1** segment deactivation.
Support article: [How do I deactivate F&O on my account?](https://support.zerodha.com/category/your-zerodha-account/account-modification-and-segment-addition/account-modification/articles/how-do-i-deactivate-f-o-on-my-account)

#### Active Segments Check

Kite app: Client ID → Profile. Kite web: Client ID → Name. Click segment → Console redirect for Kill Switch.

#### Upload Troubleshooting

If client reports error uploading income proof or documents during segment activation → provide troubleshooting steps first: "(1) Clear your browsing history completely. (2) Clear cookies and cache. (3) Try in incognito/private mode. (4) Try on a different device and different network." Do not check or report the segment's internal status when the client's issue is an upload error — troubleshoot the upload first.

---

### A11: Nomination

**Verification:** Console → Account → Nominees | CMR copy.

**Minor nominees:** The minor's PAN is mandatory for the online nomination process. If the minor does not have a PAN, the offline process must be used. Refer to: [How to add a nominee(s) to the Zerodha account offline?](https://support.zerodha.com/category/your-zerodha-account/nomination-process/articles/update-modify-nominee-details)

**Modification online:** Modify name, DOB, address (with nominee ID proof — Aadhaar or Driving Licence), relationship, email, mobile. Process: download + print nominee form (PDF) + account modification form (PDF) → wet sign both → eSign both → attach to ticket. Charges: **A2** standard.

**Modification offline:** Delete/opt-out of nominee only. Forms: account modification form + annexure 1B → sign → courier to **A3** address.

**Online cannot do:** Delete or opt out of nominee.

**Nominee modifications are handled through the nominee process only** — direct to: [How to update or modify nominee details in Zerodha?](https://support.zerodha.com/category/your-zerodha-account/nomination-process/articles/update-modify-nominee-details)

**Joint accounts:** Offline only.

**Charges:** **A2** standard.

**Demat-mode MF nominee sync (Coin holdings)**

For mutual funds held in Demat mode through Coin, the nominee registered in the Demat account (with CDSL) applies automatically. RTAs such as Kfintech may show "Nominee Not Registered" in the CAS due to a synchronisation delay between CDSL and the RTA — this does not indicate the nominee is absent.

To handle this query: pull nominee_details from get_all_client_data. If any of nominee_1_first_name, nominee_2_first_name, or nominee_3_first_name is populated, the nominee is confirmed. Share the response below and direct the client to verify at Console → Account → Nominees. If none of the nominee name fields are populated, guide the client to add a nominee: How to add a nominee online in Zerodha?

Response: "The nominee details added to your Zerodha Demat account are applicable to all Demat holdings, including mutual funds held through Coin. If you hold mutual funds outside of Zerodha or in non-Demat form, please get in touch with the respective AMC for nomination updates. You can verify your Zerodha nominee details at console.zerodha.com/account/nominee."

**Inactivity alert:** No trading for 24 months → deactivated/dormant. If not reactivated within 30 days → nominee notified.

Support article: [How to update or modify nominee details in Zerodha?](https://support.zerodha.com/category/your-zerodha-account/nomination-process/articles/update-modify-nominee-details)

---

### A12: KYC & Reactivation

#### ReKYC Process Details

**Aadhaar OTP requirement:** Aadhaar OTP is required during ReKYC only when the client selects "Update as per Aadhaar" (i.e., updating their address). If the client is completing ReKYC without an address change, only eSign is required — no Aadhaar OTP is needed.

**Support article:** [How to re-activate a dormant/inactive Zerodha account?](https://support.zerodha.com/category/your-zerodha-account/your-profile/kyc-re-activation/articles/re-activate-my-account)

#### Deactivated Account Reactivation

Applies to voluntarily deactivated accounts only. Dormant accounts: complete Re-KYC instead.

**Online:** Eligibility: Aadhaar-linked mobile (see **A3**). Method: attach eSigned reactivation letter to ticket.
**Offline:** Documents: signed reactivation letter, self-attested PAN, address proof (see **A3**). Courier: **A3** address.
Timeline: **A1** deactivated reactivation.
Result: same client ID, new password.
Demat closed: submit demat application. Account closed: complete new account opening.

#### Additional Documents / Rejection Reasons

Reason: SEBI requires valid, current documents.

**Father/spouse name mismatch during ReKYC:** Client cannot skip this field. Must follow offline process — refer to [How to change the name in my Zerodha account?](https://support.zerodha.com/category/your-zerodha-account/your-profile/general-profile-questions/articles/why-is-the-name-on-my-zerodha-account-different-than-on-the-documents-i-ve-submitted). Courier completed forms + self-attested PAN + address proof (see **A3**) to **A3** address. Do not reference Console for form downloads.

**Rejection reasons and resolution:**

| Rejection | Resolution |
|---|---|
| PAN not clear | Attach clear self-attested PAN |
| Minor PAN | Attach major PAN |
| Father name mismatch | Offline process — see above |
| Signature not clear | Attach clear self-attested signature |
| Name confirmation | Attach government ID proof |
| Proprietor bank | Attach banker letter |
| Invalid bank proof | Update correct bank details on Console |
| Bank not in name | Attach self-attested bank proof to ticket or update Console |
| Invalid IPV | Complete Re-KYC |
| 3rd party Aadhaar | The eSign was completed using a different Aadhaar, or there is a name mismatch between Aadhaar and Demat account. Retry using own Aadhaar with matching name. If names do not match, use the offline process: download the account modification form, attach bank proof (per **A3**), and courier to **A3** address. See **A7** Primary Bank Change for the offline alternative. |

---

### A13: Utilities

**Password removal from PDF:** Open PDF → Menu → Print → Print to PDF → Save.

**eSign documents:** Platform: digilocker.gov.in. Requires: Aadhaar-linked mobile (see **A3**). Cost: free. Steps: Login → Drive → Documents → Upload → Sign → Enter Aadhaar → OTP → Download.

**Trade alerts not received:** Cause: incorrect contact details. Resolution: update contact online or offline. If contact correct but no alerts → contact exchanges directly: NSE (nseindia.com/contact/corporate-office), BSE (bseindia.com/static/about/contact_us.aspx), MCX (mcxindia.com/contact-us/department-contacts). Note: DND may block alerts.

---

**Escalation behavior:** When any rule in this protocol says **ESCALATE**, do not draft a customer-facing response. Instead, output only: **HUMAN AGENT ACTION REQUIRED** — followed by the reason from the rule. The human agent will handle the query manually.

--

## Section B: Decision Flow

On every account modification query, execute in order:

```
1. PREFLIGHT
   ├─ Call get_all_client_data → extract context per A5
   ├─ If account_blocks non-empty → STOP. **ESCALATE** — support manager review needed.
   │   Do not share block reason or raw field values with client.
   ├─ If third_party_demat = true → STOP. **ESCALATE** — third-party demat mapped;
   │   support manager review needed. Do not proceed with any standard guidance.
   ├─ If nse_eq_status OR bse_eq_status = "Dormant" → Rule 6 (Dormancy)
   └─ Check account_modification_report for existing requests

2. ROUTE by query type
   ├─ Name / DOB / PAN update → Rule 1 (Escalate)
   ├─ Modification status inquiry → Rule 2
   ├─ ReKYC query → Rule 3
   ├─ Account closure → Rule 4
   ├─ Segment activation → Rule 5 (check demat prerequisite Rule 8 first)
   ├─ Segment deactivation (disable / deactivate F&O, Currency, or Commodity) → Rule 12
   ├─ Dormant account → Rule 6
   ├─ Segment status issue → Rule 7
   ├─ Segment rejected (PAN failure) → Rule 7.1
   ├─ Demat prerequisite check → Rule 8
   ├─ Nominee rejection → Rule 9
   ├─ Console/Kite UI error during activation → Rule 10
   ├─ Pledging / collateral margin query → Rule 11
   ├─ Bank account queries → refer to A7
   ├─ DDPI / POA queries → refer to A9
   ├─ Nomination queries → refer to A11
   ├─ KYC / reactivation → refer to A12
   └─ Closure-related escalations (secondary demat, employer policy,
       IL&FS, closure cum transfer) → Rule 4 escalation

3. SCOPE
   Only address what the customer asked. Do not volunteer information
   about unrelated topics unless directly relevant to the issue.
```

---

## Section C: Rules

---

### Rule 1: Name / DOB / PAN Updates

If query mentions name change, DOB mismatch, or PAN correction → **ESCALATE** — support manager review needed.

---

### Rule 2: Modification Status

**Check request:** For segment activation → query `form_type` IN (`rekyc`, `rekyc_fno`, `segment_addition`), most recent within 3 months. For Coin/MF → query `form_type` = `rekyc`, most recent within 3 months. If no request found OR last request > 3 months → "Your last request from [date] is closed. Submit a new request at account.zerodha.com/account."

**Multi-row processing:** When the query returns multiple rows (e.g., both `rekyc` and `rekyc_fno` from the same submission), evaluate each row's status independently. A single ReKYC submission can result in equity segments approved while F&O segments are rejected. Match the row to the client's query — if the client is asking about F&O/currency/commodity, check the `rekyc_fno` row specifically. Report only the status relevant to what the client asked.

**Silent segment check:** Before responding to any segment activation query, check actual segment status fields in `get_all_client_data` using the field pairs in **A4**. Use this only to detect problems (rejections, PAN failures, dormancy). If segment shows Rejected, Activation_rejected, or Deactivated → check the corresponding remarks field (per **A4**) and apply Rule 7.1 before giving any other response.

**Status responses:**

| Status | Response |
|---|---|
| Request_pending / Processing | "Your [modification_type] request was received on [submission_date]. It will be processed within [relevant timeline from **A1**]. You will receive an email confirmation once complete." |
| Pending_eSign | "[modification_type] is pending eSign — complete on Console to proceed." |
| Approved | Verify submission_date is at least [relevant timeline] before current date. "[modification_type] approved on [date]; active within [timeline from **A1**]." |
| Rejected | Check all relevant form_types (`rekyc`, `rekyc_fno`, `segment_addition`) when looking for rejections. "[modification_type] rejected: [rejection_reason]. Resolve and resubmit." |

Read the exact value of the status field. Cross-check against submission date — a request submitted today or recently is almost certainly not yet Approved.

---

### Rule 3: ReKYC

**Before giving any ReKYC guidance:** Check `account_modification_report` for an existing ReKYC request (`form_type` IN (`rekyc`, `rekyc_fno`)) within the last 3 months.

- **Found → apply Rule 2** status response for that request first.
- **Rejected with "Invalid IPV"** → ask client to complete ReKYC again at account.zerodha.com/account.
- **Rejected with any other reason** → inform client of the specific rejection reason and **ESCALATE** — KYC team review needed.
- **Not found OR > 3 months** → proceed with standard ReKYC guidance:

Visit account.zerodha.com/account → complete ReKYC with Aadhaar eSign. Requires: Aadhaar-linked mobile (see **A3**). For detailed steps, refer to: [How to re-activate a dormant/inactive Zerodha account?](https://support.zerodha.com/category/your-zerodha-account/your-profile/kyc-re-activation/articles/re-activate-my-account). Aadhaar OTP is required only if updating address (per **A12**).

**Charges:** **A2** standard — applicable only if client selects "Update as per Aadhaar" during ReKYC. Mention charges only if this option is selected.

---

### Rule 4: Account Closure

**Escalation triggers:** If query mentions "secondary demat" / "employer policy" / "employer restriction" / "empanelment" / "company policy" / "IL&FS" / "ILFS" / "closure cum transfer" → **ESCALATE** — relevant team review needed. Note: accounts with a third-party demat are caught earlier at preflight (`third_party_demat = true`) and escalated before reaching this rule.

**Before responding:** Check `account_modification_report` for an existing account closure request. If a closure request is already in progress → confirm its status to the client using the status table below. Do not offer retention or Kill Switch if a closure request has already been submitted.

| Status | Response |
|---|---|
| blank / Request_pending / Processing | Express regret; offer Kill Switch alternative; invite feedback call |
| Pending_eSign | Complete eSign on Console to proceed; invite feedback call |
| Rejected | State rejection reason; invite feedback call |
| Approved | Completed within **A1** account closure timeline; invite feedback call |
| No match | **ESCALATE** — support manager review needed |

**Post-closure new account error:** **ESCALATE** — agent review needed.

---

### Rule 5: Segment Activation Queries

1. Check demat prerequisite first (Rule 8).
2. Check `account_modification_report` for existing requests: query `form_type` IN (`rekyc`, `rekyc_fno`, `segment_addition`), most recent within 3 months. If multiple rows exist, match each row to the segment the client is asking about — evaluate independently per Rule 2 multi-row processing. If a request exists (`rekyc`, `rekyc_fno`, or `segment_addition`):
   - **In progress or approved:** If `form_type = rekyc_fno`, F&O/currency/commodity activation is already included in the ReKYC request — do not advise a separate activation request. Confirm that the existing request covers F&O and provide the processing timeline per **A1**.
   - **Rejected:** Surface the rejection reason first (per Rule 2) before providing any new activation guidance.
3. If no existing request → guide per **A10** based on account type.
4. Both trading and demat accounts must be active for any segment activation (Rule 8).

---

### Rule 6: Dormancy

Triggered when `nse_eq_status` OR `bse_eq_status` = "Dormant":

1. **Identify which segments are dormant.** Check equity segment status (`nse_eq_status`, `bse_eq_status`) and F&O/commodity segment status (per **A4** field pairs) separately.
   - If equity segments are dormant → proceed to step 2 (ReKYC path).
   - If equity segments are already active and only F&O/commodity segments are dormant → check `account_modification_report` for `form_type` IN (`rekyc_fno`, `segment_addition`) first. If not found, also check `form_type` = `rekyc`. Evaluate each row independently and match to the segment the client is asking about (per Rule 2 multi-row processing). If a rejected request exists for the relevant segment, surface the rejection reason per Rule 2 before providing new activation guidance. If no existing request → guide to segment activation per Rule 5.
2. **For dormant equity:** "Your account is inactive due to inactivity; trading requires ReKYC." Check `account_modification_report` for existing ReKYC request (`form_type` IN (`rekyc`, `rekyc_fno`)):
   - Found + in progress (Request_pending / Processing / Reactivation_pending) → "ReKYC received and being processed; account reactivated within 24–48 working hours."
   - Found + Rejected → surface the rejection reason first (per Rule 2). Inform the client of the specific reason before advising resubmission.
   - Not found OR > 3 months → "Complete ReKYC at account.zerodha.com/account." Share the support article: [How to re-activate a dormant/inactive Zerodha account?](https://support.zerodha.com/category/your-zerodha-account/your-profile/kyc-re-activation/articles/re-activate-my-account). Aadhaar OTP is required only if updating address (per **A12**).
3. After equity reactivation, dormant F&O/commodity segments → guide to Console → Account → Segment Activation. **Coin/MF:** ReKYC automatically re-enables Coin — no separate Coin activation request needed. Cross-check `get_all_client_data` for Coin segment status to confirm.
4. Mention dormancy date/year only if asked.
5. Use "dormant" once in the response — do not repeat.

---

### Rule 7: Segment & Account Status Translations

| Raw Status | Response |
|---|---|
| `Reactivation_pending` | Check timestamp against current time. Within 24 working hours → "[segment/account] being processed; active within 24 working hours of submission." 24 working hours elapsed → **ESCALATE** — support manager review needed. |
| `Request_pending` | Same as Reactivation_pending. Cross-check: ReKYC → verify rekyc or rekyc_fno form status; segment → verify segment_addition form status (Rule 2). |
| `Blocked` | Rewrite `remarks` field conversationally. This is the only status where remarks content is rewritten for the client. |
| `Activated` | Confirm "[segment] is active." If client reports inability to place orders or shows 0 available funds → check activation timestamp. Calculate: activation time + 24 hours. If that time is still in the future → "Your [segment] was activated on [activation date]. You will be able to place orders from [specific date: activation + 24 hours]." If 24 hours have already passed → **ESCALATE** — support manager review needed. Always give the specific date, not a generic window. |
| Coin segment = `Generated` | **ESCALATE** — support manager review needed. Cannot be self-resolved. |
| `Dormant` | Apply Rule 6. |
| `Activation_rejected` | Treat as Rejected. Check the corresponding remarks field (per **A4**). Apply Rule 7.1 if remarks contain "PAN Verification Failed." For other rejection reasons, inform client of the specific reason and guide to resubmission. |

---

### Rule 7.1: Segment Rejection — PAN Verification

If any segment (per **A4** field pairs) shows as Rejected, Activation_rejected, or Deactivated AND the corresponding remarks field contains "PAN Verification Failed":

1. Call `pan_status` tool to retrieve the specific rejection reason.
2. If `pan_status` returns a specific, actionable mismatch → follow the pan_status tool's resolution guidance for that mismatch.
3. For all other `pan_status` results (no issues found, ambiguous, or unclear) → **ESCALATE** — support manager review needed for UCC process team investigation. Redoing the process will not resolve the issue when no mismatch exists.
4. Do not guess the rejection reason from `get_all_client_data` alone.

---

### Rule 8: Demat Prerequisite for Segment Activation

If any segment activation query (F&O, Currency, MCX/Commodity) → check `primary_dp_status` from `get_all_client_data`.

If `primary_dp_status` ≠ "Active":
"To activate any segment, both trading and demat accounts must be active. You can open a demat account linked to your existing trading account by following the steps here: [Can I open a demat account if I already have a trading or commodity account?](https://support.zerodha.com/category/your-zerodha-account/account-opening/online-account-opening/articles/open-demat-with-existing-trading-commodity). Once your demat account is active, you can enable segments under the single ledger facility: [What is the single ledger facility?](https://support.zerodha.com/category/your-zerodha-account/account-opening/online-account-opening/articles/what-is-the-single-ledger-facility)."

If the system blocks activation, there is always a reason — investigate before responding.

---

### Rule 9: Nominee Request Rejection

Nominee modifications are handled through the nominee process only — direct to **A11** support article.

If query mentions nominee modification/request AND customer reports rejection:

1. Check `account_modification` form where `form_type` = "nominee_addition".
2. Status = Rejected → "Your nominee request was rejected: [rejection_reason]. Our team will investigate this and get back to you shortly." **ESCALATE** — account modification team review needed with the rejection reason.
3. Status ≠ Rejected → proceed with Rule 2 status response.

---

### Rule 10: Console/Kite UI Error During Segment Activation

If client reports a UI or interface error (e.g., "Service unavailable", "Unknown exchange segment", page not loading, repeated errors) during the activation flow (not during order placement):

Provide troubleshooting steps first: "(1) Clear your browsing history completely. (2) Clear cookies and cache. (3) Try in incognito/private mode. (4) Try on a different device and different network."

Do not provide full activation steps or income proof guidance until the client confirms they can access the activation form.

---

### Rule 11: Pledging / Collateral Margin Queries

If the client is unable to pledge or has a query about pledging holdings for collateral margin:

1. Check `nse_fo_status` (per **A4**). Pledging for margin purposes requires an active F&O segment.
2. If `nse_fo_status` = "Activated" but the client is still unable to pledge → share troubleshooting guidance: [Why am I unable to pledge?](https://support.zerodha.com/category/console/portfolio/pledging/articles/unable-to-pledge)
3. If `nse_fo_status` ≠ "Activated" → guide client to activate F&O first per Rule 5.

---

### Rule 12: Segment Deactivation

If the client wants to disable or deactivate an F&O, Currency, or Commodity segment:

1. **Determine intent — temporary or permanent.** If the client says "disable," "turn off," or "pause" without specifying permanence → present both options per **A10** Segment Deactivation. If the client explicitly says "permanently deactivate" or "remove segment" → guide directly to the permanent deactivation process.
2. **Temporary (Kill Switch):** Ensure no open orders or positions before disabling. Guide per **A10** Kill Switch process. Mention the 12-hour re-enable restriction.
3. **Permanent deactivation:** Guide per **A10** permanent deactivation process — download the account modification form, specify the segment(s) to be permanently deactivated, eSign via Digilocker, and submit the eSigned form in the same support ticket. Share the support article: [How do I deactivate F&O on my account?](https://support.zerodha.com/category/your-zerodha-account/account-modification-and-segment-addition/account-modification/articles/how-do-i-deactivate-f-o-on-my-account)
4. **Equity segment deactivation:** Equity segments cannot be individually deactivated. If the client wants to deactivate all trading → refer to **A6** Account Deactivation (Kill Switch for entire account) or **A8** Account Closure.
