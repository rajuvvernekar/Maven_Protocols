# clientwise_margin_report

## Description

WHEN TO USE:

When client asks:
- About margin penalty calculation, breakdown, or explanation
- Questions why a margin shortfall occurred despite having funds
- How much margin penalty was or will be charged
- Where to find margin penalty entries in their ledger/statement
- About upfront vs non-upfront margin penalty difference
- About penalty slab rates, escalation rules, or 5% penalty
- Why both auto square-off and margin penalty were charged
- About margin shortfall email when positions are already closed
- Questions peak margin vs EOD margin difference
- About MCX margin penalty specifics
- About expiry day margin increase, ELM, or physical delivery margin
- About hedged position margin shortfall after closing one leg
- When margin penalty will appear in their account
- Why margin penalty was charged when they only bought options

TRIGGER KEYWORDS: "margin penalty", "short margin", "shortfall penalty", "peak margin", "upfront margin penalty", "non-upfront penalty", "margin shortfall", "margin shortfall penalty", "short-margin penalty", "margin penalty calculation", "5% penalty", "penalty slab", "margin required vs available", "peak margin required", "EOD margin", "margin penalty MCX", "margin penalty NSE", "margin penalty F&O", "T+5", "T+6 penalty", "shortfall email", "add funds shortfall", "margin call", "margin utilisation exceeded"

## Protocol

# CLIENTWISE MARGIN REPORT PROTOCOL


### A1 — Report Fundamentals

- Report is a fixed 12-row × 7-column grid (`col_1`–`col_7`); meaning determined by row+column position (0-indexed).
- Inputs: Company, Segment, Client ID, Report Date (T-Day from `ledger_report` narration).
- Company mapping: Zerodha = EQ/FO/CDS (all NSE segments); Zerodha Commodities Pvt Ltd = MCX commodity; Zerodha Securities Pvt Ltd = never used.
- Date can be fetched from `ledger_report` penalty entry narration: "{segment} short-margin penalty for date yyyy-mm-dd".
- Segment prefix in labels changes: EQ/FO/CDS depending on segment input.
- Row 11 can return string "Not available" instead of float — means T+1 data not yet available.

### A2 — Report Grid Map

**Value rows:**

| Row | col_1 | col_2 | col_3 | col_4 | col_5 | col_6 | col_7 |
|---|---|---|---|---|---|---|---|
| Row 2 | EOD Margin available | T day unencumbered balance | Collateral Value | EPI Holding Value | — | — | — |
| Row 4 | Peak margin available | T day unencumbered balance | Collateral Value | EPI Holding Value | Unpledge Amount | JV and BP Debit Amount | Delivery Buy value |
| Row 8 | Total Peak Margin Required | Total Peak Margin Collected | Total EOD Required | Total EOD Collected | — | — | — |
| Row 11 | Collected Short Margin Additional Margin | Collected Short Margin On MTM loss (may be "Not available") | — | — | — | — | — |

**Header rows (skip):** 0 (section), 1 (labels), 3 (labels), 5 (spacer), 6 (section), 7 (labels), 9 (section), 10 (labels).

### A3 — Penalty Formulas

**Upfront (peak margin) shortfall:**
Shortfall = Total Peak Margin Required (row 8, col_1) − Total Peak Margin Collected (row 8, col_2).
If result ≤ 0 → no upfront shortfall, no penalty.

**Non-upfront (EOD margin) shortfall:**
Shortfall = Total EOD Required (row 8, col_3) − (Collected Short Margin Additional (row 11, col_1) + Total EOD Collected (row 8, col_4)).
If result ≤ 0 → no non-upfront shortfall, no penalty.
Dependency: requires row 11 data (T+1 collection). If "Not available", non-upfront penalty cannot be calculated yet.

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

**Communication rule:** Always translate grid positions to client-friendly labels. E.g., "Your Peak Margin Required was ₹X" — never "col_1 row 8 = X".

**Internal reasoning only (never share with client):** raw field names (`col_1` through `col_7`), internal row indices.

### A9 — Links

| Topic | URL |
|---|---|
| What is margin penalty | https://support.zerodha.com/category/trading-and-markets/margins/margin-reporting-and-margin-penalty/articles/i-saw-margin-penalty-entries-on-my-ledger-what-is-margin-penalty-and-why-have-i-been-charged |
| Margin penalty calculation | https://support.zerodha.com/category/trading-and-markets/margins/margin-reporting-and-margin-penalty/articles/margin-penalty-calculation |
| Margin shortfall instances | https://support.zerodha.com/category/trading-and-markets/margins/margin-reporting-and-margin-penalty/articles/margin-shortfall-instances |
| Hedged position penalty | https://support.zerodha.com/category/trading-and-markets/margins/margin-reporting-and-margin-penalty/articles/peak-margin-on-hedged-positions |
| Margin call email explanation | https://support.zerodha.com/category/trading-and-markets/margins/margin-leverage-and-product-and-order-types/articles/a-received-a-margin-call-sms-email-what-is-it |
| Physical settlement policy | https://support.zerodha.com/category/trading-and-markets/trading-faqs/f-otrading/articles/policy-on-physical-settlement |
| Why transfer funds for margin | https://support.zerodha.com/category/trading-and-markets/margins/margin-reporting-and-margin-penalty/articles/why-should-clients-transfer-funds-to-cover-margin-shortfalls |

### A10 — DPC vs Margin Penalty Distinction

| | Margin Penalty | DPC (Delayed Payment Charges) |
|---|---|---|
| Charged by | Exchange (Zerodha passes on as intermediary) | Zerodha |
| Trigger | Margin required exceeds margin available at snapshot time | Debit balance (0.05%/day) or excess collateral utilisation (0.035%/day) |
| Ledger narration | "{segment} short-margin penalty for date yyyy-mm-dd" | "Charge for excess collateral utilisation and margin shortfall" |
| Details report | Clientwise Margin Report | DPC Report on Console |

For DPC-specific queries, redirect to the Delayed Payment Charges protocol.

### A11 — Cross-Reference Protocols

| Topic | Refer to |
|---|---|
| Penalty entries on ledger (narration, date lookup) | Ledger Report protocol |
| DPC (debit balance / excess collateral charges) | Delayed Payment Charges protocol |

### A12 — Escalation Triggers (Consolidated)

Escalate when any of the following occur:
- Client requests refund citing SEBI circular 60/2022 or claims upfront penalties cannot be passed to clients.
- Client requests waiver, reversal, or refund of margin penalty.
- Calculated penalty from report doesn't match ledger entry amount after correct calculation.
- Report data appears inconsistent or missing.
- Row 11 shows "Not available" and client needs non-upfront penalty calculation — advise to check back after T+1 data is posted.

Include in escalation: client ID, segment, date, report values, and the specific discrepancy or request.


### Preflight (run on every query)

1. Identify the penalty date: check `ledger_report` for entries with narration "{segment} short-margin penalty for date yyyy-mm-dd" or use the date provided by the client.
2. Determine Company and Segment from the penalty context (per **A1** company mapping).
3. Fetch the clientwise margin report for the identified date, company, and segment.
4. Apply field protection per **A8** — never expose raw grid field names or row indices.
5. Check row 11 for "Not available" — if present, non-upfront calculation is not yet possible.
6. Format all amounts with ₹ and Indian comma notation.

### Routing Tree

```
Query relates to margin penalty →
│
├─ Client asks about upfront / peak margin penalty
│  → Rule 1
│
├─ Client asks about non-upfront / EOD margin penalty
│  → Rule 2
│
├─ Client asks about penalty for a specific date (type unspecified)
│  → Rule 3 (Check both)
│
├─ Client asks where to find penalty in ledger
│  → Rule 4
│
├─ Client says they had sufficient margin but got penalty
│  ├─ General → Rule 5
│  ├─ Positions were auto squared off → Rule 7
│  ├─ Received notification but no open positions → Rule 8
│  └─ Only bought options → Rule 10
│
├─ Client asks about penalty rate / slab
│  → Rule 6
│
├─ Client asks about expiry week / physical delivery margin
│  → Rule 9
│
├─ Client asks about hedged position shortfall
│  → Rule 11
│
├─ Client asks when penalty will appear
│  → Rule 12
│
├─ MCX-specific penalty query
│  → Rule 13
│
├─ Client cites SEBI circular / requests refund
│  → Rule 14 (Escalate)
│
├─ Client requests waiver / reversal
│  → Rule 15 (Escalate)
│
├─ Client confuses DPC with margin penalty
│  → Rule 16
│
├─ Client asks about "other debits/credits" in P&L
│  → Rule 17
│
└─ Data mismatch / no root cause found
   → Rule 18 (Escalation)
```

### Scope

- Address: margin penalty calculations, shortfall explanations, penalty slabs, and related ledger entries.

### Fallback

If no root cause is identified after checking all relevant rules → escalate per Rule 18.


### Rule 1 — Upfront Penalty Calculation

1. Pull the report for the penalty date, segment, and company.
2. Calculate shortfall using the upfront formula from **A3**.
3. If shortfall ≤ 0: "There was no upfront margin shortfall on [date] for [segment]. The margin collected (₹[collected]) was sufficient to cover the peak margin required (₹[required])."
4. If shortfall > 0: determine penalty rate per **A4**, calculate penalty + 18% GST.
5. Respond:
   "Your upfront margin shortfall for [segment] on [date]:
   Peak Margin Required: ₹[required]
   Peak Margin Collected: ₹[collected]
   Shortfall: ₹[shortfall]
   Penalty rate: [rate]%
   Penalty: ₹[penalty]
   GST (18%): ₹[gst]
   Total penalty: ₹[total]"

### Rule 2 — Non-Upfront Penalty Calculation

1. Pull the report for the penalty date.
2. Check row 11, col_1: if "Not available" → "The T+1 shortfall collection data is not yet available for [date]. Non-upfront penalty can only be calculated after this data is posted. Please check back later."
3. If available: calculate shortfall using the non-upfront formula from **A3**.
4. If shortfall ≤ 0 → no non-upfront penalty.
5. If shortfall > 0 → determine penalty rate per **A4**, calculate penalty + 18% GST. Present breakdown in the same format as Rule 1.

### Rule 3 — Both Penalties on Same Date

1. Check both upfront and non-upfront shortfall. A client can be charged both penalties for the same date — they are separate entries on the ledger (per **A3**).
2. Calculate each independently per Rules 1 and 2. Present both results.

### Rule 4 — Where to Find Penalty in Ledger

1. Respond: "Margin penalty entries appear in your funds statement on Console. Search for entries with the narration '{segment} short-margin penalty for date yyyy-mm-dd'. For example, 'NSE F&O short-margin penalty for date 2025-10-28'."
2. Add: "You can filter by date range on Console → Account → Funds Statement. Penalty is posted on T+6 day (6 trading days after the shortfall date)." (Per **A7**.)

### Rule 5 — Why Penalty Despite Having Funds

1. Pull the report and check Peak Margin Required vs Collected.
2. Identify the likely cause from **A5** based on the data.
3. Respond: "The clearing corporation takes 4 random snapshots during the day to capture your margin requirement. The highest margin from these snapshots is the peak margin required. Even if you had sufficient funds at other times, a shortfall at the snapshot moment triggers the penalty." (Per **A7**.)
4. Present the margin data:
   "Your margin data for [date]:
   Peak Margin Required: ₹[required]
   Peak Margin Collected: ₹[collected]
   Shortfall: ₹[shortfall]"
5. Add applicable cause explanation from **A5**: "Common reasons for unexpected shortfall: exiting one leg of a hedged position, EOD margin increase after market hours, or collateral not covering full requirement due to haircuts."
6. Share link: margin shortfall instances from **A9**.

### Rule 6 — Penalty Slab and Rate

1. Share only the applicable rate based on shortfall amount, using **A4**.
2. Always note: "18% GST is levied on all penalty amounts."

### Rule 7 — Auto Square-Off AND Penalty

1. Respond: "Auto square-off and margin penalty are independent actions (per **A7**). The margin penalty is charged by the exchange based on the shortfall at the time of the snapshot — this happens before or regardless of any square-off. Auto square-off is done by the RMS team to reduce further risk, but it doesn't reverse the penalty for the period the shortfall existed."
2. Add: "Even if your positions were squared off, the clearing corporation had already captured the margin shortfall in its snapshot, and the penalty applies for that instance."

### Rule 8 — Shortfall Email but Positions Closed

1. Respond: "A peak margin shortfall can occur due to various reasons during market hours. The clearing corporation takes four random snapshots of your margin requirement throughout the day. The highest margin among these snapshots is considered the peak margin required for the day. If your available margin doesn't meet this requirement, a margin shortfall occurs, and we notify clients to bring in additional funds." (Per **A7**.)
2. Add: "Even if you've closed your position, the peak margin might have already been captured. By the end of the day, if you do not have funds to meet the peak margin requirement, you will receive this notification. To avoid this, maintain sufficient funds or add funds when you receive such notification."
3. Share link: margin call email from **A9**.

### Rule 9 — Expiry Day / Physical Delivery Margin

1. Respond using the schedule from **A6**: "ITM (in-the-money) stock options and futures attract incremental physical delivery margins in the last week before expiry:
   - E-4 day (Wednesday): 10% of VaR + ELM + Adhoc margins
   - E-3 day (Thursday): 25%
   - E-2 day (Friday): 45%
   - E-1 day (Monday): 70%"
2. Add: "If you don't maintain sufficient margin for these increased requirements, a shortfall will occur and the exchange will charge a penalty. To avoid this, either close your ITM positions before delivery margins kick in, or add funds to cover the increased requirement."
3. Share link: physical settlement from **A9**.

### Rule 10 — Option Buying: Why Penalty

1. Respond: "When you buy options, the margin required is limited to the premium paid. However, if your option becomes in-the-money (ITM) close to expiry, physical delivery margins apply starting from 4 days before expiry (per **A6**). These margins increase daily and can cause a shortfall if you don't have sufficient funds."
2. Add: "Additionally, if you sell some holdings to fund your option purchase and buy them back the same day, settlement timing can create a temporary margin shortfall that the clearing corporation captures in its snapshot."

### Rule 11 — Hedged Position Shortfall

1. Respond: "When you hold a hedged position (e.g., long futures + long put), the margin requirement is reduced due to the hedge benefit. If you close the protective leg (e.g., sell the put) before closing the higher-risk leg (e.g., futures), the margin requirement increases significantly." (Per **A5** hedge leg closed.)
2. Add: "If the clearing corporation captures a snapshot at this moment, the increased margin is recorded as the peak requirement — and if your available margin doesn't cover it, a shortfall occurs."
3. Advice: "To avoid this, always exit the higher-margin position first when unwinding a hedged trade."
4. Share link: hedged position penalty from **A9**.

### Rule 12 — When Penalty Appears

1. Respond: "Margin penalties are reported by the exchange on T+5 days (5 trading days after the shortfall date). Zerodha posts the penalty entry to your funds statement on the T+6th day once the penalty file is received from the exchange. The entry appears with the narration '{segment} short-margin penalty for date yyyy-mm-dd'." (Per **A7**.)

### Rule 13 — MCX-Specific Rules

1. Use the same calculation formulas (Rules 1–2) with Company = Zerodha Commodities Pvt Ltd, Segment = EQ (per **A1** company mapping).
2. Key MCX difference: "For MCX, if the exchange reports 3 or more margin shortfall instances in a month (consecutive or separate), the penalty escalates to 5% from the 4th instance (per **A4**). The clearing corporation takes 8 random snapshots for the commodity segment (vs 4 for other segments per **A7**)."

### Rule 14 — SEBI Circular Refund Request

1. Escalate immediately. Do not attempt to explain or deny.
2. Include in escalation: client ID, penalty dates referenced, and the client's specific claim.

### Rule 15 — Penalty Waiver Request

1. Escalate immediately.
2. Include in escalation: client ID, penalty date(s), amount(s), and client's reason for requesting waiver.

### Rule 16 — DPC vs Margin Penalty Confusion

1. Respond using the distinction from **A10**:
   "Delayed payment charges (DPC) and margin penalties are different:
   - Margin penalty: charged by the exchange when margin required exceeds margin available at snapshot time. Appears as '{segment} short-margin penalty for date yyyy-mm-dd'.
   - DPC: charged by Zerodha on debit balances (0.05%/day) or excess collateral utilisation (0.035%/day). Appears as 'Charge for excess collateral utilisation and margin shortfall'."
2. Add: "For DPC details, check the Delayed Payment Charges report on Console."
3. Redirect to DPC protocol for DPC-specific queries (per **A11**).

### Rule 17 — "Other Debits/Credits" Confusion

1. Redirect to Ledger Report protocol (per **A11**): "The 'Other credits & debits' section in your P&L includes various charges like margin penalties, DPC, DP charges, pledge charges, AMC, etc. To identify what each debit is for, check your funds statement on Console for the specific date range — each entry will have a narration explaining the charge."

### Rule 18 — Escalation

Escalate when any trigger in **A12** is met.

Include in escalation: client ID, segment, date, report values, and the specific discrepancy or request.

