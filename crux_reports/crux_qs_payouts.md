# crux_qs_payouts

## Description

WHEN TO USE:

- Customer asks about their quarterly settlement payout status or amount
- Customer asks when their next quarterly settlement will happen
- Customer asks why they weren't settled in a previous quarter
- Customer asks if they can opt out of or change their settlement frequency
- Customer asks about settlement happening monthly instead of quarterly
- Customer asks about moving funds to LIQUIDCASE to prevent settlement
- Customer says funds are not showing / not there / missing, and the cause may be a quarterly settlement payout
- Customer says funds were automatically withdrawn or transferred without their action

TRIGGER KEYWORDS: "quarterly settlement", "settlement", "when is settlement", "settlement date", "payout", "settled", "transfer back", "funds transferred", "LIQUIDCASE", "opt out settlement", "change settlement", "monthly settlement instead of quarterly", "funds not showing", "money not there", "where is my money", "funds not reflected", "automatically withdrawn", "auto withdrawn"

## Protocol

# QS PAYOUT PROTOCOL

## Knowledge Base

<knowledge_base>
<facts>
- Settlement is mandatory; frequency (monthly/quarterly) set at account opening, cannot be changed
- Transfers to PRIMARY bank account only, free of charge
- Inactive 30+ days in a month → settlement becomes monthly (applies to both preferences; reverts when active). Inactivity = no trades executed for 30+ calendar days. Segment activation status, KYC status, and account type do NOT determine inactivity — only trading activity does.
- Outstanding positions: 225% of EOD margins blocked, rest transferred
- Account opened after previous settlement date: no payout that quarter
- Bank transfer completes within 24 hours, statement emailed
- Bank rejections: funds credited back to Zerodha account, available for trading/withdrawal
- Primary bank details must exactly match bank records (Name, Account Number, IFSC)
</facts>

<settlement_dates>
First Friday of Jan/Apr/Jul/Oct (previous trading day if bank holiday)
</settlement_dates>

<bank_update_links>
<regular>https://support.zerodha.com/category/funds/adding-bank-accounts/primary-bank-account/articles/how-do-i-change-my-primary-bank-account-linked-with-zerodha</regular>
<nri>Courier account modification form (PDF) and bank proof to Zerodha. If Aadhaar-linked mobile, esign and submit via ticket. Refer to sample copy (PDF).</nri>
</bank_update_links>
</knowledge_base>

---

## Business Rules

### Rule 0: NRI PIS Early Gate (ALWAYS RUN FIRST)
**if:** `client_acc_type` from `get_all_client_data` = NRE PIS or NRO PIS
**then:** QS FOR NRI PIS ACCOUNT. ESCALATE TO NRI TEAM. Do NOT proceed with any QS processing.

### Rule 1: Settlement Non-Negotiable
**if:** Customer asks to opt out or change frequency
**then:** Settlement is mandatory; frequency set at account opening cannot be changed.

### Rule 2: Determine Settlement Type
**if:** Customer asks about a settlement payout or why it happened

Apply layered detection in order:
1. **Ledger text** contains "quarterly settlement (inactive)" → **INACTIVITY QS**
2. **Payout date** does NOT match `<settlement_dates>` (first Friday of Jan/Apr/Jul/Oct) → **INACTIVITY QS**
3. **If still ambiguous** (payout date matches `<settlement_dates>` + no "(inactive)" marker): call `kite_order_history` for the 30 calendar days before the payout date. If NO trades found → **INACTIVITY QS**. If trades found → **REGULAR QS**.
4. **Fallback**: If `kite_order_history` is unavailable or inconclusive → default to **REGULAR QS**, use general language accurate for both types.

For inactivity: explain 30+ day inactivity rule, mention it reverts when active.
If both conditions apply (inactive during regular QS period), mention inactivity first.

### Rule 3: New Account Exclusion
**if:** No payout last quarter AND account opened after previous settlement date
**then:** First payout will be next quarter.

### Rule 4: Bank Reference Sharing
**if:** Uppercase letters in bank reference → share with customer
**if:** All lowercase → say "Check your bank statement." Do NOT share.

### Rule 5: Outstanding Positions
**if:** Customer asks about fund retention or has outstanding positions
**then:** 225% of EOD margins blocked; remaining balance transferred.

### Rule 6: Protect Internal Fields
**NEVER expose:** `internal_status`, `company_segment_details`, `bank_response_status`, `remarks`
**NEVER share raw bank rejection reasons** from `remarks` (e.g., "NOCM Not Compliant", error codes).
**Instead use:** "We're processing your payout" / "Your bank is processing the transfer" / "rejected by your bank"

### Rule 7: Bank Rejection — Standard Accounts
**if:** Bank rejection AND NOT NRE/NRI/PIS account
**then:** Apply Rule 6 (never share remarks). Inform:
- Transfer of ₹[amount] on [date] was rejected by bank [share reference per Rule 4]
- Funds credited back on [reversal_date], available for trading/withdrawal
- Bank details must match: suggest CMR download (Console → Profile → CMR) and cross-check
- If mismatch: update via [refer to `<bank_update_links><regular>`]
- Next settlement on first Friday of [next quarter month per `<settlement_dates>`]

### Rule 8: QS Credited But Not Received
**if:** Customer says QS payout was completed/done but funds not received in bank account
**then:**
1. Share the transaction reference number (apply Rule 4 for uppercase/lowercase check)
2. Advise: "You can confirm this transaction with your bank using the provided reference number."
3. Add: "If the amount has not been credited, please share your bank statement for the settlement date so we can investigate."
