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

TAGS: investments

## Protocol

# CONDITIONAL ORDERS PROTOCOL

## Section A: Reference Data

### A1 — Conditional Order Fundamentals

- Available for lumpsum only.  
- Trigger check uses T-1 day NAV. Actual allotment/redemption NAV = T day NAV (will differ from trigger price).  
- Once triggered, the order moves to ‘mf_order_history’. No longer visible in this tool.  
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

### A4 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |  
|---|---|  
| `fund` | Fund name |  
| `transaction_type` | BUY/SELL |  
| `trigger_price` | Trigger price |  
| `created` | Share only if asked |  
| `remarks` | Translate to plain language before sharing — do not share raw value |

**Non-shareable:**

| Field | Interpretation |  
|---|---|  
| `amount` | Internal reasoning |  
| `gtt_id` | Internal GTT identifier |  
| `client_id` | Internal client identifier |  
| `tradingsymbol` | Internal |  
| `tag` | Internal tag |

## Section B: Decision Flow

### Routing

```  
Route by scenario  
   ├─ Order not triggered despite NAV reaching target → Rule 1  
   ├─ NAV mismatch after trigger → Rule 2  
   ├─ When is payment debited (buy) → Rule 3  
   ├─ CDSL authorization for sell → Rule 4  
   ├─ Triggered order — status inquiry → Rule 5  
   ├─ "Redeem all" not available → Rule 6  
   ├─ Can conditional sell act as stop-loss → Rule 7  
   └─ Expired / cancelled order → Rule 8  
```

### Fallback

If no root cause found after completing all diagnostic steps → escalate to human agent.

## Section C: Rules

### Rule 1 — Order Not Triggered

1. Order will trigger when T-1 day NAV reaches or crosses the `trigger_price`.

### Rule 2 — NAV Mismatch After Trigger

1. Per **A1**, the difference between trigger price and applied NAV is expected.

### Rule 3 — Payment Timing (Buy)

1. Once NAV reaches trigger price and the order is triggered, the client receives a notification and can complete payment via Coin.

### Rule 4 — CDSL Authorization (Sell)

1. Communicate per **A3**.

### Rule 5 — Triggered Order: Cross-Tool Lookup

1. Invoke `mf_order_history` — check for orders at 10:05 AM (buy) or 10:15 AM (sell) on the trigger date, variety = GTT.  
2. Once triggered, conditional order becomes a regular order; status can be checked in order history.

### Rule 6 — Redeem All Not Available

1. Per **A1**, client must enter exact unit count manually.

### Rule 7 — Stop-Loss Query

1. Per **A2**, order triggers when T-1 day NAV falls to or below the trigger price.

### Rule 8 — Expiry / Cancellation

1. Per **A1**, communicate expiry timeline and confirm no refund applies.
