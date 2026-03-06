# ipo_application

## Description

WHEN TO USE:

- Customer has issues with UPI mandate (not received, rejected, wrong UPI ID entered, status not updating)
- Customer cannot cancel or modify their IPO application (especially HNI/SME bids above ₹2 lakh)
- Customer's IPO application was not allotted but funds are still blocked/not refunded
- Customer asks about IPO application process (how to apply, SME process, minor accounts, UPI limits)
- Customer wants to check their IPO application status or allotment
- Customer asks about IPO timelines (application window, listing date, refund timeline)
- Customer's UPI handle is not supported or not showing in IPO application form
- Customer says their UPI ID or UPI handle is not available or not showing (even without explicitly mentioning IPO — this is typically an IPO query, not a funds/payin query)
- Customer wants to apply for IPO via netbanking/ASBA (without UPI)

TRIGGER KEYWORDS: "IPO", "mandate", "UPI", "UPI handle", "UPI not showing", "not allotted", "refund", "blocked", "cannot cancel", "SME", "HNI", "allotment", "IPO application", "bid", "pre IPO", "before IPO purchase", "IPO shares lockin", "netbanking IPO", "ASBA", "no UPI ID", "UPI ID not available", "UPI ID not showing", "can't find UPI", "UPI not available", "bank UPI not supported"

## Protocol

# PROTOCOL

## Knowledge Base

<knowledge_base>
<facts>
- Mandates are bank-controlled (Zerodha cannot regenerate/resend/modify)
- One application per PAN per IPO per category (RTA rejects duplicates), except multiple eligible categories if company allows
- Minors can apply using own bank/demat only
- No Zerodha charges for IPO applications
- Zerodha demat = CDSL (not NSDL)
- Pre-IPO shares have 6-month lock-in from listing date, not visible in Kite during lock-in
- IPO refunds = bank unblocking funds (nothing to do with Zerodha ledger)
- Kite supports UPI only; ASBA must be done via bank portal or offline form
- UPI limit (₹5L) and HNI category (≥₹2L) are independent thresholds
- Multiple PANs for same IPO = violation, all rejected, possible penalties
- Multiple applications same PAN same category = ALL rejected by RTA, cannot undo
</facts>

<thresholds>
<retail_max>₹2,00,000</retail_max>
<upi_max>₹5,00,000 per application</upi_max>
<asba_required>Above ₹5,00,000</asba_required>
</thresholds>

<timelines>
<mandate_receipt>1 hour after application</mandate_receipt>
<mandate_deadline>5:00 PM on IPO closing day</mandate_deadline>
<retail_window>10:00 AM - 4:45 PM</retail_window>
<hni_closing_day>10:00 AM - 4:00 PM (closing day only, otherwise same as retail)</hni_closing_day>
<status_verification>Up to 1 week post-closure at NSE/BSE</status_verification>
<modification_limit>3 (exchange mandated)</modification_limit>
</timelines>

<restrictions>
<scope_rule>When explaining cancellation/modification policies, ONLY state the rules for the customer's specific bid category. Do NOT mention other category restrictions unless the customer explicitly asks about switching categories or applying at different amounts.</scope_rule>

<retail>Below ₹2L: Cancel/modify freely. If failed/cancelled, can reapply within window.</retail>
<hni_mainboard>≥₹2L Mainboard: Cannot cancel/reduce, can only increase. If failed/cancelled, can reapply via ASBA (warn: one per PAN, duplicates rejected).</hni_mainboard>
<sme>ALL SME: Cannot cancel/delete, can only increase. If mandate fails, CANNOT reapply via ASBA (one UPI attempt per PAN). This is absolute.</sme>
</restrictions>

<external_urls>
<kite_bids>https://kite.zerodha.com/bids/ipo</kite_bids>
<nse_status>https://nseindia.com/products/dynaContent/equities/ipos/ipo_login.jsp</nse_status>
<bse_status>https://bseindia.com/investors/appli_check.aspx</bse_status>
<upi_partners>https://npci.org.in/what-we-do/ipo/live-partners</upi_partners>
<demat_id>console.zerodha.com/account/demat</demat_id>
<nse_asba_form>https://www.nseindia.com/products/content/equities/ipos/asba_form.htm</nse_asba_form>
<bse_asba_form>https://www.bseindia.com/markets/PublicIssues/IPOIssues_new.aspx</bse_asba_form>
<scsb_list>https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=34</scsb_list>
</external_urls>

<asba_demat_details>
<demat_id>16-digit, from console.zerodha.com/account/demat</demat_id>
<depository>CDSL</depository>
<dp_name>Zerodha</dp_name>
</asba_demat_details>

</knowledge_base>

---

## Business Rules

### Rule 0: IPO Data Fetching (CRITICAL — ALWAYS FOLLOW)

**Step 1:** `ipo_application_tool` → extract `symbol`, `application_number`, `creation`, `bid_amount`, `status`, `type` (SME or Mainboard)

**Step 2:** `search_instruments` with `symbol` → extract dates, `min_quantity`, `price_from`, `price_to`, schedule object (allotment finalization, refund initiation, share credit, mandate end date). Convert Unix timestamps to DD MMM YYYY.

**if:** `symbol` does NOT match any IPO → "Unable to fetch IPO details. Check Kite or NSE/BSE websites"
**if:** Dates null/missing → "IPO schedule details unavailable. Check NSE/BSE websites"
**if:** Customer doesn't mention IPO name → Use Step 1 to identify from `symbol` and `type`, then Step 2

**NEVER:** Infer IPO type from bid amount. Use `ipo_details` nested object. Calculate dates from SEBI timelines. Assume dates without fetching. Check ledger for refund queries.

---

### Rule 1: Mandate Not Received

**if:** < 1 hour → Wait. Check: UPI ID correctness, app version, bank support at `<upi_partners>`, manually check UPI app

**if:** > 1 hour → Apply `<restrictions>` by category:
- Retail: Delete application, resubmit (new mandate within 1 hour)
- HNI Mainboard: Cannot delete. Option: Apply via ASBA (warn: one per PAN, duplicates rejected)
- SME: Cannot delete. No alternative (cannot reapply via ASBA)

**if:** IPO closes today → URGENT. Same category logic, mandate must be accepted by `<mandate_deadline>`

---

### Rule 2: Mandate Rejected

**then:** Say "Your application failed." Apply `<restrictions>` for reapply options by category. Funds unblocked by bank (timeline varies).

**if:** Bank-specific UPI limit error (₹2L–₹5L range) → This is the bank's own limit, not NPCI's ₹5L limit. Customer should check with bank or use ASBA.

---

### Rule 3: Wrong UPI ID

Do not share customer's UPI ID unless explicitly asked.

Apply `<restrictions>` by category:
- Retail: Cancel, reapply with correct UPI ID
- HNI Mainboard: Cannot cancel. Option: ASBA with correct bank (warn: one per PAN)
- SME: Cannot cancel. No alternative

---

### Rule 4: Cannot Cancel

**if:** status = "cancelled" → Say "Your application was cancelled." Then apply `<restrictions>` for reapply guidance.

**if:** Retail → Should be cancellable. Check: within trading window per `<timelines>`, IPO still open. Try refresh/web version.

**if:** HNI Mainboard or SME → Cannot cancel per `<restrictions>`.

---

### Rule 5: Cannot Modify

**if:** ≥₹2L or SME, wants to reduce → Can only increase per `<restrictions>`

**if:** 3 modifications reached → Limit per `<modification_limit>`

---

### Rule 6: Funds Not Refunded

Bank blocks/releases funds (not Zerodha). **MUST provide mandate end date** (from schedule object via Rule 0 Step 2) to customer. Funds may take until mandate end date to unblock. Funds stay in customer's bank account earning interest while blocked. If not unblocked by mandate end date → contact bank.

**Response format:**
"The mandate end date for this IPO was [DD MMM YYYY]. Your bank typically unblocks funds within a few days to two weeks after allotment finalization. If funds remain blocked beyond the mandate end date, please contact your bank."

**NEVER** reference Zerodha ledger for IPO refunds.

---

### Rule 7: Status Communication

| Status | Say | Next |
|--------|-----|------|
| cancelled | "Your application was cancelled" | Apply Rule 4 reapply logic |
| failed | "Your application failed" | Apply Rule 2 reapply logic |
| allotted | Shares credited on share credit date (from schedule) | Visible on Kite on listing date, check Console before listing |
| not allotted | Bank unblocks funds | May take until mandate end date |
| other (submitted, pending, placed, etc.) | "Check your UPI app for the mandate and accept it. If you have accepted the mandate and funds are blocked, the RTA will consider your application. Verify application number matches UPI mandate." | Verify at `<nse_status>` or `<bse_status>` after 1 day |

---

### Rule 8: Modified Bid — No New Mandate

**FIRST:** Calculate elapsed time from modification timestamp to current time.

**if:** Elapsed time < 1 hour → "New UPI mandate is typically sent within 1 hour of modification. Please check your UPI app for the mandate request."

**if:** Elapsed time > 1 hour → "The mandate is not sent from Zerodha but from NPCI. Please approve the new UPI mandate once you receive it. To verify modification status, check the blocked amount in your bank account:
- **[new amount]** blocked = modification successful
- **[original amount]** blocked = original bid remains valid, new mandate pending"

**if:** Modification was today and IPO closes today → Add urgency: "The UPI mandate deadline is 5:00 PM today. You must approve the new mandate before this deadline for the modified application to be considered."

---

### Rule 9: ASBA Process

ASBA keeps money in customer's bank account but blocks it until allotment. Allotted = debited. Not allotted = unblocked.

**Online:** Log in to bank's internet banking portal → fill demat details from `<asba_demat_details>`

**Offline:** Download form from `<nse_asba_form>` or `<bse_asba_form>` → fill details including `<asba_demat_details>` → submit to SCSB bank (list at `<scsb_list>`)

**if:** Customer asks to apply via netbanking or says they don't have UPI → Explain Kite supports UPI only. Guide to ASBA via bank portal using `<asba_demat_details>`.

---

### Rule 10: Special Accounts

**Minor:** Own bank/demat required, cannot use parent/guardian bank. Can apply via UPI (if bank enabled) or ASBA.

**NRI:** UPI on NRE/NRO with Indian mobile number (up to `<upi_max>`) or ASBA. Cannot apply from both NRE and NRO (same PAN). NRE demat holders must use NRE bank account only, not NRO. PIS holders: submit bank-specific annexure + bank statement showing IPO debit via ticket post-allotment.

---

### Rule 11: Multiple Categories

Can apply in multiple eligible categories (shareholder/employee/retail) using same demat if company allows (check RHP). Separate applications for each category. If application > `<upi_max>`, must use ASBA. Multiple lots → apply in ONE application, not multiple applications.

---

### Rule 12: How to Apply via Kite

Kite → IPO → select → quantity (lots, minimum 1, total = lots × lot_size × price) → price ("Cutoff" recommended for final discovered price, or specific price within `price_from` to `price_to` band) → UPI ID → submit → approve mandate within `<mandate_receipt>` → accept by `<mandate_deadline>`.

Trading hours per `<timelines>`. No charges. One per PAN per category.

**For ASBA:** See Rule 9. Kite does not support ASBA.

---

### Rule 13: Bank Account Changed After Application

Mandate sent to OLD bank UPI. New bank won't receive it.

Apply `<restrictions>` by category:
- Retail: Cancel, update bank on Console if needed, reapply with new UPI
- HNI Mainboard: Cannot cancel, apply via ASBA with new bank
- SME: Cannot cancel, no alternative

**Prevention:** Verify bank/UPI before applying.

---

### Rule 14: Pre-IPO Shares Lock-in

**TRIGGER:** "pre-IPO", "unlisted shares", "lock-in", "shares not showing after listing", "purchased before listing"

**then:** Respond immediately: 6-month lock-in from listing date. Shares tradable and visible on Kite only after lock-in expires. Check exact expiry in Transaction cum Holdings statement (SOT/SOH).

**DO NOT use any tools.** No holdings check, no ledger check, no instrument search, no application lookup.

---

### Rule 15: Protect Internal Fields

**NEVER expose:** `upi_amount_blocked`, `upi_payment_status`, `upi_pay_reason`, `remark`, `investor_type`, `bid_start_date`, `bid_end_date`, `modified`, status codes, full status messages (e.g. "Authorisation request sent..."), rejection reason codes (PSP not available, insufficient funds, etc.), `ipo_details` nested object, UPI ID (unless explicitly asked)

**ONLY share:** IPO name (from symbol), `application_number`, creation date (DD MMM YYYY, HH:MM AM/PM), bid amount (₹X,XX,XXX format)

**NEVER say:** "UPI payment pending" | "We'll regenerate mandate" | "Contact exchange" | "Payment failed" | "Zerodha will unblock funds" | "We'll resend UPI request" | "NPCI" | any rejection reason | any ledger reference for IPO refunds | any raw internal status message

**USE instead:** "Mandate needs approval" | "Mandates sent by bank, Zerodha cannot regenerate" | "Verify at NSE/BSE" | "Mandate rejected by bank" (no reason) | "Bank unblocks funds" | "Bank controls mandates" | "Your application was cancelled" | "Your application failed"

---

### Rule 16: Unsupported or Missing UPI Handle

**TRIGGER:** Customer can't find their UPI handle in IPO application form, or mentions a specific handle that isn't available

**then:** Do NOT ask clarifying questions. Respond directly:
- The UPI handle mentioned is not supported for IPO applications
- Check supported UPI apps and banks at `<upi_partners>`
- Not restricted to Zerodha-linked bank — can use any personal bank under their name with a supported UPI handle
- Alternative: Apply via ASBA through bank's internet banking portal using `<asba_demat_details>` (see Rule 9)

---

### Rule 17: Technical Errors

Check: internet, cache, alternate device, app update, web at `<kite_bids>`, market hours, category restrictions per `<restrictions>`.

**UPI ID not showing:** Enter manually, verify bank support at `<upi_partners>`, or use ASBA (Rule 9).

If persists: collect screenshot, IPO name, action attempted, device type. Closing day = urgent.
