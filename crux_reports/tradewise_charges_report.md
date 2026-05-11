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

TAGS: charges, reports

## Protocol

# TRADEWISE CHARGES PROTOCOL

---

## Section A: Reference Data

### A1 — Report Fundamentals

- With "View orderwise" selected, each row represents one complete order with charges already consolidated across all fills — no manual summing needed.
- Trade value = quantity × price (from tradebook). Charges are calculated on this value.
- CN (Contract Note) charges may not include later adjustments posted directly to ledger.

---

### A2 — Account Type Detection

| Account Type | Detection Logic |
|---|---|
| Individual | `category` = "Individual" AND `client_acc_type` = "Individual" |
| Non-Individual (HUF, Corporate, LLP, Partnership, Trust) | `category` = "Non-Individual" |
| NRI | `client_acc_type` IN ("NRO", "NRE", "NRI") → resolve PIS/Non-PIS via `pis_bank_*` fields |
| NRI PIS | `client_acc_type` IN ("NRO", "NRE", "NRI") AND `pis_bank_1_name` OR `pis_bank_2_name` NOT None |
| NRI Non-PIS | `client_acc_type` IN ("NRO", "NRE", "NRI") AND both `pis_bank_*_name` = None |

---

### A3 — Charge Components

| Charge | Rate / Basis | Notes |
|---|---|---|
| Brokerage | Delivery (CNC): varies by account type — see table below. Intraday/F&O: ₹20 per executed order OR 0.03% of trade value, whichever is lower. | Can be null/0 for some trades. |
| Exchange transaction charges | Charged by exchange on turnover. Rate varies by exchange and segment — NSE equity ~0.00297%, BSE equity varies, NSE F&O varies by contract type. | SENSEX options have specific rates different from NIFTY options. Rates updated periodically — recent changes may cause different charges for the same trade type on different dates. |
| STT (Securities Transaction Tax) | Equity delivery: 0.1% on both buy and sell value. Equity intraday: 0.025% on sell-side only. Futures: 0.02% on sell-side. Options: 0.1% on sell-side (on premium value). | Government tax on securities transactions. |
| Stamp duty | Buy-side transactions. Typically 0.015% for delivery, 0.003% for intraday/F&O. | Varies by state. |
| SEBI turnover fee | ₹10 per crore of turnover (0.0001%). | — |
| GST (CGST + SGST) | 18% (9% CGST + 9% SGST) on brokerage + exchange transaction charges. | IGST is typically null (only for inter-state; standard is CGST + SGST). |

**Delivery Brokerage by Account Type:**

| Account Type | Delivery (CNC) Brokerage | Intraday / F&O Brokerage |
|---|---|---|
| Individual | ₹0 | ₹20 per executed order OR 0.03% of trade value, whichever is lower |
| Non-Individual (HUF, Corporate, LLP, Partnership, Trust) | 0.1% of trade value OR ₹20 per executed order, whichever is lower | Same as Individual |
| NRI PIS | 0.5% of trade value OR ₹200 per executed order, whichever is lower | Same as Individual |
| NRI Non-PIS | 0.5% of trade value OR ₹50 per executed order, whichever is lower | Same as Individual |

---

### A4 — Field Rules

**Shareable with client:**

| Field | Interpretation |
|---|---|
| `trading_symbol` | Share as "trading symbol" or stock name |
| `order_time` | Share as "date/time of trade" |
| `brokerage` | Brokerage charge |
| `turnover` | Share as "exchange transaction charges" |
| `sebi` | Share as "SEBI turnover fee" |
| `stamp_duty` | Stamp duty charge |
| `stt` | Securities Transaction Tax (STT) |
| `sgst` | SGST |
| `cgst` | CGST |

**Non-shareable:**

| Field | Interpretation |
|---|---|
| `trade_process_type` | Trade process type — "auction" for auction trades; used for Rule 8 routing |
| `order_no` | Internal order number |
| `exchange` | Exchange and segment identifier — used for charge rate lookup per A3 |
| `igst` | Inter-state GST — typically null; only applicable for inter-state transactions |

---

### A5 — Escalation Data

Required fields when escalating: **client ID**, **trading_symbol**, **order_time**, **specific charge values**, **discrepancy description**.

---

## Section B: Decision Flow

### Routing

```
Query relates to tradewise charges →
│
├─ Client asks about charges for a specific trade             → Rule 1
├─ Client questions brokerage amount                          → Rule 2
├─ Client disputes exchange transaction charges               → Rule 3
├─ Client asks about STT                                      → Rule 4
├─ Client asks about GST / CGST / SGST                       → Rule 5
├─ Client says charges differ from Zerodha calculator         → Rule 6
├─ Client reports contract note vs tradewise mismatch         → Rule 7
├─ Auction trade charges                                      → Rule 8
└─ Data mismatch / no root cause found                        → Rule 9
```

### Fallback

If no rule matches, ESCALATE TO HUMAN AGENT.

---

## Section C: Rules

### Rule 1 — Trade Charges Breakdown

1. Locate the trade by `trading_symbol` and `order_time`.
2. Present the charges breakdown across all charge components per A3.

---

### Rule 2 — Brokerage Verification

1. From `get_all_client_data`, confirm account type per A2.
2. Verify delivery brokerage against the applicable rate per A3 for the client's account type:
   - If Individual account + delivery trade + brokerage ≠ ₹0 → flag discrepancy, escalate to human agent.
   - If Non-Individual or NRI account + delivery trade + brokerage = null/0 → brokerage may have been incorrectly waived, escalate to human agent.
   - For all other Non-Individual and NRI delivery trades → verify brokerage against rates per A3.
3. For Intraday/F&O trades (all account types): verify brokerage cap per A3. If brokerage exceeds the cap → escalate to human agent.

---

### Rule 3 — Exchange Transaction Charges Dispute

1. Use `exchange` field internally to identify the segment.
2. Verify the applied rate against published rates per A3 for the identified segment.
3. Note: SENSEX options have specific rates different from NIFTY options; BSE equity rates may differ from NSE (per A3).
4. If the applied rate significantly differs from the published rate for that segment → escalate to human agent.

---

### Rule 4 — STT Explanation

1. Identify the trade type (equity delivery, equity intraday, futures, or options) using `exchange` and trade details internally.
2. Apply STT rates per A3 for the identified trade type.

---

### Rule 5 — GST Calculation

1. GST base = `brokerage` + `turnover` (per A3).

---

### Rule 6 — Calculator vs Actual Charges Difference

1. Differences can occur due to rounding at trade level vs order level, exchange rate updates not yet reflected in the calculator, or fill-level charge application.
2. The tradewise charges report reflects the actual charges applied.
3. If the difference is significant (greater than 10% or greater than ₹5 for a single order) → verify charges against A3 and A2. If discrepancy remains → escalate to human agent.

---

### Rule 7 — Contract Note vs Tradewise Charges Mismatch

1. Exchange transaction charges may be revised after the trade date and the difference posted directly to the ledger as an adjustment entry. The contract note may show the original amount while the ledger reflects the updated total.
2. Direct the client to check their ledger for adjustment entries posted after the trade date — invoke `ledger_report`.
3. If no adjustment entry is found and the mismatch persists → escalate to human agent.

---

### Rule 8 — Auction Trade Charges

1. If `trade_process_type` = "auction" OR client asks about auction charges: auction trades have a different charge structure arising when a trade goes to exchange auction (for example, due to short delivery) and may include additional penalties beyond standard trade charges.
2. Escalate to human agent immediately — auction charge calculations require manual handling (per A5).

---

### Rule 9 — Escalation

Escalate to human agent when any of the following apply:

- Brokerage exceeds the applicable cap per order (per A3 and A2).
- Individual account is charged delivery brokerage that is not ₹0.
- Non-Individual or NRI delivery trade shows null/0 brokerage (possible incorrect waiver).
- Exchange transaction charge rate significantly differs from the published rate for that segment (per A3).
- Contract note charges differ from the tradewise charges sum for the same date/exchange/segment and no ledger adjustment entry is found.
- Auction trade requiring detailed charge calculation — manual handling required.
- Data mismatch with no root cause found after checking all applicable rules.

Include all fields per A5 when escalating.
