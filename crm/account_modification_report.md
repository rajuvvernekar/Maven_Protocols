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
- Report inability to place orders immediately after a segment (MCX, currency) was activated

TRIGGER KEYWORDS: "activate", "segment activation", "Coin", "bank account", "change bank", "modify bank", "DDPI", "MTF", "margin", "address update", "Aadhar", "status of request", "DOB", "date of birth", "gender", "marital status", "occupation", "PEP", "politically exposed", "nominee", "add nominee", "change nominee", "update nominee", "remove nominee", "nominee details", "nominee percentage", "nominee address", "mobile number", "change mobile", "update mobile", "unable to change mobile", "already registered mobile", "email", "change email", "update email", "email address", "email-id", "income proof", "income details", "update income", "secondary demat", "secondary account", "open secondary demat", "secondary account opening", "secondary account rejected", "secondary account status", "secondary account on hold", "contact details", "CERSAI", "close account", "close demat", "account closure", "close trading account", "deactivate account", "submit account closure", "cancel closure request", "closure request submitted by mistake", "open positions", "account closure status", "closure process", "invalid IFSC", "IFSC code error", "IFSC not working", "wrong IFSC", "KYC", "ReKYC", "dormant", "no activity", "inactivity", "segment activated but can't trade", "activated today", "just activated MCX", "MCX not working after activation", "currency not working", "segment sync"

TAGS: account, nri, non-individual

## Protocol

# ACCOUNT MODIFICATION REPORT PROTOCOL
---

## Section A: Reference Data

### A1: Timelines

| Action | Timeline |
|---|---|
| General modification processing | 1–3 working days |
| Segment activation (after approval) | 1 working day |
| F&O activation | Up to 3 working days |
| Contact detail changes (mobile/email) | 1 working day |
| Secondary bank add/change | 2 working days |
| Account closure | 2 working days |
| DDPI offline activation | 1 working day |
| Secondary demat | 3 working days |
| Deactivated account reactivation | 7 working days |
| POA/DDPI revocation | Up to 5 working days |
| Segment deactivation | 1–3 working days |

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

- **Aadhaar-linked mobile:** Mobile number must be linked to Aadhaar — required to eSign.
- **Income proof (any one):** Bank statement (6 months, avg ₹10k+) | Salary slip (gross monthly ₹15k+) | ITR (gross annual ₹1.2L+) | Form 16 (gross annual ₹1.2L+) | Net worth certificate (₹10L+) | Demat holdings (₹10k+, unpledged) | FD receipt (₹1L+)
- **Bank proof (any one):** Personalised cancelled cheque (name printed) | Self-attested bank statement (IFSC/MICR visible) | Self-attested passbook
- **Address proof (any one):** Driving Licence | Voter ID | Passport | Masked Aadhaar | NREA job card | NPR letter
- **File requirements:** PDF, under 5 MB, logo and seal of authority.
- **Courier address:** Zerodha Customer Support Centre, 192A 4th Floor, Kalyani Vista, 3rd Main Road, JP Nagar 4th Phase, Bengaluru, 560076

---

### A4: Field Rules

**Non-shareable:**

| Field | Interpretation |
|---|---|
| `form_type` | Type of modification request — `segment_activation` = segment activation; `bank_modification` = bank modification; `rekyc` = ReKYC for equity and mutual fund segments; `rekyc_fno` = ReKYC for F&O, currency, and commodity segments; `primary_bank` = primary bank; `secondary_bank` = secondary bank |
| `description` | Internal request description |
| `request_type` | Internal request type classification |
| `income_proof` | Internal field indicating income proof status |
| `bank_name` | Bank name associated with the modification request |
| `account_number` | Account number for bank modification requests |
| `new_email` | New email address submitted in the request |
| `new_mobile` | New mobile number submitted in the request |
| `signer_name` | Name of the signatory for the request |
| `notary_id` | Internal notary identifier |
| `bank_order` | Internal bank ordering field |
| `kyc_field_type` | Internal KYC field type classification |
| `STARMF` | Refers to the Coin / Mutual Funds segment |
| `primary_ddpi_flag` | DDPI status — if active, communicate as "DDPI is active" |
| `primary_ddpi_agreement_date` | Date the DDPI agreement was signed |
| `poa_consent` | Internal POA consent status |
| `primary_poa_for_securities` | Internal POA field for securities |
| `primary_dp_status` | Internal demat account status |
| `third_party_demat` | Indicates third-party demat linkage |
| `client_id` | Internal client identifier |

- **Segment status and remarks field pairs:**

Use `*_status` values with the client-facing name for communication. Use `*_remarks` for internal diagnosis only.

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
| CDSL | `cdsl_status` | `cdsl_remarks` | — |
| CKYC | `ckyc_status` | `ckyc_remarks` | — |
| KRA | `kra_status` | `kra_remarks` | — |
| ITD | `itd_status` | `itd_remarks` | — |
| POA | `poa_status` | `poa_remarks` | — |
| NSE SLB | `nse_slb_status` | `nse_slb_remarks` | Securities Lending and Borrowing (SLB) |
| BSE SLB | `bse_slb_status` | `bse_slb_remarks` | Securities Lending and Borrowing (SLB) |
| ZBL MCX | `zbl_mcx_status` | `zbl_mcx_remark` | Commodity segment — Single Ledger activated |

Segments with — in the label column are internal systems. Use their status and remarks for reasoning only.

---

### A5: Account Context

Context extracted from `get_all_client_data`:

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

- **Online:** Eligibility: Aadhaar-linked mobile (see **A3**). Ineligible: joint accounts, mobile not linked to Aadhaar. Process: account portal per **A14**. Charges: **A2** standard. Timeline: **A1** general processing. Requirements: Name on Aadhaar must match e-sign name. Minor: minor's Aadhaar for address, guardian's Aadhaar for e-sign.
- **Offline:** Documents: account modification form per **A14**, self-attested PAN, address proof (see **A3**). Charges: **A2** standard. Timeline: **A1** general processing. Validity: forms valid 30 days from submission. Conditions: signature must match account opening. NRI: notarised address proof. Courier: **A3** address. Support article: offline address change per **A14**.

#### Contact Details Change

- Share the contact details change article per **A14**.
- **Indian mobile:** A number is Indian if it has exactly 10 digits and starts with 6, 7, 8, or 9. Any other format is international.
- **Online:** Platform: Kite app/web. Eligibility: Indian mobile, Aadhaar-linked mobile (see **A3**), IPV, e-sign. Timeline: **A1** contact detail changes. Ineligible: international mobile, non-individual, joint accounts.
- **Offline:** Courier to **A3** address. Documents: modification form + IPV. Timeline: **A1** contact detail changes. No charges. Mandatory for non-individual; optional for individual.
- **International mobile / NRI:** eSign and attach to ticket, or courier.
- **No access to registered mobile AND email:** Refer to the reset password article per **A14**.
- **Mobile/email already linked to another account:** escalate to human agent without addressing the query.
- **Client requests deletion/removal of mobile number from system:** escalate to human agent without addressing the query.

#### DOB / Gender / Marital / Occupation / PEP Update

- **Online:** Condition: correct on Aadhaar + ITD. Process: account portal per **A14** → ReKYC → Update profile → IPV → e-sign.
- **Offline:** Condition: Aadhaar not linked OR joint account. Documents: account modification form per **A14**, self-attested PAN, address proof (see **A3**). Charges: **A2** standard. Timeline: **A1** general processing. Courier: **A3** address.

#### Financial Proof Update

Process: signup.zerodha.com/rekyc. Timeline: **A1** general processing. Acceptable proofs: **A3** income proof. File requirements: **A3** file requirements.

#### Account Deactivation

- **Method:** Kill Switch feature.
- **Effects:** Trading deactivated, demat frozen. No Kite/Console access. AMC continues. Periodic emails continue.
- **Re-enable restriction:** Per **A10** Kill Switch.
- **Deactivation:** Online: eSign the account deactivation form per **A14** and attach to ticket. Offline: courier the account deactivation form per **A14** to **A3** address.
- **Reactivation:** Online (Aadhaar-linked): attach eSigned reactivation letter to ticket. Offline: courier reactivation letter, self-attested PAN, address proof (see **A3**) to **A3** address. Timeline: **A1** deactivated reactivation.

---

### A7: Bank Account Processes

- **Limits:** Max 3 accounts: 1 primary (payin + withdrawal) + 2 secondary (payin + withdrawal). All linked bank accounts support both deposits and withdrawals once verified.
- **Pending verification:** If a secondary/tertiary bank account is pending penny drop verification, withdrawals to that account will be available once verification completes (typically within 2 working days of approval). No charges apply for penny drop verification.
- **Allowed account types:** Savings, Current, Cash Credit. Overdraft (OD) accounts are not allowed. PayTM Payments Bank cannot be linked.
- **Relative's bank account:** Not allowed. SEBI mandates bank in client's name only.

#### Primary Bank Change (Online)

Eligibility: Individual accounts, NRO Non-PIS. Process: Console → Account → Bank → Modify → Details → E-sign. Verification: test transfer. Charges: **A2** standard. Timeline: **A1** general processing. Support article: primary bank change per **A14**.

- **Joint bank account:** Primary holder of bank and demat must match. If different: offline with account modification form per **A14** + bank proof (see **A3**).
- **Minor accounts:** Online; guardian e-signs. Bank details must be for minor.

#### Secondary Bank Add

Eligibility: Resident individual or non-individual. Process: Console → Account → Bank → Add → Details → OTP → Verify. Timeline: **A1** secondary bank. Withdrawals available once penny drop verification completes.

- **Joint account secondary:** If not the primary holder: share self-attested bank proof (see **A3**) by replying to this ticket.

#### Secondary Bank Change

Process: Console → Account → Bank → Modify → Details → OTP → Verify. Verification: test transfer. Timeline: **A1** secondary bank. No charges.

- **If verification fails:** Share bank proof (see **A3**) by replying to this ticket. If joint account and not the primary holder: share self-attested bank proof by replying to this ticket.

#### Secondary to Primary Conversion

Eligibility: Aadhaar-linked mobile (see **A3**). Process: Console → Account → Bank → Set as primary → E-sign. Timeline: **A1** general processing. Charges: **A2** standard. Effect: current primary becomes secondary. Note: during processing, withdrawals go to old primary.

#### Secondary Bank Remove

Process: Console → Account → Bank → Delete → OTP → Verify. Processing: instant.

#### Current Account Linking

Allowed as primary or secondary. Condition: names match across Zerodha/PAN/bank.
- **Primary:** Documents: modification form, cancelled cheque/statement, banker letter. Charges: **A2** standard. Courier: **A3** address.
- **Secondary:** Update Console, then attach banker letter to ticket.
- **Banker letter:** Current accounts are registered in a business name, not an individual name. The banker letter confirms the individual's authority to make personal investment transactions through the business account. It must state that the account holder solely operates the business and makes all financial transactions.
- Timeline: **A1** secondary bank.

#### Joint Bank Accounts

Allowed if joint holder. Same process as single-holder. Restriction: if linked to multiple Zerodha accounts → UPI/gateway only; IMPS/NEFT/RTGS reversed.

#### Bank Details Update Errors

When IFSC errors occur (O vs 0 confusion, branch not recognised by CDSL, "invalid IFSC" error): escalate to human agent with client ID and error details.

#### Primary Bank Penny Drop Verification

Condition: bank_type = "Primary" AND request_type = "update" AND bank validation failed. Resolution: direct to ReKYC flow at account portal per **A14**. Client uploads bank statement, cheque, or passbook within the ReKYC flow.

---

### A8: Account Closure

- **Methods:** Online: resident Indians, NRIs, minors with Kite. Offline: non-individual only.
- **Timeline:** **A1** account closure.
- **Pre-closure requirements:** Clear negative balance, square off positions, sell/transfer holdings, delete SIPs and mandates, download reports (inaccessible after closure).
- **Closure cum transfer:** Transfer holdings to another demat while closing. No additional charges. Refer to the closure cum transfer SOP per **A14**.
- **Online process:** Console → Account → Segments → Account closure. Options: sell holdings (Kite redirect) OR transfer holdings (demat in your name only). Accept terms → eSign with Aadhaar.
- **Demat closure:** When a trading account is closed, the linked CDSL demat account is also closed as part of the same process. The client does not need to submit a separate demat closure request to CDSL.
- **AMC after closure:** Not charged from day closure is processed.
- **Post-closure new account error:** escalate to human agent.
- **Blocked closure:** If closure is blocked due to unlisted securities or pending corporate actions → escalate to human agent. Cannot reopen same account/user ID after closure.

---

### A9: Demat (DDPI / POA / Secondary Demat)

#### DDPI

Definition: Document allowing broker to debit securities. Benefit: no CDSL TPIN/OTP required for selling. SEBI restriction: debits only for client-placed sell trades. Optional — can use CDSL TPIN instead. Replaced POA (Nov 2022).

- **Online activation:** Console → Account → Demat → Enable DDPI → Accept → E-sign with Aadhaar. Minor accounts: guardian's Aadhaar required. Charges: **A2** DDPI activation.
- **Offline activation:** Applies to: NRI using Orbis, joint accounts, non-individual. Documents: DDPI form (signature must match account opening). Courier: **A3** address. Charges: **A2** DDPI activation. Requirement: sufficient balance for charge deduction. Timeline: **A1** DDPI offline.
- **Status check:** Kite app: User ID → Profile. Kite web: Client ID → My Profile. Alternative: CDSL TPIN if no POA/DDPI.

#### POA/DDPI Revocation

- **Online:** Eligibility: individual, Aadhaar-linked mobile (see **A3**). Process: print → fill → sign → scan → eSign → attach to ticket.
- **Offline:** Applies to: non-individual, joint, individual with no Aadhaar link. Process: print → fill → courier to **A3** address.
- Timeline: **A1** POA/DDPI revocation. Post-revocation: must use CDSL TPIN to sell.

#### Secondary Demat Account

Availability: free, online. Eligibility: Aadhaar-linked mobile (see **A3**), resident individual only. Process: Kite → User ID → Profile → Demat → Secondary → Nominee → IPV → E-sign. Timeline: **A1** secondary demat. Visibility: Console only (not Kite). Closure: offline only.

- **Pending eSign troubleshooting:** eSign link may require a hard refresh (Ctrl + Refresh or F5) to appear.

---

### A10: Segments

#### F&O / Currency / Commodity Activation

Prerequisite: equity segment must be active. Demat prerequisite: `primary_dp_status` must be "Active" (see Rule 5).

- **Online eligibility:** Aadhaar-linked mobile (see **A3**). Offline only: non-individual accounts.
- **Process:** Kite/Console → User ID → Profile → Segments → Activate.
- **Required info:** Income range and proof, trading experience, commodity classification (for commodities).
- **Timeline:** **A1** F&O activation.
- **Income proof:** See **A3**.
- **File requirements:** See **A3**.
- **Support article:** F&O activation per **A14**.
- **Commodity classification:** Farmers/FPO: farmer, cooperatives, FPOs. VCP: processor, commercial user, importer, exporter, trader, stockist, producer, SME/MSME, wholesaler. Others: MCX traders not in above.
- **Restrictions:** Sikkim: domicile certificate for commodities. Minors: cannot enable F&O.
- **Currency F&O:** RBI declaration form eSign required.

#### F&O / Currency / Commodity Deactivation

- **Temporary (Kill Switch):** Disables the segment until the client chooses to re-enable. Ensure no open orders or positions before disabling. Once disabled, the segment can only be re-enabled after 12 hours. Process: Kite/Console → User ID → Profile → Segments → Kill Switch.
- **Permanent deactivation:** Requires submission of an account modification form. Applicable to F&O, Currency, and Commodity segments. Process: (1) Download and fill the account modification form per **A14** — specify the segment(s) to be permanently deactivated. (2) eSign the form via Digilocker per **A14**. (3) Submit the eSigned form in the same support ticket.
- Timeline: **A1** segment deactivation.
- Support article: F&O deactivation per **A14**.

#### MTF (Margin Trading Facility) Activation

MTF allows clients to buy stocks with leverage. Prerequisite: DDPI must be active on the account.

- **DDPI active:** MTF can be used via Kite order placement with MTF product type.
- **DDPI not active:** Client must first activate DDPI per **A9**. If a DDPI request already exists in `account_modification_report`, apply Rule 2 to report its status.
- Support article: MTF trading not allowed per **A14**.

#### Active Segments Check

Kite app: Client ID → Profile. Kite web: Client ID → Name. Click segment → Console redirect for Kill Switch.

---

### A11: Nomination

- **Verification:** Console → Account → Nominees | CMR copy.
- **Minor nominees:** The minor's PAN is mandatory for the online nomination process. If the minor does not have a PAN, the offline process must be used. Refer to nomination update article per **A14**.
- **Modification online:** Modify name, DOB, address (with nominee ID proof — Aadhaar or Driving Licence), relationship, email, mobile. Process: download + print nominee form (PDF) + account modification form (PDF) → wet sign both → eSign both → attach to ticket. Charges: **A2** standard.
- **Modification offline:** Delete/opt-out of nominee only. Forms: account modification form + annexure 1B → sign → courier to **A3** address.
- **Online scope limitation:** Delete or opt-out of nominee requires the offline process.
- **Joint accounts:** Offline only.
- **Charges:** **A2** standard.
- **Inactivity alert:** No trading for 24 months → deactivated/dormant. If not reactivated within 30 days → nominee notified.
- **Demat-mode MF (CDSL / RTA sync):** For Coin holdings in Demat mode, the nominee registered with CDSL applies. RTAs (e.g., Kfintech) may show "Nominee Not Registered" due to a sync delay between CDSL and the RTA — this does not mean the nominee is missing.
- Support article: nomination update article per **A14**.

---

### A12: KYC & Reactivation

#### ReKYC Process Details

- **ReKYC authentication:**
  - Address update selected ("Update as per Aadhaar"): Aadhaar OTP + IPV required. eSign not required.
  - Profile-only ReKYC (no address change): eSign required. Aadhaar OTP not required.

- **Support article:** ReKYC / account reactivation per **A14**.

#### Deactivated Account Reactivation

Applies to voluntarily deactivated accounts only. Dormant accounts: complete ReKYC instead.

- **Online:** Eligibility: Aadhaar-linked mobile (see **A3**). Method: attach eSigned reactivation letter to ticket.
- **Offline:** Documents: signed reactivation letter, self-attested PAN, address proof (see **A3**). Courier: **A3** address.
- Timeline: **A1** deactivated reactivation.
- Result: same client ID, new password.
- Demat closed: submit demat application. Account closed: complete new account opening.

#### Rejection Reasons & Resolution

- **Father/spouse name mismatch during ReKYC:** Cannot be skipped; requires the offline process via the name change article per **A14**. Forms are not available on Console — use **A14** links.

**Rejection reasons and resolution:**

| Rejection | Resolution |
|---|---|
| PAN not clear | Attach clear self-attested PAN |
| Minor PAN | Attach major PAN |
| Father name mismatch | Offline process — see above |
| Signature not clear | Attach clear self-attested signature |
| Name confirmation | Attach government ID proof |
| Proprietor bank | Attach banker letter |
| Invalid bank proof | Resubmit ReKYC with valid bank proof |
| Bank not in name | Share self-attested bank proof by replying to this ticket |
| Invalid IPV | Complete ReKYC |
| 3rd party Aadhaar | eSign completed using a different Aadhaar, or name mismatch between Aadhaar and Demat account. |

---

### A13: Utilities

- **eSign documents:** Platform: see **A14** (Digilocker). Requires: Aadhaar-linked mobile (see **A3**). Cost: free. Steps: Login → Drive → Documents → Upload → Sign → Enter Aadhaar → OTP → Download.
- **Trade alerts not received:** Cause: incorrect contact details or DND blocking. Exchange contacts per **A14** for platform-level issues.

---

### A14: Links

| Topic | URL |
|---|---|
| Account portal (modifications, ReKYC, segments) | account.zerodha.com/account |
| ReKYC / account reactivation | https://support.zerodha.com/category/your-zerodha-account/your-profile/kyc-re-activation/articles/re-activate-my-account |
| Nominee update / modification | https://support.zerodha.com/category/your-zerodha-account/nomination-process/articles/update-modify-nominee-details |
| eSign via Digilocker | https://support.zerodha.com/category/your-zerodha-account/account-modification-and-segment-addition/account-modification/articles/esign-via-digilocker |
| Contact details change | https://support.zerodha.com/category/your-zerodha-account/account-modification-and-segment-addition/account-modification/articles/change-contact-details |
| Reset password / new contact details | https://support.zerodha.com/category/your-zerodha-account/your-profile/account/articles/reset-password-new-contact-details |
| Account closure cum transfer SOP | https://s3.ap-south-1.amazonaws.com/staticassets.zerodha.net/support-portal/2025/06/24/Article/FZUJ7VWF_E6T6ngib3xeSu0JR1750748598.pdf |
| Account modification form (PDF) | https://zerodha-common.s3.ap-south-1.amazonaws.com/Downloads-and-resources/AccountDetailsModificationDeletionForm.pdf |
| F&O deactivation | https://support.zerodha.com/category/your-zerodha-account/account-modification-and-segment-addition/account-modification/articles/how-do-i-deactivate-f-o-on-my-account |
| MTF trading not allowed | https://support.zerodha.com/category/console/portfolio/pledging/articles/mtf-trading-not-allowed |
| Name change / profile name mismatch | https://support.zerodha.com/category/your-zerodha-account/your-profile/general-profile-questions/articles/why-is-the-name-on-my-zerodha-account-different-than-on-the-documents-i-ve-submitted |
| Open demat with existing trading account | https://support.zerodha.com/category/account-opening/resident-individual/ri-online/articles/how-do-i-open-a-demat-account-if-i-already-have-a-trading-or-commodity-account |
| Single ledger facility | https://support.zerodha.com/category/console/segments/segment-addition/articles/single-ledger |
| Unable to pledge | https://support.zerodha.com/category/console/portfolio/pledging/articles/unable-to-pledge |
| Primary bank change | https://support.zerodha.com/category/funds/adding-bank-accounts/primary-bank-account/articles/how-do-i-change-my-primary-bank-account-linked-with-zerodha |
| Account deactivation | https://support.zerodha.com/category/your-zerodha-account/account-modification-and-segment-addition/account-modification/articles/deactivate-account |
| F&O activation | https://support.zerodha.com/category/console/segments/segment-addition/articles/how-do-i-enable-trading-futures-and-options |
| Address change (online) | https://support.zerodha.com/category/your-zerodha-account/account-modification-and-segment-addition/account-modification/articles/how-do-i-change-the-registered-address-on-my-account-online |
| Offline address change | https://support.zerodha.com/category/your-zerodha-account/account-modification-and-segment-addition/account-modification/articles/what-is-the-procedure-to-change-the-registered-address-on-my-account-offline |
| NSE exchange contact | nseindia.com/contact/corporate-office |
| BSE exchange contact | bseindia.com/static/about/contact_us.aspx |
| MCX exchange contact | mcxindia.com/contact-us/department-contacts |

---

## Section B: Decision Flow

### Routing

```
Route by scenario
   ├─ Name / DOB / PAN update → Rule 1
   ├─ Modification status inquiry → Rule 2
   ├─ Modification cancellation (eSign not yet completed) → escalate to human agent
   ├─ Closure-related escalations (secondary demat, employer policy,
   │   IL&FS, closure cum transfer) → Rule 4
   ├─ Segment activation → Rule 5
   ├─ MTF activation query → check primary_ddpi_flag; if inactive, apply Rule 2 on DDPI request and guide per A9 / A10 MTF subsection
   ├─ Any equity segment Dormant (nse_eq_status or bse_eq_status) → Rule 6
   ├─ Segment status issue → Rule 7
   ├─ Segment rejected (PAN failure) → Rule 7.1
   ├─ Nominee query (modification, rejection, CAS nominee mismatch) → Rule 8
   ├─ Pledging / collateral margin query → Rule 9
   ├─ Segment deactivation (disable / deactivate F&O, Currency, or Commodity) → Rule 10
   ├─ Client reports app/web error message → Rule 11
   ├─ Unpaid dividend / RTA CML query → Rule 12
   ├─ Email or mobile modification status / request query → Rule 13
   └─ Address change query → Rule 14
```

### Fallback

If the query does not match any route above → escalate to human agent.

---

## Section C: Rules

### Rule 1: Name / DOB / PAN Updates

If query mentions name change, DOB mismatch, or PAN correction → escalate to human agent without addressing the query.

---

### Rule 2: Modification Status

- **Check request:** For segment activation → query `form_type` IN (`rekyc`, `rekyc_fno`, `segment_addition`), most recent within 3 months. For Coin/MF → query `form_type` = `rekyc`, most recent within 3 months. If no request found OR last request > 3 months → communicate: last request date (if any) and guide to submit a new request at account portal per **A14**.

- **No matching request (count=0):** If the client claims they submitted a request but `account_modification_report` returns no matching row, treat the report as the source of truth. Apply the "No request found (count=0) despite client claim of submission" row in the status table below.

- **Multi-row processing:** When the query returns multiple rows (e.g., both `rekyc` and `rekyc_fno` from the same submission), evaluate each row's status independently. A single ReKYC submission can result in equity segments approved while F&O segments are rejected. Match the row to the client's query — if the client is asking about F&O/currency/commodity, check the `rekyc_fno` row specifically. Report only the status relevant to what the client asked.

- **Segment status check:** For segment activation queries, check segment status fields in `get_all_client_data` using the field pairs in **A4**. If segment shows Rejected, Activation_rejected, or Deactivated → check the corresponding remarks field (per **A4**) and apply Rule 7.1 before any other response.

**Status responses:**

| Status | Communicate |
|---|---|
| Request_pending / Processing | Modification type, submission date, expected timeline per **A1**. |
| Pending_eSign | Modification type is pending eSign on Console. |
| Approved | Cross-check: submission_date must be at least [relevant timeline per **A1**] before current date. Communicate: modification type, approval date, activation timeline per **A1**. |
| Rejected | Check all relevant form_types (`rekyc`, `rekyc_fno`, `segment_addition`). Communicate: modification type, rejection reason, guidance to resolve and resubmit. |
| No request found (count=0) despite client claim of submission | No matching request found; process may not have completed. Ask client to retry. If IPV and eSign were completed but request is absent, ask for confirmation screenshot. |

---

### Rule 3: ReKYC

Check `account_modification_report` for an existing ReKYC request (`form_type` IN (`rekyc`, `rekyc_fno`)) within the last 3 months.

- **Found → apply Rule 2** for that request.
- **Rejected with "Invalid IPV"** → guide to complete ReKYC again at account portal per **A14**.
- **Rejected with any other reason** → communicate rejection reason and escalate to human agent.
- **Not found OR > 3 months** → guide to account portal per **A14**; complete ReKYC with Aadhaar eSign. Requires: Aadhaar-linked mobile (see **A3**). Share the reactivation support article from **A14**. Authentication per **A12**.

**Charges:** **A2** standard — applicable only if client selects "Update as per Aadhaar". Mention only if this option is selected.

---

### Rule 4: Account Closure

Query mentions "secondary demat" / "employer policy" / "employer restriction" / "empanelment" / "company policy" / "IL&FS" / "ILFS" / "closure cum transfer" / "cancel account opening" / "don't want to proceed with account opening" → escalate to human agent without addressing the query.

**Pre-closure checks:**
Invoke `ledger_report`, `console_eq_holdings`, `kite_positions`, `console_mf_holdings`. Note:
- Debit balance status
- Active holdings status
- Open positions status

**Closure request:**
Invoke `account_modification_report`.

If a closure request exists:

| Status | Action |
|---|---|
| Approved | Acknowledge closure; ask for feedback on issues that led to closure; thank client for their association with Zerodha. |
| Request_pending / Processing / Pending_eSign / Rejected / No match | Escalate to human agent; include pre-closure check results. |

No closure request found → escalate to human agent; include pre-closure check results.

**Post-closure new account error:** escalate to human agent.

---

### Rule 5: Segment Activation Queries

**Demat prerequisite:**
From `get_all_client_data`, check `primary_dp_status`. If ≠ "Active" → the client will see an error and cannot activate any segment until the demat account is active; share the demat account opening and single ledger facility articles per **A14**. Stop.

**Existing activation request:**
Check `account_modification_report` for `form_type` IN (`rekyc`, `rekyc_fno`, `segment_addition`), most recent within 3 months. If multiple rows exist, match each row to the segment the client is asking about — evaluate independently per Rule 2 multi-row processing. If a request exists:
- In progress or approved: if `form_type = rekyc_fno`, F&O/currency/commodity activation is included in the ReKYC request. Confirm the existing request covers the segment and provide the processing timeline per **A1**.
- Rejected: apply Rule 2 for the rejection before providing any new activation guidance.

**No existing request:**
Guide per **A10** based on account type.

**UI error during activation:**
If client reports a UI error (e.g., "Service unavailable", "Unknown exchange segment", page not loading, repeated errors) during the activation flow:
1. Clear browsing history completely.
2. Clear cookies and cache.
3. Try in incognito/private mode.
4. Try on a different device and different network.

If error persists after troubleshooting → escalate to human agent.

---

### Rule 6: Dormancy

Triggered when `nse_eq_status` OR `bse_eq_status` = "Dormant". Check which segments are dormant (equity vs. F&O/commodity) using the field pairs in **A4**.

- **Equity dormant:** Check `account_modification_report` for `form_type` IN (`rekyc`, `rekyc_fno`):
  - In progress (Request_pending / Processing / Reactivation_pending) → ReKYC in process; account reactivates within 1–2 working days.
  - Rejected → apply Rule 2 for the rejection reason before advising resubmission.
  - Not found OR > 3 months → guide to account portal per **A14**; share reactivation article from **A14**. Authentication per **A12**.

- **F&O/commodity dormant (equity already active):** Check `account_modification_report` for `form_type` IN (`rekyc_fno`, `segment_addition`); also check `form_type` = `rekyc` if not found. Evaluate each row independently per Rule 2. Rejected request exists → apply Rule 2 first. No existing request → guide per Rule 5.

- **After equity reactivation:** F&O/commodity segments require separate activation via Console → Account → Segment Activation. Coin/MF: ReKYC automatically re-enables Coin — cross-check Coin segment status in `get_all_client_data` to confirm.

---

### Rule 7: Segment & Account Status Translations

When a client queries about commodity trading (MCX, CRUDEOILM, commodity options, or any commodity product), check both `zbl_mcx_status` and `nse_com_status`. Report the status of each segment that is not fully active. Both segments may need to be active depending on the product the client wants to trade.

| Raw Status | Response |
|---|---|
| `Reactivation_pending` | Check timestamp against current time. Within 1 working day → segment/account being processed; active within 1 working day of submission. 1 working day elapsed → escalate to human agent. |
| `Request_pending` | Same as Reactivation_pending. Cross-check: ReKYC → verify rekyc or rekyc_fno form status; segment → verify segment_addition form status (Rule 2). |
| `Blocked` | Communicate the `remarks` field content for this status. |
| `Activated` | Confirm segment is active. If client reports inability to place orders or shows 0 available funds → check activation timestamp. Calculate: activation time + 1 working day. If that time is still in the future → inform client of the activation date and that orders will be possible from activation date + 1 working day. If 1 working day has already passed → escalate to human agent. Always give the specific date, not a generic window. |
| Coin segment = `Generated` | Escalate to human agent. |
| `Dormant` | Apply Rule 6. |
| `Activation_rejected` | Treat as Rejected. Check the corresponding remarks field (per **A4**). Apply Rule 7.1 if remarks contain "PAN Verification Failed." For other rejection reasons, inform client of the specific reason and guide to resubmission. |

---

### Rule 7.1: Segment Rejection — PAN Verification

If any segment (per **A4** field pairs) shows as Rejected, Activation_rejected, or Deactivated AND the corresponding remarks field contains "PAN Verification Failed":

1. Invoke `pan_status` to retrieve the specific rejection reason.
2. If `pan_status` returns a specific, actionable mismatch → follow the ‘pan_status’ tool's resolution guidance.
3. For all other `pan_status` results (no issues found, ambiguous, or unclear) → escalate to human agent.

---

### Rule 8: Nominee Queries

Nominee modifications are handled through the nominee process only — direct to **A11** support article per **A14**.

From `get_all_client_data`, check `nominee_1_first_name`, `nominee_2_first_name`, `nominee_3_first_name`.

**Client wants to modify / change / add a nominee:**
- Nominee present → modification is offline only; guide per **A14** nomination update article.
- No nominee present → guide per **A14** nomination update article to add a nominee.

**Client reports "Nominee Not Registered" in CAS or RTA statement (Demat-mode MF):**
- Any nominee name populated → nominee is confirmed per A11; direct client to verify at Console → Account → Nominees.
- No nominee name populated → guide client to add a nominee per **A14** nomination update article.

**If query mentions nominee modification request AND client reports rejection:**
1. Check `account_modification_report` where `form_type` = "nominee_addition".
2. Status = Rejected → communicate rejection reason and escalate to human agent.
3. Status ≠ Rejected → apply Rule 2.

---

### Rule 9: Pledging / Collateral Margin Queries

If the client is unable to pledge or has a query about pledging holdings for collateral margin:

1. Check `nse_fo_status` (per **A4**). Pledging for margin purposes requires an active F&O segment.
2. If `nse_fo_status` = "Activated" but the client is still unable to pledge → share the unable to pledge article per **A14**.
3. If `nse_fo_status` ≠ "Activated" → guide client to activate F&O first per Rule 5.

---

### Rule 10: Segment Deactivation

If the client wants to disable or deactivate an F&O, Currency, or Commodity segment:

1. Temporary or ambiguous intent → present Kill Switch first (per **A10**), then permanent deactivation as an alternative. Permanent intent ("permanently deactivate", "remove segment") → guide directly to permanent deactivation per **A10**.
2. **Temporary (Kill Switch):** Check for open orders and positions. If found, communicate to the client that all open orders and positions must be closed before disabling the segment. Guide per **A10** Kill Switch process. Mention the 12-hour re-enable restriction.
3. **Permanent deactivation:** Guide per **A10** permanent deactivation process — download the account modification form, specify the segment(s) to be permanently deactivated, eSign via Digilocker per **A14**, and submit the eSigned form in the same support ticket. Share the support article from **A10**.
4. **Equity segment deactivation:** Equity segments cannot be individually deactivated. If the client wants to deactivate all trading → refer to **A6** Account Deactivation (Kill Switch for entire account) or **A8** Account Closure.

---

### Rule 11: UI / App Error

When the client reports an error message in the app or web platform (e.g., "account is inactive," "service unavailable," "account not found") not related to segment activation:

1. From `get_all_client_data`, check account status, segment statuses, and `account_blocks`. If any underlying account issue is found → apply the relevant rule for that issue.
2. If account data shows no issues (account status = Approved, segments Activated, no account blocks):
   a. Ask the client to verify they are entering the correct User ID during login.
   b. If User ID is correct, ask the client to retry after clearing the app cache or using a different browser/device.
   c. If the issue persists, ask the client to share a screenshot of the error message.
   d. Screenshot confirms a persistent error with no account-level cause → escalate to human agent. Include: client ID, error message, and confirmation that account data shows no issues.

---

### Rule 12: RTA / Unpaid Dividend

1. Check `bank_details` in `get_all_client_data` — verify `bank_1_dividend` = YES.
2. If bank details are correct and dividend enabled: communicate that Zerodha shares updated CML data with CDSL; CDSL forwards it to RTAs in their regular update cycle, typically within a few business days. If not credited within 10 business days, follow up with RTA directly. Share the primary bank change article per **A14** only if bank details need updating. Charge of ₹25 + GST applies for primary bank change.
3. If bank details missing, incorrect, or dividend ≠ YES: guide client to update bank details per **A7** Primary Bank Change. Confirm that the updated CML will be shared with CDSL after the change is processed.

---

### Rule 13: Email / Mobile Modification

| Query type | `form_type` to check |
|---|---|
| Email modification | `email_modification` |
| Mobile modification | `mobile_modification` |

**No request found (count = 0):**
Guide per **A6** Contact Details Change.

**Request exists:**
Communicate status per Rule 2 status responses. If status = Rejected → communicate the `remarks` field.

---

### Rule 14: Address Change

-From `get_all_client_data`, check `client_acc_type`.

**Account type = individual:**
-Check `primary_dp_joint_account`.
- "Yes" → joint account; offline process only per **A6** Address Change.
- Not "Yes" → guide per **A6** Address Change online process and **A14** address change (online) article.

**Account type ≠ individual:**
Offline process only per **A6** Address Change.
