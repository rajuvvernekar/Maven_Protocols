# cashier_payins

## Description

WHEN TO USE:

When clients:
- Ask how to add funds using a specific payment method (UPI, Netbanking, Bank Transfer, Cheque)
- Report a payment failed or was rejected with an error message
- Say money was deducted from their bank account but hasn't appeared in Zerodha yet
- Report receiving only partial amount in their Zerodha account vs what they sent
- Have questions about payment limits, charges, or timelines for fund additions
- Need to understand why a specific payment method is not available to them
- Ask about Zerodha's bank details for fund transfers

TRIGGER KEYWORDS: "add funds", "add money", "transfer", "payin", "payment failed", "not reflected", "not credited", "deducted but not showing", "money not added", "how to add", "fund", "UPI", "netbanking", "bank transfer", "IMPS", "NEFT", "RTGS", "deposit", "unregistered bank", "unmapped account", "bank details"

## Protocol

# PAYIN PROTOCOL

---

## Section A: Reference Data

All rules reference these blocks as single sources of truth.

---

### A1: Payment Methods & Specs

| Method | Charge | Credit Timeline | Refund Timeline | Limits/Notes |
|---|---|---|---|---|
| UPI | ₹0 | Instant | 72 working hours | Max ₹5,00,000/txn · Max 35 txn/day · Must use "Add Funds" in Kite (direct UPI transfers fail). The ₹5,00,000 per-transaction limit is set by NPCI and the Zerodha payment gateway — it is not a Zerodha-imposed limit. |
| Netbanking | ₹10.62 (₹9 + 18% GST) | By 2:00 PM on T+1 banking working day (or instant) | By 5:00 PM on T+2 banking working day | Minimum ₹50 |
| IMPS | ₹0 | 10 minutes | — | — |
| NEFT | ₹0 | 2 hours | — | — |
| RTGS | ₹0 | 2 hours | — | — |
| Cheque | ₹0 (bounce: ₹413 incl. GST) | 3–5 days | — | — |

**Zerodha-side transfer limits:**
- Netbanking: No Zerodha-imposed limit on amount (bank limits may apply). Up to 25 transfers/day.
- NEFT/RTGS: No Zerodha-imposed limits on amount or frequency.
- IMPS: No Zerodha-imposed limits (banks typically cap at ₹2L/txn).
- UPI: Max ₹5,00,000/txn (NPCI/payment gateway limit, not Zerodha), 35 txn/day.

If a customer reports hitting a limit on netbanking, NEFT, RTGS, or IMPS, it is bank-imposed. Zerodha does not impose amount limits on these methods. For large transfers, recommend NEFT or RTGS.

**Unregistered bank transfer reversal:** 2–3 days.

**Batch window:** Transfers between 12 AM and 7:30 AM reflect in Kite only after 7:30 AM (applies every day including weekends).

**Device wait (UPI):** 24 hours after device mismatch before retry.

**Banking calendar (used for netbanking credit/refund deadlines):**
A banking working day is any day that is not:
- A Sunday
- A public holiday
- The 2nd or 4th Saturday of the month

All other days are banking working days, including the 1st, 3rd, and 5th Saturdays. This is different from the trading calendar — use the banking calendar only for netbanking timelines.

**Cashier Payin report visibility:**
- Netbanking (payment gateway) transactions: Visible in Cashier Payin report for 7 days only. After 7 days, these records are no longer available in the Cashier Payin report.
- UPI and NEFT/IMPS transactions: Continue to be available in the Cashier Payin report beyond 7 days.
- For netbanking transactions older than 7 days, use the `ledger_report` to verify payin status instead of the Cashier Payin report.

---

### A2: Account & Bank Restrictions

| Account/Bank Type | Restriction |
|---|---|
| Current account | No gateway (UPI/netbanking). IMPS/NEFT/RTGS only. |
| Joint account | UPI/gateway only. IMPS/NEFT/RTGS transfers are auto-reversed. |
| NRI PIS | No UPI/IMPS/NEFT/RTGS. Transfer from NRE/NRO savings → PIS bank account. Bank reports PIS balance to Zerodha EOD, updated before next market open. |
| IDFC 3-in-1 block enabled | Secondary bank accounts cannot be used for payins. Client must disable at console.zerodha.com/account/bank. |
| Third-party accounts (spouse, family, others) | Not accepted. Only the account holder's own registered bank accounts can be used for payins. Transfers from third-party accounts, including spouse or family members, will be rejected or auto-reversed. |
| HUF (Hindu Undivided Family) | No UPI. UPI is only available for individual or sole proprietorship accounts. HUF must use netbanking, NEFT, RTGS, IMPS, or cheque. |

**Bank account limits:**
- Primary: 1 allowed. Payins + withdrawals.
- Secondary: 2 allowed. Payins + withdrawals.

Both primary and secondary registered accounts are accepted for payins. Rejection applies only to unregistered accounts.

---

### A3: Zerodha Bank Details (RTGS/NEFT/IMPS)

When a customer asks for Zerodha's bank details, share only these exact values:

- Bank Name: HDFC Bank
- Account Title: ZERODHA BROKING LTD
- Account Number: ZERNSE
- Account Type: Current account
- Branch: Sandoz Branch, Mumbai
- IFSC: HDFC0000240

For step-by-step instructions: https://support.zerodha.com/category/funds/adding-funds/how-to-add-funds/articles/how-do-i-add-money-to-my-trading-account-using-imps-neft-or-rtgs

These are the only valid bank details. Any other bank details (from tool data, virtual accounts, or any other source) are incorrect.

**HDFC Bank users:** If the bank's interface does not accept the alphanumeric account number "ZERNSE" when adding Zerodha as a beneficiary for NEFT/IMPS, select the "Transfer to eCMS account" option in HDFC netbanking. This bypasses the alphanumeric restriction.

---

### A4: UPI Error Translations

| Error Code (internal only) | Client-Facing Explanation |
|---|---|
| U30 | "The transaction failed due to a bank-side issue. Please contact your bank for details." |
| U66 | "The transaction was declined due to a device mismatch. Please use the device registered with your bank or wait 24 hours and retry." |
| U69 | "The transaction expired. UPI requests must be approved within 5 minutes. Please retry." |
| Z8 | "The transaction exceeded your daily UPI limit. Please reduce the amount or retry tomorrow." |
| Z9 | "The transaction failed due to insufficient funds in your bank account. Please verify your balance and retry." |
| ZA | "The transaction was declined from your end." |
| ZE | "Your UPI ID (VPA) appears to be blocked at your bank's end. Please contact your bank to unblock it." |
| ZH | "The UPI ID entered appears to be invalid. Please verify and retry." |
| ZM | "The transaction failed due to an incorrect UPI PIN." |

Error codes are for internal identification only — use only the client-facing explanation in responses.

---

### A5: UPI VPA IDs

Official Zerodha UPI IDs: zerodhabroking.brk@validhdfc, zerodhabroking.brk@validicici, zerodhabroking.brk@validaxis, zerodhabroking@hdfcbank, zerodha.broking@icici, zerodhabroking@axisbank, zerodhabroking@yesbank

---

### A6: Field Rules

**Shareable with client:** `bank_reference` (when available)

**Internal reasoning only (use for analysis, communicate findings in plain language):** `status`, `nest_status`, `cashier_reference`, `bank_account_number`, internal error codes, `transfer_mode`

**Status communication — use exactly one of these phrases:**
- Success → "Your payment is credited to your account"
- Failed → "Your payment didn't reach your account"
- Pending (netbanking only) → "Your payment is pending at the bank"

**Status determination:** Only the `Status` field determines outcome. The presence of `cashier_reference` does not mean the payment was processed. Always use `transfer_mode` from tool data for the payment method, not the customer's claimed method.

---

### A7: Kite vs Console Timing

| Scenario | Kite Balance | Console Ledger |
|---|---|---|
| Weekday transfer, after 7:30 AM | Instant | Updates by end of day |
| Weekday transfer, 12 AM–7:30 AM | After 7:30 AM | Updates by end of day |
| Weekend transfer, after 7:30 AM | Instant | Updates Monday morning |
| Weekend transfer, 12 AM–7:30 AM | After 7:30 AM | Updates Monday morning |

Successful payins show instantly on Kite (or after 7:30 AM for batch window). Console ledger updates EOD on weekdays, Monday morning for weekends.

**Weekend payin visibility on Kite:** Funds added on Saturday or Sunday are recorded in the ledger on the same day (the ledger updates on weekends). However, on Monday, these funds still appear under the **"Payin"** line item in `kite_margins` rather than in the opening balance — because Monday's opening balance is carried forward from Friday's closing balance and does not include weekend payins. The funds are safe, fully available for trading from Monday, and included in the total available balance on Kite. This is normal processing.

Single ledger — balance available for both Equity and Commodity. No separate commodity funds needed.

---

### A8: Links

| Purpose | URL |
|---|---|
| Add funds via IMPS/NEFT/RTGS | https://support.zerodha.com/category/funds/adding-funds/how-to-add-funds/articles/how-do-i-add-money-to-my-trading-account-using-imps-neft-or-rtgs |
| Unmapped bank transfer info | https://support.zerodha.com/category/funds/adding-funds/how-to-add-funds/articles/can-funds-be-transferred-using-imps-neft-rtgs-or-cheque-from-bank-accounts-not-linked-to-the-zerodha-account |
| IDFC 3-in-1 facility | https://support.zerodha.com/category/funds/adding-funds/how-to-add-funds/articles/idfc-3-in-1-with-blocking-facility |

---

## Section B: Decision Flow

On every payin query, execute in order:

```
1. PREFLIGHT
   ├─ get_all_client_data → check account type, registered banks, IDFC 3-in-1 status
   ├─ If NRI PIS (client_acc_type IN NRO/NRE/NRI AND pis_bank present) → STOP. **ESCALATE** — agent review needed.
   ├─ UNLINKED ACCOUNT CHECK: If customer mentions transferring from an unlinked,
   │   unregistered, or unmapped bank account, or from a third-party account (spouse, family,
   │   others) → address this concern directly, even if other successful transactions exist
   │   in the system. A successful transaction from a different account does not resolve
   │   the client's stated concern about the unlinked transfer.
   │   State: "As per SEBI regulations, funds can only be transferred from bank accounts
   │   linked to your Zerodha account." Do not proceed to alternatives that suggest unlinked
   │   or third-party transfers are possible. Do not substitute a different transaction as
   │   the answer.
   ├─ FRESH ACCOUNT CHECK: If account_activation_date is within the last 24 hours AND the
   │   payin creation date is the same as the activation date → this applies only to newly
   │   opened accounts (not REKYC or segment activation). See Rule 16.
   └─ Check payin tool data for matching transactions

2. ROUTE by scenario
   ├─ UPI success/failure → Rule 1
   ├─ Netbanking pending → Rule 2
   ├─ UPI failure troubleshooting → Rule 3
   ├─ Bank details request (RTGS/NEFT/IMPS) → Share A3 details
   ├─ Batch window transfer (12 AM–7:30 AM) → Rule 4
   ├─ Funds deducted, not credited (match found) → Rule 5
   ├─ IMPS/NEFT/RTGS not found in system → Rule 6 (includes UTR-based re-query)
   ├─ Customer provides UTR/proof, no match → Rule 7 (includes UTR-based re-query)
   ├─ Date mismatch (wrong date, nearby match) → Rule 8
   ├─ Direct UPI transfer → Rule 9
   ├─ Account restriction error → Rule 10
   ├─ Payin confirmed but "not visible" → Rule 11
   ├─ Balance lower than expected / negative → Rule 12
   ├─ Old payin not reflecting, balance = ₹0 → Rule 13
   ├─ Multiple same-day transactions → Rule 14
   ├─ Escalation triggers → Rule 15
   ├─ Fresh account payin failures → Rule 16
   └─ Penny drop / test deposit query → Rule 17

3. SCOPE
   - Keep responses focused on the customer's payin query. Include information
   about withdrawals, holdings, positions, or other topics only when directly
   relevant to the reported issue.
```

---

## Section C: Rules

Rules reference Section A blocks. They do not redefine what is already defined there.

---

### Rule 1: UPI Status

- Success → "Your payment is credited to your account. Check Kite → Funds."
- Failed OR Unknown → "Your payment didn't reach your account. The amount will be refunded to your bank account within 72 working hours." Treat Unknown as Failed.

---

### Rule 2: Netbanking Pending

If `transfer_mode` = netbanking AND `Status` = Unknown:

**Note on data availability:** Netbanking (payment gateway) transactions are only visible in the Cashier Payin report for 7 days (per **A1**). If the transaction is older than 7 days and not found in the Cashier Payin report, check the `ledger_report` for the payin entry before concluding the transaction doesn't exist.

**Step 1 — Calculate credit deadline:**
Credit deadline = 2:00 PM on the next banking working day (T+1) after `date_initiated`. Use the banking calendar from **A1**: working day = any day that is not a Sunday, not a public holiday, not a 2nd/4th Saturday. State the explicit date and day name.

**Step 1b — VERIFY date and day name:** Confirm that the day name matches the calendar date before responding. If the computed date falls on a different day than stated, correct it. Incorrect day names will mislead the customer.

Refund deadline = 5:00 PM on the second banking working day (T+2) after `date_initiated`.

**T+1 quick reference by initiation day:**

| Initiated on | T+1 (next banking working day) |
|---|---|
| Monday | Tuesday |
| Tuesday | Wednesday |
| Wednesday | Thursday |
| Thursday | Friday |
| Friday | Saturday (if 1st/3rd/5th) or Monday (if 2nd/4th Saturday or Sunday next) |
| Saturday (1st/3rd/5th — banking working day) | Monday (unless Monday is a holiday → Tuesday) |
| Saturday (2nd/4th — not a banking working day) | Monday (unless Monday is a holiday → Tuesday) |
| Sunday | Monday (unless Monday is a holiday → Tuesday) |

**Step 2 — Check if credit deadline has passed:**

- **Credit deadline NOT passed:**
  "Your payment of ₹[amount] [if bank_reference: (bank reference: [bank_reference])] is pending at the bank. The amount will either be credited to your Zerodha account by 2:00 PM on [T+1 day name, date] or refunded to your bank account by 5:00 PM on [T+2 day name, date]."

- **Credit deadline PASSED, refund deadline NOT passed:**
  "Your payment of ₹[amount] was not credited within the processing window. If the amount was debited from your bank account, it will be refunded by 5:00 PM on [T+2 day name, date]. If not debited, no action is needed — the transaction was not completed."

- **Both deadlines PASSED:**
  "Your payment of ₹[amount] was not successful. If the amount was debited from your bank account and has not been refunded yet, please share a screenshot of your bank statement showing the debit so we can investigate further. If not debited, no action is needed."

**Step 3 — Customer confirms debit or provides bank statement proof:**
When the customer explicitly states the amount was debited OR provides a bank statement screenshot showing the debit, state both deadlines:
"Your payment of ₹[amount] is pending at the bank. The amount will either be credited to your Zerodha account by 2:00 PM on [T+1 day name, date] or refunded to your bank account by 5:00 PM on [T+2 day name, date]."
If both deadlines have already passed → **ESCALATE** — funds team review needed, include proof.

---

### Rule 3: UPI Failure Troubleshooting

1. Identify the failure cause from **A4** error translations. Use only the client-facing explanation.
2. Check **A1** UPI limits (₹5,00,000/txn, 35 txn/day).
3. Offer alternatives in this order:
   - First: "Please try using a different UPI application linked to your primary bank account (e.g., Google Pay, PhonePe, BHIM)."
   - If UPI issues persist across apps: "You can add funds using IMPS/NEFT/RTGS (link: **A8**) or netbanking."
   - If customer indicates their registered bank is inactive → suggest adding another active bank on Console → Profile → Bank accounts.
   - If customer mentions being outside India → escalate NRI conversion to support agent.

UPI failure and negative account balance are separate issues. Address the UPI failure first, then mention the outstanding debit balance separately if applicable.

---

### Rule 4: Batch Window

If `time_initiated` falls within 12 AM–7:30 AM → include this line: "Funds transferred between 12 AM and 7:30 AM will reflect in your Kite account only after 7:30 AM."

Applies every day including weekends.

---

### Rule 5: Funds Deducted, Not Credited (Match Found)

If customer says money left bank and a matching transaction exists in payins with status unconfirmed → "Your payment is pending at the bank." Provide the method-specific timeline from **A1**. If not credited within the timeline, auto-reversed.

Only apply when a matching transaction IS found. If no match → Rule 6.

---

### Rule 6: IMPS/NEFT/RTGS Not Found

If customer reports an IMPS/NEFT/RTGS transfer and no matching transaction exists in payins:

**Step 1:** Check `get_all_client_data` → `registered_bank_accounts`. Compare customer's source account against registered accounts.

**Step 2a — Source doesn't match any registered account:**
"The transfer was sent from a bank account not linked to your Zerodha account. Only registered bank accounts are accepted (SEBI mandate). The amount will be reversed to your bank account within 2–3 days." Share unmapped bank transfer link from **A8**. Direct to Console → Profile → Bank accounts.

**Step 2b — Source matches OR not provided:**
"We don't see this transfer in our system." Ask customer to confirm source account and registration status. If attachment shows debit, acknowledge it but state it hasn't reached the system. Note SEBI registered-account mandate and 2–3 day reversal timeline for unregistered transfers.

**Step 3 — UTR / Reference-Based Re-query for Direct Transfers:**

Some NEFT/IMPS/RTGS transfers do not appear in `cashier_payins` because they were made via direct bank transfer (not through Kite "Add Funds"). These transactions bypass the normal payin flow and may only be locatable by their UTR or bank reference number.

**When to trigger this step:**
- No matching transaction found in `cashier_payins` for the client, AND
- The customer has provided a UTR number, bank reference number, or bank statement screenshot/attachment showing the transaction details.

**Procedure:**

1. **Extract the reference number:**
   - From attachment/screenshot: Read the UTR number or bank reference number from the document/image provided by the customer.
   - From message text: Use the UTR or reference number the customer has typed in the ticket.

2. **Re-query the payin tool WITHOUT the client ID:**
   - Call the `cashier_payins` lookup tool again.
   - **Leave the client ID field empty/blank.**
   - **Enter the UTR number or bank reference number** in the reference number field.
   - This searches across all incoming transfers (not scoped to the specific client), which is necessary because direct NEFT/IMPS/RTGS transfers may not be tagged to the client's account in the system.

3. **Evaluate the result:**

   **3a — Transaction found, account number matches a registered bank account:**
   - Cross-check the `bank_account_number` from the re-query result against the customer's `registered_bank_accounts` from `get_all_client_data`.
   - If the account number matches any registered (primary or secondary) bank account:
     - Response: "We have located your transfer of ₹[amount] (reference: [bank_reference]). The transaction was received via direct bank transfer and requires a manual update to reflect in your account. Escalating this to our funds team for processing."
     - **ESCALATE** — funds team review needed, include: client ID, UTR/reference number, amount, date, and source bank account number.

   **3b — Transaction found, account number does NOT match any registered bank account:**
   - The transfer was made from an unmapped/unregistered bank account.
   - Response: "We have located a transfer matching your reference number. However, the transfer was sent from a bank account not linked to your Zerodha account. As per SEBI regulations, only transfers from registered bank accounts are accepted. The amount will be reversed to the source bank account within 2–3 days."
   - Share unmapped bank transfer link from **A8**.

   **3c — Transaction NOT found even after re-query:**
   - The transfer has not reached Zerodha's banking system at all.
   - If the customer has provided proof (attachment/screenshot): **ESCALATE** — funds team review needed immediately per **Rule 7 Sub-case A**.
   - If the customer provided only a reference number in text (no attachment): Request bank statement screenshot per **Rule 7 Sub-case B**.

**Important safeguards:**
- Only perform this re-query when the customer has explicitly provided a UTR or bank reference number (via text or attachment). Do not guess or fabricate reference numbers.
- The re-query without client ID is an internal lookup step. Do not share raw tool output, internal field names, or the fact that the search was broadened. Communicate findings in plain language only.
- This step applies exclusively to NEFT/IMPS/RTGS transfers. It does not apply to UPI or netbanking transactions.

---

### Rule 7: Customer Provides UTR / Proof — No Match

**Sub-case A — Proof provided as attachment (NEFT/IMPS/RTGS transfers):**
1. Extract the UTR or bank reference number from the attachment.
2. **Perform the UTR-based re-query as described in Rule 6 Step 3** (re-query the `cashier_payins` tool without client ID, using the reference number from the proof).
3. Follow the outcome:
   - **Rule 6 Step 3a** (match found, registered account) → **ESCALATE** — funds team review needed for manual update.
   - **Rule 6 Step 3b** (match found, unregistered account) → Inform customer of unmapped transfer reversal.
   - **Rule 6 Step 3c** (no match even after re-query) → Acknowledge the proof. Response: "Your [UTR / transaction slip / bank receipt] for ₹[amount] shows a transfer that hasn't reached our system yet and requires a manual update. Escalating this to our funds team for investigation." **ESCALATE** immediately with all available details.

**Sub-case A — Proof provided as attachment (UPI / netbanking transfers):**
Acknowledge the proof. Response: "Your [UTR / transaction slip / bank receipt] for ₹[amount] shows a transfer that hasn't reached our system yet and requires a manual update. Escalating this to our funds team for investigation." **ESCALATE** immediately with all available details. Do not request details already provided. (UTR re-query does not apply to UPI/netbanking.)

**Sub-case B — UTR or reference number in message text only, no attachment:**
1. If the transfer method is NEFT/IMPS/RTGS: **Perform the UTR-based re-query as described in Rule 6 Step 3** using the reference number provided in the message text.
   - **Rule 6 Step 3a** (match found, registered account) → **ESCALATE** — funds team review needed for manual update.
   - **Rule 6 Step 3b** (match found, unregistered account) → Inform customer of unmapped transfer reversal.
   - **Rule 6 Step 3c** (no match even after re-query) → Response: "We're unable to locate a transaction matching the reference number you've provided. To help us investigate, please share a screenshot of your bank statement showing the transaction details (amount, date, and reference number)." Do not escalate until proof is received.
2. If the transfer method is UPI/netbanking or unknown: Response: "We're unable to locate a transaction matching the reference number you've provided. To help us investigate, please share a screenshot of your bank statement showing the transaction details (amount, date, and reference number)." Do not share any other transaction data from the system. Do not escalate until proof is received.

---

### Rule 8: Date Mismatch

If customer states a specific transfer date, no match on that date, but transactions exist on a nearby date:

1. Address all transactions found on the nearby date — apply Rule 1, 2, 5, or 6 as applicable per transaction.
2. Add: "We don't see a transaction on [customer's claimed date]. If you believe a separate transfer was made on that date, please share a screenshot of your bank statement showing the transaction details so we can investigate further."

---

### Rule 9: Direct UPI Transfer

If customer transferred directly via UPI (not through "Add Funds"): "Direct UPI transfers to Zerodha are not supported. Please use the 'Add Funds' button in Kite → select UPI to add funds."

---

### Rule 10: Account Restrictions

Check **A2** for the customer's account/bank type and advise per restriction.

**Third-party / spouse accounts:** If customer asks about adding funds from a spouse's, family member's, or any other person's bank account → "Only bank accounts registered in your name and linked to your Zerodha account can be used to add funds. Transfers from third-party accounts, including spouse or family members, are not accepted as per SEBI regulations." Share fund transfer methods link from **A8**.

**NRI PIS:** Escalate all payin queries to support agent (handled in preflight).

**IDFC 3-in-1 Block:**
If customer reports "lien enabled" / "not allowed instant transfer" / "block facility" error OR payin fails from secondary account → check `idfc_3_in_1_status` from `get_all_client_data`. If = "Yes": "Your account has the IDFC 3-in-1 block facility enabled, which prevents adding funds from secondary bank accounts. To disable this, visit console.zerodha.com/account/bank and click 'Disable IDFC 3-in-1 account.'" Link: **A8** IDFC 3-in-1.

---

### Rule 11: Payin Confirmed but "Not Visible"

1. Use `kite_margins` to confirm current available balance. **kite_margins is the authoritative source for whether funds are available.** If kite_margins shows the balance includes the payin amount, the funds are credited — regardless of what the payin tool status shows.
2. **Weekend payin check:** If the payin was made on a Saturday or Sunday, confirm the amount is visible under the Payin line in `kite_margins` (per **A7**). Respond: "Your payment of ₹[amount] added on [Saturday/Sunday] has been recorded in your ledger. On Monday, this amount appears under the Payin line on Kite rather than in your opening balance — this is because the opening balance is carried forward from Friday's closing balance. Your funds are safe and available for trading."
3. For weekday payins, respond: "Your payment of ₹[amount] is credited to your account on [date] at [time] (bank reference: [bank_reference]). Check updated balance on Kite → Funds."
4. Check `ledger_report`:
   - Transaction found → "You may check the ledger statement on Console to verify the transaction details."
   - Transaction not found → use **A7** timing guidance for the appropriate scenario.
5. If customer insists funds are not visible despite confirmed payin → "Please check if Privacy mode is enabled on Kite, which hides account details. You can disable it from Kite → Settings."

---

### Rule 12: Balance Lower Than Expected / Negative Balance

If payin is successful but available balance (from `kite_margins`) is lower than expected or ledger shows negative opening balance:

1. Confirm the payin using Rule 11 format.
2. Check `kite_orders` for order history on the payin date only:
   - Orders found → "Your account placed orders on [date], which reduced your available balance."
   - No orders found → do not reference trading activity.
3. Check `ledger_report` for: negative opening balance, AMC charges, NSE/BSE charges, trading debit obligations, delayed payment charges, or prior QS payouts.
4. State: "Your account had a negative balance of -₹[X] prior to this transaction due to [specific reason from ledger]. This was adjusted against your deposit, resulting in your current balance of ₹[current balance]."

Only explain if ledger data confirms the cause. If ledger doesn't explain the gap → **ESCALATE** — funds team review needed.

**MTF margin shortfall:** If ledger shows MTF-related debits (look for "MTF" entries in the ledger) → flag urgency: "Your account has an MTF margin shortfall of ₹[X]. If this shortfall is not cleared, open MTF positions may be squared off. Please check the email notification sent regarding this shortage." Reference the Communication Tab for notifications sent to the client.

---

### Rule 13: Quarterly Settlement (QS) Check

If customer reports old payin (>30 days) not reflecting and account balance = ₹0:

1. Check `crux_qs_payouts` and `ledger_report` for any QS between payin date and today.
2. QS found → "Your funds were added successfully on [payin date], but a Quarterly Settlement was processed on [QS date], which transferred the idle balance back to your bank account."
3. No QS found → **ESCALATE** — funds team review needed.

---

### Rule 14: Multiple Same-Day Transactions

**Present a maximum of 3 individual transactions in a response.** For more than 3, summarize the rest. This limit applies regardless of how many transactions exist.

If multiple payin transactions exist on the same day → address ALL transactions relevant to the query. Apply Rule 1, 2, 5, or 6 per transaction based on `transfer_mode` and `Status`.

**Pre-response completeness check:** Before responding, count all transactions for the queried date. If the tool returns more transactions than addressed in the response, either detail them (≤3) or summarize the rest. Silently omitting transactions is incorrect.

**Match the client's stated method and amount:** If the client says "UPI transfer of ₹10,000", look for UPI transactions of that amount first. Do not substitute a different method's transaction (e.g., netbanking) as the answer. If transactions from both methods exist, address both.

When multiple transactions exist, always address both successful AND failed/pending transactions. A successful transaction does not cancel the need to explain a failed or pending one.

For multi-source-account queries (customer mentions transfers from different banks/accounts), address each source account's transactions separately.

- 3 or fewer transactions: present each with amount, method, status, and action.
- More than 3: detail the 3 most recent. For the rest: "There are [N] additional transactions on this date. Please check Kite → Funds for the complete list or write back for details on a specific transaction."

**Template for summarizing multiple failed UPI transactions:**
"We can see [N] failed UPI payment attempts from your [bank name] account between [date range]. None of these amounts were credited to your Zerodha account. If any amounts were debited from your bank account, they will be refunded within 72 working hours."

**Transaction scope:** Only present transactions relevant to the customer's query. For "unable to add funds" or recent failure queries, show only the most recent failed attempt and any same-day transactions. After a successful transfer, past failed attempts on the same day are typically irrelevant — summarize them briefly rather than listing individually.

---

### Rule 15: Escalation Triggers

**ESCALATE** — funds team review needed, include transaction details when:
- Unlinked bank transfer (confirmed via Rule 6)
- Bank success but Zerodha failed
- U30 error (bank-side issue)
- Cheque debited but no system entry — **ESCALATE** immediately without troubleshooting
- Customer provides UTR/bank receipt with no matching payin (Rule 7 Sub-case A)
- Direct NEFT/IMPS/RTGS transfer found via UTR re-query from a registered account (Rule 6 Step 3a)

---

### Rule 16: Fresh Account Payin Failures

If `account_activation_date` is within the last 24 hours AND the payin creation date is the same as the activation date:

This applies only to newly opened accounts — not to accounts that have undergone REKYC or segment activation.

Response: "Your account was recently activated. It takes up to 24 working hours for the account to fully synchronize with the exchanges. Errors may occur when adding funds or placing orders during this period. Please try again tomorrow."

---

### Rule 17: Penny Drop / Test Deposit

If customer asks about a ₹1 credit from "ZERODHA BR" via IMPS:

Response: "The ₹1 credited to your account is a standard test deposit. This typically occurs when you create a mandate or recently add a bank account to your Zerodha account. This transaction is normal and does not impact your account."

