# ledger_report

## Description

WHEN TO USE:

- Withdrawal failed and need to check why (same-day funds, settlement pending, balance issues)
- Partial withdrawal processed and need to explain the difference
- Zero/low withdrawable balance despite having funds (need to check for same-day deposits or unsettled trades)
- Customer sold stocks but can't withdraw or funds not showing (need to check settlement status)
- Quarterly settlement query about payout status, amount, or timing
- Customer asks why they weren't settled in previous quarter or why settlement is monthly instead of quarterly
- Customer asks about opting out of settlement or changing settlement frequency
- Customer asks about specific transaction in their account history
- Customer mentions adding funds and trying to withdraw same day
- Customer asks about LIQUIDCASE or moving funds to prevent settlement
- Client questions ledger balance, opening balance, closing balance, or fund statement
- Client questions a specific debit or credit entry in their ledger
- Client reports ledger balance mismatch between Console and Kite funds page
- Agent needs to trace a specific charge, obligation, settlement, or margin entry
- Client asks why their balance changed overnight or between sessions
- Client questions "With Margin" vs "Without Margin" ledger views
- Client asks about DP charges, pledge charges, interest debits, or settlement entries in ledger
- Client reports net balance showing Dr (debit) and doesn't understand why
- Client needs ledger statement for a specific date range (for CA/auditor/tax purposes)
- Client asks about MTF-related ledger entries (net settlement, initial margin, MTM obligation)
- Any query where you need to verify: recent deposits, trade settlements, transaction history, or balance changes

TRIGGER KEYWORDS: "withdrawal failed", "partial amount", "can't withdraw", "zero balance", "sold stocks", "funds not received", "same day", "added money", "where is my money", "balance not updating", "withdrawal rejected", "withdrawable balance", "quarterly settlement", "settlement date", "payout", "LIQUIDCASE", "opt out settlement", "monthly settlement", "ledger", "fund statement", "ledger balance", "opening balance", "closing balance", "debit entry", "credit entry", "net balance", "Dr balance", "Cr balance", "margin blocked", "obligation", "settlement entry", "DP charges", "interest debit", "ledger calculation"

## Protocol

# LEDGER BALANCE PROTOCOL

<knowledge_base>

<facts>
- Ledger = complete financial statement of client's trading account — every debit and credit
- Two views: "With Margin" (includes margin blocked/reversed entries for F&O) and "Without Margin" (only cash movements)
- "Without Margin" = actual cash balance; "With Margin" = cash adjusted for margin blocks
- net_balance suffix: Cr = credit (client has funds), Dr = debit (client owes). Cr is NOT crores.
- Opening balance of day N = closing balance of day N-1 (may differ if late entries posted)
- T+1 rule: same-day deposits and unsettled trade proceeds block withdrawals until next trading day
- Settlement entries: net obligation credited/debited per settlement cycle — combines buy/sell obligations for that trading day. Each trading day settles under a distinct settlement number posted the next trading day (T+1) — never group trades from different trading days under the same settlement number. Share settlement numbers with clients only when explicitly asked.
- Margin entries (With Margin only): Span/Exposure/Delivery margin blocked — reversed next day and re-blocked at new levels
- cost_center identifies segment: NSE-EQ = equity, NSE-F&O = F&O, MCX-F&O = commodity (internal use only)
- Single ledger system: equity and commodity share same ledger — no separate commodity funds needed
- Common entries: DP charges (₹15.34 per sell), pledge/unpledge charges, interest debits, QS payout, net settlement, obligation
- Quarterly settlement: mandatory, first Friday of Jan/Apr/Jul/Oct — cannot opt out or change
- Inactive accounts (no trading 30+ days) may settle monthly instead of quarterly
- Account opened after previous settlement date: first payout next quarter
- Settlement applies to entire balance regardless of investment type (including LIQUIDCASE)
- Ledger entries for trade settlements are posted on the same day between 5-9 PM
- Withdrawable balance is updated on the next working day morning after settlement processing
- Clients can place a withdrawal request at any time; withdrawals are processed at standard cutoff times
</facts>

<field_usage>
  <share>posting_date | debit | credit | net_balance | remarks (sanitized only)</share>
  <banned>cost_center | account | voucher_type | voucher_no | client_id</banned>
</field_usage>

<voucher_meanings>
"Bank Receipts" = Funds added via bank (blocks same-day withdrawal)
"Book Voucher" + "Net settlement for equity" = Equity settlement (T+1)
"Book Voucher" + "Net obligation of equity F&O" = F&O settlement (T+1)
"Book Voucher" + "Net obligation for MCX commodity FNO" = Commodity settlement (T+1)
"Book Voucher" + "Net obligation for CDS FNO" = Currency settlement (T+1)
"Book Voucher" + "quarterly settlement" = Quarterly settlement payout
"Bank Payments" = Withdrawals processed
"Journal Entry" = Charges (DP, pledge, interest, penalties)
"Delivery Voucher" = Margin blocked/reversed entries
"MTF Delivery Voucher" = MTF margin/settlement entries
</voucher_meanings>

<sanitization>
Remove from remarks before sharing: "with reference number" + everything after | "reference number:" + alphanumeric | "ref no" + alphanumeric | standalone alphanumeric codes (e.g., 88a8eb2b6400fa4c)
NEVER share raw bank reference numbers or internal reference codes.
</sanitization>

<withdrawal_balance_calc>
  <case_1>No collateral → Withdrawal balance = Closing balance − same day payin − credits from unsettled trades</case_1>
  <case_2>Equity collateral only → Closing balance + 50% of margin blocked from equity collateral − same day payin − unsettled credits</case_2>
  <case_3>Liquid collateral only → Closing balance + margin blocked from liquid collateral − same day payin − unsettled credits</case_3>
  <case_4>Both collateral types → Closing balance + 50% equity collateral margin + liquid collateral margin − same day payin − unsettled credits</case_4>
</withdrawal_balance_calc>

<cross_reference>
  <delayed_payment_charges>For interest/DPC calculation details and daily breakdown</delayed_payment_charges>
  <client_retention_dates>For quarterly settlement details — funds released, retained, obligations</client_retention_dates>
  <pledge_request_report>For pledge/unpledge charge entries appearing on ledger</pledge_request_report>
  <contract_note_charges>For trade charge breakdowns referenced in ledger</contract_note_charges>
</cross_reference>

</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection & Sanitization
**NEVER expose:** `cost_center`, `account`, `voucher_type`, `voucher_no`, `client_id`
**ALWAYS:** Sanitize remarks per `<sanitization>` rules before sharing. Translate voucher_type using `<voucher_meanings>` to client-friendly language. Format amounts with ₹ and Indian comma notation. Format dates as DD MMM YYYY.
**if:** debit = 0 → share only credit amount. **if:** credit = 0 → share only debit amount.

### Rule 1: With Margin vs Without Margin
**if:** Client confused about ledger balance or asks which view to use
**then:** "The ledger has two views:
- 'Without Margin' shows your actual cash balance — money in and money out (deposits, withdrawals, trade settlements, charges).
- 'With Margin' additionally shows margin blocked and reversed for your F&O positions. This helps understand how much margin is being used.

For your actual cash balance, refer to 'Without Margin'. For understanding margin utilization, use 'With Margin'."

### Rule 2: Dr vs Cr Balance
**if:** Client confused about Dr/Cr or asks why balance is negative
**then:** "In your ledger, 'Cr' means credit balance — you have funds available. 'Dr' means debit balance — your account has a shortfall. Note: 'Cr' does not mean crores.

Your current balance of ₹[net_balance] [Dr/Cr] means [you have ₹X available / your account has a shortfall of ₹X]."

If Dr balance → "A debit balance may result from charges, obligations, or margin shortfalls. Interest may be charged on debit balances."

### Rule 3: Standard Transaction Inquiry
**if:** Client asks about a specific ledger entry
**then:** Sanitize remarks per Rule 0. Translate voucher_type using `<voucher_meanings>`.
- If debit > 0: "On [date], ₹[debit] was debited for [sanitized remarks]. Balance after: ₹[net_balance]."
- If credit > 0: "On [date], ₹[credit] was credited for [sanitized remarks]. Balance after: ₹[net_balance]."

### Rule 4: Withdrawal Failed — Same-Day Funds
**if:** Withdrawal failed AND voucher_type = "Bank Receipts" on same posting_date
**then:** "Your withdrawal could not be processed because funds added on the same day cannot be withdrawn due to the T+1 settlement rule. On [date], ₹[credit] was added to your account. These funds will be available for withdrawal from the next trading day."

### Rule 5: Withdrawal Failed — Unsettled Trade
**if:** Withdrawal failed AND "Book Voucher" with settlement remarks near withdrawal date
**then:** Identify trade type from `<voucher_meanings>`.
"Your withdrawal could not be processed because your [trade type] settlement funds haven't cleared yet. On [date], ₹[credit] was credited from [trade type]. These funds settle on T+1 and the withdrawable balance will be updated by the next working day ([T+1 date]) morning. You can place a regular withdrawal request anytime, and it will be processed at the standard cutoff times."

### Rule 6: Partial Withdrawal
**if:** Withdrawal processed but less than requested AND same-day deposits or unsettled trades found
**then:** "Your withdrawal was partially processed because [same-day funds / unsettled trade proceeds] cannot be withdrawn on the same day (T+1 rule). The remaining ₹[difference] will be available for withdrawal from the next trading day."

### Rule 7: Zero/Low Withdrawable Balance
**if:** Client has funds in ledger but withdrawable = 0 or very low
**then:** Check for same-day Bank Receipts OR recent Book Voucher settlement entries.
- Same-day deposit → "Your withdrawable balance is zero because the ₹[credit] added today is subject to the T+1 rule. Available for withdrawal tomorrow."
- Unsettled trades → "Your withdrawable balance is low because [trade type] funds from [date] are still settling. The withdrawable balance will be updated by the next working day ([T+1 date]) morning. You can place a regular withdrawal request anytime, and it will be processed at the standard cutoff times."
- If collateral is involved → explain per `<withdrawal_balance_calc>` cases.

### Rule 8: Stock Sale — Funds Not Withdrawable
**if:** Client sold stocks but can't withdraw proceeds
**then:** "Stock sale proceeds settle on T+1 (next working day). Your [trade type] trade from [date] will settle on [T+1 date]. The withdrawable balance will be updated by the next working day morning. You can place a regular withdrawal request anytime, and it will be processed at the standard cutoff times."

### Rule 9: Quarterly Settlement — Explanation
**if:** Remarks contains "quarterly settlement" OR client asks about QS
**then:** Sanitize remarks. "On [date], ₹[amount] was transferred to your bank account as part of the mandatory quarterly settlement. Your trading balance after the transfer: ₹[net_balance].

Quarterly settlement happens on the first Friday of January, April, July, and October. This is a regulatory requirement and applies to your entire available balance."

### Rule 10: QS — No Payout (New Account)
**if:** Client asks why no QS payout AND no settlement entry found AND account opened after previous settlement date
**then:** "Your account was opened after the last settlement date. Your first quarterly settlement payout will be on [next settlement date — first Friday of next quarter]."

### Rule 11: QS — Monthly Instead of Quarterly
**if:** Client asks why settlement is monthly
**then:** "If there's been no trading activity for 30+ days, the settlement frequency may shift to monthly. Once you resume trading, it will revert to quarterly."

### Rule 12: QS — Opt Out / Change Frequency
**if:** Client asks to opt out or change settlement frequency
**then:** "Quarterly settlement is mandatory per SEBI regulations. The frequency is set at account opening and cannot be changed or opted out of. This applies to all Zerodha accounts."

### Rule 13: QS — LIQUIDCASE Query
**if:** Client asks about LIQUIDCASE to avoid settlement
**then:** "Investing in LIQUIDCASE (or similar liquid funds) helps avoid your balance sitting idle in the trading account — the funds are invested instead of remaining as free cash. However, quarterly settlement applies to any free cash balance in your account. Your LIQUIDCASE units are NOT redeemed as part of the settlement process — only the uninvested free cash balance is settled."

### Rule 14: Opening vs Closing Balance Mismatch
**if:** Client reports opening balance differs from previous day's closing
**then:** "The opening balance for a day equals the previous day's closing balance. If you see a difference, it may be because late entries (such as charges, interest, or settlement adjustments) were posted after the close. Check if any entries were added between the two dates."

If after verification the balances still don't match → escalate.

### Rule 15: Ledger vs Kite Funds Page Mismatch
**if:** Client says ledger balance differs from Kite funds page
**then:** "The Kite funds page shows real-time available margin including collateral, while the ledger shows the historical cash movement record. The ledger closing balance matches the 'Available Cash' on Kite, not the 'Available Margin' (which includes collateral).

If the ledger closing balance and Kite 'Available Cash' still differ, it may be due to pending entries not yet reflected. Please check after market hours."

### Rule 16: MTF Ledger Entries
**if:** Client questions MTF-related entries (MTM obligation, net settlement, initial margin)
**then:** "MTF entries in your ledger include:
- 'MTM obligation blocked/reversed for MTF' — daily mark-to-market adjustments on your MTF positions
- 'Initial margin charged for MTF' — margin blocked when you purchased shares under MTF
- 'Net settlement for Equity' — settlement of MTF buy/sell obligations

These are system-generated entries related to your MTF positions. For detailed MTF interest charges, refer to the MTF Interest Statement on Console."

**CRITICAL:** If client raises any calculation dispute related to MTF MTM amounts or claims funds were credited less than expected for MTF trades → escalate immediately. Do not attempt to calculate or verify MTF MTM manually.

### Rule 17: Multiple Transactions
**if:** Showing multiple entries
**then:** Apply Rules 0-16 to EACH entry. Group logically (deposits together, settlements together, charges together). Keep response concise — under 150 words unless detailed breakdown specifically needed.

### Rule 18: Escalation Criteria
**if:** Any of the following:
- Ledger closing balance doesn't match Console/Kite after verifying all entries (Rule 14, 15)
- Entry appears in ledger that client never initiated and cannot be explained by any rule
- Sequence of entries on Console differs from what agent sees (known display bug)
- Charges debited without corresponding trade or event
**then:** Escalate with: client ID, date range, specific mismatched entries, and screenshots if available.
