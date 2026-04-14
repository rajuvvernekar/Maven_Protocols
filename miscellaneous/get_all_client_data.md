# get_all_client_data

## Description

WHEN TO USE:

- To look up client profile, account status, PAN, DOB, category
- To determine account type: NRI (NRE/NRO), PIS/Non-PIS, joint, minor, non-individual
- To check bank details, segment status, dormancy, DDPI/POA, nominees, account blocks
- To detect name/DOB mismatch before calling pan_status tool
- To provide client context for: account_modification_report, cashier_payins, withdrawal_request, crux_qs_payouts

## Protocol

---

## Section A: Reference Data

---

### A1 — Tool Purpose

This tool collects and interprets client data, then routes to the appropriate downstream tool for resolution — all client queries are resolved exclusively by downstream tools, not by this tool.

---

### A2 — Field Usage Rules

**Shareable fields** (can be disclosed to client):

`client_name` | `status` | `dob` | `pan` | `client_acc_type` | `category` | `gender` | `gross_annual_income` | `gross_annual_income_date` | `bo_sub_status` | `country_list_iso_3166` | `nationality` | `rekyc_flag` | `rekyc_date` | `idfc_3_in_1_status` | `bank_N_name` | `bank_N_ifsc_code` | `bank_N_account_type` | `pis_bank_N_name` | `pis_bank_N_ifsc_code` | `nominee_N_first_name` | `nominee_N_last_name` | `nominee_N_percentage_of_shares` | `primary_dp_status` | `primary_dp_activation_date` | `primary_dp_joint_account` | `primary_ddpi_flag` | `primary_ddpi_agreement_date` | `poa_consent` | all `*_status` and `*_remarks` fields | `zbl_mcx_status`

**Internal-only fields** (use for reasoning; communicate outcomes in plain language):

`owner` | `modified_by` | `broker_code` | `support_code` | `support_code_masked` | `email_masked` | `mobile_masked` | `primary_dp_id` | `primary_dp_account_no` | `secondary_dp_id` | `secondary_dp_account_no` | `tertiary_dp_id` | `tertiary_dp_account_no` | all `*_soft_enable` fields | `bank_N_account_number` (raw) | `bank_N_micr_code` | `bank_N_poa` | `pis_bank_N_account_number` | `pis_bank_N_micr_code` | `docstatus` | `idx` | `doctype` | `creation` | `modified` | `acc_open_flag` | `eq_sign` | `eq_signed_on` | `comm_sign` | `comm_signed_on` | `tags` | `holdings_as_on_date` | `poa_details` | `address_details` | `bank_details` | `dp_details` | `segment_details` | `client_documents` | `uid_meta` | `custodial_participant_code` | `cp_code` | `third_party_demat`

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

| Raw Status | Meaning |
|---|---|
| Activated | Active. Note `*_update_on` timestamp for downstream tools. |
| Segment Not Active | Not activated. |
| Dormant | No trading in 24+ months — requires ReKYC. Route via Preflight Step 4. |
| Pending | Activation in progress. Note approval status in `account_modification_report` and `*_update_on` timestamp for downstream tools. |
| Activation Pending | Same as Pending. |
| Activation Rejected | Collect status and route to downstream tool. |
| Blocked | Collect status and route to downstream tool. |
| Inactivated | Disabled by Zerodha. |

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

---

### A7 — Account Type Flags

| Flag | Note |
|---|---|
| Joint (`primary_dp_joint_account` = "YES") | Pass joint status to downstream tools. |
| Minor (`bo_sub_status` contains "Minor") | Pass minor status to downstream tools. |
| Non-Individual (`category` = "Non-Individual") | Pass non-individual status to downstream tools. |
| Orbis (`custodial_participant_code` NOT None OR `cp_code` NOT None) | Route all queries to Orbis team per Rule 4. |

---

### A8 — Key Account Flags

| Field | Meaning |
|---|---|
| `zbl_mcx_status` = Active | Single ledger MCX account. Pass to downstream tools for timeline logic. |
| `idfc_3_in_1_status` = Yes | IDFC 3-in-1 account active. |
| `rekyc_flag` = True | ReKYC completed; `rekyc_date` = date of completion. |

---

### A9 — Client ID Field

The `name` field in the tool response is the client's unique Client ID (e.g., "XX0000"). Store this value and pass it to any downstream tool that requires a client ID (e.g., `stock_gift_requests` fields like `gifted_by`, `claimed_by`, `client_id`).

---

## Section B: Decision Flow

---

### Preflight (run on every query)

```
1. Check `account_blocks`
   └─ Non-empty → ESCALATE TO SM: "[value]". STOP.

2. Resolve account type (per A3)
   ├─ If `client_acc_type` = "NRI" → resolve NRE/NRO via `bo_sub_status` → PIS via `pis_bank_*`
   └─ Note applicable flags/restrictions (per A7)

3. Check Orbis (partner-managed account)
   └─ If `custodial_participant_code` OR `cp_code` has any value → account is managed
      by a partner broker (Orbis). ESCALATE per Rule 4. STOP.

3a. Check third-party demat
    └─ If `third_party_demat` = true → ESCALATE TO SM: third-party demat mapped;
       support manager review needed. STOP.

4. Check dormancy
   └─ `nse_eq_status` OR `bse_eq_status` OR any segment = "Dormant"
      → collect dormancy details and route to `account_modification_report`

5. Store Client ID from `name` field (per A9)
```

### Route

```
Intent / Condition                            → Action
────────────────────────────────────────────────────────
Segment status query                          → Rule 1 → route to `account_modification_report`
PAN / Name / DOB mismatch                     → Rule 2 → route to `pan_status`
DDPI / POA / TPIN query                       → Rule 3 → route to `account_modification_report`
Nominee query                                 → route to `account_modification_report`
Request for email / mobile / contact info     → route to `account_modification_report`
Any field from internal-only list requested   → route to `account_modification_report`
BSDA query                                   → route to `amc_charges`
Orbis account — any support query             → Rule 4
```

### Scope

- Collect and interpret client data; route to the appropriate downstream tool for resolution.

### Fallback

If the query does not match any route above, interpret the tool response using the reference data in Section A and general knowledge of the account structure. If no root cause is found, acknowledge the question and escalate if appropriate.

---

## Section C: Rules

---

### Rule 1 — Segment Status Interpretation

1. Identify the segment via **A6**.
2. Read `[segment]_status` and interpret per **A5**.
3. If `*_soft_enable` = 0, the client has disabled this segment (kill switch ON per **A5**).
4. Collect the segment status, `*_update_on` timestamp, and kill switch state.
5. Route to `account_modification_report` for resolution.

---

### Rule 2 — PAN / Name / DOB Mismatch

1. Extract `pan`, `client_name`, `dob` from the tool response.
2. Route to `pan_status` tool with those fields for validation and resolution.

---

### Rule 3 — DDPI / POA Status

1. Collect `primary_ddpi_flag`, `poa_consent`, `primary_poa_for_securities`.
2. Note account type and online DDPI eligibility: Individual account + Aadhaar-linked mobile number. Not eligible: Joint, Non-Individual, Orbis NRI.
3. Route to `account_modification_report` for resolution.

---

### Rule 4 — Orbis Partner-Managed Account

1. If `custodial_participant_code` OR `cp_code` has any value (e.g., "ORBIS0009164"), the account is managed by a partner broker (Orbis).
2. For any support query — including fund withdrawal, payin, account transfer, delayed payment charges, or any other account servicing request → **ESCALATE** — route to Orbis partner team for handling.
