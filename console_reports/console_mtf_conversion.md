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

## Protocol

# CONSOLE MTF CONVERSION PROTOCOL 

---

## Section A: Reference Data

---

### A1 — Fundamentals

This tool tracks **MTF-to-CNC conversion requests** — requested qty, converted qty, status, and remarks. It is the source of truth for whether a conversion actually succeeded.

**Status = "Processed" does NOT always mean conversion succeeded.** Always check `converted_quantity` against `request_quantity` before communicating the outcome. If `converted_quantity` = 0 and status = Processed → conversion failed due to insufficient margin (known display issue).

Conversion requires full funded amount available as free cash in the account — partial funds = full failure.


---

### A2 — Field Usage Rules

**Shareable fields:**

`status` | `isin` | `trade_date` | `request_quantity` | `converted_quantity` | `remarks`

**Internal-only fields** (use for reasoning; communicate outcomes in plain language):

`client_id`

**Communication rule:** When sharing conversion outcome with the client, always base the response on `converted_quantity` vs `request_quantity` — not on the `status` field value alone.

---

### A3 — Status Values

| Status | Meaning | Action |
|---|---|---|
| Processed | System attempted conversion | Check `converted_quantity`: if = `request_quantity` → success. If = 0 → failed (display issue). If < `request_quantity` → partial. |
| Pending | Request awaiting processing | Typically processed same day or next morning. |

---

### A4 — Common Failure Reasons

| Reason | Explanation |
|---|---|
| Insufficient funds | Account did not have sufficient free cash to cover the funded amount |
| T+1 restriction | Shares bought today under MTF cannot be converted until next trading day |
| Ex-date restriction | Conversions on ex-date of corporate actions are not processed — retry after ex-date |
| Short delivery | Short-delivered MTF position auto-converted to CNC — interest should stop; if not, escalate for reversal |

---

### A5 — Cross-Reference Tools

| Tool | When to Use |
|---|---|
| `console_mtf_holdings` | Verify if shares still under MTF after conversion. Contains MTF-specific rules, interest, square-off details. |
| `console_eq_holdings` | Verify if converted shares now appear in regular equity holdings. |

---

### A6 — Escalation Data Template

When escalating, always include: **client ID, tradingsymbol/ISIN, conversion date, request_quantity, converted_quantity, and specific issue.**

---

## Section B: Decision Flow

---

### Preflight (run on every query)

```
1. Identify the stock (ISIN / tradingsymbol) the client is asking about.
2. Look up matching conversion records by Client ID.
3. For any record with status = Processed:
   └─ Always check converted_quantity before communicating outcome.
```

### Route

```
Intent / Condition                                          → Rule
──────────────────────────────────────────────────────────────────────
Conversion status check                                     → Rule 1
Conversion cost inquiry                                     → Rule 2
Conversion failed — diagnose reason                         → Rule 3
Shares still in MTF after successful conversion             → Rule 4
MTF interest still charged after conversion                 → Rule 5
Stock removed from MTF list — must I convert?               → Rule 6
Remarks field interpretation                                → Rule 7
```

### Scope

- Address the client's query about MTF-to-CNC conversion requests, status, cost, and failure diagnosis.
- Use **A2** field rules and communication rule in all client interaction.
- Base all outcome communication on `converted_quantity` vs `request_quantity`, not on `status` alone.

### Fallback

If no route matches, cross-reference with **A5** tools for additional context. If no root cause is found, escalate per **A6**.

---

## Section C: Rules

---

### Rule 1 — Conversion Status Verification

1. Find matching ISIN/tradingsymbol in conversion records.
2. Check `converted_quantity` vs `request_quantity`:
   a. `converted_quantity` = `request_quantity` → Your conversion of [request_quantity] shares has been successfully processed. These shares have moved from MTF to regular delivery holdings..
   b. `converted_quantity` = 0 AND status = Processed → Your conversion request was not processed due to insufficient funds in your account. The status shows 'Processed' but the actual conversion did not go through — this is a display issue. Please add the required funds (the funded amount for these shares) and place a new conversion request..
   c. `converted_quantity` < `request_quantity` → Only [converted_quantity] of your requested [request_quantity] shares were converted. The remaining shares are still under MTF. This may be due to insufficient funds for the full conversion..
   d. Status = Pending → Your conversion request is pending processing. It will typically be processed by the next trading day..

---

### Rule 2 — Conversion Cost Inquiry

1. To convert your MTF position to regular delivery, you need to have the funded amount available as free cash in your account. The funded amount is the portion that Zerodha contributed when you purchased the shares under MTF.

You can check the funded amount in the remarks field of your conversion request, or calculate it as: total purchase value minus the initial margin you paid..
2. If client asks about MTM already paid → The MTM (Mark-to-Market) margin you've paid covers daily price fluctuations. The conversion cost is the original funded amount, not the MTM..

---

### Rule 3 — Conversion Failed (Diagnose Reason)

1. `converted_quantity` = 0. Diagnose against **A4**:
   a. Insufficient funds → Your account did not have sufficient free cash to cover the funded amount of ₹[from remarks]. Please add the required funds and retry. (use cost from `remarks`).
   b. T+1 → Shares purchased today under MTF can only be converted from the next trading day..
   c. Ex-date → Conversions on the ex-date of a corporate action are not processed. Please retry after the ex-date..
2. If none of the above explains → escalate per **A6**.

---

### Rule 4 — Shares Still in MTF After Successful Conversion

1. `converted_quantity` > 0 but client says shares still appear under MTF.
2. Check `console_mtf_holdings` (per **A5**) for the stock.
3. If conversion was within last 1 trading day → may take overnight to reflect.
4. If 2+ trading days since conversion and still in MTF → escalate per **A6**.
5. Also check `console_eq_holdings` (per **A5**) — converted shares should now appear there.

---

### Rule 5 — Interest After Conversion

1. After a successful conversion, MTF interest should stop accruing on the converted quantity from the next day. If interest is still being charged on the converted shares, we'll investigate and reverse any incorrect charges..
2. Verify conversion was successful (`converted_quantity` > 0).
3. If yes and interest still charged → escalate per **A6**.

---

### Rule 6 — Stock Removed from MTF List

1. If a stock is removed from the MTF approved list, your existing MTF position is NOT automatically converted or squared off. You can continue to hold the position under MTF. However, if you wish to convert to regular delivery to avoid ongoing MTF interest, you can place a conversion request provided you have sufficient funds..

---

### Rule 7 — Remarks Field Interpretation

1. The `remarks` field contains system-generated text with: quantity converted, trade date, and total cost of conversion.
2. Parse and Your conversion details: [converted_quantity] shares converted from your MTF purchase on [trade_date]. The total conversion cost was ₹[cost from remarks]..

