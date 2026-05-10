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

TAGS: investments

## Protocol

# MF ORDER HISTORY PROTOCOL

---

## Section A: Reference Data

---

### A1 — Order Lifecycle and Status Values

```  
New → Placed → Processing → Allotted / Redeemed / Cancel / Failed  
                    ↘ TPV Pending (auto-revalidates next working day)  
```

| Status | What it means |  
|---|---|  
| Placed | Order is placed |  
| Processing | Order is being processed |  
| Allotted | Order is successfully allotted |  
| Redeemed | Redemption order is placed |  
| Cancel \+ `payment_confirmed` = true | Order is placed, payment is made, order is cancelled. Refund is due. |  
| Cancel \+ `payment_confirmed` = false | Order is placed and cancelled without payment. No refund applies. |  
| Failed | Order did not go through. See A5 for specific failure causes. |  
| TPV Pending | Pending third-party bank account validation at the exchange. |

---

### A2 — Payment & NAV Rules

**Entities:**  
- ICCL: receives client payments for MF orders.  
- BSE STAR MF: order aggregator that sends orders to the AMC once ICCL confirms the payment.

**Payment flow:** Purchases are debited directly from client's bank account via ICCL — Kite balance is not involved. Redemption proceeds are credited directly to client's primary registered bank account. For redemption credit queries, direct client to check their primary bank account.

**T-day (Trading day):** The date on which the order is processed at the exchange. T-day is determined by when the payment is confirmed at ICCL, captured in `payment_updated_at`. If `payment_updated_at` is not yet populated, use `payment_initiated_at` as reference — the applicable NAV depends on when the payment is updated at ICCL.

**Working-day check:** If `payment_updated_at` falls on a weekend or trading/settlement holiday, T = the next working day. If that day is also non-working, shift further until a working day is reached.

**Holiday shift scope:** The holiday shift applies only to the date on which `payment_updated_at` falls (or the order placement date for redemptions). Holidays after T-day affect the settlement/allotment timeline (when units appear in holdings), not T-day or the NAV date.

**Naming holidays:** When a weekend or holiday shifts T-day or extends a settlement timeline, state each non-working day and whether it was a weekend or a trading/settlement holiday.

**NAV cutoffs:**

| Fund type | Payment method | NAV rule |  
|---|---|---|  
| Liquid | UPI / Netbanking (direct) | Before 12:30 PM → T-1 NAV. After 12:30 PM → T-day NAV. |  
| Liquid | Netbanking (non-direct) | T-day NAV. |  
| Other | UPI / Netbanking (direct) | Before 2:00 PM → T-day NAV. After 2:00 PM → T = next working day. |  
| Other | Netbanking (non-direct) | T+1 NAV. |  
| Any | NEFT/RTGS/IMPS | NAV depends on ICCL settlement time (up to T+5). |  
| Redemption | Any | Before 3:00 PM → T-day NAV. After 3:00 PM → T = next working day. |

**Payment source mapping:**

| `fund_source` value | Meaning |  
|---|---|  
| rp_pg | Netbanking (payment gateway) |  
| neft-rtgs | NEFT/RTGS/IMPS |  
| digio_mandates | eNACH mandate |  
| inapp_upi | In-app UPI |  
| upi_mandates | UPI autopay |

---

### A3 — Order Variety Mapping

| `variety` value | Meaning |  
|---|---|  
| regular | Lumpsum order |  
| SIP | SIP instalment |

`purchase_type`: FRESH = first-ever order in a fund. ADDITIONAL = subsequent order (SIP instalments, top-ups, repeat lumpsum).

---

### A4 — Refund Statement

- Standard refund statement: "The debited amount will be refunded by BSE STAR MF to your source bank account within 5–7 working days (excluding weekends and holidays)."  
- When trading/settlement holidays fall within the 5–7 working day window, name the holidays in the response so the client understands the working-day count.

---

### A5 — Common Rejections

| `status_message` pattern | Cause category | Action |  
|---|---|---|  
| INVALID BANK ACCOUNT DETAILS, PAN/PEKRN MISMATCH, DOB DIFFERS WITH PAN, FOLIO LOCKED KRA, INVALID MODE OF HOLDING, BANK ACCOUNT MISMATCH WITH UCC, REGISTER WITH AMC | Account-level KYC or registration issue | Escalate to a human agent |  
| E-KYC limit ₹50K/AMC | Incomplete KYC — investment limit hit | Escalate to a human agent |  
| SCHEME CLOSED | Scheme suspended | Communicate the closure and suggest AMC SIP as an alternative |  
| NON ELIGIBLE SCHEME | Scheme suspended or restricted | Communicate that the scheme is unavailable |  
| MINIMUM AMOUNT FAILED | Order below scheme minimum | Communicate the scheme's minimum amount |  
| UNITS NOT AUTHORISED / UNRID | CDSL T-PIN authorisation not completed | T-PIN must be completed on the same day before 3 PM. Advise placing a fresh order and suggest enabling DDPI. For SWP/STP orders: T-PIN window is 10:00 AM (trigger) to 3:00 PM on trigger day; if missed, the order is cancelled. |  
| UNITS NOT AUTHORISED / UNRID — settlement holiday | Sell date authorised on CDSL did not match order process date due to a settlement holiday | Communicate that the sell date authorised on CDSL must match the order process date, and the mismatch was caused by the settlement holiday. Advise placing a fresh redemption order. |  
| UNITS NOT AUTHORISED / UNRID — near cutoff (non-holiday) | CDSL authorisation date did not match order process date due to order placement near the 3:00 PM cutoff | Communicate the same mismatch reason (sell date / order process date). Advise placing a fresh redemption order. |  
| FREE QTY LESS | Insufficient unlocked units | Invoke `console_mf_pseudo_holdings` for pledged units (`margin`). Communicate the actual available quantity. |  
| UNIT NOT RECEIVED IN DEPOSITORY | Units not in demat — pledged or ELSS locked | Invoke `console_mf_pseudo_holdings` for pledged units (`margin`) and invoke `console_mf_tradebook` for ELSS lock-in (FIFO from `trade_date`). If pledged → advise unpledging via Console → Portfolio → Holdings → [fund] → Unpledge. If ELSS locked → advise waiting for lock-in expiry. |  
| TPV INVALID | Bank validation failed on re-validation | See Rule 4 (TPV Pending) |  
| BSE STAR MF system-side errors (network-related or instance-specific error, BSEMFDB, Connection Timeout, DUPLICATE UNIQUE REF NO, CLIENT DOES NOT EXISTS, PASSWORD EXPIRED, login failed) | Exchange infrastructure issue | Communicate that there was a technical issue at the exchange. If `payment_confirmed` = true, apply A4 refund language. |  
| Buy/lumpsum option not available, only AMC SIP visible | AMC has suspended lumpsum investments due to valuation/size constraints; Zerodha SIPs (placed as lumpsum) are also affected | Communicate the AMC restriction. AMC SIP is available as an alternative. Share link from A9. |

---

### A6 — Redemption Settlement Computation

- **T-day:** Order placed before 3:00 PM on a working day → T = that day. After 3:00 PM, or on a weekend/settlement holiday → T = next working day. Holiday shift scope per A2.  
- **Credit date:** Add `redemption_time` working days (Monday–Friday, excluding trading/settlement holidays) to T. `redemption_time` applies only to redemption (SELL) orders — it is the settlement period for redemption proceeds.  
- **If `redemption_time` is blank or null:** Communicate that the settlement timeline for this fund is being updated and will be available shortly.

---

### A7 — Field Rules

**Shareable with client:**

| Field | Interpretation |  
|---|---|  
| `fund` | Name of the fund |  
| `amount` | Order amount in rupees |  
| `average_price` | Average allotment price per unit (share if asked) |  
| `quantity` | Number of units (share if asked) |  
| `order_timestamp` | When the order was placed (records order creation time only — cancellation time is not captured) |  
| `exchange_timestamp` | When the exchange processed the order |  
| `status_message` | Status description from the exchange |  
| `folio` | Folio number associated with the order (share if asked) |  
| `redemption_time` | Time of redemption processing |  
| `transaction_type` | Transaction type (purchase, redemption, SIP, etc.) |  
| `status` | Order status — translate per A1 status interpretation |  
| `payment_updated_at` | When payment was confirmed at ICCL; primary reference for T-day per A2 |  
| `payment_initiated_at` | When payment was initiated; fallback when `payment_updated_at` is not yet populated |

**Non-shareable:**

| Field | Interpretation |  
|---|---|  
| `tradingsymbol` | Internal trading symbol identifier for the instrument |  
| `sip_id` | Links the order to the associated SIP record |  
| `payment_details` | Raw payment data — internal use only |  
| `last_price` | Last NAV price at time of order |  
| `last_price_date` | Date of the last NAV used |  
| `payment_confirmed` | true = payment was debited; false = no payment debited |  
| `payment_error_code`, `payment_error_description` | Indicate payment failure reason |  
| `exchange_order_id`, `settlement_id` | Map the order to `fund_allocation_report` (by `order_number` or `settlement_number`) |  
| `unique_payment_id` | Internal payment reference |  
| `tag` | Detect NFO orders (value contains `"product": "nfo"`) |  
| `purchase_type` | See A3 |  
| `variety` | See A3 |  
| `payment_method` | Used to identify the bank per A10 for netbanking orders |  
| `fund_source` | Payment source — see A2 mapping |

---

### A8 — Key Facts

- Stamp duty: 0.005% deducted from allotted units.  
- Zerodha fund house WhatsApp orders are processed separately and appear in AMC records, not in Coin order history.  
- NAV display differs between platforms: Coin shows the NAV as of T-1 (previous working day); Console shows the NAV as of T-2 (two working days prior). P&L values on the two platforms may differ for this reason; both are correct for their respective display dates.  
- NEFT/RTGS/IMPS payments are credited directly to ICCL and cannot be tracked on Coin.  
- Minor account MF purchases must use the minor's linked bank account. The guardian's bank account cannot be used. Kite balance is not used for MF purchases.  
- Minor account initial investment: if the minor does not have access to NetBanking or UPI, NEFT/RTGS from the minor's linked bank account is the only available payment option for the initial investment. Subsequent SIP instalments can then be debited from the linked mandate.  
- CDSL redemption redirect: when a client places a redemption order and DDPI/POA is not enabled, they are redirected to the CDSL authorisation page. This page displays all the client's MF holdings in demat. The client can authorise any of the funds shown, but only the units selected for the specific redemption order will be redeemed.  
- CDSL authorisation loop (repeated OTP redirect): occurs when recently allotted units haven't synced with CDSL. Units are credited by 8 PM on the settlement date. If delayed at RTA/CDSL, units become available for authorisation on the second working day after settlement (T+3). Enabling DDPI avoids this loop in future.  
- ETF NFO allotment verification: invoke `console_eq_external_trades` and check for an 'IPO' entry matching the fund. Order status in `mf_order_history` may remain "Processing" even after ETF NFO allotment is complete.  
- MF units not in CDSL statement: units are held in demat with CDSL. Delays may be due to reporting cycles or PAN/email mismatches. Advise checking the monthly CAS email or viewing on Coin/Console.  
- Client cannot view a fund on Coin: invoke `console_mf_pseudo_holdings` first. If holdings exist → escalate. If no holdings → ask for a screenshot.  
- **Allotment timeline:** Units are expected to be allotted on T+1 (the next working day after `exchange_timestamp`). In some cases, late delivery of units to the demat account causes allotment to take longer than T+1 — up to T+3 working days (excluding weekends and trading/settlement holidays). When units are delivered late, NA is shown on Coin on T+2 (the day after the expected allotment) for one day only, and is rectified on T+3. Communicate this as late delivery of units, not as an allotment duration of T+3.  
- **Multi-order principle:** When the client's query involves multiple orders for the same fund, diagnose each order independently. One order succeeding does not mean all orders succeeded.  
- **SIP mechanics:**  
  - SIPs trigger 2 days prior to the preferred date.  
  - Zerodha SIP unpaid → auto-deleted at T+4 calendar days. AMC SIP unpaid → auto-deleted at T+5 working days.  
  - AMC SIP supports deletion only — modification and pause are not supported. Deletion must be at least 2 days before the next instalment. To change amount or date, delete and create a new SIP.  
  - For daily SIPs with a linked mandate, orders are placed on T-1.  
  - Fortnightly SIP contribution counts depend on actual allotment dates, not fixed monthly triggers.

---

### A9 — Links

| Purpose | URL |  
|---|---|  
| MF cutoff times | https://support.zerodha.com/category/mutual-funds/understanding-mutual-funds/buying/articles/cut-off-time-for-mutual-fund-transactions-on-coin |  
| How to make payments on Coin | https://support.zerodha.com/category/mutual-funds/payments-and-orders/payment-methods/articles/add-funds-coin-new |  
| How to pay via NEFT/RTGS on Coin | https://support.zerodha.com/category/mutual-funds/payments-and-orders/payment-methods/articles/neft-rtgs-coin |  
| Why NAV on Console differs from Coin (T-2 vs T-1) | https://support.zerodha.com/category/mutual-funds/coin-general/coin-reports/articles/mf-nav-of-t-2-days-on-console |  
| How to redeem on Coin app | https://support.zerodha.com/category/mutual-funds/understanding-mutual-funds/selling/articles/redeem-on-coin-app |  
| How to redeem on Coin web | https://support.zerodha.com/category/mutual-funds/understanding-mutual-funds/selling/articles/how-do-i-redeem-my-mutual-fund-units-on-coin |  
| Reactivate account | https://support.zerodha.com/category/your-zerodha-account/your-profile/kyc-re-activation/articles/re-activate-my-account |  
| MF units settlement timeline | https://support.zerodha.com/category/mutual-funds/features-on-coin/others-coin/articles/how-long-will-it-take-for-the-mutual-fund-units-to-show-up-in-my-demat-account |  
| Delay allotment / NA units | https://support.zerodha.com/category/mutual-funds/payments-and-orders/orders-on-coin/articles/coin-app-na-new-units |  
| Buy option not available | https://support.zerodha.com/category/mutual-funds/understanding-mutual-funds/buying/articles/unable-to-place-buy-order-in-mutual-funds |  
| Convert resident account to NRI | https://support.zerodha.com/category/account-opening/nri-account-opening/process-nri/articles/convert-resident-account-to-nri-account |

---

### A10 — Direct vs Non-Direct Settlement Banks

Non-direct settlement banks report payments to the exchange on the next working day. Because the exchange only registers the payment on the next working day, that next day becomes T-day for the order. This shift happens regardless of when the client made the payment or whether it was made before the cutoff.

**Direct Settlement Banks:**

| Bank |  
|---|  
| HDFC Bank |  
| ICICI Bank |  
| State Bank of India (SBI) |  
| Axis Bank |  
| Kotak Bank |

**Non-Direct Settlement Banks:**

| Bank |  
|---|  
| Allahabad Bank |  
| Andhra Bank |  
| AU Small Finance Bank |  
| Bank of Baroda |  
| Bank of India |  
| Bank of Maharashtra |  
| Canara Bank |  
| Catholic Syrian Bank |  
| Central Bank of India |  
| City Union Bank |  
| Corporation Bank |  
| DCB |  
| Deutsche Bank AG |  
| Dhanalaxmi Bank |  
| Equitas Small Finance Bank |  
| Federal Bank |  
| IDBI Bank |  
| Indian Bank |  
| Indian Overseas Bank |  
| Jammu & Kashmir Bank |  
| Karnataka Bank |  
| Karur Vysya Bank |  
| Punjab National Bank |  
| South Indian Bank |  
| Standard Chartered |  
| SVC Co-operative Bank |  
| Tamilnad Mercantile Bank |  
| The Lakshmi Vilas Bank Limited |  
| The Ratnakar Bank Limited (RBL) |  
| The Saraswat Co-Operative Bank |  
| UCO Bank |  
| Union Bank of India |  
| IDFC Bank |  
| IndusInd Bank |  
| Yes Bank |

---

### A11 — NRI MF Investment Eligibility

- **Account requirement:** NRI clients must have an NRO or NRE account to invest in MFs on Coin. KYC details are collected during the conversion process.  
- **US/Canada restriction:** US/Canada-based NRIs cannot invest in MF schemes on Coin due to technical restrictions.  
- **Dormant account:** If the account is dormant, it must be reactivated before investing. See A9 for the reactivation link.  
- Conversion support article: see A9.

---

## Section B: Decision Flow

### Routing

```  
Query relates to an MF order →  
├─ Order stuck in Processing / payment confirmed but units not allotted → Rule 1  
├─ Order failed (status = Failed or rejection message received) → Rule 2  
├─ Order cancelled — refund or status query → Rule 3  
├─ Order in TPV Pending status → Rule 4  
├─ Redemption — credit delay, CDSL auth issues, unit availability → Rule 5  
├─ NAV applied is incorrect or wrong NAV date → Rule 6  
├─ SIP — missed instalment, initial investment, schedule question → Rule 7  
├─ NEFT/RTGS/IMPS payment not reflecting on Coin → Rule 8  
├─ Repeated UPI or netbanking payment failures → Rule 9  
├─ NRI MF eligibility or resident-to-NRI account conversion → Rule 10  
├─ Duplicate or extra payment debited → Rule 11  
└─ Out-of-scope (children's/gift plans, scheme not on Coin) or miscellaneous escalation → Rule 12  
```

### Fallback

If no rule matches and no root cause is identified → escalate to a human agent.

---

## Section C: Rules

---

### Rule 1 — Processing Orders

**NEFT/RTGS payment:**

If `status_message` contains "Pending payment via NEFT/RTGS" → go to Rule 8.

**NFO order:**

If `tag` contains `"product": "nfo"`, the order follows NFO logic:

- **Allotted** → Communicate that units have been allotted. For MF/FOF NFO: units appear in Coin only after the fund is listed — typically within 5 working days of allotment; after listing, units are visible on Coin within T+2 working days. Share the listing date if known from order data. For ETF NFO: units appear in Kite/Console equity holdings, not Coin — invoke `console_eq_external_trades` and check for an 'ipo' entry matching the fund per A8.  
- **Still Processing — ETF NFO:** Invoke `console_eq_external_trades`. If an 'IPO' entry exists → communicate that units are in Kite holdings under the scrip name, even though order status on Coin shows Processing.  
- **Still Processing — non-ETF NFO:** Communicate that the NFO order is being processed and status updates within T+2 after listing. Rejection remarks for NFO orders update only after the allotment window closes. Share allotment quantities only if `mf_order_history` shows order status as 'Allotted'. Invoke `console_mf_pseudo_holdings` to check quantities — for NFO orders, these may be preliminary until allotment is officially confirmed.  
- **Cannot determine** → Escalate to a human agent.

**Payment not yet confirmed (`payment_confirmed` = false):**

For non-SIP orders:

1. Check `payment_error_code` and `payment_error_description`. If either is populated → payment failed. Communicate that the payment was not confirmed and advise placing a new order. Apply A4 refund language.  
2. If no error code is present, invoke `fund_allocation_report` using the order mapping per A7. If an entry exists, use its data to confirm what happened to the payment.  
3. If `fund_allocation_report` has no matching entry, the data is inconclusive. Apply A4 refund language conditionally (if the client's bank was debited, the refund will apply).

For SIP orders (`variety` = sip):

Invoke `sip_report` and check `fund_source`:  
- `fund_source` = `digio-mandates` or `upi-mandates` → mandate is linked. Invoke `mandate_debit_report` and check for a debit entry on the order date. Apply the debit status per Mandate Debit Report A4 translations.  
- Otherwise → no mandate linked.

**Determine T-day (when `payment_confirmed` = true):**

- Apply the working-day check from A2. If `payment_updated_at` falls on a weekend or trading/settlement holiday → T = next working day. State the non-working day(s) and reason.  
- For netbanking orders, identify the client's bank per A10. If the bank is a non-direct settlement bank → T shifts per A10. Communicate that the payment was made via a non-direct settlement bank, the payment was reported to the exchange on the next working day, and that became T-day; allotment is expected by T+1.  
- For UPI orders or netbanking with a direct settlement bank, apply NAV cutoff logic per A2:  
  - `payment_updated_at` is populated, before cutoff → T = that day. Allotment expected by T+1.  
  - `payment_updated_at` is populated, after cutoff → T shifts per A2 (for liquid funds, NAV moves from T-1 to T-day; for other funds, T = next working day). Further shift if that day is non-working.  
  - `payment_updated_at` is not yet populated → use `payment_initiated_at` as reference. Share the cutoff link from A9. Communicate that the applicable NAV depends on when the payment is updated at ICCL.  
- Cross-check T-day against `exchange_timestamp`. If they differ, use `exchange_timestamp` as the actual T-day (this confirms when the exchange processed the order). Invoke `fund_allocation_report` and verify against `payment_date` as well.  
- Allotment is expected on T+1 per A8. Name any holidays that fall within the window.

**Invoke `fund_allocation_report`:**

Map the order per A7.

Check flags:

- `settled_flag` = Y, `allotment_flag` = Y, status still Processing → units have been allotted. Within T+3 working days from `exchange_timestamp` → late delivery of units per A8. Communicate that the payment has been settled and units have been allotted by the AMC, and holdings may take up to T+3 working days to be credited due to late delivery. Share the MF units settlement timeline link from A9. Beyond T+3 → escalate to a human agent.  
- `settled_flag` = Y, `allotment_flag` = N, `mf_order_history` status = "Allotted" → allotment is finalised; units will be credited.  
- `settled_flag` = Y, `allotment_flag` = N, `mf_order_history` status ≠ "Allotted" → Communicate: "Payment settled. Allotment expected by [date]." — date = T+1 working day from `exchange_timestamp` per A8.  
- `settled_flag` = N → check the mapping columns first. If both `order_number` AND `settlement_number` are null or empty, the payment was received but never mapped to an order — this is a failed payment regardless of timeline. Apply A4 refund language. If either column is populated, the payment is mapped. Count working days from `payment_date` in `fund_allocation_report`:  
  - Within T+1 → Communicate: "Payment pending settlement. Allow one working day."  
  - Beyond T+2 → order has failed. Check `refund_utr`:  
    - Populated → Communicate that the refund of ₹[amount] has been processed; share the reference to track with the bank.  
    - Empty → Apply A4 refund language.

---

### Rule 2 — Failed Orders

- Match `status_message` against A5 and apply the Action column.  
- If `payment_confirmed` = true → apply A4 refund language alongside the failure cause.  
- If the client has multiple recent failed orders → invoke `fund_allocation_report` and check `error_remarks` for "INVALID BANK ACCOUNT DETAIL". If found → escalate to a human agent.

---

### Rule 3 — Cancelled Orders

For cancelled orders, apply A1 status interpretation based on `payment_confirmed`:  
- `payment_confirmed` = true → apply A4 refund language.  
- `payment_confirmed` = false → proceed to the SIP check below before concluding no payment was debited.

**SIP cancelled with `payment_confirmed` = false:** For SIP orders (`variety` = sip) cancelled after placement, invoke `sip_report` and check `fund_source`:  
- `fund_source` = `digio-mandates` or `upi-mandates` → mandate is linked. Invoke `mandate_debit_report` and check for a debit entry on the same date. If debit status = Success or Created and funds were debited → a debit was initiated even though `payment_confirmed` has not updated. Apply A4 refund language.  
- Otherwise → no mandate linked. No payment was debited.

---

### Rule 4 — TPV Pending

- Check `order_timestamp` to determine working days elapsed.  
- Within T+3 working days from `order_timestamp` → Communicate that the order is pending third-party bank account validation. The exchange automatically re-validates pending orders on the next working day. If the order is rejected due to TPV pending status, the exchange performs a penny drop test on the bank account used for payment. If the account passes, the order status updates to allotted within 2 working days.  
- Beyond T+3 working days from `order_timestamp`, status unchanged → Ask the client to share their bank statement from the order date to present. Escalate to a human agent with the bank statement.  
- Rejected after re-validation (`status_message` contains TPV INVALID, per A5) → Escalate to a human agent.

---

### Rule 5 — Redemption Issues

**Redemption order check:**  
Check `transaction_type` = SELL. If no SELL order is found → ask the client for the fund name and when the order was placed.

- Compute expected credit date per A6 using `redemption_time` from order data.  
- Apply A6 cutoff logic first: if the order was placed after 3:00 PM on a working day, or on a weekend/settlement holiday, T shifts to the next working day. State the adjusted T-day and compute credit per A6.

Match the client's scenario:

| Scenario | What to do |  
|---|---|  
| Order after cutoff | Communicate the adjusted T-day and expected credit date per A6. |  
| UNITS NOT AUTHORISED / UNRID | Per A5. |  
| FREE QTY LESS | Invoke `console_mf_pseudo_holdings` for pledged units (`margin`) and `console_mf_holdings` for available units. Communicate the actual available quantity and the reason for the difference (margin or pledge reduces free qty). |  
| Redeemed, no bank credit | Compute expected credit date per A6. Within the window → communicate the expected date. Beyond → escalate to a human agent. |  
| ELSS lock-in | Invoke `console_mf_tradebook` and follow FIFO from `trade_date`. Communicate which units are under lock-in and when eligible units become available. |  
| UI error, no order found | Advise clearing cache, retrying with fewer units, retrying the next day. If persistent → escalate to a human agent with screenshot. |  
| TPV failed on redemption | Escalate to a human agent. |  
| CDSL portal showing all funds | Apply A8 CDSL redemption redirect explanation. Share redemption links from A9. |  
| NRI account \+ exit load/TDS dispute | Escalate to a human agent. |  
| Non-NRI exit load dispute | Escalate to a human agent. |  
| Client disputes redemption NAV (lower than published NAV for that date) | Escalate to a human agent. |  
| Repeated OTP redirect on CDSL authorisation | Apply A8 CDSL authorisation loop context. Advise the client of the two options: place a fresh redemption for remaining units (excluding recently allotted ones), or wait until the next working day for holdings to sync. Suggest enabling DDPI via Console → Settings → Account Authorization (using the Aadhaar-linked mobile number) to avoid this in future. |

---

### Rule 6 — NAV Disputes

- Check `payment_method`:  
  - `status_message` contains "Pending payment via NEFT/RTGS" → NAV depends on ICCL settlement time only. Share the NEFT/RTGS link from A9. Go to Rule 8.  
  - `payment_method` = netbanking → identify the bank per A10. If non-direct settlement bank → communicate that the bank is non-direct, the payment was reported to the exchange on the next working day, and T-day shifted accordingly with the corresponding NAV applying per A2. Share the MF cutoff times link from A9. If direct settlement bank → proceed to cutoff check.  
  - `payment_method` = UPI → proceed to cutoff check.

- **Cutoff check:** Compare `payment_updated_at` against A2 cutoffs for the fund type. State the exact time and date from `payment_updated_at`.  
- Invoke `fund_allocation_report` and cross-check `payment_date`. This verification applies to UPI and netbanking orders only — NEFT/RTGS/IMPS payments do not appear in `fund_allocation_report` (see Rule 8).  
  - `payment_updated_at` after cutoff → communicate the confirmation time and applicable NAV per A2.  
  - `payment_updated_at` before cutoff → NAV should match T-day per A2.

---

### Rule 7 — SIP Queries

Invoke `sip_report`.

**Initial investment check (Zerodha SIPs only, `sip_type` = sip):**

The SIP will not trigger until the initial lumpsum is allotted and settled. Invoke `console_mf_pseudo_holdings` for the specific fund:

- **Units found** → initial investment confirmed. Proceed to the trigger check below.  
- **No units** → check for a FRESH order (`purchase_type` = FRESH):  
  - **No FRESH order** → Communicate that no initial investment was found for the fund, advise placing a lumpsum order, and state that the next SIP instalment is scheduled for `next_sip_date`. The SIP will trigger only after the initial lumpsum is allotted and settled.  
  - **FRESH Processing/Placed** → Check `preferred_date` against initial order date. If `preferred_date` is within 2 days of the initial order, the SIP skips the current month and moves to the next cycle. Communicate that the initial investment is being processed, the SIP will trigger once units are allotted and settled, and state the next SIP date. If the cycle-skip applies, state it.  
  - **FRESH Failed/Cancelled** → Communicate that the initial investment was not completed. Advise placing a fresh lumpsum order and, once units are allotted, pausing and resuming the SIP to reset the trigger date. State the current `next_sip_date`.  
- If multiple SIPs are affected → check each fund separately and name each explicitly.

**Upcoming or recent trigger:** If `next_sip_date` is within 5 days, or the client asks about a missed/recent instalment → check order history for the SIP order around that date. Report the actual status and apply the relevant rule (Rule 1/2/3/4) for the status found.

---

### Rule 8 — NEFT/RTGS/IMPS Payments

- Communicate that payments via NEFT/RTGS/IMPS are credited directly to ICCL and are tracked at the exchange level, not on Coin. Units will be allotted as per the settlement cycle. Share the NEFT/RTGS link from A9.

**Payment mapping mechanics:**  
- NAV is based on ICCL settlement time (up to 24 hours from transfer).  
- Payments are mapped to orders on a FIFO basis. Each incoming transfer is matched against open orders in order of placement. If a transfer amount meets or exceeds an order amount, that order is fulfilled. Remaining funds carry forward to the next order.  
- **Partial/split transfers:** If a client sends multiple smaller transfers intended for a single larger order, each transfer is mapped independently on FIFO. If no single transfer matches or exceeds the order amount, the order will fail and the unmatched amount will be reversed (apply A4 refund language). Example: a ₹40L order with two ₹20L transfers — ₹20L maps to the ₹40L order but does not fulfil it, so the order fails. Conversely, a ₹20L order with a ₹40L transfer fulfils the ₹20L order, and the remaining ₹20L carries forward.  
- Common issue: the client transferred without selecting NEFT mode on Coin first → payment not received.

- Order still Processing beyond T+4 → communicate that the order is unlikely to go through and advise placing a fresh order if needed.

---

### Rule 9 — Payment Gateway Failures

- UPI failing repeatedly → suggest netbanking or NEFT/RTGS.  
- Netbanking failing repeatedly → suggest UPI or NEFT/RTGS.  
- All methods failing → escalate to a human agent.

Share Payments on Coin and NEFT/RTGS on Coin links from A9 where relevant.

---

### Rule 10 — NRI MF Investment Eligibility

- From ‘get_all_client_data’, check account type details and then apply A11 based on the following fields:  
  - `account_type` indicates a resident account (for a client who has become an NRI) → advise conversion to NRO or NRE. Share the conversion support article from A9.  
  - `starmf_status` = "MF inactive" → advise reactivation first. Share the reactivation link from A9.  
  - `communication_country` = USA or Canada → communicate the technical restriction per A11.  
  - Conversion query (client intent, no data check needed) → share the conversion support article from A9. KYC details are collected as part of the conversion.

---

### Rule 11 — Duplicate/Extra Payment Claims

- Invoke `fund_allocation_report` for all entries on the order date. An unmapped payment is a row where both `order_number` AND `settlement_number` are null or empty — the payment was received but never mapped to any `mf_order_history` order.  
  - Unmapped payment found → apply A4 refund language.  
  - No unmapped payment found → ask the client to share a bank statement showing the debit(s) with UTR numbers for further investigation.

---

### Rule 12 — Out-of-scope and Miscellaneous Escalations

- Client cannot find a scheme on Coin → communicate that the scheme may be suspended or restricted.  
- Client asks about children's fund or gift plans → communicate that these schemes are not available on Coin.  
- `status_message` contains TRANSMISSION, DESIGNATED PERSON, or TAX STATUS → escalate to a human agent with fund, amount, `order_timestamp`, and `status_message`.
