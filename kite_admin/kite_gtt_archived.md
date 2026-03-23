# kite_gtt_archived

## Description

WHEN TO USE:

When clients:
- Ask about old or past GTT orders no longer in the active GTT list (expired, deleted, cancelled, or triggered months ago)
- Report a GTT they placed previously is not found in active GTTs
- Ask about outcome of a GTT that was triggered weeks or months ago (whether the order was executed or rejected)
- Ask why an old GTT was cancelled (corporate action, delisting, series change), expired (1-year lapse or contract expiry), or disabled (trigger too close to LTP, bonus/split)
- Ask about historical GTT rejection reasons (why a triggered order failed in the past)
- Ask about F&O GTT that expired along with the contract
- Ask about details of a GTT they deleted (confirmation of deletion date and original details)

TRIGGER KEYWORDS: "old GTT", "past GTT", "expired GTT", "deleted GTT", "previous GTT", "GTT from last month", "GTT from last year", "GTT history", "archived GTT", "GTT not found", "can't find my GTT", "GTT disappeared", "where is my GTT"

## Protocol

# KITE GTT ARCHIVED PROTOCOL

---

## Section A: Reference Data

---

### A1 — Tool Purpose & Fundamentals

This tool returns **historical/old GTT orders** — expired, deleted, cancelled, or triggered GTTs that are no longer in the active GTT list. For current/recent GTTs, use `kite_gtt`.

Same GTT mechanics apply: single trigger, OCO (two-leg), 1-year equity validity, F&O until contract expiry. Trigger is one-time only — if triggered order was placed but not executed, a new GTT must have been created.

Triggered GTT becomes CNC limit order with DAY validity — cancelled by exchange at end of day if unfilled.

GTT triggers based on ticks recorded by the system — missed ticks mean GTT may not have triggered.

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
| `ltp` | (omit — LTP at GTT creation time, not available for archived) |
| `exchange` | (omit — not available for archived GTTs) |
| `expires_at` | (omit — describe as "1 year validity" for equity or "until contract expiry" for F&O) |

---

### A3 — Status Values

| Status | Meaning |
|---|---|
| Active (archived) | Was pending trigger — now archived, likely superseded or system-moved |
| Triggered | Trigger hit — order placed on exchange. Check `order_result_status` for outcome. |
| Cancelled | CA, series change, delisting, suspension, lot size change |
| Expired | Equity: 1 year lapsed. F&O: contract expired. |
| Disabled | Trigger too close to LTP, or CA like bonus/stock split |
| Deleted | Removed by user |

---

### A4 — Common Rejection Reasons (Triggered but Failed)

| Reason | Explanation |
|---|---|
| Insufficient margin (buy) | No funds at trigger time |
| TPIN not authorised (sell) | Holdings not authorised via CDSL TPIN |
| Insufficient holdings (sell) | Not enough shares in demat at trigger time |
| Price band | Limit price outside circuit limit on trigger day |
| Series change | Instrument underwent series change or suspension |
| Segment killed | Segment disabled via Kill Switch |
| Contract not allowed | F&O contract not allowed by Zerodha at trigger time |

---

### A5 — Links

| Topic | URL |
|---|---|
| GTT Terms of Service | zerodha.com/tos/gtt |

---

### A6 — Escalation Data Template

When escalating, always include: **client ID, GTT id, tradingsymbol, status, created_at, and specific issue.**

---

### A7 — Response Templates

**R1 — Triggered + executed:**
"Your GTT for [tradingsymbol] was triggered and the order was executed on [updated_at]."

**R2 — Triggered + rejected (insufficient margin):**
"Your GTT triggered but was rejected due to insufficient funds at trigger time."

**R3 — Triggered + rejected (TPIN):**
"Your sell GTT was rejected because holdings weren't authorised via CDSL TPIN."

**R4 — Triggered + rejected (insufficient holdings):**
"Your sell GTT was rejected — not enough shares in demat when trigger fired."

**R5 — Triggered + rejected (price band):**
"Your GTT triggered but the limit price was outside the circuit limit for that day."

**R6 — Triggered + rejected (series change):**
"Your GTT was rejected because the instrument underwent a series change or suspension."

**R7 — Triggered + cancelled by user:**
"Your GTT for [tradingsymbol] was triggered and an order was placed, but this order was cancelled from your end during the trading session. The GTT trigger is a one-time event — you would have needed to create a new GTT."

**R8 — Triggered + unfilled (EOD cancellation):**
"Your GTT triggered and an order was placed, but it wasn't filled by end of day. The exchange cancelled it at session end. A triggered GTT is a one-time event — you would have needed to create a new GTT."

**R9 — Cancelled:**
"Your GTT for [tradingsymbol] was cancelled. Common reasons: the instrument was delisted, suspended, underwent a series change, or a corporate action affected the contract. For F&O, lot size changes also cause cancellation."

**R10 — Expired (equity):**
"Your GTT for [tradingsymbol] expired because it wasn't triggered within 1 year of creation (created [created_at])."

**R11 — Expired (F&O):**
"Your GTT expired because the F&O contract expired. F&O GTTs are valid only until contract expiry."

**R12 — Disabled:**
"Your GTT for [tradingsymbol] was disabled. This happens when: the trigger was set too close to LTP (< 0.25% for stocks > ₹50), or a corporate action like bonus/stock split affected the instrument."

**R13 — Deleted:**
"This GTT was deleted from your account on [updated_at]."

**R14 — Active (archived):**
"This GTT was active but has been archived. It may have been superseded. Create a new GTT if needed."

**R15 — Unavailable fields requested:**
"The expiry date and exchange details are not available for archived GTT orders. Here's what can be confirmed: your [transaction_type] GTT for [tradingsymbol] had a trigger at ₹[trigger_values] with a limit price of ₹[price] for [quantity] qty, created on [created_at]. Status: [status]."

**R16 — GTT not found in either tool:**
"No matching GTT found for [tradingsymbol]. Possible reasons:
- The GTT may have been created with a different instrument name (check exact trading symbol).
- Very old GTTs may not be available in the system. Check your email for GTT trigger/creation notifications.
- If you need details for a specific GTT from a long time ago, please raise a support ticket with the approximate date and instrument."

---

## Section B: Decision Flow

---

### Preflight (run on every query)

```
1. Locate GTT by tradingsymbol or browse archived list.
2. If customer is looking for a current/active GTT
   → invoke kite_gtt instead.
```

### Route

```
Intent / Condition                                          → Rule
──────────────────────────────────────────────────────────────────────
Archived GTT status check                                   → Rule 1
Status = Triggered                                          → Rule 2
Status = Cancelled                                          → Rule 3
Status = Expired                                            → Rule 4
Status = Disabled                                           → Rule 5
Client asks for expiry/exchange/LTP details                 → Rule 6
GTT not found in either tool                                → Rule 7
```

### Scope

- Address the client's query about historical/archived GTT orders — past triggers, rejections, cancellations, and expirations.
- Use **A2** field rules and client-facing terminology in all client communication.
- For current GTTs, redirect to `kite_gtt`.

### Fallback

If no route matches, investigate using Section A reference data. If no root cause is found, escalate per **A6**.

---

## Section C: Rules

---

### Rule 1 — Archived GTT Status Check

1. Locate by tradingsymbol. Share: tradingsymbol, transaction_type, type (single/OCO), status, price, quantity, product, created_at, updated_at.
2. Route by status:
   a. Triggered → Rule 2.
   b. Cancelled → Rule 3.
   c. Expired → Rule 4.
   d. Disabled → Rule 5.
   e. Deleted → respond per **A7-R13**.
   f. Active (archived) → respond per **A7-R14**.
3. If looking for current GTT → invoke `kite_gtt`.

---

### Rule 2 — Status: Triggered

1. Check `order_result_status`:
   a. COMPLETE → respond per **A7-R1**. Invoke `kite_order_history` with date from `updated_at` for execution details.
   b. REJECTED → match `order_result_rejection_reason` against **A4**:
      - Insufficient margin → **A7-R2**. If client asks about current balance → invoke `kite_margins`.
      - TPIN → **A7-R3**.
      - Insufficient holdings → **A7-R4**. If client asks about current holdings → invoke `kite_holdings`.
      - Price band → **A7-R5**.
      - Series change → **A7-R6**.
      - Unmatched → share `order_result_rejection_reason` verbatim.
   c. CANCELLED → invoke `kite_order_history` with date from `updated_at`.
      - Cancelled during market hours → **A7-R7** (user cancelled).
      - Cancelled after market hours → **A7-R8** (EOD unfilled).

---

### Rule 3 — Status: Cancelled

1. Check `rejection_reason` if available.
2. Respond per **A7-R9**.

---

### Rule 4 — Status: Expired

1. Equity → respond per **A7-R10**.
2. F&O → respond per **A7-R11**.

---

### Rule 5 — Status: Disabled

1. Respond per **A7-R12**.

---

### Rule 6 — Client Asks for Unavailable Fields

1. Client asks for expiry date, exchange, or LTP at creation → respond per **A7-R15**.
2. If client needs these details for dispute resolution → escalate per **A6** with GTT `id` and `created_at`.

---

### Rule 7 — GTT Not Found in Either Tool

1. Respond per **A7-R16**.

---

## Section D: General Notes

- This tool contains historical/archived GTTs only. For current active GTTs, use `kite_gtt`.
- Same mechanics as active GTTs: single/OCO trigger, 1-year equity validity, F&O until contract expiry, one-time trigger.
- Triggered GTT becomes CNC limit order with DAY validity — cancelled at EOD if unfilled.
- Sell GTT requires shares in demat + TPIN authorization. Buy GTT requires funds at trigger time (not creation).
- F&O GTTs cancelled by corporate actions affecting lot size/price. Not available for Currency segment.
- Expiry date, exchange, and LTP at creation are not available for archived GTTs.
- Very old GTTs may not be available in the system — direct client to check email notifications or raise a ticket.
