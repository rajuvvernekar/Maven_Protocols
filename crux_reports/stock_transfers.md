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

TAGS: demat

## Protocol

# STOCK TRANSFER PROTOCOL

---

## Section A: Reference Data

### A1 — Transfer Fundamentals

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

### A4 — Status Translations

| Internal Status | Client-Facing Communication |
|---|---|
| Pending | Transfer request is pending execution |
| Stocks Transferred | Transfer has been completed. Stocks will be visible in the receiver's account within 24 working hours |
| Failed | Transfer request has failed |

### A5 — Transfer Failure Reasons

| Reason | Client-Facing Explanation |
|---|---|
| OTP not completed | CDSL OTP verification was not completed by the 8 PM deadline. The transfer process needs to be initiated again |
| Lock-in / pledge / frozen | Stocks are under lock-in, pledge, or frozen status. Stocks need to be unpledged, or the lock-in period must be over, or the demat account must be unfrozen before the transfer can be initiated |
| Negative / zero balance | Transfer request will not be processed if the Zerodha account balance is negative. If funds are added today, the funds statement balance will be updated the following day and the transfer request will only be processed then |
| Dormant account | Shares cannot be transferred if the Zerodha account is dormant. Client must complete the Re-KYC process — Invoke `account_modification_report` to guide the client through the Re-KYC process |

### A6 — Buy Average & Discrepancy

- Buy average is auto-updated within 3 working days for stocks transferred between primary and secondary accounts.
- Stocks may show as discrepant (discrepancy mark or incorrect buy average) in the target account until the update completes.
- Invoke `console_eq_external_trades` for transfer entries related to buy average calculation.

### A7 — Field Rules

**Shareable with client:**

| Field | Interpretation |
|---|---|
| `creation` | Share as date (not timestamp) |
| `transaction_type` | Share as "direction" — do not use the raw field name |
| `status` | Translate per A4 before sharing |
| `execution_date` | Date the transfer was executed |
| `items` | Stocks and quantities in the transfer |

**Non-shareable:**

| Field | Interpretation |
|---|---|
| `name` | Internal transfer ID |
| `modified` | Last update timestamp |
| `from_account` | Source demat account |
| `to_account` | Destination demat account |
| `secondary_client_id` | Internal identifier for the counterpart account |
| `remarks` | Internal remarks |
| `client_id` | Internal client identifier |

---

## Section B: Decision Flow

### Routing

```
Query relates to demat transfer →
│
├─ Client asks about transfer status
│  ├─ Pending → Rule 1
│  ├─ Stocks Transferred → Rule 1
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

### Fallback

If no root cause is identified after checking all relevant rules → ESCALATE TO HUMAN AGENT

---

## Section C: Rules

### Rule 1 — Transfer Status Check

1. Look up by Client ID and optional date range.
2. Translate the status using **A4** and communicate the appropriate status meaning to the client.
3. For Failed status → route to Rule 2.

### Rule 2 — Transfer Failed: Diagnose and Retry

1. Status is Failed — present the applicable failure reason and its meaning from **A5**.
2. Client can retry by placing a new transfer request on Kite and ensuring OTP verification is completed by 8 PM (per **A3**).
3. If client confirms they completed OTP and balance was sufficient → ESCALATE TO HUMAN AGENT.

### Rule 3 — Transferred Stocks Not Visible

1. Confirm status = Stocks Transferred (per **A4**).
2. Stocks should be visible within 24 working hours of transfer completion.
3. If more than 24 working hours have passed since completion and stocks are still not visible → ESCALATE TO HUMAN AGENT.

### Rule 4 — Buy Average After Transfer

1. Buy average is auto-updated within 3 working days post-transfer (per **A6**). Stocks may show discrepancy or incorrect buy average during this period.
2. If more than 3 working days have passed and buy average is still incorrect → ESCALATE TO HUMAN AGENT. Invoke `console_eq_external_trades` for entry reference.

### Rule 5 — Transfer Charges

1. Transfer charge is ₹13 + 18% GST = ₹15.34 per transaction, regardless of number of shares or stock value (per **A2**).

### Rule 6 — Escalation

1. ESCALATE TO HUMAN AGENT when any of the following occur:
   - Status = Stocks Transferred but stocks not visible in target account after 24 working hours.
   - Buy average not updated or incorrect after 3+ working days post-transfer.
   - Transfer failed despite client completing OTP verification and having sufficient balance.
   - No root cause identified after checking all relevant rules.
2. Include in escalation: client ID, creation date, direction, status, items, and the specific issue.
