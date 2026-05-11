# console_mtf_conversion

## Description

WHEN TO USE:

When clients:
- Ask about the status of their MTF-to-CNC conversion request
- Report MTF conversion shows "Processed" but shares still under MTF
- Ask about MTF conversion cost or amount required to convert
- Question why MTF conversion failed or was not processed
- Ask about partial MTF conversion (some qty converted, some not)
- Ask about MTF conversion history for a specific security

TRIGGER KEYWORDS: "MTF conversion", "MTF to CNC", "MTF to delivery", "convert MTF", "conversion status", "conversion processed", "conversion failed", "conversion request", "conversion cost", "convert to delivery"

TAGS: margins, holdings

## Protocol

# CONSOLE MTF CONVERSION PROTOCOL

---

## Section A: Reference Data

### A1 — Fundamentals

- Conversion requires the funded amount as free cash. If free cash is less than the funded amount, only the affordable portion converts (`converted_quantity` < `request_quantity`); the rest stays under MTF.
- **Funded amount:** the portion Zerodha contributed during the original MTF purchase. Equals total purchase value minus initial margin paid.
- **MTM margin** is separate from the funded amount — MTM covers daily price fluctuations and does not reduce the conversion cost.
- `converted_quantity` = 0 with `status` = Processed is a known display issue — the record may show 0 even when the conversion actually went through. Verify via `console_eq_holdings` per A6.

---

### A2 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |
|---|---|
| `status` | Conversion request status; translate per A3 |
| `tradingsymbol` | Stock symbol |
| `isin` | ISIN identifier |
| `trade_date` | Date of original MTF purchase |
| `request_quantity` | Quantity requested for conversion |
| `converted_quantity` | Quantity actually converted |
| `remarks` | System-generated remarks; carries the funded amount and conversion details for the request |

**Non-shareable:**

| Field | Interpretation |
|---|---|
| `client_id` | Internal client identifier |

---

### A3 — Status Values

| Status | Meaning |
|---|---|
| Processed | Conversion request was processed by the system. Outcome (success / partial / display-issue zero) is determined by `converted_quantity` vs `request_quantity` per Rule 1. |
| Pending | Conversion request awaiting processing; typically processed same day or by next morning. |

---

### A4 — Common Failure Reasons

| Reason | Explanation |
|---|---|
| Insufficient funds | Free cash less than funded amount at processing time. |
| T+1 restriction | MTF shares bought today or on the previous trading day (accounting for holidays) cannot be converted until the next trading day. |
| Ex-date restriction | Conversions on the ex-date of a corporate action are not processed; the request can be retried after ex-date. |
| Short delivery | A short-delivered MTF position is auto-converted to CNC. MTF interest stops on auto-conversion. |

---

### A5 — MTF List Removal Behaviour

- When a stock is removed from the MTF approved list, an existing MTF position continues to be held under MTF; it is not auto-converted or squared off.
- MTF interest continues to accrue. The client can place a conversion request to stop interest, provided sufficient funds.

---

### A6 — Cross-Reference Tools

| Tool | When to invoke |
|---|---|
| `kite_order_history` | To verify purchase date when diagnosing T+1 restriction (Rule 3). |
| `console_mtf_holdings` | To check whether shares still appear under MTF after a conversion (Rule 4). |
| `console_eq_holdings` | To confirm converted shares now appear in delivery holdings (Rule 1 display-issue verification, Rule 4). |

---

### A7 — Escalation Data

-Include when escalating to human agent: client ID, `tradingsymbol`, `isin`, conversion date, `request_quantity`, `converted_quantity`, and specific issue.

---

## Section B: Decision Flow

### Routing

```
Route by scenario
   ├─ Conversion outcome verification (status, partial, pending) → Rule 1
   ├─ Funded amount / conversion cost calculation → Rule 2
   ├─ `converted_quantity` = 0 confirmed as actual failure (after Rule 1) → Rule 3
   ├─ Shares still under MTF after a conversion attempt → Rule 4
   ├─ MTF interest accruing on an already-converted position → Rule 5
   ├─ Stock removed from MTF approved list — impact on existing position → Rule 6
   └─ Conversion details from `remarks` field (qty, trade date, cost) → Rule 7
```

### Fallback

If no rule matches → escalate to human agent per A7.

---

## Section C: Rules

### Rule 1 — Conversion Outcome Verification

Diagnose by `converted_quantity` vs `request_quantity`:

| Condition | Outcome to communicate |
|---|---|
| `converted_quantity` = `request_quantity` | Conversion succeeded; shares moved from MTF to delivery holdings. |
| `converted_quantity` = 0 AND `status` = Processed | Known display issue per A1. Invoke `console_eq_holdings` per A6 to verify: if converted shares appear in delivery holdings → conversion actually went through and the record will auto-correct. If shares are not in delivery → conversion did not execute; route to Rule 3 for failure reason. |
| `converted_quantity` < `request_quantity` | Partial conversion — free cash covered only `converted_quantity` shares (A1). Remaining shares stay under MTF. |
| `status` = Pending | Request awaiting processing per A3. |

---

### Rule 2 — Funded Amount / Conversion Cost

1. The conversion cost is the funded amount per A1. Read it from the `remarks` field on the conversion record, or compute it per A1.
2. If the client conflates MTM with conversion cost → distinguish per A1: MTM is daily fluctuation margin, not the conversion amount.

---

### Rule 3 — Conversion Failed (Actual Failure Confirmed by Rule 1)

Diagnose against A4:

| Reason | Action |
|---|---|
| Insufficient funds | Share funded amount from `remarks` per A1; client adds funds and re-requests. |
| T+1 restriction | Invoke `kite_order_history` per A6 to confirm purchase date; apply A4. |
| Ex-date restriction | Apply A4. |
| None of the above | Escalate to human agent per A7. |

---

### Rule 4 — Shares Still Showing Under MTF Post-Conversion

1. Invoke `console_eq_holdings` per A6 — confirm converted shares are now in delivery holdings.
2. Invoke `console_mtf_holdings` per A6 — check whether shares still appear under MTF.
3. If conversion was within the last 1 trading day → reflection can take overnight; advise client to check the next trading day.
4. If 2+ trading days since conversion and shares still in MTF → escalate to human agent per A7.

---

### Rule 5 — MTF Interest After Conversion

1. If the conversion was an auto-conversion from short delivery → interest should stop per A4. If interest is still charged → escalate to human agent per A7 for reversal.
2. Otherwise (regular conversion, interest still accruing) → escalate to human agent per A7.

---

### Rule 6 — Stock Removed from MTF List

1. Existing positions remain under MTF per A5; MTF interest continues to accrue.
2. To stop interest → place a conversion request per A1 (funded amount must be available as free cash).

---

### Rule 7 — Conversion Details from `remarks`

- The `remarks` field carries quantity converted, trade date of the original MTF purchase, and total conversion cost. Surface these per A2.
