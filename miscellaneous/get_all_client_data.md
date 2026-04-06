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

---

## Section A: Reference Data

---

### A1 — Tool Purpose

This is an internal data-lookup tool for interpretation only; business logic lives in downstream tools.

---

### A2 — Field Usage Rules

**Shareable fields** (can be disclosed to client):

`client_name` | `status` | `dob` | `pan` | `client_acc_type` | `category` | `gender` | `gross_annual_income` | `gross_annual_income_date` | `bo_sub_status` | `bsda_flag` | `country_list_iso_3166` | `nationality` | `rekyc_flag` | `rekyc_date` | `idfc_3_in_1_status` | `bank_N_name` | `bank_N_ifsc_code` | `bank_N_account_type` | `pis_bank_N_name` | `pis_bank_N_ifsc_code` | `nominee_N_first_name` | `nominee_N_last_name` | `nominee_N_percentage_of_shares` | `primary_dp_status` | `primary_dp_activation_date` | `primary_dp_joint_account` | `primary_ddpi_flag` | `primary_ddpi_agreement_date` | `poa_consent` | all `*_status` and `*_remarks` fields | `zbl_mcx_status`

**Internal-only fields** (use for reasoning; communicate outcomes in plain language):

`owner` | `modified_by` | `broker_code` | `support_code` | `support_code_masked` | `email_masked` | `mobile_masked` | `primary_dp_id` | `primary_dp_account_no` | `secondary_dp_id` | `secondary_dp_account_no` | `tertiary_dp_id` | `tertiary_dp_account_no` | all `*_soft_enable` fields | `bank_N_account_number` (raw) | `bank_N_micr_code` | `bank_N_poa` | `pis_bank_N_account_number` | `pis_bank_N_micr_code` | `docstatus` | `idx` | `doctype` | `creation` | `modified` | `acc_open_flag` | `eq_sign` | `eq_signed_on` | `comm_sign` | `comm_signed_on` | `tags` | `holdings_as_on_date` | `poa_details` | `address_details` | `bank_details` | `dp_details` | `segment_details` | `client_documents` | `uid_meta` | `custodial_participant_code` | `cp_code`

**Masked fields** (share last 4 digits only, format: `****1234`):

`bank_N_account_number` | `pis_bank_N_account_number`

**Interactions/Communications tabs:** These tabs are off-limits. Content from these tabs stays internal and is not surfaced to the client.

**Documents tab:** Access only if the client explicitly requests it AND the agent has the "Client Documents Viewer" role.

---

### A3 — Account Type Detection

| Account Type | Detection Logic |
|---|---|
| Individual | `category` = "Individual" AND `client_acc_type` = "Individual" |
| Joint | `primary_dp_joint_account` = "YES" |
| Minor | `bo_sub_status` contains "Minor" |
| NRI | `client_acc_type` IN ("NRO", "NRE", "NRI") |
| NRE | `bo_sub_status` contains "RepatriableWith" |
| NRO | `bo_sub_status` contains "NonRepatriableWith" |
| PIS | `pis_bank_1_name` OR `pis_bank_2_name` NOT None |
| Non-PIS | Both `pis_bank_*_name` = None |
| Non-Individual | `category` = "Non-Individual" |
| Orbis (NRI custodial) | `custodial_participant_code` NOT None OR `cp_code` NOT None |

**NRI resolution chain:** If `client_acc_type` = "NRI" → determine NRE/NRO via `bo_sub_status` → determine PIS/Non-PIS via `pis_bank_*` fields.

---

### A4 — Account Statuses

| Raw Status | Client-Facing Meaning |
|---|---|
| Approved | Active |
| Deactivated | Closed permanently |
| Inactivated | Soft-closed / voluntarily deactivated |

---

### A5 — Segment Statuses

| Raw Status | Meaning & Action |
|---|---|
| Activated | Active. If `*_update_on` < 24h and orders rejected → exchange activation pending, ask client to wait. If `*_update_on` > 24h and still failing → ESCALATE. |
| Segment Not Active | Not activated. |
| Dormant | No trading in 24+ months — requires ReKYC (see **Rule 2**). |
| Pending | Activation in progress. If approved in `account_modification_report` and > 48h have passed → ESCALATE. |
| Activation Pending | Same as Pending. |
| Activation Rejected | ESCALATE. |
| Blocked | ESCALATE. |
| Inactivated | Disabled by Zerodha — client must submit a fresh activation request. |

**Kill switch:** `*_soft_enable` = 0 means the client has disabled this segment themselves. `*_soft_enable` = 1 means the kill switch is OFF (segment enabled by client).

---

### A6 — Segment Field Mapping

| Field Prefix | Segment Name |
|---|---|
| `nse_eq` | NSE Equity |
| `bse_eq` | BSE Equity |
| `nse_fo` | NSE F&O |
| `bse_fo` | BSE F&O |
| `nse_cfx` | NSE Currency Derivatives |
| `bse_cds` | BSE Currency Derivatives |
| `nse_com` | NSE Commodity |
| `mcx` | MCX Commodity (legacy) |
| `starmf` | Mutual Funds (Coin) |
| `nse_slb` | NSE SLB |
| `bse_slb` | BSE SLB |
| `cdsl` | Demat (CDSL) |
| `kra` | KYC Registration Agency |
| `ckyc` | Central KYC |
| `itd` | Income Tax Department |
| `zbl_mcx` | Single Ledger MCX |

<!-- TODO: mtf — not yet exposed -->

---

### A7 — Bank Structure

| Slot | Fields | Capabilities |
|---|---|---|
| Primary | `bank_1_*` | Payin + withdrawal |
| Secondary | `bank_2_*` | Payin only |
| Tertiary | `bank_3_*` | Payin only |
| PIS (NRI only) | `pis_bank_1_*`, `pis_bank_2_*` | NRI PIS operations |

Maximum 3 banks: 1 primary (payin + withdrawal) + 2 secondary (payin only).

Primary bank change online: available for Individual and NRO Non-PIS accounts only.

---

### A8 — PAN Mismatch Response Template

> As per the regulations, to carry out any transactions in the account, the name on the Income tax database (ITD), Exchange (NSE, BSE, MCX), and Depository (CDSL) and KRA records should match. Since your name doesn't match the intermediary records, we request you update your name and verify the correct date of birth (DOB) as soon as possible by following the instructions mentioned below.
>
> Check the name and DOB as per ITD by logging in to the Income Tax Department portal.
> Check the name as per Zerodha records on the Console by downloading the CMR copy.
> To know the documents required and the process to update your name, please visit here.
> Note:
> Please send the scanned copies of the documents for verification by creating a ticket here before sending them via courier.
> It may take up to 7 working days after the documents are received. You can only carry out the transactions on your Zerodha account once your records are updated.

---

### A9 — Account Type Flags & Restrictions

| Flag | Restriction |
|---|---|
| Joint (`primary_dp_joint_account` = "YES") | DDPI: offline only. IMPS/NEFT/RTGS auto-reversed if bank linked to multiple Zerodha accounts. |
| Minor (`bo_sub_status` contains "Minor") | F&O: blocked. |
| Non-Individual (`category` = "Non-Individual") | F&O: offline only. DDPI: offline only. ReKYC: can be done online. |
| Orbis (`custodial_participant_code` NOT None OR `cp_code` NOT None) | Fund withdrawal, payin, account transfer, and all support queries: escalate to Orbis team (Rule 8). DDPI: offline only. |

---

### A10 — Key Account Flags

| Field | Meaning |
|---|---|
| `zbl_mcx_status` = Active | Single ledger MCX; withdrawal cutoffs: weekdays 11:59 PM, Saturday 4:30 PM |
| `idfc_3_in_1_status` = Yes | IDFC 3-in-1 account active |
| `bsda_flag` | **Do not rely on this flag alone.** It is indicative only and may not reflect the latest depository update. To determine BSDA status definitively, fetch `amc_charges` report and apply the BSDA determination logic in **A10a**. |
| `rekyc_flag` = True | ReKYC completed; `rekyc_date` = date of completion |

---

### A10a — BSDA Status Determination Logic

**Do not use `bsda_flag` from get_all_client_data to determine BSDA status.** Instead, fetch the `amc_charges` report and use `charge_after_gst` and `client_holdings` (highest holdings value during the billing quarter) to determine status:

| `charge_after_gst` | `client_holdings` | BSDA Status | Reasoning |
|---|---|---|---|
| ₹0 | ≤ ₹4,00,000 | **BSDA eligible** | Nil AMC — within Slab 1 threshold |
| ₹29.50 | ₹4,00,001 – ₹10,00,000 | **BSDA eligible** | Reduced AMC — within Slab 2 threshold |
| ₹88.50 | ≤ ₹4,00,000 | **Not BSDA** | Standard AMC charged despite low holdings — account not categorised as BSDA |
| ₹88.50 | ₹4,00,001 – ₹10,00,000 | **Not BSDA** | Standard AMC charged despite holdings within BSDA range — account not categorised as BSDA |
| ₹88.50 | > ₹10,00,000 | **Not BSDA** | Holdings exceed ₹10,00,000 BSDA eligibility limit |

**When to apply:** Any time a client asks about BSDA status, BSDA eligibility, or why they were charged a specific AMC amount. This logic supersedes `bsda_flag` — the actual charge applied is the definitive indicator of whether the account is receiving BSDA benefits.

---

### A11 — Client ID Field

The `name` field in the tool response is the client's unique Client ID (e.g., "XX0000"). Store this value and pass it to any downstream tool that requires a client ID (e.g., `stock_gift_requests` fields like `gifted_by`, `claimed_by`, `client_id`).

---

### A12 — Dormancy Response Template

"As you have not traded in your account in 2 years, you must complete your Re-KYC online. Our team will validate the details entered, and the IPV captured and your account status will be marked as Active within 24-48 working hours and we request your patience in this."

---

### A13 — Email/Mobile Redirect Response

"For security, we cannot share contact details. Please check your registered email/mobile in the Kite app under Profile."

---

### A14 — Zerodha Bank Details (NEFT/IMPS/RTGS Payin)

| Field | Value |
|---|---|
| Bank Name | HDFC Bank |
| Account Title | ZERODHA BROKING LTD |
| Account Number | ZERNSE |
| Account Type | Current account |
| Branch | Sandoz Branch, Mumbai |
| IFSC | HDFC0000240 |

These are the only valid Zerodha bank details for fund transfers. Ignore any other bank details from tool data, virtual accounts, or other sources.

**HDFC Bank users:** If the client's HDFC netbanking interface rejects the alphanumeric account number "ZERNSE" when adding Zerodha as a beneficiary, advise the client to select the "Transfer to eCMS account" option in HDFC netbanking.

Step-by-step instructions: https://support.zerodha.com/category/funds/adding-funds/how-to-add-funds/articles/how-do-i-add-money-to-my-trading-account-using-imps-neft-or-rtgs

---

## Section B: Decision Flow

---

### Preflight (run on every query)

```
1. Check `account_blocks`
   └─ Non-empty → ESCALATE TO SM: "[value]". STOP.

2. Resolve account type (per A3)
   ├─ If `client_acc_type` = "NRI" → resolve NRE/NRO via `bo_sub_status` → PIS via `pis_bank_*`
   └─ Note applicable flags/restrictions (per A9)

3. Check Orbis (partner-managed account)
   └─ If `custodial_participant_code` OR `cp_code` has any value → account is managed
      by a partner broker (Orbis). ESCALATE per Rule 8. STOP.

4. Check dormancy
   ├─ `nse_eq_status` OR `bse_eq_status` = "Dormant" → respond per A12
   └─ Any other segment "Dormant" → same message, name the segment via A6

5. Store Client ID from `name` field (per A11)
```

### Route

```
Intent / Condition                            → Rule
────────────────────────────────────────────────────────
Segment status query                          → Rule 1
PAN / Name / DOB mismatch                     → Rule 2
DDPI / POA / TPIN query                       → Rule 3
Bank details query                            → Rule 4
Withdrawal timing query                       → Rule 5
Nominee query                                 → Rule 6
Request for email / mobile / contact info     → Rule 7
Any field from internal-only list requested   → Rule 7
Orbis account — any support query             → Rule 8
Fund transfer to Zerodha via NEFT/IMPS/RTGS   → Rule 9
```

### Scope

- Address queries the client raises about their account data.

### Fallback

If the query does not match any route above, interpret the tool response using the reference data in Section A and general knowledge of the account structure. If no root cause is found, acknowledge the question and escalate if appropriate.

---

## Section C: Rules

---

### Rule 1 — Segment Status Interpretation

1. Identify the segment via **A6**.
2. Read `[segment]_status` and interpret per **A5**.
3. If `*_soft_enable` = 0, the client has disabled this segment (kill switch ON per **A5**).
4. Follow the escalation or wait guidance in **A5** based on the status value and `*_update_on` timestamp.

---

### Rule 2 — PAN / Name / DOB Mismatch

1. Extract `pan`, `client_name`, `dob` from the tool response.
2. Call the `pan_status` tool with those fields.
3. Interpret results:
   - PAN: "E" = valid; anything else = invalid.
   - Name / DOB: "Y" = match; "N" = mismatch.
   - Aadhaar-PAN link: "Y" = linked; "R" or "N" = not linked; "NA" = exempt (NRI, non-citizen, age > 80, Assam/Meghalaya/J&K resident).
4. If Name OR DOB = "N" → respond with the **A8** template.

---

### Rule 3 — DDPI / POA Status

1. Check `primary_ddpi_flag`:
   - "Yes" → DDPI active; client does not need TPIN for delivery sell orders.
2. If DDPI not active, check POA (legacy):
   - `poa_consent` = "YES" AND `primary_poa_for_securities` NOT IN ("NO", "PENDING") → POA active.
3. If neither DDPI nor POA → client must use CDSL TPIN/OTP for delivery sell orders.

**Online DDPI eligibility:** Individual account + Aadhaar-linked mobile number. Not eligible: Joint, Non-Individual, Orbis NRI.

---

### Rule 4 — Bank Details

1. Share bank details using only **A2** shareable fields.
2. Mask account numbers per **A2** masking rules (last 4 digits only).
3. Refer to **A7** for bank slot structure (primary/secondary/tertiary/PIS).
4. If `bank_N_account_type` = "Saving -OD" → this is an overdraft account; overdraft accounts are not allowed.
5. If client has NRE PIS account and asks about withdrawal → NRE PIS accounts cannot withdraw.

---

### Rule 5 — Withdrawal Timing

1. If `zbl_mcx_status` = Active → single ledger; withdrawal cutoffs per **A10**: weekdays 11:59 PM, Saturday 4:30 PM.
2. Otherwise → standard timelines apply. Refer to the withdrawal_request protocol for timeline details.

*(This data is also consumed by the `withdrawal_request` downstream tool.)*

---

### Rule 6 — Nominees

1. If `nominee_1_first_name` = None → no nominees are registered.
2. Share only: first name, last name, percentage of shares (per **A2**).
3. Guardian fields: share only if the client specifically asks about minor nominees.

---

### Rule 7 — Protected Information Requests

1. For email/mobile requests → respond with **A13** template.
2. For any internal-only field → use the field for internal reasoning only; do not disclose its value or existence to the client.

---

### Rule 8 — Orbis Partner-Managed Account

1. If `custodial_participant_code` OR `cp_code` has any value (e.g., "ORBIS0009164"), the account is managed by a partner broker (Orbis).
2. For any support query — including fund withdrawal, payin, account transfer, delayed payment charges, or any other account servicing request → **ESCALATE** — route to Orbis partner team for handling.

---

### Rule 9 — Fund Transfer to Zerodha (NEFT/IMPS/RTGS)

1. Share Zerodha's bank details per **A14**.
2. If the client banks with HDFC → include the eCMS workaround per **A14**.
3. Share the step-by-step instructions link from **A15**.
