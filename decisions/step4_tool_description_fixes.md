# Step 4 — Description rewrites for 6 underperforming tools

Each tool below has a low upvote rate that no tag-routing fix will repair. The "current" description tells Maven too vague a story; the "proposed" version tightens the positive WHEN TO USE scope and removes over-firing trigger keywords.

For 4 of the 6 tools the tighter positive scope is the entire fix — trust the LLM to infer exclusions. For 2 tools (`auto_debit_payins`, `swp_report`) the cousin-tool confusion is real (near-twin tool names with overlapping triggers), so a single "for X, use other_tool instead" line stays in.

Apply by editing the `## Description` block in each tool's file in the maven-protocols repo, then push to Frappe so workers pick up the new description on the next cache refresh.

Order below is by impact (worst tool first).

---

## 1. `get_client_contact` — 3.1% upvote (1/32)

**File:** `miscellaneous/get_client_contact.md`

### Current

```
Get client contact details including email for a client
```

(Single line — no scoping.)

### Why it's mis-picked

Maven picks it for any query mentioning email/phone/contact: change-email requests, send-CMR-to-email requests, generic payment-not-received tickets where the customer leaves a phone number. The description doesn't tell the selector this is an internal helper.

### Proposed

```
WHEN TO USE:

Internal helper. Use only when another tool's protocol explicitly invokes this tool to fetch the client's email or mobile so that another action (statement send, callback) can complete.

The selector should not pick this tool from the customer's prompt alone — it has no customer-facing scope.

TRIGGER KEYWORDS: (none — invoked only by other tools' protocols)
```

---

## 2. `console_eq_tradebook_prepared` — 10.9% upvote (6/55)

**File:** `console_reports/console_eq_tradebook_prepared.md`

### Current

```
WHEN TO USE:

When clients:
- Ask about equity trade history older than 100 days
- Need full tradebook for tax filing, audit, employer compliance, or legal purposes
- Request tradebook since account inception or for a past financial year
- Question tax P&L values and need to verify old trades beyond 100-day window
- Have a closed account and request historical trade data

TRIGGER KEYWORDS: "old trades", "last year trades", "FY 2023-24", "FY 2024-25", "since inception", "full tradebook", "trade history more than 100 days", "historical trades", "closed account tradebook", "tax filing tradebook", "audit", "old tradebook"
```

### Why it's mis-picked

The ">100 days" qualifier is buried in the first bullet and gets overridden by generic terms like "tradebook" or "report". The trigger keyword list also includes broad phrases ("audit", "tax filing tradebook") that fire on tax P&L and capital-gain queries.

### Proposed

```
WHEN TO USE:

Equity trade history STRICTLY older than 100 days from today. Use only when the customer's request explicitly extends beyond the last 100 days, such as:
- A previous financial year (FY older than the current one)
- Trades since account inception
- A closed account's historical trade data
- Tax filing / audit / employer compliance covering a date range entirely beyond 100 days

For the last 100 days of trades, the regular `console_eq_tradebook` is the right tool.

TRIGGER KEYWORDS: "tradebook for FY [past year]", "trades since inception", "trades from [date older than 100 days]", "closed account historical trades"
```

(Removed broad triggers `"audit"`, `"tax filing tradebook"`, `"old trades"` — they fire across too many tools.)

---

## 3. `corporate_action_orders` — 11.1% upvote (2/18)

**File:** `console_reports/corporate_action_orders.md`

### Current

```
WHEN TO USE:

When clients:
- Ask about the status of a buyback, rights issue, or open offer order they placed
- Ask whether their buyback/rights/open offer application was accepted or rejected
- Question allotment price or investment amount for a CA order
- Ask about buyback proceeds or when shares will be debited/credited
- Report applying for a CA but order not showing
- Ask about rights issue allotment status or payment details
- Question why CA order was rejected

TRIGGER KEYWORDS: "buyback order", "buyback status", "rights issue order", "rights issue applied", "open offer order", "tender status", "buyback applied", "buyback accepted", "buyback rejected", "allotment status", "CA order", "corporate action order", "rights allotment", "buyback proceeds", "tender offer"
```

### Why it's mis-picked

The "they placed" qualifier in the first bullet gets diluted by generic CA terms in the rest of the description and the trigger list. Maven picks this for how-to / eligibility / holdings questions about CAs.

### Proposed

```
WHEN TO USE:

Status of a corporate-action ORDER the customer has ALREADY PLACED. Use when:
- Customer asks whether their existing CA application was accepted, rejected, or pending
- Customer asks about allotment price, investment amount, or proceeds for an order they submitted
- Customer reports their submitted CA application not visible after submission
- Customer asks why their CA order was rejected and the order exists in records

TRIGGER KEYWORDS: "buyback order status", "rights bid status", "open offer tender status", "CA order rejected reason", "allotment price for my CA order", "buyback proceeds for my application", "my CA application not showing"
```

(Trigger list trimmed to status-of-existing-order language. Removed the standalone words `"buyback order"`, `"rights issue applied"`, `"allotment status"`, `"buyback proceeds"`, `"tender offer"` — they fire on how-to and eligibility queries too.)

---

## 4. `swp_report` — 15.6% upvote (5/32)  [keeps cousin-tool callout]

**File:** `mf_reports/swp_report.md`

### Current

```
WHEN TO USE:

When clients:
- Ask about SWP status, schedule, or amount
- Report SWP not triggered on expected date
- Ask about next/last SWP date
- Report SWP redemption amount differs from expected

TRIGGER KEYWORDS: "SWP", "systematic withdrawal", "withdrawal plan", "SWP not triggered", "coin"
```

### Why it's mis-picked

The bare keyword `"coin"` fires on any MF query, and the tool's name is one letter away from `stp_report` / `sip_report`. Maven routinely picks `swp_report` for STP and SIP queries.

### Proposed (cousin-tool case — explicit redirect kept)

```
WHEN TO USE:

Mutual-fund SWP (Systematic Withdrawal Plan) on Coin. Use when:
- Customer asks about SWP status, next/last SWP date, configured amount
- Customer reports SWP not triggered on the expected date
- Customer reports SWP redemption amount differs from what was configured
- Customer wants to stop or modify an active SWP

For STP queries use `stp_report`. For SIP / ZSIP queries use `sip_report`. For cashier-side withdrawals from the trading account use `withdrawal_request`.

TRIGGER KEYWORDS: "SWP", "systematic withdrawal plan", "SWP not triggered", "stop SWP", "modify SWP", "SWP next date", "SWP redemption amount wrong"
```

(Dropped bare `"coin"` trigger.)

---

## 5. `console_mf_external_trades` — 24.3% upvote (9/37)

**File:** `mf_reports/console_mf_external_trades.md`

### Current

```
WHEN TO USE:

When clients:
- Report wrong buy average or P&L after transferring MF from another platform
- Report holdings discrepancy for transferred units
- Report XIRR incorrect after transfer
- Ask about external trade entry corrections

TRIGGER KEYWORDS: "transferred from Groww/Kuvera", "wrong buy average", "P&L incorrect after transfer", "discrepancy", "external trade", "XIRR wrong", "coin"
```

### Why it's mis-picked

Trigger keywords `"discrepancy"` and `"coin"` are way too broad — they fire on every MF holdings issue, not just transfers. The tool's actual scope (units brought in from outside Coin) gets lost.

### Proposed

```
WHEN TO USE:

MF units that were transferred INTO Coin from another platform (Groww, Kuvera, Paytm Money, AMC direct, etc.) and are now showing wrong data on Coin. Use when:
- Customer explicitly states the units were transferred or originally bought outside Coin
- Customer reports wrong buy average / cost basis specifically on transferred holdings
- XIRR is wrong AFTER a transfer-in
- Customer needs to correct an external-trade entry

TRIGGER KEYWORDS: "transferred from Groww", "transferred from Kuvera", "transferred from Paytm Money", "external trade entry", "bought outside Coin then transferred", "wrong buy average after transfer", "XIRR wrong after transfer to Coin"
```

(Dropped `"discrepancy"` and `"coin"` — both were over-firing.)

---

## 6. `auto_debit_payins` — 33.3% upvote (9/27)  [keeps cousin-tool callout]

**File:** `cashier_reports/auto_debit_payins.md`

### Current

```
WHEN TO USE:

When clients:
- Ask about status of an auto-debit / eMandate fund transfer to Kite
- Report money debited from bank via mandate but not reflecting in Kite
- Report auto-debit failed or was not attempted
- Ask why funds were debited a day early
- Ask when auto-debit amount will appear in Kite balance
- Report SIP order failing despite having mandate set up

TRIGGER KEYWORDS: "auto debit", "mandate debit", "schedule debit", "funds not credited", "mandate debit delayed", "auto pay", "NACH debit", "emandate debit", "stock SIP funds", "mandate failed", "debit not reflecting"
```

### Why it's mis-picked

This is a true cousin-tool case: `auto_debit_payins` (cashier auto-debit → Kite trading balance) is one of three near-twin mandate tools. Triggers `"mandate debit"`, `"emandate debit"`, `"stock SIP funds"`, `"mandate failed"` all match MF-mandate queries that should go to `mandate_debit_report`.

### Proposed (cousin-tool case — explicit redirects kept)

```
WHEN TO USE:

Cashier-side auto-debit that pulls money from the customer's bank into the Kite TRADING BALANCE via an active eMandate. Use when:
- Customer reports auto-debit to Kite balance failed or didn't happen
- Customer reports money debited from bank via cashier eMandate but not visible in the Kite trading balance
- Customer asks why funds were debited a day early
- Customer asks when an auto-debited amount will appear in Kite
- Kite stock SIP (equity SIP) failed because the cashier auto-debit didn't trigger

For MF SIP / ZSIP mandate debits (bank → AMC, never via Kite balance) use `mandate_debit_report`. For mandate creation / activation / cancellation use `e_mandate_report`. For mandate schedule changes use `e_mandate_schedule_report`.

TRIGGER KEYWORDS: "Kite balance auto-debit", "auto-debit to Kite failed", "stock SIP auto-debit not triggered", "Kite eMandate not pulling funds", "Kite balance not credited after mandate", "auto-pay to trading account"
```

(Dropped broad triggers `"mandate failed"`, `"emandate debit"`, `"stock SIP funds"`, `"debit not reflecting"`, `"mandate debit"` — they fire on MF SIP queries.)

---

## How to apply

For each tool:
1. Open the file (`<category>/<tool_name>.md`) in the maven-protocols repo.
2. Replace the body of the `## Description` block with the proposed text above (keep the `# tool_name` header line and `## Protocol` line untouched).
3. Push to Frappe via the usual flow so st-workflow workers pick up the new description on the next cache refresh.
4. Do them one at a time in the order above (highest impact first), and watch the upvote rate per tool over the next 24–48 hours.

If you want me to apply any of these to the maven-protocols files directly, say which ones (e.g., "apply all 6" or "apply 1, 2, 4 only") and I'll edit them — per the repo's CLAUDE.md, I don't touch tool files without explicit approval.

## Expected impact

| Tool | Now | Target |
|---|---:|---:|
| get_client_contact | 3.1% | volume should drop sharply once selector stops picking it from prompt alone |
| console_eq_tradebook_prepared | 10.9% | 50%+ |
| corporate_action_orders | 11.1% | 50%+ |
| swp_report | 15.6% | 55%+ |
| console_mf_external_trades | 24.3% | 55%+ |
| auto_debit_payins | 33.3% | 60%+ |
