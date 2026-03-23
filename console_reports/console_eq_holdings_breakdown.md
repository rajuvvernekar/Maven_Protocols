# console_eq_holdings_breakdown

## Description

WHEN TO USE:

When clients:
- Question buy average and need to walk through the FIFO calculation entry by entry
- Ask to see the breakdown of their holdings for a specific stock
- Report breakdown not matching tradebook or missing entries
- Ask about LIQUIDBEES or ETF dividend reinvestment entries (fractional units at price 0)
- Need verification if a corporate action entry (bonus, split, dividend reinvestment, merger, demerger) was posted
- Need confirmation if an external/discrepant trade entry is reflected in the breakdown
- Need to check if a specific buy/sell trade is included in the holdings calculation

TRIGGER KEYWORDS: "breakdown", "view breakdown", "holdings breakdown", "FIFO calculation", "how average calculated", "trade entries", "dividend reinvestment", "LIQUIDBEES dividend", "bonus entry", "split entry", "breakdown missing", "breakdown not showing"

## Protocol

# CONSOLE EQ HOLDINGS BREAKDOWN PROTOCOL

---

## Section A: Reference Data

---

### A1 — Tool Purpose & Fundamentals

This tool shows **all entries** impacting holdings for a stock: regular trades + external trades + corporate action credits/debits. Each entry shows how the holding qty was built or adjusted over time — the complete audit trail.

Buy average is calculated from these entries using FIFO —  use this to walk through entries to verify. Breakdown reflects the same data that drives buy average and P&L on Console — if breakdown is correct, avg and P&L are correct.

Breakdown entries may be delayed by up to 1 day after trade execution due to file processing.

**Input:** Client ID + tradingsymbol/ISIN.

---

### A2 — Field Usage Rules

**Shareable fields:**

`tradingsymbol` | `isin` | `price` | `quantity` | `exchange` | `order_execution_time` | `external_trade_type` | `trade_type` | `trade_id` | `order_id`

**Internal-only fields** (use for reasoning; communicate outcomes in plain language):

`client_id` | `instrument_id` | `pseudo_trade` | `corporate_action_id` | `pledged`

**Client-facing terminology:**

| Internal Term | Client-Facing Alternative |
|---|---|
| pseudo_trade = true | "system entry" or "corporate action entry" |
| corporate_action_id | "corporate action entry" (reference the CA type, not the ID) |
| pledged | (use internally to check pledge status; describe outcome to client) |
| Any internal field name or system term | (describe the outcome, not the field) |

---

### A3 — Entry Type Identification

| Detection Logic | Entry Type | Description |
|---|---|---|
| `exchange` = NSE/BSE, `pseudo_trade` = false, `external_trade_type` = blank | Regular trade | Normal buy/sell from tradebook |
| `exchange` = DIVIDEND, `price` = 0, fractional qty, `pseudo_trade` = true | Dividend reinvestment | ETF/MF dividend unit credit (e.g., LIQUIDBEES, GOLDBEES). Directly impacts avg price. |
| `price` = 0, `pseudo_trade` = true, `corporate_action_id` populated | Bonus credit | Bonus shares credited at zero cost |
| `pseudo_trade` = true, `corporate_action_id` populated (qty/price adjusted) | Split adjustment | Qty multiplied, price divided per split ratio |
| `external_trade_type` populated (discrepant/buyback/IPO/gift/ESOP/internal_transfer) | External entry | Came from external trades system |

---

### A4 — Cross-Reference Tools

| Tool | When to Use |
|---|---|
| `console_eq_holdings` | Current holdings summary with buy avg. If avg appears wrong, use breakdown to trace FIFO entry by entry. |
| `console_eq_tradebook` | Regular exchange trades. Breakdown should include all tradebook entries plus CA and external entries. |
| `console_eq_external_trades` | External entries only. Breakdown includes these; use external trades tool to check if a specific entry was posted. |
| `console_eq_pnl` | Realized P&L. Both breakdown and P&L are computed from the same FIFO logic. |

---

### A5 — CA Entry Timelines

| Corporate Action | Expected Entry Timeline |
|---|---|
| Bonus | T+2 from record date |
| Split | Immediate (on record date) |
| Demerger | 30–45 days from record date |

If beyond expected timeline and CA entry not found → escalate.

---

### A6 — Escalation Data Template

When escalating, always include: **client ID, tradingsymbol, ISIN, specific missing/wrong entries, and dates.**

---

### A7 — Response Templates

**R1 — FIFO walkthrough (intro):**
"Here is the breakdown of your [tradingsymbol] holdings:
[Date] — [Buy/Sell] [qty] shares at ₹[price] ([exchange/source])
[...continue for all entries...]

Your buy average is calculated using FIFO — when you sell, the oldest purchased shares are consumed first, changing the average of remaining shares."

**R2 — FIFO sell consumption explanation (append to R1 when sells exist):**
"When you sold [qty] on [date], the oldest [qty] shares bought at ₹[price] on [buy date] were consumed."

**R3 — FIFO verification conclusion:**
"Based on the FIFO calculation from your transaction history, your current buy average of ₹[buy_average] for [remaining qty] shares is correct."

**R4 — Dividend reinvestment:**
"The entries showing ₹0 price with small/fractional quantities for [tradingsymbol] are dividend reinvestment credits. When ETFs like LIQUIDBEES distribute dividends, the dividend amount is reinvested as additional units at zero acquisition cost. These are normal entries and directly impact your buy average calculation."

**R5 — Bonus entry:**
"The entry showing [quantity] shares at ₹0 on [date] is your bonus share credit. Bonus shares are credited at zero cost, which reduces your overall buy average."

**R6 — Split entry:**
"The split adjustment on [date] changed your holding from [old qty] shares to [new qty] shares. The price per share was proportionally adjusted. Your total investment value remains unchanged."

**R7 — Entry delayed (within 1 day):**
"Breakdown entries can take up to 1 trading day to reflect. The trade is recorded in the tradebook and will appear in the breakdown shortly. This delay does not affect your buy average or P&L."

**R8 — Extra entry is external trade:**
"This entry is a [client-facing label per A3] entry — it was recorded for shares received via [transfer/gift/IPO/ESOP/buyback]. You can verify the details in the external trades section."

**R9 — Extra entry is CA:**
"This is a corporate action entry for [bonus/split/merger/demerger] of [tradingsymbol]."

**R10 — Breakdown loading error (intermittent):**
"The breakdown view is experiencing a temporary issue. Please try again after some time or use a different browser. If the issue persists, we'll investigate further."

---

## Section B: Decision Flow

---

### Preflight (run on every query)

```
1. Identify the stock (tradingsymbol / ISIN) and the client's concern
   (wrong avg, unrecognized entry, missing entry, CA verification, etc.)

2. Load breakdown entries for the stock
```

### Route

```
Intent / Condition                                          → Rule
──────────────────────────────────────────────────────────────────────
Client questions buy average — need to verify via FIFO      → Rule 1
Entries with price = 0 or fractional qty (dividend/ETF)     → Rule 2
Bonus or split entries in breakdown                         → Rule 3
Trade in tradebook but missing from breakdown               → Rule 4
Unrecognized entries in breakdown                           → Rule 5
Breakdown page not loading / error                          → Rule 6
Client insists buy average is wrong — need to prove it      → Rule 7
Verify if a specific CA was posted in breakdown             → Rule 8
```

### Scope

- Address the client's query about their holdings breakdown entries, FIFO calculation, and entry verification.
- Use **A2** field rules and client-facing terminology in all client communication.
- Translate internal entry types using **A3** detection logic; describe entries by their purpose, not internal field names.

### Fallback

If no route matches, cross-reference with **A4** tools for additional context. If no root cause is found, escalate per **A6**.

---

## Section C: Rules

---

### Rule 1 — Walk Through FIFO Calculation

1. List all entries for the tradingsymbol chronologically.
2. For each entry show: date, trade_type (buy/sell), quantity, price, and source (identify via **A3**: exchange trade / corporate action / external entry / dividend reinvestment).
3. Respond per **A7-R1**.
4. If sell entries exist, explain FIFO consumption per **A7-R2** — show which buy entries each sell consumed.

---

### Rule 2 — Dividend Reinvestment Entries

1. Identify entries via **A3** (exchange = DIVIDEND, price = 0, fractional qty, pseudo_trade = true).
2. Respond per **A7-R4**.

---

### Rule 3 — Bonus / Split Entries in Breakdown

1. Identify entry type via **A3**.
2. Bonus (price = 0, CA entry) → respond per **A7-R5**.
3. Split (qty/price adjusted, CA entry) → respond per **A7-R6**.

---

### Rule 4 — Entry Missing from Breakdown

1. Check if the trade was executed within the last 1 trading day — breakdown entries may be delayed up to 1 day due to file processing (per **A1**).
2. If trade was yesterday → respond per **A7-R7**.
3. If trade was 2+ trading days ago and still not in breakdown → escalate per **A6**.

---

### Rule 5 — Unrecognized Entries in Breakdown

1. Check the entry type via **A3**:
   a. `external_trade_type` populated → respond per **A7-R8**.
   b. `exchange` = DIVIDEND → respond per **A7-R4** (Rule 2).
   c. Corporate action entry (price = 0, system entry) → respond per **A7-R9**.
   d. None of the above explain it → escalate per **A6** as potential breakdown-tradebook mismatch.

---

### Rule 6 — Breakdown Not Loading / Error

1. Try a different stock to confirm if the issue is stock-specific or account-wide.
2. Stock-specific → may be a data issue for that ISIN. Escalate per **A6** with client ID and tradingsymbol.
3. Account-wide → respond per **A7-R10**. If persists beyond 24 hours → escalate per **A6**.

---

### Rule 7 — Verifying Buy Average is Correct

The breakdown contains all entries (buys, CAs, external entries) that make up the current holding. Calculate the weighted average directly from these entries:
a. List all entries chronologically with qty and price.
b. Weighted average = total value of all entries / total quantity.
Respond per A7-R3.
If the calculation does not match what console_eq_holdings shows → escalate per A6.

---

### Rule 8 — Corporate Action Entry Verification

1. Look for entries matching CA patterns in **A3**: price = 0 (bonus), or entries around the CA date with adjusted qty/price (split/merger/demerger).
2. If CA entry found → confirm with date, qty, price.
3. If CA entry not found → check expected timeline per **A5**. If beyond expected timeline → escalate per **A6**.

---

## Section D: General Notes

- Breakdown is the complete audit trail — it includes regular trades, external trades, and corporate action entries combined.
- LIQUIDBEES/ETF dividend reinvestments appear as exchange = "DIVIDEND", price = 0 with fractional qty. These are normal and directly impact average price.
- `pledged` field shows if a specific entry's qty is currently pledged (internal use only).
- Breakdown entries may lag trade execution by up to 1 trading day due to file processing.
- If breakdown is correct, buy average and P&L on Console are also correct — they use the same underlying data.
