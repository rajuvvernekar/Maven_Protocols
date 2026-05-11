# ledger_report

## Description

WHEN TO USE:

When clients:
- Ask about withdrawal failure reasons (same-day funds, settlement pending, balance issues)
- Report partial withdrawal processed and question the difference in amount
- Report zero or low withdrawable balance despite having funds (same-day deposits, unsettled trades)
- Report sold stocks but can't withdraw or funds not showing (settlement status)
- Ask about quarterly settlement payout status, amount, or timing
- Ask why they were not settled in previous quarter or why settlement is monthly instead of quarterly
- Ask about opting out of settlement or changing settlement frequency
- Ask about a specific transaction in their account history
- Report adding funds and trying to withdraw same day
- Ask about LIQUIDCASE or moving funds to prevent settlement
- Ask about ledger balance, opening balance, closing balance, or fund statement
- Ask about a specific debit or credit entry in their ledger
- Report ledger balance mismatch between Console and Kite funds page
- Need to trace a specific charge, obligation, settlement, or margin entry
- Report balance changing overnight or between sessions
- Ask about "With Margin" vs "Without Margin" ledger views
- Ask about DP charges, pledge charges, interest debits, or settlement entries in ledger
- Report net balance showing Dr (debit) and not understanding why
- Need ledger statement for a specific date range (for CA/auditor/tax purposes)
- Ask about MTF-related ledger entries (net settlement, initial margin, MTM obligation)
- Ask about verifying recent deposits, trade settlements, transaction history, or balance changes
- Ask why their account balance or fund balance is negative
- Report a negative number showing in their funds or balance

TRIGGER KEYWORDS: "withdrawal failed", "partial amount", "can't withdraw", "zero balance", "sold stocks", "funds not received", "same day", "added money", "where is my money", "balance not updating", "withdrawal rejected", "withdrawable balance", "quarterly settlement", "settlement date", "payout", "LIQUIDCASE", "opt out settlement", "monthly settlement", "ledger", "fund statement", "ledger balance", "opening balance", "closing balance", "debit entry", "credit entry", "net balance", "Dr balance", "Cr balance", "margin blocked", "obligation", "settlement entry", "DP charges", "interest debit", "ledger calculation", "negative balance", "balance is negative", "showing negative", "minus balance", "negative amount", "why is it minus", "fund showing negative"

TAGS: funds, charges, reports

## Protocol

# LEDGER REPORT PROTOCOL

---

## Section A: Reference Data

### A1 — Ledger Fundamentals

- Two views: **"Without Margin"** (only cash movements = actual cash balance) and **"With Margin"** (cash adjusted for margin blocks, includes margin blocked/reversed entries for F&O).
- `net_balance` suffix: **Cr** = credit (client has funds), **Dr** = debit (client owes). Cr does not mean crores.
- Opening balance of day N = closing balance of day N−1. Differences arise only from late-posted entries (charges, interest, settlement adjustments).
- Single ledger system: equity and commodity share the same ledger — no separate commodity funds needed.

---

### A2 — T+1 Settlement Rule

- Same-day deposits and unsettled trade proceeds block withdrawals until the next settlement working day.
- Settlement entries: net obligation credited/debited per settlement cycle — combines buy/sell obligations for that trading day.
- Each trading day settles under a distinct settlement number, posted the next settlement working day (T+1). Trades from different trading days always have different settlement numbers.
- "Next trading day" and "next settlement working day" are usually the same but differ on settlement holidays. A settlement holiday is a day when exchanges are open for trading but clearing and settlement operations are closed (no payin/payout of stocks and funds). When settlement holidays exist, T+1 refers to the next settlement working day, not the next trading day.
- Impact of settlement holidays: Trade proceeds from the trading day immediately before a settlement holiday (and from the settlement holiday itself, if trading occurred) are not settled until the next settlement working day.

---

### A3 — Voucher Type Translations

| Voucher Type + Remark Pattern | Meaning |
|---|---|
| "Bank Receipts" | Funds added via bank (blocks same-day withdrawal) |
| "Book Voucher" + "Net settlement for equity" | Equity settlement (T+1) |
| "Book Voucher" + "Net obligation of equity F&O" | F&O settlement (T+1) |
| "Book Voucher" + "Net obligation for MCX commodity FNO" | Commodity settlement (T+1) |
| "Book Voucher" + "Net obligation for CDS FNO" | Currency settlement (T+1) |
| "Bank Payments" + "quarterly settlement" | Quarterly settlement payout |
| "Bank Payments" | Withdrawals processed |
| "Journal Entry" | Charges (DP, pledge, interest, penalties, AMC, modification charges etc.) — not brokerage related |
| "Journal Entry" + "Interest for MTF funded value on [date]" | MTF interest charge for funded amount on that date |
| "Delivery Voucher" | Margin blocked/reversed entries |
| "MTF Delivery Voucher" | MTF margin/settlement entries |

---

### A4 — Quarterly Settlement (QS) Facts

- Mandatory per SEBI regulations — cannot opt out or change frequency.
- Schedule: first Friday of January, April, July, and October.
- Applies to the entire free cash balance regardless of investment type (including LIQUIDCASE).
- LIQUIDCASE units are not redeemed as part of QS — only uninvested free cash is settled.
- Account opened after previous settlement date → first payout at next quarter's settlement date.
- Inactive accounts (no trading 30+ days) may settle monthly instead of quarterly. Reverts to quarterly once trading resumes.
- Frequency is set at account opening and cannot be changed.

---

### A5 — Common Charges Entries in Ledger (not brokerage charges)

| Charge Type | Ledger Remark Pattern | Amount | Notes |
|---|---|---|---|
| DP charges (Male primary holder) | "DP Charges for Sale of [STOCK]" | **₹15.34** = ₹9.50 Zerodha + ₹3.50 CDSL + 18% GST | Per scrip per transaction whenever stock is debited from demat — applies to regular sale, SLB lending, and MTF unpledge sales |
| DP charges (Female primary holder) | "DP Charges for Sale of [STOCK]" | **₹15.045** = ₹9.50 Zerodha + ₹3.25 CDSL + 18% GST | Same as above — CDSL gives a reduced depository charge when the primary demat holder is female |
| Pledge / unpledge charges | "Being pledge charges for [STOCK]" (non-MTF) or "MTF pledge charges for [STOCK]" / "MTF unpledge charges for [STOCK]" | **₹35.40** = ₹30 + 18% GST per scrip per action | Pledging or unpledging a stock (for collateral margin or MTF). Each pledge and each unpledge is charged separately |
| AMC for Demat Account | "AMC for Demat Account for [period]" | ₹88.50 quarterly (standard) or ₹29.50 for small/BSDA-eligible accounts | Demat account maintenance, billed quarterly |
| Account opening fee | "Account opening fee" | **₹500** | One-time, typically for Non-individual, Corporate, or NRI accounts. Resident individual accounts are usually opened for free |
| DDPI activation charge | "Charges for enabling DDPI" | **₹118** = ₹100 + 18% GST | One-time, when DDPI is enabled on the account |
| Modification Charges | Remark reflects the specific modification type (e.g., "Bank Modification Charges", "Address Modification Charges") | **₹29.50** | Any account-detail modification — bank account change, address change, or other KYC/profile modifications. The ledger remark will reflect the actual modification type |
| Payment gateway charges | "Being payment gateway charges debited for [CLIENT_ID]" | **₹10.62** = ₹9 + 18% GST | Each time funds are added via Payment Gateway (Netbanking). UPI deposits do NOT attract this charge |
| Call and Trade / Auto Square-Off | "Call and Trade charges(Auto Square Off) for [date]" or "Call and Trade charges for [date]" | **₹59** = ₹50 + 18% GST per order | Orders placed via phone, or RMS auto-square-off triggered by margin shortfall or end-of-day intraday close |
| Delayed Payment Charges (DPC) | "Delayed payment charges for [month] - [year]" | Variable — interest on debit balance | Monthly, posted early in the following month. Invoke `delayed_payment_charges` for day-wise breakdown |

---

### A6 — Margin Entries (With Margin view only)

- Span/Exposure/Delivery margin blocked — reversed next day and re-blocked at new levels.
- `cost_center` identifies segment: NSE-EQ = equity, NSE-F&O = F&O, MCX-F&O = commodity. Internal use only — see A7.

---

### A7 — Field Rules

**Shareable with client:**

| Field | Interpretation |
|---|---|
| `posting_date` | Date the entry was posted to the ledger |
| `debit` | Debit amount |
| `credit` | Credit amount |
| `net_balance` | Running balance after the entry — Cr (credit) or Dr (debit) per A1 |
| `remarks` | Translate per A3 / A5 / A9 before sharing |
| `settlement_number` | Settlement cycle identifier — distinct per trading day per A2 |

**Non-shareable:**

| Field | Interpretation |
|---|---|
| `cost_center` | Segment identifier (NSE-EQ, NSE-F&O, MCX-F&O) — use for internal segment reasoning per A6 |
| `account` | Internal account reference |
| `voucher_type` | Internal voucher type — translate via A3 before communicating |
| `voucher_no` | Internal voucher number |
| `client_id` | Internal client identifier |

---

### A8 — Withdrawal Balance Calculation

| Scenario | Formula | Condition |
|---|---|---|
| No collateral | Closing balance − same-day payin − credits from unsettled trades | Always applies |
| Equity collateral only | Closing balance + 50% of margin blocked from equity collateral − same-day payin − unsettled credits | Only when position is closed and equity collateral is not actively being used as margin |
| Liquid collateral only | Closing balance + margin blocked from liquid collateral − same-day payin − unsettled credits | Only when position is closed and liquid collateral is not actively being used as margin |
| Both collateral types | Closing balance + 50% equity collateral margin + liquid collateral margin − same-day payin − unsettled credits | Only when position is closed and neither collateral type is actively being used as margin |

---

### A9 — MTF Entry Types

| Entry Remark Pattern | Voucher Type | Meaning |
|---|---|---|
| "MTM obligation blocked/reversed for MTF" | Delivery Voucher / MTF Delivery Voucher | Daily mark-to-market adjustments on MTF positions |
| "Initial margin charged for MTF" | Delivery Voucher / MTF Delivery Voucher | Margin blocked when shares purchased under MTF |
| "Net settlement for Equity" | Book Voucher | Settlement of MTF buy/sell obligations |
| "Interest for MTF funded value on [date]" | Journal Entry | Daily MTF interest charge — debited for the funded amount outstanding on the specified date. Interest rate: 0.04% per day (₹40 per lakh). Accrues on all calendar days including weekends and holidays. |

MTF Interest Statement available at Console → Reports → MTF Interest Statement for per-day funded amount breakdown.

---

### A10 — Common Bank Rejection Reasons

| Reason | Suggestion |
|---|---|
| Incorrect or outdated bank account details | Verify and update bank details on Console under Profile → Bank Details |
| Bank account frozen or inactive | Contact the bank to resolve the account status |
| Bank-side technical issue or downtime | Wait and retry; if persistent, contact the bank |
| Name mismatch between Zerodha and bank records | Ensure the registered name matches across both accounts |

---

### A11 — Withdrawal Eligibility: FIFO Settlement Logic

Withdrawal processing uses settled funds only. Unsettled credits posted on T day (settling T+1) cannot be used for withdrawal on the same day they appear.

**Settled vs unsettled — fund sources:**

| Fund Source | Status on Posting Day (T) | Available for Withdrawal |
|---|---|---|
| Opening balance (prior day's closing balance) | Settled | Immediately |
| Same-day payin (Bank Receipts on T day) | Unsettled | T+1 working day |
| Equity net settlement credit (Book Voucher on T day) | Unsettled | T+1 working day |
| FNO net obligation credit (Book Voucher on T day) | Unsettled | T+1 working day |
| MTF settlement / obligation credit (Book Voucher or MTF Delivery Voucher on T day) | Unsettled | T+1 working day |
| MCX / CDS obligation credit (Book Voucher on T day) | Unsettled | T+1 working day |

- **FIFO principle:** Unsettled debits posted on T day (equity / FNO / MTF obligation debits) consume the settled opening balance first — not the unsettled credits posted the same day.

| Balance Type | Formula |
|---|---|
| Net account balance (visible in ledger) | Opening settled (A) + unsettled credits (B) − unsettled debits (D) |
| Withdrawal-eligible balance | Opening settled (A) − unsettled debits (D) |

**Outcomes:**
- Withdrawal-eligible < withdrawal requested → partial processing; only the eligible amount is released.
- Withdrawal-eligible ≤ 0 → withdrawal fails, even when net account balance is positive.

T+1 refers to the next settlement working day per the settlement calendar.

---

## Section B: Decision Flow

### Routing

```
Route by scenario
├─ Ledger view (With Margin / Without Margin) → Rule 1
├─ Dr / Cr / negative balance interpretation → Rule 2
├─ Specific ledger entry inquiry → Rule 3
├─ Withdrawal issue
│  ├─ Bank reference number / UTR provided → Rule 4
│  ├─ Withdrawal failed or processed as ₹0 despite positive net balance → Rule 14
│  ├─ Withdrawal partially processed (amount less than requested) → Rule 5
│  └─ Zero / low withdrawable balance despite ledger funds → Rule 6
├─ Stock sale proceeds not visible or not withdrawable → Rule 7
├─ Quarterly Settlement (QS) — any query → Rule 8
├─ Balance mismatch
│  ├─ Opening vs closing mismatch → Rule 9
│  └─ Ledger vs Kite funds page mismatch → Rule 10
├─ MTF-related entries
│  ├─ MTF interest charges (total, date range, or specific date) → Rule 12
│  └─ Other MTF entries (MTM, margin, settlement) → Rule 11
└─ No matching rule / unexplained entry / data discrepancy → Rule 13
```

### Fallback

-If no root cause is identified after checking all relevant rules → escalate to human agent.

---

## Section C: Rules

### Rule 1 — With Margin vs Without Margin Explanation

1. Communicate:
   - "Without Margin" view shows the actual cash balance — deposits, withdrawals, trade settlements, charges.
   - "With Margin" view additionally shows margin blocked and reversed for F&O positions.
   - For actual cash balance, use "Without Margin". For margin utilisation, use "With Margin".

---

### Rule 2 — Dr vs Cr Balance Explanation

1. Reference A1 for Dr/Cr definitions — Cr = credit (client has funds), Dr = debit (client owes).
2. Present the actual `net_balance` value and its Dr/Cr status.
3. If Dr balance: flag that interest may be charged on debit balances.

---

### Rule 3 — Standard Transaction Inquiry

**Translate and present:**
- Translate `voucher_type` using A3.
- If debit > 0: present the date, debit amount, translated remarks, and balance after.
- If credit > 0: present the date, credit amount, translated remarks, and balance after.

**Trade breakdown for settlement entries:**

-When the entry is a settlement or net obligation (`voucher_type` = "Book Voucher" with settlement/obligation remarks per A3):

1. Invoke `kite_order_history` for the trading date. The trading date is the same as the posting date on the ledger (settlement entries are posted on T day itself between 7–9 PM).
2. For each order in the order history:
   - **Status = "COMPLETE":** Trade value = filled quantity × average price. Buy = debit; sell = credit to net obligation.
   - **Status = "CANCELLED":** If filled quantity > 0, partially executed — trade value = filled quantity × average price. If filled quantity = 0, fully cancelled — does not contribute to settlement.
   - Other statuses (REJECTED, etc.): Do not contribute to settlement.
3. Present each executed/partially executed trade: stock name, transaction type, filled quantity, average price, and trade value.
4. Confirm sum of trade values (net of buys and sells) aligns with the settlement debit/credit. Minor differences may exist due to charges included in the net obligation.

**Cross-references for specific entry types:**
- DPC / interest entries → invoke `delayed_payment_charges` for day-wise breakdown
- Pledge / unpledge entries → invoke `pledge_request_report`
- Trade charge breakdowns → invoke `contract_note_charges`
- MTF interest entries → Rule 12

---

### Rule 4 — Withdrawal Status Lookup by Reference Number

1. When client quotes a bank reference number or UTR, Invoke `withdrawal_report` to look up that specific transaction.
2. Identify the transaction status: processed, rejected, or pending.
3. If rejected: funds are credited back to the Zerodha trading account — check ledger for the corresponding credit entry. Check if a subsequent withdrawal was placed after the rejection.
4. If processed: if not received by client's bank within 24 hours of the processing date, advise client to follow up with their bank.
5. If pending: share current status and expected processing timeline.
6. Present last 3–5 payout entries in chronological order for context.
7. If rejected due to bank-side issue: reference A10 for common rejection reasons; advise verifying bank details on Console (Profile → Bank Details).

---

### Rule 5 — Partial Withdrawal: FIFO Settlement

1. From `ledger_report` for the withdrawal date (T), identify:
   - Opening settled balance: prior day's closing balance.
   - All unsettled credits posted on T day per A11: same-day payin (Bank Receipts), equity settlement credit, FNO obligation credit, MTF settlement/obligation credit, MCX/CDS credit.
2. Confirm: opening settled balance ≈ processed amount. Minor differences are expected due to taxes and charges applied on that day.
3. Identify which unsettled fund sources per A11 make up the unprocessed portion (requested − processed).
4. Identify the next settlement working day from the settlement calendar.
5. The settled opening balance was the only eligible amount for release. The unprocessed portion consists of unsettled credits from the identified sources — these become withdrawable on the next settlement working day.
6. If T+1 has already passed, confirm whether funds are now available or check if a subsequent withdrawal request already exists.

---

### Rule 6 — Zero / Low Withdrawable Balance

Check for same-day "Bank Receipts" or recent "Book Voucher" settlement entries:

**6a — Same-day deposit found:**
`voucher_type` = "Bank Receipts" on the same posting date — funds added on the same day are subject to T+1 per A2 and not available for withdrawal until the next settlement working day.

**6b — Unsettled trades found:**
"Book Voucher" settlement credits on or near the query date are subject to T+1 per A2 — withdrawable balance updates the next settlement working day morning.

**6c — Collateral involved:**
Apply the applicable formula from A8. Formulas apply only when the position is closed and the collateral is not actively being used as margin.

---

### Rule 7 — Stock Sale Proceeds Not Visible or Not Withdrawable

**Key distinction:** For normal sales (existing demat holdings), proceeds are visible in `kite_margins` immediately after the sale but not withdrawable until T+1. For BTST sales (shares bought on T−1, sold on T), proceeds are not visible in `kite_margins` at all on the sale date — they appear only on the next trading day.

**BTST check:**
1. Invoke `kite_order_history` for the sale date to identify the sell order.
2. Invoke `kite_order_history` for the previous trading day (T−1) to check if the same stock was purchased.
3. If purchased on T−1 and sold on T (BTST): proceeds will not show in `kite_margins` on the sale date — this is expected. Proceeds appear the next trading day. Ledger settlement is unchanged — T+1 applies as normal per A2.
4. If not purchased on T−1 (existing holding from demat): proceeds are already visible in `kite_margins`. The concern is about withdrawal — T+1 settlement applies per A2.

---

### Rule 8 — Quarterly Settlement

1. Check ledger for "Bank Payments" + "quarterly settlement" entry per A3.
2. If QS entry found: present date, amount, and balance after. Reference A4 for schedule and regulatory context.
3. If no QS entry found:
   - Check account opening date against the previous settlement date per A4 — if opened after, first payout is at the next quarter's settlement date.
   - Check if account has been inactive (no trading for 30+ days) per A4 — monthly settlement may be in effect; reverts to quarterly once trading resumes.
4. If client asks to opt out or change frequency: not possible per A4 — mandatory SEBI regulation, frequency set at account opening.
5. If client asks about LIQUIDCASE and QS: LIQUIDCASE units are not redeemed as part of QS — only uninvested free cash is settled per A4.
6. For detailed breakdown of funds released/retained: Invoke `client_retention_dates`.

---

### Rule 9 — Opening vs Closing Balance Mismatch

1. Opening balance of day N = closing balance of day N−1 per A1. If mismatch, check for late-posted entries between the two dates (charges, interest, settlement adjustments).
2. If still unexplained → escalate to human agent.

---

### Rule 10 — Ledger vs Kite Funds Page Mismatch

1. Invoke `kite_margins` to fetch current Kite funds data.
2. Compare ledger closing balance against "Available Cash" from `kite_margins`. The ledger closing balance corresponds to "Available Cash" on Kite, not "Available Margin" (which includes collateral).
3. If they differ: check if a settlement holiday falls between the trade date and current date per A2. On a settlement holiday, the ledger shows the sale credit (posted on T day, 7–9 PM) but Kite only reflects settled funds — the mismatch equals the unsettled proceeds and resolves on the next settlement working day.
4. If still unexplained after ruling out settlement holidays and pending entries → escalate to human agent.

---

### Rule 11 — MTF Ledger Entries (Non-Interest)

1. Explain relevant MTF entries using A9.
2. For MTF interest queries, apply Rule 12. Invoke `console_mtf_holdings` if needed.
3. If client raises any calculation dispute related to MTF MTM amounts or claims funds were credited less than expected for MTF trades → escalate to human agent immediately. Do not attempt to calculate or verify MTF MTM manually.

---

### Rule 12 — MTF Interest Charges

1. From the ledger, filter entries per A9 where `voucher_type` = "Journal Entry" AND `remarks` contains "Interest for MTF funded value". Each matching entry represents one day's interest charge. The date in the remark (e.g., "Interest for MTF funded value on 2026-01-20") is the accrual date — `posting_date` may differ by 1–2 days due to processing.
2. Specific date query: locate the entry where the remark contains that date and present the debit amount and posting date.
3. Multi-day / range query: sum all matching debit entries within the period and present the total with entry count.
4. No entries found: either no MTF positions were held during the period or entries have not yet been posted.
5. If client disputes the interest amount → escalate to human agent with client ID, date range, and total interest charged.

---

### Rule 13 — Escalation

Escalate to human agent when any of the following occur:
- Ledger closing balance doesn't match Console/Kite after verifying all entries (Rules 9, 10).
- An entry appears in the ledger that cannot be explained by any rule.
- Charges debited without a corresponding trade or event.
- MTF interest dispute unresolved after client reviews MTF Interest Statement (per Rule 12).

When escalating, include: client ID, date range, and a summary of the context and findings so far.

---

### Rule 14 — Withdrawal Failed: Settled Funds Exhausted by Unsettled Debits

1. From `ledger_report` for the withdrawal date (T), identify:
   - Opening settled balance = A (prior day's closing balance).
   - Total unsettled credits on T day = B: sum of same-day payin, equity / FNO / MTF / MCX / CDS settlement credits per A11.
   - Total unsettled debits on T day = D: sum of equity / FNO / MTF / MCX / CDS obligation debits per A11.
2. Compute:
   - Net account balance = A + B − D (what the client sees in the ledger — likely positive).
   - Withdrawal-eligible = A − D (FIFO: debits consume settled funds first per A11).
3. Confirm: if withdrawal-eligible ≤ 0, this is the cause of the failed withdrawal.
4. Identify the next settlement working day from the settlement calendar.
5. The net account balance (A + B − D) is visible but unsettled credits (B) cannot offset obligation debits (D) under FIFO — withdrawal-eligible = A − D. The full balance becomes withdrawable on the next settlement working day; client should place a new request from that date.
