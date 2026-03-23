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

## Protocol

# KITE GTT PROTOCOL 

---

## Section A: Reference Data

---

### A1 — Tool Purpose & Fundamentals

This tool shows a client's **GTT (Good Till Triggered) orders** — orders that stay active until the trigger condition is met or validity expires. GTT is free — no additional charges.

**Validity:** Equity GTT = 1 year from creation. F&O GTT = until contract expiry.

**Trigger behavior:** Valid only once. If the triggered order is placed but not executed, the client must create a new GTT. Triggered GTT becomes a CNC limit order with DAY validity — cancelled by exchange at end of day if unfilled.

**Single trigger:** One trigger price → one order placed when LTP hits/breaches trigger.

**OCO (two-leg):** Stoploss + target triggers. When one triggers, the other is cancelled. Buy OCO available only for F&O contracts. OCO uses NRML only for index F&O.

GTT triggers based on ticks recorded by the system — if a tick is not captured, GTT may not trigger even if price briefly touched the level.

Max 500 active GTTs per account. Notifications: email + Kite push notification on trigger and order placement.

**Input:** Client ID.

---

### A2 — Field Usage Rules

**Shareable fields:**

`id` | `tradingsymbol` | `transaction_type` | `status` | `type` | `quantity` | `trigger_values` | `price` | `product` | `order_type` | `trigger_percentage` | `order_result_status` | `order_result_rejection_reason` | `created_at` | `updated_at` | `rejection_reason`

**Internal-only fields** (use for reasoning; communicate outcomes in plain language):

`order_result_id` | `ltp` | `exchange` | `expires_at`

**Client-facing terminology:**

| Internal Term | Client-Facing Alternative |
|---|---|
| `ltp` | (omit — LTP at GTT creation time, not current price) |
| `exchange` | (omit — internal routing) |
| `expires_at` | Describe as "valid for 1 year" (equity) or "until contract expiry" (F&O) |

---

### A3 — Status Values

| Status | Meaning |
|---|---|
| Active | Pending trigger — GTT is live and monitoring price |
| Triggered | Trigger hit — order placed on exchange. Check `order_result_status` for outcome. |
| Cancelled | Cancelled due to corporate action (series change, delisting, suspension, extraordinary dividend, rights issue, consolidation, capital reduction), or lot size change for index F&O |
| Expired | Equity: 1 year lapsed. F&O: contract expired. |
| Disabled | Trigger set too close to LTP (< 0.25% for stocks > ₹50), or CA like bonus/stock split affected instrument |
| Deleted | Removed by user |

---

### A4 — Trigger Distance Rules

| Stock Price | Minimum Trigger Distance |
|---|---|
| Above ₹50 | At least 0.25% away from LTP |
| Below ₹50 | At least 9 paise away from LTP |

---

### A5 — Buy GTT Rejections

| Reason | Explanation |
|---|---|
| Insufficient margin | No funds at trigger time — GTT can be created without funds, but needs funds when triggered |
| Trigger too close | Trigger < 0.25% from LTP (stocks > ₹50) or < 9 paise (stocks < ₹50) |
| Price band | Limit price outside exchange circuit limit on trigger day |
| Contract not allowed | F&O contract not allowed by Zerodha at trigger time |
| Segment killed | Segment disabled via Kill Switch at trigger time |

---

### A6 — Sell GTT Rejections

| Reason | Explanation |
|---|---|
| TPIN not authorised | Holdings not authorised via CDSL TPIN — must authorise daily after 7 AM if no POA/DDPI |
| Insufficient holdings | Not enough shares in demat at trigger time |
| Series change | Instrument underwent series change or suspension |
| Segment killed | Segment disabled via Kill Switch |

---

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

---

### A8 — Links

| Topic | URL / Reference |
|---|---|
| GTT Terms of Service | zerodha.com/tos/gtt |
| Generate CDSL TPIN | support.zerodha.com — How to generate CDSL TPIN |
| Activate DDPI | support.zerodha.com — How to activate DDPI |

---

### A9 — Escalation Data Template

When escalating, always include: **client ID, tradingsymbol, GTT type, status, trigger values, and specific issue.**

---

### A10 — Response Templates

**R1 — Active (single):**
"Your [transaction_type] GTT for [tradingsymbol] is active. Trigger price: ₹[trigger_values], limit price: ₹[price], quantity: [quantity]. Equity GTTs are valid for 1 year from creation; F&O GTTs until contract expiry."

**R2 — Active (when will it trigger):**
"Your GTT will trigger when the LTP of [tradingsymbol] hits or breaches ₹[trigger_values]. Once triggered, a [order_type] order at ₹[price] will be placed on the exchange."

**R3 — Active (OCO):**
"Your OCO GTT has two triggers — stoploss at ₹[lower_trigger] and target at ₹[upper_trigger]. When one triggers, the other is automatically cancelled."

**R4 — Triggered + executed:**
"Your GTT for [tradingsymbol] was triggered and the order was executed."

**R5 — Triggered + rejected (insufficient margin):**
"Your GTT triggered but was rejected due to insufficient funds. GTTs can be created without funds, but funds must be available when the trigger fires."

**R6 — Triggered + rejected (TPIN not authorised):**
"Your sell GTT was rejected because holdings were not authorised via CDSL TPIN. Without POA/DDPI, you must authorise daily after 7 AM. Consider activating DDPI to avoid this."

**R7 — Triggered + rejected (insufficient holdings):**
"Your sell GTT was rejected because you didn't have enough shares in your demat account when the trigger fired."

**R8 — Triggered + rejected (price band/circuit):**
"Your GTT triggered but the limit price was outside the exchange's circuit limit for the day. The order was rejected."

**R9 — Triggered + rejected (series change/suspension):**
"Your GTT was rejected because the instrument underwent a series change or was suspended."

**R10 — Triggered + rejected (segment killed):**
"Your GTT was rejected because you had disabled this segment using Kill Switch."

**R11 — Triggered + cancelled by user:**
"Your GTT for [tradingsymbol] was triggered on [trigger date] and a [order_type] order was placed on the exchange. However, this order was cancelled from your end during the trading session. The GTT trigger is a one-time event — you'll need to create a new GTT if you still want this order."

**R12 — Triggered + unfilled (EOD cancellation):**
"Your GTT for [tradingsymbol] triggered on [trigger date] and an order was placed, but it wasn't filled by end of day. Triggered GTT orders become limit orders with DAY validity — if unfilled, the exchange cancels them at session end. You'll need to create a new GTT."

**R13 — Triggered GTT not visible in order book:**
"Once triggered, the GTT order is a regular limit order with DAY validity. If it wasn't filled, the exchange cancelled it at end of day. From the next day, it won't appear in the order book. Check your email for the trigger and order details."

**R14 — Price reached but not triggered:**
"GTT triggers based on ticks recorded by the system. Hundreds of transactions occur per second on the exchange, and each is represented by a tick. If the system didn't capture the tick at your trigger price of ₹[trigger_values], the GTT may not trigger. It will remain active until the price reaches the trigger again."

**R15 — Cancelled (CA/series change):**
"Your GTT was cancelled because [instrument] was [delisted/suspended/underwent a series change/category change]. You'll need to create a new GTT."

**R16 — Cancelled (F&O CA/lot change):**
"Your GTT for the F&O contract was cancelled due to a [corporate action affecting lot size/price / lot size change for index contracts]. You'll need to create a new GTT."

**R17 — Cancelled (extraordinary CA):**
"Extraordinary corporate actions (dividends above 2%, rights issue, consolidation, capital reduction) also cause GTT cancellation. You'll need to create a new GTT."

**R18 — Expired (equity):**
"Your GTT expired because it wasn't triggered within 1 year of creation (created on [created_at]). Create a new GTT if needed."

**R19 — Expired (F&O):**
"Your GTT expired because the F&O contract expired. GTTs for derivatives are valid only until contract expiry."

**R20 — Disabled:**
"Your GTT was disabled because the trigger price was set too close to LTP (less than 0.25% for stocks above ₹50, or less than 9 paise for stocks below ₹50) after validation, or the instrument underwent a corporate action like a bonus issue or stock split. You'll need to create a new GTT with a valid trigger price."

**R21 — Deleted:**
"This GTT was deleted from your account [on updated_at]."

**R22 — Email price mismatch:**
"The price in the email is the actual LTP at the moment the GTT triggered — not your trigger price. Due to market volatility or gaps (opening gap up/down), the LTP at trigger time may be higher or lower than your set trigger price. Example: if you set a sell trigger at ₹95 but the stock opened at ₹90 (gap down), the trigger fires at ₹90 and the email shows ₹90."

**R23 — Trigger too close (creation error):**
"For stocks above ₹50, the trigger must be at least 0.25% away from the current market price. For stocks below ₹50, the trigger must be at least 9 paise away."

**R24 — No LTP (creation error):**
"GTTs require an LTP to validate the trigger. If the instrument has no LTP due to illiquidity, GTT creation is not possible."

**R25 — Max GTTs reached:**
"You can have a maximum of 500 active GTTs. Delete existing GTTs to create new ones."

**R26 — Stoploss prompt (index options):**
"This prompt encourages setting a stoploss when buying options to manage risk. You can proceed without setting one, but Zerodha recommends a GTT stoploss (5–10% is a reasonable starting point). Remember to cancel open GTT stoploss orders when you directly exit the position to avoid unintended positions."

---

## Section B: Decision Flow

---

### Preflight (run on every query)

```
1. Locate GTT by tradingsymbol.
2. If not found → check if it's an old/expired/deleted GTT
   → invoke kite_gtt_archived.
```

### Route

```
Intent / Condition                                          → Rule
──────────────────────────────────────────────────────────────────────
GTT status check (any status)                               → Rule 1
Status = Active                                             → Rule 2
Status = Triggered                                          → Rule 3
Price reached but GTT didn't fire                           → Rule 4
Status = Cancelled                                          → Rule 5
Status = Expired                                            → Rule 6
Status = Disabled                                           → Rule 7
GTT email price differs from trigger                        → Rule 8
F&O GTT specifics                                           → Rule 9
GTT creation error                                          → Rule 10
GTT stoploss prompt (index options)                         → Rule 11
```

### Scope

- Address the client's query about their GTT orders — status, triggers, rejections, and F&O specifics.
- Use **A2** field rules and client-facing terminology in all client communication.
- For triggered GTT execution details → invoke `kite_orders` (today) or `kite_order_history` (past).

### Fallback

If no route matches, investigate using Section A reference data. If no root cause is found, escalate per **A9**.

---

## Section C: Rules

---

### Rule 1 — GTT Status Check

1. Locate by `tradingsymbol`. Share: tradingsymbol, transaction_type, type (single/OCO), status, trigger_values, price, quantity, product, created_at.
2. Route by status: active → Rule 2, triggered → Rule 3, cancelled → Rule 5, expired → Rule 6, disabled → Rule 7, deleted → respond per **A10-R21**.
3. If GTT not found → invoke `kite_gtt_archived`.

---

### Rule 2 — Status: Active

1. Respond per **A10-R1**.
2. If client asks when it will trigger → respond per **A10-R2**.
3. If OCO → respond per **A10-R3**.

---

### Rule 3 — Status: Triggered

1. Check `order_result_status`:
   a. COMPLETE → respond per **A10-R4**. Invoke `kite_orders` (today) or `kite_order_history` (past) for execution details.
   b. REJECTED → match `order_result_rejection_reason` against **A5** (buy) or **A6** (sell) and respond with the matching template (**A10-R5** through **A10-R10**). Cross-reference `kite_margins` (margin) or `kite_holdings` (holdings) as needed.
   c. CANCELLED → invoke `kite_order_history` filtered to the GTT trigger date only. Use the `gtt` field internally to confirm the order is linked to this GTT. Do not look at orders on subsequent dates.
      - Cancelled during market hours → respond per **A10-R11** (user cancelled).
      - Cancelled after market hours → respond per **A10-R12** (EOD unfilled).
2. If triggered GTT not visible in order book → respond per **A10-R13**.

---

### Rule 4 — Price Reached but GTT Didn't Fire

1. Respond per **A10-R14**.
2. Additional checks:
   - Price briefly touched and bounced — tick may not have been recorded.
   - GTT was modified — check `updated_at` to confirm latest trigger value.
   - GTT was disabled due to CA or trigger too close to LTP.

---

### Rule 5 — Status: Cancelled

1. Check `rejection_reason` if available.
2. Match cause and respond:
   a. Series change / delisting / suspension → **A10-R15**.
   b. F&O CA or lot size change → **A10-R16**.
   c. Extraordinary CA (dividend >2%, rights, consolidation, capital reduction) → **A10-R17**.

---

### Rule 6 — Status: Expired

1. Equity → respond per **A10-R18**.
2. F&O → respond per **A10-R19**.

---

### Rule 7 — Status: Disabled

1. Respond per **A10-R20**. Trigger distance rules per **A4**.

---

### Rule 8 — GTT Email Price Mismatch

1. Respond per **A10-R22**.

---

### Rule 9 — F&O GTT Specifics

1. Respond with applicable rules from **A7**:
   - Validity until contract expiry, not 1 year.
   - Physical delivery risk for stock F&O.
   - Hedge risk: closing one leg increases margin. Invoke `kite_margins` to check. If client asks about affected position → invoke `kite_positions`.
   - CA/lot change cancellation.
   - Currency: GTT not available.
   - OCO restriction: buy OCO for F&O only, NRML for index F&O OCO.

---

### Rule 10 — GTT Creation Errors

1. Trigger too close → respond per **A10-R23**. Distance rules per **A4**.
2. No LTP (illiquid) → respond per **A10-R24**.
3. Max 500 active GTTs reached → respond per **A10-R25**.

---

### Rule 11 — GTT Stoploss Prompt (Index Options)

1. Respond per **A10-R26**.

---

## Section D: General Notes

- GTT is free. Max 500 active per account. Notifications via email + Kite push.
- Equity GTT valid 1 year; F&O GTT until contract expiry.
- Trigger is one-time only. If triggered order is not executed, client must create a new GTT.
- Triggered GTT becomes a CNC limit order with DAY validity — cancelled at EOD if unfilled, not visible from next day.
- GTT triggers on system-captured ticks — brief price touches may not be captured.
- GTT email may show price different from trigger — this is actual LTP at trigger moment (gap up/down).
- Sell GTT executes only if shares are in demat and order fills on exchange. TPIN authorization required daily if no POA/DDPI.
- GTT closing one leg of hedged position → margin increases → Zerodha may square off remaining position.
- F&O GTTs cancelled when lot size changes or CA affects lot size/price. Not available for Currency segment.
- Buy OCO available only for F&O. Index F&O OCO uses NRML only.
