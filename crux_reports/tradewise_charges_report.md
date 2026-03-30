# tradewise_charges_report

## Description

WHEN TO USE:

When clients:
- Ask for a breakdown of charges applied to a specific trade or order
- Question why brokerage, STT, stamp duty, or exchange charges are a certain amount
- Want order-wise charges for trades executed on a specific date
- Report charges don't match their calculation or the Zerodha brokerage calculator
- Ask about exchange transaction charges, SEBI fees, or GST on brokerage
- Want to understand what each charge component means
- Report discrepancy between contract note charges and tradewise charges

TRIGGER KEYWORDS: "tradewise charges", "trade charges", "charges breakdown", "brokerage calculation", "brokerage per trade", "STT charges", "stamp duty", "exchange transaction charges", "SEBI charges", "GST on brokerage", "order charges", "charges for my trade", "why brokerage higher", "total charges for order", "charges per order"

## Protocol

# TRADEWISE CHARGES PROTOCOL

---

## Section A: Reference Data

All rules reference these blocks as single sources of truth.

### A1 — Report Fundamentals

- Report shows per-trade breakdown of all charges: brokerage, exchange transaction charges, SEBI fees, STT, stamp duty, CGST, SGST, IGST.
- Required inputs: Client ID, From/To Date. Optional: Exchange, Segment. Select "View orderwise" checkbox for order-level grouping.
- Multiple rows with the same `order_no` = multiple fills for one order. Sum charges by `order_no` for total per order.
- Trade value = quantity × price (from tradebook). Charges are calculated on this value.
- CN (Contract Note) charges may not include later adjustments posted directly to ledger.

### A2 — Charge Components

| Charge | Rate / Basis | Notes |
|---|---|---|
| Brokerage | Delivery (CNC): ₹0 (zero). Intraday/F&O: ₹20 per executed order OR 0.03% of trade value, whichever is lower. | Can be null/0 for some trades. |
| Exchange transaction charges | Charged by exchange on turnover. Rate varies by exchange and segment — NSE equity ~0.00297%, BSE equity varies, NSE F&O varies by contract type. | SENSEX options have specific rates different from NIFTY options. Rates updated periodically — recent changes may cause different charges for the same trade type on different dates. |
| STT (Securities Transaction Tax) | Equity delivery: 0.1% on both buy and sell value. Equity intraday: 0.025% on sell-side only. Futures: 0.02% on sell-side. Options: 0.1% on sell-side (on premium value). | Government tax on securities transactions. |
| Stamp duty | Buy-side transactions. Typically 0.015% for delivery, 0.003% for intraday/F&O. | Varies by state. |
| SEBI turnover fee | ₹10 per crore of turnover (0.0001%). | — |
| GST (CGST + SGST) | 18% (9% CGST + 9% SGST) on brokerage + exchange transaction charges. | IGST is typically null (only for inter-state; standard is CGST + SGST). |

### A3 — Field Rules

**Shareable with client (use these client-facing names):**

| Internal Field | Client-Facing Name |
|---|---|
| `trading_symbol` | trading symbol / stock name |
| `order_time` | date/time of trade |
| `brokerage` | brokerage |
| `turnover` | exchange transaction charges |
| `sebi` | SEBI turnover fee |
| `stamp_duty` | stamp duty |
| `stt` | STT |
| `sgst` | SGST |
| `cgst` | CGST |

**Internal reasoning only (never share with client):** `trade_process_type` (ignore this field), `order_no` (use internally to group fills), `exchange` (use internally for segment identification), `igst` (typically null).

Use client-facing names in all responses — never use internal field names.

### A4 — Cross-Reference Protocols

| Topic | Refer to |
|---|---|
| Summary of total charges per contract note period (aggregate view) | Contract Note Charges protocol |
| Charge debits as ledger entries (when charges were debited) | Ledger Report protocol |

### A5 — Escalation Triggers (Consolidated)

Escalate when any of the following occur:
- Brokerage exceeds ₹20 per order for F&O/intraday after summing all fills by `order_no`.
- Exchange transaction charge rate significantly differs from published rate for that exchange/segment.
- Contract note charges differ from tradewise charges sum for the same date/exchange/segment, and no ledger adjustment entry is found.
- Auction trade requiring detailed charge calculation (manual handling required).

Include in escalation: client ID, trading_symbol, order_time, specific charge values, and the discrepancy.

---

## Section B: Decision Flow

### Preflight (run on every query)

1. Fetch the tradewise charges report for the client's relevant date range.
2. Apply field protection per **A3** — identify shareable vs internal-only fields.
3. If multiple rows share the same `order_no`, sum all charge fields to get the per-order total before responding.
4. Format all amounts with ₹ and Indian comma notation. Format dates as DD MMM YYYY.
5. Translate all internal field names to client-facing names per **A3**.

### Routing Tree

```
Query relates to trade charges →
│
├─ Client asks about charges for a specific trade
│  ├─ Single fill → Rule 1
│  └─ Multiple fills (same order_no) → Rule 2
│
├─ Client questions brokerage amount
│  → Rule 3
│
├─ Client disputes exchange transaction charges
│  → Rule 4
│
├─ Client asks about STT
│  → Rule 5
│
├─ Client asks about GST / CGST / SGST
│  → Rule 6
│
├─ Client says charges differ from Zerodha calculator
│  → Rule 7
│
├─ Client reports contract note vs tradewise mismatch
│  → Rule 8
│
├─ Auction trade charges
│  → Rule 9 (Escalate)
│
└─ Data mismatch / no root cause found
   → Rule 10 (Escalation)
```

### Scope

- Address: per-trade and per-order charge breakdowns, charge component explanations, brokerage verification, and charge discrepancies.

### Fallback

If no root cause is identified after checking all relevant rules → escalate per Rule 10.

---

## Section C: Rules

Rules reference Section A blocks. They do not redefine what is already defined there.

### Rule 1 — Single Trade Charges Breakdown

1. Find the trade by `trading_symbol` and `order_time`. If multiple rows share the same `order_no` → use Rule 2 instead.
2. Respond:
   "Here's the charges breakdown for your [trading_symbol] trade on [order_time]:
   - Brokerage: ₹[brokerage]
   - Exchange transaction charges: ₹[turnover]
   - STT: ₹[stt]
   - SEBI turnover fee: ₹[sebi]
   - Stamp duty: ₹[stamp_duty]
   - GST (CGST + SGST): ₹[cgst + sgst]
   - Total charges: ₹[sum of all]"

### Rule 2 — Multiple Fills Per Order

1. Confirm: multiple rows exist with the same `order_no`. Sum all charge fields across fills.
2. Respond: "Your order for [trading_symbol] was executed in [N] parts (fills). The charges are calculated per fill. Here's the combined total for the entire order:"
3. Present the combined charges using the same format as Rule 1.
4. Do not expose `order_no` — describe it as "your order was executed in multiple parts."

### Rule 3 — Brokerage Calculation Verification

1. Check the trade type and verify against the rates in **A2** (brokerage row):
   - Delivery (CNC): brokerage should be ₹0.
   - Intraday/F&O: ₹20 per executed order OR 0.03% of trade value, whichever is lower.
   - If brokerage = null/0: "No brokerage was charged for this trade."
2. If brokerage > ₹20 for a single F&O/intraday order → check if multiple fills exist (sum by `order_no`). If still > ₹20 per order after summing → escalate per Rule 10.
3. Respond: "Zerodha charges a flat ₹20 per executed order for intraday and F&O trades, or 0.03% of trade value — whichever is lower. Delivery trades have zero brokerage."

### Rule 4 — Exchange Transaction Charges Dispute

1. Respond: "Exchange transaction charges are set by the exchange and vary by segment and instrument type. The rates are updated periodically. For your [segment] trade, the applicable rate was applied on the trade value."
2. Use `exchange` field internally to identify the segment, but do not share it with the client.
3. Note: SENSEX options have specific rates different from NIFTY options. BSE equity rates may differ from NSE (per **A2**).
4. If the rate significantly differs from known published rates → escalate per Rule 10.

### Rule 5 — STT Explanation

1. Respond using the STT rates from **A2** (STT row):
   "Securities Transaction Tax (STT) is a government tax on securities transactions:
   - Equity delivery: 0.1% on both buy and sell value
   - Equity intraday: 0.025% on sell-side only
   - Futures: 0.02% on sell-side
   - Options: 0.1% on sell-side (on premium value)

   STT for your trade: ₹[stt] on [trading_symbol]."

### Rule 6 — GST Calculation

1. Calculate the GST base: brokerage + exchange transaction charges.
2. Respond:
   "GST at 18% is charged on the total of brokerage + exchange transaction charges.
   - CGST (9%): ₹[cgst]
   - SGST (9%): ₹[sgst]
   - Total GST: ₹[cgst + sgst]

   GST base = brokerage (₹[brokerage]) + exchange charges (₹[turnover]) = ₹[sum]. GST = 18% of ₹[sum] = ₹[result]."

### Rule 7 — Calculator vs Actual Charges Difference

1. Respond: "The Zerodha brokerage calculator provides an estimate. Slight differences can occur due to:
   - Rounding at trade level vs order level
   - Exchange rate updates not yet reflected in the calculator
   - Multiple fills for a single order being charged separately

   The tradewise charges report shows the actual charges applied to your trades."
2. If the difference is significant (>10% or >₹5 for a single order) → verify charges against **A2** rates and escalate per Rule 10 if discrepancy remains.

### Rule 8 — Contract Note vs Tradewise Charges Mismatch

1. Respond: "The contract note shows charges as of the trade date. In some cases, exchange transaction charges are updated after the trade date and the difference is posted directly to your ledger. This means the contract note may show the original charges while your ledger reflects the updated amount."
2. Direct client to check the ledger: "Check your ledger for any adjustment entries posted after the trade date." (Per **A4**, Ledger Report protocol.)
3. If no adjustment found and mismatch persists → escalate per Rule 10.

### Rule 9 — Auction Trade Charges

1. If `trade_process_type` = "auction" or client asks about auction charges:
   "Auction trades have different charge structures. Auction charges are applied when a trade goes to exchange auction (e.g., short delivery). The charges for auction trades may include additional penalties beyond standard trade charges."
2. Escalate immediately for detailed auction charge calculations — manual handling required (per **A5**).

### Rule 10 — Escalation

Escalate when any trigger in **A5** is met.

Include in escalation: client ID, trading_symbol, order_time, specific charge values, and the discrepancy.

