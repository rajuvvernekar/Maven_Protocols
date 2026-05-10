# kite_gtt

## Description

WHEN TO USE:

When clients:
- Ask about active GTT order details (status, trigger price, quantity, limit price, product type)
- Ask about GTT triggered (what price it triggered at, when, and the order outcome)
- Report GTT triggered but order was rejected or not executed (insufficient margin, TPIN, holdings, price band)
- Report GTT not triggered even though the price was reached (tick not captured by system)
- Ask about GTT disabled, cancelled, or expired (reason and what to do next)
- Report GTT trigger price vs execution price or email price mismatch (gap up/down scenarios)
- Report GTT email notification showing a different price than the set trigger
- Report triggered GTT order not visible in the order book the next day
- Report sell GTT rejection (TPIN not authorised, insufficient holdings, series change, segment killed)
- Report buy GTT rejection (insufficient margin, trigger too close to LTP, price band violation)
- Ask about GTT OCO (two-leg) behavior (which leg triggered, other leg auto-cancelled)
- Ask about GTT for F&O contracts (validity until contract expiry, physical delivery risk, hedge leg impact)
- Report GTT creation errors (trigger too close to LTP, no LTP for illiquid stocks)
- Ask about maximum active GTTs (500 per account) or GTT limits
- Ask about GTT stoploss prompt when buying index options

TRIGGER KEYWORDS: "GTT", "good till triggered", "trigger order", "GTT triggered", "GTT not triggered", "GTT rejected", "GTT expired", "GTT cancelled", "GTT disabled", "GTT deleted", "OCO", "two-leg", "single trigger", "GTT stoploss", "GTT target", "GTT email", "GTT validity", "GTT order status", "triggered but not executed", "GTT creation error", "GTT limit", "500 GTT"

TAGS: orders

## Protocol

# KITE GTT PROTOCOL

---

## Section A: Reference Data

### A1 — Fundamentals

- GTT (Good Till Triggered) orders stay active until the trigger condition is met or validity expires. GTT is free — no additional charges.  
- **Validity:** Equity GTT = 1 year from creation. F&O GTT = until contract expiry.  
- **Trigger behavior:** Valid only once. If the triggered order is placed but not executed, the client must create a new GTT. Triggered GTT becomes a CNC limit order with DAY validity — cancelled by exchange at end of day if unfilled.  
- **Single trigger:** One trigger price → one order placed when LTP hits/breaches trigger.  
- **OCO (two-leg):** Stoploss \+ target triggers. When one triggers, the other is cancelled. Buy OCO available only for F&O contracts. OCO uses NRML only for index F&O.  
- **Trigger price vs LTP at trigger moment:** The trigger price is the threshold; the price shown in the trigger email/notification is the LTP at the moment the tick was captured. Due to gaps or volatility, the LTP at trigger can be higher or lower than the trigger price (e.g., sell trigger at ₹95, stock gaps down to ₹90 → trigger fires at ₹90).  
- GTT triggers based on ticks recorded by the system — if a tick is not captured, GTT may not trigger even if price briefly touched the level.  
- Max 500 active GTTs per account. Notifications: email \+ Kite push notification on trigger and order placement.

### A2 — Field Rules

**Shareable with client:**

| Field | Interpretation |  
|---|---|  
| `id` | GTT id |  
| `tradingsymbol` | Stock symbol |  
| `transaction_type` | Buy or sell |  
| `status` | GTT status; translate per A3 |  
| `type` | Single or OCO |  
| `quantity` | Order quantity |  
| `trigger_values` | Trigger price(s) |  
| `price` | Limit price |  
| `product` | Product type (CNC, etc.) |  
| `order_type` | Order type (limit, etc.) |  
| `trigger_percentage` | Trigger percentage |  
| `order_result_status` | Outcome of triggered order |  
| `order_result_rejection_reason` | Rejection reason if triggered order was rejected |  
| `created_at` | GTT creation timestamp |  
| `updated_at` | Last update timestamp |  
| `rejection_reason` | Cancellation reason (when present) |

**Non-shareable:**

| Field | Interpretation |  
|---|---|  
| `order_result_id` | Internal order reference |  
| `ltp` | LTP at GTT creation time (not current price) |  
| `exchange` | Internal exchange routing |  
| `expires_at` | Internal expiry timestamp; use A1 validity rules to communicate |

### A3 — Status Values

| Status | Meaning |  
|---|---|  
| Active | Pending trigger — GTT is live and monitoring price |  
| Triggered | Trigger hit — order placed on exchange. Check `order_result_status` for outcome. |  
| Cancelled | Cancelled due to corporate action (series change, delisting, suspension, extraordinary dividend, rights issue, consolidation, capital reduction), or lot size change for index F&O |  
| Expired | Equity: 1 year lapsed. F&O: contract expired. |  
| Disabled | Trigger set too close to LTP (< 0.25% for stocks > ₹50), or CA like bonus/stock split affected instrument |  
| Deleted | Removed by user |

### A4 — Trigger Distance Rules

| Stock Price | Minimum Trigger Distance |  
|---|---|  
| Above ₹50 | At least 0.25% away from LTP |  
| Below ₹50 | At least 9 paise away from LTP |

### A5 — Buy GTT Rejections

| Reason | Explanation |  
|---|---|  
| Insufficient margin | No funds at trigger time — GTT can be created without funds, but needs funds when triggered |  
| Trigger too close | Trigger < 0.25% from LTP (stocks > ₹50) or < 9 paise (stocks < ₹50) |  
| Price band | Limit price outside exchange circuit limit on trigger day |  
| Contract not allowed | F&O contract not allowed by Zerodha at trigger time |  
| Segment killed | Segment disabled via Kill Switch at trigger time |

### A6 — Sell GTT Rejections

| Reason | Explanation |  
|---|---|  
| TPIN not authorised | Holdings not authorised via CDSL TPIN — must authorise daily after 7 AM if no POA/DDPI |  
| Insufficient holdings | Not enough shares in demat at trigger time |  
| Series change | Instrument underwent series change or suspension |  
| Segment killed | Segment disabled via Kill Switch |

### A7 — F&O GTT Rules

| Rule | Detail |  
|---|---|  
| Validity | Until contract expiry — not 1 year |  
| Physical delivery | Stock F&O GTT may lead to physical delivery if contract expires ITM |  
| Hedge risk | GTT closing one leg of hedge → margin increases → Zerodha may square off |  
| Corporate action | Equity F&O GTTs cancelled if CA affects lot size/price |  
| Index lot change | Index F&O GTTs cancelled when lot size changes |  
| Currency | GTT not available for Currency segment |  
| OCO restriction | Buy OCO available only for F&O. NRML only for index F&O OCO. |

### A8 — Links

| Topic | URL |  
|---|---|  
| GTT Terms of Service | https://zerodha.com/tos/gtt |  
| Generate CDSL TPIN | https://support.zerodha.com/category/trading-and-markets/trading-faqs/general/articles/tpin-preauthorisation |  
| Activate DDPI | https://support.zerodha.com/category/your-zerodha-account/your-profile/ddpi/articles/activate-ddpi |  
| GTT stoploss option | https://support.zerodha.com/category/trading-and-markets/charts-and-orders/gtt/articles/gtt-stoploss-option |

### A9 — Escalation Triggers

Escalate to human agent when any of the following occur:  
- GTT report data appears inconsistent or missing.  
- Client provides evidence (screenshot/email) showing different GTT details than the report.  
- Client requests compensation or reversal for GTT non-execution.

Include when escalating to human agent: client ID, tradingsymbol, GTT type, status, trigger values, and the specific issue.

---

## Section B: Decision Flow

### Routing

```  
Route by scenario  
   ├─ GTT status check (any status) → Rule 1  
   ├─ Status = Active → Rule 2  
   ├─ Status = Triggered → Rule 3  
   ├─ Price reached but GTT didn't fire → Rule 4  
   ├─ Status = Cancelled → Rule 5  
   ├─ Status = Expired → Rule 6  
   ├─ Status = Disabled → Rule 7  
   ├─ GTT email price differs from trigger → Rule 8  
   ├─ F&O GTT specifics → Rule 9  
   ├─ GTT creation error → Rule 10  
   └─ GTT stoploss prompt (index options) → Rule 11  
```

### Fallback

If no rule matches, escalate to human agent per A9.

---

## Section C: Rules

### Rule 1 — GTT Status Check

1. Locate by `tradingsymbol`. Share: tradingsymbol, transaction_type, type (single/OCO), status, trigger_values, price, quantity, product, created_at.  
2. If status = deleted → confirm deletion using `updated_at`.  
3. If GTT not found → invoke `kite_gtt_archived`.

### Rule 2 — Status: Active

1. Confirm GTT is active. Share `transaction_type`, `tradingsymbol`, `trigger_values`, `price`, `quantity`. Explain validity per A1.  
2. If client asks when it will trigger → explain trigger mechanics per A1 (single or OCO as applicable).

### Rule 3 — Status: Triggered

1. Check `order_result_status`:  
   a. COMPLETE → triggered and executed. Invoke `kite_orders` (today) or `kite_order_history` (past) for execution details.  
   b. REJECTED → match `order_result_rejection_reason` against A5 (buy) or A6 (sell). Cross-reference `kite_margins` (margin) or `kite_holdings` (holdings) as needed.  
   c. CANCELLED → invoke `kite_order_history` filtered to the GTT trigger date. Use `gtt` field internally to confirm linkage.  
      - Cancelled during market hours → user cancelled during the session. Trigger is one-time per A1; advise creating a new GTT.  
      - Cancelled after market hours → triggered but unfilled by EOD per A1; advise creating a new GTT.  
2. If triggered GTT not visible in order book → reference DAY-validity behaviour per A1; direct client to email for trigger and order details.

### Rule 4 — Price Reached but GTT Didn't Fire

1. Explain tick-based trigger behaviour per A1.  
2. Additional checks:  
   - Price briefly touched and bounced — tick may not have been recorded.  
   - GTT was modified — check `updated_at` to confirm latest trigger value.  
   - GTT was disabled due to CA or trigger too close to LTP.

### Rule 5 — Status: Cancelled

1. Check `rejection_reason` if available; match cause per A3 (Cancelled row).

### Rule 6 — Status: Expired

1. Equity: explain validity per A1; reference `created_at`.  
2. F&O: explain expiry per A7.

### Rule 7 — Status: Disabled

1. Explain disable cause per A3 (Disabled row) and trigger distance rules per A4. Advise client to create a new GTT with a valid trigger price.

### Rule 8 — GTT Email Price Mismatch

1. Explain trigger price vs LTP-at-trigger-moment behaviour per A1.

### Rule 9 — F&O GTT Specifics

1. Apply rules per A7.  
2. Hedge risk check: invoke `kite_margins` to check margin impact. If client asks about affected position → invoke `kite_positions`.

### Rule 10 — GTT Creation Errors

1. Trigger too close → distance rules per A4.  
2. No LTP (illiquid) → GTTs require an LTP to validate the trigger; creation not possible if instrument has no LTP.  
3. Max 500 active GTTs reached → max active GTTs per A1; advise client to delete existing GTTs.

### Rule 11 — GTT Stoploss Prompt (Index Options)

1. Explain that the prompt encourages a stoploss when buying options. Client can proceed without setting one, but Zerodha recommends a GTT stoploss (5–10% is a reasonable starting point).  
2. Remind client to cancel open GTT stoploss orders when directly exiting the position to avoid unintended positions.  
3. Share GTT stoploss article from A8 for more details.
