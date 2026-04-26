# Proposed Changes: mf_order_history
Date: 2026-03-12
Feedback entries: 10 issues

## Issue #1: Cancel status value — add allotment guard
**Problem**: Maven was implying cancelled orders with payment_confirmed=true might still get allotted.
**Current protocol** (exact section):
> `<cancel>Cancelled by client or system</cancel>`
**Proposed fix**:
```
<cancel>Cancelled by client or system — NEVER implies allotment. payment_confirmed = true means refund only.</cancel>
```
**Root cause**: Missing rule

---

## Issue #2: Rule 0 — remove redundant example
**Problem**: Example in field protection rule is redundant given Rule 0 already bans field names.
**Current protocol** (exact section):
> `**NEVER** surface raw data from fund_allocation_report directly in a client response — flags, reference numbers, and internal remarks are for reasoning only. Translate findings into plain language: say "your payment has been settled with the exchange" not "settled_flag = Y".`
**Proposed fix**:
```
**NEVER** surface raw data from fund_allocation_report directly in a client response — flags, reference numbers, and internal remarks are for reasoning only. Translate findings into plain language.
```
**Root cause**: Token efficiency

---

## Issue #3: Rule 0.1 — add multiple orders handling
**Problem**: Maven was only reporting the first order when multiple existed for the same fund in the queried date range.
**Current protocol** (exact section):
> `Only address what the customer explicitly asked. Do not volunteer NAV details, cutoff explanations, SIP auto-debit behavior, or status of unrelated orders unless the customer asks or it is the direct cause of the issue being reported. If multiple orders exist for a customer, only reference orders relevant to their specific query. Providing unsolicited information leads to follow-up queries and customer confusion.`
**Proposed fix**:
```
Only address what the customer explicitly asked. Do not volunteer NAV details, cutoff explanations, SIP auto-debit behavior, or status of unrelated orders unless the customer asks or it is the direct cause of the issue being reported.
**Multiple orders for the same fund:** When a client references a specific fund, check mf_order_history for ALL orders in that fund within the date range the client mentions. If multiple orders exist for the same fund, address each one separately — status, payment_confirmed, and next steps for each. Do not stop at the first match.
```
**Root cause**: Missing rule

---

## Issue #4: Rule 1 — expand Cancel status handling
**Problem**: Maven was not providing adequate cancel status responses, particularly for payment_confirmed=true cases.
**Current protocol** (exact section):
> `- Cancel → "Your order was cancelled." + refund if `payment_confirmed` = true`
**Proposed fix**:
```
- Cancel → "Your order was cancelled."
  - `payment_confirmed` = true → "The debited amount will be refunded to your source bank account within 5-7 working days (excluding weekends and holidays)." **NEVER state or imply that units will be allotted or the order will be processed — a cancelled order with payment_confirmed = true means a refund is due, not allotment.**
  - `payment_confirmed` = false → "No payment was debited."
```
**Root cause**: Missing rule

---

## Issue #5: Rule 2 Step 1 — expand NFO check
**Problem**: Maven was giving minimal NFO handling, often escalating unnecessarily instead of resolving NFO status directly.
**Current protocol** (exact section):
> ```
> **Step 1 — NFO check:**
> NFO → stays Processing until listing. "Status updates within T+2 after listing."
> - If client mentions "ETF" in the fund name AND units not visible on Coin → "ETF NFOs will appear in your Kite holdings after listing, not on Coin. Please check the Equity section on Kite or Console."
> - If ETF FOF (e.g., "Silver ETF FoF", "Gold ETF FoF") → check **console_mf_pseudo_holdings**, NOT Kite.
> - If allotted but not visible → check **console_mf_pseudo_holdings**. If units found → "Units allotted. Fund will appear in your holdings within T+2 working days of listing."
> - If cannot determine listing date → escalate to agent.
> ```
**Proposed fix**:
```
**Step 1 — NFO check:**
If fund is an NFO → do NOT escalate immediately. First check mf_order_history for any NFO order for this fund within the last 30 days (not just the date the client mentions).
- If NFO order found with status = Allotted → "Your units for [fund] have been allotted. NFO units are visible in your Coin holdings only after the fund is listed on the exchange. This typically takes up to 5 working days after allotment. Once listed, the fund will appear in your Coin holdings within T+2 working days of the listing date. No action is required from your end."
  - ETF NFO → "ETF NFOs appear in your Kite/Console equity holdings after listing, not on Coin."
  - MF/FOF NFO → "This fund will appear in your Coin holdings after listing."
- If listing date is known from order data → share it. If not → use the standard 5 working days timeline.
- Do NOT escalate to depository for this scenario.
- If NFO order still Processing → "Your NFO order is being processed. Status updates within T+2 after listing."
- If cannot determine order or listing date after checking → escalate to agent.
```
**Root cause**: Missing rule / Incomplete logic

---

## Issue #6: Rule 2 Step 3 — add payment_updated_at not available case
**Problem**: Maven was stating definitive T-days even when payment hadn't been confirmed at ICCL yet.
**Current protocol** (exact section):
> ```
> **Step 3 — Determine T-day:**
> Check `payment_updated_at` time against `<nav_cutoffs>` for the `fund_source` type and fund category. `payment_updated_at` is when the payment was reported to ICCL — this is the governing timestamp for NAV cut-off.
> - If `payment_updated_at` is before cut-off → T = that day. Proceed to Step 4.
> - If `payment_updated_at` is after cut-off → T = next working day. If that next working day falls on a weekend or settlement holiday, T shifts further to the next working day. Do NOT name the settlement holiday unless explicitly confirmed in the order data — say "a settlement holiday" instead.
> - Share: "The payment was reported to the exchange [before/after] the [cut-off time] cut-off. The order will be processed on [T] with [NAV date] NAV. Allotment expected within T+1 business day from [T]."
> ```
**Proposed fix**:
```
**Step 3 — Determine T-day:**
Check `payment_updated_at` (the timestamp when payment was confirmed at ICCL) against `<nav_cutoffs>` for the `fund_source` type and fund category.
- **If `payment_updated_at` is available** → use it as the governing timestamp for cut-off determination. Apply the rules below.
- **If `payment_updated_at` is NOT yet available** (payment still pending confirmation at ICCL) → use `payment_initiated_at` as reference only. Say: "Your payment was initiated on [payment_initiated_at date/time]. The applicable NAV will depend on when the payment is confirmed at the exchange. For cut-off time details, refer to: [What is the cut-off time for mutual fund transactions on Coin?](https://support.zerodha.com/category/mutual-funds/understanding-mutual-funds/buying/articles/cut-off-time-for-mutual-fund-transactions-on-coin)" Do not state a specific T-day or NAV in this case.
**When `payment_updated_at` is available, apply cut-off logic:**
- **If `payment_updated_at` is before cut-off** → T = that day. Say: "Your payment was received before the [cut-off time] cut-off on [payment date]. Your order has been placed with the exchange and allotment is expected within T+1 business day."
- **If `payment_updated_at` is after cut-off** → T = next working day. If that next working day falls on a weekend or settlement holiday, T shifts further to the next working day. Say: "Your payment was received after the [cut-off time] cut-off on [payment date]. As a result, your order was placed with the exchange on [T-day]. Allotment is expected by [T+1 working day]."
- Do NOT name any specific day as a holiday unless explicitly confirmed in the order data — say "a settlement holiday" instead.
```
**Root cause**: Missing rule

---

## Issue #7: Rule 2 Step 4 — split settled_flag=N into two cases
**Problem**: Maven was telling clients to "wait T+1" even when orders were well past T+2 and had clearly failed.
**Current protocol** (exact section):
> ```
>   - `settled_flag` = N → "Payment pending settlement. Allow T+1 business day."
> ```
**Proposed fix**:
```
  - `settled_flag` = N AND within T+1 business day → "Your payment is pending settlement with the exchange. Allow one business day."
  - `settled_flag` = N AND beyond T+2 business days → order has failed. Check `refund_utr` in fund_allocation_report:
    - `refund_utr` populated → "Your payment could not be settled. A refund of ₹[refund_amount] has been processed. Use reference number [refund_utr] to track it with your bank."
    - `refund_utr` empty → "Your payment could not be settled and the order will not be processed. The debited amount will be refunded to your bank account within 5-7 working days (excluding weekends and holidays)."
```
**Root cause**: Missing rule

---

## Issue #8: Rule 2.5 — fund-by-fund initial investment check
**Problem**: Maven was giving generic "place a lumpsum" responses without checking FRESH order status, and wasn't handling multiple SIPs individually.
**Current protocol** (exact section):
> ```
> 1. **Check initial investment first:** For Zerodha SIPs (`sip_type` = sip), the SIP will NOT trigger until the initial lumpsum order is allotted and settled. Check **console_mf_pseudo_holdings**. If no units → "The initial investment needs to be allotted first. Please place a lumpsum order. Once allotted, the SIP will trigger from the next cycle."
> 2. **Check upcoming trigger:** If `next_sip_date` (from **sip_report**) is within 5 days, check MF Order History for an already-placed SIP order and report its actual status.
> 3. **AMC SIP orders:** Always check the full MF Order History for allotment status. Do NOT rely only on the SIP order book. Search by fund name and date range.
> ```
**Proposed fix**:
```
1. **Check initial investment — fund by fund:** For Zerodha SIPs (`sip_type` = sip), the SIP will NOT trigger until the initial lumpsum order is allotted and settled. For each SIP in question, check **console_mf_pseudo_holdings** for that specific fund:
   - Units found → initial investment confirmed for this fund. Continue to Step 2.
   - No units found → check mf_order_history for a FRESH order (purchase_type = FRESH) for that fund:
     - No FRESH order → "No initial investment was found for [fund name]. Please place a lumpsum order for this fund first. Once allotted and settled (T+2), the SIP will begin triggering."
     - FRESH order Processing/Placed → "The initial investment for [fund name] is still being processed. The SIP will trigger once the units are allotted and settled."
     - FRESH order Failed/Cancelled → "The initial investment for [fund name] was not completed. Please place a fresh lumpsum order. Once allotted, pause and resume your SIP to reset the trigger date."
   - **If multiple SIPs are affected:** Perform this check for each fund separately and list all funds missing initial investment by name. Do not give a generic response — name each fund explicitly.
2. **Check upcoming trigger:** If `next_sip_date` (from **sip_report**) is within 5 days, check MF Order History for an already-placed SIP order and report its actual status.
3. **AMC SIP orders:** Always check the full MF Order History for allotment status. Do NOT rely only on the SIP order book. Search by fund name and date range.
```
**Root cause**: Missing rule / Incomplete logic

---

## Issue #9: Rule 4 — add ledger guard for MF payment confirmation
**Problem**: Maven was checking the trading ledger, finding no entry, and telling clients "no debit occurred" when payment was actually debited through ICCL.
**Current protocol** (exact section):
> ```
> ### Rule 4: Cancelled — Refund
> **if:** `status` = Cancel
> **then:**
> - `payment_confirmed` = true → "₹[amount] will be refunded by BSE STAR MF to your source bank account within 5-7 working days (excluding weekends and holidays)."
> - `payment_confirmed` = false → "No payment was debited."
> ```
**Proposed fix**:
```
### Rule 4: Cancelled — Refund
**if:** `status` = Cancel
**CRITICAL — Before concluding no payment was debited:**
NEVER conclude "no payment was made" or "no debit occurred" based on ledger checks alone. For ANY cancelled MF order refund query:
1. Check `payment_confirmed` in mf_order_history FIRST.
2. If `payment_confirmed` = true → payment was debited. Refund will be processed — do NOT say units will be allotted.
3. Only if `payment_confirmed` = false → "No payment was debited for this order."
The trading ledger is NOT a reliable source for MF payment confirmation — always use mf_order_history and fund_allocation_report.
**then:**
- `payment_confirmed` = true → "₹[amount] will be refunded by BSE STAR MF to your source bank account within 5-7 working days (excluding weekends and holidays)."
- `payment_confirmed` = false → "No payment was debited."
```
**Root cause**: Wrong logic

---

## Issue #10: Rule 6 — add CDSL authorization loop handling
**Problem**: No guidance for repeated OTP redirect during CDSL T-PIN authorization, likely resulting in generic troubleshooting or incorrect escalations.
**Current protocol**: No existing section for this scenario in Rule 6.
**Proposed fix** (append to Rule 6):
```
**CDSL authorization loop (repeated OTP redirect):**
**if:** Client reports CDSL T-PIN authorization keeps looping / returning to OTP page repeatedly after completing OTP
**then:** This occurs when recently allotted units have not yet synced with CDSL. Units are credited by 8 PM on settlement date; if delayed at RTA/CDSL, units are only available for authorization on T+3 (second business day after settlement date).
Say: "We regret the inconvenience. This issue occurs due to a delay in crediting recently purchased units to your CDSL demat account. Normally, units are credited by 8 PM on the settlement date. If there is a delay at RTA/CDSL, these units will be available for redemption and authorization on the second business day after the settlement date (T+3). Since your redemption request includes these recently allotted units, it cannot be authorized right now. You can place a fresh redemption request for your remaining units (total units minus the recently allotted ones) and authorize those. Alternatively, you can wait until the next business day for your holdings to sync with CDSL. To avoid this issue in future, we recommend enabling DDPI on your account — this removes the need for CDSL T-PIN authorization for every redemption. To enable DDPI: Log in to Console → Settings → Account Authorization → complete DDPI activation using your Aadhaar-linked mobile number."
```
**Root cause**: Missing rule

---

## Issue #11: Rule 16 — simplify NRI exit load handling
**Problem**: Extra disclaimer text is unnecessary since the rule already escalates to agent.
**Current protocol** (exact section):
> `- **If client account type is NRI** → Do not attribute to exit load. TDS on MF redemptions is deducted by the AMC directly — Zerodha does not control or deduct TDS. → ESCALATE TO AGENT. "For NRI accounts, TDS on mutual fund redemptions is deducted by the AMC as per applicable tax rules. Please contact the AMC directly for a TDS certificate and deduction breakdown."`
**Proposed fix**:
```
- **If client account type is NRI** → ESCALATE TO AGENT. "For NRI accounts, TDS on mutual fund redemptions is deducted by the AMC as per applicable tax rules. Please contact the AMC directly for a TDS certificate and deduction breakdown."
```
**Root cause**: Token efficiency
