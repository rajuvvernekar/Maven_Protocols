# contract_note_charges

## Description

WHEN TO USE:

When clients:
- Ask for total charges summary for a specific date range, exchange, or segment
- Want aggregate charges breakdown (not per-trade, but totals by charge type)
- Compare aggregate charges across months or segments
- Ask about clearing charges, IPTF charges, or other CN-specific charge heads

TRIGGER KEYWORDS: "contract note charges", "total charges", "aggregate charges", "charges summary", "total brokerage", "total STT", "total stamp duty", "charges for the month", "charges breakdown summary", "CN charges", "contract note"

## Protocol

# CONTRACT NOTE CHARGES PROTOCOL 
---

## Section A: Reference Data

All rules reference these blocks as single sources of truth.

### A1 — Report Fundamentals

- This report provides aggregate charges by account head (charge type) for a selected date range, exchange, and segment.
- Required inputs: Client ID, Exchange (NSE/BSE), Segment (EQ/FO/CDS/COM), From/To Date.
- Each row = one charge component (account head) with its total charge amount. A Total row provides the sum of all charges for the period.
- This is a summary tool — for order-level breakdown, use the Tradewise Charges Report (per **A5**).
- XML contract notes may show slightly different charges than PDF CN due to IPFT inclusion timing. The PDF version is the authoritative document.

### A2 — Account Head Definitions

| Account Head | Client-Facing Name | What It Is |
|---|---|---|
| Stamp Duty | Stamp duty | Government stamp duty on trade value |
| Exchange Transaction Charges | Exchange transaction charges | Exchange charges for trade execution |
| STT | STT (Securities Transaction Tax) | Government tax on securities transactions |
| SEBI Turnover Fees | SEBI turnover fee | SEBI regulatory fee based on turnover |
| Brokerage | Brokerage | Zerodha's brokerage charges for executing trades |
| Clearing Charges | Clearing charges | Charges for clearing and settlement of trades (separate from exchange charges) |
| CGST | CGST | Central GST (9%) on brokerage + exchange charges |
| SGST | SGST | State GST (9%) on brokerage + exchange charges |
| IGST | IGST | Integrated GST (for inter-state — usually zero) |
| IPTF | Investor Protection Fund Tax | Contribution towards investor protection mechanisms — small amount per trade |

### A3 — Field Rules

**Shareable with client:** `account_head` (translated to client-facing name per **A2**), `charge` (as amount), `Total`.

**Internal reasoning only (no client use):** `client_id`, `exchange` (use internally for segment identification), `segment` (use internally).

### A4 — Charges Summary Template

"Here's your charges summary for [period]:
- Brokerage: ₹[brokerage]
- Exchange transaction charges: ₹[exchange_txn]
- STT: ₹[stt]
- SEBI turnover fee: ₹[sebi]
- Stamp duty: ₹[stamp_duty]
- Clearing charges: ₹[clearing]
- GST (CGST + SGST): ₹[cgst + sgst]
- Investor Protection Fund: ₹[iptf]
- **Total charges: ₹[Total]**"

### A5 — Cross-Reference Protocols

| Topic | Refer to |
|---|---|
| Per-trade / per-order charge breakdown | Tradewise Charges Report protocol |
| Charge debit entries on ledger | Ledger Report protocol |

### A6 — Escalation Triggers (Consolidated)

Escalate when:
- Total charges seem significantly wrong compared to trading volume for the period.
- A specific charge head shows an unusual amount that cannot be explained by the account head definition.

Include in escalation: client ID, date range, exchange, segment, and the specific discrepancy.

**Escalation behavior:** When any rule in this protocol says **ESCALATE**, do not draft a customer-facing response. Instead, output only: **HUMAN AGENT ACTION REQUIRED** — followed by the reason from the rule. The human agent will handle the query manually.

---

## Section B: Decision Flow

### Preflight (run on every query)

1. Fetch the contract note charges report for the client's date range, exchange, and segment.
2. Apply field protection per **A3** — identify shareable vs internal-only fields.
3. Translate account head names to client-facing terms per **A2**.
4. Format all amounts with ₹ and Indian comma notation.

### Routing Tree

```
Query relates to contract note charges →
│
├─ Client asks for total charges for a period
│  → Rule 1
│
├─ Client asks for per-trade or per-order breakdown
│  → Rule 2 (Redirect to Tradewise Charges)
│
├─ Client asks what a specific charge component means
│  → Rule 3
│
├─ Client reports difference between PDF and XML contract note
│  → Rule 4
│
└─ Charges seem significantly wrong / unusual amount
   → Rule 5 (Escalation)
```

### Scope

- Address: aggregate charge summaries, charge component explanations, and CN format differences.
- Do not volunteer: internal field values (per **A3**), exchange/segment identifiers, or per-trade detail (redirect to Tradewise Charges per **A5**).

### Fallback

If no root cause is identified after checking all relevant rules → **ESCALATE** per Rule 5.

---

## Section C: Rules

Rules reference Section A blocks. They do not redefine what is already defined there.

### Rule 1 — Charges Summary

1. Present the charges using the template from **A4**, filling in the values from the report.
2. Combine CGST + SGST into a single GST line for the client.

### Rule 2 — Per-Trade Redirect

1. Respond: "This report shows the total charges for the period. For a per-trade breakdown showing charges for each individual order, I can check the tradewise charges report instead." (Per **A5**.)
2. If the client confirms, use the Tradewise Charges Report protocol.

### Rule 3 — Charge Component Explanation

1. Look up the charge component in **A2** and respond with the client-facing name and explanation.

### Rule 4 — PDF vs XML Contract Note Difference

1. Respond: "The PDF contract note includes the most up-to-date charges. The XML version may occasionally differ slightly, particularly for exchange transaction charges and IPTF, as these may be adjusted after the initial CN generation. The PDF version is the authoritative document." (Per **A1**.)

### Rule 5 — Escalation

Escalate when any trigger in **A6** is met.

Include in escalation: client ID, date range, exchange, segment, and the specific discrepancy.

---

## Section D: General Notes

1. This is a summary-level tool. For any question about charges on a specific trade or order, redirect to the Tradewise Charges Report protocol (**A5**) rather than attempting to break down the aggregates.
2. The PDF contract note is always the authoritative document when there is a discrepancy between PDF and XML versions.
3. Clearing charges and IPTF are smaller, less commonly questioned components. If a client asks about them, the definitions in **A2** provide sufficient explanation.
