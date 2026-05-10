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

---

## Section A: Reference Data

### A1 — Gift Fundamentals

- Gift flow: Sender creates → Receiver gets SMS/email → Receiver accepts → Sender approves with TPIN → Beneficiary addition on CDSL → CDSL sets up off-market transfer → Sender completes OTP verification → Stocks transferred.  
- Stocks, ETFs, MF, and gold bonds between two Zerodha accounts can be gifted.  
- MF gifting: done via console.zerodha.com/gift (separate from Kite stock gifting).  
- Unsettled shares cannot be gifted.  
- Dormant account cannot gift — must complete re-KYC first.  
- Required input: Gifted By (sender Client ID) or Claimed By (receiver Client ID) — at least one. Optional: From/To Date.

### A2 — Charges

- Gift charges: ₹25 per security per transaction \+ 18% GST.  
- Charges debited from the sender's trading account.  
- Gift won't process if sender has a negative balance.  
- Example: gifting 3 different stocks in one transaction = ₹75 \+ 18% GST.

### A3 — Timelines

| Event | Timeline |  
|---|---|  
| CDSL beneficiary verification email | Sent between 3 PM and 5 PM on trading days |  
| CDSL OTP verification email/SMS | Sent at 5 PM on the same trading day |  
| OTP completion deadline | 8 PM same day — if missed, the gift request fails and the entire process must be restarted with a fresh gift request |  
| Approval cutoff | If sender approves after 2 PM, CDSL email comes next trading day |  
| Receiver acceptance deadline | 7 days from gift creation — request expires if not accepted |

### A4 — Status Meanings

| Status | Meaning |  
|---|---|  
| Created | Gift request created; waiting for receiver to accept (7-day window) |  
| Accepted | Receiver accepted; sender needs to approve using CDSL TPIN |  
| Approved | Sender approved; beneficiary addition and CDSL verification in progress |  
| Processing | Beneficiary addition done; sender needs to complete CDSL OTP verification by 8 PM |  
| Failed | Gift request has failed |  
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

### A9 — Escalation Triggers

Escalate when any of the following occur:  
- Status = Stocks Transferred but receiver cannot see shares after 2+ trading days.  
- Stocks transferred but buy average not updated after 3+ working days.  
- Gift request fails repeatedly despite completing all steps correctly.

Include in escalation: client ID (sender/receiver), creation date, status, items, and the specific issue.

---

## Section B: Decision Flow

### Routing

```  
Query relates to stock gift →  
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
└─ Data mismatch / no root cause found  
   → Rule 10 (Escalation)  
```

---

## Section C: Rules

### Rule 1 — Gift Status Check

1. Find the matching gift request.  
2. Translate the status using A4.  
3. For Approved status: check `modified` timestamp internally per A3. If after 2 PM, CDSL email comes next trading day.

### Rule 2 — Gift Failed: Diagnose and Retry

Failure causes:  
- Beneficiary not added on CDSL or verification email not completed between 3 PM and 5 PM (per A3).  
- CDSL OTP verification not completed by 8 PM (per A3).

Retry: Place a fresh gift request. If no CDSL beneficiary email received, use A7 link between 3 PM and 5 PM. Complete OTP by 8 PM.

### Rule 3 — CDSL Email Not Received

Check `modified` timestamp internally per A3:  
- Approved after 2 PM: CDSL email comes next trading day.  
- Approved before 2 PM and no email by 5 PM: manually add beneficiary via A7 link. OTP arrives at 5 PM, complete by 8 PM.

### Rule 4 — Beneficiary Already Added

If receiver's demat account was already added as a beneficiary from a previous transfer, skip beneficiary addition step. CDSL OTP arrives at 5 PM, complete by 8 PM (per A3).

### Rule 5 — Gifted Stocks Not Visible in Holdings

- Confirm status = Stocks Transferred (per A4).  
- If 2+ trading days have passed and stocks still not visible → ESCALATE TO HUMAN AGENT.  
- Invoke `console_eq_holdings`.

### Rule 6 — Discrepancy Mark on Gifted Stocks

- Normal for recently gifted stocks (per A5).  
- If discrepancy persists after 3 working days → ESCALATE TO HUMAN AGENT.

### Rule 7 — Buy Average Not Updated

- Confirm 3+ working days since transfer (per A5).  
- If still N/A or incorrect → ESCALATE TO HUMAN AGENT.  
- Invoke `console_eq_external_trades`.

### Rule 8 — Gift Charges

- Charges per A2.  
- If sender balance is negative → see Rule 9.

### Rule 9 — Sender Balance Negative

- Gift cannot process if sender's trading account balance is negative (per A2).  
- Sender needs to add funds to cover transfer charges.  
- Balance updates next day after funds are added.

### Rule 10 — Escalation

ESCALATE TO HUMAN AGENT when no root cause is identified after checking all relevant rules. Include details per A9.
