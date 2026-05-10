# ipo_application

## Description

WHEN TO USE:

When clients:
- Have issues with UPI mandate (not received, rejected, wrong UPI ID entered, status not updating)
- Cannot cancel or modify their IPO application (especially HNI/SME bids above ₹2 lakh)
- Report IPO application was not allotted but funds are still blocked/not refunded
- Ask about IPO application process (how to apply, SME process, minor accounts, UPI limits)
- Want to check their IPO application status or allotment
- Ask about IPO timelines (application window, listing date, refund timeline)
- Report UPI handle is not supported or not showing in IPO application form
- Report UPI ID or UPI handle is not available or not showing (even without explicitly mentioning IPO — this is typically an IPO query, not a funds/payin query)
- Want to apply for IPO via netbanking/ASBA (without UPI)

TRIGGER KEYWORDS: "IPO", "mandate", "UPI", "UPI handle", "UPI not showing", "not allotted", "refund", "blocked", "cannot cancel", "SME", "HNI", "allotment", "IPO application", "bid", "pre IPO", "before IPO purchase", "IPO shares lockin", "netbanking IPO", "ASBA", "no UPI ID", "UPI ID not available", "UPI ID not showing", "can't find UPI", "UPI not available", "bank UPI not supported"

TAGS: ipo

## Protocol

# IPO PROTOCOL

---

## Section A: Reference Data

### A1 — IPO Fundamentals

- Mandates are bank-controlled. Zerodha cannot regenerate, resend, or modify mandates.  
- One application per PAN per IPO per category. RTA rejects duplicates. Exception: multiple eligible categories if company allows.  
- Multiple applications same PAN same category = all rejected by RTA, cannot undo.  
- No Zerodha charges for IPO applications.  
- Zerodha demat = CDSL (not NSDL).  
- IPO refunds = bank unblocking funds. Nothing to do with Zerodha ledger. Funds stay in customer's bank account earning interest while blocked.  
- Pre-IPO purchased shares have 6-month lock-in from listing date. Not visible in Kite during lock-in.  
- Kite supports UPI only. ASBA must be done via bank portal or offline form.  
- Minors can apply using their own bank/demat only — cannot use parent/guardian bank.  
- REIT/InvIT IPOs have distinct category rules. All UPI bids in REIT/InvIT IPOs are categorised as Non-Individual Investor (NII) regardless of bid amount. IPOs with "Investment Trust" in the name are REIT/InvIT IPOs.

---

### A2 — Thresholds

| Threshold | Value |  
|---|---|  
| Retail maximum | ₹2,00,000 |  
| UPI maximum | ₹5,00,000 per application |  
| ASBA required | Above ₹5,00,000 |

UPI limit (₹5L) and HNI category (≥₹2L) are independent thresholds.

---

### A3 — Timelines

| Event | Timeline |  
|---|---|  
| Mandate receipt | 1 hour after application |  
| Mandate acceptance deadline | 5:00 PM on IPO closing day |  
| Retail trading window | 10:00 AM – 4:45 PM |  
| HNI closing day window | 10:00 AM – 4:00 PM (closing day only; otherwise same as retail) |  
| Status verification | Up to 1 week post-closure at NSE/BSE |  
| Modification limit | 3 only (exchange mandated) |

> If the IPO closing date is earlier than the current date, apply post-closure logic for all relevant rules.

---

### A4 — Category Restrictions

For standard IPOs, category is determined by bid amount (below ₹2L = Retail, ≥₹2L = HNI). For REIT/InvIT IPOs (identified by "Investment Trust" in the IPO name), category is always NII regardless of bid amount — apply the REIT/InvIT row below.

| Category | Cancel/Reduce | Increase | Reapply After Failure/Cancel |  
|---|---|---|---|  
| Retail (below ₹2L) | Freely cancel/modify | Yes | Can reapply within window |  
| HNI Mainboard (≥₹2L) | Cannot cancel or reduce | Can only increase | Can reapply via ASBA only (warn: one per PAN, duplicates rejected) |  
| SME (all SME) | Cannot cancel or delete | Can only increase | Cannot reapply via ASBA — one UPI attempt per PAN. This is absolute. |  
| REIT/InvIT (all UPI bids) | Cannot cancel or reduce — all UPI applications are treated as NII bids regardless of bid amount | Can only increase (up to ₹5L UPI limit per A2) | If UPI mandate was not completed, can apply separately via ASBA as a unique application |

> When explaining cancellation or modification restrictions, state only the rules applicable to the customer's specific bid category. Do not mention other category restrictions unless the customer explicitly asks about switching categories or applying at a different amount.

---

### A5 — IPO Application Status

| Internal Status | Client-Facing Communication | Next Action |  
|---|---|---|  
| cancelled | "Your application was cancelled." | Apply reapply guidance per A4 for customer's category. |  
| failed | "Your application failed." | Apply reapply guidance per A4 for customer's category. Inform: "Funds will be unblocked by your bank (timeline varies)." |  
| allotted | "Your shares have been allotted and will be credited on [share credit date]." | Visible in Kite holdings from listing date. Customer notified via CDSL credit email/SMS. |  
| not allotted | "Your application was not allotted. Your bank will unblock the blocked funds." | May take until mandate end date. |  
| other (submitted, pending, placed, etc.) | "Check your UPI app for the mandate and accept it. If you have accepted the mandate and funds are blocked, the RTA will consider your application. Verify your application number matches the UPI mandate." | Verify at NSE or BSE status page (per A8) after 1 day. |

---

### A6 — Field Rules

**Shareable with client:**

| Field | Interpretation |  
|---|---|  
| `symbol` | Share as the IPO name |  
| `application_number` | Application reference number |  
| Creation date | Application submission date |  
| Bid amount | Amount bid in the application |  
| UPI ID | Share only if customer explicitly asks |

**Non-shareable:**

| Field | Interpretation |  
|---|---|  
| `upi_amount_blocked` | UPI amount blocked for the application |  
| `upi_payment_status` | UPI payment status code — use for internal diagnosis |  
| `upi_pay_reason` | UPI payment reason — use for internal diagnosis |  
| `remark` | Internal remarks |  
| `investor_type` | Investor type classification — use for category determination |  
| `bid_start_date` | IPO bid window start date |  
| `bid_end_date` | IPO bid window end date |  
| `modified` | Last update timestamp |  
| Status codes, rejection reason codes | Never share raw values — translate using A5 |  
| `ipo_details` | Nested IPO details object — use for internal reference only |

---

### A7 — ASBA Details

**Demat details (for ASBA forms):**  
- Demat ID: 16-digit, from console.zerodha.com/account/demat  
- Depository: CDSL  
- DP Name: Zerodha

**ASBA process:**  
- **Online:** Log in to bank's internet banking portal → fill demat details above.  
- **Offline:** Download form from NSE or BSE ASBA form page (per A8) → fill details including demat details above → submit to SCSB bank (list at SEBI SCSB page per A8).

ASBA keeps money in customer's bank account but blocks it until allotment. Allotted = debited. Not allotted = unblocked.

---

### A8 — Links

| Purpose | URL |  
|---|---|  
| Kite IPO page | https://kite.zerodha.com/bids/ipo |  
| NSE IPO status check | https://nseindia.com/products/dynaContent/equities/ipos/ipo_login.jsp |  
| BSE IPO status check | https://bseindia.com/investors/appli_check.aspx |  
| UPI supported partners | https://npci.org.in/what-we-do/ipo/live-partners |  
| Demat ID lookup | https://console.zerodha.com/account/demat |  
| NSE ASBA form | https://www.nseindia.com/static/products-services/initial-public-offerings-asba-procedures |  
| BSE ASBA form | https://www.bseindia.com/markets/PublicIssues/IPOIssues_new.aspx |  
| SCSB list (SEBI) | https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=34 |  
| REIT IPO UPI info | https://support.zerodha.com/category/trading-and-markets/ipo/ipo-application/articles/reit-ipos-using-upi |

> If the IPO symbol does not match any IPO → "Unable to fetch IPO details. Check Kite or NSE/BSE websites."  
> If schedule dates are null/missing → "IPO schedule details unavailable. Check NSE/BSE websites."

---

### A9 — Special Account Rules

| Account Type | Rules |  
|---|---|  
| Minor | Own bank/demat required — cannot use parent/guardian bank. Can apply via UPI (if bank enabled) or ASBA. |  
| NRI | UPI on NRE/NRO with Indian mobile number (up to ₹5L per A2) or ASBA. Cannot apply from both NRE and NRO accounts (same PAN). NRE demat holders must use NRE bank account only — not NRO. PIS holders: bank-specific annexure \+ bank statement showing IPO debit required post-allotment via ticket. |

---

### A10 — Escalation Conditions

Escalate when:  
- A technical error persists after all troubleshooting steps (re-login, cache clear, alternate device, web version, market hours check).  
- Closing day urgency with an unresolved technical issue.

Include when escalating to human agent: screenshot, IPO name, action attempted, device type.

---

## Section B: Decision Flow

###Routing

```  
Query relates to IPO →  
│  
├─ Mandate not received  
│  ├─ IPO already closed              → Rule 1d (Post-closure)  
│  ├─ < 1 hour since application      → Rule 1a (Wait)  
│  ├─ > 1 hour since application      → Rule 1b (Category-specific action)  
│  └─ IPO closes today                → Rule 1c (Urgent)  
│  
├─ Mandate rejected / application failed  
│  ├─ IPO already closed              → Rule 2 (post-closure path)  
│  ├─ Standard failure                → Rule 2  
│  └─ Bank-specific UPI limit error   → Rule 2 (bank limit note)  
│  
├─ Wrong UPI ID entered  
│  ├─ IPO already closed              → Rule 3 (post-closure path)  
│  └─ IPO still open                  → Rule 3  
│  
├─ Cannot cancel application  
│  ├─ IPO already closed              → Rule 4 (post-closure path)  
│  └─ IPO still open                  → Rule 4  
│  
├─ Cannot modify application  
│  ├─ IPO already closed              → Rule 5 (post-closure path)  
│  └─ IPO still open                  → Rule 5  
│  
├─ Funds not refunded / still blocked → Rule 6  
├─ Application status inquiry         → Rule 7  
├─ Modified bid — no new mandate      → Rule 8  
├─ ASBA / no UPI / netbanking         → Rule 9  
├─ Special account (minor / NRI)      → Rule 10  
├─ Multiple category application      → Rule 11  
├─ How to apply via Kite              → Rule 12  
├─ Bank account changed               → Rule 13  
├─ Pre-IPO shares / lock-in           → Rule 14  
├─ UPI handle not supported           → Rule 15  
├─ Technical errors                   → Rule 16  
├─ Buying instrument, no active IPO   → Rule 17  
│  
└─ No matching scenario               → Escalate per A10  
```

---

## Section C: Rules

### Rule 1 — Mandate Not Received

**Post-closure gate:** If IPO closing date is earlier than current date, go directly to **1d**.

**1a — Less than 1 hour since application:**  
"The UPI mandate is typically sent within 1 hour of application." Customer should wait and check UPI app manually. Verify: UPI ID correctness, app version, bank support at UPI partners page (A8).

**1b — More than 1 hour since application:**  
Apply the customer's category from A4:  
- **Retail:** Delete application, resubmit. New mandate arrives within 1 hour (per A3).  
- **HNI Mainboard:** Cannot delete. Option: Apply via ASBA (warn: one per PAN, duplicates rejected). Guide per Rule 9.  
- **SME:** Cannot delete. No alternative — one UPI attempt per PAN is absolute.  
- **REIT/InvIT:** Cannot delete. Option: Apply via ASBA as a unique application (since UPI mandate was not completed). Guide per Rule 9.

**1c — IPO closes today:**  
Same category logic as 1b. Add urgency: mandate must be accepted by 5:00 PM today (per A3).

**1d — IPO already closed:**  
"Since the IPO closed on [closing date] and the UPI mandate deadline was 5:00 PM on [closing date], your application will not be considered by the RTA as the mandate was not approved before the deadline. Your funds were not blocked, so no unblocking is needed. For future IPOs, ensure you approve the mandate within 1 hour of applying and before the 5:00 PM deadline on the closing day."

If REIT/InvIT, add: "For REIT IPOs, if the UPI mandate was not completed, you could have applied separately via ASBA as a unique application — please keep this option in mind for future REIT IPOs."

---

### Rule 2 — Mandate Rejected / Application Failed

**Post-closure gate:** If IPO closing date is earlier than current date → "Since the IPO closed on [closing date], your application can no longer be acted upon. Your bank will unblock the funds — this may take until the mandate end date [mandate end date]. If funds remain blocked beyond this date, please contact your bank."

**Window open — apply all of the following:**

1. Communicate status: "Your application failed." (Per A5.)  
2. Apply reapply options for the customer's category:  
   - **Retail:** Can reapply. Delete application and resubmit.  
   - **HNI Mainboard:** Cannot cancel. Option: Apply via ASBA only (warn: one per PAN, duplicates rejected). Guide per Rule 9.  
   - **SME:** Cannot cancel or reapply — one UPI attempt per PAN is absolute.  
   - **REIT/InvIT:** Cannot cancel. Option: Apply via ASBA as a unique application if UPI mandate was not completed. Guide per Rule 9.  
3. "Funds will be unblocked by your bank (timeline varies)."  
4. If failure is due to a bank-specific UPI limit in the ₹2L–₹5L range: "This is your bank's own UPI limit, not the overall ₹5 lakh limit. Please check with your bank or apply via ASBA." Guide per Rule 9.

---

### Rule 3 — Wrong UPI ID

**Post-closure gate:** If IPO closing date is earlier than current date → "Since the IPO closed on [closing date], it is no longer possible to modify or reapply. If the mandate was not approved or funds were not blocked, the application will not be considered and no action is needed. If funds were blocked, they will be unblocked by your bank before the mandate end date [mandate end date]."

1. Do not share the customer's UPI ID unless they explicitly ask.  
2. Apply the customer's category from A4:  
   - **Retail:** Cancel, reapply with the correct UPI ID.  
   - **HNI Mainboard:** Cannot cancel. Option: Apply via ASBA with correct bank (warn: one per PAN). Guide per Rule 9.  
   - **SME:** Cannot cancel. No alternative.  
   - **REIT/InvIT:** Cannot cancel. Option: Apply via ASBA as a unique application if UPI mandate was not completed. Guide per Rule 9.

---

### Rule 4 — Cannot Cancel

**Post-closure gate:** If IPO closing date is earlier than current date → "Since the IPO closed on [closing date], it is no longer possible to cancel your application. If the mandate was not approved or funds were not blocked, the application will not be considered by the RTA and the funds will be automatically unblocked by your bank before the mandate end date [mandate end date]. You can safely ignore this application."

1. If `status` = "cancelled" → "Your application was cancelled." Then apply reapply guidance for customer's category:  
   - **Retail:** Can reapply within window.  
   - **HNI Mainboard:** Can reapply via ASBA only (warn: one per PAN, duplicates rejected). Guide per Rule 9.  
   - **SME:** Cannot reapply — one UPI attempt per PAN is absolute.  
   - **REIT/InvIT:** Can apply via ASBA as a unique application if UPI mandate was not completed. Guide per Rule 9.  
2. If REIT/InvIT → "REIT IPO applications made through UPI are categorised as Non-Individual Investor (NII) bids. These bids cannot be cancelled or decreased once applied, but they can be increased up to ₹5 lakhs. If the UPI mandate was not completed, you can apply separately via ASBA — this will be treated as a unique application." Guide per Rule 9.  
3. If Retail → application should be cancellable. Check: within trading window (per A3), IPO still open. Suggest: refresh or web version at Kite IPO page (A8).  
4. If HNI Mainboard or SME → cannot cancel per A4. Explain the restriction for their specific category only.

---

### Rule 5 — Cannot Modify

**Post-closure gate:** If IPO closing date is earlier than current date → "Since the IPO closed on [closing date], modifications are no longer possible. Your existing application will be processed as-is."

1. If REIT/InvIT and customer wants to reduce → "REIT IPO bids can only be increased, not reduced or cancelled." (Per A4.)  
2. If HNI Mainboard (≥₹2L) or SME and customer wants to reduce → "Your bid can only be increased, not reduced." (Per A4.)  
3. If 3 modifications already made → "The exchange allows a maximum of 3 modifications per application." (Per A3.)

---

### Rule 6 — Funds Not Refunded

1. Retrieve mandate end date from the IPO schedule. Share with customer.  
2. "The mandate end date for this IPO was [DD MMM YYYY]. Your bank typically unblocks funds within a few days to two weeks after allotment finalization. If funds remain blocked beyond the mandate end date, please contact your bank."  
3. Do not reference Zerodha ledger for IPO refunds — refunds are entirely bank-side (per A1 and A6).

---

### Rule 7 — Status Communication

1. Translate the internal status using A5.  
2. Provide the next action per A5:  
   - **cancelled:** "Your application was cancelled." Apply reapply guidance from A4 for customer's category.  
   - **failed:** "Your application failed." Apply reapply guidance from A4. Inform: "Funds will be unblocked by your bank (timeline varies)."  
   - **allotted:** "Your shares have been allotted and will be credited on [share credit date from schedule]." Visible in Kite holdings from listing date.  
   - **not allotted:** "Your application was not allotted. Your bank will unblock the blocked funds." May take until mandate end date.  
   - **other (submitted, pending, placed, etc.):** "Check your UPI app for the mandate and accept it. If you have accepted the mandate and funds are blocked, the RTA will consider your application. Verify your application number matches the UPI mandate." Direct to NSE or BSE status page (A8) after 1 day.

---

### Rule 8 — Modified Bid: No New Mandate

Calculate elapsed time from modification timestamp to current time.

**Less than 1 hour:**  
"The new UPI mandate is typically sent within 1 hour of modification. Please check your UPI app for the mandate request."

**More than 1 hour:**  
"The mandate is sent by your bank, not Zerodha. To verify if the modification was successful, check the blocked amount in your bank account:  
- [new amount] blocked = modification successful.  
- [original amount] blocked = original bid remains valid; new mandate still pending."

**Modification made today and IPO closes today:**  
Add urgency: "The UPI mandate deadline is 5:00 PM today. You must approve the new mandate before this deadline for the modified application to be considered."

---

### Rule 9 — ASBA Process

1. If customer has no UPI or wants to apply via netbanking → "Kite supports UPI only. You can apply via ASBA through your bank's internet banking portal or via an offline form." (Per A1.)  
2. Share demat details from A7: Demat ID (16-digit, from console.zerodha.com/account/demat), Depository: CDSL, DP Name: Zerodha.  
3. **Online ASBA:** Log in to bank's internet banking portal → fill demat details above.  
4. **Offline ASBA:** Download form from NSE or BSE ASBA form page (A8) → fill demat details → submit to SCSB bank (list at A8).

---

### Rule 10 — Special Accounts

Apply rules from A9 for the customer's account type.

**Minor:** Own bank/demat required — cannot use parent/guardian bank. Can apply via UPI (if bank enabled) or ASBA.

**NRI:**  
- UPI on NRE/NRO with Indian mobile number (up to ₹5L per A2) or ASBA.  
- Cannot apply from both NRE and NRO accounts (same PAN).  
- NRE demat holders must use NRE bank account only — not NRO.  
- PIS holders: submit bank-specific annexure \+ bank statement showing IPO debit via ticket post-allotment.

---

### Rule 11 — Multiple Categories

1. A customer can apply in multiple eligible categories (shareholder/employee/retail) using the same demat if the company allows (check RHP). Each category requires a separate application.  
2. If application exceeds ₹5L (per A2), ASBA is required.  
3. Multiple lots must be applied in one application — not as separate applications.

---

### Rule 12 — How to Apply via Kite

1. Kite IPO page (A8) → select IPO → quantity (lots; minimum 1; total = lots × lot_size × price) → price ("Cutoff" recommended, or specific price within `price_from` to `price_to` band) → UPI ID → submit → approve mandate within 1 hour (per A3) → accept by 5:00 PM on closing day (per A3).  
2. Trading hours per A3. No charges. One per PAN per category (per A1).  
3. ASBA not available on Kite — see Rule 9.

---

### Rule 13 — Bank Account Changed After Application

**Post-closure gate:** If IPO closing date is earlier than current date → "Since the IPO closed on [closing date], it is no longer possible to modify or reapply. If the mandate was not approved or funds were not blocked, the application will not be considered. If funds were blocked, they will be unblocked by your bank before the mandate end date [mandate end date]."

1. "The mandate was sent to your old bank's UPI. Your new bank will not receive it."  
2. Apply the customer's category from A4:  
   - **Retail:** Cancel, update bank on Console if needed, reapply with new UPI.  
   - **HNI Mainboard:** Cannot cancel. Apply via ASBA with new bank (warn: one per PAN). Guide per Rule 9.  
   - **SME:** Cannot cancel. No alternative.  
   - **REIT/InvIT:** Cannot cancel. Apply via ASBA with new bank as a unique application (if UPI mandate was not completed). Guide per Rule 9.  
3. Prevention: "Always verify your bank/UPI details before applying."

---

### Rule 14 — Pre-IPO Purchased Shares Lock-in

**Do not call any tools.** Respond immediately:  
"Pre-IPO purchased shares have a 6-month lock-in from the listing date. The shares will be tradable and visible on Kite only after the lock-in expires. You can check the exact expiry in your Transaction cum Holdings statement (SOT/SOH)."

---

### Rule 15 — Unsupported UPI Handle

Do not ask clarifying questions. Respond directly:  
1. "The UPI handle mentioned is not supported for IPO applications."  
2. Check supported UPI apps and banks at UPI partners page (A8).  
3. "You are not restricted to your Zerodha-linked bank — you can use any personal bank under your name with a supported UPI handle."  
4. Alternative: Apply via ASBA through bank's internet banking portal. Guide per Rule 9.

---

### Rule 16 — Technical Errors

1. Troubleshoot in order: internet connection, cache clear, alternate device, app update, web version at Kite IPO page (A8), market hours (per A3), category restrictions (per A4).  
2. UPI ID not showing: suggest entering manually, verify bank support at UPI partners page (A8), or use ASBA per Rule 9.  
3. If issue persists after all troubleshooting: collect screenshot, IPO name, action attempted, device type. Escalate to support agent per A10. If closing day → treat as urgent.

---

### Rule 17 — Post-Listing Purchase Inquiry

Triggered when customer asks about investing in or buying an instrument and no active IPO data is found.

"The IPO period for [instrument name] has ended. The instrument is now listed on the exchanges and can be purchased on Kite like any regular stock or REIT/InvIT unit. Search for the name or symbol on Kite and place a delivery order. Ensure sufficient funds are available in your account."
