# clientwise_margin_report

## Description

WHEN TO USE:

When clients:
- Question a margin penalty charged on their ledger ("short-margin penalty for date ...")
- Ask why a margin penalty was charged despite having sufficient funds
- Want a breakdown of upfront (peak margin) vs non-upfront (EOD/MTM) penalty calculation
- Ask about penalty rates, slabs, or 18% GST on margin penalty
- Report auto-squareoff happened and a penalty was also charged
- Ask about physical delivery margin or expiry-week margin penalties
- Report a margin shortfall email despite no open positions
- Ask about hedged-position margin penalties (closing the protective leg first)
- Ask why option buying triggered a penalty
- Cite SEBI circular 60/2022 or request a margin penalty refund/waiver
- Confuse DPC (delayed payment charges) with margin penalty

TRIGGER KEYWORDS: "margin penalty", "short margin penalty", "short-margin penalty", "peak margin shortfall", "EOD margin shortfall", "upfront margin penalty", "non-upfront penalty", "MTM penalty", "physical delivery margin", "hedged position penalty", "auto squareoff penalty", "auto square-off penalty", "SEBI 60/2022", "margin penalty refund", "margin penalty waiver", "exchange penalty"

TAGS: margins, charges

## Protocol

# CLIENTWISE MARGIN REPORT PROTOCOL

---

## Section A: Reference Data

### A1 — Report Fundamentals

- Company is always Zerodha (single ledger covers all segments). Segment values: EQ for equity, FO for NSE F&O and CDS for currency.
- T-Day can be fetched by invoking `ledger_report` and reading the penalty entry narration per A7.
- Segment prefix in labels changes: EQ/FO/CDS depending on segment input.
- `{seg}_collected_short_delivery_margin` and `{seg}_collected_short_margin_on_crystallised_obligation` can return the text "Not available" instead of a number — means T+1 data not yet posted.

### A2 — Report Grid Map

**Visual grid (0-indexed rows, for orientation only):**

| Row | col_1 | col_2 | col_3 | col_4 | col_5 | col_6 | col_7 |
|---|---|---|---|---|---|---|---|
| Row 2 | EOD Margin available | T day unencumbered balance | Collateral Value | EPI Holding Value | — | — | — |
| Row 4 | Peak margin available | T day unencumbered balance | Collateral Value | EPI Holding Value | Unpledge Amount | JV and BP Debit Amount | Delivery Buy value |
| Row 8 | Total Peak Margin Required | Total Peak Margin Collected | Total EOD Required | Total EOD Collected | — | — | — |
| Row 11 | Collected Short Margin (Delivery) | Collected Short Margin (MTM/crystallised) | — | — | — | — | — |

**Header rows (skip):** 0 (section), 1 (labels), 3 (labels), 5 (spacer), 6 (section), 7 (labels), 9 (section), 10 (labels).

**Field name map (use these for all data lookups):**

| Semantic Label | API Field Name | Notes |
|---|---|---|
| EOD Margin Available | `eod_margin_available` | |
| T-Day Unencumbered Balance | `t_day_unencumbered_balance` | |
| Collateral Value | `collateral_value` | |
| EPI Holding Value | `epi_holding_value` | |
| Peak Margin Available | `{seg}_peak_margin_available` | `{seg}` = `fno` for F&O, `eq` for EQ, `cds` for CDS |
| Unpledge Amount | `unpledge_amount` | |
| JV & BP Debit Amount | `jv_bp_debit_amount` | |
| Total Peak Margin Required | `total_peak_margin_required` | |
| Total Peak Margin Collected | `total_peak_margin_collected` | |
| Total EOD Required | `total_eod_required` | |
| Total EOD Collected | `total_eod_collected` | |
| Collected Short Margin (Delivery) | `{seg}_collected_short_delivery_margin` | `{seg}` = `fo` for F&O, `eq` for EQ, `cds` for CDS; may return "Not available" |
| Collected Short Margin (MTM) | `{seg}_collected_short_margin_on_crystallised_obligation` | Same `{seg}` prefix rules as above; may return "Not available" |

**Segment prefix note:** The API uses inconsistent prefixes for the F&O segment — peak margin uses `fno_` (e.g., `fno_peak_margin_available`) while collected short fields use `fo_` (e.g., `fo_collected_short_delivery_margin`). Use the exact prefix patterns listed above; do not assume uniformity across fields.

### A3 — Penalty Formulas

**Upfront (peak margin) shortfall:**

Shortfall = `total_peak_margin_required` − `total_peak_margin_collected`

If result ≤ 0 → no upfront shortfall, no penalty.

**Non-upfront (EOD margin) shortfall:**

Shortfall = `total_eod_required` − (`{seg}_collected_short_delivery_margin` + `total_eod_collected`)

If result ≤ 0 → no non-upfront shortfall, no penalty.

Both penalty types can apply on the same date as separate ledger entries.

### A4 — Penalty Slabs

| Condition | Rate |
|---|---|
| Shortfall < ₹1L AND < 10% of applicable margin | 0.5% |
| Shortfall ≥ ₹1L OR ≥ 10% of applicable margin | 1.0% |
| Shortfall continues 3+ consecutive days | 5% for each subsequent instance |
| 5+ instances in a calendar month | 5% for every further instance |
| MCX: 3+ instances in a month | 5% from 4th instance |

18% GST is always levied on the penalty amount.

### A5 — Shortfall Causes

| Cause | Explanation |
|---|---|
| Hedge leg closed | Closing the low-risk leg of a hedged position increases margin requirement. CC snapshot captures the peak at that moment. |
| Physical delivery margin | ITM options near expiry attract incremental physical delivery margins (E-4 to expiry day). |
| EOD margin file update | EOD margin file updated after market hours — margin requirement can change after close. |
| MTM loss on futures | Futures MTM losses require funds by T+1 11:59 PM. Failure = non-upfront deficit. |
| Option buying near expiry | Buying options requires only premium, but ITM near expiry → physical delivery margin applies. |
| Intraday not squared off | Intraday trade not squared off → delivery obligation → margin shortfall if insufficient balance. |
| Collateral haircut | Pledged securities valued at less than market value — may not cover full margin requirement. |

### A6 — Physical Delivery Margin Schedule

| Day | Margin Increment |
|---|---|
| E-4 (Wednesday) | 10% of VaR + ELM + Adhoc margins |
| E-3 (Thursday) | 25% |
| E-2 (Friday) | 45% |
| E-1 (Monday) | 70% |

### A7 — Key Facts for Client Communication

- Clearing corporation takes 4 random snapshots during the day (8 for MCX). The highest = peak margin required.
- Even after closing positions, peak margin may have already been captured — shortfall still applies.
- Penalty is exchange-imposed, not Zerodha-imposed. Zerodha passes it on as intermediary.
- Auto square-off and penalty are independent. Penalty is for the period the shortfall existed; square-off happens later to reduce risk.
- Client must add funds by 11:59 PM same day to avoid upfront penalty. Consequences: penalty, increased margin for new positions (₹40 brokerage), potential square-off.
- Penalty posted to ledger on T+6 day (exchange reports on T+5). Narration: "{segment} short-margin penalty for date yyyy-mm-dd".

### A8 — Field Rules

Use the client-friendly labels from the Semantic Label column in A2 when communicating values to the client. API field names, snake_case keys, and row/column indices are internal only.

### A9 — Links

| Topic | URL |
|---|---|
| What is margin penalty | https://support.zerodha.com/category/trading-and-markets/margins/margin-reporting-and-margin-penalty/articles/i-saw-margin-penalty-entries-on-my-ledger-what-is-margin-penalty-and-why-have-i-been-charged |
| Margin penalty calculation | https://support.zerodha.com/category/trading-and-markets/margins/margin-reporting-and-margin-penalty/articles/what-is-margin-penalty-and-how-does-it-work |
| Margin shortfall instances | https://support.zerodha.com/category/trading-and-markets/margins/margin-reporting-and-margin-penalty/articles/margin-shortfall-instances |
| Hedged position penalty | https://support.zerodha.com/category/trading-and-markets/margins/margin-reporting-and-margin-penalty/articles/peak-margin-on-hedged-positions |
| Margin call email explanation | https://support.zerodha.com/category/trading-and-markets/margins/margin-leverage-and-product-and-order-types/articles/a-received-a-margin-call-sms-email-what-is-it |
| Physical settlement policy | https://support.zerodha.com/category/trading-and-markets/trading-faqs/f-otrading/articles/policy-on-physical-settlement |
| Why transfer funds for margin | https://support.zerodha.com/category/trading-and-markets/margins/margin-reporting-and-margin-penalty/articles/transfer-funds-to-cover-margin-shortfalls |

### A10 — DPC vs Margin Penalty Distinction

| | Margin Penalty | DPC (Delayed Payment Charges) |
|---|---|---|
| Charged by | Exchange (Zerodha passes on as intermediary) | Zerodha |
| Trigger | Margin required exceeds margin available at snapshot time | Debit balance (0.05%/day) or excess collateral utilisation (0.035%/day) |
| Ledger narration | "{segment} short-margin penalty for date yyyy-mm-dd" | "Charge for excess collateral utilisation and margin shortfall" |
| Details report | Clientwise Margin Report | DPC Report on Console |

For DPC-specific queries, invoke `delayed_payment_charges`.

### A11 — Escalation Triggers

Escalate to human agent when any of the following occur:
- Client requests refund citing SEBI circular 60/2022 or claims upfront penalties cannot be passed to clients.
- Client requests waiver, reversal, or refund of margin penalty.
- Calculated penalty from report doesn't match ledger entry amount after correct calculation.
- Report data appears inconsistent or missing.

Include when escalating to human agent: client ID, segment, date, report values, and the specific discrepancy or request.

---

## Section B: Decision Flow

### Routing

```
Route by scenario
   ├─ Upfront / peak margin penalty query → Rule 1
   ├─ MTM / EOD margin penalty query (post T+1) → Rule 2
   ├─ Penalty on a specific date, type not stated → Rule 3
   ├─ Where the penalty entry appears in the ledger → Rule 4
   ├─ Sufficient margin claimed yet penalty charged → Rule 5
   ├─ Penalty rate / slab → Rule 6
   ├─ Positions auto squared off but penalty still charged → Rule 7
   ├─ Shortfall notification but no open positions → Rule 8
   ├─ Penalty around expiry / physical settlement → Rule 9
   ├─ Penalty after only buying options → Rule 10
   ├─ Protective leg of a hedge closed first → Rule 11
   ├─ When the penalty will reflect in the ledger → Rule 12
   ├─ Penalty on MCX commodity segment → Rule 13
   ├─ SEBI circular 60/2022 / refund request → Rule 14
   ├─ Penalty waiver or reversal request → Rule 15
   ├─ DPC charges confused with margin penalty → Rule 16
   └─ "Other debits/credits" line in P&L → Rule 17
```

### Fallback

If no root cause is identified after checking all relevant rules → escalate to human agent per A11.

---

## Section C: Rules

### Rule 1 — Upfront Penalty Calculation

1. Calculate upfront shortfall per **A3**.
2. If shortfall ≤ 0 → inform client there was no upfront shortfall; share Peak Margin Required and Peak Margin Collected values.
3. If shortfall > 0 → determine penalty rate per **A4**, calculate penalty + 18% GST, and present the full breakdown (Peak Margin Required, Collected, Shortfall, rate, penalty, GST, total) to the client.

### Rule 2 — Non-Upfront Penalty Calculation

1. If `{seg}_collected_short_delivery_margin` = "Not available" → inform client that T+1 collection data is not yet available and non-upfront penalty cannot be calculated yet.
2. If available: calculate non-upfront shortfall per **A3**.
3. If shortfall ≤ 0 → inform client there is no non-upfront penalty.
4. If shortfall > 0 → determine penalty rate per **A4**, calculate penalty + 18% GST, and present the full breakdown to the client.

### Rule 3 — Both Penalties on Same Date

1. Per **A3**, calculate both upfront and non-upfront penalties independently using Rules 1 and 2 and present both results.

### Rule 4 — Where to Find Penalty in Ledger

1. Direct client to Console → Account → Funds Statement and instruct them to search for the penalty narration per **A7**.
2. Note T+6 posting timeline per **A7**.

### Rule 5 — Why Penalty Despite Having Funds

1. Compare `total_peak_margin_required` vs `total_peak_margin_collected`.
2. Identify the likely cause from **A5**.
3. Explain the CC snapshot mechanism per **A7**.
4. Share Peak Margin Required, Peak Margin Collected, and Shortfall with the client.
5. Share margin shortfall instances link from **A9**.

### Rule 6 — Penalty Slab and Rate

1. Determine the applicable rate from **A4** based on shortfall amount and share with client.
2. Note that 18% GST applies on the penalty amount.

### Rule 7 — Auto Square-Off AND Penalty

1. Explain that auto square-off and margin penalty are independent per **A7**.

### Rule 8 — Shortfall Email but Positions Closed

1. Explain the CC snapshot mechanism per **A7**.
2. Advise client to maintain sufficient funds or add funds upon receiving such a notification.
3. Share margin call email link from **A9**.

### Rule 9 — Expiry Day / Physical Delivery Margin

1. Explain the physical delivery margin schedule per **A6**.
2. Advise client to either close ITM positions before delivery margins apply or add funds to cover the increased requirement.
3. Share physical settlement link from **A9**.

### Rule 10 — Option Buying: Why Penalty

1. Explain that option buying requires only the premium, but ITM options near expiry attract physical delivery margins per **A6**.
2. Note that selling holdings intraday to fund an option purchase and buying them back the same day can create a temporary margin shortfall captured in a CC snapshot.

### Rule 11 — Hedged Position Shortfall

1. Explain hedge leg closure mechanics per **A5**.
2. Advise client to always exit the higher-margin position first when unwinding a hedged trade.
3. Share hedged position penalty link from **A9**.

### Rule 12 — When Penalty Appears

1. Inform client of T+6 posting timeline per **A7**.

### Rule 13 — MCX-Specific Rules

1. Use the same calculation formulas (Rules 1–2) with Company = Zerodha and Segment = FO per **A1** (single ledger).
2. For MCX: CC takes 8 snapshots per day (vs 4 for other segments per **A7**); penalty escalates to 5% from the 4th instance if 3+ shortfall instances occur in a month per **A4**.

### Rule 14 — SEBI Circular Refund Request

1. Escalate to human agent immediately. Do not attempt to explain or deny.
2. Include when escalating to human agent: client ID, penalty dates referenced, and the client's specific claim.

### Rule 15 — Penalty Waiver Request

1. Escalate to human agent immediately.
2. Include when escalating to human agent: client ID, penalty date(s), amount(s), and client's reason for requesting waiver.

### Rule 16 — DPC vs Margin Penalty Confusion

1. Explain the distinction per **A10**.
2. For DPC-specific queries, invoke `delayed_payment_charges`.

### Rule 17 — "Other Debits/Credits" Confusion

1. Invoke `ledger_report`.
2. Direct client to Console → Account → Funds Statement for the relevant date range — each entry carries a narration identifying the charge type.
