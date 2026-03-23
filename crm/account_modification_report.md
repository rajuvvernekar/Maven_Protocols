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

TRIGGER KEYWORDS: "activate", "segment activation", "Coin", "bank account", "change bank", "modify bank", "DDPI", "MTF", "margin", "address update", "Aadhar", "status of request", "DOB", "date of birth", "gender", "marital status", "occupation", "PEP", "politically exposed", "nominee", "add nominee", "change nominee", "update nominee", "remove nominee", "nominee details", "nominee percentage", "nominee address", "mobile number", "change mobile", "update mobile", "unable to change mobile", "already registered mobile", "email", "change email", "update email", "email address", "email-id", "income proof", "income details", "update income", "secondary demat", "secondary account", "open secondary demat", "secondary account opening", "secondary account rejected", "secondary account status", "secondary account on hold", "contact details", "CERSAI", "close account", "close demat", "account closure", "close trading account", "deactivate account", "submit account closure", "cancel closure request", "closure request submitted by mistake", "open positions", "account closure status", "closure process", "invalid IFSC", "IFSC code error", "IFSC not working", "wrong IFSC"

## Protocol

# ACCOUNT MODIFICATION PROTOCOL

---

## Section A: Reference Data

All rules reference these blocks as single sources of truth.

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

---

### A2: Charges

| Action | Charge |
|---|---|
| Standard modification | ₹25 + 18% GST |
| DDPI offline activation | ₹100 + 18% GST |
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
`form_type`, `description`, `client_id`, `bank_name`, `account_number`, `request_type`, `income_proof`, `new_email`, `new_mobile`, `signer_name`, `notary_id`, `bank_order`, `kyc_field_type`, `STARMF`, `primary_ddpi_flag`, `primary_ddpi_agreement_date`, `poa_consent`, `primary_poa_for_securities`, `primary_dp_status`, raw segment identifiers (e.g. `NSE_COM`, `NSE_FO`, `BSE_EQ`, `MCX_FO`), raw status values

**Client-friendly translations:**
- `form_type` values → "segment activation" / "bank modification" / "ReKYC" / "primary bank" / "secondary bank"
- STARMF → "Your mutual funds are now active and you can start investing on Coin"
- NSE_COM → "NSE Commodity"
- `primary_ddpi_flag` active → "DDPI is active"
- Segment `remarks` field → rewrite conversationally. The only exception: `Blocked` status — rewrite `remarks` conversationally for that status only. For all other statuses, use only: "[Segment name] is not currently active on your account."

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

**No access to registered mobile AND email:** Refer to [How do I reset my Zerodha password if I can't access my registered phone number or email?](https://support.zerodha.com/category/console/profile/account/articles/reset-password-new-contact-details)

**Mobile/email already linked to another account:** Escalate to support manager.

#### DOB / Gender / Marital / Occupation / PEP Update

**Online:** Condition: correct on Aadhaar + ITD. Process: account.zerodha.com/account → ReKYC → Update profile → IPV → e-sign.

**Offline:** Condition: Aadhaar not linked OR joint account. Documents: modification form, self-attested PAN, address proof (see **A3**). Charges: **A2** standard. Timeline: **A1** general processing. Courier: **A3** address.

#### Financial Proof Update

Process: signup.zerodha.com/rekyc. Timeline: **A1** general processing. Acceptable proofs: **A3** income proof. File requirements: **A3** file requirements.

#### Account Deactivation

**Method:** Kill Switch feature.
**Effects:** Trading deactivated, demat frozen. No Kite/Console access. AMC continues. Periodic emails continue.
**Deactivation:** Online: eSign deactivation form and attach to ticket. Offline: courier deactivation form to **A3** address.
**Reactivation:** Documents: reactivation letter, self-attested PAN, address proof (see **A3**). Timeline: **A1** general processing. Courier: **A3** address.

#### Modification Cancellation

If client requests cancellation of a pending modification (any type) where eSign not yet completed → acknowledge cancellation request → escalate to account modification team.

---

### A7: Bank Account Processes

**Limits:** Max 3 accounts: 1 primary (payin + withdrawal) + 2 secondary (payin only).

**Allowed account types:** Savings, Current, Cash Credit. Overdraft (OD) accounts are not allowed. PayTM Payments Bank cannot be linked.

**Relative's bank account:** Not allowed. SEBI mandates bank in client's name only.

#### Primary Bank Change (Online)

Eligibility: Individual accounts, NRO Non-PIS. Process: Console → Account → Bank → Modify → Details → E-sign. Verification: test transfer. Charges: **A2** standard. Timeline: **A1** general processing.

**Joint bank account:** Primary holder of bank and demat must match. If different: offline with modification form + bank proof (see **A3**).

**Minor accounts:** Online; guardian e-signs. Bank details must be for minor.

#### Secondary Bank Add

Eligibility: Resident individual or non-individual. Process: Console → Account → Bank → Add → Details → OTP → Verify. Timeline: **A1** secondary bank. Note: deposits only, no withdrawals.

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

Causes: incorrect IFSC (O vs 0 confusion), branch/IFSC not recognised by CDSL, "invalid IFSC" error. Resolution: escalate to support manager. Do not request bank proof or attempt to resolve IFSC errors directly.

#### Primary Bank Penny Drop Failure

Condition: bank_type = "Primary" AND request_type = "update" AND bank validation failed. Resolution: direct to ReKYC flow at account.zerodha.com. Client uploads bank statement, cheque, or passbook within the ReKYC flow. Do not direct to offline courier process.

---

### A8: Account Closure

**Methods:** Online: resident Indians, NRIs, minors with Kite. Offline: non-individual only.
**Timeline:** **A1** account closure.
**Pre-closure requirements:** Clear negative balance, square off positions, sell/transfer holdings, delete SIPs and mandates, download reports (inaccessible after closure).

**Closure cum transfer:** Transfer holdings to another demat while closing. No additional charges. Refer to [SOP](https://s3.ap-south-1.amazonaws.com/staticassets.zerodha.net/support-portal/2025/06/24/Article/FZUJ7VWF_E6T6ngib3xeSu0JR1750748598.pdf).

**Online process:** Console → Account → Segments → Account closure. Options: sell holdings (Kite redirect) OR transfer holdings (demat in your name only). Accept terms → eSign with Aadhaar.

**AMC after closure:** Not charged from day closure is processed.

**Post-closure new account error:** If client reports error opening new account after closure → escalate to agent.

**Blocked closure causes:** Negative balance, open positions, unlisted securities, pending corporate actions. Cannot reopen same account/user ID after closure.

---

### A9: Demat (DDPI / POA / Secondary Demat)

#### DDPI

Definition: Document allowing broker to debit securities. Benefit: no CDSL TPIN/OTP required for selling. SEBI restriction: debits only for client-placed sell trades. Optional — can use CDSL TPIN instead. Replaced POA (Nov 2022).

**Online activation:** Console → Account → Demat → Enable DDPI → Accept → E-sign with Aadhaar. Minor accounts: guardian's Aadhaar required.

**Offline activation:** Applies to: NRI using Orbis, joint accounts, non-individual. Documents: DDPI form (signature must match account opening). Courier: **A3** address. Charges: **A2** DDPI offline. Requirement: sufficient balance for charge deduction. Timeline: **A1** DDPI offline.

**Status check:** Kite app: User ID → Profile. Kite web: Client ID → My Profile. Alternative: CDSL TPIN if no POA/DDPI.

#### POA/DDPI Revocation

**Online:** Eligibility: individual, Aadhaar-linked mobile (see **A3**). Process: print → fill → sign → scan → eSign → attach to ticket.
**Offline:** Applies to: non-individual, joint, individual with no Aadhaar link. Process: print → fill → courier to **A3** address.
Timeline: **A1** POA/DDPI revocation. Post-revocation: must use CDSL TPIN to sell.

#### Secondary Demat Account

Availability: free, online. Eligibility: Aadhaar-linked mobile (see **A3**), resident individual only. Process: Kite → User ID → Profile → Demat → Secondary → Nominee → IPV → E-sign. Timeline: **A1** secondary demat. Visibility: Console only (not Kite). Closure: offline only.

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

#### Active Segments Check

Kite app: Client ID → Profile. Kite web: Client ID → Name. Click segment → Console redirect for Kill Switch.

#### Upload Troubleshooting

If client reports error uploading income proof or documents during segment activation → provide troubleshooting steps first: "(1) Clear your browsing history completely. (2) Clear cookies and cache. (3) Try in incognito/private mode. (4) Try on a different device and different network." Do not check or report the segment's internal status when the client's issue is an upload error — troubleshoot the upload first.

---

### A11: Nomination

**Verification:** Console → Account → Nominees | CMR copy.

**Modification online:** Modify name, DOB, address (with nominee ID proof — Aadhaar or Driving Licence), relationship, email, mobile. Process: download + print nominee form (PDF) + account modification form (PDF) → wet sign both → eSign both → attach to ticket. Charges: **A2** standard.

**Modification offline:** Delete/opt-out of nominee only. Forms: account modification form + annexure 1B → sign → courier to **A3** address.

**Online cannot do:** Delete or opt out of nominee.

**Nominee modifications are handled through the nominee process only** — direct to: [How to update or modify nominee details in Zerodha?](https://support.zerodha.com/category/your-zerodha-account/nomination-process/articles/update-modify-nominee-details)

**Joint accounts:** Offline only.

**Charges:** **A2** standard.

**Inactivity alert:** No trading for 24 months → deactivated/dormant. If not reactivated within 30 days → nominee notified.

Support article: [How to update or modify nominee details in Zerodha?](https://support.zerodha.com/category/your-zerodha-account/nomination-process/articles/update-modify-nominee-details)

---

### A12: KYC & Reactivation

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

---

### A13: Utilities

**Password removal from PDF:** Open PDF → Menu → Print → Print to PDF → Save.

**eSign documents:** Platform: digilocker.gov.in. Requires: Aadhaar-linked mobile (see **A3**). Cost: free. Steps: Login → Drive → Documents → Upload → Sign → Enter Aadhaar → OTP → Download.

**Trade alerts not received:** Cause: incorrect contact details. Resolution: update contact online or offline. If contact correct but no alerts → contact exchanges directly: NSE (nseindia.com/contact/corporate-office), BSE (bseindia.com/static/about/contact_us.aspx), MCX (mcxindia.com/contact-us/department-contacts). Note: DND may block alerts.

---

## Section B: Decision Flow

On every account modification query, execute in order:

```
1. PREFLIGHT
   ├─ Call get_all_client_data → extract context per A5
   ├─ If account_blocks non-empty → STOP. Escalate to support manager.
   │   Do not share block reason or raw field values with client.
   ├─ If nse_eq_status OR bse_eq_status = "Dormant" → Rule 6 (Dormancy)
   └─ Check account_modification_report for existing requests

2. ROUTE by query type
   ├─ Name / DOB / PAN update → Rule 1 (Escalate)
   ├─ Modification status inquiry → Rule 2
   ├─ ReKYC query → Rule 3
   ├─ Account closure → Rule 4
   ├─ Segment activation → Rule 5 (check demat prerequisite Rule 8 first)
   ├─ Dormant account → Rule 6
   ├─ Segment status issue → Rule 7
   ├─ Segment rejected (PAN failure) → Rule 7.1
   ├─ Demat prerequisite check → Rule 8
   ├─ Nominee rejection → Rule 9
   ├─ Console/Kite UI error during activation → Rule 10
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

Rules reference Section A blocks. They do not redefine what is already defined there.

---

### Rule 1: Name / DOB / PAN Updates

If query mentions name change, DOB mismatch, or PAN correction → escalate to support manager.

---

### Rule 2: Modification Status

**Check request:** For segment activation → query form_type IN (rekyc, segment_addition), most recent within 3 months. For Coin/MF → query form_type = rekyc, most recent within 3 months. If no request found OR last request > 3 months → "Your last request from [date] is closed. Submit a new request at account.zerodha.com/account."

**Silent segment check:** Before responding to any segment activation query, check actual segment status fields in `get_all_client_data` (e.g. `nse_eq_status`, `bse_eq_status`, `mcx_status`). Use this only to detect problems (rejections, PAN failures, dormancy). If segment shows Rejected or Deactivated → apply Rule 7.1 before giving any other response.

**Status responses:**

| Status | Response |
|---|---|
| Request_pending / Processing | "Your [modification_type] request was received on [submission_date]. It will be processed within [relevant timeline from **A1**]. You will receive an email confirmation once complete." |
| Pending_eSign | "[modification_type] is pending eSign — complete on Console to proceed." |
| Approved | Verify submission_date is at least [relevant timeline] before current date. "[modification_type] approved on [date]; active within [timeline from **A1**]." |
| Rejected | "[modification_type] rejected: [rejection_reason]. Resolve and resubmit." |

Read the exact value of the status field. Cross-check against submission date — a request submitted today or recently is almost certainly not yet Approved.

---

### Rule 3: ReKYC

**Before giving any ReKYC guidance:** Check `account_modification_report` for an existing ReKYC request (`form_type = rekyc`) within the last 3 months.

- **Found → apply Rule 2** status response for that request first.
- **Rejected with "Invalid IPV"** → ask client to complete ReKYC again at account.zerodha.com/account.
- **Rejected with any other reason** → inform client of rejection reason and escalate to KYC team. Do not direct to self-service resubmission.
- **Not found OR > 3 months** → proceed with standard ReKYC guidance:

Visit account.zerodha.com/account → complete ReKYC with Aadhaar eSign. Requires: Aadhaar-linked mobile (see **A3**).

**Charges:** **A2** standard — applicable only if client selects "Update as per Aadhaar" during ReKYC. Mention charges only if this option is selected.

---

### Rule 4: Account Closure

**Escalation triggers:** If query mentions "secondary demat" / "employer policy" / "employer restriction" / "empanelment" / "company policy" / "IL&FS" / "ILFS" / "closure cum transfer" → escalate to relevant team.

| Status | Response |
|---|---|
| blank / Request_pending / Processing | Express regret; offer Kill Switch alternative; invite feedback call |
| Pending_eSign | Complete eSign on Console to proceed; invite feedback call |
| Rejected | State rejection reason; invite feedback call |
| Approved | Completed within **A1** account closure timeline; invite feedback call |
| No match | Escalate to support manager |

**Post-closure new account error:** Escalate to agent.

---

### Rule 5: Segment Activation Queries

1. Check demat prerequisite first (Rule 8).
2. Check for existing request via Rule 2.
3. If no existing request → guide per **A10** based on account type.
4. All segment activations (F&O, Currency, MCX/Commodity) require both trading AND demat accounts to be active.

---

### Rule 6: Dormancy

Triggered when `nse_eq_status` OR `bse_eq_status` = "Dormant":

1. "Your account is inactive due to inactivity; trading requires ReKYC."
2. Check `get_all_client_data` for existing ReKYC request:
   - Found + in progress (Request_pending / Processing / Reactivation_pending) → "ReKYC received and being processed; account reactivated within 24–48 working hours."
   - Not found OR > 3 months → "Complete ReKYC at account.zerodha.com/account."
3. Dormant F&O/commodity segments → after equity reactivation, guide to Console → Account → Segment Activation. **Coin/MF:** ReKYC automatically re-enables Coin — no separate Coin activation request needed. Cross-check `get_all_client_data` for Coin segment status to confirm.
4. Mention dormancy date/year only if asked.
5. Use "dormant" once in the response — do not repeat.

---

### Rule 7: Segment & Account Status Translations

| Raw Status | Response |
|---|---|
| `Reactivation_pending` | Check timestamp against current time. Within 24 working hours → "[segment/account] being processed; active within 24 working hours of submission." 24 working hours elapsed → escalate to support manager. |
| `Request_pending` | Same as Reactivation_pending. Cross-check: ReKYC → verify rekyc form status; segment → verify segment_addition form status (Rule 2). |
| `Blocked` | Rewrite `remarks` field conversationally. This is the only status where remarks content is rewritten for the client. |
| `Activated` | Confirm "[segment] is active." If client reports inability to place orders or shows 0 available funds → check activation timestamp. Calculate: activation time + 24 hours. If that time is still in the future → "Your [segment] was activated on [activation date]. You will be able to place orders from [specific date: activation + 24 hours]." If 24 hours have already passed → escalate to support manager. Always give the specific date, not a generic window. |
| Coin segment = `Generated` | Escalate to support manager. Cannot be self-resolved. |
| `Dormant` | Apply Rule 6. |

---

### Rule 7.1: Segment Rejection — PAN Verification

If any segment (`nse_eq_status`, `bse_eq_status`, `mcx_status`, etc.) shows as Rejected or Deactivated AND remarks contain "PAN Verification Failed":

1. Call `pan_status` tool to retrieve the specific rejection reason.
2. Respond based on the `pan_status` result — follow the pan_status tool's protocol for resolution guidance.
3. Do not guess the rejection reason from `get_all_client_data` alone.

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
2. Status = Rejected → "Your nominee request was rejected: [rejection_reason]. Our team will investigate this and get back to you shortly." Escalate to account modification team with the rejection reason.
3. Status ≠ Rejected → proceed with Rule 2 status response.

---

### Rule 10: Console/Kite UI Error During Segment Activation

If client reports a UI or interface error (e.g., "Service unavailable", "Unknown exchange segment", page not loading, repeated errors) during the activation flow (not during order placement):

Provide troubleshooting steps first: "(1) Clear your browsing history completely. (2) Clear cookies and cache. (3) Try in incognito/private mode. (4) Try on a different device and different network."

Do not provide full activation steps or income proof guidance until the client confirms they can access the activation form.

---

## Section D: General Notes

- ReKYC reactivates dormant accounts and previously held segments. ReKYC also automatically re-enables Coin/MF.
- Active accounts add new segments without ReKYC.
- DDPI replaced POA (Nov 2022); optional — CDSL TPIN usable instead.
- Secondary demat: resident individuals only, free.
- Max 3 bank accounts: 1 primary (payin + withdrawal) + 2 secondary (payin only).
- Account closure blocked if: negative balance, open positions, unlisted securities, pending corporate actions.
- Cannot reopen same account/user ID after closure.
- All segment activations require both trading AND demat accounts to be active.
- Coin segment status "Generated" requires agent intervention.
