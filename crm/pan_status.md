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

- PAN verification checks name/DOB validity across ITD, Exchange, Depository, and KRA. All intermediary records must match for trading — SEBI requirement.

- Zerodha's name record is sourced from ITD, not from submitted documents — the two may differ. Name/DOB mismatch blocks transactions until resolved.

- **pan_status inputs:** `client_name`, `pan`, `dob` — must be sourced from `get_all_client_data`. The client's self-reported name must not be used as input; the client may reference an updated name not yet reflected in Zerodha's system.

---

### A2 — Field Usage Rules

**Non-shareable:**

| Field | Interpretation |
|---|---|
| `pan_status` | PAN validation result from ITD records — use to determine if PAN is valid (per A3) |
| `name_status` | Whether the name matches ITD records (per A4) |
| `dob_status` | Whether the DOB matches ITD records (per A4) |
| `seeding_status` | Whether Aadhaar is linked with PAN in ITD records (per A5) |

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

**Online process:** Re-KYC via [A7 — Name change / Re-KYC process] (requires Aadhaar linked to mobile number).

**Offline process:** Courier documents to Zerodha. Charges: ₹25 + GST. Updated within 72 working hours. Resolution may take up to 7 working days after documents received. [A7 — Name change / Re-KYC process] [A7 — Courier address]

---

### A7 — Links

| Topic | URL / Reference |
|---|---|
| Name change / Re-KYC process (online + offline) | https://support.zerodha.com/category/your-zerodha-account/your-profile/general-profile-questions/articles/why-is-the-name-on-my-zerodha-account-different-than-on-the-documents-i-ve-submitted |
| Update name / details on PAN at ITD (incl. DOB) | https://tradingqna.com/t/how-do-i-update-and-correct-my-name-and-other-details-on-pan-card/146151 |
| ITD portal (verify name/DOB) | https://www.incometax.gov.in/iec/foportal/ |
| Aadhaar–PAN linking | https://support.zerodha.com/category/account-opening/resident-individual/ri-online/articles/i-have-not-linked-my-pan-with-my-aadhaar |
| Update DOB at Zerodha | https://support.zerodha.com/category/your-zerodha-account/account-modification-and-segment-addition/account-modification/articles/update-dob-gender-pep-marital-status-occupation |

**Courier address:** Zerodha Customer Support Centre, 192A 4th Floor, Kalyani Vista, 3rd Main Road, JP Nagar 4th Phase, Bengaluru, 560076

### A8 — Scenarios & Interpretations

| Scenario | Interpretation |
|---|---|
| S1 — PAN invalid | PAN is invalid, deactivated, or blocked. |
| S2 — Name and/or DOB mismatch (ITD not yet updated) | Records mismatch between ITD, Exchange, and Depository. Client must first update ITD, then update Zerodha records before transactions can proceed. |
| S3 — All clear | PAN verification successful. Name and DOB match ITD records. No action needed. |
| S4 — Minor PAN verification failed | Minor's PAN or DOB does not match ITD records. Client should verify details on ITD portal and retry. |
| S5 — Name mismatch, ITD already updated | Zerodha records still reflect the earlier name. Client must update Zerodha records via online (re-KYC) or offline process. |

---

## Section B: Decision Flow

### Routing

```
Route by scenario
├─ pan_status ≠ "E" (invalid / deactivated / blocked) → Rule 1
├─ seeding_status = "R" or "N" (Aadhaar–PAN not linked) → Rule 6
├─ name_status = "N" OR dob_status = "N" → Rule 2
├─ name_status = "Y" AND dob_status = "Y" AND pan_status = "E" → Rule 3
├─ Minor account — PAN verification failed → Rule 4
├─ Single ledger activation error (name/DOB mismatch) → Rule 5
└─ Segment rejected with "PAN Verification Failed" → diagnose the name/DOB mismatch via Rule 2 (segment re-activation itself follows the segment-activation protocol)
```

### Fallback

If no rule matches, check `get_all_client_data` for other account remarks or blocks. If `account_blocks` is non-empty, escalate.

---

## Section C: Rules

### Rule 1 — PAN Invalid

1. `pan_status` ≠ "E" (per A3).
2. escalate.

---

### Rule 2 — Name and/or DOB Mismatch

1. `name_status` = "N" or `dob_status` = "N" (per A4) — Zerodha's record differs from current ITD records (A8-S2 / A8-S5).

**Name mismatch (`name_status` = N):**
2. ITD already reflects the new name → direct client to update Zerodha to match ITD (A8-S5). Online (re-KYC) only for A6 online-eligible categories; all others are offline only (per A6). Online additionally needs Aadhaar linked to the registered mobile for OTP — `seeding_status` = Y confirms only Aadhaar–PAN linkage, not Aadhaar–mobile.
3. ITD not yet updated → client updates the name at ITD first ([A7 — Update name / details on PAN at ITD]; verify on [A7 — ITD portal]), then updates Zerodha per step 2.

**DOB mismatch (`dob_status` = N):**
4. A DOB mismatch is a data-entry error on one side — identify which record is wrong:
   - Zerodha DOB wrong (ITD correct) → client updates the DOB at Zerodha to match ITD ([A7 — Update DOB at Zerodha]).
   - ITD DOB wrong → client corrects DOB at ITD first ([A7 — Update name / details on PAN at ITD]; verify on [A7 — ITD portal]), then updates Zerodha.
5. Repeated re-KYC will not resolve the mismatch until the underlying record is corrected — advise the client to stop re-submitting and fix the mismatch first.

---

### Rule 3 — Name and DOB Both Match

1. `name_status` = "Y" AND `dob_status` = "Y" AND `pan_status` = "E" (per A3, A4) — A8-S3.
2. If the client is requesting a name/DOB update but status is already "Y": Zerodha already matches current ITD. Either the change is already reflected (compare `client_name`/`dob` from `get_all_client_data` with what the client expects — if it matches, no action needed) or the ITD change has not yet propagated. Do not initiate the A6 name-change process while status = "Y".
   - If the client wants a name change and ITD has not yet been updated: share [A7 — Update name / details on PAN at ITD] and explain they must update ITD first. Once ITD propagates the change, `name_status` will flip to "N" — they should contact support again at that point, and Rule 2 will apply.
3. If client still faces issues after all-clear (e.g., segment rejection, account block):
   - Check `get_all_client_data` for other remarks or blocks on the account.
   - If no root cause found, escalate.

---

### Rule 4 — Minor Account PAN Verification Failed

1. Query is about minor account opening with PAN verification failure.
2. Direct client to verify the minor's PAN and DOB on [A7 — ITD portal] and retry. If the PAN was recently issued, advise it may take a few days to reflect in the ITD database.

---

### Rule 5 — Single Ledger Activation Error

1. Client reports "name and/or date of birth do not match" error during single ledger activation.
2. Apply Rule 2 in full. The name/DOB mismatch must be resolved before single ledger activation can proceed.

---

### Rule 6 — Aadhaar–PAN Not Linked

1. `seeding_status` = "R" or "N" (per A5) — Aadhaar is not linked with PAN; the PAN is inoperative and blocks transactions.
2. `seeding_status` = "NA" → exempt category (per A5); no linking required.
3. Direct the client to link Aadhaar with PAN — see [A7 — Aadhaar–PAN linking] (linking is done on the ITD portal, [A7 — ITD portal]); once linked, re-verify PAN status.
