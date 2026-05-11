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

TAGS: account

## Protocol

# MINOR ACCOUNT OPENING PROTOCOL

---

## Section A: Reference Data

### A1 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |
|---|---|
| `reasons` | Communicate in customer-friendly language per A6 — do not share raw values |

**Non-shareable:**

| Field | Interpretation |
|---|---|
| `status` | Application status — interpret per A2 |
| `form_type` | Type of application form |
| `eq_signed_on` | Timestamp of guardian's eSign; empty/null = eSign not completed |
| `minor_client_id` | Minor's internal client ID |
| `full_name` | Minor's full name |
| `client_id` | Guardian's client ID |
| `creation` | Application submission timestamp — used to calculate elapsed processing time per A3 |
| `modified` | Last update timestamp |

---

### A2 — Status Values

| Status | Meaning |
|---|---|
| Processing | Application under review |
| Completed | Application approved |

---

### A3 — Timelines

| Event | Timeline |
|---|---|
| Online account opening | 48 working hours |
| Offline account opening | 72 working hours after documents received at Bengaluru office |
| Kite access for pre-Jan 2024 demat-only accounts | 72 working hours after trading form received |
| Account enabled after approval | 24–48 hours |

---

### A4 — Trading Restrictions

| Allowed | Not Allowed |
|---|---|
| Sell existing holdings | Buy shares |
| Buy mutual funds (Coin) | Government securities |
| Apply for IPOs, buybacks, takeovers | Intraday trading |
| | F&O |
| | OFS |

Guardian can transfer securities to minor's account using CDSL Easiest or Zerodha's gifting feature.

---

### A5 — Account Opening Requirements

- **Online:** Guardian needs Zerodha account + both guardian and minor Aadhaar linked to mobile. No charges or AMC.
- **Documents (online):** Minor PAN | Guardian PAN | Minor Aadhaar (OTP) | DOB proof | Minor photo | Bank proof | Guardian signature | Legal guardian letter (if not parent).
- **PAN:** Mandatory for minor — apply at onlineservices.nsdl.com if needed.
- **Bank account:** Only the minor's bank account can be linked (not guardian's). Joint bank account is OK only if minor is a holder.
- **Guardian:** Signs all forms. Unique mobile + email required per minor account (offline).
- **NRI-minor:** Offline only.
- **When minor turns 18:** Convert to individual account (fresh KYC required).
- **Pre-Jan 2024 demat-only accounts:** Submit trading form + KYC for Kite access (72 working hours).

---

### A6 — Common Rejection Reason Meanings

| System Reason | Meaning |
|---|---|
| Bank proof invalid/unclear | Bank document is missing, unclear, or not accepted |
| DOB proof missing/invalid | Date of birth document is absent or invalid |
| eSign pending/failed | Guardian's eSign is incomplete or failed |
| IPV pending | In-Person Verification not yet completed by guardian and/or minor |
| PAN verification failed | Minor's PAN or date of birth doesn't match ITD records |

---

### A7 — Links

| Topic | URL |
|---|---|
| Online minor account signup | signup.zerodha.com/minor |
| In-Person Verification (IPV) | signup.zerodha.com/ipv |
| Offline document email | forms@zerodha.com |
| ITD portal (PAN / DOB verification) | incometax.gov.in |

**Courier address:** Zerodha Customer Support Centre, 192A 4th Floor, Kalyani Vista, 3rd Main Road, JP Nagar 4th Phase, Bengaluru, 560076

---

## Section B: Decision Flow

### Routing

```
Query relates to minor account opening →
│
├─ eSign not completed                                        → Rule 5
├─ Application processing — within timeline, no reasons       → Rule 1
├─ Application processing — correction required               → Rule 2
├─ Application processing — overdue (> 48 working hours)      → Rule 3
├─ Application completed                                      → Rule 4
├─ PAN verification failed during opening                     → Rule 6
├─ NRI-minor account opening                                  → Rule 7
├─ Trading capabilities / restrictions                        → Rule 8
└─ General account opening requirements / documents           → A6 directly
```

### Fallback

If no rule matches, escalate to human agent.

---

---

## Section C: Rules

### Rule 1 — Application Processing (Within Timeline)

1. `status` = "Processing" AND `creation` ≤ 48 working hours AND `reasons` is empty/null.
2. Normal processing, no action needed. Timeline per A3.

---

### Rule 2 — Application Processing — Correction Required

1. `status` = "Processing" AND `reasons` is not empty.
2. Application needs corrections — communicate reasons per A6.

---

### Rule 3 — Application Overdue

1. `status` = "Processing" AND `creation` > 48 working hours AND `reasons` is empty/null.
2. Application is overdue — escalate to human agent.

---

### Rule 4 — Application Completed

1. `status` = "Completed".
2. Account approved; credentials sent to registered email; account enabled within 24–48 hours (A3).
3. If client reports credentials not received → ask client to check spam/junk folder; if not received within 48 hours of approval, escalate to human agent.

---

### Rule 5 — eSign Not Completed

1. `status` = "Processing" AND `eq_signed_on` is empty/null.
2. Direct guardian to complete eSign via the account opening flow. Link per A7.

---

### Rule 6 — PAN Verification Failed

1. `reasons` contains a PAN verification failure entry (per A6) OR client reports PAN verification failed during account opening.
2. PAN or DOB doesn't match ITD records — direct to verify at ITD portal (A7). Note it may take a few days if PAN was recently issued.

---

### Rule 7 — NRI-Minor Account

1. Client is an NRI enquiring about opening a minor account.
2. Offline only — direct to email documents to forms@zerodha.com and courier to Bengaluru office (A7). Processed within 72 working hours (A3).

---

### Rule 8 — Trading Capabilities / Restrictions

1. Client asks about what a minor account can or cannot trade.
2. Refer to A4 for full list of allowed and restricted activities.
