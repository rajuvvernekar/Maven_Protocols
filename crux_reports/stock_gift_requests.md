# stock_gift_requests

## Description

WHEN TO USE:

When clients:
- Ask about the status of a stock gift request (sending or receiving)
- Report gift request failed and want to know why
- Report they didn't receive CDSL email for beneficiary verification or OTP
- Report gifted stocks not visible in receiver's holdings
- Ask why gift shows as "Failed" or "Cancelled"
- Report buy average not updated for received gift stocks
- Report discrepancy mark on gifted stocks in holdings
- Ask about gift request timeline (creation, approval, transfer)

TRIGGER KEYWORDS: "gift stock", "gift request", "gift status", "gift failed", "gift cancelled", "gifted shares", "stock transfer gift", "gift not received", "accept gift", "approve gift", "beneficiary gift", "CDSL OTP gift", "gift processing", "gift buy average", "discrepant gifted stock", "stocks transferred gift"

TAGS: general

## Protocol


# STOCK GIFT REQUESTS PROTOCOL

## Section A: Reference Data

### A1 — Gift Fundamentals

- Gift flow: Sender creates → Receiver gets SMS/email → Receiver accepts → Sender approves with TPIN → Beneficiary addition on CDSL → CDSL sets up off-market transfer → Sender completes OTP verification → Stocks transferred.
- Stocks, ETFs, MF, and gold bonds between two Zerodha accounts can be gifted.
- MF gifting: done via console.zerodha.com/gift (separate from Kite stock gifting).
- Unsettled shares cannot be gifted.
- Dormant account cannot gift — must complete re-KYC first.
- Required input: Gifted By (sender Client ID) or Claimed By (receiver Client ID) — at least one. Optional: From/To Date.
- Receiver can be a joint account. For a joint-account receiver, the primary holder of the receiver's demat must be added as the beneficiary owner (BO) in CDSL.
- The sender completes the beneficiary (BO) addition on CDSL — the beneficiary added is the gift receiver (compulsory).

### A2 — Charges

- Gift charges: ₹25 per security per transaction + 18% GST.
- Charges debited from the sender's trading account.
- Gift won't process if sender has a negative balance.
- Example: gifting 3 different stocks in one transaction = ₹75 + 18% GST.

### A3 — Timelines

| Event | Timeline |
|---|---|
| CDSL beneficiary verification email | Sent to the sender between 3 PM and 5 PM on trading days (only if the receiver is not already a beneficiary). If the sender misses it, CDSL sends a one-time email to the receiver |
| CDSL OTP verification email/SMS | Sent at 5 PM on the same trading day |
| OTP completion deadline | 8 PM same day — if missed, the gift request fails and the entire process must be restarted with a fresh gift request |
| Approval cutoff | If sender approves after 2 PM, CDSL email comes next trading day |
| Gift request processing window | If approved before 2 PM, the request is processed on our end between 5 PM and 6 PM the same trading day |
| Final status update (Transferred / Failed) | The Transferred/Failed status itself updates the next day around 12 PM — until then the status may still show "Processing" even after a successful OTP |
| Receiver acceptance deadline | 7 days from gift creation — request expires if not accepted |

### A4 — Status Meanings

| Status | Meaning |
|---|---|
| Created | Gift request created; waiting for receiver to accept (7-day window) |
| Accepted | Receiver accepted; sender needs to approve using CDSL TPIN — TPIN authorization is required even if POA/DDPI is enabled on the sender's account |
| Approved | Sender approved; beneficiary addition and CDSL verification in progress |
| Processing | File fetched and processed (after the 2 PM cutoff); beneficiary addition email/SMS sent to the sender (skipped if the receiver was already added as a beneficiary from a previous transfer); sender needs to complete CDSL OTP verification by 8 PM |
| Failed | Gift request has failed (e.g., sender did not complete the CDSL OTP by 8 PM) |
| Cancelled | Gift request was cancelled by the client |
| Stocks Transferred | Gift successfully transferred; stocks visible in receiver's holdings by next trading day |

### A5 — Buy Average & Pricing

- Buy average for receiver: updated within 3 working days. Entry price = closing price on transfer date.
- Exit price for sender: closing price on transfer date.
- Recently gifted stocks may show a red exclamation / discrepancy mark in holdings — this is normal and resolves when buy average is updated.

### A6 — Field Rules

**Shareable with client:**

| Field | Interpretation |
|---|---|
| `creation` | Share as date and time |
| `status` | Current status of the gift request |
| `items` | Stock names and quantities in the gift |

**Non-shareable:**

| Field | Interpretation |
|---|---|
| `modified` | Last update timestamp |
| `sender_fullname` | Full name of the gift sender |
| `gifted_by` | Sender's client ID |
| `receiver_fullname` | Full name of the gift receiver |
| `receiver_email` | Receiver's email address |
| `receiver_phone_number` | Receiver's phone number |
| `claimer_fullname` | Full name of the person who claimed the gift |
| `claimed_by` | Claimer's client ID |

### A7 — CDSL Links

| Purpose | URL |
|---|---|
| Manual beneficiary addition (if CDSL email not received) | https://www.cdslindia.com/Authentication/OTP.aspx?id=B |

### A8 — Beneficiary Verification Steps (Sender)

1. Open the link in the CDSL email (or the A7 link).
2. Enter the sender's PAN or 16-digit demat account number.
3. Click Submit.
4. Tick the beneficiary details → Generate OTP.
5. Enter the OTP → Accept.
6. Click OK.

## Section B: Decision Flow

### Routing

```
Route by scenario
│
├─ Client asks about gift request status
│  → Rule 1
│
├─ Gift failed (status = Failed)
│  → Rule 2
│
├─ CDSL email not received (beneficiary or OTP)
│  → Rule 3
│
├─ Beneficiary already added from previous gift
│  → Rule 4
│
├─ Gifted stocks not visible in receiver's holdings
│  → Rule 5
│
├─ Discrepancy mark on gifted stocks
│  → Rule 6
│
├─ Buy average not updated / shows N/A
│  → Rule 7
│
├─ Gift charges inquiry / unexpected charge
│  → Rule 8
│
├─ Gift not processing — sender balance negative
│  → Rule 9
│
├─ Gift to a joint account (receiver)
│  → Rule 10
│
└─ Data mismatch / no root cause found
   → escalate
```

---

## Section C: Rules

### Rule 1 — Gift Status Check

1. Find the matching gift request.
2. Translate the status using A4.
3. For Approved status: check `modified` timestamp internally per A3. If after 2 PM, CDSL email comes next trading day.
4. The Transferred/Failed status updates only the next day around 12 PM (per A3). If the status still shows "Processing" before then — even after a successful OTP — this is normal; do not treat it as failed or escalate.

### Rule 2 — Gift Failed: Diagnose and Retry

Failure causes:
- Beneficiary not added on CDSL or verification email not completed between 3 PM and 5 PM (per A3).
- CDSL OTP verification not completed by 8 PM (per A3).

Retry: Place a fresh gift request. If no CDSL beneficiary email received, use A7 link between 3 PM and 5 PM. Complete OTP by 8 PM.

### Rule 3 — CDSL Email Not Received

Check `modified` timestamp internally per A3:
- Approved after 2 PM: CDSL email comes next trading day.
- Approved before 2 PM and no email by 5 PM: the sender adds the beneficiary via the A7 link (steps in A8). OTP arrives at 5 PM, complete by 8 PM.

### Rule 4 — Beneficiary Already Added

If receiver's demat account was already added as a beneficiary from a previous transfer, skip beneficiary addition step. CDSL OTP arrives at 5 PM, complete by 8 PM (per A3).

### Rule 5 — Gifted Stocks Not Visible in Holdings

- Confirm status = Stocks Transferred (per A4). Note the status itself updates only the next day around 12 PM (per A3) — before then it may still show "Processing".
- If 2+ trading days have passed and stocks still not visible → escalate.
- Invoke `console_eq_holdings`.

### Rule 6 — Discrepancy Mark on Gifted Stocks

- Normal for recently gifted stocks (per A5).
- If discrepancy persists after 3 working days → escalate.

### Rule 7 — Buy Average Not Updated

- Confirm 3+ working days since transfer (per A5).
- If still N/A or incorrect → escalate.
- Invoke `console_eq_external_trades`.

### Rule 8 — Gift Charges

- Charges per A2.
- If sender balance is negative → see Rule 9.

### Rule 9 — Sender Balance Negative

- Gift cannot process if sender's trading account balance is negative (per A2).
- Sender needs to add funds to cover transfer charges.
- Balance updates next day after funds are added.

### Rule 10 — Joint Account Receiver

- Gifting to a joint-account receiver is supported. The primary holder of the receiver's demat must be added as the beneficiary owner (BO) in CDSL.
