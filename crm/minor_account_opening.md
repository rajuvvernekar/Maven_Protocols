# minor_account_opening

## Description

WHEN TO USE:

When clients:
- Ask about minor account opening application status
- Report application rejected or stuck in processing
- Haven't received login credentials after account opening
- Report PAN verification failure during minor account opening
- Ask what documents are needed for minor account

TRIGGER KEYWORDS: "minor account status", "minor account opening", "minor demat", "child account", "minor application", "minor rejected", "minor login credentials", "minor PAN failed", "esign minor", "minor account processing"

## Protocol

# MINOR ACCOUNT OPENING PROTOCOL 

---

## Section A: Reference Data

---

### A1 — Tool Purpose & Fundamentals

This tool shows **minor account opening application status**. It tracks the application through processing to completion.

For questions about trading restrictions, fund transfers, MF investment, guardian changes, converting to individual account, or Kite login for pre-2024 accounts — answer from the reference data in this protocol, not from tool output.

**Input:** Client ID (guardian's).

---

### A2 — Field Usage Rules

**Shareable fields:**

`reasons` (communicate in customer-friendly language)

**Internal-only fields** (use for reasoning; communicate outcomes in plain language):

`status` | `form_type` | `eq_signed_on` | `minor_client_id` | `full_name` | `client_id` | `creation` | `modified`

---

### A3 — Status Values

| Status | Meaning | Action |
|---|---|---|
| Processing | Under review | If ≤48 working hours + no reasons → inform client to wait. If reasons present → share rejection reasons. If >48 working hours + no reasons → escalate. |
| Completed | Approved | Account enabled within 24–48 hours. Credentials sent to registered email. |

---

### A4 — Timelines

| Event | Timeline |
|---|---|
| Online account opening | 48 working hours |
| Offline account opening | 72 working hours after documents received at Bengaluru office |
| Kite access for pre-Jan 2024 demat-only accounts | 72 working hours after trading form received |
| Account enabled after approval | 24–48 hours |

---

### A5 — Trading Restrictions

| Allowed | Not Allowed |
|---|---|
| Sell existing holdings | Buy shares |
| Buy mutual funds (Coin) | Government securities |
| Apply for IPOs, buybacks, takeovers | Intraday trading |
| | F&O |
| | OFS |

Guardian can transfer securities to minor's account using CDSL Easiest or Zerodha's gifting feature.

---

### A6 — Account Opening Requirements

**Online:** Guardian needs Zerodha account + both guardian and minor Aadhaar linked to mobile. No charges or AMC.

**Documents (online):** Minor PAN | Guardian PAN | Minor Aadhaar (OTP) | DOB proof | Minor photo | Bank proof | Guardian signature | Legal guardian letter (if not parent).

**PAN:** Mandatory for minor — apply at onlineservices.nsdl.com if needed.

**Bank account:** Only the minor's bank account can be linked (not guardian's). Joint bank account is OK only if minor is a holder.

**Guardian:** Signs all forms. Unique mobile + email required per minor account (offline).

**NRI-minor:** Offline only.

**When minor turns 18:** Convert to individual account (fresh KYC required).

**Pre-Jan 2024 demat-only accounts:** Submit trading form + KYC for Kite access (72 working hours).

---

### A7 — Common Rejection Reason Translations

| System Reason | Client-Friendly Response |
|---|---|
| Bank proof invalid/unclear | "Please provide a clear copy of the minor's cancelled cheque, bank statement, or passbook" |
| DOB proof missing/invalid | "Please upload a valid date of birth proof (birth certificate, school leaving certificate, passport, or marksheet)" |
| eSign pending/failed | "The guardian's eSign is pending. Please complete the eSign to proceed" |
| IPV pending | "In-Person Verification is pending. Both guardian and minor must complete IPV at signup.zerodha.com/ipv" |
| PAN verification failed | "The minor's PAN verification failed. Please verify the PAN number and date of birth match the Income Tax Department records" |

---

### A8 — Links

| Topic | URL |
|---|---|
| Online minor account signup | signup.zerodha.com/minor |
| In-Person Verification (IPV) | signup.zerodha.com/ipv |
| Offline document email | forms@zerodha.com |

**Courier address:** Zerodha Customer Support Centre, 192A 4th Floor, Kalyani Vista, 3rd Main Road, JP Nagar 4th Phase, Bengaluru, 560076

---

### A9 — Escalation Data Template

When escalating, always include: **client ID (guardian's), minor's name/details, application date, and specific issue.**

---

### A10 — Response Templates

**R1 — Processing (within timeline, no reasons):**
"Your minor account application is being reviewed. It typically takes up to 48 working hours for the account to be processed after document verification."

**R2 — Processing (reasons present):**
"Your minor account application requires corrections. [Share reasons per A7 translations]. Please make the necessary changes and resubmit."

**R3 — Processing (overdue):**
"Your application has been under review for longer than expected. I'm escalating this to our team for priority processing."

**R4 — Completed:**
"Your minor account application has been approved. The account will be enabled within 24–48 hours, and login credentials will be sent to the registered email ID."

**R5 — Credentials not received:**
"Please check your registered email (including spam/junk folder). If credentials haven't arrived within 48 hours of approval, please let us know."

**R6 — eSign not completed:**
"It appears the guardian's eSign has not been completed yet. Please complete the eSign process to proceed with the application. You can do this during the account opening flow at signup.zerodha.com/minor."

**R7 — PAN verification failed:**
"The minor's PAN could not be verified. This means either the PAN number or date of birth entered does not match the Income Tax Department (ITD) records. Please verify the details at incometax.gov.in. If the PAN was recently issued, it may take a few days to reflect in the ITD database."

**R8 — NRI-minor account:**
"NRI-minor accounts can only be opened offline. Please email the required documents to forms@zerodha.com for review, then courier them to our Bengaluru office. The account will be opened within 72 working hours after document verification."

**R9 — Trading capabilities:**
"Minor accounts have specific restrictions as per SEBI regulations. Minors cannot buy shares or place intraday/F&O orders. However, minors can sell existing holdings, invest in mutual funds through Coin, and apply for IPOs, buybacks, and takeovers. The guardian can transfer securities to the minor's account using CDSL Easiest or Zerodha's gifting feature."

---

## Section B: Decision Flow

---

### Preflight (run on every query)

```
1. Determine if query is about application status OR general minor account info
   ├─ Application status → use tool data, route to Rules below
   └─ General info (trading restrictions, fund transfers, MF, guardian change,
      converting to individual, Kite login for pre-2024 accounts)
      → answer from Section A reference data directly
```

### Route

```
Intent / Condition                                          → Rule
──────────────────────────────────────────────────────────────────────
Application status (processing, within timeline)            → Rule 1
Application rejected / corrections needed                   → Rule 2
Application overdue                                         → Rule 3
Application completed                                       → Rule 4
eSign not completed                                         → Rule 5
PAN verification failed during opening                      → Rule 6
NRI-minor account opening                                   → Rule 7
Trading capabilities / restrictions                         → Rule 8
```

### Scope

- Address the client's query about minor account opening applications and general minor account information.
- Use **A2** field rules in all client communication — only `reasons` is shareable (in friendly language). All other fields are for internal reasoning.
- For general minor account questions, answer from **A5**, **A6**, and other Section A blocks.

### Fallback

If no route matches, answer from Section A reference data. If unable to resolve, escalate per **A9**.

---

## Section C: Rules

---

### Rule 1 — Application Processing (Within Timeline)

1. `status` = "processing" AND `creation` ≤ 48 working hours AND `reasons` is empty/null.
2. Respond per **A10-R1**. Timeline per **A4**.

---

### Rule 2 — Application Rejected / Reasons Present

1. `status` = "processing" AND `reasons` is not empty.
2. Translate reasons per **A7** and respond per **A10-R2**.

---

### Rule 3 — Application Overdue

1. `status` = "processing" AND `creation` > 48 working hours AND `reasons` is empty/null.
2. Respond per **A10-R3**. Escalate per **A9**.

---

### Rule 4 — Application Completed

1. `status` = "completed".
2. Respond per **A10-R4**. Timeline per **A4**.
3. If client says credentials not received → respond per **A10-R5**.

---

### Rule 5 — eSign Not Completed

1. `status` = "processing" AND `eq_signed_on` is empty/null.
2. Respond per **A10-R6**.

---

### Rule 6 — PAN Verification Failed

1. Respond per **A10-R7**.

---

### Rule 7 — NRI-Minor Account

1. Respond per **A10-R8**. Courier address per **A8**.

---

### Rule 8 — Trading Capabilities / Restrictions

1. Respond per **A10-R9**. Full restrictions per **A5**.

---

## Section D: General Notes

- Online minor account opening requires guardian's Zerodha account + both Aadhaar linked to mobile. No charges or AMC.
- PAN is mandatory for minor — apply at onlineservices.nsdl.com if needed.
- Only the minor's bank account can be linked (not guardian's). Joint bank account OK only if minor is a holder.
- Guardian signs all forms. Unique mobile + email required per minor account (offline).
- NRI-minor accounts: offline only.
- Login credentials sent to registered email after account enabled at exchanges.
- Pre-Jan 2024 demat-only accounts need trading form + KYC for Kite access (72 working hours).
- When minor turns 18: convert to individual account (fresh KYC required).
- Minors cannot buy shares, trade intraday, or use F&O. Can sell holdings, buy MF, apply for IPOs/buybacks/takeovers.
