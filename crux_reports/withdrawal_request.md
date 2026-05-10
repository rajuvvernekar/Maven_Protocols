# withdrawal_request

## Description

WHEN TO USE:

When clients:
- Ask about withdrawal status ("processed but not received", "where is my money", "withdrawal failed")
- Are unable to withdraw money ("showing 0 withdrawable", "withdrawal rejected", "can't withdraw")
- Ask about instant withdrawal errors ("getting error", "instant withdrawal not working")
- Report receiving partial amount ("withdrew X but got Y", "less amount processed", "partial payout")
- Ask about withdrawal timeline ("when will I get money", "how long does it take", "when will funds settle")
- Ask about negative withdrawable balance ("showing negative amount", "minus balance", "delayed payment charges", "interest on negative balance")
- Ask to expedite/fasttrack withdrawal ("need money urgently", "please process faster")
- Ask about withdrawal from dormant or minor account
- Have NRI PIS account and ask about withdrawal
- Confuse holdings value with withdrawable balance ("sell holdings and withdraw", "holdings withdrawal")

TRIGGER KEYWORDS: "withdraw", "withdrawal", "payout", "transfer to bank", "not received", "not credited", "processed", "failed", "rejected", "withdrawable balance", "instant withdrawal", "regular withdrawal", "0 balance", "negative balance", "partial payout", "less amount processed", "NRI withdrawal", "NRI PIS", "sell holdings and withdraw", "delayed payment charges", "when will funds settle", "same day credit"

TAGS: funds

## Protocol

# WITHDRAWAL PROTOCOL

---

## Section A: Reference Data

---

### A1 — Withdrawal Types

| Field Value | Label | Amount Range | Frequency | Window | Credit Timeline | Cancellable |    
|---|---|---|---|---|---|---|    
| `Instant_Payout` | Instant | ₹100–₹2,00,000 | Once per day (regardless of outcome) | 09:00–16:00 daily (incl. weekends; intermittent before 09:25) | Within minutes | No |    
| `Payout` | Regular | ₹1 to available balance (up to ₹5 crore via Console) | No daily limit | At applicable cutoff (per A4) | Within 24h of processing | Yes — while Pending, via Console → Funds → Withdrawal history |

-One instant and one regular can be pending simultaneously. A pending regular withdrawal has no effect on instant availability. Regular withdrawals are automated and cannot be expedited.

---

### A2 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |    
|---|---|    
| `payout_type` | `Instant_Payout` = instant withdrawal; `Payout` = regular withdrawal |    
| `status` | Current withdrawal request status |    
| `creation` | Date and time the client placed the request |    
| `payout_date` | Date when Zerodha processed the request |    
| `modified` | Credit time if `bank_ref_no` is present; otherwise last update time |    
| `amount` | Withdrawal amount requested |    
| `bank_ref_no` / `bank_reference_no` | Bank reference number |    
| `processed_amount` | Amount processed |

**Non-shareable:**

| Field | Interpretation |    
|---|---|    
| `bank_response_remarks` | Bank's response description |    
| `bank_response_status` | Bank's response code/status |    
| `payout_category` | Internal payout category classification |    
| `remarks` | Internal processing remarks |    
| `client_id` | Internal client identifier |

---

### A3 — Instant Eligibility

| Category | Blocker / Scenario | Effect |    
|---|---|---|    
| Full-day blocker (instant only) | Any orders on the query date (status = pending / executed / rejected / cancelled), except CNC sell executed | Instant unavailable for the entire day |    
| Full-day blocker (instant only) | Any positions on the query date (open or closed), except CNC sell executed | Instant unavailable for the entire day |    
| Full-day blocker (instant only) | Orbis-linked account | Instant unavailable for the entire day |    
| Full-day blocker (instant only) | Non-whole-number withdrawal amount | Instant unavailable for the entire day |    
| Account-level blocker | Paytm Payments Bank as primary bank account | Blocks both instant and regular |    
| Fund availability | Same-day deposit (weekday) | Funds deposited today not available for instant withdrawal today |    
| Fund availability | Deposit on Saturday, Sunday, or settlement holiday | Funds deposited that day not available for instant withdrawal on next working day |

Confirmed non-blockers: GTT orders, pending regular withdrawals.

---

### A4 — Processing Cutoffs (Regular Withdrawal / Payout only)

| Condition | Processed at | Credit by |    
|---|---|---|    
| Saturday | 16:30 | Within 24h |    
| Sunday / settlement holiday | Next working day cutoff | Within 24h of processing |    
| Weekday \+ ZBL_MCX active | 23:59 | Within 24h |    
| Weekday \+ before 17:00 \+ no trades/positions/instant \+ sufficient balance | \~17:00 same day | Same-day bank credit |    
| Weekday \+ before 17:00 \+ has trades/positions/instant | 22:00 | Within 24h |    
| Weekday \+ after 17:00 (no ZBL_MCX) | 22:00 | Within 24h |

---

### A5 — T+1 Settlement Rule

| Aspect | Detail |    
|---|---|    
| Definition | Funds from trades (equity, F&O, MCX, CDS) and same-day deposits appear in the account balance on the same day but are not withdrawable until T+1 (next working day, excluding weekends and settlement holidays) |    
| Stock sales | Credit appears in ledger same day (after 19:00–21:00 update); withdrawable only after T+1 settlement completes |    
| Intraday / F&O trades | T+1 applies to realised profits, mark-to-market (M2M), and option sell value |    
| Ledger signal | DP charges on a date confirm a stock sale on that date; T+1 settlement is the cause for the withdrawal restriction |    
| Balance display | Settlement credits appear in ledger same day; only withdrawal eligibility follows T+1 |

The official settlement holiday list is the authoritative source for confirmed settlement holidays. Settlement holidays defer T+1 settlement by one working day. Dates not on the list are not confirmed holidays.

---

### A6 — Reversal Terminology

| Scenario | Correct Framing |    
|---|---|    
| Bank rejected (funds were sent to bank, returned by bank) | Funds reversed to trading account |    
| T+1 / same-day deposit / balance shortfall (funds never left the trading account) | Request did not go through; funds remained in the trading account throughout |

"Reversed" applies only when funds actually left the trading account and were returned by the bank.

---

### A7 — Bank Rejection Reference

| Signal | Meaning |    
|---|---|    
| `bank_response_status` = failed | Transaction rejected by the bank; funds to be reversed to the trading account |    
| Ledger entry: remarks contain "Transfer rejected by bank" | Reversal complete; funds are back in the trading account |    
| `bank_response_remarks` contains "NPCI" | Rejection originated from the client's bank payment network (NPCI), not from Zerodha |    
| `bank_response_status` = failed \+ no "Transfer rejected by bank" ledger entry | Reversal in progress; funds expected back within 24–48 working hours |

- **Post-rejection — instant:** An instant withdrawal counts as the day's single attempt whether it succeeds or fails. Regular withdrawal remains available for the rest of the day.

---

### A8 — Ledger Translation

| Voucher Type | Remarks Pattern | Meaning | Withdrawal Impact |    
|---|---|---|---|    
| Bank Receipts | On creation/query date (weekday) | Same-day deposit | Not withdrawable until next working day |    
| Bank Receipts | On Saturday or Sunday | Weekend deposit | Regular: available now. Instant: available Tuesday |    
| Book Voucher | "Net settlement for Equity..." | Equity trade settlement | T+1 per A5 |    
| Book Voucher | "Net obligation for Equity F&O" | F&O trade settlement | T+1 per A5 |    
| Book Voucher | "Net obligation for MCX commodity FNO" | MCX commodity trade settlement | T+1 per A5 |    
| Book Voucher | "Net obligation for CDS FNO" | CDS currency trade settlement | T+1 per A5 |    
| Journal Entry | "DP Charges for Sale of [STOCK] on [DATE]" | Stock sold that day | T+1 per A5 |    
| Journal Entry | "Delayed payment charges for [Month] - [Year]" | Delayed payment charges | Client must add funds to clear dues |    
| Bank Payments | Remarks containing "quarterly settlement" | Quarterly settlement payout | Funds transferred to client's primary bank account via mandatory quarterly settlement; trading account balance reduced accordingly |    
| — | Time 19:00–21:00, no other signals | Balance update window | Retry after 21:00 |

---

### A9 — Withdrawable Balance Reference

| Fact | Detail |    
|---|---|    
| Available Cash vs Available Margin | `kite_margins` returns both values. Available Cash excludes collateral; Available Margin includes collateral. Only Available Cash reflects withdrawable funds. |    
| Collateral margin accounts | For accounts with collateral, Available Cash in `kite_margins` may not reflect the true withdrawable balance; `ledger_report` provides the accurate figure. |    
| Post-trading | Withdrawable balance may change after market close as charges and obligations are updated during EOD (19:00–21:00). |

---

### A10 — Links

| Purpose | URL |    
|---|---|    
| Bank account update | https://support.zerodha.com/category/funds/adding-bank-accounts/primary-bank-account/articles/how-do-i-change-my-primary-bank-account-linked-with-zerodha |    
| Bank verification for withdrawal | https://support.zerodha.com/category/funds/fund-withdrawal/withdrawal-process/articles/select-bank-for-withdrawal |    
| Console withdrawal page | https://console.zerodha.com/funds/overview |

---

### A11 — Rejection Reasons: Regular Withdrawals

`bank_response_remarks` and `bank_response_status` are internal per A2. Once `bank_response_status` = failed, funds are reversed to the client's ledger and a fresh withdrawal request can be placed.

| Rejection Reason (internal — `bank_response_remarks`) | Resolution |    
|---|---|    
| Destination Bank and Branch could not be resolved | Invalid IFSC; update IFSC on Console (Profile → Bank Details), place fresh request |    
| Rejected by sfms / Rejected by SFMS / Transaction is not accepted by the payment body | Confirm latest bank details with bank; update on Console if needed |    
| No transaction found during reconciliation, retry the transaction | Reprocessed automatically on T+1 before EOD |    
| Account does not exist | Contact bank |    
| Credit to NRE/NRI account | NRE account is mapped; if resident trading account, change primary bank account to a resident account on Console |    
| Beneficiary Bank is not enabled for Foreign Inward Remittance through IMPS | NRE account is mapped; if resident trading account, change primary bank account to a resident account on Console |    
| Account closed | Contact bank |    
| Operations Suspended | Contact bank |    
| Beneficiary name differs | Name mismatch between trading account and bank; verify and update name in bank or trading account |    
| There is a High memo on the account. Transactions not allowed. | Contact bank |    
| Transaction not allowed as the beneficiary account is not in Active Status | Contact bank |    
| Account blocked / Account frozen | Contact bank |    
| Payment Stopped | Contact bank |    
| Incorrect Account number | Contact bank |    
| Unknown End Customer | Name mismatch between trading account and bank; verify and update name |    
| Not specified reason customer generated | Contact bank |    
| Not Compliant | Contact bank |    
| Multiple reasons why beneficiary account could not be credited | Contact bank |

---

### A12 — Rejection Reasons: Instant Withdrawals

`bank_response_remarks` and `bank_response_status` are internal per A2. After any instant withdrawal rejection, today's instant attempt is consumed — only regular withdrawal is available for the rest of the day.

| Rejection Reason (internal — `bank_response_remarks`) | Resolution |    
|---|---|    
| Any rejection containing "NPCI" | Declined by the client's bank payment network (NPCI); contact bank |    
| IMPS is not enabled for the beneficiary IFSC | Contact bank |    
| Invalid beneficiary account number / Invalid Account | Contact bank |    
| Transfer Amount Exceeds Limit | Contact bank |    
| Beneficiary Bank is not enabled for Foreign Inward Remittance through IMPS | NRE account is mapped; if resident trading account, change primary bank account to a resident account on Console |    
| Request Not Found | Intermittent — regular withdrawal available; instant retriable next day |    
| Rejected/Failed at downstream system | Intermittent — regular withdrawal available; instant retriable next day |    
| failed to reduce margin on nest | Intermittent — regular withdrawal available; instant retriable next day |    
| Host (Cbs) Offline | Intermittent — regular withdrawal available; instant retriable next day |    
| Internal error or user have placed a request already | Refer to the first instant payout attempt status for that day; if the first attempt was successful, instant is used for the day |    
| Transaction could not be processed | Declined by client's bank; contact bank |

---

### A13 — Query Date Anchor

The query date is the date the client is asking about. All data analysis — orders, positions, eligibility checks, withdrawal records — is evaluated as of this date, not the current handling date.

| Priority | Source |    
|---|---|    
| 1 | Explicit date in the client's message (e.g., "on 11 Apr", "yesterday") |    
| 2 | Ticket/query creation date |    
| 3 | Current date (only if the client is asking about a live/ongoing issue) |

Conditions on the current date (e.g., orders placed today) are irrelevant to a query about a past date.

---

### A14 — Escalation Required Data

Include when escalating to human agent: client ID, `payout_type`, creation date, amount, `bank_response_remarks` (if rejection), `bank_ref_no` (if present), and specific issue.

---

## Section B: Decision Flow

### Routing

```    
Route by scenario    
├─ NRI PIS account                                                → Rule 1    
├─ Withdrawal request > ₹5 crore                                  → Rule 1    
├─ Instant withdrawal not working / blocked / eligibility question → Rule 2    
├─ Partial withdrawal (processed_amount < amount by ≥ ₹1)         → Rule 3    
├─ Failed / rejected withdrawal                                    → Rule 4    
├─ Funds not received (status = Processed)                        → Rule 5    
├─ Sold stocks / funds not available / no withdrawable balance     → Rule 6    
├─ Multiple or repeat withdrawal question                          → Rule 7    
├─ Existing withdrawal — status, timeline, expedite, or cancel    → Rule 8    
├─ App or UI issue on withdrawal page                              → Rule 9    
├─ Zero / low / negative balance                                   → Rule 10    
└─ No withdrawal records / charges query                           → Rule 11    
```

### Fallback

If no route matches after all checks, escalate to human agent per A14.

## Section C: Rules

---

### Rule 1: Early Exit — Escalate to Human Agent

If any condition below matches, stop immediately and escalate. Do not provide any response or bank details.

| Condition | Action |    
|---|---|    
| NRI PIS account | Escalate to human agent per A14 |    
| Withdrawal request > ₹5 crore | Escalate to human agent per A14 |

---

### Rule 2: Instant Withdrawal Issues

Invoke `kite_orders` and `kite_positions` for the query date per A13.

**Step 1 — Existing instant withdrawal:**    
If one already exists for the query date, it consumes the day's single attempt per A1. If an additional A3 blocker also applies, cite it after.

**Step 2 — Check A3 blockers:**    
Compare the reported error time against the earliest order/position timestamp. Filter CNC sell executed first (non-blocker per A3).    
- Orders/positions placed after the error time → not the cause; skip to Step 4. Instant is blocked for the rest of the day due to subsequent trading; offer regular withdrawal per A4.    
- Category 2 blocker (Paytm Payments Bank) → escalate to human agent per A14.    
- All other blockers → apply per A3.

**Step 3 — No blockers → check settlement:**    
Invoke `ledger_report`. If unsettled funds are present → T+1 per A5 applies. Suggest regular withdrawal.

**Step 4 — No blockers, funds settled:**    
Service is intermittent before 09:25 per A1 — retry after 09:25. If after 09:25 and still failing → direct to Console per A10; try alternate device if issue persists. If still unresolved → escalate to human agent per A14.

---

### Rule 3: Partial Withdrawals

Invoke `ledger_report` (±5 days). Applies when amount − processed_amount ≥ ₹1.

**Rounding edge case:** If amount − processed_amount < ₹1 → treat as fully processed; do not apply this rule.

**Step 1 — Confirm processed amount:**    
Share the processed amount and `bank_ref_no` if present (per A2).

**Step 2 — Identify cause from ledger per A8:**    
Exclude MTF entries. Match signals to causes — T+1 per A5, same-day deposit, delayed payment charges as applicable.

**Step 3 — Check for an existing subsequent withdrawal:**    
If a subsequent request (Pending or Processed) already exists for the remaining balance → share its status and timeline per A4. Do not suggest a new request.

**Step 4 — Suggest fresh withdrawal (only if no subsequent request exists):**    
Confirm withdrawable balance covers the remaining amount. If cause is same-day deposit or T+1, suggest placing on the next working day. If eligible per A1 and A3, suggest instant.

---

### Rule 4: Withdrawal Request Failure

Invoke `ledger_report` (±3 days from creation date).

**Step 1 — Bank rejection:**

If `bank_response_status` = failed:

1. Identify rejection reason from `bank_response_remarks` using A11 (Regular) or A12 (Instant) based on `payout_type`. Apply the resolution from the matching row.    
2. Check ledger per A7 for a "Transfer rejected by bank" entry:    
   - Present → funds back in trading account; fresh request can be placed.    
   - Absent → reversal in progress; funds return within 24–48 working hours.    
3. If `bank_response_remarks` contains "NPCI" per A7 → rejection from the client's bank payment network. If `Instant_Payout` → today's instant attempt is consumed; only regular is available.    
4. Cross-check with CMR (Console → Profile) and bank statement. Bank update per A10.    
5. NRI/NRE: NRE PIS details must match bank records exactly. Verify via Console → Profile → Bank accounts. Bank update requires courier form and bank proof; if Aadhaar-linked, e-sign and submit via ticket.

**Step 2 — Non-rejection failure:**    
Identify cause from ledger per A8. Apply A6 for reversal framing.

If client traded with the credited/deposited funds during the same period, identify the net remaining balance after trading.

---

### Rule 5: Funds Not Received (Status = Processed)

| Scenario | Action |    
|---|---|    
| Within timeline (Instant: < 10 min; Regular: before T+1 14:00) | Processing within expected window — no action |    
| Past timeline \+ bank_ref_no present \+ < 3 days since modified | Share bank_ref_no; refer client to their bank |    
| Past timeline \+ bank_ref_no present \+ ≥ 3 days since modified | Share bank_ref_no; client to request bank statement from payout_date to today |

---

### Rule 6: Stock Sale — Funds Not Available

**Step 1:** Invoke `ledger_report` (5 days) and `kite_holdings`. Check if a withdrawal request has already been placed.

**Step 2:** Identify cause from ledger per A8. T+1 per A5 applies if a settlement entry is found. Root cause is T+1 settlement — not a balance shortfall or unrelated charge.

**Step 3 — No withdrawal placed, settlement complete:** Direct to place a withdrawal request. If eligible per A1 and A3, suggest instant.

**Step 4 — Withdrawal already placed:** Route to Rule 2, 3, or 4 as applicable.

**Step 5 — Holdings confusion:** If withdrawable balance ≤ ₹0 and `kite_holdings` value approximates the requested amount → amount is held as equity, not cash. Client must sell first; T+1 per A5 applies after sale.

**Step 6 — Negative "used margin" after stock sale:** Negative "used margin" on Kite funds page reflects sale proceeds pending T+1 settlement per A5.

---

### Rule 7: Multiple / Repeat Withdrawals

| Scenario | Action |    
|---|---|    
| Both instant and regular pending or processed | Handle instant per Rule 2; handle regular per Rule 8 |    
| Second instant attempt same day | Once-per-day limit per A1; regular available per A4 |    
| Second regular while one is pending | Wait for completion or cancel per A1; place new request after |    
| Instant rejected \+ retry query | Attempt consumed per A12; identify rejection reason per A12; only regular available |    
| Remaining balance after instant | Balance updates after EOD per A9 |

---

### Rule 8: Status / Timeline / Expedite / Cancellation

**Step 1 — Status / timeline inquiry:**    
Share current `status` per A2 with expected processing timeline per A4 based on withdrawal type and day:    
- Instant: within minutes of approval per A1.    
- Regular: per applicable cutoff in A4. Regular withdrawals are automated and cannot be expedited.

**Step 2 — Cancellation request:**    
Regular withdrawals can be cancelled while status = Pending via Console → Funds → Withdrawal history per A1. Instant withdrawals cannot be cancelled.

**Step 3 — Expedite request:**    
Regular withdrawals cannot be expedited. Inform the client of the applicable processing cutoff per A4 and expected credit timeline.

---

### Rule 9: App / UI Troubleshooting

**Step 1:** Route to Console web withdrawal page per A10.

**Step 2:** If issue persists on Console web → try alternate device. If still unresolved → escalate to human agent per A14.

---

### Rule 10: Zero / Low / Negative Balance

**Step 1:** Invoke `ledger_report` (5 days). Identify cause from ledger per A8.

**Step 2 — Quarterly settlement:**    
If ledger contains a "quarterly settlement" entry (Bank Payments voucher type per A8) → funds were paid out to the client's bank as part of Zerodha's mandatory quarterly settlement. Client should check their bank account for the credited amount.

**Step 3 — Delayed payment charges:**    
If ledger shows "Delayed payment charges" (Journal Entry per A8) → client has outstanding dues. They must add funds to clear the balance before a withdrawal can be placed.

**Step 4 — Negative balance:**    
If balance is negative → outstanding dues or unsettled obligations. Identify the specific charge from ledger per A8 and inform the client accordingly.

---

### Rule 11: No Records / Charges

| Scenario | Action |    
|---|---|    
| No withdrawal records found | No requests on file; "Withdrawal Balance" on Console is the current withdrawable balance, not a withdrawal request |    
| Charges on withdrawal | Withdrawals are free; if processed amount < requested amount → route to Rule 4 |
