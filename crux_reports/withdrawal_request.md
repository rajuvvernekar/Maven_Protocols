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

---

### A1: Withdrawal Types

| Field Value | Label | Specs |
|---|---|---|
| `Instant_Payout` | Instant | ₹100–₹2,00,000 · Once/day regardless of outcome · Window 09:00–16:00 daily (incl. weekends; intermittent before 09:25) · Credited within minutes · Cannot be cancelled |
| `Payout` | Regular | ₹1 to available balance · Up to ₹5 crore via Console (above → Escalate to support agent) · Processed once at applicable cutoff · Credited within 24h of processing · Can be cancelled while Pending via Console → Funds → Withdrawal history |

Type verification is mandatory. Always read the `payout_type` field — only source of truth. If client's stated type ≠ actual field → correct them before proceeding.

One instant AND one regular can be pending simultaneously. A pending regular has no effect on instant availability.

---

### A2: Instant Eligibility

Instant withdrawal is unavailable for the **entire day** if ANY of the following are true (block is permanent for the day even if condition is later resolved):

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

Funds from trades (equity, F&O, MCX, CDS) and same-day deposits reflect in the account on the same day but are not withdrawable until T+1 (next working day, excluding weekends and settlement holidays).

- Stock sale credits appear in ledger same day (after 17:00–21:00 update) but are withdrawable only after T+1 settlement.
- For intraday and F&O trades, T+1 applies to realised profits, M2M, and option sell value.

**Framing rules:**
- Settlement credits appear in ledger same day — only withdrawal eligibility follows T+1.
- DP charges on the date indicate a stock sale — root cause is always T+1 settlement.
- If balance appears insufficient due to unsettled funds, root cause is T+1, not the shortfall amount.

---

### A5: Reversal Language

| Scenario | Meaning |
|---|---|
| Bank rejected (funds were sent to bank, returned by bank) | Funds reversed to trading account |
| T+1 / same-day deposit / balance shortfall (funds never left) | Request did not go through — funds remained in trading account throughout |

"Reversed" applies only when funds actually left the trading account and were returned. Otherwise, funds never left.

---

### A6: Bank Rejection Handling

Applies to both Standard and NRI/NRE accounts. `bank_response_status` and `bank_response_remarks` are for internal reasoning only — never share with client.

**Step 1 — Check ledger** for remarks containing "Transfer rejected by bank":
- Entry EXISTS → Bank rejected withdrawal. Funds already credited back to trading account. Client can place fresh request.
- Entry NOT YET present → Bank rejected withdrawal. Funds reverse to trading account within 24–48 working hours. Client can place fresh request after reversal.

**Step 2 — NPCI rejection check:**
If `bank_response_remarks` contains "NPCI" AND `bank_response_status` = failed → rejection originated from banking/payments infrastructure (NPCI), not Zerodha. Client should check with their bank for the specific reason.
- If `Instant_Payout` → today's instant attempt is used; only regular available rest of the day.
- If `Payout` (Regular) → client can place fresh regular request after confirming with bank that issue is resolved.
- Instant remains unavailable for entire day after NPCI rejection regardless of bank resolution.

**Step 3 — Resolution:**
- Download CMR (Console → Profile), cross-check bank statement.
- Update bank details: https://support.zerodha.com/category/funds/adding-bank-accounts/primary-bank-account/articles/how-do-i-change-my-primary-bank-account-linked-with-zerodha
- If `Instant_Payout` → today's attempt is used; only regular available today.

**Additional for NRI/NRE:** NRE PIS details must exactly match bank records. Verify Console → Profile → Bank accounts, cross-check NRE statement. Bank update: courier form + bank proof (if Aadhaar-linked mobile, e-sign and submit via ticket). Check bank compliance holds.

---

### A7: Suggest Instant Conditions

Before suggesting instant withdrawal, ALL must be true:
1. Current time is 09:00–16:00
2. No instant withdrawal already used today (regardless of outcome)
3. Amount is ₹100–₹2,00,000
4. No blockers per **A2**

---

### A8: Ledger Translation

| Voucher Type | Remarks Pattern | Meaning |
|---|---|---|
| Bank Receipts | (on withdrawal creation date) | Same-day payin → T+1 applies |
| Book Voucher | "Net settlement for Equity with settlement number..." | Equity trade settlement |
| Book Voucher | "Net obligation for Equity F&O" | F&O trade settlement |
| Book Voucher | "Net obligation for MCX commodity FNO" | MCX commodity trade settlement |
| Book Voucher | "Net obligation for CDS FNO" | CDS currency trade settlement |
| Journal Entry | "DP Charges for Sale of [STOCK] on [DATE]" | Stock sold that day → root cause is T+1 settlement |
| Journal Entry | "Delayed payment charges for [Month] - [Year]" | Delayed payment charges — cite month + amount |
| Bank Payments | "Funds transferred back as part of quarterly settlement" or remarks containing "quarterly settlement" | Quarterly settlement (QS) — unused funds returned to client's primary bank per SEBI mandate |

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
- `processed_amount = 0` with `bank_ref_no` present: treat as processed and share the reference number.
- Financial figures: Always display to 2 decimal places (e.g., ₹1,119.96, ₹45.14).

---

### A10: Withdrawable Balance Rules

- Always use the withdrawable balance as shown in the system.
- When collateral margin exists, use withdrawal balance from `ledger_report`. Use ONLY "Available Cash" from `kite_margins` (not "Available Margin," which includes collateral).
- If client has traded during the day: withdrawable balance may change after market closing as charges and obligations update during EOD process (5 PM to 9 PM).

---

### A11: Links

| Purpose | URL |
|---|---|
| Bank update (regular) | https://support.zerodha.com/category/funds/adding-bank-accounts/primary-bank-account/articles/how-do-i-change-my-primary-bank-account-linked-with-zerodha |
| Bank verification for withdrawal | https://support.zerodha.com/category/funds/fund-withdrawal/withdrawal-process/articles/select-bank-for-withdrawal |
| Console withdrawal page | https://console.zerodha.com/funds/overview |

---

## Section B: Decision Flow

On every withdrawal query, execute in order:

```
1. PREFLIGHT
   ├─ get_all_client_data → check account type, active segments (ZBL_MCX)
   ├─ If NRI PIS → STOP. Escalate to support agent.
   ├─ Fetch last 3 withdrawals (both types, descending)
   ├─ Verify payout_type field for each (correct client if misidentified)
   ├─ For each fetched withdrawal, compare amount vs processed_amount.
   │   If processed_amount < amount AND the difference ≥ ₹1 → route to Rule 3.
   ├─ If any fetched withdrawal has creation date of today, note its status.
   │   Address this existing request's status before suggesting a new one.
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
   └─ >₹5 crore → Escalate to support agent

3. FALLBACK
   If all mandatory checks completed and no root cause identified →
   ask client for a screenshot of the error to investigate further.
```

**Scope:** Only address what the customer asked.

**Settlement Holiday Check:** If a settlement holiday falls within the relevant date range, verify against the settlement holiday list in the system prompt. Mention only confirmed holidays — refer to unconfirmed dates as "a settlement holiday."

---

## Section C: Rules

---

### Rule 1: Status Responses

| Status | Logic |
|---|---|
| **Processed** | Share creation date, payout_date. If `bank_ref_no` exists → credit already sent, share modified date + ref number. Client should check with bank using ref. If no `bank_ref_no` → credit expected within 24h. |
| **Bank_Reconciliation_Pending** | Transaction pending at bank. May take up to 48h for bank to update. If rejected, funds reverse to trading account. Share bank_ref_no if exists. Status name is internal only — don't share it. Resolution steps only if it later fails. |
| **Pending (Regular)** | Will be processed at time per **A3**. Check ZBL_MCX from preflight. Credit within 24h after processing. |
| **Pending (Instant)** | Typically credited within minutes. |
| **Canceled** | Canceled at modified time. Only client can cancel (Console → Funds → Withdrawal history) — Zerodha-initiated issues appear as Failed/Rejected. Client can place new request. If confused → check ledger for T+1/settlement context. If eligible per **A7** → suggest instant. |

---

### Rule 2: Failed Withdrawals

Always invoke `ledger_report` (±3 days from creation).

| Ledger Signal | Cause | Logic |
|---|---|---|
| "Bank Receipts" on creation date | Same-day deposit | Funds remain in account per **A5**. Same-day deposits can be used for trading immediately but withdrawal only available next day due to EOD settlement/reconciliation. Client can place new request next working day. |
| "Bank Receipts" on Sat/Sun + `Instant_Payout` | Weekend deposit | Regular available now. Instant available Tuesday. |
| "Book Voucher" + settlement/obligation remarks | T+1 settlement | Apply **A4** — cite segment, trade date, T+1 date. |
| "Journal Entry" + "DP Charges for Sale of [STOCK]" on creation date | Stock sold same day | DP charges confirm the sale. Root cause is T+1 per **A4**. |
| `bank_response_status` = failed | Bank rejection | Follow **A6** (including NPCI check). |

**Trading Activity Check:** Always check ledger for trading activity during the same period. If client traded with the funds, note that deposited/credited funds were utilised for trading on that date and state the remaining balance.

Use **A5** for reversal language.

---

### Rule 3: Partial Withdrawals

Invoke `ledger_report` (±5 days) for all partials where `(amount - processed_amount)` ≥ ₹1.

If `Instant_Payout` → state processed instant amount. If bank_ref_no exists → share ref, credit within hours.

**Identify all applicable causes from ledger (using A8):**
1. Settlement/obligation entries → apply **A4**, cite unsettled amount and T+1 date.
2. "Bank Receipts" on creation date → same-day funds non-withdrawable, available next working day.
3. Relevant debit entries (exclude MTF per **A8**): DP charges, delayed payment charges, F&O/MCX/CDS obligation debits, equity settlement debits. Cite each with amount.
4. No signals found → balance updated EOD via charges, obligations, margins.

**Rounding:** If `(amount - processed_amount)` < ₹1 → display rounding, full balance processed.

**Before suggesting fresh withdrawal:**
1. Verify current withdrawable balance supports the remaining amount.
2. If root cause is same-day deposit or T+1 → suggest fresh request for next working day, not today.
3. If eligible per **A7** → suggest instant as alternative.

Always inform client they can place a fresh request for the remaining amount (amount - processed_amount) with applicable timing from above.

---

### Rule 4: Stock Sale Scenarios

Client mentions selling stocks but funds not received/available.

1. Invoke `ledger_report` (5 days) + `kite_holdings` + check if withdrawal request has been placed.
2. If settlement entry found → apply **A4**.
3. If no withdrawal placed + settlement complete → suggest placing a request. If eligible per **A7** → suggest instant.
4. If withdrawal placed → follow Rule 1/2/3 as applicable.
5. If withdrawable balance is ₹0 or insufficient AND `kite_holdings` shows total holdings value approximately matching the requested amount → funds are held in equity holdings, not available as cash. Client needs to sell shares, then withdraw after T+1 settlement per **A4**.

**"Used margin" display:** If client references "used margin" showing negative after selling shares → amount shown reflects sale proceeds pending T+1 settlement. Funds available for withdrawal from T+1 date. Root cause is strictly T+1 — not system behavior, negative balance mechanics, or unrelated charges.

---

### Rule 5: Processing Timeline

- **Pending** → processed at time per **A3**, credited within 24h.
- **Processed** → processed at payout_date, credited within 24h.

State facts only — when placed, when processed, when credited.

---

### Rule 6: Not Received (Status = Processed)

| Scenario | Logic |
|---|---|
| Within timeline (Instant <10 min, Regular <T+1 by 14:00) | Still being processed, credit expected by applicable time. |
| Past timeline + bank_ref_no exists + <3 days | Credit sent at modified time with ref. Client should check with bank. |
| Past timeline + bank_ref_no exists + ≥3 days | Credit sent at modified time with ref. Bank-side issue. Request bank statement from payout_date to today. |

---

### Rule 7: Balance Discrepancy (Zero / Low / Negative)

Invoke `ledger_report` + `kite_margins`.

**If withdrawable is zero or low:**

| Ledger Signal | Logic |
|---|---|
| "Bank Receipts" today | Same-day deposit — available next working day. |
| "Bank Receipts" Sat/Sun | Weekend deposit — Regular: Monday. Instant: Tuesday. |
| Settlement/obligation entry | Apply **A4** with specific T+1 date. |
| Remarks containing "quarterly settlement" | Quarterly settlement — unused funds returned to client's primary bank per SEBI mandate. Occurs first Friday of each quarter (Jan, Apr, Jul, Oct). If account inactive 30 consecutive days, settlement occurs monthly. Client should check bank for credited amount. Can add funds again and place withdrawal if needed. |
| Time 17:00–21:00, no above signals | Balance update window — re-login or retry after. |
| Weekend/holiday, post stock sale | Non-working day — retry next working day. |
| No signals, funds appear in ledger | Check kite_margins for Payin (same-day deposit → T+1). If no same-day deposit, balance may not have updated — suggest regular withdrawal which processes at applicable cutoff. If 17:00–21:00 → balance update window. |

**If negative balance with available cash in kite_margins (from deposits or stock sales):**
- Check kite_margins for Payin → if same-day deposit, T+1 applies.
- Temporary state — balance updates after EOD settlement.
- Exact withdrawable amount confirmed only after EOD processing (charges may apply).
- Withdrawal possible once balance is positive after EOD.

**If negative balance with no available cash (genuine negative):**
- Invoke ledger_report (±5 days) to identify charges: AMC fees, delayed payment charges, brokerage, penalties, or trading losses.
- Client needs to add funds to clear dues. Amount should cover dues plus desired withdrawal — clearing to zero leaves nothing to withdraw.
- 0.05% daily interest applies on debit balances — recommend adding funds at earliest.
- Withdrawal possible once balance is positive.

**Holdings confusion:** Withdrawable ≤ 0 and client mentions amount ≈ holdings value (check kite_margins) → that amount reflects holdings value, not cash. To access: sell holdings → T+1 settlement → withdraw. State actual withdrawable cash balance.

---

### Rule 8: Instant Withdrawal Issues

**General query:** Refer to **A1** for specs, **A2** for blockers. GTT orders are confirmed non-blockers. Intermittent before 09:25 — retry after 09:25.

When troubleshooting instant issues, use only instant withdrawal data. Instant and regular are independent tracks.

**Eligibility troubleshooting (error reported or "not working"):**

Invoke `kite_orders` (today) + `kite_positions`. Check for attached screenshot.

**Step 1 — Check A2 blockers:**

Before citing orders/positions as the blocker, compare ticket creation time (or client's reported error time) against earliest order/position timestamp. If earliest order/position was placed after the reported error time, those cannot be the cause — skip to Step 3. Then acknowledge instant is now blocked for rest of day due to subsequent trading, offer regular per **A3**.

- Filter out CNC sell executed orders/positions — confirmed non-blockers per **A2**.
- If any non-CNC-sell-executed orders/positions exist and were placed before the error → instant unavailable due to same-day orders/positions (except CNC sell executed). Regular is the only same-day option.
- Same-day deposit, weekend deposit, Paytm, Orbis, non-whole amount → cite specific blocker.
- If `bank_response_remarks` contains "NPCI" AND `bank_response_status` = failed → follow **A6** Step 2. Instant unavailable rest of day.

**Step 2 — No blockers found → check settlement/balance:**
Invoke `ledger_report`. If unsettled funds → apply **A4**, suggest regular.

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

**Instant + bank rejection:** Today's attempt is used regardless of failure. Only regular available today. If `bank_response_remarks` contains "NPCI" → also follow **A6** Step 2.

**Balance after instant:** Only share remaining balance if client explicitly asks. Default: withdrawable balance will be updated by EOD after settlement processing.

---

### Rule 10: Expedite / Timeline / Cancellation

**Expedite:** Regular withdrawals are automated, cannot be expedited. If eligible per **A7** → suggest instant. If qualifies same-day per **A3** → may process same day. Else T+1.

**Timeline:** Instant → within minutes. Regular → T+1 by 14:00 from payout_date. If Processed → credited by modified time per **A9**. If Pending → credited within 24h after processing.

**Cancellation:**
- **Pending:** Request not yet processed. Client can cancel via Console → Funds → Withdrawal history → select request → Cancel. Can place new request after cancellation.
- **Processed:** Funds already sent to bank, cannot be cancelled. If bank rejects, funds auto-reverse to trading account within 2–3 working days. If credit not reflecting after 24h, client should contact bank with the bank_ref_no.

---

### Rule 11: Commodity / No Records / Charges

- **Commodity funds:** Single ledger — add once via Kite/Console, available for equity and commodity.
- **No withdrawal records:** No requests found. Current withdrawable = ₹[amount]. "Withdrawal Balance" row is current balance, not a withdrawal request.
- **Charges query:** All withdrawal requests are free of charge. If processed < requested → invoke `ledger_report`, cite per **A8**.

---

### Rule 12: App / UI Troubleshooting

If client reports blank screen, page not loading, app not responding, or any UI issue on withdrawal page — address UI issue first. Settlement/balance info comes after UI is resolved.

1. Place withdrawal via Console web: https://console.zerodha.com/funds/overview
2. If issue persists → try alternate device and write back for further assistance.
