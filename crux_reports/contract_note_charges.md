# contract_note_charges

## Description

WHEN TO USE:

When clients:
- Ask for total charges summary for a specific date range, exchange, or segment
- Want aggregate charges breakdown (not per-trade, but totals by charge type)
- Compare aggregate charges across months or segments
- Ask about clearing charges, IPTF charges, or other CN-specific charge heads

TRIGGER KEYWORDS: "contract note charges", "total charges", "aggregate charges", "charges summary", "total brokerage", "total STT", "total stamp duty", "charges for the month", "charges breakdown summary", "CN charges", "contract note"

TAGS: charges, reports

## Protocol

# CONTRACT NOTE CHARGES PROTOCOL

---

## Section A: Reference Data

### A1 — Report Fundamentals

- Each row = one charge component (account head) with its total charge amount. A Total row provides the sum of all charges for the period.
- Segment values: **EQ** (equity), **FO** (equity F&O), **CDS** (currency F&O), **COM** (commodity F&O).
- XML contract notes may show slightly different charges than PDF CN, particularly for exchange transaction charges and IPFT, as these may be adjusted after initial CN generation. The PDF version is the authoritative document.

### A2 — Account Head Definitions

| Account Head | Client-Facing Name | What It Is |
|---|---|---|
| Stamp Duty | Stamp duty | Government stamp duty on trade value |
| Exchange Transaction Charges | Exchange transaction charges | Exchange charges for trade execution |
| STT | STT (Securities Transaction Tax) | Government tax on securities transactions |
| SEBI Turnover Fees | SEBI turnover fee | SEBI regulatory fee based on turnover |
| Brokerage | Brokerage | Zerodha's brokerage charges for executing trades |
| Clearing Charges | Clearing charges | Charges for clearing and settlement of trades (separate from exchange charges) |
| IGST | GST | Total GST charge for the period (CGST \+ SGST consolidated into this field in the report) |
| IPFT | Investor Protection Fund Trust | Contribution towards investor protection mechanisms — small amount per trade |

### A3 — Field Rules

**Shareable with client:**

| Field | Interpretation |
|---|---|
| `account_head` | Translate to client-facing name per A2 |
| `charge` | Charge amount |
| `Total` | Sum of all charges for the period |
| `segment` | Translate per A1 segment values |

**Non-shareable:**

| Field | Interpretation |
|---|---|
| `client_id` | Internal client identifier |
| `exchange` | Internal exchange identification (NSE/BSE) |

### A4 — Charges Summary Order

Order of charges to communicate to the client: Brokerage, Exchange transaction charges, STT, SEBI turnover fee, Stamp duty, Clearing charges, GST, Investor Protection Fund Trust, Total charges. Include the period in the response.

### A5 — Escalation Triggers

Escalate to human agent when any of the following occur:
- Total charges seem significantly wrong compared to trading volume for the period.
- A specific charge head shows an unusual amount that cannot be explained by the account head definition.

Include when escalating to human agent: client ID, date range, exchange, segment, and the specific discrepancy.

---

## Section B: Decision Flow

### Routing

```
Route by scenario
   ├─ Total charges summary for a period → Rule 1
   ├─ Per-trade or per-order breakdown → Rule 2
   ├─ Specific charge component meaning → Rule 3
   └─ PDF vs XML contract note difference → Rule 4
```

### Fallback

If no root cause is identified after checking all relevant rules → escalate to human agent per A5.

---

## Section C: Rules

### Rule 1 — Charges Summary

1. Communicate charges in the order specified in A4, using client-facing names from A2.
2. For the GST line, use the IGST field value (this carries the consolidated GST charge per A2).

### Rule 2 — Per-Trade Redirect

1. Direct client to the Tradewise Charges Report protocol for per-trade breakdown.
2. If client confirms, route to that protocol.

### Rule 3 — Charge Component Explanation

1. Look up the charge component in A2 and respond with the client-facing name and explanation.

### Rule 4 — PDF vs XML Contract Note Difference

1. Explain the PDF vs XML difference per A1 and confirm PDF is the authoritative document.
