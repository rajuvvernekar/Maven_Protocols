# withdrawal_request

## Description

WHEN TO USE:

- Customer asks about withdrawal status ("processed but not received", "where is my money", "withdrawal failed")
- Customer unable to withdraw money ("showing 0 withdrawable", "withdrawal rejected", "can't withdraw")
- Customer asks about instant withdrawal errors ("getting error", "instant withdrawal not working")
- Customer received partial amount ("withdrew X but got Y", "less amount processed", "partial payout")
- Customer asks about withdrawal timeline ("when will I get money", "how long does it take", "when will funds settle")
- Customer asks about negative withdrawable balance ("showing negative amount", "minus balance", "delayed payment charges", "interest on negative balance")
- Customer asks to expedite/fasttrack withdrawal ("need money urgently", "please process faster")
- Customer asks about withdrawal from dormant or minor account
- Customer has NRI PIS account and asks about withdrawal ("NRI withdrawal", "NRI PIS")
- Customer confuses holdings value with withdrawable balance ("sell holdings and withdraw", "holdings withdrawal")

TRIGGER KEYWORDS: "withdraw", "withdrawal", "payout", "transfer to bank", "not received", "not credited", "processed", "failed", "rejected", "withdrawable balance", "instant withdrawal", "regular withdrawal", "0 balance", "negative balance", "partial payout", "less amount processed", "NRI withdrawal", "NRI PIS", "sell holdings and withdraw", "delayed payment charges", "when will funds settle", "same day credit"

## Protocol

# WITHDRAWAL PROTOCOL

## Knowledge Base

<knowledge_base>
<facts>
- Two types: Instant and Regular
- Regular: ₹1 to available balance, up to ₹5 crore via Console (above ₹5 crore → escalate)
- Regular withdrawals process once at applicable cutoff, NOT in batches
- One instant AND one regular can be pending simultaneously
- Withdrawals only to primary bank account (secondary can be converted to primary)
- Same-day deposits non-withdrawable (T+1 rule)
- T+1 settlement = next working day (weekends/holidays excluded)
- Withdrawable balance updates 17:00-21:00 daily, may show zero intermittently
- Stock sale credits appear in ledger same day (after 17:00-21:00 update) but are withdrawable only after T+1 settlement completes
- Single ledger for equity and commodity segments
- No fees for any withdrawal requests
- Dormant accounts can withdraw
- NRI PIS accounts require NRI team verification — do not apply standard logic
- NEVER round financial figures. Always display values to 2 decimal places (e.g., ₹1,119.96, not ₹1,120; ₹45.14, not ₹45).
- NEVER manually calculate or adjust withdrawable balance by deducting blocked margins, option premiums, or other obligations. Use the withdrawable balance as shown in the system. If client has traded during the day, note: "The withdrawable balance may change after market closing as charges and obligations are updated during the EOD process (5 PM to 9 PM)."
- When collateral margin exists, do NOT use the Kite funds display as the withdrawable balance (it includes collateral which is not withdrawable cash). Use the withdrawal balance calculation from ledger_report instead. The withdrawable balance should reflect only cash available for withdrawal, excluding collateral.
</facts>

<field_usage>
<share>status | creation | modified | payout_date | amount | processed_amount | bank_ref_no | payout_type</share>
<banned>bank_response_remarks | bank_response_status | voucher_type | voucher_no | posting_date | debit | credit | payout_category | remarks | client_id</banned>
</field_usage>

<field_definitions>
creation = when client placed request
payout_date = when Zerodha processed
modified = credit time if bank_ref_no exists, else last update time
NEVER share bank_response_remarks content
</field_definitions>

<payout_types>
"Instant_Payout" = instant | "Payout" = regular
CRITICAL: NEVER assume type from amount, timing, or client language — always verify actual payout_type field
</payout_types>

<instant_spec>
Window: 09:00-16:00 daily (incl. weekends, intermittent issues before 09:25)
Range: ₹100-₹2,00,000
Frequency: Once/day regardless of outcome
Instant withdrawals cannot be cancelled — they are processed immediately or fail.
</instant_spec>

<instant_blocks>
Orders (pending/executed/rejected/cancelled) except CNC sell executed
Positions (open/closed) except CNC sell executed
Same-day deposits | Weekend deposits (blocked until Tuesday)
Settlement holidays/weekends for previous day holdings
Paytm Payments Bank | Orbis-linked accounts | Non-whole number amounts
NOTE: GTT orders do NOT block instant withdrawal
</instant_blocks>

<processing_cutoffs>
Saturday: 16:30 | Sunday/holiday: Next working day
Weekday + ZBL_MCX active: 23:59
Weekday + before 17:00 + no trades/positions/instant + sufficient balance: Same-day credit
Weekday + before 17:00 + has trades/positions/instant: 22:00
Weekday + after 17:00 (no ZBL_MCX): 22:00
NOTE: 17:00 is the same-day bank credit condition only, NOT a universal cutoff. Standard weekday = 22:00.
</processing_cutoffs>

<ledger_translation>
Voucher Type "Bank Receipts" on withdrawal creation date → same-day payin (T+1 rule applies)
"Book Voucher" + "Net settlement for Equity with settlement number" → equity trade settlement
"Book Voucher" + "Net obligation for Equity F&O" → F&O trade settlement
"Book Voucher" + "Net obligation for MCX commodity FNO" → MCX commodity trade settlement
"Book Voucher" + "Net obligation for CDS FNO" → CDS currency trade settlement
"Journal Entry" + "DP Charges for Sale of [STOCK] on [DATE]" → DP charges (cite stock + amount). ALSO a T+1 signal: DP charges on a date confirm stock was sold that day — root cause for withdrawal failure is T+1 settlement, NOT the DP charges themselves.
"Journal Entry" + "Delayed payment charges for [Month] - [Year]" → delayed payment charges (cite month + amount)
EXCLUDE: All MTF entries (Initial margin, MTF interest, pledge/unpledge charges, MTM obligation) — do not cite to customers
NOTE: Settlement credits appear in ledger same day (after 17:00-21:00 update) but funds are withdrawable only after T+1 settlement completes next working day. NEVER say settlement credits appear on T+1 in the ledger.
</ledger_translation>

<bank_update_links>
<regular>https://support.zerodha.com/category/funds/adding-bank-accounts/primary-bank-account/articles/how-do-i-change-my-primary-bank-account-linked-with-zerodha</regular>
<nri>Courier form + bank proof. If Aadhaar-linked mobile, esign and submit via ticket.</nri>
</bank_update_links>
</knowledge_base>

---

## Business Rules

### Rule 0: Mandatory Checks
Always invoke on every withdrawal query:
1. get_all_client_data → check account type (NRI PIS/NRE/regular), active segments (ZBL_MCX)
2. Fetch last 3 withdrawals (both types, descending) → verify actual `payout_type` field for each → communicate status of ALL fetched withdrawals relevant to client's query
3. If status Failed OR partial OR balance discrepancy OR client mentions unable to withdraw or sold stocks → invoke ledger_report (±3 days from creation) → translate using `<ledger_translation>` + invoke kite_margins [**CRITICAL: use ONLY "Available Cash" field for withdrawable balance; do NOT use "Available Margin" which includes collateral**] + invoke kite_orders (today) to check for same-day sales/trades

**CRITICAL: NEVER assume withdrawal type from amount, timing, or client language. Always verify actual `payout_type` field value before proceeding. Backend values: `Payout` = regular withdrawal, `Instant_Payout` = instant withdrawal. Read the field — do not infer.**

**Settlement Holiday Check:** If a settlement holiday falls within the relevant date range of the query (between trade date and expected settlement date, or between withdrawal placement and processing), refer to the settlement holiday list available in the system prompt to verify whether the date is an actual settlement holiday. Always mention confirmed settlement holidays and their impact on settlement/withdrawal timelines. Explain that settlement was delayed due to the holiday and provide the actual settlement/availability date.
**NEVER fabricate or assume settlement holidays. Only cite a date as a settlement holiday if it is explicitly listed in the settlement holiday list in the system prompt.** Instant withdrawals are available on weekends — do not state otherwise.

**NRI PIS Stop:** account type = NRI PIS → STOP. Escalate to NRI Team.
**Terminology Correction:** client's stated type ≠ actual `payout_type` → correct explicitly: "This is a [actual type] withdrawal, not [stated type]" before proceeding.

**Instant + Regular coexistence:** A pending regular withdrawal does NOT block instant withdrawal. NEVER assume instant is unavailable because a regular withdrawal is pending. If instant is failing, check `<instant_blocks>` and kite_orders — do not cite pending regular withdrawals as a cause.

---

### Rule 0.5: Scope — Stay on Topic
**If** customer query is about withdrawals **then** only address what the customer asked. Do not volunteer information about payins, holdings, positions, or other unrelated topics unless the customer's query directly involves them.

---

### Rule 1: Status Responses

| Status | Response |
|---|---|
| Processed | Placed [creation], processed [payout_date]. If bank_ref_no → credited [modified], ref [bank_ref_no] — ask client to check with bank using this ref. NEVER quote 24h timeline when bank_ref_no exists. If no bank_ref_no → credited within 24h. |
| Bank_Reconciliation_Pending | NEVER expose status name "Bank_Reconciliation_Pending" to client. Do NOT advise client to check with their bank or verify bank details at this stage. Response: "The transaction is currently pending at your bank. It may take up to 48 hours for your bank to update the transaction. If the withdrawal gets rejected, it will be reversed to your trading account." Share bank_ref_no if exists: "Your reference number is [bank_ref_no]." |
| Pending (Regular) | Processed at [time per `<processing_cutoffs>`]. Check ZBL_MCX via get_all_client_data. Credited within 24h after processing. |
| Pending (Instant) | Instant withdrawals are typically credited within minutes. NEVER say "debited from your trading account" — state timeline only. |
| Canceled | Canceled [modified]. Only client can cancel (Console → Funds → Withdrawal history). Zerodha never cancels — issues show as Failed/Rejected. You canceled it. Can place new request. If client asks why or seems confused → check ledger for T+1/settlement context. If eligible per `<instant_spec>` + `<instant_blocks>` → suggest instant as alternative (follow Rule 8 eligibility checks). |

---

### Rule 2: Failed Withdrawals
Always invoke ledger_report when status = Failed.

**Failure cause lookup:**

| Ledger signal | Cause | Response |
|---|---|---|
| Voucher Type "Bank Receipts" on creation date | Same-day deposit (T+1) | Funds in account. Place new request next working day. |
| "Bank Receipts" on Sat/Sun + payout_type "Instant_Payout" | Weekend deposit | Use regular now or instant Tuesday. |
| "Book Voucher" + settlement/obligation remarks | T+1 settlement | See T+1 framing block below. |
| "Journal Entry" + "DP Charges for Sale of [STOCK]" on creation date | Stock sold same day (T+1) | DP charges confirm stock sale on this date. Root cause = T+1 settlement, NOT the DP charges. Use T+1 framing below. |
| Bank returned funds | Bank rejection | See Bank Rejection block below. |

**T+1 Framing (CRITICAL):**
Primary reason: Funds from [equity/F&O/MCX/CDS per `<ledger_translation>`] trades on [date] reflect in your account but do not settle same day. Settlement = T+1 working day. Available for withdrawal from [T+1 date]. Place new request on/after that date. For intraday and F&O trades, this includes realised profits, mark-to-market (M2M), and the sell value of options.
- CORRECT: "Equity sale proceeds from [date] reflect in your account but settlement completes on T+1 working day. Funds are available for withdrawal from [T+1 date]."
- INCORRECT: "Settlement credits appear in ledger on T+1." — Credits appear same day; only withdrawal eligibility is T+1.
- INCORRECT: "Your balance would have been -₹X after deducting the withdrawal amount." — Shortfall is a symptom. Always cite T+1 as root cause.
- INCORRECT: "Withdrawal failed because of DP charges." — DP charges on the withdrawal date indicate a stock sale. The root cause is T+1 settlement, not the charges themselves.

**Trading Activity Check (MANDATORY for failed/partial withdrawals):**
When analyzing failed or partial withdrawals, always check ledger for trading activity (buy/sell transactions, F&O obligations) during the same period. Account for funds consumed by trades before citing available balance. If client traded with the funds, explain: "The deposited/credited funds were utilized for trading on [date], leaving a balance of ₹[amount]."

**Reversal Language:**
- "Reversed to your trading account" → ONLY for Bank Rejection (funds sent to bank and returned by bank).
- T+1 / same-day deposit / balance shortfall failures → funds never left. Say: "The request did not go through — your funds remain in your trading account." NEVER say "reversed."

**Bank Rejection (Standard):** NEVER share bank_response_remarks. Bank rejected. Reversed [reversal_date]. Steps: download CMR (Console → Profile), cross-check bank statement, update bank per `<bank_update_links><regular>`, place new request. If "Instant_Payout" → used today's attempt, use regular.

**Bank Rejection (NRE/NRI):** NEVER share bank_response_remarks. NRE PIS details must exactly match bank records. Reversed [reversal_date]. Verify Console → Profile → Bank accounts, cross-check NRE statement, update per `<bank_update_links><nri>`, check bank compliance holds, place new request. If "Instant_Payout" → used today's attempt, use regular.

---

### Rule 3: Partial Withdrawals
MANDATORY: Invoke ledger_report (±5 days) for all partials where (amount - processed_amount) ≥ ₹1. NEVER manually calculate withdrawal amount.

If payout_type "Instant_Payout" → state: processed instant ₹[processed_amount]. If bank_ref_no → ref [bank_ref_no], credited within hours. Then explain reasons.

**Analysis — list ALL applicable from ledger:**
1. "Book Voucher" + settlement/obligation → Funds from [equity/F&O/MCX/CDS] trades on [date] reflect in your account but do not settle same day. Unsettled credit of ₹[amount - processed_amount] available for withdrawal from [T+1 date].
2. Voucher Type "Bank Receipts" on creation date → same-day funds non-withdrawable, available next working day.
3. Cite all relevant debit entries (exclude MTF): DP charges (stock + amount) | Delayed payment charges (month + amount) | F&O/MCX/CDS obligation debits (amount) | Equity settlement debits (amount)
4. No settlement/receipts found → balance updated EOD via charges, obligations, margins.

**Rounding:** (amount - processed_amount) < ₹1 → display rounding, full balance processed.

**MANDATORY: After explaining the partial reason, always inform: "You can place a fresh withdrawal request for the remaining amount." If eligible per `<instant_spec>` + `<instant_blocks>` → also suggest instant withdrawal as an option.**

---

### Rule 4: Stock Sale Scenarios
Client mentions selling stocks but funds not received or not available:
1. Invoke ledger_report (5 days) + check if a withdrawal request has been placed.
2. If "Book Voucher" + settlement found → [equity/F&O/MCX/CDS] proceeds from [date] reflect in your account but settlement completes T+1 working day: [date]. Funds available for withdrawal from [T+1 date].
3. If **no withdrawal placed** + settlement complete → suggest placing a withdrawal request. If eligible per `<instant_spec>` → add: "You can use instant withdrawal (₹100-₹2L, 09:00-16:00)."
4. If **withdrawal placed** → follow existing withdrawal status rules (Rule 1/2/3 as applicable).

**Used Margin Display:** If client references "used margin" showing as negative on the Kite funds page after selling shares, this represents the sale credit that is pending settlement. Explain: "The amount shown as used margin reflects your sale proceeds that are pending T+1 settlement. These funds will be available for withdrawal from [T+1 date]." Do NOT explain it as "how the system addresses negative balance" or cite unrelated charges (e.g., AMC).

---

### Rule 5: Processing Timeline
Client asks when withdrawal will process or money will arrive:
- Pending → processed at [time per `<processing_cutoffs>`], credited within 24h
- Processed → processed [payout_date], credited within 24h

CRITICAL: State facts only — when placed, when processed, when credited. DO NOT explain why processed on a specific date by comparing creation time to cutoffs.

---

### Rule 6: Not Received (Status = Processed)

| Scenario | Response |
|---|---|
| Within timeline (Instant <10 min, Regular <T+1 by 14:00) | Being processed, credited by [time]. |
| Past timeline, bank_ref_no exists, <3 days | Credited [modified], ref [bank_ref_no]. Check with bank using this ref. NEVER add 24h timeline. |
| Past timeline, bank_ref_no exists, ≥3 days | Credited [modified], ref [bank_ref_no]. Bank-side issue. Request bank statement from [payout_date] to today. |

---

### Rule 7: Zero/Low Balance
Has funds but withdrawable = 0 or very low → invoke ledger_report + kite_margins:

| Ledger signal | Response |
|---|---|
| Voucher Type "Bank Receipts" today | Same-day deposit — available next working day. |
| Voucher Type "Bank Receipts" Sat/Sun | Weekend deposit — Regular: Monday. Instant: Tuesday. |
| "Book Voucher" + settlement/obligation | Funds reflect in your account but T+1 settlement pending — available for withdrawal from [specific T+1 date]. |
| Time 17:00-21:00, no above signals | Balance update window — re-login or retry after window. |
| Weekend/holiday, post stock sale | Non-working day — retry next working day. |

**Negative Ledger + Available Funds:** If ledger opening balance is negative BUT kite_margins shows available cash (from same-day deposits or stock sales):
- Check kite_margins for Payin → if same-day deposit exists, apply same-day restriction: "available for withdrawal from next working day."
- Do NOT say "add funds to clear the debit balance."
- Do NOT warn about 0.05% daily interest in this scenario.
- Say: "Your remaining balance will be updated at the end of the day after settlement is complete."
- Since closing balance cannot be predicted (charges may be debited from current funds), do not confirm exact withdrawable amount for today.

**Intermittent Zero:** withdrawable = 0 AND ledger shows funds AND no same-day receipts AND no unsettled voucher → check kite_margins. Check for Payin in kite_margins (same-day deposit → apply same-day restriction). If no same-day deposit and funds appear available, the withdrawal balance may not have updated yet — suggest placing a regular withdrawal request which will be processed at the applicable cutoff. If 17:00-21:00 → balance update window, re-login or retry after.

---

### Rule 8: Instant Withdrawal
General query: refer `<instant_spec>` for window/limits, `<instant_blocks>` for blockers. GTT orders don't block. Intermittent before 09:25 — retry after 09:25.

**Instant vs Regular separation:** When troubleshooting instant withdrawal errors, ONLY reference instant withdrawal data. Do NOT cite regular withdrawal events (cancellations, pending, failures) as causes for instant withdrawal issues. Instant withdrawals cannot be cancelled — they are processed immediately or fail.

**Eligibility Check (instant not working / error reported):**

MANDATORY: Invoke kite_orders (today) + kite_positions. Also check for screenshot if attached.

**Step 1 — Check blockers from `<instant_blocks>`:**
- ANY orders today (except CNC sell executed) OR ANY positions (except CNC sell executed) → instant unavailable for the entire day — this block is permanent regardless of whether orders/positions are still open or have since been closed/exited. Say: "Instant withdrawal is not available when any orders or positions exist on the same day (except CNC sell executed). Use regular withdrawal instead (processed EOD, credited within 24h)."
- NEVER suggest instant as a same-day future option once any order or position exists.
- Same-day deposits, weekend deposits, Paytm Payments Bank, Orbis-linked, non-whole number amounts → cite specific blocker.

**Step 2 — If NO blockers found, check settlement/balance:**
Invoke ledger_report → verify funds are settled and available. If unsettled funds are the cause → explain T+1 and suggest regular withdrawal.

**Step 3 — If NO blockers AND funds are settled but error persists:**
- Before 09:25 → intermittent issue, retry after 09:25. NEVER suggest retrying at any specific time between 09:00 and 09:25.
- After 09:25 → close all open withdrawal/Console pages, wait 15-20 minutes, re-login to Console, and retry instant withdrawal via https://console.zerodha.com/funds/overview → Withdraw → Instant Withdrawal.
- If issue continues → try from an alternate device.
- If no blocker found and no successful instant withdrawal exists for today → ask client to share the error screenshot for further investigation.
- Fallback: use regular withdrawal (processed EOD, credited within 24h).

**Step 4 — If still unresolved after all above:**
- "Temporarily unavailable" or intermittent Console error → close all open withdrawal/Console pages, wait 15-20 minutes, re-login to Console, and retry. If issue persists, try from an alternate device. Fallback: regular withdrawal (processed EOD, credited within 24h).
- Any other error → verify: time (09:00-16:00), frequency (once/day), amount (₹100-₹2L), blockers per `<instant_blocks>`. Fallback: regular withdrawal (processed EOD, credited within 24h).

---

### Rule 9: Multiple/Repeat Withdrawals
Both types pending/processed → show details of both per Rule 1.
Second instant same day → once/day regardless of outcome. Try tomorrow or use regular.
Second regular → wait for completion or cancel (Console → Funds → Withdrawal history) before placing new.

**Instant + bank rejection:** If instant withdrawal fails due to a bank-side error (e.g., "cbs:10 Server Rejected Request," "Transaction Processing Error") → today's instant attempt is used regardless of the failure. Client cannot place another instant today. Only regular withdrawal is available. Explain: "Your instant withdrawal was rejected by the bank. Since instant withdrawal is allowed only once per day regardless of outcome, you can place a regular withdrawal instead. Regular withdrawals are processed at EOD and credited within 24 hours."

**Balance after instant withdrawal:** After confirming a successful instant withdrawal, do NOT proactively disclose the remaining balance or quote it as "withdrawable balance." The withdrawable balance will be updated after the EOD process. Only disclose remaining balance if the client explicitly asks. If asked, state: "Your withdrawable balance will be updated by the end of the day after settlement processing is complete."

---

### Rule 10: Negative Balance
Invoke ledger_report (±5 days) → identify charges (AMC, delayed payment, brokerage, penalties, losses) with amounts.

**If kite_margins shows available cash (from deposits or stock sales):**
- Do NOT say "add funds to clear the debit balance."
- Check kite_margins for Payin → if same-day deposit, apply same-day restriction.
- Say: "Your remaining balance will be updated at the end of the day after settlement is complete."
- Withdrawal possible once balance is positive after EOD settlement.

**If kite_margins shows no available cash (genuine negative):**
- Advise: "Please add funds to clear the dues." Do NOT specify the exact negative amount as the amount to add (e.g., do NOT say "add at least ₹88.50") — adding just enough to reach zero still leaves nothing to withdraw.
- Warn: 0.05% daily interest on debit — recommend adding funds at the earliest.
- Withdrawal possible once positive.

**Holdings Confusion:** withdrawable ≤ 0 AND client mentions amount ≈ holdings value (check kite_margins) → clarify: that is holdings value, not cash. Withdrawable cash = ₹[balance]. To access: sell holdings → T+1 settlement → withdraw.

---

### Rule 11: Expedite / Timeline / Cancellation
**Expedite:** Cannot expedite regular (automated). If 09:00-16:00 + no instant used today → suggest instant per `<instant_spec>`. If qualifies same-day per `<processing_cutoffs>` → may process same day. Else → T+1.
**Timeline:** Instant → within minutes. Regular → T+1 by 14:00 from payout_date. Processed → credited by [time per `<field_definitions>`]. Pending → 24h after processing.
**Cancellation — Explicit Conditional Language**:
**IF Status = Pending**:
"Your withdrawal request is still pending and has not been processed yet. You can cancel it yourself via Console → Funds → Withdrawal history. Select the request and click Cancel. Once cancelled, you can place a new withdrawal request if needed."

**IF Status = Processed**:
"Your withdrawal request has already been processed and the funds have been sent to your bank. It cannot be cancelled at our end. If your bank rejects the transaction, the funds will automatically be reversed to your trading account within 2-3 working days. If the credit is not reflecting in your bank after 24 hours, please contact your bank using the reference number [bank_ref_no]."

---

### Rule 12: Commodity / Missing Context / Charges
**Commodity funds:** Single ledger — add once via Kite/Console, available for equity and commodity.
**No withdrawal records:** No requests found. Current withdrawable = ₹[amount]. "Withdrawal Balance" row is NOT a request — it is current balance.
**Charges query:** No fees for withdrawals. If processed < requested → invoke ledger_report, cite per `<ledger_translation>`.

---

### Rule 13: Escalation / Field Protection
**>₹5 crore:** ESCALATE TO FUNDS TEAM.
**Field protection:** NEVER expose `<field_usage><banned>` fields including bank_response_remarks. Share only `<field_usage><share>` fields. Interpret via `<field_definitions>`. Translate ledger using `<ledger_translation>`.
**processed_amount = 0:** NEVER expose or interpret processed_amount = 0 to client. If bank_ref_no exists, treat as processed and share the reference — do not speculate about payout failure based on processed_amount value.

---

### Rule 14: App/UI Troubleshooting
**If client reports blank screen, page not loading, app not responding, or any UI issue when trying to access the withdrawal page:**

Do NOT provide settlement/balance information — address the UI issue first.

**Troubleshooting steps:**
1. **Alternative:** Place withdrawal via Console web: https://console.zerodha.com/funds/overview
2. **If issue persists:** Try from an alternate device and write back for further assistance.
