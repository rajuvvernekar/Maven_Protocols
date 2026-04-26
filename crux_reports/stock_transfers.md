# stock_transfers

## Description

WHEN TO USE:

When clients:
- Ask about the status of a stock transfer between primary and secondary demat accounts
- Report transfer failed and want to know why
- Report transferred stocks not visible in target account
- Report buy average wrong after transferring stocks back from secondary to primary
- Ask about pending transfer or execution date
- Ask about transfer history (which stocks, when, direction, status)

TRIGGER KEYWORDS: "primary to secondary transfer", "secondary to primary transfer", "stock transfer status", "transfer failed", "transfer pending", "inter-account transfer", "secondary demat transfer", "transfer request status", "stocks transferred between accounts", "transfer not showing"

## Protocol

# STOCK TRANSFER PROTOCOL

—

### A1 — Transfer Fundamentals

- This report tracks transfers between a client's own primary and secondary Zerodha demat accounts only.
- Required input: Client ID. Optional: From/To Date, Transaction Type (Primary to Secondary / Secondary to Primary).
- Transfer requires CDSL TPIN authorization and OTP verification.
- Stocks under lock-in, pledge, or frozen status cannot be transferred.
- Cannot transfer if trading account balance is negative or account is dormant.

### A2 — Charges

- Transfer charge: ₹13 + 18% GST = ₹15.34 per transfer transaction.
- Applies per transaction regardless of the number of shares or stock value being transferred.

### A3 — Timelines

| Event | Timeline |
|---|---|
| CDSL verification email | Sent between 3 PM and 5 PM on trading days |
| OTP completion deadline | 8 PM same day — if missed, transfer fails |
| Same-day processing cutoff | Submitted before 6 PM on a trading day → processed same day |
| Next-day processing | Submitted after 6 PM → execution date is next working day |
| Stocks visible in target account | Within 24 hours of completion |
| Buy average auto-update | Within 3 working days of transfer |

### A4 — Status Translations

| Internal Status | Client-Facing Communication |
|---|---|
| Pending | "Your transfer request from [creation date] is pending execution. Transfers submitted before 6 PM are processed the same trading day. If submitted after 6 PM, the execution date will be the next working day." |
| Stocks Transferred | "Your transfer of [items] from [direction] was completed on [execution_date]. The stocks will be visible in the target account within 24 hours." |
| Failed | "Your stock transfer request from [creation date] has failed." (See Rule 2 for diagnosis.) |

### A5 — Transfer Failure Reasons

| Reason | Client-Facing Explanation |
|---|---|
| OTP not completed | "CDSL OTP verification was not completed by the 8 PM deadline." |
| Lock-in / pledge / frozen | "The stocks are under lock-in, pledge, or frozen status and cannot be transferred." |
| Negative / zero balance | "The trading account has a negative or zero balance." |
| Dormant account | "The account is in dormant status." |

### A6 — Buy Average & Discrepancy

- Buy average is auto-updated within 3 working days for stocks transferred between primary and secondary accounts.
- Stocks may show as discrepant (discrepancy mark or incorrect buy average) in the target account until the update completes.
- Transfer entries appear in Console EQ External Trades for buy average calculation.

### A7 — Field Rules

**Shareable with client:** `creation` (as date), `transaction_type` (as "direction"), `status` (translated per **A4**), `execution_date`, `items` (stocks and quantities).

**Internal reasoning only (never share with client):** `modified`, `name` (transfer ID), `client_id`, `secondary_client_id`, `from_account`, `to_account`, `remarks`.
tr
### A8 — Cross-Reference Protocols

| Topic | Refer to |
|---|---|
| Verify transferred stocks in target account (may show discrepancy initially) | Console EQ Holdings |
| Transfer entries for buy average calculation | Console EQ External Trades |

### A9 — Escalation Triggers (Consolidated)

Escalate when any of the following occur:
- Status = Stocks Transferred but stocks not visible in target account after 24 hours.
- Buy average not updated or incorrect after 3+ working days post-transfer.
- Transfer failed despite client completing OTP verification and having sufficient balance.

Include in escalation: client ID, creation date, direction, status, items, and the specific issue.


### Preflight (run on every query)

1. Fetch the transfer report using client ID and optional date range/transaction type.
2. Apply field protection per **A7** — identify shareable vs internal-only fields.
3. Translate the status using **A4**.
4. Format amounts with ₹ and Indian comma notation. Format dates as DD MMM YYYY.

### Routing Tree

```
Query relates to demat transfer →
│
├─ Client asks about transfer status
│  ├─ Pending → Rule 1 (Pending guidance)
│  ├─ Stocks Transferred → Rule 1 (Completion confirmation)
│  └─ Failed → Rule 2 (Diagnose)
│
├─ Transferred stocks not visible in target account
│  → Rule 3
│
├─ Buy average wrong / discrepancy after transfer
│  → Rule 4
│
├─ Transfer charges inquiry
│  → Rule 5
│
└─ Data mismatch / no root cause found
   → Rule 6 (Escalation)
```

### Scope

- Address: transfer status, failure diagnosis, stock visibility, buy average updates, and transfer charges.

### Fallback

If no root cause is identified after checking all relevant rules → escalate per Rule 6.


### Rule 1 — Transfer Status Check

1. Look up by Client ID and optional date range.
2. Translate the status using **A4** and respond with the appropriate client-facing communication.
3. For Failed status → route to Rule 2.

### Rule 2 — Transfer Failed: Diagnose and Retry

1. Respond: "Your stock transfer request from [creation date] has failed." Present the applicable reasons from **A5**.
2. Retry guidance: "To retry, place a new transfer request on Kite and ensure OTP verification is completed by 8 PM." (Per **A3**.)
3. If client confirms they completed OTP and balance was sufficient → escalate per Rule 6.

### Rule 3 — Transferred Stocks Not Visible

1. Confirm: status = Stocks Transferred (per **A4**).
2. Respond: "Transferred stocks should be visible within 24 hours of completion. If the transfer was completed today, please check again tomorrow." (Per **A3**.)
3. If more than 24 hours since completion: "If it's been more than 24 hours and the stocks are still not visible, we'll investigate." → escalate per Rule 6.

### Rule 4 — Buy Average After Transfer

1. Respond using **A6**: "The buy average for stocks transferred between primary and secondary accounts is automatically updated within 3 working days. During this period, the stocks may show a discrepancy mark or incorrect buy average."
2. If more than 3 working days: "If the buy average is still incorrect after 3 working days, please let us know with the specific stocks and expected buy average." → escalate per Rule 6. Reference Console EQ External Trades (per **A8**) for entry correction.

### Rule 5 — Transfer Charges

1. Respond using **A2**: "The transfer charge is ₹13 + 18% GST = ₹15.34 per transfer transaction between your primary and secondary demat accounts. This charge applies per transaction regardless of the number of shares or stock value being transferred."

### Rule 6 — Escalation

Escalate when any trigger in **A9** is met.

Include in escalation: client ID, creation date, direction, status, items, and the specific issue.

