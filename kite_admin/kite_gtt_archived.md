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

TAGS: orders

## Protocol

# KITE GTT ARCHIVED PROTOCOL

## Section A: Reference Data

### A1 — Fundamentals

Same GTT mechanics apply: single trigger, OCO (two-leg), 1-year equity validity, F&O until contract expiry. Trigger is one-time only — if triggered order was placed but not executed, a new GTT must have been created.

Triggered GTT becomes CNC limit order with DAY validity — cancelled by exchange at end of day if unfilled.

GTT triggers based on ticks recorded by the system — missed ticks mean GTT may not have triggered.

### A2 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |  
|---|---|  
| `id` | GTT id |  
| `tradingsymbol` | Stock symbol |  
| `transaction_type` | Buy/sell |  
| `status` | GTT status |  
| `type` | Single / OCO |  
| `quantity` | Quantity |  
| `trigger_values` | Trigger price(s) |  
| `price` | Limit price |  
| `product` | CNC etc. |  
| `order_type` | Limit etc. |  
| `trigger_percentage` | Trigger percentage |  
| `order_result_status` | Outcome of triggered order |  
| `order_result_rejection_reason` | Rejection reason if rejected |  
| `created_at` | Creation timestamp |  
| `updated_at` | Last update timestamp |  
| `rejection_reason` | Cancellation reason (when present) |

**Non-shareable:**

| Field | Interpretation |  
|---|---|  
| `order_result_id` | Internal order reference |  
| `ltp` | LTP at GTT creation time; not available for archived GTTs |  
| `exchange` | Not available for archived GTTs |  
| `expires_at` | Internal — equity validity is 1 year; F&O validity is until contract expiry |

### A3 — Status Values

| Status | Meaning |  
|---|---|  
| Active (archived) | Was pending trigger — now archived, likely superseded or system-moved |  
| Triggered | Trigger hit — order placed on exchange |  
| Cancelled | CA, series change, delisting, suspension, lot size change |  
| Expired | Equity: 1 year lapsed. F&O: contract expired |  
| Disabled | Trigger too close to LTP (< 0.25% for stocks > ₹50), or a CA like bonus/stock split |  
| Deleted | Removed by user |

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

### A5 — Links

| Topic | URL |  
|---|---|  
| GTT Terms of Service | zerodha.com/tos/gtt |

### A6 — Escalation Required Data

Include when escalating to human agent: client ID, GTT id, tradingsymbol, status, created_at, and specific issue.

## Section B: Decision Flow

### Routing

```  
Route by scenario  
   ├─ Looking for current/active GTT → invoke ‘kite_gtt’  
   ├─ Old/missing GTT — initial lookup before status is known → Rule 1  
   ├─ Status = Triggered → Rule 2  
   ├─ Status = Cancelled → Rule 3  
   ├─ Status = Expired → Rule 4  
   ├─ Status = Disabled → Rule 5  
   ├─ Expiry/exchange/LTP details → Rule 6  
   └─ GTT not found in either tool → Rule 7  
```

### Fallback

If no route matches, escalate to human agent per **A6**.

## Section C: Rules

### Rule 1 — Archived GTT Status Check

1. Locate by `tradingsymbol`. Share: `tradingsymbol`, `transaction_type`, `type` (single/OCO), `status`, `price`, `quantity`, `product`, `created_at`, `updated_at`.  
2. Route by status:  
   a. Triggered → Rule 2.  
   b. Cancelled → Rule 3.  
   c. Expired → Rule 4.  
   d. Disabled → Rule 5.  
   e. Deleted → confirm deletion on `updated_at`.  
   f. Active (archived) → was active but archived; may have been superseded; create a new GTT if needed.  
3. If looking for current GTT → invoke `kite_gtt`.

### Rule 2 — Status: Triggered

1. Check `order_result_status`:  
   a. COMPLETE → triggered and executed on `updated_at`. Invoke `kite_order_history` with date from `updated_at` for execution details.  
   b. REJECTED → match `order_result_rejection_reason` against **A4**. Additionally:  
      - Insufficient margin: if asked about current balance, invoke `kite_margins`.  
      - Insufficient holdings: if asked about current holdings, invoke `kite_holdings`.  
      - If reason is unmatched in A4: share `order_result_rejection_reason` as-is.  
   c. CANCELLED → invoke `kite_order_history` with date from `updated_at`:  
      - Cancelled during market hours → user cancelled.  
      - Cancelled after market hours → EOD unfilled.

### Rule 3 — Status: Cancelled

1. Check `rejection_reason` if available.  
2. Match against cancellation causes per **A3** (Cancelled row).

### Rule 4 — Status: Expired

1. Equity → 1-year validity lapsed since `created_at` per **A3**.  
2. F&O → contract expired per **A3**.

### Rule 5 — Status: Disabled

1. Match the disable cause against **A3** (Disabled row): trigger too close to LTP, or a CA like bonus/stock split.

### Rule 6 — Client Asks for Unavailable Fields

1. Expiry date, exchange, and LTP at creation are not available for archived GTTs per **A2**. Confirm what is available per **A2** Shareable list.  
2. If client needs these for dispute resolution → escalate to human agent per **A6** with GTT `id` and `created_at`.

### Rule 7 — GTT Not Found in Either Tool

1. Possible reasons: created with a different instrument name (verify exact tradingsymbol); very old GTTs may not be available; suggest checking email for GTT trigger/creation notifications. For details on a very old GTT, escalate to human agent per **A6** with approximate date and instrument.
