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

## Protocol

# WITHDRAWAL PROTOCOL 

---

## Section A: Reference Data

All rules reference these blocks as single sources of truth. If a definition exists here, rules must not restate it — only cite the block ID.

---

### A1: Withdrawal Types

| Field Value | Label | Specs |
|---|---|---|
| `Instant_Payout` | Instant | ₹100–₹2,00,000 · Once/day regardless of outcome · Window 09:00–16:00 daily (incl. weekends; intermittent before 09:25) · Credited within minutes · Cannot be cancelled |
| `Payout` | Regular | ₹1 to available balance · Up to ₹5 crore via Console (above → **ESCALATE** — funds team review needed) · Processed once at applicable cutoff · Credited within 24h of processing · Can be cancelled while Pending via Console → Funds → Withdrawal history |

**Type verification is mandatory.** Always read the `payout_type` field — it is the only source of truth. If client's stated type ≠ actual field → correct explicitly before proceeding: *"This is a [actual type] withdrawal, not [stated type]."*

One instant AND one regular can be pending simultaneously. A pending regular has no effect on instant availability.

---

### A2: Instant Eligibility

Instant withdrawal is unavailable for the **entire day** if ANY of the following are true (the block is permanent for the day even if the condition is later resolved):

- Any orders today (pending/executed/rejected/cancelled) **except** CNC sell executed
- Any positions today (open/closed) **except** CNC sell executed
- Same-day deposit
- Weekend deposit (blocked until Tuesday)
- Settlement holiday/weekend affecting previous-day holdings
- Paytm Payments Bank account
- Orbis-linked account
- Non-whole-number amount

**Confirmed non-blockers:** GTT orders, pending regular withdrawals.

---

### A3: Processing Cutoffs

| Condition | Processed at | Credit by |
|---|---|---|
| Saturday | 16:30 | Within 24h |
| Sunday / settlement holiday | Next working day cutoff | Within 24h of processing |
| Weekday + ZBL_MCX active | 23:59 | Within 24h |
| Weekday + before 17:00 + no trades/positions/instant + sufficient balance | Same-day | Same-day bank credit |
| Weekday + before 17:00 + has trades/positions/instant | 22:00 | Within 24h |
| Weekday + after 17:00 (no ZBL_MCX) | 22:00 | Within 24h |

Note: 17:00 is the same-day bank credit condition only, not a universal cutoff. Standard weekday processing = 22:00.

---

### A4: T+1 Settlement Rule

**Definition:** Funds from trades (equity, F&O, MCX, CDS) and same-day deposits reflect in the account on the same day but are not available for withdrawal until T+1 (next working day, excluding weekends and settlement holidays).

- Stock sale credits appear in ledger same day (after 17:00–21:00 update) but are withdrawable only after T+1 settlement completes.
- For intraday and F&O trades, T+1 applies to realised profits, mark-to-market (M2M), and option sell value.

**Standard T+1 response template:**
> Funds from your [segment] trades on [date] reflect in your account but settlement completes on the next working day. Your funds will be available for withdrawal from [T+1 date]. You can place a new withdrawal request on or after that date.

**Framing rules:**
- Settlement credits appear in ledger same day — only *withdrawal eligibility* follows T+1. Always frame it this way.
- DP charges on the date indicate a stock sale — always cite T+1 settlement as the root cause.
- If balance appears insufficient, cite T+1 as the root cause, not the shortfall amount. T+1 is the explanation; the shortfall is just a symptom.

---

### A5: Reversal Language

| Scenario | Language |
|---|---|
| Bank rejected (funds were sent to bank, returned by bank) | "Reversed to your trading account" |
| T+1 / same-day deposit / balance shortfall (funds never left) | "The request did not go through — your funds remain in your trading account" |

"Reversed" applies only when funds actually left the trading account and were returned by the bank. In all other cases, funds remained in the account throughout.

---

### A6: Bank Rejection Handling

Applies to both Standard and NRI/NRE accounts. Use `bank_response_status` for internal reasoning only. Use `bank_response_remarks` for internal reasoning only. Client communication relies on ledger entries and the templates below.

**Step 1 — Check ledger** for remarks containing "Transfer rejected by bank":
- Entry EXISTS → *"Your withdrawal was rejected by your bank and the funds have been credited back to your trading account. You can place a fresh withdrawal request."*
- Entry NOT YET present → *"Your withdrawal was rejected by your bank. The funds will be reversed to your trading account within 24–48 working hours, after which you can place a fresh withdrawal request."*

**Step 2 — NPCI rejection check:**
If `bank_response_remarks` contains "NPCI" AND `bank_response_status` = failed → the rejection originated from the banking/payments infrastructure (NPCI), not from Zerodha.
- *"Your withdrawal was declined by your bank's payment network (NPCI). Please check with your bank for the specific reason."*
- If `Instant_Payout` → today's instant attempt is used; only regular withdrawal is available for the rest of the day.
- If `Payout` (Regular) → client can place a fresh regular withdrawal request after confirming with their bank that the issue is resolved.
- Instant withdrawal remains unavailable for the entire day after an NPCI rejection, regardless of the bank's resolution.

**Step 3 — Resolution:**
- Download CMR (Console → Profile), cross-check bank statement.
- Update bank details per: https://support.zerodha.com/category/funds/adding-bank-accounts/primary-bank-account/articles/how-do-i-change-my-primary-bank-account-linked-with-zerodha
- If `Instant_Payout` → today's attempt is used; only regular available today.

**Additional for NRI/NRE:** NRE PIS details must exactly match bank records. Verify Console → Profile → Bank accounts, cross-check NRE statement. Bank update: courier form + bank proof (if Aadhaar-linked mobile, e-sign and submit via ticket). Check bank compliance holds.

---

### A7: Suggest Instant Template

Use this whenever suggesting instant withdrawal as an alternative. Check ALL conditions before suggesting:

1. Current time is 09:00–16:00
2. No instant withdrawal already used today (regardless of outcome)
3. Amount is ₹100–₹2,00,000
4. No blockers per **A2**

If all pass → *"You can also use instant withdrawal (₹100–₹2,00,000, available 09:00–16:00, credited within minutes)."*

---

### A8: Ledger Translation

| Voucher Type | Remarks Pattern | Meaning |
|---|---|---|
| Bank Receipts | (on withdrawal creation date) | Same-day payin → T+1 applies |
| Book Voucher | "Net settlement for Equity with settlement number..." | Equity trade settlement |
| Book Voucher | "Net obligation for Equity F&O" | F&O trade settlement |
| Book Voucher | "Net obligation for MCX commodity FNO" | MCX commodity trade settlement |
| Book Voucher | "Net obligation for CDS FNO" | CDS currency trade settlement |
| Journal Entry | "DP Charges for Sale of [STOCK] on [DATE]" | Stock sold that day → root cause is T+1 settlement. Cite stock + amount. |
| Journal Entry | "Delayed payment charges for [Month] - [Year]" | Delayed payment charges. Cite month + amount. |
| Bank Payments | "Funds transferred back as part of quarterly settlement" or remarks containing "quarterly settlement" | Quarterly settlement (QS) — unused funds returned to client's primary bank account per SEBI mandate. |

**Exclude from client responses:** All MTF entries (initial margin, MTF interest, pledge/unpledge charges, MTM obligation).

---

### A9: Field Rules

**Shareable fields:** status, creation, modified, payout_date, amount, processed_amount, bank_ref_no, payout_type

**Internal reasoning only:** bank_response_remarks, bank_response_status, voucher_type, voucher_no, posting_date, debit, credit, payout_category, remarks, client_id

**Field definitions:**
- `creation` = when client placed request
- `payout_date` = when Zerodha processed
- `modified` = credit time if bank_ref_no exists, else last update time

**Special rules:**
- `processed_amount = 0` with `bank_ref_no` present: treat as processed and share the reference number. The processed_amount value is for internal use only.
- Financial figures: Always display to 2 decimal places (e.g., ₹1,119.96, ₹45.14).

---

### A10: Withdrawable Balance Rules

- Always use the withdrawable balance as shown in the system.
- When collateral margin exists, use the withdrawal balance calculation from `ledger_report`. Use ONLY the "Available Cash" field from `kite_margins` (not "Available Margin," which includes collateral).
- If client has traded during the day: *"The withdrawable balance may change after market closing as charges and obligations are updated during the EOD process (5 PM to 9 PM)."*

---

### A11: Links

| Purpose | URL |
|---|---|
| Bank update (regular) | https://support.zerodha.com/category/funds/adding-bank-accounts/primary-bank-account/articles/how-do-i-change-my-primary-bank-account-linked-with-zerodha |
| Bank verification for withdrawal | https://support.zerodha.com/category/funds/fund-withdrawal/withdrawal-process/articles/select-bank-for-withdrawal |
| Console withdrawal page | https://console.zerodha.com/funds/overview |

**Escalation behavior:** When any rule in this protocol says **ESCALATE**, do not draft a customer-facing response. Instead, output only: **HUMAN AGENT ACTION REQUIRED** — followed by the reason from the rule. The human agent will handle the query manually.

---

## Section B: Decision Flow

On every withdrawal query, execute in order:

```
1. PREFLIGHT
   ├─ get_all_client_data → check account type, active segments (ZBL_MCX)
   ├─ If NRI PIS → STOP. **ESCALATE** — NRI team review needed.
   ├─ Fetch last 3 withdrawals (both types, descending)
   ├─ Verify payout_type field for each (correct client if misidentified)
   ├─ For each fetched withdrawal, compare amount vs processed_amount.
   │   If processed_amount < amount AND the difference ≥ ₹1 → route to Rule 3 (Partial Withdrawals).
   ├─ If any fetched withdrawal has a creation date of today, note its status.
   │   Address this existing request's status before suggesting a new withdrawal request.
   └─ Communicate status of ALL fetched withdrawals relevant to client's query

2. ROUTE by client intent
   ├─ Status inquiry → Rule 1
   ├─ Failed withdrawal → Rule 2
   ├─ Partial withdrawal → Rule 3
   ├─ Sold stocks / funds not available → Rule 4
   ├─ Processing timeline question → Rule 5
   ├─ "Not received" (status = Processed) → Rule 6
   ├─ Zero/low/negative balance → Rule 7
   ├─ Instant withdrawal issue → Rule 8
   ├─ Multiple/repeat withdrawals → Rule 9
   ├─ Expedite / cancel → Rule 10
   ├─ Commodity / charges / no records → Rule 11
   ├─ App/UI issue → Rule 12
   └─ >₹5 crore → **ESCALATE** — funds team review needed

3. FALLBACK
   If all mandatory checks completed and no root cause identified →
   "Could you share a screenshot of the error you're seeing?
   This will help us investigate further."
```

**Scope:** Only address what the customer asked. Do not volunteer information about payins, holdings, positions, or other unrelated topics unless the query directly involves them.

**Settlement Holiday Check:** If a settlement holiday falls within the relevant date range, verify against the settlement holiday list in the system prompt. Mention only confirmed holidays — refer to unconfirmed dates as "a settlement holiday."

---

## Section C: Rules

Rules reference Section A blocks. They do not redefine what is already defined there.

---

### Rule 1: Status Responses

| Status | Response |
|---|---|
| **Processed** | Placed [creation], processed [payout_date]. If `bank_ref_no` exists → credited [modified], ref [bank_ref_no]. Ask client to check with bank using this ref. When bank_ref_no exists, the credit has already been sent — share the ref only. If no `bank_ref_no` → credited within 24h. |
| **Bank_Reconciliation_Pending** | Use only this client-facing language: *"The transaction is currently pending at your bank. It may take up to 48 hours for your bank to update the transaction. If the withdrawal gets rejected, it will be reversed to your trading account."* Share bank_ref_no if exists. The status name itself is internal only. The client should wait for the bank to process — resolution steps come only if it later fails. |
| **Pending (Regular)** | Processed at [time per **A3**]. Check ZBL_MCX from preflight. Credited within 24h after processing. |
| **Pending (Instant)** | Typically credited within minutes. State the expected timeline only. |
| **Canceled** | Canceled [modified]. Only the client can cancel (Console → Funds → Withdrawal history) — you canceled this request. Zerodha-initiated issues appear as Failed/Rejected. Can place new request. If client seems confused → check ledger for T+1/settlement context. If eligible per **A7** → suggest instant. |

---

### Rule 2: Failed Withdrawals

Always invoke `ledger_report` (±3 days from creation).

**Identify cause from ledger:**

| Ledger Signal | Cause | Response |
|---|---|---|
| "Bank Receipts" on creation date | Same-day deposit | Funds in account per **A5**. Place new request next working day. |
| "Bank Receipts" on Sat/Sun + `Instant_Payout` | Weekend deposit | Use regular now or instant Tuesday. |
| "Book Voucher" + settlement/obligation remarks | T+1 settlement | Use **A4** template. |
| "Journal Entry" + "DP Charges for Sale of [STOCK]" on creation date | Stock sold same day | DP charges confirm the sale. Root cause is T+1 per **A4**. |
| `bank_response_status` = failed | Bank rejection | Follow **A6** (including NPCI rejection check in Step 2). |

**Trading Activity Check:** Always check ledger for trading activity during the same period. If client traded with the funds, explain: *"The deposited/credited funds were utilized for trading on [date], leaving a balance of ₹[amount]."*

Use **A5** for reversal language.

---

### Rule 3: Partial Withdrawals

Invoke `ledger_report` (±5 days) for all partials where `(amount - processed_amount)` ≥ ₹1.

If `Instant_Payout` → state: processed instant ₹[processed_amount]. If bank_ref_no → ref [bank_ref_no], credited within hours.

**Identify all applicable causes from ledger (using A8):**
1. Settlement/obligation entries → use **A4** template, citing unsettled credit of ₹[amount - processed_amount] and T+1 date.
2. "Bank Receipts" on creation date → same-day funds non-withdrawable, available next working day.
3. Relevant debit entries (exclude MTF per **A8**): DP charges, delayed payment charges, F&O/MCX/CDS obligation debits, equity settlement debits. Cite each with amount.
4. No signals found → balance updated EOD via charges, obligations, margins.

**Rounding:** If `(amount - processed_amount)` < ₹1 → display rounding, full balance processed.

**Before suggesting a fresh withdrawal request, verify:**
1. Current withdrawable balance supports the remaining amount.
2. If the root cause is same-day deposit or T+1 settlement, suggest the fresh request for the next working day (not today).
3. If eligible per **A7** → suggest instant as an alternative.

After explaining, always inform: *"You can place a fresh withdrawal request for the remaining amount of ₹[amount - processed_amount]."* with the applicable timing from the pre-checks above.

---

### Rule 4: Stock Sale Scenarios

Client mentions selling stocks but funds not received/available.

1. Invoke `ledger_report` (5 days) + check if a withdrawal request has been placed.
2. If settlement entry found → use **A4** template.
3. If no withdrawal placed + settlement complete → suggest placing a withdrawal request. If eligible per **A7** → suggest instant.
4. If withdrawal placed → follow Rule 1/2/3 as applicable.

**"Used margin" display:** If client references "used margin" showing as negative on Kite funds page after selling shares → *"The amount shown as used margin reflects your sale proceeds that are pending T+1 settlement. These funds will be available for withdrawal from [T+1 date]."* The explanation is strictly T+1 settlement — not system behavior, negative balance mechanics, or unrelated charges (e.g., AMC).

---

### Rule 5: Processing Timeline

Client asks when withdrawal will process or money will arrive.

- **Pending** → processed at [time per **A3**], credited within 24h.
- **Processed** → processed [payout_date], credited within 24h.

State facts only — when placed, when processed, when credited.

---

### Rule 6: Not Received (Status = Processed)

| Scenario | Response |
|---|---|
| Within timeline (Instant <10 min, Regular <T+1 by 14:00) | Being processed, credited by [time]. |
| Past timeline + bank_ref_no exists + <3 days | Credited [modified], ref [bank_ref_no]. Check with bank. Share only the ref — the credit has been sent. |
| Past timeline + bank_ref_no exists + ≥3 days | Credited [modified], ref [bank_ref_no]. Bank-side issue. Request bank statement from [payout_date] to today. |

---

### Rule 7: Balance Discrepancy (Zero / Low / Negative)

Invoke `ledger_report` + `kite_margins`.

**If withdrawable is zero or low:**

| Ledger Signal | Response |
|---|---|
| "Bank Receipts" today | Same-day deposit — available next working day. |
| "Bank Receipts" Sat/Sun | Weekend deposit — Regular: Monday. Instant: Tuesday. |
| Settlement/obligation entry | Use **A4** template with specific T+1 date. |
| Remarks containing "quarterly settlement" or "Funds transferred back as part of quarterly settlement" (check ledger ±14 days) | Quarterly settlement — *"Your funds of ₹[amount from ledger entry] were transferred back to your primary bank account as part of the quarterly settlement of unused funds, as mandated by SEBI. This settlement occurs on the first Friday of each quarter (January, April, July, October). If your account has been inactive for 30 consecutive days, settlement occurs monthly. Please check your bank account for the credited amount. You can add funds again and place a withdrawal request if needed."* |
| Time 17:00–21:00, no above signals | Balance update window — re-login or retry after. |
| Weekend/holiday, post stock sale | Non-working day — retry next working day. |
| No signals, funds appear in ledger | Check kite_margins for Payin (same-day deposit → apply T+1). If no same-day deposit, balance may not have updated — suggest placing a regular withdrawal which will be processed at the applicable cutoff. If 17:00–21:00 → balance update window. |

**If negative balance with available cash in kite_margins (from deposits or stock sales):**
- Check kite_margins for Payin → if same-day deposit, apply T+1 restriction.
- This is a temporary state — the balance will update after EOD settlement.
- Say: *"Your remaining balance will be updated at the end of the day after settlement is complete."*
- The exact withdrawable amount will only be confirmed after EOD processing (charges may apply).
- Withdrawal possible once balance is positive after EOD settlement.

**If negative balance with no available cash (genuine negative):**
- Invoke ledger_report (±5 days) to identify charges: AMC fees, delayed payment charges, brokerage, penalties, or trading losses.
- Advise: *"Please add funds to clear the dues."* The amount to add should cover the dues plus whatever withdrawal amount is needed — clearing the debit to zero alone leaves nothing to withdraw.
- Inform: 0.05% daily interest applies on debit balances — recommend adding funds at the earliest.
- Withdrawal possible once balance is positive.

**Holdings confusion:** Withdrawable ≤ 0 and client mentions amount ≈ holdings value (check kite_margins) → *"That amount reflects your holdings value, not cash. Withdrawable cash = ₹[balance]. To access: sell holdings → T+1 settlement → withdraw."*

---

### Rule 8: Instant Withdrawal Issues

**General query:** Refer to **A1** for specs, **A2** for blockers. GTT orders are confirmed non-blockers. Intermittent before 09:25 — retry after 09:25.

When troubleshooting instant issues, use only instant withdrawal data. Instant and regular are independent tracks.

**Eligibility troubleshooting (error reported or "not working"):**

Invoke `kite_orders` (today) + `kite_positions`. Check for attached screenshot.

**Step 1 — Check A2 blockers:**
- Filter out CNC sell executed orders/positions first — these are confirmed non-blockers per **A2**.
- Evaluate only the remaining orders/positions. If any non-CNC-sell-executed orders or positions exist → cite them: *"Instant withdrawal is not available when any orders or positions exist on the same day (except CNC sell executed). Use regular withdrawal instead (processed EOD, credited within 24h)."* Once any such order/position exists for the day, regular is the only same-day option.
- Same-day deposit, weekend deposit, Paytm, Orbis, non-whole amount → cite specific blocker.
- If `bank_response_remarks` contains "NPCI" AND `bank_response_status` = failed → follow **A6** Step 2 (NPCI rejection). Instant is unavailable for the rest of the day.

**Step 2 — No blockers found → check settlement/balance:**
Invoke `ledger_report`. If unsettled funds → explain T+1 per **A4**, suggest regular.

**Step 3 — No blockers, funds settled, error persists:**
- Before 09:25 → intermittent issue, retry after 09:25.
- After 09:25 → close all open withdrawal/Console pages, wait 15–20 minutes, re-login, retry via https://console.zerodha.com/funds/overview → Withdraw → Instant Withdrawal.
- If issue continues → try alternate device.
- If still unresolved → apply Section B fallback (request screenshot).
- Always offer regular as fallback.

---

### Rule 9: Multiple / Repeat Withdrawals

- Both types pending/processed → show details of both per Rule 1.
- Second instant same day → once/day regardless of outcome. Try tomorrow or use regular.
- Second regular → wait for completion or cancel (Console → Funds → Withdrawal history) before placing new.

**Instant + bank rejection:** Today's attempt is used regardless of failure (e.g., "cbs:10 Server Rejected Request", "Transaction Processing Error"). Only regular available today. Explain: *"Your instant withdrawal was rejected by the bank. Since instant withdrawal is allowed only once per day regardless of outcome, you can place a regular withdrawal instead (processed EOD, credited within 24h)."* If `bank_response_remarks` contains "NPCI" → also follow **A6** Step 2.

**Balance after instant:** Only share remaining balance if client explicitly asks. Default response: *"Your withdrawable balance will be updated by the end of the day after settlement processing is complete."*

---

### Rule 10: Expedite / Timeline / Cancellation

**Expedite:** Regular withdrawals are automated and cannot be expedited. If eligible per **A7** → suggest instant. If qualifies same-day per **A3** → may process same day. Else T+1.

**Timeline:** Instant → within minutes. Regular → T+1 by 14:00 from payout_date. If status is Processed → credited by [modified time per **A9**]. If status is Pending → credited within 24h after processing.

**Cancellation:**
- **Pending:** *"Your withdrawal request is still pending and has not been processed yet. You can cancel it yourself via Console → Funds → Withdrawal history. Select the request and click Cancel. Once cancelled, you can place a new withdrawal request if needed."*
- **Processed:** *"Your withdrawal request has already been processed and the funds have been sent to your bank. It cannot be cancelled at our end. If your bank rejects the transaction, the funds will automatically be reversed to your trading account within 2–3 working days. If the credit is not reflecting in your bank after 24 hours, please contact your bank using the reference number [bank_ref_no]."*

---

### Rule 11: Commodity / No Records / Charges

- **Commodity funds:** Single ledger — add once via Kite/Console, available for equity and commodity.
- **No withdrawal records:** No requests found. Current withdrawable = ₹[amount]. "Withdrawal Balance" row is current balance, not a withdrawal request.
- **Charges query:** All withdrawal requests are free of charge. If processed < requested → invoke `ledger_report`, cite per **A8**.

---

### Rule 12: App / UI Troubleshooting

If client reports blank screen, page not loading, app not responding, or any UI issue on the withdrawal page — address the UI issue first. Settlement/balance information comes after the UI issue is resolved.

1. Place withdrawal via Console web: https://console.zerodha.com/funds/overview
2. If issue persists → try alternate device and write back for further assistance.

---

## Section D: General Notes

- Withdrawals can be made to any linked bank account (primary, secondary, tertiary). Client selects the preferred account on Console after entering the amount. Secondary/tertiary accounts that are not penny-drop verified will show as unavailable with "Account verification is pending." Verification steps: see **A11** bank verification link.
- Withdrawable balance updates 17:00–21:00 daily and may show zero intermittently during this window.
- Dormant accounts can withdraw.
- NRI PIS accounts require NRI team verification (handled in preflight).
- All withdrawal requests are free of charge.
- Amount >₹5 crore → **ESCALATE** — funds team review needed.
