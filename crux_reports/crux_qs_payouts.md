# crux_qs_payouts

## Description

WHEN TO USE:

When clients:
- Ask about their quarterly settlement payout status or amount
- Ask when their next quarterly settlement will happen
- Ask why they weren't settled in a previous quarter
- Ask if they can opt out of or change their settlement frequency
- Ask about settlement happening monthly instead of quarterly
- Ask about moving funds to LIQUIDCASE to prevent settlement
- Report funds not showing / not there / missing, and the cause may be a quarterly settlement payout
- Report funds were automatically withdrawn or transferred without their action

TRIGGER KEYWORDS: "quarterly settlement", "settlement", "when is settlement", "settlement date", "payout", "settled", "transfer back", "funds transferred", "LIQUIDCASE", "opt out settlement", "change settlement", "monthly settlement instead of quarterly", "funds not showing", "money not there", "where is my money", "funds not reflected", "automatically withdrawn", "auto withdrawn"

## Protocol

# QS PAYOUT PROTOCOL


### A1 — Settlement Fundamentals

- Settlement is mandatory; frequency (monthly/quarterly) set at account opening, cannot be changed.
- Transfers to primary bank account only, free of charge.
- Bank transfer completes within 24 hours; settlement statement emailed.
- Bank rejections: funds credited back to Zerodha account, available for trading/withdrawal.
- Primary bank details must exactly match bank records (Name, Account Number, IFSC).
- Account opened after previous settlement date: no payout that quarter — first payout next quarter.

### A2 — Settlement Dates

First Friday of January, April, July, and October. If that Friday is a bank holiday, the previous trading day is used.

### A3 — Inactivity Rules

- Inactive 30+ calendar days in a month → settlement becomes monthly (applies to both monthly and quarterly preferences).
- Reverts to original frequency when trading resumes.
- Inactivity = no trades executed for 30+ calendar days.
- Segment activation status, KYC status, and account type do not determine inactivity — only trading activity does.

### A4 — Outstanding Positions

- If client has outstanding positions: 225% of EOD margins blocked, remaining balance transferred.

### A5 — Inactivity QS Detection Logic

Apply layered detection in this order:

1. Ledger text contains "quarterly settlement (inactive)" → **Inactivity QS**.
2. Payout date does not match **A2** settlement dates (first Friday of Jan/Apr/Jul/Oct) → **Inactivity QS**.
3. If still ambiguous (payout date matches **A2** + no "(inactive)" marker): call `kite_order_history` for the 30 calendar days before the payout date. No trades found → **Inactivity QS**. Trades found → **Regular QS**.
4. Fallback: if `kite_order_history` is unavailable or inconclusive → default to **Regular QS**, use general language accurate for both types.

If both conditions apply (inactive during regular QS period), mention inactivity first.

### A6 — Field Rules

**Shareable with client:** settlement date, payout amount, bank reference (conditionally per **A7**).

**Internal reasoning only (never share with client):** `internal_status`, `company_segment_details`, `bank_response_status`, `remarks`.

Raw bank rejection reasons from `remarks` (e.g., "NOCM Not Compliant", error codes) are never shared with the client.

**Client-facing status phrases — use only these:**

| Situation | Say |
|---|---|
| Payout in progress | "We're processing your payout" |
| Transfer in progress | "Your bank is processing the transfer" |
| Bank rejected | "rejected by your bank" |

### A7 — Bank Reference Sharing Rule

| Reference Format | Action |
|---|---|
| Contains uppercase letters | Share with customer |
| All lowercase | Say "Check your bank statement." Not for client use. |

### A8 — Bank Update Links

| Account Type | Update Process |
|---|---|
| Regular | https://support.zerodha.com/category/funds/adding-bank-accounts/primary-bank-account/articles/how-do-i-change-my-primary-bank-account-linked-with-zerodha |
| NRI | Courier account modification form (PDF) and bank proof to Zerodha. If Aadhaar-linked mobile, esign and submit via ticket. Refer to sample copy (PDF). |

### A9 — Cross-Reference Protocols

| Topic | Refer to |
|---|---|
| QS retention breakdown (margin, obligation, max retention) | Client Retention Dates protocol |
| QS payout entry on ledger | Ledger Report protocol |
| QS facts (schedule, opt-out, LIQUIDCASE) | Ledger Report protocol — A4 (QS Facts) |

### A10 — Escalation Triggers

Escalate when:
- NRI PIS account (NRE PIS or NRO PIS) — escalate to support agent, do not proceed with QS processing.
- Bank rejection persists after client verifies bank details match.
- Client provides bank statement showing no credit after QS completed status.


### Preflight (run on every query)

1. Call `get_all_client_data` → check `client_acc_type`.
2. **NRI PIS gate:** If `client_acc_type` = NRE PIS or NRO PIS → STOP. Escalate to support agent. Do not proceed with any QS processing.
3. Fetch relevant QS/ledger data for the settlement period.
4. Apply field protection per **A6** — identify shareable vs internal-only fields.
5. Determine settlement type using the detection logic in **A5**.
6. Format amounts with ₹ and Indian comma notation. Format dates as DD MMM YYYY.

### Routing Tree

```
Query relates to QS payout →
│
├─ NRI PIS account detected in preflight
│  → Escalate to support agent (STOP)
│
├─ Client asks to opt out or change frequency
│  → Rule 1
│
├─ Client asks about a settlement payout or why it happened
│  → Rule 2
│
├─ No payout last quarter, new account
│  → Rule 3
│
├─ Client asks about fund retention / outstanding positions
│  → Rule 4
│
├─ Bank rejection (standard account)
│  → Rule 5
│
├─ QS credited but funds not received in bank
│  → Rule 6
│
└─ No matching scenario
   → escalate per A10
```

### Scope

- Address: QS payout status, settlement type, bank rejections, fund retention, and new account exclusion.

### Fallback

If no matching scenario is found → escalate per **A10**.


### Rule 1 — Settlement Non-Negotiable

1. Respond: "Settlement is mandatory. The frequency (monthly or quarterly) is set at account opening and cannot be changed." (Per **A1**.)

### Rule 2 — Determine and Explain Settlement Type

1. Apply the detection logic from **A5** to determine if this is a Regular QS or Inactivity QS.
2. **Regular QS:** "A quarterly settlement was processed on [date] as per the regular schedule. Settlement happens on the first Friday of January, April, July, and October." (Per **A2**.)
3. **Inactivity QS:** "A settlement was processed on [date] because there was no trading activity in your account for 30+ days. When an account is inactive for 30+ calendar days, the settlement frequency shifts to monthly. Once you resume trading, it will revert to your original frequency." (Per **A3**.)
4. If both conditions apply (inactive during regular QS period), mention inactivity first.

### Rule 3 — New Account Exclusion

1. Confirm: no payout found for last quarter and account was opened after the previous settlement date.
2. Respond: "Your account was opened after the last settlement date. Your first payout will be on [next settlement date per **A2**]." (Per **A1**.)

### Rule 4 — Outstanding Positions / Fund Retention

1. Respond: "If you have outstanding positions, 225% of your EOD margin requirement is blocked to cover them. The remaining balance is transferred to your primary bank account." (Per **A4**.)
2. For detailed retention breakdown (margin, obligation, max retention), refer to the Client Retention Dates protocol (per **A9**).

### Rule 5 — Bank Rejection (Standard Accounts)

1. Apply field protection per **A6** — never share raw `remarks` or bank rejection reasons.
2. Apply bank reference sharing per **A7** (uppercase → share; all lowercase → "Check your bank statement").
3. Respond:
   - "The transfer of ₹[amount] on [date] was rejected by your bank [share reference per **A7** if applicable]."
   - "The funds have been credited back to your Zerodha account on [reversal_date] and are available for trading or withdrawal."
   - "Bank rejections usually happen when the primary bank details on your Zerodha account don't match your bank's records. Please download your CMR from Console → Profile → CMR and cross-check your Name, Account Number, and IFSC."
   - If mismatch found: "You can update your primary bank details here: [**A8** regular link]."
   - "Your next settlement will be on the first Friday of [next quarter month per **A2**]."

### Rule 6 — QS Credited But Not Received in Bank

1. Share the transaction reference number (apply **A7** for uppercase/lowercase check).
2. Respond: "You can confirm this transaction with your bank using the provided reference number."
3. Add: "If the amount has not been credited, please share your bank statement for the settlement date so we can investigate."

