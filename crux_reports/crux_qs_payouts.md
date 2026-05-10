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
- Report their balance suddenly showing zero or reduced without any trade, withdrawal, or pledge action from their side — especially around known quarterly settlement dates
- Report money was debited or deducted from their Zerodha account automatically but not credited to their bank account
- See "inactive" in their ledger or statement and are confused about why money was deducted
- Report their quarterly settlement payout was rejected or failed due to bank issues (bank frozen, IFSC mismatch, bank closed, account details mismatch)
- Reference SEBI guidelines about unused funds being transferred to their bank account
- Received an email or notification about funds being transferred back but haven't received the money in their bank
- Are worried about settlement impacting their MTF positions, SIP mandates, or open orders
- Paste a settlement reference number and ask about fund status
- Ask about unused funds or unused balance being sent back to their bank

WHEN NOT TO USE:

Client has an open withdrawal request that failed or is delayed (use Funds-Payout tool instead)
Client is asking about trading P&L, brokerage charges, STT, or other trading-related deductions
Client is asking about a specific buy/sell transaction debit
Client's issue is about UPI or payment gateway failure while adding funds
Client is asking about DP charges, account opening charges, or AMC charges
Client is asking about a pledge or margin shortfall debit

TRIGGER KEYWORDS: "quarterly settlement", "settlement", "when is settlement", "settlement date", "payout", "settled", "transfer back", "funds transferred", "LIQUIDCASE", "opt out settlement", "change settlement", "monthly settlement instead of quarterly", "funds not showing", "money not there", "where is my money", "funds not reflected", "automatically withdrawn", "auto withdrawn", "balance showing zero suddenly", "balance became zero", "balance showing 0", "funds not credited to bank", "amount not credited to bank", "funds not received in bank", "amount not received in bank", "debited without action", "debited automatically", "amount deducted automatically", "deducted from account without", "money gone", "money lost", "money disappeared", "unused funds", "unused balance", "amount missing", "funds missing", "inactive", "inactivity", "SEBI", "SEBI guideline", "payout rejected", "settlement rejected", "transfer rejected by bank", "payout failed", "settlement failed", "IFSC", "bank frozen", "bank closed", "refund settlement amount", "settlement reference number"

TAGS: funds

## Protocol

# QS PAYOUT PROTOCOL

## Section A: Reference Data

### A1 — Settlement Fundamentals

- Settlement is mandatory; frequency (monthly/quarterly) set at account opening, cannot be changed.  
- Transfers to primary bank account only, free of charge.  
- Bank transfer completes within 24 hours; settlement statement emailed.  
- Bank rejections: funds credited back to Zerodha account, available for trading/withdrawal.  
- Primary bank details must exactly match bank records (Name, Account Number, IFSC).  
- Account opened after previous settlement date: no payout that quarter — first payout next quarter.

### A2 — Settlement Dates

First Friday of January, April, July, and October. If that Friday is a bank holiday, the previous trading day is used.

**April 2026 operational note:**  
- Clients with inactive accounts (no trades or fund additions for the last five days) will have funds transferred back on 18 April 2026.  
- Funds added back to the trading account before 17 April 2026 that remain unused will be settled back to the primary bank account per regulatory requirement.  
- Regular withdrawal requests placed on 17 April 2026 onwards will be processed on 18 April 2026.  
- Instant withdrawal is not available on 18 April 2026.

### A3 — Inactivity Rules

- Inactive 30+ calendar days in a month → settlement becomes monthly (applies to both monthly and quarterly preferences).  
- Reverts to original frequency when trading resumes.  
- Inactivity = no trades executed for 30+ calendar days.  
- Segment activation status, KYC status, and account type do not determine inactivity — only trading activity does.

### A4 — Outstanding Positions

- If client has outstanding positions: 225% of EOD margins blocked, remaining balance transferred.  
- Check `client_retention_dates` for the specific funds retained and breakdown for the client.

### A5 — Inactivity QS Detection Logic

Apply layered detection in this order:

1. `ledger_report` text contains "quarterly settlement (inactive)" → Inactivity QS.  
2. Payout date does not match **A2** settlement dates (first Friday of Jan/Apr/Jul/Oct, or any date listed in the **A2** operational note) → Inactivity QS.  
3. If still ambiguous (payout date matches **A2** \+ no "(inactive)" marker): call `kite_order_history` for the 30 calendar days before the payout date. No trades found → Inactivity QS. Trades found → Regular QS.  
4. Fallback: if `kite_order_history` is unavailable or inconclusive → default to Regular QS, use general language accurate for both types.

If both conditions apply (inactive during regular QS period), mention inactivity first.

### A6 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |  
|---|---|  
| Settlement date | Share when relevant |  
| Payout amount | Share when relevant |  
| Bank reference | Conditionally per **A7** |

**Non-shareable:**

| Field | Interpretation |  
|---|---|  
| `internal_status` | Internal status |  
| `company_segment_details` | Internal segment details |  
| `bank_response_status` | Internal bank response status |  
| `remarks` | Internal remarks — raw bank rejection reasons (e.g., "NOCM Not Compliant", error codes) never shared |

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

| Topic | Tool |  
|---|---|  
| QS retention breakdown (margin, obligation, max retention) | `client_retention_dates` |  
| QS payout entry on ledger | `ledger_report` |  
| QS facts (schedule, opt-out, LIQUIDCASE) | `ledger_report` — A4 (QS Facts) |  
| Instant withdrawal eligibility / regular withdrawal processing cutoffs | `withdrawal_request` — A2 (Instant Eligibility) and A3 (Processing Cutoffs) |

### A10 — Escalation Triggers

Escalate when:  
- NRI PIS account (NRE PIS or NRO PIS) — escalate to support agent, do not proceed with QS processing.  
- Bank rejection persists after client verifies bank details match.  
- Client provides bank statement showing no credit after QS completed status.

## Section B: Decision Flow

### Routing

```  
Route by scenario  
   ├─ NRI PIS account detected → escalate (STOP)  
   ├─ Opt out / change frequency request → Rule 1  
   ├─ Settlement payout query / why it happened → Rule 2  
   ├─ No payout last quarter, new account → Rule 3  
   ├─ Fund retention / outstanding positions → Rule 4  
   ├─ Bank rejection (standard account) → Rule 5  
   └─ QS credited but funds not received in bank → Rule 6  
```

### Fallback

If no matching scenario is found → escalate per **A10**.

## Section C: Rules

### Rule 1 — Settlement Non-Negotiable

1. Settlement is mandatory; frequency (monthly/quarterly) set at account opening, cannot be changed per **A1**.

### Rule 2 — Determine and Explain Settlement Type

1. Apply detection logic from **A5** to determine Regular QS or Inactivity QS.  
2. Regular QS → state settlement date and that it follows the regular schedule per **A2**.  
3. Inactivity QS → state settlement date, explain 30+ day inactivity triggered monthly settlement, reverts when trading resumes per **A3**.  
4. If both conditions apply (inactive during regular QS period), mention inactivity first.

### Rule 3 — New Account Exclusion

1. Confirm: no payout found for last quarter and account opened after previous settlement date.  
2. Inform client first payout will be on the next settlement date per **A2** and **A1**.

### Rule 4 — Outstanding Positions / Fund Retention

1. Explain: 225% of EOD margin requirement blocked for outstanding positions; remainder transferred to primary bank account per **A4**.  
2. For detailed retention breakdown, refer to `client_retention_dates` per **A9**.

### Rule 5 — Bank Rejection (Standard Accounts)

1. Apply field protection per **A6** — never share raw `remarks` or bank rejection reasons.  
2. Apply bank reference sharing per **A7** (uppercase → share; all lowercase → direct client to check bank statement).  
3. Communicate:  
   - Rejection amount, date, and bank reference per **A7**.  
   - Funds credited back to Zerodha account on reversal date, available for trading/withdrawal.  
   - Common cause: primary bank details on Zerodha don't match bank records — advise CMR download from Console → Profile → CMR to cross-check Name, Account Number, IFSC.  
   - If mismatch found: share bank update link per **A8**.  
   - Next settlement date per **A2**.  
   - April 2026 note: if rejection occurs around 17–18 April 2026 and client wants to withdraw reversed funds: instant withdrawal not available on 18 April 2026, regular withdrawal requests from 17 April onwards processed on 18 April 2026.

### Rule 6 — QS Credited But Not Received in Bank

1. Share the transaction reference number (apply **A7** for uppercase/lowercase check).  
2. If not credited, request client's bank statement for the settlement date to investigate.

---
