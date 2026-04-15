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

## Protocol

---

## Section A: Reference Data

### A1 — Ledger Fundamentals

- Ledger = complete financial statement of a client's trading account — every debit and credit.
- Two views: **"Without Margin"** (only cash movements = actual cash balance) and **"With Margin"** (cash adjusted for margin blocks, includes margin blocked/reversed entries for F&O).
- `net_balance` suffix: **Cr** = credit (client has funds), **Dr** = debit (client owes). Cr does not mean crores.
- Opening balance of day N = closing balance of day N−1. Differences arise only from late-posted entries (charges, interest, settlement adjustments).
- Single ledger system: equity and commodity share the same ledger — no separate commodity funds needed.

### A2 — T+1 Settlement Rule

- Same-day deposits and unsettled trade proceeds block withdrawals until the next settlement working day.
- Settlement entries: net obligation credited/debited per settlement cycle — combines buy/sell obligations for that trading day.
- Each trading day settles under a distinct settlement number, posted the next settlement working day (T+1). Trades from different trading days always have different settlement numbers.
- "Next trading day" and "next settlement working day" are usually the same but differ on settlement holidays. A settlement holiday is a day when exchanges are open for trading but clearing and settlement operations are closed (no payin/payout of stocks and funds). When settlement holidays exist, T+1 refers to the next settlement working day, not the next trading day.
- Share settlement numbers with clients only when explicitly asked.
- Ledger entries for trade settlements are posted on the same day between 5–9 PM.
- Withdrawable balance is updated on the next settlement working day morning after settlement processing.
- Clients can place a withdrawal request at any time; withdrawals are processed at standard cutoff times.

### A3 — Voucher Type Translations

| Voucher Type + Remark Pattern | Client-Facing Meaning |
|---|---|
| "Bank Receipts" | Funds added via bank (blocks same-day withdrawal) |
| "Book Voucher" + "Net settlement for equity" | Equity settlement (T+1) |
| "Book Voucher" + "Net obligation of equity F&O" | F&O settlement (T+1) |
| "Book Voucher" + "Net obligation for MCX commodity FNO" | Commodity settlement (T+1) |
| "Book Voucher" + "Net obligation for CDS FNO" | Currency settlement (T+1) |
| "Bank Payments" + "quarterly settlement" | Quarterly settlement payout |
| "Bank Payments" | Withdrawals processed |
| "Journal Entry" | Charges (DP, pledge, interest, penalties) |
| "Journal Entry" + "Interest for MTF funded value on [date]" | MTF interest charge for funded amount on that date |
| "Delivery Voucher" | Margin blocked/reversed entries |
| "MTF Delivery Voucher" | MTF margin/settlement entries |

### A4 — Quarterly Settlement (QS) Facts

- Mandatory per SEBI regulations — cannot opt out or change frequency.
- Schedule: first Friday of January, April, July, and October.
- Applies to the entire free cash balance regardless of investment type (including LIQUIDCASE).
- LIQUIDCASE units are not redeemed as part of QS — only uninvested free cash is settled.
- Account opened after previous settlement date → first payout at next quarter's settlement date.
- Inactive accounts (no trading 30+ days) may settle monthly instead of quarterly. Reverts to quarterly once trading resumes.
- Frequency is set at account opening and cannot be changed.

### A5 — Common Ledger Entries

- DP charges: ₹15.34 per sell transaction.
- Other common entries: pledge/unpledge charges, interest debits, QS payout, net settlement, obligation.

### A6 — Margin Entries (With Margin view only)

- Span/Exposure/Delivery margin blocked — reversed next day and re-blocked at new levels.
- `cost_center` identifies segment: NSE-EQ = equity, NSE-F&O = F&O, MCX-F&O = commodity. Use for internal reasoning only (see **A7**).

### A7 — Field Rules

**Shareable with client:** `posting_date`, `debit`, `credit`, `net_balance`, `remarks` (sanitized only per **A8**).

**Internal reasoning only (never share with client):** `cost_center`, `account`, `voucher_type`, `voucher_no`, `client_id`.

### A8 — Remarks Sanitization Rules

Remove from remarks before sharing:
- "with reference number" + everything after it
- "reference number:" + any following alphanumeric string
- "ref no" + any following alphanumeric string
- Standalone alphanumeric codes (e.g., `88a8eb2b6400fa4c`)

Raw bank reference numbers and internal reference codes are never shared with clients.

### A9 — Withdrawal Balance Calculation

| Scenario | Formula |
|---|---|
| No collateral | Closing balance − same-day payin − credits from unsettled trades |
| Equity collateral only | Closing balance + 50% of margin blocked from equity collateral − same-day payin − unsettled credits |
| Liquid collateral only | Closing balance + margin blocked from liquid collateral − same-day payin − unsettled credits |
| Both collateral types | Closing balance + 50% equity collateral margin + liquid collateral margin − same-day payin − unsettled credits |

### A10 — Formatting Rules

- Amounts: ₹ symbol with Indian comma notation (e.g., ₹1,23,456.78).
- Dates: DD MMM YYYY (e.g., 19 Mar 2026).
- If `debit` = 0, share only the credit amount. If `credit` = 0, share only the debit amount.

### A11 — Cross-Reference Protocols

| Topic | Refer to |
|---|---|
| Interest / DPC calculation and daily breakdown | Delayed Payment Charges protocol |
| QS details — funds released, retained, obligations | Client Retention Dates protocol |
| Pledge/unpledge charge entries on ledger | Pledge Request Report protocol |
| Trade charge breakdowns referenced in ledger | Contract Note Charges protocol |
| MTF interest rate, per-stock funded amount, interest statement | Console MTF Holdings protocol |
| SGB interest payment dates and credit details | Not in ledger — SGB interest is credited directly to the client's bank account by RBI. Refer client to the SGB support article for interest payment dates and details. |

### A12 — MTF Entry Types

| Entry Remark Pattern | Voucher Type | Meaning |
|---|---|---|
| "MTM obligation blocked/reversed for MTF" | Delivery Voucher / MTF Delivery Voucher | Daily mark-to-market adjustments on MTF positions |
| "Initial margin charged for MTF" | Delivery Voucher / MTF Delivery Voucher | Margin blocked when shares purchased under MTF |
| "Net settlement for Equity" | Book Voucher | Settlement of MTF buy/sell obligations |
| "Interest for MTF funded value on [date]" | Journal Entry | Daily MTF interest charge — debited for the funded amount outstanding on the specified date. Interest rate: 0.04% per day (₹40 per lakh). Accrues on all calendar days including weekends and holidays. |

**MTF interest identification rule:** Filter ledger entries where `voucher_type` = "Journal Entry" AND `remarks` contains "Interest for MTF funded value". Each matching entry represents one day's interest charge. The date mentioned in the remark (e.g., "on 2026-01-20") is the date the interest accrued — the `posting_date` may differ by 1–2 days due to processing.

For the detailed MTF interest statement (with per-day breakdown and funded amount details), refer client to Console → Reports → MTF Interest Statement.

### A13 — Common Bank Rejection Reasons

| Reason | Suggestion |
|---|---|
| Incorrect or outdated bank account details | Verify and update bank details on Console under Profile → Bank Details |
| Bank account frozen or inactive | Contact the bank to resolve the account status |
| Bank-side technical issue or downtime | Wait and retry; if persistent, contact the bank |
| Name mismatch between Zerodha and bank records | Ensure the registered name matches across both accounts |

### A14 — Settlement Holidays

- A settlement holiday is a day when stock exchanges are open for trading but clearing and settlement operations are closed (no payin/payout of stocks and funds).
- Common examples: Annual Bank closing (typically 1st April), certain bank holidays where exchanges remain open.
- Impact: Trade proceeds from the trading day immediately before a settlement holiday (and from the settlement holiday itself, if trading occurred) are not settled until the next settlement working day.
- Detection: If a withdrawal was rejected and the rejection date or the expected T+1 date falls on a settlement holiday, apply Rule 19.
- The settlement calendar determines settlement working days — do not assume T+1 always equals the next trading day.

---

## Section B: Decision Flow

### Preflight (run on every query)

1. Fetch the client's ledger data for the relevant date range.
2. Identify the ledger view in context ("With Margin" or "Without Margin").
3. Apply field protection (**A7**) and sanitization (**A8**) to all data before any client-facing output.
4. Format all amounts and dates per **A10**.
5. Translate all `voucher_type` values using **A3** for client communication.

### Routing Tree

```
Query relates to ledger →
│
├─ Query is about SGB interest payments or SGB interest credit dates
│  → Out of scope. SGB interest is not recorded in the ledger (per A11). Refer client to the SGB support article.
│
├─ Client confused about ledger views / which to use
│  → Rule 1
│
├─ Client confused about Dr / Cr / negative balance
│  → Rule 2
│
├─ Client asks about a specific ledger entry
│  → Rule 3
│
├─ Withdrawal issue
│  ├─ Failed, same-day "Bank Receipts" found
│  │  → Rule 4
│  ├─ Customer quotes a bank reference number / UTR for a withdrawal
│  │  → Rule 4b
│  ├─ Failed, unsettled "Book Voucher" settlement found
│  │  → Rule 5
│  ├─ Failed or delayed, settlement holiday involved
│  │  → Rule 19
│  ├─ Partially processed, same-day deposit or unsettled trades
│  │  → Rule 6
│  └─ Zero/low withdrawable balance despite ledger funds
│     ├─ Same-day deposit → Rule 7a
│     ├─ Unsettled trades → Rule 7b
│     └─ Collateral involved → Rule 7c
│
├─ Stock sale proceeds not visible or not withdrawable
│  → Rule 8
│
├─ Quarterly Settlement (QS)
│  ├─ Explanation of QS entry → Rule 9
│  ├─ No QS payout (new account) → Rule 10
│  ├─ Monthly instead of quarterly → Rule 11
│  ├─ Opt out / change frequency → Rule 12
│  └─ LIQUIDCASE and QS → Rule 13
│
├─ Balance mismatch
│  ├─ Opening vs closing mismatch → Rule 14
│  └─ Ledger vs Kite funds page mismatch → Rule 15
│
├─ MTF-related entries
│  ├─ MTF interest charges (total, date range, or specific date)
│  │  → Rule 16a
│  └─ Other MTF entries (MTM, margin, settlement)
│     → Rule 16
│
├─ Multiple transactions in query
│  → Rule 17
│
├─ Client reports multiple independent issues (e.g., payin failure + negative balance)
│  → Address each issue separately using the applicable rule/protocol.
│     Negative/debit balance → Rule 2 or Rule 3 (identify cause from ledger).
│     Payin failure → Payin protocol.
│
└─ No matching rule / unexplained entry / data discrepancy
   → Rule 18 (Escalation)
```

### Scope

- Address: ledger entries, balances, withdrawal eligibility, QS, and mismatches within ledger context.
- SGB interest payment queries are outside ledger scope — SGB interest is credited directly to the client's bank account by RBI and does not appear in the Zerodha ledger. Refer to the SGB support article (per **A11**).
- For detailed charge breakdowns, refer to **A11** cross-reference protocols. For MTF MTM disputes, escalate per Rule 16.

### Fallback

If no root cause is identified after checking all relevant rules → escalate per Rule 18.

---

## Section C: Rules

### Rule 1 — With Margin vs Without Margin Explanation

1. Respond: "The ledger has two views:
   - 'Without Margin' shows your actual cash balance — money in and money out (deposits, withdrawals, trade settlements, charges).
   - 'With Margin' additionally shows margin blocked and reversed for your F&O positions. This helps understand how much margin is being used.

   For your actual cash balance, refer to 'Without Margin'. For understanding margin utilization, use 'With Margin'."

### Rule 2 — Dr vs Cr Balance Explanation

1. Respond: "In your ledger, 'Cr' means credit balance — you have funds available. 'Dr' means debit balance — your account has a shortfall. Note: 'Cr' does not mean crores."
2. Personalize: "Your current balance of ₹[net_balance] [Dr/Cr] means [you have ₹X available / your account has a shortfall of ₹X]."
3. If Dr balance, add: "A debit balance may result from charges, obligations, or margin shortfalls. Interest may be charged on debit balances."

### Rule 3 — Standard Transaction Inquiry

1. Sanitize remarks per **A8**. Translate voucher type using **A3**.
2. If debit > 0: "On [date], ₹[debit] was debited for [sanitized remarks]. Balance after: ₹[net_balance]."
3. If credit > 0: "On [date], ₹[credit] was credited for [sanitized remarks]. Balance after: ₹[net_balance]."

**Step 4 — Trade breakdown for settlement entries:**
When the entry is a settlement or net obligation (voucher_type = "Book Voucher" with settlement/obligation remarks per **A3**), identify and name the underlying trades that make up the net obligation:

1. A settlement entry posted on a given date corresponds to trades executed on that same date. Fetch `kite_order_history` for the posting date of the settlement entry to identify the underlying trades. Do not assume the trades were placed on a prior date — the posting date is the trade date.
2. For each order in the order history:
   - **Status = "COMPLETE":** The order was fully executed. Trade value = filled quantity × average price. Buy orders contribute a debit; sell orders contribute a credit to the net obligation.
   - **Status = "CANCELLED":** Check the filled quantity. If filled quantity > 0, the order was partially executed before cancellation. Trade value = filled quantity × average price (debit for buy, credit for sell). If filled quantity = 0, the order was fully cancelled and does not contribute to the settlement.
   - Other statuses (REJECTED, etc.): Do not contribute to the settlement.
3. Present the breakdown: "This settlement entry includes the following trades from [posting date]:" followed by each executed/partially executed trade with stock name, transaction type (buy/sell), filled quantity, average price, and trade value.
4. Confirm that the sum of individual trade values (net of buys and sells) aligns with the settlement debit/credit amount. Minor differences may exist due to charges (brokerage, STT, etc.) included in the net obligation.

### Rule 4 — Withdrawal Failed: Same-Day Funds

1. Confirm: voucher_type = "Bank Receipts" on the same posting_date as the failed withdrawal.
2. Respond: "Your withdrawal could not be processed because funds added on the same day cannot be withdrawn due to the T+1 settlement rule (per **A2**). On [date], ₹[credit] was added to your account. These funds will be available for withdrawal from the next settlement working day."

### Rule 4b — Withdrawal Status Lookup by Reference Number

1. When the customer quotes a bank reference number or UTR for a withdrawal they say was not credited, check the withdrawal/payout report for that specific transaction.
2. Identify the transaction status: processed, rejected, or pending.
3. **If rejected:** Explain that rejected withdrawal funds are credited back to the Zerodha trading account. Check the ledger for the corresponding credit entry and confirm it. Then check if a subsequent withdrawal request was placed after the rejection — if so, share its status too.
4. **If processed:** Share the processing date and suggest the client check with their bank if the credit has not appeared within 24 hours of processing.
5. **If pending:** Share the current status and expected processing timeline.
6. Provide a brief chronological summary of the last 3–5 payout entries so the customer has full context on recent withdrawal activity.
7. If the withdrawal was rejected due to a bank-side issue, share common rejection reasons from **A13** and suggest verifying bank details on Console (Profile → Bank Details).

### Rule 5 — Withdrawal Failed: Unsettled Trade

1. Locate a "Book Voucher" with settlement remarks near the withdrawal date. Identify trade type from **A3**.
2. Respond: "Your withdrawal could not be processed because your [trade type] settlement funds haven't cleared yet. On [date], ₹[credit] was credited from [trade type]. These funds settle on T+1 and the withdrawable balance will be updated by the next settlement working day ([T+1 date]) morning (per **A2**)."

### Rule 6 — Partial Withdrawal

1. Confirm: withdrawal processed but amount less than requested. Identify same-day deposits or unsettled trades.
2. Respond: "Your withdrawal was partially processed because [same-day funds / unsettled trade proceeds] cannot be withdrawn on the same day (T+1 rule). The remaining ₹[difference] will be available for withdrawal from the next settlement working day."

### Rule 7 — Zero/Low Withdrawable Balance

1. Check for same-day "Bank Receipts" or recent "Book Voucher" settlement entries.

   **7a — Same-day deposit found:**
   "Your withdrawable balance is zero because the ₹[credit] added today is subject to the T+1 rule. Available for withdrawal on the next settlement working day."

   **7b — Unsettled trades found:**
   "Your withdrawable balance is low because [trade type] funds from [date] are still settling. The withdrawable balance will be updated by the next settlement working day ([T+1 date]) morning (per **A2**)."

   **7c — Collateral involved:**
   Explain using the applicable formula from **A9**.

### Rule 8 — Stock Sale Proceeds Not Visible or Not Withdrawable

**Key distinction:** For normal sales (existing demat holdings), proceeds are visible in `kite_margins` immediately after the sale — clients can see the funds same day but cannot withdraw until T+1. For BTST sales (shares bought on T−1, sold on T), proceeds are **not visible in `kite_margins` at all on the sale date** — they appear only on the next trading day. The withdrawal rule is the same for both (available from T+1 after settlement processing). Most client queries about missing sale proceeds are BTST scenarios because the funds are completely invisible on the sale date.

**Step 1 — BTST check:** Before concluding that sale proceeds are settling normally, verify the purchase date of the sold shares:

1. Fetch `kite_order_history` for the sale date to identify the sell order (stock name, quantity, trade value).
2. Fetch `kite_order_history` for the previous trading day (T−1) to check if the same stock was purchased.
3. **If the stock was purchased on T−1 (previous trading day) and sold on T (today or the queried date):** This is a BTST (Buy Today, Sell Tomorrow) trade. The purchased shares were still T1 holdings (not yet delivered to the client's demat account) at the time of sale. Unlike a normal sale where proceeds show in `kite_margins` immediately, BTST sale proceeds do not appear in `kite_margins` on the sale date at all. Respond: "The shares of [stock name] were purchased on [T−1 date] and sold on [T date]. Since the purchased shares had not yet settled into your demat account (T1 holdings), this is a BTST trade. For BTST trades, the sale proceeds do not appear in your Kite balance on the day of the sale — this is expected. The proceeds will be visible in your balance and available for withdrawal from the next trading day ([T+1 of sale date]) after settlement processing. Your funds are safe."
4. **If the stock was NOT purchased on T−1** (i.e., it was an existing holding from demat): Proceed with the standard settlement response below.

**Step 2 — Standard settlement response (non-BTST):**
1. Identify trade type from **A3** and the trade date.
2. The sale proceeds are already visible in `kite_margins` on the sale date. The client's concern is about withdrawal.
3. Respond: "Your sale proceeds of ₹[amount] from your [trade type] trade on [date] are reflected in your Kite balance. These funds settle on T+1 (next settlement working day) and will be available for withdrawal from [T+1 date] morning after settlement processing (per **A2**)."

### Rule 9 — Quarterly Settlement Explanation

1. Sanitize remarks per **A8**.
2. Respond: "On [date], ₹[amount] was transferred to your bank account as part of the mandatory quarterly settlement. Your trading balance after the transfer: ₹[net_balance]."
3. Add context from **A4**: "Quarterly settlement happens on the first Friday of January, April, July, and October. This is a regulatory requirement and applies to your entire available balance."

### Rule 10 — No QS Payout (New Account)

1. Confirm: no QS entry found and account was opened after the previous settlement date.
2. Respond: "Your account was opened after the last settlement date. Your first quarterly settlement payout will be on [next settlement date — first Friday of next quarter]."

### Rule 11 — Monthly Instead of Quarterly Settlement

1. Respond: "If there's been no trading activity for 30+ days, the settlement frequency may shift to monthly. Once you resume trading, it will revert to quarterly." (Per **A4**.)

### Rule 12 — Opt Out / Change Settlement Frequency

1. Respond: "Quarterly settlement is mandatory per SEBI regulations. The frequency is set at account opening and cannot be changed or opted out of. This applies to all Zerodha accounts." (Per **A4**.)

### Rule 13 — LIQUIDCASE and Quarterly Settlement

1. Respond: "Investing in LIQUIDCASE (or similar liquid funds) helps avoid your balance sitting idle in the trading account — the funds are invested instead of remaining as free cash. However, quarterly settlement applies to any free cash balance in your account. Your LIQUIDCASE units are NOT redeemed as part of the settlement process — only the uninvested free cash balance is settled." (Per **A4**.)

### Rule 14 — Opening vs Closing Balance Mismatch

1. Respond: "The opening balance for a day equals the previous day's closing balance. If you see a difference, it may be because late entries (such as charges, interest, or settlement adjustments) were posted after the close. Check if any entries were added between the two dates." (Per **A1**.)
2. If balances still don't match after verification → escalate per Rule 18.

### Rule 15 — Ledger vs Kite Funds Page Mismatch

1. Invoke **kite_margins** to fetch the current Kite funds data.
2. Compare ledger closing balance against "Available Cash" from kite_margins.
3. Respond: "The Kite funds page shows real-time available margin including collateral, while the ledger shows the historical cash movement record. The ledger closing balance matches the 'Available Cash' on Kite, not the 'Available Margin' (which includes collateral)."
4. If they still differ: "If the ledger closing balance and Kite 'Available Cash' still differ, it may be due to pending entries not yet reflected. Please check after market hours."

### Rule 16 — MTF Ledger Entries (Non-Interest)

1. Explain the relevant entries using **A12**.
2. Direct client to MTF Interest Statement on Console for detailed MTF interest charges (per **A12**).
3. **Escalate immediately** if the client raises any calculation dispute related to MTF MTM amounts or claims funds were credited less than expected for MTF trades. Do not attempt to calculate or verify MTF MTM manually. (This is genuinely counterintuitive — the model may attempt to help with the math. Always escalate instead.)

### Rule 16a — MTF Interest Charges

**Trigger:** Client asks about MTF interest charged — for a specific date, a date range, a month, a financial year, or a total.

**Steps:**

1. Determine the date range from the client's query:
   - Specific date → fetch ledger for that date ± 2 days (interest posting may lag by 1–2 days).
   - "Last month" → fetch ledger for the previous calendar month.
   - "This FY" / "FY 2025-26" → fetch ledger from 1 Apr to 31 Mar of the relevant FY.
   - No date specified → ask the client for the period they want to check.

2. Filter ledger entries where `voucher_type` = "Journal Entry" AND `remarks` contains "Interest for MTF funded value" (per **A12** identification rule).

3. **If client asks for a specific date's interest:**
   - Locate the entry where the remark contains that date (e.g., "Interest for MTF funded value on 2026-01-20").
   - Respond: "MTF interest of ₹[debit] was charged for [date from remark]. This was debited on [posting_date]."

4. **If client asks for total interest over a date range:**
   - Sum all `debit` amounts from the filtered entries within the date range.
   - Respond: "Your total MTF interest charges from [start date] to [end date] were ₹[total]. This was spread across [count] entries."
   - If the client asks for a breakdown, list each entry: date from remark, debit amount, and posting date. Keep the list concise — group by month if there are more than 15 entries.

5. **If no MTF interest entries are found** for the requested period:
   - Respond: "No MTF interest charges were found in your ledger for the period [start date] to [end date]. This means either you did not hold any MTF positions during this period, or the interest entries have not yet been posted."

6. **Additional context (append when relevant):**
   - "MTF interest is charged at 0.04% per day (₹40 per lakh) on the total funded amount. Interest accrues daily, including weekends and holidays. For a detailed day-wise breakdown with funded amounts, you can also check the MTF Interest Statement on Console (Console → Reports → MTF Interest Statement)."

7. **If the client disputes the interest amount:** Do not attempt to manually verify the per-day calculation. Direct the client to the MTF Interest Statement for the funded amount breakdown. If the client still disputes after reviewing the statement → escalate per Rule 18 with client ID, date range, total interest charged, and the client's expected amount.

### Rule 17 — Multiple Transactions

1. Apply relevant rules (1–16a, 19) to each entry individually.
2. Group entries logically: deposits together, settlements together, charges together.
3. Keep response concise — under 150 words unless the client specifically requests a detailed breakdown.

### Rule 18 — Escalation

Escalate when any of the following occur:
- Ledger closing balance doesn't match Console/Kite after verifying all entries (Rules 14, 15).
- An entry appears in the ledger that the client never initiated and cannot be explained by any rule.
- Charges debited without a corresponding trade or event.
- MTF interest dispute unresolved after client reviews MTF Interest Statement (per Rule 16a).

Include in escalation: client ID, date range, specific mismatched entries, and screenshots if available.

### Rule 19 — Settlement Holiday Impact on Withdrawals

1. Confirm: the withdrawal rejection date or the expected T+1 settlement date falls on a settlement holiday per **A14**.
2. Identify the trade date, the settlement holiday date, and the next settlement working day.
3. Respond: "Your withdrawal request on [rejection date] was rejected because [settlement holiday date] was a settlement holiday ([reason, e.g., Annual Bank closing]). On a settlement holiday, trading is open but clearing and settlement are closed — funds from trades executed on [trade date] are not available for withdrawal until the next settlement working day. Your funds became available for withdrawal on [next settlement working day]."
4. If trades were also executed on the settlement holiday itself, include: "Proceeds from trades on [settlement holiday date] also settle on [next settlement working day]."
5. If the client has already successfully withdrawn after the settlement holiday, confirm the withdrawal details.
