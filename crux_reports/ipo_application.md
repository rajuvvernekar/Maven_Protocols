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

## Protocol

# IPO PROTOCOL

---

## Section A: Reference Data

All rules reference these blocks as single sources of truth.

### A1 — IPO Fundamentals

- Mandates are bank-controlled. Zerodha cannot regenerate, resend, or modify mandates.
- One application per PAN per IPO per category. RTA rejects duplicates. Exception: multiple eligible categories if company allows.
- Multiple PANs for same IPO = violation — all rejected, possible penalties.
- Multiple applications same PAN same category = all rejected by RTA, cannot undo.
- No Zerodha charges for IPO applications.
- Zerodha demat = CDSL (not NSDL).
- IPO refunds = bank unblocking funds. Nothing to do with Zerodha ledger. Funds stay in customer's bank account earning interest while blocked.
- Pre-IPO shares have 6-month lock-in from listing date. Not visible in Kite during lock-in.
- Kite supports UPI only. ASBA must be done via bank portal or offline form.
- Minors can apply using their own bank/demat only — cannot use parent/guardian bank.
- REIT/InvIT IPOs have distinct category rules — all UPI bids are categorised as NII regardless of bid amount. Always check the IPO name from `ipo_details` tool data; if it contains "Investment Trust," it is a REIT/InvIT IPO — use the REIT/InvIT row in **A4** for all cancel/modify/reapply decisions.

### A2 — Thresholds

| Threshold | Value |
|---|---|
| Retail maximum | ₹2,00,000 |
| UPI maximum | ₹5,00,000 per application |
| ASBA required | Above ₹5,00,000 |

UPI limit (₹5L) and HNI category (≥₹2L) are independent thresholds.

### A3 — Timelines

| Event | Timeline |
|---|---|
| Mandate receipt | 1 hour after application |
| Mandate acceptance deadline | 5:00 PM on IPO closing day |
| Retail trading window | 10:00 AM – 4:45 PM |
| HNI closing day window | 10:00 AM – 4:00 PM (closing day only; otherwise same as retail) |
| Status verification | Up to 1 week post-closure at NSE/BSE |
| Modification limit | 3 (exchange mandated) |

### A4 — Category Restrictions

| Category | Cancel/Reduce | Increase | Reapply After Failure/Cancel |
|---|---|---|---|
| Retail (below ₹2L) | Freely cancel/modify | Yes | Can reapply within window |
| HNI Mainboard (≥₹2L) | Cannot cancel or reduce | Can only increase | Can reapply via ASBA only (warn: one per PAN, duplicates rejected) |
| SME (all SME) | Cannot cancel or delete | Can only increase | Cannot reapply via ASBA — one UPI attempt per PAN. This is absolute. |
| REIT/InvIT (all UPI bids) | Cannot cancel or reduce — all UPI applications are treated as Non-Individual Investor (NII) bids regardless of bid amount | Can only increase (up to ₹5L UPI limit per **A2**) | If UPI mandate was not completed, customer can apply separately via ASBA — this will be treated as a unique application. Guide per Rule 9 using **A7** demat details. |

**Scope rule:** When explaining cancellation/modification policies, only state the rules for the customer's specific bid category. Do not mention other category restrictions unless the customer explicitly asks about switching categories or applying at different amounts.

### A5 — Status Translations

| Internal Status | Client-Facing Communication | Next Action |
|---|---|---|
| cancelled | "Your application was cancelled" | Apply reapply logic per **A4** |
| failed | "Your application failed" | Apply reapply logic per **A4**. Funds unblocked by bank (timeline varies). |
| allotted | Shares credited on share credit date (from schedule) | Visible on Kite on listing date. Check Console before listing. |
| not allotted | Bank unblocks funds | May take until mandate end date. |
| other (submitted, pending, placed, etc.) | "Check your UPI app for the mandate and accept it. If you have accepted the mandate and funds are blocked, the RTA will consider your application. Verify application number matches UPI mandate." | Verify at NSE or BSE status page (per **A8**) after 1 day. |

### A6 — Field Rules

**Shareable with client:** IPO name (from `symbol`), `application_number`, creation date (DD MMM YYYY, HH:MM AM/PM format), bid amount (₹X,XX,XXX format).

**Internal reasoning only (never share with client):** `upi_amount_blocked`, `upi_payment_status`, `upi_pay_reason`, `remark`, `investor_type`, `bid_start_date`, `bid_end_date`, `modified`, status codes, full status messages (e.g., "Authorisation request sent..."), rejection reason codes (PSP not available, insufficient funds, etc.), `ipo_details` nested object, UPI ID (unless customer explicitly asks).

**Client-facing terminology — always use these phrases:**

| Instead of | Use |
|---|---|
| "UPI payment pending" | "Mandate needs approval" |
| "We'll regenerate mandate" | "Mandates sent by bank, Zerodha cannot regenerate" |
| "Contact exchange" | "Verify at NSE/BSE" |
| "Payment failed" | "Mandate rejected by bank" (no reason) |
| "Zerodha will unblock funds" | "Bank unblocks funds" |
| "We'll resend UPI request" | "Bank controls mandates" |
| Any raw internal status message | Translate using **A5** |
| "NPCI" | (omit — describe in plain language) |
| Any rejection reason | (omit — say "Mandate rejected by bank") |
| Any ledger reference for IPO refunds | (omit — IPO refunds are bank-side only) |

IPO type determination: always use the `ipo_details` nested object from tool data. Bid amount determines category only for standard IPOs — for REIT/InvIT IPOs (identified by "Investment Trust" in the IPO name), category is always NII regardless of bid amount. Apply REIT-specific rules from **A4**.

### A7 — ASBA Details

**Demat details (for ASBA forms):**
- Demat ID: 16-digit, from console.zerodha.com/account/demat
- Depository: CDSL
- DP Name: Zerodha

**ASBA process:**
- Online: Log in to bank's internet banking portal → fill demat details above.
- Offline: Download form from NSE or BSE ASBA form page (per **A8**) → fill details including demat details above → submit to SCSB bank (list at SEBI SCSB page per **A8**).

ASBA keeps money in customer's bank account but blocks it until allotment. Allotted = debited. Not allotted = unblocked.

### A8 — Links

| Purpose | URL |
|---|---|
| Kite IPO page | https://kite.zerodha.com/bids/ipo |
| NSE IPO status check | https://nseindia.com/products/dynaContent/equities/ipos/ipo_login.jsp |
| BSE IPO status check | https://bseindia.com/investors/appli_check.aspx |
| UPI supported partners | https://npci.org.in/what-we-do/ipo/live-partners |
| Demat ID lookup | console.zerodha.com/account/demat |
| NSE ASBA form | https://www.nseindia.com/products/content/equities/ipos/asba_form.htm |
| BSE ASBA form | https://www.bseindia.com/markets/PublicIssues/IPOIssues_new.aspx |
| SCSB list (SEBI) | https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=34 |
| REIT IPO UPI info | https://support.zerodha.com/category/trading-and-markets/ipo/ipo-application/articles/reit-ipos-using-upi |

### A9 — Special Account Rules

| Account Type | Rules |
|---|---|
| Minor | Own bank/demat required — cannot use parent/guardian bank. Can apply via UPI (if bank enabled) or ASBA. |
| NRI | UPI on NRE/NRO with Indian mobile number (up to ₹5L per **A2**) or ASBA. Cannot apply from both NRE and NRO (same PAN). NRE demat holders must use NRE bank account only, not NRO. PIS holders: submit bank-specific annexure + bank statement showing IPO debit via ticket post-allotment. |

### A10 — Escalation Triggers

Escalate when:
- Technical error persists after all troubleshooting steps (re-login, cache clear, alternate device, web version, market hours check).
- Closing day urgency with unresolved technical issue.

Collect for escalation: screenshot, IPO name, action attempted, device type.

**Escalation behavior:** When any rule in this protocol says **ESCALATE**, do not draft a customer-facing response. Instead, output only: **HUMAN AGENT ACTION REQUIRED** — followed by the reason from the rule. The human agent will handle the query manually.

---

## Section B: Decision Flow

### Preflight (run on every query)

1. **Step 1:** Call `ipo_application_tool` → extract `symbol`, `application_number`, `creation`, `bid_amount`, `status`, `type` (SME or Mainboard).
2. **Step 2:** Call `search_instruments` with `symbol` → extract dates, `min_quantity`, `price_from`, `price_to`, schedule object (allotment finalization, refund initiation, share credit, mandate end date). Convert Unix timestamps to DD MMM YYYY.
3. If `symbol` does not match any IPO → "Unable to fetch IPO details. Check Kite or NSE/BSE websites."
4. If dates are null/missing → "IPO schedule details unavailable. Check NSE/BSE websites."
5. If customer doesn't mention IPO name → use Step 1 to identify from `symbol` and `type`, then proceed to Step 2.
6. Apply field protection per **A6** — determine shareable vs internal-only fields.
7. Determine the customer's bid category from tool data to apply the correct restrictions from **A4**.
8. **REIT/InvIT check:** Check the IPO name from `ipo_details` — if it contains "Investment Trust" (indicating REIT/InvIT), flag as REIT/InvIT and apply REIT-specific category rules from **A4** instead of standard retail/HNI category logic based on bid amount.
9. **Post-closure check:** If the IPO closing date (from Step 2) is earlier than the current date, mark the query as post-closure. Rules 1–5 must check this flag and apply post-closure logic instead of standard active-IPO guidance.

### Routing Tree

```
Query relates to IPO →
│
├─ Mandate not received
│  ├─ IPO already closed → Rule 1d (Post-closure)
│  ├─ < 1 hour since application → Rule 1a (Wait)
│  ├─ > 1 hour since application → Rule 1b (Category-specific action)
│  └─ IPO closes today → Rule 1c (Urgent)
│
├─ Mandate rejected / application failed
│  ├─ IPO already closed → Rule 2 (post-closure path)
│  ├─ Standard failure → Rule 2
│  └─ Bank-specific UPI limit error → Rule 2 (bank limit note)
│
├─ Wrong UPI ID entered
│  ├─ IPO already closed → Rule 3 (post-closure path)
│  └─ IPO still open → Rule 3
│
├─ Cannot cancel application
│  ├─ IPO already closed → Rule 4 (post-closure path)
│  └─ IPO still open → Rule 4
│
├─ Cannot modify application
│  ├─ IPO already closed → Rule 5 (post-closure path)
│  └─ IPO still open → Rule 5
│
├─ Funds not refunded / still blocked
│  → Rule 6
│
├─ Application status inquiry
│  → Rule 7
│
├─ Modified bid — no new mandate received
│  → Rule 8
│
├─ ASBA process / no UPI / netbanking application
│  → Rule 9
│
├─ Special account (minor / NRI)
│  → Rule 10
│
├─ Multiple category application
│  → Rule 11
│
├─ How to apply via Kite
│  → Rule 12
│
├─ Bank account changed after application
│  → Rule 13
│
├─ Pre-IPO shares / lock-in / shares not showing after listing
│  → Rule 14
│
├─ UPI handle not supported / not found
│  → Rule 15
│
├─ Technical errors
│  → Rule 16
│
└─ No matching scenario
   → Collect details, **ESCALATE** per A10
```

### Scope

- Address: IPO applications, mandates, status, cancellation/modification, refunds, ASBA, and application errors.
- Do not volunteer: other category restrictions beyond the customer's category (per **A4** scope rule), internal field values (per **A6**), or information the customer hasn't asked about.

### Fallback

If no matching scenario is found after checking all rules → collect details and **ESCALATE** per **A10**.

---

## Section C: Rules

Rules reference Section A blocks. They do not redefine what is already defined there.

### Rule 1 — Mandate Not Received

**Post-closure gate:** If the query is marked post-closure (Preflight Step 9), go directly to **1d**.

**1a — Less than 1 hour since application:**
"The UPI mandate is typically sent within 1 hour of application." Check: UPI ID correctness, app version, bank support at UPI partners page (**A8**), and ask customer to manually check their UPI app.

**1b — More than 1 hour since application:**
Apply the customer's category restrictions from **A4**:
- Retail: Delete application, resubmit (new mandate within 1 hour).
- HNI Mainboard: Cannot delete. Option: Apply via ASBA (warn: one per PAN, duplicates rejected). Guide per Rule 9.
- SME: Cannot delete. No alternative (cannot reapply via ASBA).
- REIT/InvIT: Cannot delete. Option: Apply via ASBA as a unique application (since UPI mandate was not completed). Guide per Rule 9.

**1c — IPO closes today:**
Same category logic as 1b, with added urgency: mandate must be accepted by 5:00 PM today (per **A3**).

**1d — IPO already closed (post-closure inquiry):**
"Since the IPO closed on [closing date] and the UPI mandate deadline was 5:00 PM on [closing date], your application will not be considered by the RTA as the mandate was not approved before the deadline. Your funds were not blocked, so no unblocking is needed. For future IPOs, ensure you approve the mandate within 1 hour of applying and before the 5:00 PM deadline on the closing day."

If the IPO is a REIT/InvIT (Preflight Step 8), add: "For REIT IPOs, if the UPI mandate was not completed, you could have applied separately via ASBA as a unique application — please keep this option in mind for future REIT IPOs."

### Rule 2 — Mandate Rejected / Application Failed

**Post-closure gate:** If the query is marked post-closure (Preflight Step 9) → "Since the IPO closed on [closing date], your application can no longer be acted upon. Your bank will unblock the funds — this may take until the mandate end date [mandate end date from schedule]. If funds remain blocked beyond this date, please contact your bank."

1. Communicate status: "Your application failed." (Per **A5**.)
2. Apply reapply options per **A4** for the customer's category (including REIT/InvIT if applicable per Preflight Step 8).
3. Add: "Funds will be unblocked by your bank (timeline varies)."
4. If the failure is due to a bank-specific UPI limit error (₹2L–₹5L range): "This is your bank's own UPI limit, not the NPCI limit of ₹5 lakh. Please check with your bank for their specific limit, or apply via ASBA." Guide per Rule 9.

### Rule 3 — Wrong UPI ID

**Post-closure gate:** If the query is marked post-closure (Preflight Step 9) → "Since the IPO closed on [closing date], it is no longer possible to modify or reapply. If the mandate was not approved or funds were not blocked, the application will not be considered and no action is needed. If funds were blocked, they will be unblocked by your bank before the mandate end date [mandate end date]."

1. Do not share the customer's UPI ID unless they explicitly ask.
2. Apply the customer's category restrictions from **A4**:
   - Retail: Cancel, reapply with correct UPI ID.
   - HNI Mainboard: Cannot cancel. Option: ASBA with correct bank (warn: one per PAN).
   - SME: Cannot cancel. No alternative.
   - REIT/InvIT: Cannot cancel. Option: Apply via ASBA as a unique application if UPI mandate was not completed. Guide per Rule 9.

### Rule 4 — Cannot Cancel

**Post-closure gate:** If the query is marked post-closure (Preflight Step 9) → "Since the IPO closed on [closing date], it is no longer possible to cancel your application. If the mandate was not approved or funds were not blocked, the application will not be considered by the RTA and the funds will be automatically unblocked by your bank before the mandate end date [mandate end date]. You can safely ignore this application."

1. If `status` = "cancelled" → "Your application was cancelled." Then apply reapply guidance per **A4**.
2. If REIT/InvIT (Preflight Step 8) → cannot cancel per **A4**. "REIT IPO applications made through UPI are categorised as Non-Individual Investor (NII) bids. These bids cannot be cancelled or decreased once applied, but they can be increased up to ₹5 lakhs. If the UPI mandate was not completed, you can apply separately via ASBA — this will be treated as a unique application." Guide per Rule 9.
3. If Retail → application should be cancellable. Check: within trading window (per **A3**), IPO still open. Suggest: try refresh or web version at **A8** Kite IPO page.
4. If HNI Mainboard or SME → cannot cancel per **A4**. Explain the restriction for their specific category only.

**Example response:**
"The error message 'Cancellation of bid not allowed for issue RIIT and Category: OTHBID' occurs because REIT IPO applications made through UPI are categorized as Non-Individual Investor (NII) bids. These bids cannot be cancelled or decreased once applied, but they can be increased up to ₹5 lakhs. If you used an incorrect UPI ID or did not receive the mandate request, you cannot delete the application. However, you can still apply for the IPO using Netbanking ASBA. This application will be considered unique and eligible for allotment since the UPI mandate step was not completed."

### Rule 5 — Cannot Modify

**Post-closure gate:** If the query is marked post-closure (Preflight Step 9) → "Since the IPO closed on [closing date], modifications are no longer possible. Your existing application will be processed as-is."

1. If REIT/InvIT (Preflight Step 8) and customer wants to reduce → "REIT IPO bids can only be increased, not reduced or cancelled." (Per **A4**.)
2. If ≥₹2L or SME and customer wants to reduce → "Your bid can only be increased, not reduced." (Per **A4**.)
3. If 3 modifications already made → "The exchange allows a maximum of 3 modifications per application." (Per **A3**.)

### Rule 6 — Funds Not Refunded

1. Retrieve the mandate end date from the schedule object (fetched in Preflight Step 2). This date must be provided to the customer.
2. Respond: "The mandate end date for this IPO was [DD MMM YYYY]. Your bank typically unblocks funds within a few days to two weeks after allotment finalization. If funds remain blocked beyond the mandate end date, please contact your bank."
3. IPO refunds are entirely bank-side — never reference Zerodha ledger for IPO refunds (per **A1** and **A6**).

### Rule 7 — Status Communication

1. Translate the internal status using **A5**.
2. Provide the next action per **A5**.
3. For "allotted": share the share credit date from the schedule object.
4. For "not allotted": note that funds may take until the mandate end date to unblock.
5. For other statuses (submitted, pending, placed, etc.): direct to verify at NSE or BSE status page (**A8**) after 1 day.

### Rule 8 — Modified Bid: No New Mandate

1. Calculate elapsed time from modification timestamp to current time.

**Less than 1 hour:**
"New UPI mandate is typically sent within 1 hour of modification. Please check your UPI app for the mandate request."

**More than 1 hour:**
"The mandate is not sent from Zerodha but from NPCI. Please approve the new UPI mandate once you receive it. To verify modification status, check the blocked amount in your bank account:
- [new amount] blocked = modification successful
- [original amount] blocked = original bid remains valid, new mandate pending"

**Modification was today and IPO closes today:**
Add urgency: "The UPI mandate deadline is 5:00 PM today. You must approve the new mandate before this deadline for the modified application to be considered."

### Rule 9 — ASBA Process

1. Explain: "ASBA keeps money in your bank account but blocks it until allotment. If allotted, the amount is debited. If not allotted, it is unblocked." (Per **A7**.)
2. If customer asks to apply via netbanking or says they don't have UPI → "Kite supports UPI only. You can apply via ASBA through your bank's internet banking portal."
3. Guide using demat details from **A7**: Demat ID (16-digit, from console.zerodha.com/account/demat), Depository: CDSL, DP Name: Zerodha.
4. For online: log in to bank's internet banking portal → fill demat details.
5. For offline: download form from NSE or BSE ASBA form page (**A8**) → fill details → submit to SCSB bank (list at **A8**).

### Rule 10 — Special Accounts

1. Apply the rules from **A9** for the customer's account type (Minor or NRI).
2. For Minors: own bank/demat required. Can apply via UPI (if bank enabled) or ASBA.
3. For NRIs: UPI on NRE/NRO with Indian mobile number (up to ₹5L) or ASBA. Cannot apply from both NRE and NRO (same PAN). NRE demat holders must use NRE bank account only, not NRO. PIS holders: submit bank-specific annexure + bank statement showing IPO debit via ticket post-allotment.

### Rule 11 — Multiple Categories

1. A customer can apply in multiple eligible categories (shareholder/employee/retail) using the same demat if the company allows (check RHP). Separate applications for each category.
2. If application exceeds ₹5L (per **A2**), must use ASBA.
3. Multiple lots must be applied in one application, not multiple applications.

### Rule 12 — How to Apply via Kite

1. Guide: Kite → IPO → select → quantity (lots; minimum 1; total = lots × lot_size × price) → price ("Cutoff" recommended for final discovered price, or specific price within `price_from` to `price_to` band) → UPI ID → submit → approve mandate within 1 hour (**A3**) → accept by 5:00 PM on closing day (**A3**).
2. Trading hours per **A3**. No charges. One per PAN per category.
3. For ASBA: Kite does not support ASBA. See Rule 9.

### Rule 13 — Bank Account Changed After Application

1. Explain: "The mandate was sent to your old bank's UPI. Your new bank will not receive it."
2. Apply the customer's category restrictions from **A4**:
   - Retail: Cancel, update bank on Console if needed, reapply with new UPI.
   - HNI Mainboard: Cannot cancel. Apply via ASBA with new bank.
   - SME: Cannot cancel. No alternative.
   - REIT/InvIT: Cannot cancel. Apply via ASBA with new bank as a unique application (if UPI mandate was not completed).
3. Prevention advice: "Always verify your bank/UPI details before applying."

### Rule 14 — Pre-IPO Shares Lock-in

1. **Do not use any tools.** No holdings check, no ledger check, no instrument search, no application lookup.
2. Respond immediately: "Pre-IPO shares have a 6-month lock-in from the listing date. The shares will be tradable and visible on Kite only after the lock-in expires. You can check the exact expiry in your Transaction cum Holdings statement (SOT/SOH)."

### Rule 15 — Unsupported UPI Handle

1. Do not ask clarifying questions. Respond directly:
   - "The UPI handle mentioned is not supported for IPO applications."
   - "Check supported UPI apps and banks at [UPI partners link from **A8**]."
   - "You are not restricted to your Zerodha-linked bank — you can use any personal bank under your name with a supported UPI handle."
   - "Alternative: Apply via ASBA through your bank's internet banking portal." Guide per Rule 9 using **A7** demat details.

### Rule 16 — Technical Errors

1. Check: internet connection, cache, alternate device, app update, web version at Kite IPO page (**A8**), market hours (per **A3**), category restrictions (per **A4**).
2. UPI ID not showing: suggest entering manually, verify bank support at UPI partners page (**A8**), or use ASBA (Rule 9).
3. If issue persists after troubleshooting: collect screenshot, IPO name, action attempted, device type. Closing day = treat as urgent.
4. **ESCALATE** per **A10**.

---

## Section D: General Notes

1. IPO type must always be determined from tool data (`ipo_details` nested object). Bid amount determines category only for standard IPOs. For REIT/InvIT IPOs (identified by "Investment Trust" in the IPO name), all UPI bids are categorised as NII — use the REIT/InvIT row in **A4** for all cancel/modify/reapply decisions. Dates must always be fetched from tool data, not calculated from SEBI timelines or assumed.
2. Category restrictions (**A4**) are the most critical reference in this protocol — nearly every rule routes through them. Always check the customer's specific category before advising on cancellation, modification, or reapplication. For REIT/InvIT IPOs, the category is always NII regardless of bid amount.
3. All fund-related queries (refund, unblocking, blocked amounts) are bank-side. Never reference Zerodha ledger for IPO refunds or blocked funds.
4. Post-closure queries: Once an IPO's closing date has passed, active-IPO guidance (cancel, modify, reapply, wait for mandate) is no longer actionable. Always check the post-closure flag (Preflight Step 9) before advising on Rules 1–5.
