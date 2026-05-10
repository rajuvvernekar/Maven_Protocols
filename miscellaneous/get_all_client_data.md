# get_all_client_data

## Description

WHEN TO USE:

- To look up client profile, account status, PAN, DOB, category
- To determine account type: NRI (NRE/NRO), PIS/Non-PIS, joint, minor, non-individual
- To check bank details, segment status, dormancy, DDPI/POA, nominees, account blocks
- To detect name/DOB mismatch before calling pan_status tool
- To provide client context for: account_modification_report, cashier_payins, withdrawal_request, crux_qs_payouts

## Protocol

# GET ALL CLIENT DATA PROTOCOL

## Section A: Reference Data

### A1 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |  
|---|---|  
| `client_name` | Client's full registered name |  
| `status` | Account status |  
| `dob` | Date of birth |  
| `pan` | PAN number |  
| `client_acc_type` | Account type (resident, NRI, HUF, etc.) |  
| `category` | Client category |  
| `gender` | Gender |  
| `gross_annual_income` | Declared annual income bracket |  
| `gross_annual_income_date` | Date of last income declaration |  
| `bo_sub_status` | Beneficial owner sub-status |  
| `country_list_iso_3166` | Country of residence |  
| `nationality` | Nationality |  
| `rekyc_flag` | Re-KYC required flag |  
| `rekyc_date` | Date Re-KYC was last completed |  
| `idfc_3_in_1_status` | IDFC 3-in-1 block facility status |  
| `bank_N_name` | Registered bank name (N = 1, 2, 3) |  
| `bank_N_ifsc_code` | IFSC code of registered bank |  
| `bank_N_account_type` | Bank account type (savings, current) |  
| `bank_N_account_number` | Bank account number — share last 4 digits only (****1234) |  
| `pis_bank_N_name` | PIS bank name (N = 1, 2) |  
| `pis_bank_N_ifsc_code` | PIS bank IFSC code |  
| `pis_bank_N_account_number` | PIS bank account number — share last 4 digits only (****1234) |  
| `nominee_N_first_name` | Nominee first name (N = 1, 2, 3) |  
| `nominee_N_last_name` | Nominee last name |  
| `nominee_N_percentage_of_shares` | Nominee's share percentage |  
| `primary_dp_status` | Primary demat account status |  
| `primary_dp_activation_date` | Date primary demat was activated |  
| `primary_dp_joint_account` | Whether primary demat is a joint account |  
| `primary_ddpi_flag` | DDPI activation status for primary demat |  
| `primary_ddpi_agreement_date` | Date DDPI agreement was executed |  
| `poa_consent` | POA consent status |  
| `*_status` fields | Status fields for segments and services — translate per reference tables |  
| `*_remarks` fields | Remarks associated with status fields |  
| `zbl_mcx_status` | ZBL MCX segment status |

**Non-shareable:**

| Field | Interpretation |  
|---|---|  
| `owner` | Internal record owner |  
| `modified_by` | Last internal modifier |  
| `broker_code` | Internal broker identifier |  
| `support_code` | Internal support identifier |  
| `support_code_masked` | Masked support code |  
| `email_masked` | Masked email address |  
| `mobile_masked` | Masked mobile number |  
| `primary_dp_id` | Primary demat DP ID |  
| `primary_dp_account_no` | Primary demat account number |  
| `secondary_dp_id` | Secondary demat DP ID |  
| `secondary_dp_account_no` | Secondary demat account number |  
| `tertiary_dp_id` | Tertiary demat DP ID |  
| `tertiary_dp_account_no` | Tertiary demat account number |  
| `*_soft_enable` fields | Internal feature flag fields |  
| `bank_N_account_number` (raw) | Full bank account number — internal use only |  
| `bank_N_micr_code` | Bank MICR code |  
| `bank_N_poa` | Bank POA flag |  
| `pis_bank_N_account_number` (raw) | Full PIS bank account number — internal use only |  
| `pis_bank_N_micr_code` | PIS bank MICR code |  
| `docstatus` | Internal document status |  
| `idx` | Internal record index |  
| `doctype` | Internal document type |  
| `creation` | Record creation timestamp |  
| `modified` | Record last modified timestamp |  
| `acc_open_flag` | Internal account opening flag |  
| `eq_sign` | Equity segment signature status |  
| `eq_signed_on` | Date equity segment agreement was signed |  
| `comm_sign` | Commodity segment signature status |  
| `comm_signed_on` | Date commodity segment agreement was signed |  
| `tags` | Internal tags |  
| `holdings_as_on_date` | Internal holdings date reference |  
| `poa_details` | Internal POA detail object |  
| `address_details` | Internal address detail object |  
| `bank_details` | Internal bank detail object |  
| `dp_details` | Internal demat detail object |  
| `segment_details` | Internal segment detail object |  
| `client_documents` | Internal document references |  
| `uid_meta` | Internal UID metadata |  
| `custodial_participant_code` | Custodial participant code |  
| `cp_code` | Internal CP code |  
| `third_party_demat` | Third-party demat flag |  
| `client_id` | Internal client identifier |

---

### A2 — Account Type Detection

| Account Type | Detection Logic |  
|---|---|  
| Individual | `category` = "Individual" AND `client_acc_type` = "Individual" |  
| Joint | `primary_dp_joint_account` = "YES" |  
| Minor | `bo_sub_status` contains "Minor" |  
| NRI | `client_acc_type` IN ("NRO", "NRE", "NRI") → if "NRI", determine NRE/NRO via `bo_sub_status`; determine PIS/Non-PIS via `pis_bank_*` fields |  
| NRE | `bo_sub_status` contains "RepatriableWith" |  
| NRO | `bo_sub_status` contains "NonRepatriableWith" |  
| PIS | `pis_bank_1_name` OR `pis_bank_2_name` NOT None |  
| Non-PIS | Both `pis_bank_*_name` = None |  
| Non-Individual | `category` = "Non-Individual" |  
| Orbis (NRI custodial) | `custodial_participant_code` NOT None OR `cp_code` NOT None |

---

### A3 — Account Statuses

| Raw Status | Meaning |  
|---|---|  
| Approved | Active |  
| Hold | Closure requested; transactions restricted |  
| Inactivated | Deactivated by client |  
| Deactivated | Closed permanently |

---

### A4 — Segment Statuses

| Raw Status | Meaning |  
|---|---|  
| Activated | Active. Note `*_update_on` timestamp. |  
| Segment Not Active | Not activated. |  
| Dormant | No trading in 24+ months; ReKYC required. |  
| Pending | Activation in progress. Note `*_update_on` timestamp. |  
| Activation Pending | Same as Pending. |  
| Activation Rejected | Activation request rejected. |  
| Blocked | Segment blocked. |  
| Inactivated | Disabled by Zerodha. |

- **Kill switch:** `*_soft_enable` = 0 → client has disabled this segment. `*_soft_enable` = 1 → segment enabled by client.

---

### A5 — Segment Field Mapping

| Field Prefix | Segment Name |  
|---|---|  
| `nse_eq` | NSE Equity |  
| `bse_eq` | BSE Equity |  
| `nse_fo` | NSE F&O |  
| `bse_fo` | BSE F&O |  
| `nse_cfx` | NSE Currency Derivatives |  
| `bse_cds` | BSE Currency Derivatives |  
| `nse_com` | NSE Commodity |  
| `mcx` | MCX Commodity |  
| `starmf` | Mutual Funds (Coin) |  
| `nse_slb` | NSE SLB |  
| `bse_slb` | BSE SLB |  
| `cdsl` | Demat (CDSL) |  
| `kra` | KYC Registration Agency |  
| `ckyc` | Central KYC |  
| `itd` | Income Tax Department |  
| `zbl_mcx` | Single Ledger MCX |

---

### A6 — Key Account Flags

| Field | Meaning |  
|---|---|  
| `zbl_mcx_status` = Active | Single ledger MCX account. |  
| `idfc_3_in_1_status` = Yes | IDFC 3-in-1 account active. |  
| `rekyc_flag` = True | ReKYC completed; `rekyc_date` = date of completion. |

---

## Section B: Decision Flow

### Routing

```  
Route by scenario  
   ├─ account_blocks non-empty → Rule 1  
   ├─ third_party_demat = true → Rule 2  
   ├─ PAN / Name / DOB mismatch → Rule 3  
   └─ Orbis account (custodial_participant_code or cp_code present) → Rule 4
```

---

## Section C: Rules

### Rule 1 — Account Blocks

If `account_blocks` is non-empty → escalate to human agent with the value. Stop.

---

### Rule 2 — Third-Party Demat

If `third_party_demat` = true → escalate to human agent: third-party demat mapped. Stop.

---

### Rule 3 — PAN / Name / DOB Mismatch

1. Extract `pan`, `client_name`, `dob` from the tool response.  
2. Invoke `pan_status` with those fields for validation and resolution.

---

### Rule 4 — Orbis Partner-Managed Account

1. If `custodial_participant_code` OR `cp_code` has any value (e.g., "ORBIS0009164"), the account is managed by a partner broker (Orbis).  
2. For any support query — including fund withdrawal, payin, account transfer, delayed payment charges, or any other account servicing request → escalate to human agent.
