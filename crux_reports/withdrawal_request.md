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

## Section A: Reference Data

### A1 — Withdrawal Types

- **Date range limit:** 30 days per call.

| Field Value | Label | Amount Range | Frequency | Window | Credit Timeline | Cancellable |
|---|---|---|---|---|---|---|
| `Instant_Payout` | Instant | ₹100–₹2,00,000 (whole rupees only) | Once per day (regardless of outcome) | 09:00–16:00 daily (incl. weekends; intermittent before 09:25) | Within minutes | No |
| `Payout` | Regular | ₹1 to available balance (up to ₹5 crore via Console) | No daily limit | At applicable cutoff (per A5) | Within 24h of processing | Yes — while Pending, via Console → Funds → Withdrawal history |

- One instant and one regular can be pending simultaneously. A pending regular withdrawal has no effect on instant availability. Regular withdrawals are automated and cannot be expedited.

- **`Bank_Reconciliation_Pending` (Instant only):** Instant withdrawal is awaiting EOD bank reconciliation. Two possible outcomes:
  - Reconciliation succeeds → funds credited to client's bank account
  - Reconciliation fails → funds reversed to trading account ledger within 24 working hours from the withdrawal request `creation` date

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

### A3 — Query Date Anchor

The query date is the date the client is asking about. All data analysis — orders, positions, eligibility checks, withdrawal records — is evaluated as of this date, not the current handling date.

| Priority | Source |
|---|---|
| 1 | Explicit date in the client's message (e.g., "on 11 Apr", "yesterday") |
| 2 | Ticket/query creation date |
| 3 | Current date (only if the client is asking about a live/ongoing issue) |

Conditions on the current date (e.g., orders placed today) are irrelevant to a query about a past date.

**Order fetch by query date:** if the query date is today → `kite_orders`; if the query date is a past date → `kite_order_history`. (`kite_positions` is always the current position — invoke `kite_positions`, no date parameter.)

---

### A4 — Instant Eligibility

| Category | Blocker / Scenario | Effect |
|---|---|---|
| Full-day blocker (instant only) | Any orders on the query date (`order_status` = pending / executed / rejected / cancelled), except CNC sell executed | Instant unavailable for the entire day |
| Full-day blocker (instant only) | Any positions (open or closed), except CNC sell executed | Instant unavailable for the entire day |
| Account-level restriction (instant only) | Orbis-linked account — verify `bo_sub_status` (from `get_all_client_data`) | Instant withdrawal is not allowed for Orbis accounts (regular withdrawal unaffected) |
| Account-level blocker | Paytm Payments Bank as primary bank account | Blocks both instant and regular |
| Fund availability | Same-day / weekend / settlement-holiday deposit | See A9 for instant/regular availability |

Confirmed non-blockers: GTT orders, pending regular withdrawals.

---

### A5 — Processing Cutoffs (Regular Withdrawal / Payout only)

| Condition | Processed at | Credit by |
|---|---|---|
| Saturday | 16:30 | Within 24h |
| Sunday / settlement holiday | Next working day cutoff | Within 24h of processing |
| Weekday + ZBL_MCX active | 23:59 | Within 24h |
| Weekday + before 17:00 + no trades/positions/instant + sufficient balance | ~17:00 same day | Same-day bank credit |
| Weekday + before 17:00 + has trades/positions/instant | 22:00 | Within 24h |
| Weekday + after 17:00 (no ZBL_MCX) | 22:00 | Within 24h |

---

### A6 — T+1 Settlement Restrictions for withdrawals

| Aspect | Detail |
|---|---|
| Definition | Funds from trades (equity, F&O, MCX, CDS) and same-day deposits appear in the account balance on the same day but are not withdrawable until T+1 (next working day, excluding weekends and settlement holidays) |
| Stock sales | Credit appears in ledger same day (after 19:00–21:00 update); withdrawable only after T+1 settlement completes |
| Intraday / F&O trades | T+1 applies to realised profits, mark-to-market (M2M), and option sell value |
| Ledger signal | DP (depository participant) charges on a date confirm a stock sale on that date; T+1 settlement is the cause for the withdrawal restriction |
| Balance display | Settlement credits appear in ledger same day; only withdrawal eligibility follows T+1 |

---

### A7 — Reversal Terminology

| Scenario | Correct Framing |
|---|---|
| Bank rejected (funds were sent to bank, returned by bank) | Funds reversed to trading account |
| T+1 / same-day deposit / balance shortfall (funds never left the trading account) | Request did not go through; funds remained in the trading account throughout |

---

### A8 — Bank Rejection Reference

| Signal | Meaning |
|---|---|
| `bank_response_status` = failed | Transaction rejected by the bank; funds to be reversed to the trading account |
| Ledger entry: `remarks` contain "Transfer rejected by bank" | Reversal complete; funds are back in the trading account |
| `bank_response_remarks` contains "NPCI" | Rejection originated from the client's bank payment network (NPCI), not from Zerodha |
| `bank_response_status` = failed + no "Transfer rejected by bank" ledger entry | Reversal in progress; funds expected back within 24–48 working hours |

---

### A9 — Ledger Translation

Read from `ledger_report` (`voucher_type`, `remarks`, `posting_date`, `debit`, `credit`, `net_balance`).

| `voucher_type` | `remarks` Pattern | Meaning | Withdrawal Impact |
|---|---|---|---|
| Bank Receipts | On creation/query date (weekday) | Same-day deposit | Not withdrawable until next working day (instant and regular) |
| Bank Receipts | On Saturday or Sunday | Weekend deposit | Regular: available now. Instant: available Tuesday |
| Bank Receipts | On settlement holiday | Settlement holiday deposit | Regular: available now. Instant: not available on the next working day |
| Book Voucher | "Net settlement for Equity..." | Equity trade settlement | T+1 per A6 |
| Book Voucher | "Net obligation for Equity F&O" | F&O trade settlement | T+1 per A6 |
| Book Voucher | "Net obligation for MCX commodity FNO" | MCX commodity trade settlement | T+1 per A6 |
| Book Voucher | "Net obligation for CDS FNO" | CDS currency trade settlement | T+1 per A6 |
| Journal Entry | "DP (depository participant) Charges for Sale of [STOCK] on [DATE]" | Stock sold that day | T+1 per A6 |
| Journal Entry | "Delayed payment charges for [Month] - [Year]" | Delayed payment charges | Client must add funds to clear dues |
| Bank Payments | "Funds auto-settled to the primary bank account" | Regular QS payout — client-chosen frequency | Funds transferred to client's primary bank account via quarterly settlement; trading account balance reduced accordingly |
| Bank Payments | "Funds transferred back as part of quarterly settlement (inactive)" | Inactivity-triggered monthly settlement | Funds transferred to client's primary bank account; account was inactive for 30+ days |
| — | Time 19:00–21:00, no other signals | Balance update window | Retry after 21:00 |

---

### A10 — Withdrawable Balance Reference

| Fact | Detail |
|---|---|
| `available_cash` vs `available_margin` | `kite_margins` returns both values. `available_cash` excludes collateral; `available_margin` includes collateral. Only `available_cash` reflects withdrawable funds. |
| Collateral margin accounts | For accounts with collateral, `available_cash` in `kite_margins` may not reflect the true withdrawable balance; `ledger_report` provides the accurate figure. |
| Post-trading | Withdrawable balance may change after market close as charges and obligations are updated during EOD (19:00–21:00). |
| `payin` (`kite_margins`) | Same-day deposit amount; reflected in `kite_margins` immediately (unlike the ledger Bank Receipts entry, which may lag intraday). Use to detect a same-day deposit for queries received before the EOD ledger update. |
| `payout` (`kite_margins`) | Amount of an instant withdrawal already processed but not yet reflected in the ledger / withdrawable balance until the EOD update. Net it out to get the true remaining withdrawable balance. |

---

### A11 — Links

| Purpose | URL |
|---|---|
| Bank account update | https://support.zerodha.com/category/funds/adding-bank-accounts/primary-bank-account/articles/how-do-i-change-my-primary-bank-account-linked-with-zerodha |
| Bank verification for withdrawal | https://support.zerodha.com/category/funds/fund-withdrawal/withdrawal-process/articles/select-bank-for-withdrawal |
| Console withdrawal page | https://console.zerodha.com/funds/overview |
| Withdrawals to secondary bank | https://support.zerodha.com/category/funds/fund-withdrawal/other-withdrawal-related-queries/articles/withdrawals-to-primary |

---

### A12 — Rejection Reasons: Regular Withdrawals

`bank_response_remarks` and `bank_response_status` are internal per A2. (Reversal handling per A8 / Rule 4.)

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

### A13 — Rejection Reasons: Instant Withdrawals

`bank_response_remarks` and `bank_response_status` are internal per A2. (Instant once-per-day attempt per A1; reversal per A8 / Rule 4.)

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

### A14 — Withdrawal Eligibility (FIFO)

For any failed / partial / "low or zero withdrawable despite positive ledger balance" diagnosis, compute eligibility from `ledger_report` for the withdrawal date T.

| Symbol | Definition (from the ledger for date T) |
|---|---|
| A | Opening settled balance = prior day's closing balance |
| B | Unsettled credits posted on T = same-day payin (Bank Receipts) + equity / FNO / MTF / MCX / CDS settlement credits (Book Voucher) — per A9 |
| D | Unsettled debits posted on T = equity / FNO / MTF / MCX / CDS obligation debits (Book Voucher) — per A9 |

- Visible ledger balance = **A + B − D**
- **Withdrawal-eligible = A − D** — FIFO: unsettled debits consume the settled opening balance (A) first, never the same-day unsettled credits (B).

Diagnose by comparing **withdrawal-eligible (A − D)** against the **requested amount**:

| Withdrawal-eligible vs requested | Meaning | Handle in |
|---|---|---|
| ≤ 0 | Fails / processes ₹0 even though visible ledger balance (A + B − D) is positive — settled funds exhausted by unsettled debits | Rule 4 (Case A) |
| 0 < eligible < requested | Partial — only the settled portion (A − D) is released; the remainder is unsettled credit B | Rule 3 |
| ≥ requested, yet client sees low/zero withdrawable | Locked amount is the unsettled credit B (same-day payin or Book Voucher trade credit, incl. sale proceeds) | Rule 6 (sale proceeds) or Rule 10 |

The unsettled portion (B) becomes withdrawable on the next settlement working day — invoke `settlement_date_calculator` for the exact date (accounts for weekends / settlement holidays).

---

## Section B: Decision Flow

### Routing

```
Route by scenario
├─ NRI PIS account                                                → Rule 1
├─ Withdrawal request > ₹5 crore                                  → Rule 1
├─ Instant withdrawal not working / blocked / eligibility question → Rule 2
├─ Partial withdrawal (0 < processed_amount < amount)             → Rule 3
├─ Failed / rejected withdrawal                                    → Rule 4
├─ Funds not received (status = Processed)                        → Rule 5
├─ Sold stocks / funds not available / no withdrawable balance     → Rule 6
├─ Multiple or repeat withdrawal question                          → Rule 7
├─ Existing withdrawal — status, timeline, expedite, or cancel    → Rule 8
├─ App or UI issue on withdrawal page                              → Rule 9
├─ Zero / low / negative balance (including same-day deposit)      → Rule 10
└─ No withdrawal records / charges query                           → Rule 11
```

### Fallback

If no route matches after all checks → escalate.

---

## Section C: Rules

### Rule 1: Early Exit — Escalate

If any condition below matches, escalate immediately. Do not share any account or bank details with the client.

| Condition | How to identify | Action |
|---|---|---|
| NRI PIS account | Verify `bo_sub_status` (from `get_all_client_data`) | → escalate |
| Withdrawal request > ₹5 crore | Requested amount > ₹5,00,00,000 | → escalate |

---

### Rule 2: Instant Withdrawal Issues

Invoke orders per A3 for the query date (today → `kite_orders`; past date → `kite_order_history`). Invoke `kite_positions` (current positions).

**Step 1 — Time of placement:**
If the client placed (or is placing) the instant withdrawal before 09:25, the service is intermittent at that time (per A1) — advise retrying after 09:25.

**Step 2 — Account-level restrictions:**
- Primary bank = Paytm Payments Bank → both instant and regular are blocked (per A4) → escalate.
- Orbis-linked account (verify `bo_sub_status` from `get_all_client_data`) → instant is not allowed (per A4); offer regular withdrawal.

**Step 3 — Existing instant withdrawal:**
If an instant withdrawal already exists for the query date → it has consumed the day's single attempt (per A1); no further instant today.

**Step 4 — No existing instant → order / position blockers:**
Check the orders (per the A3 tool selection, for the query date) and `kite_positions` for an order-placed or position blocker per A4 (exclude CNC sell executed; `transaction_type` = sell, `product` = CNC, `order_status` = executed).
- Blocker present → instant cannot be placed today; offer regular withdrawal per A5.
- No blocker → go to Step 5.

**Step 5 — No blockers → check settlement:**
Invoke `ledger_report`. If unsettled funds are present → T+1 per A6 applies; suggest regular withdrawal.

**Step 6 — No blockers, funds settled:**
After 09:25, with no blockers and funds settled, if instant still fails → direct to Console per A11; try an alternate device if the issue persists. If still unresolved → escalate.

---

### Rule 3: Partial Withdrawals

Invoke `ledger_report` (±5 days). Applies when amount − processed_amount > ₹0 (and processed_amount > 0; processed_amount = 0 → route to Rule 4).

**Step 1 — Identify cause from ledger per A9; quantify per A14:**
Compute withdrawal-eligible (A − D) per A14. A partial payout corresponds to 0 < eligible < requested — only the settled portion (A − D) was released; the remainder is unsettled credit B (same-day payin or Book Voucher trade credit). Match the underlying signal to its cause — T+1 per A6, same-day deposit, delayed payment charges as applicable.

**Step 2 — Confirm processed amount:**
Share the processed amount and `bank_ref_no` if present (per A2).

**Step 3 — Check for an existing subsequent withdrawal:**
If a subsequent request (Pending or Processed) already exists for the remaining balance → share its status and timeline per A5. Do not suggest a new request.

**Step 4 — Suggest fresh withdrawal (only if no subsequent request exists):**
Confirm withdrawable balance covers the remaining amount. If cause is same-day deposit or T+1, suggest placing on the next working day (date via `settlement_date_calculator` per A14). If eligible per A1 and A4, suggest instant.

---

### Rule 4: Withdrawal Request Failure

Invoke `ledger_report` (±3 days from creation date). Two cases:

**Case A — Failed: withdrawal amount not available (funds never left the trading account):**
Compute withdrawal-eligible (A − D) per A14. Cross-check the computed value against the `remarks` field (e.g., "Withdrawal balance - -1517.34") — if they differ, use the `remarks` value as the authoritative figure and re-examine the ledger rows used for A and D. The request failed because withdrawal-eligible ≤ 0 — settled funds (A) were exhausted by unsettled debits (D), even though the visible ledger balance (A + B − D) is positive (A14). Use A7 framing: the request did not go through; funds remained in the trading account. The unsettled credit B becomes withdrawable on the next settlement working day — invoke `settlement_date_calculator`, give the client that date, and have them place a fresh request then.
(If the client traded with the credited/deposited funds in the same period, identify the net remaining balance after trading.)
If the client's balance remains negative and the cause cannot be fully explained from the ledger → escalate.

**Case B — Processed, then failed by the bank (funds reversed to the ledger):**
`bank_response_status` = failed:
1. Identify the rejection reason from `bank_response_remarks` using A12 (Regular) or A13 (Instant) per `payout_type`; apply the matching resolution.
2. Check the ledger per A8 for a "Transfer rejected by bank" entry: present → funds are back in the trading account, a fresh request can be placed; absent → reversal in progress, funds return within 24–48 working hours.
3. Resolution — the client can: contact their bank to resolve the reason; change their primary bank account (A11 — Bank account update); or withdraw to a secondary bank account (A11 — Withdrawals to secondary bank).
4. If `bank_response_remarks` contains "NPCI" per A8 → rejection from the client's bank payment network; if `Instant_Payout`, today's instant attempt is consumed (only regular available).
5. Cross-check with CMR (Console → Profile) and bank statement.
6. NRI/NRE: NRE PIS details must match bank records exactly (Console → Profile → Bank accounts); bank update requires courier form + bank proof, or e-sign if Aadhaar-linked. *(NRI PIS accounts are escalated at Rule 1; this applies to non-PIS NRI or resident accounts with an NRE bank mapped.)*
7. If the rejection reason is not listed in A12/A13, or resolution steps do not resolve the issue → escalate.

---

### Rule 5: Funds Not Received (Status = Processed)

`modified` and `bank_ref_no` per A2, evaluated against the query date per A3.

| Scenario | Action |
|---|---|
| `bank_ref_no` present (regardless of timeline) | First check if `processed_amount` < `amount` — if yes, address the partial shortfall per **Rule 3** before proceeding. Then share `bank_ref_no` for the processed portion and refer client to their bank. |
| `status` = `Bank_Reconciliation_Pending` (`Instant_Payout` only) | Inform client per A1 — `Bank_Reconciliation_Pending` |
| No `bank_ref_no` + within 24h of `payout_date` | Funds still being processed — within expected window; no action |
| No `bank_ref_no` + past 24h of `payout_date` | → escalate |

---

### Rule 6: Stock Sale — Funds Not Available

**Step 1:** Invoke `kite_order_history` for the stated sale date and verify sell trades actually exist.
   - No sell trades found → invoke `ledger_report` for a DP charge entry ("DP Charges for Sale of [STOCK]") for the stock in question to confirm whether a sale actually occurred; explain to client what the ledger shows; clarify that share sale proceeds do not auto-credit the bank account — a withdrawal request must be placed manually after T+1 settlement.

**Step 2:** Invoke `ledger_report` for the stated sale date ±3 days. Check if a withdrawal request has already been placed.

**Step 3:** From the ledger, identify the settlement entry (Book Voucher — "Net settlement for Equity") for the sale date — confirms sale proceeds were credited to the trading account. T+1 per A6 applies — funds not withdrawable until next settlement working day. Invoke `settlement_date_calculator` to confirm the exact date.

**Step 4 — No withdrawal placed, settlement complete:** Direct to place a withdrawal request. If eligible per A1 and A4, suggest instant.

**Step 5 — Withdrawal already placed:** Route to Rule 2, 3, or 4 as applicable.

**Step 6 — Holdings confusion:** If withdrawable balance ≤ ₹0 and `kite_holdings` value approximates the requested amount → amount is held as equity, not cash. Client must sell first; T+1 per A6 applies after sale.

**Step 7 — Negative "used margin" after stock sale:** Invoke `kite_margins` and check the `used_margin` field — negative "used margin" on Kite funds page reflects sale proceeds pending T+1 settlement per A6.

---

### Rule 7: Multiple / Repeat Withdrawals

| Scenario | Action |
|---|---|
| Both instant and regular pending or processed | Handle instant per Rule 2; handle regular per Rule 8 |
| Second instant attempt same day | Once-per-day limit per A1; regular available per A5 |
| Second regular while one is pending | Wait for completion or cancel per A1; place new request after |
| Instant rejected + retry query | Attempt consumed per A13; identify rejection reason per A13; only regular available |
| Remaining balance after instant | If an instant withdrawal processed after the ticket-creation time (per A3), the displayed withdrawable balance is stale until the EOD update. True remaining = `available_cash` − `payout` (`kite_margins`, per A10). Share this figure, not the stale balance. |

---

### Rule 8: Status / Timeline / Expedite / Cancellation

**Step 1 — Status / timeline inquiry:**
Share current `status` per A2 with expected processing timeline per A5 based on withdrawal type and day:
- Instant: within minutes per A1.
- Regular: per applicable cutoff in A5. Regular withdrawals are automated and cannot be expedited.

**Step 2 — Cancellation request:**
Regular withdrawals can be cancelled while status = Pending via Console → Funds → Withdrawal history per A1. Instant withdrawals cannot be cancelled.

**Step 3 — Expedite request:**
Regular withdrawals cannot be expedited. Inform the client of the applicable processing cutoff per A5 and expected credit timeline.

---

### Rule 9: App / UI Troubleshooting

**Step 1:** Route to Console web withdrawal page per A11.

**Step 2:** If issue persists on Console web → try alternate device. If still unresolved → escalate.

---

### Rule 10: Zero / Low / Negative Balance

**Step 1:** Invoke `kite_margins` and `ledger_report` (5 days). Read `available_cash` (not `available_margin`) for the withdrawable figure per A10; for collateral accounts use `ledger_report` as the accurate source (per A10). Identify cause from ledger per A9.

**Step 2 — Same-day deposit:**
Invoke `kite_margins` and check the `payin` field — same-day payins reflect immediately (per A10), reliable even before the EOD ledger update. If `payin` shows a same-day deposit (or the ledger shows a Bank Receipts entry on the query date) → apply the instant/regular availability per A9 (weekday / Saturday–Sunday / settlement holiday).

**Step 3 — Quarterly settlement:**
If ledger contains a "Bank Payments" entry matching either QS remark per A9 ("Funds auto-settled to the primary bank account" or "Funds transferred back as part of quarterly settlement (inactive)") → funds were paid out to the client's bank as part of quarterly settlement. Client should check their bank account for the credited amount.

**Step 4 — Delayed payment charges:**
If ledger shows "Delayed payment charges" (Journal Entry per A9) → client has outstanding dues. They must add funds to clear the balance before a withdrawal can be placed.

**Step 5 — Negative balance:**
If balance is negative → outstanding dues or unsettled obligations. Identify the specific charge from ledger per A9 and inform the client accordingly.

If the cause identified is a stock-sale / trade settlement (T+1), hand off to Rule 6.

---

### Rule 11: No Records / Charges

| Scenario | Action |
|---|---|
| No withdrawal records found | No requests on file in the withdrawal report. If a withdrawable balance is present → "Withdrawal Balance" on Console is the amount available; direct the client to place a withdrawal. If no withdrawal request AND no balance → escalate. |
| Charges on withdrawal | Withdrawals are free; if processed amount < requested amount → route to Rule 3 |
