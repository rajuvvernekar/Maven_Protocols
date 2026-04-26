# Proposed Changes: sip_report
Date: 2026-03-12
Feedback entries: 4 issues

## Issue #1: Rule 1 Step 1 — reorder to check holdings first, add multi-SIP handling
**Problem**: Maven was going directly to FRESH order check without first confirming via holdings. Also wasn't handling multiple SIPs individually — gave generic responses.
**Current protocol** (exact section):
> ```
> 1. **CRITICAL — Zerodha SIP initial investment check (perform this first if `sip_type` = sip):**
> Check **mf_order_history** for a FRESH order (purchase_type = FRESH, variety = NRM/regular) for this fund.
>    - FRESH order not found → "No initial investment found for this fund. Please place a lumpsum order first. Once allotted and settled (T+2), the SIP will begin triggering."
>    - FRESH order found, status = Processing/Placed → "Your initial investment is still being processed. The SIP will trigger once the initial units are allotted and settled. Once allotted, pause and resume your SIP to update the next instalment date."
>    - FRESH order found, status = Failed/Cancelled → "Your initial investment was not completed. Please place a fresh lumpsum order. Once the lumpsum is allotted, pause and resume your SIP on Coin to ensure it triggers from the next cycle."
>    - FRESH order allotted → initial investment confirmed. Continue to Step 2.
> ```
**Proposed fix**:
```
1. **CRITICAL — Zerodha SIP initial investment check (perform for each affected SIP if `sip_type` = sip):**
For every Zerodha SIP the client is asking about, check **console_mf_pseudo_holdings** for that specific fund to confirm whether units exist.
   - **Units found** → initial investment confirmed for this fund. Continue to Step 2.
   - **No units found** → check mf_order_history for a FRESH order (purchase_type = FRESH) for that fund:
     - No FRESH order → initial investment never placed for this fund.
     - FRESH order Processing/Placed → initial investment still settling for this fund.
     - FRESH order Failed/Cancelled → initial investment was not completed for this fund.
   - **Name the fund explicitly in the response.** Do not give a generic "place a lumpsum" message.
   - **If multiple SIPs are affected:** Perform this check for each fund separately. List every fund missing initial investment by name: "We checked your SIPs and found that the following funds are missing an initial investment: [fund 1], [fund 2], [fund 3]. Please place a lumpsum order for each of these funds. Once the units are allotted and settled (T+2), the respective SIPs will begin triggering automatically."
```
**Root cause**: Incomplete logic

---

## Issue #2: Rule 1 Step 6.7 — NEW: stale next_sip_date check
**Problem**: SIPs where next_sip_date stops advancing had no handling. Maven would see an active SIP with a past date and have no guidance.
**Current protocol**: No existing step 6.7.
**Proposed fix** (insert after Step 6.6):
```
6.7. **Stale next_sip_date check (all SIP frequencies):**
**if:** `sip_status` = Active AND `next_sip_date` is before today's date
**then:** The SIP trigger has stalled and the next instalment date has not been updated. This applies to all frequencies: daily, weekly, fortnightly, and monthly.
Say: "Your SIP appears to have stalled — the next instalment date has not been updated as expected. Please pause and resume your SIP on Coin to re-sync the trigger date. Once resumed, your SIP will trigger from the next correct cycle. [How to modify, pause or delete a SIP on the Coin app?](https://support.zerodha.com/category/mutual-funds/coin-web-app/articles/modify-pause-delete-sip-coin)"
```
**Root cause**: Missing rule

---

## Issue #3: Rule 4 — NEW: NRI PIS Account mandate restriction
**Problem**: NRI PIS account holders were being told to create mandates which isn't possible for their account type.
**Current protocol**: No existing Rule 4.
**Proposed fix** (insert as new Rule 4, before current Rule 5):
```
### Rule 4: NRI PIS Account — Mandate Not Available
**if:** Client reports they cannot create a mandate for SIP, AND account type is NRI PIS (NRE account)
**then:** "Mandates for SIPs cannot be created for NRI PIS accounts. For SIP payments, each instalment will need to be paid manually using NEFT or RTGS. The payment must be made to the ICCL account unique to your Zerodha account. For detailed steps, refer to: [How to make payments using NEFT or RTGS on Coin?](https://support.zerodha.com/category/mutual-funds/payments-and-orders/payment-methods/articles/neft-rtgs-coin)"
```
**Root cause**: Missing rule

---

## Issue #4: Rule 6 — simplify escalation wording
**Problem**: Minor wording cleanup for SIP deletion failure escalation.
**Current protocol** (exact section):
> `**then:** ESCALATE TO AGENT immediately for manual handling. Do not ask for screenshots or troubleshoot further. "We are escalating this to our team for resolution. You can expect an update within 24-48 hours."`
**Proposed fix**:
```
**then:** ESCALATE TO AGENT immediately. "We are escalating this to our team for resolution. You can expect an update within 24-48 hours."
```
**Root cause**: Token efficiency
