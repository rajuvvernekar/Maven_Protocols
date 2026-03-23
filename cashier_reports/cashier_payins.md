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

TRIGGER KEYWORDS: "add funds", "add money", "transfer", "payin", "payment failed", "not reflected", "not credited", "deducted but not showing", "money not added", "how to add", "fund", "UPI", "netbanking", "bank transfer", "IMPS", "NEFT", "RTGS", "deposit", "unregistered bank", "unmapped account"

## Protocol

# PAYIN PROTOCOL

---

## Section A: Reference Data

All rules reference these blocks as single sources of truth.

---

### A1: Payment Methods & Specs

| Method | Charge | Credit Timeline | Refund Timeline | Limits/Notes |
|---|---|---|---|---|
| UPI | ₹0 | Instant | 72 working hours | Max ₹5,00,000/txn · Max 35 txn/day · Must use "Add Funds" in Kite (direct UPI transfers fail) |
| Netbanking | ₹10.62 (₹9 + 18% GST) | By 2:00 PM on T+1 banking working day (or instant) | By 5:00 PM on T+2 banking working day | Minimum ₹50 |
| IMPS | ₹0 | 10 minutes | — | — |
| NEFT | ₹0 | 2 hours | — | — |
| RTGS | ₹0 | 2 hours | — | — |
| Cheque | ₹0 (bounce: ₹413 incl. GST) | 3–5 days | — | — |

**Unregistered bank transfer reversal:** 2–3 days.

**Batch window:** Transfers between 12 AM and 7:30 AM reflect in Kite only after 7:30 AM (applies every day including weekends).

**Device wait (UPI):** 24 hours after device mismatch before retry.

**Banking calendar (used for netbanking credit/refund deadlines):**
A banking working day is any day that is not:
- A Sunday
- A public holiday
- The 2nd or 4th Saturday of the month

All other days are banking working days, including the 1st, 3rd, and 5th Saturdays. This is different from the trading calendar — use the banking calendar only for netbanking timelines.

---

### A2: Account & Bank Restrictions

| Account/Bank Type | Restriction |
|---|---|
| Current account | No gateway (UPI/netbanking). IMPS/NEFT/RTGS only. |
| Joint account | UPI/gateway only. IMPS/NEFT/RTGS transfers are auto-reversed. |
| NRI PIS | No UPI/IMPS/NEFT/RTGS. Transfer from NRE/NRO savings → PIS bank account. Bank reports PIS balance to Zerodha EOD, updated before next market open. |
| IDFC 3-in-1 block enabled | Secondary bank accounts cannot be used for payins. Client must disable at console.zerodha.com/account/bank. |

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

Single ledger — balance available for both Equity and Commodity. No separate commodity funds needed.

---

### A8: Links

| Purpose | URL |
|---|---|
| Add funds via IMPS/NEFT/RTGS | https://support.zerodha.com/category/funds/adding-funds/how-to-add-funds/articles/how-do-i-add-money-to-my-trading-account-using-imps-neft-or-rtgs |
| Unmapped bank transfer info | https://support.zerodha.com/category/funds/adding-funds/how-to-add-funds/articles/can-funds-be-transferred-using-imps-neft-rtgs-or-cheque-from-bank-accounts-not-linked-to-the-zerodha-account |
| IDFC 3-in-1 facility | https://support.zerodha.com/category/account-opening/resident-individual/ri-online/articles/idfc-3-in-1-with-blocking-facility |

---

## Section B: Decision Flow

On every payin query, execute in order:

```
1. PREFLIGHT
   ├─ get_all_client_data → check account type, registered banks, IDFC 3-in-1 status
   ├─ If NRI PIS (client_acc_type IN NRO/NRE/NRI AND pis_bank present) → STOP. Escalate to support agent.
   └─ Check payin tool data for matching transactions

2. ROUTE by scenario
   ├─ UPI success/failure → Rule 1
   ├─ Netbanking pending → Rule 2
   ├─ UPI failure troubleshooting → Rule 3
   ├─ Bank details request (RTGS/NEFT/IMPS) → Share A3 details
   ├─ Batch window transfer (12 AM–7:30 AM) → Rule 4
   ├─ Funds deducted, not credited (match found) → Rule 5
   ├─ IMPS/NEFT/RTGS not found in system → Rule 6
   ├─ Customer provides UTR/proof, no match → Rule 7
   ├─ Date mismatch (wrong date, nearby match) → Rule 8
   ├─ Direct UPI transfer → Rule 9
   ├─ Account restriction error → Rule 10
   ├─ Payin confirmed but "not visible" → Rule 11
   ├─ Balance lower than expected / negative → Rule 12
   ├─ Old payin not reflecting, balance = ₹0 → Rule 13
   ├─ Multiple same-day transactions → Rule 14
   └─ Escalation triggers → Rule 15

3. SCOPE
   Only address what the customer asked. Do not volunteer information
   about withdrawals, holdings, positions, or other unrelated topics
   unless directly relevant to the reported issue.
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

**Step 1 — Calculate credit deadline:**
Credit deadline = 2:00 PM on the next banking working day (T+1) after `date_initiated`. Use the banking calendar from **A1**: working day = any day that is not a Sunday, not a public holiday, not a 2nd/4th Saturday. State the explicit date and day name. Verify the day name matches the date before responding (e.g., 25 Feb 2026 = Wednesday).

Refund deadline = 5:00 PM on the second banking working day (T+2) after `date_initiated`.

Examples:
- Initiated Friday 1 PM → T+1 = Saturday (if 1st/3rd/5th Saturday) → credit deadline Saturday 2:00 PM. If Saturday is 2nd/4th → T+1 = Monday → credit deadline Monday 2:00 PM.
- Initiated Saturday 5 PM (1st/3rd/5th Saturday) → T+1 = Monday → credit deadline Monday 2:00 PM. If Monday is a public holiday → T+1 = Tuesday.

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
If both deadlines have already passed → escalate to funds team with proof.

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

---

### Rule 7: Customer Provides UTR / Proof — No Match

**Sub-case A — Proof provided as attachment:**
Acknowledge the proof. Response: "Your [UTR / transaction slip / bank receipt] for ₹[amount] shows a transfer that hasn't reached our system yet and requires a manual update. Escalating this to our funds team for investigation." Escalate immediately with all available details. Do not request details already provided.

**Sub-case B — UTR or reference number in message text only, no attachment:**
Response: "We're unable to locate a transaction matching the reference number you've provided. To help us investigate, please share a screenshot of your bank statement showing the transaction details (amount, date, and reference number)." Do not share any other transaction data from the system. Do not escalate until proof is received.

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

**NRI PIS:** Escalate all payin queries to support agent (handled in preflight).

**IDFC 3-in-1 Block:**
If customer reports "lien enabled" / "not allowed instant transfer" / "block facility" error OR payin fails from secondary account → check `idfc_3_in_1_status` from `get_all_client_data`. If = "Yes": "Your account has the IDFC 3-in-1 block facility enabled, which prevents adding funds from secondary bank accounts. To disable this, visit console.zerodha.com/account/bank and click 'Disable IDFC 3-in-1 account.'" Link: **A8** IDFC 3-in-1.

---

### Rule 11: Payin Confirmed but "Not Visible"

1. Use `kite_margins` to confirm current available balance.
2. Respond: "Your payment of ₹[amount] is credited to your account on [date] at [time] (bank reference: [bank_reference]). Check updated balance on Kite → Funds."
3. Check `ledger_report`:
   - Transaction found → "You may check the ledger statement on Console to verify the transaction details."
   - Transaction not found → use **A7** timing guidance for the appropriate scenario.
4. If customer insists funds are not visible despite confirmed payin → "Please check if Privacy mode is enabled on Kite, which hides account details. You can disable it from Kite → Settings."

---

### Rule 12: Balance Lower Than Expected / Negative Balance

If payin is successful but available balance (from `kite_margins`) is lower than expected or ledger shows negative opening balance:

1. Confirm the payin using Rule 11 format.
2. Check `kite_orders` for order history on the payin date only:
   - Orders found → "Your account placed orders on [date], which reduced your available balance."
   - No orders found → do not reference trading activity.
3. Check `ledger_report` for: negative opening balance, AMC charges, NSE/BSE charges, trading debit obligations, delayed payment charges, or prior QS payouts.
4. State: "Your account had a negative balance of -₹[X] prior to this transaction due to [specific reason from ledger]. This was adjusted against your deposit, resulting in your current balance of ₹[current balance]."

Only explain if ledger data confirms the cause. If ledger doesn't explain the gap → escalate to funds team.

---

### Rule 13: Quarterly Settlement (QS) Check

If customer reports old payin (>30 days) not reflecting and account balance = ₹0:

1. Check `crux_qs_payouts` and `ledger_report` for any QS between payin date and today.
2. QS found → "Your funds were added successfully on [payin date], but a Quarterly Settlement was processed on [QS date], which transferred the idle balance back to your bank account."
3. No QS found → escalate to funds team.

---

### Rule 14: Multiple Same-Day Transactions

If multiple payin transactions exist on the same day → address ALL transactions relevant to the query. Apply Rule 1, 2, 5, or 6 per transaction based on `transfer_mode` and `Status`.

- 3 or fewer transactions: present each with amount, method, status, and action.
- More than 3: detail the 3 most recent. For the rest: "There are [N] additional transactions on this date. Please check Kite → Funds for the complete list or write back for details on a specific transaction."

**Transaction scope:** Only present transactions relevant to the customer's query. For "unable to add funds" or recent failure queries, show only the most recent failed attempt and any same-day transactions.

---

### Rule 15: Escalation Triggers

Escalate to funds team with transaction details when:
- Unlinked bank transfer (confirmed via Rule 6)
- Bank success but Zerodha failed
- U30 error (bank-side issue)
- Cheque debited but no system entry — escalate immediately without troubleshooting
- Customer provides UTR/bank receipt with no matching payin (Rule 7 Sub-case A)

---

## Section D: General Notes

- Only registered bank accounts are accepted for payins (SEBI mandate). Transfers from unlinked accounts are auto-reversed within 2–3 days.
- Successful payins show instantly on Kite; Console ledger updates EOD (see **A7** for full timing).
- Privacy mode on Kite hides account details including fund balances. Suggest disabling if payin is confirmed but customer reports funds not visible.
