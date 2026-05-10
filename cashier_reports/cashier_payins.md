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

TAGS: funds

## Protocol

# CASHIER PAYINS PROTOCOL

---

## Section A: Reference Data

### A1: Payment Methods & Specs

| Method | Charge | Credit Timeline | Refund Timeline | Limits / Notes |
|---|---|---|---|---|
| UPI | ₹0 | Instant | 72 working hours | Max ₹5,00,000/txn (NPCI/gateway limit, not Zerodha) · Max 35 txn/day · Must use "Add Funds" in Kite — direct UPI transfers fail |
| Netbanking | ₹10.62 (₹9 \+ 18% GST) | By 2:00 PM on T+1 banking working day (or instant) | By 5:00 PM on T+2 banking working day | Min ₹50 · Up to 25 transfers/day · No amount limit |
| IMPS | ₹0 | 10 min | — | No Zerodha-imposed limits (banks typically cap ₹2L/txn) |
| NEFT | ₹0 | 2 hours | — | No Zerodha-imposed limits |
| RTGS | ₹0 | 2 hours | — | No Zerodha-imposed limits |
| Cheque | ₹0 (bounce: ₹413 incl. GST) | 3–5 days | — | — |

---

### A2: Important Timelines

- **Unregistered bank transfer reversal:** 2–3 days.
- **Batch window:** Transfers between 12 AM–7:30 AM reflect in Kite only after 7:30 AM (daily, including weekends).
- **Cashier Payin report visibility:** Netbanking (gateway) is visible for 7 days only — use `ledger_report` for older transactions. UPI and NEFT/IMPS are available beyond 7 days.

---

### A3: Account & Bank Restrictions

| Account/Bank Type | Restriction |
|---|---|
| Current account | No gateway (UPI/netbanking). IMPS/NEFT/RTGS only. |
| Joint account | UPI/gateway only. IMPS/NEFT/RTGS auto-reversed. |
| IDFC 3-in-1 block enabled | Secondary bank accounts cannot be used for payins. Disable at console.zerodha.com/account/bank. |
| Third-party accounts (spouse, family, others) | Not accepted. Only the account holder's own registered bank accounts. Transfers from others → rejected/auto-reversed. |
| HUF | No UPI. Use netbanking, NEFT, RTGS, IMPS, or cheque. |

- **Bank account limits:** Primary: 1. Secondary: 2. Both primary and secondary accepted for payins.

---

### A4: Zerodha Bank Details (NEFT/RTGS/IMPS)

**Primary:**
| Field | Value |
|---|---|
| Bank | HDFC Bank |
| Account Title | ZERODHA BROKING LTD |
| Account Number | ZERNSE |
| Account Type | Current |
| Branch | Sandoz Branch, Mumbai |
| IFSC | HDFC0000240 |

**Alternate:**
| Field | Value |
|---|---|
| Bank | HDFC Bank |
| Account Title | ZERODHA BROKING LTD |
| Account Number | 57500000302010 |
| Account Type | Current |
| Branch | Richmond Road, Bangalore |
| IFSC | HDFC0000523 |

- HDFC Bank holders can also use the eCMS facility (see A9).

---

### A5: UPI Error Translations

| Error Code | Cause | Suggested Resolution |
|---|---|---|
| U30 | Bank-side failure | Client to contact their bank |
| U66 | Device mismatch | Use the device registered with the bank, or retry after 24 hours |
| U69 | Transaction expired (UPI 5-minute approval window) | Retry |
| Z8 | Daily UPI limit exceeded | Reduce the amount or retry the next day |
| Z9 | Insufficient funds in source bank | Verify balance and retry |
| ZA | Transaction declined by client | — |
| ZE | UPI ID (VPA) blocked at the bank | Client to contact bank to unblock |
| ZH | Invalid UPI ID | Verify and retry |
| ZM | Incorrect UPI PIN | — |

---

### A6: Official Zerodha UPI IDs

-zerodhabroking.brk@validhdfc · zerodhabroking.brk@validicici · zerodhabroking.brk@validaxis · zerodhabroking@hdfcbank · zerodha.broking@icici · zerodhabroking@axisbank · zerodhabroking@yesbank

---

### A7: Field Rules

**Shareable with client:**

| Field | Interpretation |
|---|---|
| `bank_reference` | Bank reference number (when available) |
| `transfer_mode` | Payment method used (UPI, netbanking, NEFT, IMPS, RTGS, cheque) |

**Non-shareable:**

| Field | Interpretation |
|---|---|
| `status` | Internal payment status — use with A10 to interpret |
| `nest_status` | Internal NEST update flag indicating push to trading account |
| `cashier_reference` | Internal cashier reference identifier |
| `bank_account_number` | Source bank account number |
| Error codes | Internal UPI error codes — translate via A5 |

---

### A8: Payin Update Timings — Kite vs Console

| Scenario | Kite Balance | Console Ledger |
|---|---|---|
| Weekday, after 7:30 AM | Instant | EOD |
| Weekday, 12 AM–7:30 AM | After 7:30 AM | EOD |
| Weekend, after 7:30 AM | Instant | Monday morning |
| Weekend, 12 AM–7:30 AM | After 7:30 AM | Monday morning |

- **Weekend payin on Monday:** Funds added Sat/Sun appear under the "Payin" line in `kite_margins` on Monday (not in opening balance, which carries forward from Friday's close).
- **Single ledger:** The fund balance in the Equity segment is available across Equity, F&O, and Commodity trades.

---

### A9: Links

| Purpose | URL |
|---|---|
| Unmapped bank transfer info | https://support.zerodha.com/category/funds/adding-funds/how-to-add-funds/articles/can-funds-be-transferred-using-imps-neft-rtgs-or-cheque-from-bank-accounts-not-linked-to-the-zerodha-account |
| IDFC 3-in-1 facility | https://support.zerodha.com/category/funds/adding-funds/how-to-add-funds/articles/idfc-3-in-1-with-blocking-facility |
| Adding funds via IMPS / NEFT / RTGS (step-by-step) | https://support.zerodha.com/category/funds/adding-funds/how-to-add-funds/articles/how-do-i-add-money-to-my-trading-account-using-imps-neft-or-rtgs |
| HDFC eCMS facility | https://support.zerodha.com/category/funds/adding-bank-accounts/other-bank-related-queries/articles/how-do-i-add-money-through-hdfc-netbanking |

---

### A10: Payment Status Interpretation

| Payment Mode | Status | Meaning |
|---|---|---|
| UPI | Success | Payment credited to the trading account |
| UPI | Failed | Payment did not reach the trading account |
| UPI | Unknown | Treat as Failed — payment did not reach the trading account |
| Netbanking | Success | Payment credited to the trading account |
| Netbanking | Failed | Payment did not reach the trading account |
| Netbanking | Unknown | Payment is pending at the bank (not credited, not failed) |

---

## Section B: Decision Flow

### Routing

```
Route by scenario
├─ Early-exit / no-response conditions (e.g. NRI PIS) → Rule 1
├─ UPI status interpretation (Success / Failed / Unknown) → Rule 2
├─ Netbanking status (Success / Unknown / pending) → Rule 3
├─ UPI failure troubleshooting (error codes, retries, alternatives) → Rule 4
├─ Bank details request (NEFT/RTGS/IMPS) → Rule 16
├─ NEFT / IMPS / RTGS payin not reflected (client says they transferred; UTR / bank receipt / screenshot) → Rule 5
├─ Date mismatch (stated date has no match; amount-match on nearby dates) → Rule 6
├─ Account / bank-type restriction (joint, HUF, current, IDFC 3-in-1, etc.) → Rule 7
├─ Payin confirmed but "not visible" → Rule 8
├─ Balance lower than expected / negative → Rule 9
├─ Old payin not reflecting, balance = ₹0 → Rule 10
├─ Multiple same-day transactions → Rule 11
├─ Fresh account payin failures (≤24h since activation) → Rule 13
├─ Penny drop / ₹1 test deposit from "ZERODHA BR" → Rule 14
└─ Same-day withdrawal request after a deposit (T+1 restriction) → Rule 15
```

### Fallback

-If no root cause is identified after completing all applicable rules → escalate to a human agent.

---

## Section C: Rules

### Rule 1: Early Exit

-If `account_type` = NRI PIS → escalate to a human agent. Do not respond and do not share bank details.

---

### Rule 2: UPI Status

| Status | Meaning |
|---|---|
| Success | Payment credited to the trading account. |
| Failed | Payment did not reach the trading account. Refund to source bank within 72 working hours (per **A1**). |
| Unknown | Treat as Failed — payment did not reach the trading account. Refund to source bank within 72 working hours (per **A1**). |

---

### Rule 3: Netbanking Status

Applies when `transfer_mode` = netbanking.

**Status = Success:** Funds are credited to the trading account. No further action required.

**Status = Failed:** The payment failed. If the amount was debited from the source bank, it will be reversed within the netbanking refund timeline (per **A1**).

**Status = Unknown:** Pending at the bank — not failed. Evaluate the timeline state:

| Timeline state | Meaning |
|---|---|
| Credit deadline NOT passed | Payment pending at the bank. Will either be credited by 2:00 PM on T+1 banking working day or refunded to source bank by 5:00 PM on T+2 banking working day (per **A1**). |
| Credit deadline PASSED, refund deadline NOT passed | Payment not credited within the processing window. If debited from source bank, refund by 5:00 PM on T+2 banking working day (per **A1**). If not debited, no action needed. |
| Both deadlines PASSED | Payment unsuccessful. If debited and not yet refunded, request bank statement screenshot (debit proof) to investigate. If not debited, no action needed. |

**Customer confirms debit or provides bank statement:** State both deadlines (credit \+ refund). If both deadlines already passed → escalate to a human agent with proof.

---

### Rule 4: UPI Failure Troubleshooting

1. Identify cause from A5.
2. Check A1 UPI limits (₹5L/txn, 35 txn/day).
3. Alternatives in order:
   - Suggest a different UPI app linked to the primary bank account (e.g., Google Pay, PhonePe, BHIM).
   - If UPI issues persist, suggest IMPS/NEFT/RTGS or netbanking; share the step-by-step link from A9.
   - Inactive registered bank → suggest adding another active bank via Console → Profile → Bank accounts.
   - Customer outside India → escalate NRI conversion to a human agent.

---

### Rule 5: Payment Not Reflected (NEFT / IMPS / RTGS)

-Applies when the client says they added funds via NEFT / IMPS / RTGS but the payin isn't reflected in the trading account — directly, in a screenshot, or with a UTR / bank receipt.

UPI cases → **Rule 2**. Netbanking cases → **Rule 3**.

**Step 1 — Get the UTR / reference number:**

Check if the client has shared a UTR or bank reference number in the attachment or query text.

- Provided → go to Step 2.
- Not provided → request a bank statement screenshot showing the amount, date, and UTR / reference number. Do not proceed until received.

**Step 2 — UTR re-query:**

Invoke `cashier_payin` — keep `client_id` blank and fill only the UTR / reference number. For NEFT / IMPS / RTGS, `status` is always Success when the transaction is located — only `nest_update` and the bank-account match determine the next step.

| Result | Action |
|---|---|
| Found — `nest_update` = N/A or Pending | Transfer has reached Zerodha but hasn't been pushed to the trading account yet. Go to Step 3 (bank account match). |
| Not found | No record of this UTR in Zerodha's system. Escalate to a human agent for the funds team to check — include UTR and proof. |

**Step 3 — Bank account match:**

Check the source account against the client's registered bank accounts (`bank_1_account_number`, `bank_2_account_number`, `bank_3_account_number`):

| Status | Action |
|---|---|
| Matches a registered bank | Funds need a manual push to the trading account. Escalate to a human agent for the funds team to check — include client ID, UTR, amount, date, source account. |
| Doesn't match any registered account | Transfer sent from an unlinked account. Per SEBI regulations, the amount will be reversed to the source bank within 2–3 days (per **A2**). Share **A9** unmapped transfer link. |

---

### Rule 6: Date Mismatch

When no transaction matches the client's stated date, use **amount-matching** on nearby dates — clients typically share either a screenshot or the amount.

1. Check the amount the client has mentioned in their screenshot or query.
2. Check if the same amount appears in `cashier_payin` on dates close to the stated date.
3. If a matching-amount transaction is found on a nearby date → apply Rule 2, 3, or 5 per the matched transaction's `transfer_mode` and `Status`.
4. If no matching-amount transaction is found on any nearby date → request a bank statement screenshot (amount, date, reference number) to investigate.

---

### Rule 7: Account Restrictions

Apply A3 per account/bank type.

**Dormant accounts:** If the account is dormant: dormancy does not restrict fund addition — all methods are available. Only trading and order placement are restricted. Inform the client that ReKYC is required to resume trading. Treat fund addition as unaffected by dormancy.

**Third-party / spouse:** Only bank accounts registered in the client's name and linked to their Zerodha account can be used for payins. Per SEBI regulations, transfers from third-party accounts are not accepted. Share the unmapped-transfer link from A9.

**IDFC 3-in-1 block:** If `idfc_3_in_1_status` = "Yes" → inform the client that the IDFC 3-in-1 block facility prevents adding funds from secondary bank accounts and direct them to disable it at console.zerodha.com/account/bank → "Disable IDFC 3-in-1 account." Share the IDFC link from A9.

---

### Rule 8: Payin Confirmed but "Not Visible"

1. Invoke `kite_margins` — authoritative source for available balance.
2. **Weekend payin:** Payin recorded in the ledger. On Monday, it appears under the Payin line on Kite (not in opening balance, which carries forward from Friday's close).
3. **Weekday payin:** Payin credited on the payin date/time with `bank_reference` available. Balance visible on Kite → Funds.
4. Invoke `ledger_report`: found → verify via Console ledger. Not found → apply A8 timing guidance.
5. Balance confirmed but client insists not visible → Privacy mode may be enabled on Kite (hides account details); disable via Kite → Settings.

---

### Rule 9: Balance Lower Than Expected / Negative

1. Confirm payin per Rule 8 format.
2. If orders exist on the payin date → orders placed that day reduced the available balance. If no orders on the payin date → do not mention trading.
3. Invoke `ledger_report` for: negative opening balance, AMC charges, NSE/BSE charges, trading debit obligations, delayed payment charges, prior QS payouts.
4. A pre-existing negative balance is adjusted against the new deposit, resulting in a lower current balance. Identify the specific reason from the ledger.
5. If the ledger doesn't explain the gap → escalate to a human agent.

**MTF margin shortfall:** If `ledger_report` shows MTF debits → account has an MTF margin shortfall. Uncleared shortfalls may trigger square-off of open MTF positions; an email notification is sent regarding this shortage.

---

### Rule 10: QS Check (Old Payin, Balance = ₹0)

1. Invoke `crux_qs_payouts` and `ledger_report` for QS between the payin date and today. If the client hasn't stated the payin date, match by amount instead (when the client has shared an amount).
2. QS found → the idle balance from the payin was transferred back to the client's bank account via Quarterly Settlement on the QS date.
3. No QS found → escalate to a human agent.

---

### Rule 11: Multiple Same-Day Transactions

**Detail the last 5 transactions in a single response.** Clients often retry multiple times when a payin fails — a broader window helps identify whether the failure is a consistent issue (same bank, same error code, etc.). Summarize any remaining transactions briefly.

-Apply Rule 2 or Rule 3 per transaction based on `transfer_mode` and `Status`. Address both successful AND failed/pending transactions — a success does not cancel explanation of a failure.

**>5 transactions:** Detail the 5 most recent. For the rest, summarize the count and direct the client to Kite → Funds for the full list, or to write back for details on a specific transaction.

**Multiple failed UPI:** Count of failed attempts, source bank, and date range. None credited. Any debited amounts refund to the source bank within 72 working hours (per **A1**).

---

### Rule 12: Escalation Triggers

Escalate to a human agent for the funds team to check (include transaction details) when:
- Bank success but Zerodha failed.
- U30 error.
- Cheque debited but no system entry — escalate immediately, no troubleshooting.
- Direct NEFT / IMPS / RTGS located via UTR re-query, matched to a registered bank account (Rule 5).

---

### Rule 13: Fresh Account Payin Failures

-Applies: `account_activation_date` within last 24h AND payin date = activation date. New accounts only — not REKYC or segment activation.

-Inform the client: your account was recently opened and it will take up to 24 working hours for the account to be active at the exchanges. Errors adding funds or placing orders are expected during this period. Please try again after 24 hours.

---

### Rule 14: Penny Drop / Test Deposit

-If customer asks about a ₹1 credit from "ZERODHA BR" via IMPS:

Inform the client: the ₹1 credit is a standard test deposit that occurs when creating a mandate or adding a bank account. It is normal and does not impact the account.

---

### Rule 15: Same-Day Withdrawal after Deposit

-If the client adds funds and asks about withdrawing the same day → same-day withdrawal is not permitted. A T+1 restriction applies; the withdrawal request can be placed from the next banking working day onwards.

---

### Rule 16: Bank Details Request

Share Zerodha's bank details from A4. Lead with Primary; provide Alternate only if the client requests a numeric account number or cannot use "ZERNSE". HDFC account holders can also use the eCMS facility per A9.
