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

## Protocol

# STOCK GIFT REQUESTS PROTOCOL

### A1 — Gift Fundamentals

- Gift flow: Sender creates → Receiver gets SMS/email → Receiver accepts → Sender approves with TPIN → Beneficiary addition on CDSL → CDSL sets up off-market transfer → Sender completes OTP verification → Stocks transferred.
- Stocks, ETFs, MF, and gold bonds between two Zerodha accounts can be gifted.
- MF gifting: done via console.zerodha.com/gift (separate from Kite stock gifting).
- Unsettled shares cannot be gifted.
- Dormant account cannot gift — must complete re-KYC first.
- Required input: Gifted By (sender Client ID) or Claimed By (receiver Client ID) — at least one. Optional: From/To Date.

### A2 — Charges

- Gift charges: ₹25 per security per transaction + 18% GST (standard off-market transfer charges).
- Charges debited from the sender's trading account.
- Gift won't process if sender has a negative balance.
- Example: gifting 3 different stocks in one transaction = ₹75 + 18% GST.

### A3 — Timelines

| Event | Timeline |
|---|---|
| CDSL beneficiary verification email | Sent between 3 PM and 5 PM on trading days |
| CDSL OTP verification email/SMS | Sent at 5 PM on the same trading day |
| OTP completion deadline | 8 PM same day — if missed, entire process must restart |
| Approval cutoff | If sender approves after 2 PM, CDSL email comes next trading day |
| Receiver acceptance deadline | 7 days from gift creation — request expires if not accepted |

### A4 — Status Translations

| Internal Status | Client-Facing Communication | Notes |
|---|---|---|
| Created | "Your gift request was created on [creation date]. It's waiting for the receiver to accept it. The receiver has 7 days to accept." | — |
| Accepted | "The receiver has accepted the gift. The sender now needs to approve it using CDSL TPIN." | — |
| Approved | "The sender has approved the gift. Beneficiary addition and CDSL verification are in progress." | Check `modified` timestamp internally: if after 2 PM, CDSL email comes next trading day. |
| Processing | "The gift is being processed. The sender needs to complete CDSL OTP verification by 8 PM today." | Auto-converts from Approved at ~2 PM. Beneficiary addition and CDSL OTP pending. |
| Failed | "Your gift request for [items] created on [creation date] has failed." | See Rule 2 for diagnosis and retry guidance. |
| Cancelled | "The gift request was cancelled." | Client cancelled manually. |
| Stocks Transferred | "The gift has been successfully transferred. The stocks will be visible in the receiver's holdings by the next trading day." | — |

### A5 — Buy Average & Pricing

- Buy average for receiver: updated within 3 working days. Entry price = closing price on transfer date.
- Exit price for sender: closing price on transfer date (for tracking/reporting).
- Recently gifted stocks may show a red exclamation / discrepancy mark in holdings — this is normal and resolves when buy average is updated.

### A6 — Field Rules

**Shareable with client:** `creation` (as date/time), `status` (translated per **A4**), `items` (stock names and quantities).

**Internal reasoning only (never share with client):** `modified` (use internally for timeline analysis), `sender_fullname`, `gifted_by`, `receiver_fullname`, `receiver_email`, `receiver_phone_number`, `claimer_fullname`, `claimed_by`.

### A7 — CDSL Links

| Purpose | URL |
|---|---|
| Manual beneficiary addition (if CDSL email not received) | https://www.cdslindia.com/Authentication/OTP.aspx?id=B |

### A8 — Cross-Reference Protocols

| Topic | Refer to |
|---|---|
| Verify gifted stocks in receiver's holdings (may show discrepancy mark initially) | Console EQ Holdings |
| Gift entry as external trade for buy average update | Console EQ External Trades |

### A9 — Escalation Triggers (Consolidated)

Escalate when any of the following occur:
- Status = Stocks Transferred but receiver cannot see shares after 2+ trading days.
- Stocks transferred but buy average not updated after 3+ working days.
- Gift request fails repeatedly despite completing all steps correctly.

Include in escalation: client ID (sender/receiver), creation date, status, items, and the specific issue.


### Preflight (run on every query)

1. If the tool returned no gift request data, re-invoke the tool with the client ID in `claimed_by` only — leave `gifted_by` blank. Do NOT populate both fields simultaneously (the tool returns no data if both are filled).
2. Apply field protection per **A6** — identify shareable vs internal-only fields.
3. Identify the current status and translate using **A4**.
4. If status is Approved or Processing, check `modified` timestamp internally for timeline guidance (per **A3** approval cutoff).
5. Format amounts with ₹ and Indian comma notation. Format dates as DD MMM YYYY, HH:MM AM/PM.

### Routing Tree

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

### Scope

- Address: gift request status, CDSL verification steps, transfer timelines, charges, buy average updates, and troubleshooting.

### Fallback

If no root cause is identified after checking all relevant rules → escalate per Rule 10.


### Rule 1 — Gift Status Check

1. Use the gift request data from Preflight (including the fallback `claimed_by` re-query if needed). Find the matching request.
2. Translate the status using **A4** and respond with the appropriate client-facing communication.
3. For Approved status: check `modified` timestamp internally. If after 2 PM → add: "Since the gift was approved after 2 PM, the CDSL verification email will be sent on the next trading day." (Per **A3**.)

### Rule 2 — Gift Failed: Diagnose and Retry

1. Respond: "Your gift request for [items] created on [creation date] has failed. This typically happens when:
   - The beneficiary was not added on CDSL, or the verification email was not completed between 3 PM and 5 PM.
   - The CDSL OTP verification was not completed by 8 PM on the same day."
2. Retry guidance: "To retry: Place a fresh gift request on Console. If you don't receive the CDSL beneficiary email, use this link between 3 PM and 5 PM: [**A7** beneficiary link] to validate the beneficiary. Once added, complete the OTP verification between 5 PM and 8 PM."

### Rule 3 — CDSL Email Not Received

1. Check `modified` timestamp internally (Preflight step 4).

**Approved after 2 PM:**
"Since the gift was approved after 2 PM, the CDSL email will be sent on the next trading day." (Per **A3**.)

**Approved before 2 PM and no email by 5 PM:**
"If you haven't received the beneficiary verification email from CDSL by 5 PM, you can manually add the beneficiary using: [**A7** beneficiary link]

Once the beneficiary is added, you'll receive the OTP verification at 5 PM. Complete it before 8 PM." (Per **A3**.)

### Rule 4 — Beneficiary Already Added

1. Respond: "If the receiver's demat account was already added as a beneficiary from a previous transfer, you can skip the beneficiary addition step. The CDSL OTP verification email will be sent at 5 PM. Complete it by 8 PM." (Per **A3**.)

### Rule 5 — Gifted Stocks Not Visible in Holdings

1. Confirm: status = Stocks Transferred (per **A4**).
2. Respond: "Gifted stocks become visible in the receiver's holdings on the next trading day after the transfer is completed."
3. If more than 2 trading days since transfer: "If it's been more than 2 trading days since the status changed to 'Stocks Transferred' and the stocks are still not visible, we'll investigate." → escalate per Rule 10.

### Rule 6 — Discrepancy Mark on Gifted Stocks

1. Respond using **A5**: "This is normal for recently gifted stocks. The discrepancy appears because the buy average hasn't been updated yet. The buy average (based on the closing price on the transfer date) will be updated within 3 working days."
2. Add: "If the discrepancy persists after 3 working days, please let us know and we'll investigate."

### Rule 7 — Buy Average Not Updated

1. Confirm: more than 3 working days since transfer.
2. Respond: "The buy average for gifted stocks should be updated within 3 working days of the transfer. If it's still showing as N/A or incorrect after 3 working days, we'll look into this." (Per **A5**.)
3. escalate per Rule 10.

### Rule 8 — Gift Charges

1. Respond using **A2**: "Standard off-market transfer charges apply: ₹25 per security per transaction + 18% GST. These are debited from the sender's trading account. If you gifted 3 different stocks in one transaction, the charges would be ₹75 + 18% GST."
2. Note: gift won't process if sender's trading account balance is negative (see Rule 9 if applicable).

### Rule 9 — Sender Balance Negative

1. Respond: "The gift request cannot be processed because the sender's trading account has a negative balance. The sender needs to add funds to cover the transfer charges (₹25 + 18% GST per security per **A2**). Once funds are added, the balance updates the next day, and the gift can be processed."

### Rule 10 — Escalation

Escalate when any trigger in **A9** is met.

Include in escalation: client ID (sender/receiver), creation date, status, items, and the specific issue.

