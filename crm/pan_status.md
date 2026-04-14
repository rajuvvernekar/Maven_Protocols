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

## Protocol

---

## Section A: Reference Data

---

### A1 — Tool Purpose & Fundamentals

This tool checks **PAN verification status** — validity + name/DOB match across ITD, Exchange, Depository, and KRA. All intermediary records must match for trading — this is a SEBI requirement.

Zerodha's name record is sourced from ITD, not from submitted documents — the two may differ. Name/DOB mismatch blocks transactions until resolved.

**Input:** Client's PAN, name, and DOB (from `get_all_client_data` — see Preflight Step 1 for why).

---

### A2 — Field Usage Rules

**Shareable fields:** None — all fields are for reference only.

**Internal-only fields** (use for reasoning; communicate outcomes in plain language):

All raw field values: `pan_valid_status` | `name_match` | `dob_match` | `aadhaar_pan_seeding`

All raw values are for internal decision-making only. Communicate the outcome and resolution steps, not the field values or status codes.

---

### A3 — PAN Validity Status

| Value | Meaning | Action |
|---|---|---|
| E | Valid | Proceed to check name/DOB match |
| Any other value | Invalid / deactivated / blocked | Escalate immediately |

---

### A4 — Name / DOB Match Status

| Value | Meaning |
|---|---|
| Y | Matches ITD records |
| N | Mismatch — resolution required |

---

### A5 — Aadhaar-PAN Seeding Status

| Value | Meaning |
|---|---|
| Y | Linked |
| R or N | Not linked |
| NA | Exempt (NRI, non-citizen, age > 80, Assam/Meghalaya/J&K resident) |

All routing and action decisions in this protocol are driven by PAN validity (**A3**) and Name/DOB match (**A4**). Aadhaar-PAN seeding status is retained as informational context only.

---

### A6 — Name Change Categories & Process

| Category | Online | Offline |
|---|---|---|
| Spelling correction, interchange, middle name, initials | Yes | Yes |
| Father's / mother's name change | Yes | Yes |
| Marriage / divorce name change | No | Yes |
| Personal preference | No | Yes |
| Removing middle / last name | No | Yes |

**Online fix:** Re-KYC at account.zerodha.com (requires Aadhaar linked to mobile).

**Offline fix:** Courier documents to Zerodha. Charges: ₹25 + GST. Updated within 72 working hours. Resolution may take up to 7 working days after documents received.

---

### A7 — Links

| Topic | URL / Reference |
|---|---|
| Re-KYC (online fix) | account.zerodha.com |
| ITD portal (verify name/DOB) | incometax.gov.in |
| Name change process | How to change the name in my Zerodha account? |

**Courier address:** Zerodha Customer Support Centre, 192A 4th Floor, Kalyani Vista, 3rd Main Road, JP Nagar 4th Phase, Bengaluru, 560076

---

### A8 — Escalation Data Template

When escalating, always include: **client ID, PAN, and specific issue (invalid PAN, persistent mismatch, etc.).**

---

### A9 — Response Templates

**R1 — PAN invalid (not "E"):**
"There appears to be a regulatory issue with your PAN. Our team will investigate and get back to you."

**R2 — Name and/or DOB mismatch:**
"As per regulations, the name and date of birth on the Income Tax Department (ITD), Exchange, and Depository records must match to carry out transactions. Your records currently show a mismatch.

To resolve this:
1. Check your name and DOB as per ITD by logging into the Income Tax Department portal at incometax.gov.in
2. Check your name as per Zerodha records by downloading the CMR copy from Console
3. If your name needs to be updated, first update it with the ITD, then follow the name change process — visit: How to change the name in my Zerodha account?

For an online fix, visit account.zerodha.com and complete the re-KYC process (Aadhaar must be linked to your mobile number).

Please note: It may take up to 7 working days after documents are received for the update to take effect. Transactions will be enabled once records are updated."

**R3 — All clear:**
"Your PAN verification is successful — your name and date of birth match the Income Tax Department records."

**R4 — Minor PAN verification failed:**
"The minor's PAN verification has failed. This means the PAN number or date of birth entered does not match the Income Tax Department records. Please verify the minor's PAN details and date of birth on the ITD portal at incometax.gov.in, and retry. If the PAN was recently issued, it may take a few days to reflect in the ITD database."

**R5 — Name mismatch, client states ITD already updated:**
"Your Zerodha records still reflect the earlier name. To update your name with Zerodha:

**Online:** Visit account.zerodha.com and complete the re-KYC process (Aadhaar must be linked to your mobile number). This is available for: spelling corrections, interchange of names, middle name or initial changes, and father's/mother's name changes.

**Offline:** For marriage/divorce name changes, personal preference changes, or removing a middle/last name — courier the required documents to Zerodha. Charges: ₹25 + GST. Processing time: up to 7 working days after documents are received.

Courier address: Zerodha Customer Support Centre, 192A 4th Floor, Kalyani Vista, 3rd Main Road, JP Nagar 4th Phase, Bengaluru, 560076

For details on the process and documents required, visit: How to change the name in my Zerodha account?"

---

---

## Section B: Decision Flow

---

### Preflight (run on every query)

```
1. Retrieve client_name, pan, dob from get_all_client_data.
   These represent Zerodha's current registered records.
   Use these values as PAN status input — not the name the client
   provides in their query, which may be a different (updated) name.
   The purpose of PAN status is to check Zerodha's registered name
   against ITD for mismatch detection.

2. Call pan_status with those fields.

3. Check PAN validity (per A3):
   └─ Not "E" → respond per A9-R1. Escalate to support agent per A8. STOP.
```

### Route

```
Intent / Condition                                          → Rule
──────────────────────────────────────────────────────────────────────
Name and/or DOB mismatch                                    → Rule 1
Name and DOB both match + PAN valid                         → Rule 2
Minor account PAN verification failed                       → Rule 3
Single ledger activation error (name/DOB mismatch)          → Rule 4
```

### Scope

- Address the client's PAN verification status, name/DOB mismatch resolution, and related activation errors.
- Use **A2** field rules — all fields are internal-only. Communicate outcomes and resolution steps only.
- Do not share specific PAN status codes or raw field values with the client.

### Fallback

If the client still faces issues despite all-clear PAN status, check `get_all_client_data` for other remarks or blocks. If no root cause found, escalate per **A8**.

---

## Section C: Rules

---

### Rule 1 — Name and/or DOB Mismatch

1. Name match = "N" OR DOB match = "N".
2. If the client has explicitly stated that their name has already been updated at ITD, respond per **A9-R5**. Name change categories per **A6**, links per **A7**.
3. Otherwise, respond per **A9-R2**. Name change options per **A6**. Links per **A7**.

---

### Rule 2 — Name and DOB Both Match

1. Name match = "Y" AND DOB match = "Y" AND PAN valid = "E".
2. Respond per **A9-R3**.
3. If client still faces issues (segment rejection, block) → check `get_all_client_data` for other remarks or blocks.

---

### Rule 3 — Minor Account PAN Verification Failed

1. Query is about minor account opening + PAN verification failed.
2. Respond per **A9-R4**.

---

### Rule 4 — Single Ledger Activation Error

1. Client reports "name and/or date of birth do not match" error during single ledger activation.
2. Apply Rule 1 (**A9-R2** or **A9-R5** depending on client context). The mismatch must be resolved before single ledger can be enabled.
