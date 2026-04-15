# mf_order_history

## Description

WHEN TO USE:

When clients:
- Ask about any MF order (buy, sell, lumpsum, SIP order, NFO)
- Report payment debited but order not processed
- Ask about allotment timeline or unit credit
- Ask about NAV applied to order
- Ask about refund for cancelled/failed order
- Ask about order rejection reason
- Ask about NFO allotment status
- Report conditional order not visible
- Default first tool when specific Coin tool is unclear

TRIGGER KEYWORDS: "order", "status", "processing", "allotted", "failed", "cancelled", "rejected", "payment", "debited", "NAV", "refund", "NFO", "lumpsum", "buy", "when will", "units not showing", "conditional order", "UNRID", "coin"

## Protocol


---

### A1: Order Lifecycle

```
New → Placed → Processing → Allotted / Redeemed / Cancel / Failed
                    ↘ TPV Pending (auto-revalidates next business day)
```

| Internal Status | Client-Facing Language |
|---|---|
| Placed | "Your order has been placed and is pending processing at the exchange." |
| Processing | "Your order for [fund] of ₹[amount] is being processed by the AMC." |
| Allotted | "Your order has been allotted. Units credited to your demat." |
| Redeemed | "Redemption processed." + credit date per **A6**. |
| Cancel + payment_confirmed = true | "Your order was cancelled. The debited amount will be refunded to your source bank account within 5–7 working days (excluding weekends and holidays)." A cancelled order with confirmed payment means a refund is due — this is a refund scenario only. |
| Cancel + payment_confirmed = false | "Your order was cancelled. No payment was debited." |
| Failed | "Your order was not processed. Reason: [status_message in plain language]" |
| TPV Pending | "Your order is pending third-party bank account validation at the exchange. The exchange automatically re-validates pending orders on the next business day." |


### A2: Payment & NAV Rules

**MF payment flow:** Purchases are debited directly from client's bank account via ICCL — Kite balance is not involved. Redemption proceeds are credited directly to client's primary registered bank account. When discussing redemption credits, always direct client to check their primary bank account.

**T-day determination:** Governed by `payment_updated_at` (when payment was confirmed at ICCL). If not yet available, use `payment_initiated_at` as reference only and state that the applicable NAV depends on exchange confirmation.

**Working day check (apply first, before cutoff logic):** Before applying any cutoff logic, check whether `payment_updated_at` falls on a working day. If `payment_updated_at` falls on a weekend or trading/settlement holiday → T = next working day. If that next day is also a non-working day, shift further until a working day is reached. State: "Your payment was confirmed on [date], which was a [weekend/holiday — name it and state reason]. The order was processed on the next working day [date]." Only apply cutoff logic after confirming the payment date is a working day.

**Holiday shift scope:** The holiday shift rule applies only to the `payment_updated_at` date itself. If `payment_updated_at` falls on a working day and is before cutoff, T = that day regardless of whether the next day is a holiday. Holidays after T-day affect the settlement/allotment timeline (when units are allotted and appear in holdings), not the T-day or NAV date.

**Naming holidays:** When a weekend or holiday shifts the T-day or extends the settlement timeline, state each non-working day and whether it was a weekend or a trading/settlement holiday.

**NAV cutoffs (apply after T-day is established):**

| Fund Type | Payment Method | Before Cutoff | After Cutoff |
|---|---|---|---|
| Liquid | UPI / Netbanking (direct) | Before 12:30 PM → T-1 NAV | T = next working day |
| Liquid | Netbanking (non-direct) | Any time → T day NAV | — |
| Other | UPI / Netbanking (direct) | Before 2:00 PM → T day NAV | T = next working day |
| Other | Netbanking (non-direct) | Any time → T+1 NAV | — |
| Any | NEFT/RTGS/IMPS | NAV depends on ICCL settlement time (up to T+5) | — |
| Redemption | Any | Before 3:00 PM → T day NAV | T = next working day |

**Payment source mapping:**

| `fund_source` value | Meaning |
|---|---|
| rp_pg | Netbanking (payment gateway) |
| neft-rtgs | NEFT/RTGS/IMPS |
| digio_mandates | eNACH mandate |
| inapp_upi | In-app UPI |
| upi_mandates | UPI autopay |


### A3: Order Variety Mapping

| `variety` value | Meaning |
|---|---|
| NRM / empty | Lumpsum |
| SIP | SIP instalment (or STP purchase leg) |
| SWP | SWP redemption (or STP redemption leg) |
| XSP | Step-up / external SIP |
| GTT | Conditional order |

STP shows as two orders: SWP (redemption leg) + SIP (purchase leg).

`purchase_type`: FRESH = first-ever order in a fund; ADDITIONAL = subsequent order (SIP instalments, top-ups, repeat lumpsum).


### A4: Refund Rules

**Standard refund language (use this exact phrasing every time):**
> "The debited amount will be refunded by BSE STAR MF to your source bank account within 5–7 working days (excluding weekends and holidays)."

**Refund communication rules:**
- Always use only the standard language above.
- Refund status and real-time settlement details are internal processes managed by BSE STAR MF. Communicate only the standard timeline.
- Specific refund dates depend on BSE STAR MF processing — use the standard timeline range only.
- When trading/settlement holidays fall within the 5–7 working day refund window, mention them in the response so the client understands the extended calendar duration: "Due to [holiday name(s)] falling within the refund processing period, the working day count excludes these days, which may extend the calendar duration. Your refund is expected within the standard 5–7 working day window."

**Determining if payment was debited:**
- Always check `payment_confirmed` in mf_order_history first — this is the authoritative source. The trading ledger reflects trading account transactions, not MF payment confirmations.
- `payment_confirmed` = true → payment was debited, refund applies.
- `payment_confirmed` = false → no payment was debited.


### A5: Common Rejections

| `status_message` pattern | Cause | Action |
|---|---|---|
| INVALID BANK ACCOUNT DETAILS | Bank mismatch (typically after modification) | Escalate to support agent |
| SCHEME CLOSED | Scheme suspended | Use AMC SIP instead |
| REGISTER WITH AMC | Re-KYC required | Escalate to support agent |
| PAN/PEKRN MISMATCH | PAN issue | Verify PAN, submit copy. Escalate to support agent |
| DOB DIFFERS WITH PAN | DOB mismatch | Update DOB in Zerodha |
| E-KYC limit ₹50K/AMC | Incomplete KYC | Complete full KYC |
| NON ELIGIBLE SCHEME | Suspended/restricted | Inform client |
| FOLIO LOCKED KRA | KRA lock | Contact AMC directly. Escalate to support agent |
| INVALID MODE OF HOLDING | Minor account issue | Escalate to support agent |
| MINIMUM AMOUNT FAILED | Below scheme minimum | Inform client of minimum |
| UNITS NOT AUTHORISED | CDSL T-PIN missed | Must be completed same day before 3 PM. Place fresh order. Suggest DDPI. |
| UNITS NOT AUTHORISED — settlement holiday | CDSL authorization date did not match order process date due to a settlement holiday | "Your redemption request has been rejected due to a mismatch between the sell date and the order processed date due to the settlement holiday. The sell date for which the units were authorised on CDSL must match the order process date on which the order was processed and placed. Please place a fresh redemption order." |
| UNITS NOT AUTHORISED — near cutoff (non-holiday) | CDSL authorization date did not match order process date due to order placement near the 3:00 PM cutoff | "Your recent redemption order has been rejected. The order placement was near the cutoff time, and as a result, there was a mismatch between the CDSL authorisation and order process date. The sell date for which the units were authorised on CDSL must match the order process date on which the order was processed and placed. Please place a fresh redemption request." |
| UNRID | CDSL T-PIN authorization not completed | Same as UNITS NOT AUTHORISED. For SWP/STP orders: T-PIN authorization window is 10:00 AM (when SWP triggers) to 3:00 PM on trigger day. If missed → order cancelled. Suggest DDPI to avoid repeated authorizations. |
| UNRID — settlement holiday | Same date mismatch as UNITS NOT AUTHORISED — settlement holiday | Use the settlement holiday response above. |
| UNRID — near cutoff (non-holiday) | Same date mismatch as UNITS NOT AUTHORISED — near cutoff | Use the near-cutoff response above. |
| FREE QTY LESS | Insufficient unlocked units | Check pseudo_holdings for margin/pledged |
| UNIT NOT RECEIVED IN DEPOSITORY | Units not available in demat | Check console_mf_pseudo_holdings for pledged units (`margin`) and console_mf_tradebook for ELSS lock-in (FIFO from `trade_date`). If pledged → advise unpledging: Console → Portfolio → Holdings → [fund] → Unpledge. If ELSS locked → advise waiting for lock-in expiry per console_mf_tradebook Rule 1. |
| BANK ACCOUNT MISMATCH WITH UCC | Bank details not updated on BSE Star MF | escalate — agent review needed. |
| ER[XX] prefixed | AMC-level restriction | Share status_message verbatim |
| TPV INVALID | Bank validation failed | See Rule 3 (TPV Pending) |
| BSE infrastructure/database errors (e.g., "network-related or instance-specific error", "BSEMFDB", "Connection Timeout", "DUPLICATE UNIQUE REF NO", "CLIENT DOES NOT EXISTS", "PASSWORD EXPIRED", "login failed") | BSE STAR MF system-side failure — order failed due to exchange infrastructure issue | "As per the reverse feed received from BSE, there was a technical issue at the exchange level. Your payment will be refunded to your bank account within 7 working days. We apologize for the inconvenience." Apply **A4** refund language if `payment_confirmed` = true. |


### A6: Redemption Settlement Computation

1. **Determine T:** Order before 3:00 PM on a working day → T = that day. After 3:00 PM, or on weekend/settlement holiday → T = next working day. If that day is also a holiday, shift further. Refer to unconfirmed dates as "a holiday" — only name a holiday if explicitly confirmed in the data.
2. **Credit date:** Add `redemption_time` working days (Mon–Fri, excluding trading/settlement holidays) to T. `redemption_time` applies only to redemption (SELL) orders — it is the settlement period for redemption proceeds. If `redemption_time` is blank or null in the order data, do not assume a default settlement period. State: "The settlement timeline for this fund is being updated and will be available shortly."
3. **Response:** "Your redemption was processed on [T]. Based on [redemption_time] working days settlement, funds should be credited to your primary bank account by [date]."


### A7: Field Rules

**Shareable with client:** fund, amount, average_price (if asked), quantity (if asked), order_timestamp, exchange_timestamp, status_message, folio (if asked), redemption_time, transaction_type

**Internal reasoning only (use for analysis, communicate findings in plain language):** status, payment_confirmed, fund_source, variety, payment_initiated_at, payment_updated_at, payment_method, payment_remarks, purchase_type, exchange_order_id, unique_payment_id, payment_error_description, payment_error_code, tag (use for NFO detection: if `tag` contains `"product": "nfo"`, the order is an NFO order)

**Banned (internal infrastructure fields with no client relevance):** tradingsymbol, settlement_id, sip_id, payment_details, last_price, last_price_date

**Communication style:**
- Use customer-friendly language: "Your order was placed on [date]" rather than referencing system fields or tool names.
- Translate fund_allocation_report findings into plain language.
- `order_timestamp` records when the order was created. Cancellation time is not captured — communicate only that the order was cancelled after it was placed.
- Financial figures: Always display to 2 decimal places.
- Communicate payment failures in plain language: state that the payment failed and where in the process it failed (gateway, bank, exchange). Technical details such as error codes and system error descriptions are for internal diagnosis only — translate them into the cause before responding.


### A8: Key Facts

- Order history has a backend limitation of 180 days. For orders older than 180 days, use **console_mf_tradebook** — it has no time limitation. Always use console_mf_tradebook for verifying older allotments, historical trade entries, and XIRR-related checks that require complete buy/sell history.
- Stamp duty: 0.005% deducted from allotted units.
- Cancelled/failed order refunds: per **A4**.
- Zerodha fund house WhatsApp orders are processed separately and appear in AMC records, not in Coin order history.
- Console shows T-2 NAV; Coin shows T-1 NAV (P&L values may differ).
- NEFT/RTGS/IMPS payments go directly to ICCL and are tracked at the exchange level, not on Coin.
- Minor account MF purchases must use the minor's linked bank account. The guardian's bank account cannot be used. Kite balance is not used for MF purchases.
- When redeeming via CDSL portal, all MF holdings in demat are displayed. Only the selected fund's units will be redeemed. Recommend Coin app for a cleaner experience.
- ETF NFO allotment verification: check console_eq_external_trades for an "IPO" entry matching the fund. Order status in mf_order_history may remain "Processing" even after ETF NFO allotment is complete.
- MF units not in CDSL statement: "Units are held in demat with CDSL. Delays may be due to reporting cycles or PAN/email mismatches. Check monthly CAS email or view on Coin/Console."
- Client cannot view fund on Coin: Check console_mf_pseudo_holdings first. If holdings exist → escalate. If no holdings → ask for screenshot.
- Allotment timeline: Units are typically allotted within T+3 working days (excluding weekends and trading/settlement holidays) from `exchange_timestamp`. When explaining allotment timelines, compute T+3 from `exchange_timestamp` accounting for holidays. Once `exchange_timestamp` is established, it is the processing date. Holidays falling after that date are skipped when counting the T+3 working days, extending the allotment window. State the `exchange_timestamp` date as the processing date and count forward from it.


### A9: Links

| Purpose | URL |
|---|---|
| MF cutoff times | https://support.zerodha.com/category/mutual-funds/understanding-mutual-funds/buying/articles/cut-off-time-for-mutual-fund-transactions-on-coin |
| Payments on Coin | https://support.zerodha.com/category/mutual-funds/payments-and-orders/payment-methods/articles/complete-payments-purchase-orders-coin |
| NEFT/RTGS on Coin | https://support.zerodha.com/category/mutual-funds/payments-and-orders/payment-methods/articles/neft-rtgs-coin |
| Console NAV difference | https://support.zerodha.com/category/mutual-funds/coin-general/coin-reports/articles/mf-nav-of-t-2-days-on-console |
| How to redeem on Coin | https://support.zerodha.com/category/mutual-funds/coin-web-app/articles/redeem-sell-mutual-fund-investments |
| Reactivate account | https://support.zerodha.com/category/your-zerodha-account/your-profile/kyc-re-activation/articles/re-activate-my-account |
| MF units settlement timeline | https://support.zerodha.com/category/mutual-funds/features-on-coin/others-coin/articles/how-long-will-it-take-for-the-mutual-fund-units-to-show-up-in-my-demat-account |
| Convert resident account to NRI | https://support.zerodha.com/category/account-opening/nri-account-opening/process-nri/articles/convert-resident-account-to-nri-account |
| Delay allotment / NA units | https://support.zerodha.com/category/mutual-funds/payments-and-orders/orders-on-coin/articles/coin-app-na-new-units |


### A10: Direct vs Non-Direct Settlement Banks

Non-direct settlement banks report payments to the exchange on the next business day. This means the client receives T+1 NAV regardless of when the payment was made or confirmed before cutoff.

**Identifying the client's bank for a specific order:**
1. Check `payment_method` in the order. If `payment_method` = netbanking → proceed to identify the bank.
2. Extract `acc_number` from `payment_details`.
3. Match `acc_number` against `bank_1_account_number`, `bank_2_account_number`, `bank_3_account_number` from get_all_client_data.
4. Use the matching `bank_1_name` / `bank_2_name` / `bank_3_name` to identify the bank.
5. Check the bank against the classification below.

| Direct Settlement Banks | Non-Direct Settlement Banks |
|---|---|
| HDFC Bank | Allahabad Bank |
| ICICI Bank | Andhra Bank |
| State Bank of India (SBI) | AU Small Finance Bank |
| Axis Bank | Bank Of Baroda |
| Kotak Bank | Bank Of India |
| | Bank of Maharashtra |
| | Canara Bank |
| | Catholic Syrian Bank |
| | Central Bank of India |
| | City Union Bank |
| | Corporation Bank |
| | DCB |
| | Deutsche Bank AG |
| | Dhanalaxmi Bank |
| | Equitas Small Finance Bank |
| | Federal Bank |
| | IDBI Bank |
| | Indian Bank |
| | Indian Overseas Bank |
| | Jammu & Kashmir Bank |
| | Karnataka Bank |
| | Karur Vysya Bank |
| | Punjab National Bank |
| | South Indian Bank |
| | Standard Chartered |
| | SVC Co-operative Bank |
| | Tamilnad Mercantile Bank |
| | The Lakshmi Vilas Bank Limited |
| | The Ratnakar Bank Limited (RBL) |
| | The Saraswat Co-Operative Bank |
| | UCO Bank |
| | Union Bank of India |
| | IDFC Bank |
| | IndusInd Bank |
| | Yes Bank |


### A11: NRI MF Investment Eligibility

**Account requirement:** NRI clients must have an NRO or NRE type account to invest in MFs on Coin. Resident accounts cannot be used. Clients needing to convert from a resident account to NRI can follow the conversion process — KYC details are collected during the conversion itself.

**US/Canada restriction:** US/Canada-based NRIs currently cannot invest in any MF schemes on Coin due to technical restrictions.

**Dormant account:** If the account is dormant, it must be reactivated before investing.

**Support article:** [Convert resident account to NRI account](https://support.zerodha.com/category/account-opening/nri-account-opening/process-nri/articles/convert-resident-account-to-nri-account)


On every MF order query, execute in order:

```
1. PREFLIGHT
   ├─ get_all_client_data → check account status
   │   └─ If dormant → answer query normally, then append reactivation note (A9 link)
   ├─ Check transaction_type to determine BUY vs SELL
   ├─ If client mentions "withdrawal" + "Coin" or "mutual fund" → treat as redemption, check SELL orders
   ├─ MULTI-ORDER CHECK (run before any individual order diagnosis):
   │   Before diagnosing any individual order, list all orders for the queried fund
   │   within the relevant date range. If more than one order exists, diagnose each
   │   order independently — report the status of every order to the client. One order
   │   succeeding does not mean all orders succeeded.
   │   Map each order to its fund_allocation_report entry using exchange_order_id
   │   (mf_order_history) = order_number (fund_allocation_report). This is the only
   │   reliable way to match payment and settlement data to each individual order.
   │   Check payment_confirmed and status for EACH order individually.
   └─ Check if client is NRI → if query is about MF investment eligibility, route to Rule 10

2. ROUTE by status / intent
   ├─ Status = Processing → Rule 1
   ├─ Status = Failed → Rule 2
   ├─ Status = Cancel or TPV Pending → Rule 3
   ├─ Redemption issue (transaction_type = SELL) → Rule 4
   ├─ NAV dispute → Rule 5
   ├─ SIP query → Rule 6
   ├─ NEFT/RTGS/IMPS payment → Rule 7
   ├─ Payment gateway failures → Rule 8
   ├─ NRI MF investment eligibility / account conversion → Rule 10
   ├─ Duplicate/extra payment claims → Rule 11
   ├─ Order older than 180 days → "Check console_mf_tradebook for older records."
   └─ Escalation trigger → Rule 9

3. SCOPE
   Only address what the customer asked. Volunteer NAV details,
   cutoff explanations, SIP auto-debit behavior, or status of unrelated
   orders only when directly relevant to the reported issue.
```


---

### Rule 1: Processing Orders

**Step 0 — NEFT/RTGS check:**
If `status_message` contains "Pending payment via NEFT/RTGS" → **stop**, go to Rule 7.

**Step 1 — NFO check:**
Check the `tag` field for `"product": "nfo"` to identify NFO orders. If the order is an NFO → check mf_order_history for any NFO order for this fund within last 30 days:
- Allotted → "Your units have been allotted. NFO units appear in holdings only after the fund is listed, typically within 5 working days of allotment, then T+2 from listing date." If listing date is known from order data → share it. If not → use the standard 5 working days timeline. MF/FOF NFO → appears in Coin. The depository is not involved in this timeline.
- **ETF NFO — allotment verification:** ETF NFO units appear in Kite/Console equity holdings, not Coin. The order `status` may remain "Processing" even after allotment is complete. To confirm allotment, check console_eq_external_trades for an "IPO" entry matching the ETF NFO fund. If an IPO entry exists → allotment is complete. Inform: "Your ETF NFO units have been allotted and are available in your Kite holdings under [scrip name]. The order status on Coin may still show as Processing — this is expected for ETF NFOs."
- Still Processing (non-ETF NFO) → "Your NFO order is being processed. Status updates within T+2 after listing." Rejection remarks for NFO orders update only after the allotment window closes.
- Cannot determine → Escalate to support agent.

**Step 2 — Payment error check (run before any other status interpretation):**
Check `payment_error_code` and `payment_error_description` fields. If either field is present AND `payment_confirmed` = false → payment failed, regardless of what `status_message` shows. The order may display "Payment received" or "order sent to AMC" in status_message, but the error fields are authoritative. Respond: "Your order shows a processing status, but the payment was not successfully confirmed. Please place a new order and complete the payment. If your bank account was debited for the previous order, the amount will be refunded to your source bank account within 5–7 working days (excluding weekends and holidays)."

**Step 3 — Payment check:**
`payment_confirmed` = false (and no payment error from Step 2) → "Payment not confirmed. Allow 24 hours for gateway update."

For SIP orders (`variety` = sip): also check sip_report for the SIP's `fund_source`. If `fund_source` = `digio-mandates` or `upi-mandates` → mandate is linked, check mandate_debit_report for a debit entry on the order date. If a debit entry exists, apply the debit status per Mandate Debit Report **A2** translations to determine whether the debit succeeded, is pending, or failed. If `fund_source` = `rp-pg`, `pool`, or blank → no mandate-based debit occurred.

**Step 3a — Fast-track for confirmed payment beyond T+2:**
If `payment_confirmed` = true AND the order is beyond T+2 from `payment_updated_at` → proceed directly to Step 5 (fund_allocation_report cross-check). This order requires immediate investigation — payment was received but allotment has not completed within the expected window.

**Step 4 — Determine T-day:**

First check whether `payment_updated_at` falls on a working day per **A2**. If it falls on a weekend or trading/settlement holiday → set T = next working day and state which day(s) were non-working and why. If the next day is also a non-working day, shift further.

Then check `payment_method`. If `payment_method` = netbanking → identify the client's bank per **A10**. If the bank is a non-direct settlement bank → T-day shifts to the next business day regardless of cutoff. State: "Your payment was made via [bank name], which is a non-direct settlement bank. The payment was reported to the exchange on the next business day [date], so your order was placed on that date. Allotment is expected by [T+1]."

If `payment_method` is not netbanking, or the bank is a direct settlement bank, proceed with standard cutoff logic:
- Available + before cutoff → T = that day. "Allotment expected within T+1 business day."
- Available + after cutoff → T = next working day per **A2**. If that day is also a weekend or holiday, shift further until a working day is reached.
- Not yet available → use `payment_initiated_at` as reference. Share cutoff link from **A9**. State that the applicable NAV depends on exchange confirmation.

After determining T-day (whether from cutoff or holiday shift), cross-check using `exchange_timestamp` in mf_order_history. If `exchange_timestamp` date differs from the computed T-day, use `exchange_timestamp` date as the actual T-day — this confirms when the exchange processed the order. State the exact time and date from `payment_updated_at` in the response when explaining cutoff determination. If fund_allocation_report is available, verify against `payment_date` as well.

Allotment is expected within T+3 working days from `exchange_timestamp` (excluding weekends and trading/settlement holidays per **A8**). When explaining the timeline, name any holidays that fall within the T+3 window per **A2**.

**Step 5 — Within T+2, payment confirmed:**
Check **fund_allocation_report**. Map the order using `exchange_order_id` (mf_order_history) = `order_number` (fund_allocation_report).

Check `error_remarks` first:
- "INVALID BANK ACCOUNT DETAIL" → Escalate to support agent immediately.

Then check flags:
- `settled_flag` = Y, `allotment_flag` = Y, but still Processing → check whether `exchange_timestamp` is within T+3 working days (excluding weekends and trading/settlement holidays). If within T+3 → file sync delay is expected. "Your payment has been settled and units have been allotted by the AMC. Holdings typically update within T+3 working days from the exchange timestamp. Your holdings will update automatically." Share MF units settlement timeline link from **A9**. If beyond T+3 → escalate to support agent: "Order settled and allotted but holdings not updated beyond T+3."
- `settled_flag` = Y, `allotment_flag` = N → "Payment settled. Allotment expected by [date]."
- `settled_flag` = N → first check `order_number`: if `order_number` is null or empty in fund_allocation_report, the payment was received but never mapped to an order — this is a failed payment regardless of timeline. Apply **A4** refund language. If `order_number` is present, count working days from `payment_date` in fund_allocation_report (not from `order_timestamp` in mf_order_history):
  - Within T+1 → "Payment pending settlement. Allow one business day."
  - Beyond T+2 → order has failed. Check `refund_utr`:
    - Populated → "Payment could not be settled. Refund of ₹[amount] processed — use reference [refund_utr] to track with your bank."
    - Empty → apply **A4** refund language.

**Step 6 — Beyond T+3:**
Cross-check fund_allocation_report. No entry → escalate.

**Step 6.5 — payment_confirmed = true, settled_flag = N, beyond T+2:**
"Your order is likely to fail. Place a lumpsum order for the current cycle." + **A4** refund language.


### Rule 2: Failed Orders

Match `status_message` against **A5**. Communicate the cause in plain language — state what failed and why, translated from the technical status into a clear explanation for the client.

If `payment_confirmed` = true → apply **A4** refund language.

If multiple recent orders failing → check fund_allocation_report `error_remarks` for "INVALID BANK ACCOUNT DETAIL" → escalate if found.

Escalate if: INVALID BANK ACCOUNT, PAN/PEKRN MISMATCH, KRA LOCKED, MODE OF HOLDING, BANK ACCOUNT MISMATCH WITH UCC.


### Rule 3: Cancelled Orders & TPV Pending

**Cancelled:**

When multiple orders exist for the same fund (some successful, some cancelled), address every order the client asks about individually. For successful orders, confirm units were allotted. For cancelled orders, check `payment_confirmed` independently per **A4** and include the refund information in the response for each cancelled order where `payment_confirmed` = true. For cancelled orders with `payment_confirmed` = false, check further per the SIP mandate check below before concluding no payment was debited. A wrong refund determination directly contradicts the client's bank statement.

For SIP orders (`variety` = sip) cancelled after placement: if `payment_confirmed` = false, check sip_report for the SIP's `fund_source`. If `fund_source` = `digio-mandates` or `upi-mandates` → check mandate_debit_report for a debit entry on the same date. If debit status = Success or Created and funds were debited → a debit was initiated even though `payment_confirmed` has not updated. Apply **A4** refund language. If `fund_source` = `rp-pg`, `pool`, or blank → no mandate-based debit occurred, no payment was debited.

Cancellation time is not recorded — communicate only: "Your order was cancelled after it was placed."

**TPV Pending:**

1. Check `order_timestamp` to determine how many business days have elapsed.
2. "Your order is pending third-party bank account validation. The exchange automatically re-validates pending orders on the next business day."
3. "If the order is rejected due to the TPV pending status, the exchange performs a penny drop test on the bank account used for payment. If the bank account passes this test, the order status will be updated to allotted within 2 business days."
4. If the order status remains unchanged beyond T+3 (3 business days from `order_timestamp`) → ask the client to share their bank statement from the order date to present for further investigation.

If rejected after re-validation → check `status_message` for TPV INVALID per **A5**. Escalate to support agent.


### Rule 4: Redemption Issues

Redemption proceeds are credited directly to the client's primary registered bank account via the AMC. Always direct the client to check their primary bank account for redemption credits. Compute the expected credit date per **A6** using the actual `redemption_time` from order data. If `redemption_time` is blank or null, follow the fallback in **A6**.

**Step 0 — Cutoff check (run first for every redemption query):**
Check order time against the 3:00 PM cutoff per **A6** Step 1. If the order was placed after 3:00 PM on a working day, or on a weekend/settlement holiday → T shifts to the next working day. State this explicitly: "Your redemption was placed after the 3:00 PM cutoff, so it will be processed on the next working day [date]." Then compute credit date per **A6** from the adjusted T-day.

| Scenario | Response |
|---|---|
| Order after 3:00 PM | Next working day processing. Compute credit per **A6**. |
| UNITS NOT AUTHORISED | Per **A5**. CDSL T-PIN must be same day before 3 PM. Suggest DDPI. |
| FREE QTY LESS | Verify via console_mf_pseudo_holdings (margin/pledged) and console_mf_holdings for available units. |
| Redeemed, no bank credit | Compute expected date per **A6**. If beyond → escalate. |
| ELSS lock-in | Verify via console_mf_tradebook (FIFO from trade_date). |
| UI error, no order found | Clear cache, retry with fewer units, retry next day. If persists → escalate with screenshot. |
| TPV failed on redemption | Escalate to support agent. |
| CDSL portal showing all funds | "All MF holdings show during CDSL redemption — only selected units will be redeemed. Recommend using Coin app." Link: **A9**. |
| Units not visible post-allotment | Check console_mf_pseudo_holdings + console_mf_tradebook. Always use Coin MF tools for MF holdings verification. |
| NRI account + exit load/TDS dispute | Escalate to support agent. "For NRI accounts, TDS is deducted by the AMC per applicable tax rules." |
| Non-NRI exit load dispute | "Exit load is per the AMC's fund factsheet." → Escalate to support agent. |
| Client disputes redemption NAV (lower than published NAV for that date) | Escalate to support agent. "We are escalating this to our team for a detailed review of the redemption NAV applied to your order." |

**CDSL authorization loop (repeated OTP redirect):**
Occurs when recently allotted units haven't synced with CDSL. Units credited by 8 PM on settlement date; if delayed at RTA/CDSL, available for authorization on T+3 (second business day after settlement).

Response: "This occurs due to a delay in crediting recently purchased units to your CDSL demat account. Units are normally credited by 8 PM on the settlement date. If delayed, they will be available on the second business day after settlement (T+3). You can place a fresh redemption for your remaining units (excluding recently allotted ones) now, or wait until the next business day for holdings to sync. To avoid this in future, enable DDPI: Console → Settings → Account Authorization → complete DDPI activation using your Aadhaar-linked mobile number."


### Rule 5: NAV Disputes

**Step 1 — Identify payment method:**
Check `payment_method` in the order.
- If `status_message` contains "Pending payment via NEFT/RTGS" → NAV depends on ICCL settlement time only. Share NEFT/RTGS link from **A9**. Stop here.
- If `payment_method` = netbanking → proceed to Step 2.
- If UPI → proceed to Step 3.

**Step 2 — Netbanking: determine direct vs non-direct settlement bank:**
Identify the client's bank using the process in **A10** (extract `acc_number` from `payment_details` → match against bank account numbers in get_all_client_data → get bank name → check classification in **A10**).

If the client's bank is a non-direct settlement bank → "Your payment was made via [bank name], which is a non-direct settlement bank. For non-direct settlement banks, the payment is reported to the exchange on the next business day, so the next day's NAV applies regardless of when the payment was completed." Share MF cutoff times link from **A9**.
If direct settlement bank → proceed to Step 3.

**Step 3 — Check payment confirmation time against cutoffs:**
Use `payment_updated_at` vs **A2** cutoffs for the fund type. State the exact time and date from `payment_updated_at` in the response. To verify, map the order using `exchange_order_id` (mf_order_history) = `order_number` (fund_allocation_report) and cross-check with `payment_date` from fund_allocation_report.
- If `payment_updated_at` is after cutoff → "Your payment was confirmed at [time] on [date], which was after the [cutoff time] cutoff. The next working day's NAV was applied."
- If before cutoff → NAV should match T-day. Cross-check `payment_date` in fund_allocation_report.

Payment mapping: Match `exchange_order_id` = `settlement_number` in fund_allocation_report. This mapping applies to UPI and netbanking orders only.


### Rule 6: SIP Queries

**Step 0 — Fetch SIP details:**
Check **sip_report** for the fund → get `sip_type`, `next_sip_date`, `public_id`.

**Step 1 — Check initial investment (Zerodha SIPs only, `sip_type` = sip):**
SIP will not trigger until initial lumpsum is allotted and settled. Check **console_mf_pseudo_holdings** for the specific fund:
- Units found → initial investment confirmed. Go to Step 2.
- No units → check mf_order_history for FRESH order (`purchase_type` = FRESH):
  - No FRESH order → "No initial investment found for [fund]. Please place a lumpsum order first. Once allotted and settled (T+2), the SIP will begin triggering."
  - FRESH Processing/Placed → "Initial investment is still being processed. SIP will trigger once units are allotted and settled."
  - FRESH Failed/Cancelled → "Initial investment was not completed. Place a fresh lumpsum order. Once allotted, pause and resume the SIP to reset the trigger date."
- If multiple SIPs affected → check each fund separately. Name each fund explicitly.

**Step 2 — Check upcoming trigger:**
If `next_sip_date` within 5 days → check MF Order History for already-placed SIP order. Report actual status.

**SIP-specific facts:**
- SIPs trigger 2 days prior to preferred date.
- Zerodha SIP unpaid → auto-deleted T+4 calendar days. AMC SIP unpaid → T+5 business days.
- If `preferred_date` is within 2 days of initial order, SIP skips current month.
- AMC SIP can only be deleted (modification and pause are not supported). Deletion must be ≥2 days before next instalment. To change amount/date, delete and create new.
- For daily SIPs with linked mandate, orders are placed on T-1. Always check T-1 in order history before concluding an instalment is missing.
- Fortnightly SIP contribution counts depend on actual allotment dates. Always verify actual executed orders rather than assuming fixed triggers per month.
- AMC SIP allotment: always check full MF Order History by fund and date range, not just SIP order book.


### Rule 7: NEFT/RTGS/IMPS Payments

"Payments via NEFT/RTGS/IMPS are credited directly to ICCL and are tracked at the exchange level, not on Coin. Units will be allotted as per the settlement cycle." Link: **A9**.

- NAV based on ICCL settlement time (up to 24h from transfer).
- Payments mapped to orders on FIFO basis. Each incoming transfer is matched against open orders in order of placement. If a transfer amount meets or exceeds an order amount, that order is fulfilled. Remaining funds from the transfer carry forward to the next order.
- **Partial/split transfers:** If a client sends multiple smaller transfers intended for a single larger order, each transfer is mapped independently on FIFO. If no single transfer matches or exceeds the order amount, the order will fail. The unmatched amount will be reversed within 5–7 working days (excluding weekends and holidays). Example: a ₹40L order with two ₹20L transfers — ₹20L maps to the ₹40L order but does not fulfil it, so the order fails. However, if there were a ₹20L order and a ₹40L transfer, ₹20L would map to the order and the remaining ₹20L would carry forward.
- Common issue: transferred without selecting NEFT mode on Coin first → payment not received.
- Order still Processing beyond T+4 → "Your order is likely to fail. Please place a fresh order if needed."


### Rule 8: Payment Gateway Failures

If client reports repeated UPI or netbanking failures → suggest alternate method:
- UPI failing → try netbanking or NEFT/RTGS.
- Netbanking failing → try UPI or NEFT/RTGS.

Links: Payments on Coin and NEFT/RTGS on Coin from **A9**.

If all methods fail → escalate.


### Rule 9: Escalation Triggers

**Escalate to support agent with fund, amount, order_timestamp, and status_message when:**
- `status_message` contains: KRA, REGISTER WITH AMC, MODE OF HOLDING, TRANSMISSION, DESIGNATED PERSON, TAX STATUS, BANK ACCOUNT MISMATCH WITH UCC
- Client cannot find a scheme on Coin → "The scheme may be suspended or restricted."
- Client asks about transferring MF to/from another platform → "Demat transfer query requiring manual assistance."
- Client asks about children's fund / gift plans → these schemes are not available on Coin.
- INVALID BANK ACCOUNT DETAILS in any context.


### Rule 10: NRI MF Investment Eligibility

1. Check account type from get_all_client_data.

**Investment eligibility:**
- Account must be NRO or NRE type to invest in MFs on Coin (per **A11**).
- If account is a resident account → "To invest in mutual funds on Coin as an NRI, your account needs to be converted to an NRO or NRE account." Share the conversion support article from **A11**. KYC details are collected during the conversion process itself.
- If account is dormant → advise reactivation first. Share reactivation link from **A9**.

**US/Canada restriction:**
- If client is based in the US or Canada → "US/Canada-based NRIs currently cannot invest in MF schemes on Coin due to technical restrictions." (Per **A11**.)

**Account conversion queries:**
- If client asks how to convert their resident account to NRI → share the conversion support article from **A11**: "You can initiate the conversion from your Zerodha account. KYC details are collected as part of the conversion process."


### Rule 11: Duplicate/Extra Payment Claims

1. When a client claims extra or duplicate debits for MF orders: check fund_allocation_report for all entries on the order date. Look for entries without a matching `exchange_order_id` from mf_order_history (unmapped payments).
2. If an unmapped payment is found → apply **A4** refund language: "The debited amount will be refunded by BSE STAR MF to your source bank account within 5–7 working days (excluding weekends and holidays)."
3. If no unmapped payment is found → ask the client to share a bank statement showing the debit(s) with UTR numbers for further investigation.
