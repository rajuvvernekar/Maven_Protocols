# conditional_orders

## Description

WHEN TO USE:

When clients:
- Ask about conditional order status (pending, not triggered)
- Report conditional order not triggering despite NAV reaching target
- Report NAV mismatch between trigger price and allotment NAV
- Ask about payment timing for conditional buy orders
- Ask about CDSL authorization for conditional sell orders
- Ask how conditional orders work
- Report conditional order expired or auto-rejected after 365 days
- Report "Redeem all" not working with conditional orders
- Ask about stop-loss via conditional sell order
- Report cancelled conditional order not visible in order history

TRIGGER KEYWORDS: "conditional order", "NAV trigger", "trigger pending", "conditional buy", "conditional sell", "conditional redeem"

## Protocol

# CONDITIONAL ORDERS PROTOCOL

---

## Section A: Reference Data

All rules reference these blocks as single sources of truth.

### A1 — Conditional Order Fundamentals

- Conditional orders = NAV-tracking orders to buy/sell MF when NAV reaches a trigger price.
- Available for lumpsum only.
- Trigger check uses T-1 day NAV. Actual allotment/redemption NAV = T day NAV (will differ from trigger price).
- Once triggered, the order moves to mf_order_history. No longer visible in this tool.
- Valid for 365 days. Auto-rejected after expiry.
- Payment is not debited at placement. Client must pay manually (UPI/Netbanking) after trigger notification. No payment held = no refund on expiry/cancellation.
- "Redeem all" is not available with conditional orders — client must enter exact unit count manually.
- Sell redemption proceeds credited to primary bank account as per scheme settlement time.

### A2 — Trigger Times & Limits

| | Buy Conditional | Sell Conditional |
|---|---|---|
| Trigger time | 10:05 AM | 10:15 AM |
| Trigger limit | Cannot set below 60% of current NAV | Cannot set above 200% of current NAV |
| Below current NAV | — | Can set below current NAV (acts as stop-loss) |

### A3 — T-PIN / DDPI Authorization (Sell Only)

| Account Type | Requirement |
|---|---|
| Non-DDPI/POA | Must authorize CDSL T-PIN before 3 PM on trigger day (not at placement). If missed → order rejected. |
| DDPI enabled | No T-PIN required. |

### A4 — Field Rules

**Shareable with client:** `fund`, `transaction_type` (BUY/SELL), `trigger_price`, `created` (only if asked).

**Internal reasoning only:** `remarks` (share in client-friendly language if populated), `amount`.

**Never share with client:** `gtt_id`, `client_id`, `tradingsymbol`, `tag`.

### A5 — Cross-Reference Protocols

| Topic | Refer to |
|---|---|
| Triggered order status | mf_order_history (10:05 AM buy / 10:15 AM sell, variety = GTT on trigger date) |

## Section B: Decision Flow

### Preflight (run on every query)

1. Fetch the conditional orders data for the client.
2. Apply field protection per **A4** — identify shareable, internal, and banned fields.
3. If `remarks` is populated, translate to client-friendly language before sharing.
4. Format amounts with ₹ and Indian comma notation.

### Routing Tree

```
Query relates to conditional orders →
│
├─ Order not triggered despite NAV reaching target
│  → Rule 1
│
├─ NAV mismatch after trigger
│  → Rule 2
│
├─ When is payment debited (buy)
│  → Rule 3
│
├─ CDSL authorization for sell
│  → Rule 4
│
├─ Triggered order — status inquiry
│  → Rule 5
│
├─ "Redeem all" not available
│  → Rule 6
│
├─ Can conditional sell act as stop-loss
│  → Rule 7
│
├─ Expired / cancelled order
│  → Rule 8
│
└─ General conditional order query
   → Check data, respond with shareable fields
```

### Scope

- Address: trigger logic, NAV differences, payment timing, T-PIN authorization, expiry, and triggered order routing.

### Fallback

If the conditional order is no longer visible in this tool → it was triggered. Check mf_order_history per **A5**.

---

## Section C: Rules

Rules reference Section A blocks. They do not redefine what is already defined there.

### Rule 1 — Order Not Triggered

1. Respond: "Conditional orders use T-1 day NAV for trigger comparison. Your order will trigger when T-1 day NAV reaches or crosses your trigger price of ₹[trigger_price]." (Per **A1**.)

### Rule 2 — NAV Mismatch After Trigger

1. Respond: "Trigger check uses T-1 day NAV, but allotment/redemption happens at T day NAV. A difference between your trigger price and the applied NAV is expected." (Per **A1**.)

### Rule 3 — Payment Timing (Buy)

1. Respond: "Payment is not debited when you place a conditional order. Once the NAV reaches your trigger price and the order is triggered, you will receive a notification and the payment can be completed via Coin." (Per **A1**.)

### Rule 4 — CDSL Authorization (Sell)

1. Respond using **A3**: "For non-DDPI/POA accounts, CDSL T-PIN authorization is required on the day the order is triggered — not when placing the order. Authorize before 3 PM on trigger day. If missed, the order will be rejected."

### Rule 5 — Triggered Order: Cross-Tool Lookup

1. Check mf_order_history (per **A5**) for orders placed at 10:05 AM (buy) or 10:15 AM (sell) on the trigger date.
2. Respond: "Once triggered, your conditional order becomes a regular order. We can check the status in your order history."

### Rule 6 — Redeem All Not Available

1. Respond: "'Redeem all' is not available for conditional orders. Please enter the exact number of units you wish to redeem manually." (Per **A1**.)

### Rule 7 — Stop-Loss Query

1. Respond: "Yes, you can set a conditional sell trigger below the current NAV. The order will trigger when T-1 day NAV falls to or below your trigger price." (Per **A2**.)

### Rule 8 — Expiry / Cancellation

1. Respond: "Conditional orders are valid for 365 days. If not triggered within this period, the order is automatically rejected. Since no payment is debited when placing a conditional order, there is no refund." (Per **A1**.)

