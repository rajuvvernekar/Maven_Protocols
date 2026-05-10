# pan_status

## Description

WHEN TO USE:

When clients:
- Report account blocked due to name mismatch or PAN verification failure
- Report segment activation rejected with "PAN Verification Failed" remark
- Report "name and/or date of birth do not match income tax database" error
- Ask how to update name/DOB to match PAN
- Report DOB/Name mismatch flagged on account modification
- Report single ledger activation error due to name/DOB mismatch
- Report minor account opening fails with "PAN verification failed" (for the minor's PAN)

TRIGGER KEYWORDS: "PAN verification failed", "name mismatch", "DOB mismatch", "name not matching", "income tax database", "ITD mismatch", "change name", "update name", "PAN blocked", "PAN invalid", "segment rejected name"

PREREQUISITE: Always run get_all_client_data FIRST to obtain client_name, pan, dob before checking pan_status.

TAGS: account

## Protocol

# PAN STATUS PROTOCOL

---

## Section A: Reference Data

### A1 — Fundamentals

-PAN verification checks name/DOB validity across ITD, Exchange, Depository, and KRA. All intermediary records must match for trading — SEBI requirement.

-Zerodha's name record is sourced from ITD, not from submitted documents — the two may differ. Name/DOB mismatch blocks transactions until resolved.

- **pan_status inputs:** `client_name`, `pan`, `dob` — must be sourced from `get_all_client_data`. The client's self-reported name must not be used as input; the client may reference an updated name not yet reflected in Zerodha's system.

---

### A2 — Field Usage Rules

**Non-shareable:**

| Field | Interpretation |
|---|---|
| `pan_valid_status` | PAN validation result from IT department records — use to determine if PAN is valid |
| `name_match` | Whether the name on PAN matches KYC records |
| `dob_match` | Whether the date of birth on PAN matches KYC records |
| `aadhaar_pan_seeding` | Whether Aadhaar is linked with PAN in IT department records |

---

### A3 — PAN Validity Status

| Value | Meaning |
|---|---|
| E | The PAN is valid. |
| Any other value | The PAN is invalid, deactivated, or blocked for regulatory reasons. |

---

### A4 — Name and DOB Status

| Value | Meaning |
|---|---|
| Y | The entered name and DOB match the ITD records. |
| N | The entered name and DOB do not match the ITD records. |

---

### A5 — Aadhaar-PAN Seeding Status

| Value | Meaning |
|---|---|
| Y | The PAN is linked to Aadhaar. |
| R or N | The PAN is not linked to Aadhaar. |
| NA | Applicable for non-individuals and clients in the exempt category. (NRIs, not a citizen of India, age > 80 years as of date, state of residence is Assam, Meghalaya or Jammu & Kashmir.) |

---

### A6 — Name Change Categories & Process

| Category | Online | Offline |
|---|---|---|
| Spelling correction, interchange, middle name, initials | Yes | Yes |
| Father's / mother's name change | Yes | Yes |
| Marriage / divorce name change | No | Yes |
| Personal preference | No | Yes |
| Removing middle / last name | No | Yes |

**Online process:** Re-KYC [A7 — Re-KYC] [A7 — Name change process] (requires Aadhaar linked to mobile number).

**Offline process:** Courier documents to Zerodha. Charges: ₹25 + GST. Updated within 72 working hours. Resolution may take up to 7 working days after documents received. [A7 — Name change process] [A7 — Courier address]

---

### A7 — Links

| Topic | URL / Reference |
|---|---|
| Re-KYC (online fix) | https://support.zerodha.com/category/your-zerodha-account/account-modification-and-segment-addition/account-modification/articles/how-do-i-change-the-registered-address-on-my-account-online |
| ITD portal (verify name/DOB) | incometax.gov.in |
| Name change process | https://support.zerodha.com/category/your-zerodha-account/your-profile/general-profile-questions/articles/why-is-the-name-on-my-zerodha-account-different-than-on-the-documents-i-ve-submitted |

**Courier address:** Zerodha Customer Support Centre, 192A 4th Floor, Kalyani Vista, 3rd Main Road, JP Nagar 4th Phase, Bengaluru, 560076

---

### A8 — Escalation Data

-Include when escalating to human agent: **client ID**, **PAN**, **specific issue** (e.g., invalid PAN, persistent name/DOB mismatch).

---

### A9 — Scenarios & Interpretations

| Scenario | Interpretation |
|---|---|
| S1 — PAN invalid | PAN is invalid, deactivated, or blocked. |
| S2 — Name and/or DOB mismatch (ITD not yet updated) | Records mismatch between ITD, Exchange, and Depository. Client must first update ITD, then update Zerodha records before transactions can proceed. |
| S3 — All clear | PAN verification successful. Name and DOB match ITD records. No action needed. |
| S4 — Minor PAN verification failed | Minor's PAN or DOB does not match ITD records. Client should verify details on ITD portal and retry. |
| S5 — Name mismatch, ITD already updated | Zerodha records still reflect the earlier name. Client must update Zerodha records via online (re-KYC) or offline process. |

---

---

## Section B: Decision Flow

### Routing

```
Route by scenario
├─ PAN validity ≠ "E" (invalid / deactivated / blocked) → Rule 1
├─ Name match = "N" OR DOB match = "N" → Rule 2
├─ Name match = "Y" AND DOB match = "Y" AND PAN valid = "E" → Rule 3
├─ Minor account — PAN verification failed → Rule 4
└─ Single ledger activation error (name/DOB mismatch) → Rule 5
```

### Fallback

If no rule matches, check `get_all_client_data` for other account remarks or blocks, If `account_blocks` is non-empty, escalate to human agent per A8.

---

## Section C: Rules

### Rule 1 — PAN Invalid

1. PAN validity ≠ "E" (per A3).
2. Escalate to human agent per A8.

---

### Rule 2 — Name and/or DOB Mismatch

1. Name match = "N" OR DOB match = "N" (per A4).
2. If client states their name has already been updated at ITD:
   - Direct client to update Zerodha records via online or offline process per A6. Links per A7.
3. If client has not yet updated at ITD:
   - Direct client to first update ITD via [A7 — ITD portal], then update Zerodha records per A6. Links per A7.

---

### Rule 3 — Name and DOB Both Match

1. Name match = "Y" AND DOB match = "Y" AND PAN valid = "E" (per A3, A4).
2. If client still faces issues after all-clear (e.g., segment rejection, account block):
   - Check `get_all_client_data` for other remarks or blocks on the account.
   - If no root cause found, escalate to human agent per A8.

---

### Rule 4 — Minor Account PAN Verification Failed

1. Query is about minor account opening with PAN verification failure.
2. Direct client to verify the minor's PAN and DOB on [A7 — ITD portal] and retry. If the PAN was recently issued, advise it may take a few days to reflect in the ITD database.

---

### Rule 5 — Single Ledger Activation Error

1. Client reports "name and/or date of birth do not match" error during single ledger activation.
2. Apply Rule 2 in full. The name/DOB mismatch must be resolved before single ledger activation can proceed.
