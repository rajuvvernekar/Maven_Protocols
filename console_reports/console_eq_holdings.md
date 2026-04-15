# console_eq_holdings

## Description

WHEN TO USE:

When clients:
- Ask about equity holdings quantity, buy average, or invested value
- Report shares not visible, missing, or showing wrong quantity
- Report buy average is wrong, showing N/A, or showing 0
- Report discrepancy in holdings (transferred shares, IPO, off-market, gift, ESOP)
- Ask about corporate action impact on holdings (bonus, split, merger, demerger, rights)
- Ask why bonus/split/demerger shares not credited yet
- Ask about pledged quantity showing in holdings
- Ask about T1 holdings or settlement timing
- Ask about dividend credit, tracking, or TDS on dividends
- Ask about corporate action eligibility (ex-date, record date)
- Report investment value mismatch in holdings

TRIGGER KEYWORDS: "holdings", "buy average", "average price", "discrepancy", "not visible", "missing shares", "bonus not credited", "split", "demerger", "merger", "pledged", "T1", "settlement", "dividend", "invested value", "buy value", "wrong price", "showing 0", "showing N/A", "transferred shares", "gift shares", "ESOP", "corporate action", "record date", "ex-date", "fractional shares"

## Protocol

# CONSOLE EQ HOLDINGS PROTOCOL

---

## Section A: Reference Data

---

### A1 — Fundamentals

This tool looks up a client's equity holdings. Buy average uses FIFO (First In, First Out). Holdings = available + t1 + margin + pending + discrepant + loan (`total_quantity`). `buy_value` = `buy_average` × `total_quantity`.

---

### A2 — Field Usage Rules

**Shareable fields:**

`tradingsymbol` | `isin` | `buy_average` | `buy_value` | `available` | `t1` | `margin` | `discrepant` | `loan` | `total_quantity`

**Internal-only fields** (use for reasoning; communicate outcomes in plain language):

`name` | `instrument_id` | `holdings_date` | `closing_price` | `failure_date` | `pending`

**Client-facing terminology:**

| Internal Term | Client-Facing Alternative |
|---|---|
| pending | "being processed for credit" or "yet to be credited" |
| failure_date | (omit — use for internal escalation only) |
| holdings_date | (omit — internal modification timestamp) |
| instrument_id | (omit — internal system mapping) |

---

### A3 — Quantity Field Definitions

| Field | Meaning |
|---|---|
| `available` | Free qty for trading/selling |
| `t1` | Yesterday's buy — settles end of today |
| `margin` | Pledged or blocked for collateral; still in client demat |
| `pending` | Qty expected from corporate action — not yet credited to demat |
| `discrepant` | Qty mismatch between tradebook and demat holdings file; common for transfers, IPOs, off-market, gifts |
| `loan` | Qty lent via SLB or pledged outside Zerodha (NBFC/LAS) |
| `total_quantity` | Sum of all above fields |

---

### A4 — Timelines

| Event | Timeline |
|---|---|
| T+1 settlement (shares visible in holdings) | T+1 day (bought Monday → holdings Tuesday) |
| Bonus share credit | T+2 from record date; tradeable after 4–5 days (temp ISIN → perm ISIN) |
| Corporate action buy average adjustment | ~2 weeks from corporate action date |
| Demerger new entity share credit | 30–45 days from record date |
| Discrepant entry buy average update | Within 24 hours of adding entry |
| Dividend credit to primary bank | 30–45 days after ex-date/record date |
| Split share buy average update | 2–3 working days after split shares are credited |

---

### A5 — Buy Average Rules

**Method:** FIFO — sell oldest shares first. Mandated by the Income Tax Department.

**Intraday exception:** Sell from holdings + buy back same day → average unchanged (treated as separate speculative transactions, not delivery).

**T2T exception:** Trade-to-Trade stocks — buy average updates to latest purchase price since all T2T trades are delivery.

**Transfer in:** Shows as discrepancy → client adds buy average via the self-resolution path in **A8**.

**Transfer-in entry rules:** Date must be ≤ demat credit date. Only 1 entry per ISIN per date. No holidays/weekends. Same-date multiple buys = weighted average, total qty.

**Gift transfer in:** Closing price on transfer date used as entry price (gift only — off-market transfers require manual discrepancy entry).

**Buy average null reasons:** Discrepant without entry | Transfer without manual update | CA in progress | ESOP/off-market without entry.

**Buy average ₹0 reason:** Only bonus shares remain after FIFO sold all original bought shares (bonus cost = ₹0).

**Grandfather clause (pre-2018 holdings with no purchase records):** If the client purchased shares before 31 Jan 2018 and original purchase records are unavailable, Section 112A of the Income Tax Act provides a grandfathering provision. The cost of acquisition for tax purposes is the higher of: (a) the actual purchase price, or (b) the stock's high price on NSE or BSE on 31 Jan 2018. The client can enter trade date as 31 Jan 2018 and use the high price from that date. Historical prices are available on the NSE and BSE websites.

**Same-day sell FIFO impact:** When shares are sold today using FIFO, the buy average of remaining shares may change. If the earliest lots had a different average than the current market price, the reduction in holdings value will differ from the sale proceeds received. Updated invested value and buy average reflect after end-of-day processing. Client can verify via View breakdown on Kite or Console.

---

### A6 — Corporate Actions

#### Bonus

Free shares to existing shareholders in a ratio (e.g., 2:1). Qty increases; price adjusts proportionally; total value unchanged; bonus shares at cost ₹0. Credit: T+2 from record date; temp ISIN; tradeable after 4–5 days. P&L shows artificial drop until credited — expected, auto-corrects.

#### Split

Shares divided by reducing face value (e.g., 1:5 = 1 becomes 5). Qty multiplied, price divided by ratio; total value unchanged. Client can sell original qty immediately; wait for additional credited shares. Buy average update may take 2–3 working days after split shares are credited; client can sell in the meantime without P&L impact.

#### Consolidation (Reverse Split)

Fewer shares at higher price. Qty reduces, price increases; fractional shares settled in cash to primary bank by company-appointed trustee.

#### Merger

Two companies combine; shares exchanged at defined swap ratio. Old debited, new credited per ratio; fractional shares = cash to primary bank.

#### Demerger

Company splits into separate entities; new shares credited proportionally. Original retained; new entity credited; average split per COA ratio announced by company. New entity shares within 30–45 days from record date (per **A4**).

#### Rights Issue

Existing shareholders buy additional shares at discounted price. REs credited as temp securities before issue; lapse if not used/sold. RE premium not included in rights share average.

#### Eligibility

Hold shares in demat on ex-date/record date. Buy at least 1 trading day before ex-date (T+1 settlement). Selling on ex-date still qualifies (shares debited T+1). Pledged shares eligible for all CA benefits. Exceptions: settlement holiday or short delivery can cause ineligibility even if bought before ex-date.

#### Fractional Shares

Fractional shares from any CA settled in cash by company-appointed trustee → credited to primary bank.

#### Short Delivery

Short delivery occurs when the seller of shares does not deliver them by the settlement deadline. Two common scenarios: (1) Counter-party default — buyer's shares should have been credited by T+1, settlement extends to T+2 while exchange conducts auction. (2) Intraday short sell stuck in circuit — trader unable to close position, results in delivery obligation. In both cases, client receives notification. If auction successful, shares credited. If auction fails, cash settlement at close-out price.

---

### A7 — Dividends

**Credit:** Primary bank account (not trading account); 30–45 days after ex-date/record date (per **A4**).

**Not received:** Contact company's Registrar and Transfer Agent (RTA) — Zerodha does not process dividend payments and does not receive details about dividend credits.

**RTA lookup:** NSE: nseindia.com → search company → Corporate information → Transfer Agent Details. BSE: bseindia.com → search company → Corp Information.

**Failed credit:** RTA issues dividend warrant via courier to registered address.

**TDS:** Resident: 10% above ₹10,000/FY (from FY25-26). NRI: 20%, no threshold. No PAN: 20%.

**Tracking:** Kite: Portfolio → select stock → View dividends. Console: Reports → Downloads → Dividend statement.

**Debt Instrument Interest (G-Secs, NCDs, Bonds):**

Interest on G-Secs, NCDs, and bonds is credited directly to the client's primary bank account by RBI or the paying agent — not through Zerodha's trading account. Zerodha does not process or track debt instrument interest payments.

**Interest payment schedule:** The official schedule published by RBI is available at rbi.org.in/Scripts/NotificationUser.aspx — look for the document titled "Auction for Sale (Issue/Re-issue) of Government Stock (GS)" under Notifications. For older issues, check under Archives.

**Payment method:** Interest is credited semi-annually to the client's primary bank account linked with Zerodha, typically within 5–7 working days of the payment date.

**Eligibility:** To receive interest, the client must have purchased the G-Secs at least 15 days before the interest date.

**Tracking methods for clients:**
1. Bank statements — check primary bank account for the credit
2. CDSL Consolidated Account Statement (CAS) — available via CDSL website
3. RBI Retail Direct portal — if the client has an account there

---

### A8 — Discrepancy Resolution

**Common causes:** Transfer from other broker | IPO | Off-market | Gift | ESOP | CA system delay.

**Self-resolution path:** Console → Portfolio → Holdings → View discrepancy → Select stock → Add trade → Enter date, price, qty.

**Entry rules:** Date must be ≤ demat credit date. Only 1 entry per ISIN per date. No holidays/weekends. Same-date multiple buys = weighted average, total qty.

**Locking:** Entries editable only while status is "Pending"; locked once buy average updated (within 24 hours per **A4**).

**Cannot resolve:** Trading holidays | Inactive/suspended/unlisted stocks (verify current exchange status first — see Rule 6) | CA within 10 days | IPO within 3 days.

**Applies to all instrument types:** Equity, NCDs, bonds, and other securities follow the same discrepancy resolution path. If any instrument was transferred from another broker and shows invested value as NA with `discrepant` > 0, the client must add purchase details via the self-resolution path above.

**Transfer-in note:** Only the units are transferred from the previous broker — the purchase history is not carried over automatically. Client should obtain purchase details from their previous broker.

---

### A9 — Gift & Off-Market Transfer Rules

**Gift transfer in:** Closing price on transfer date used as entry price for P&L tracking (gift only). Off-market transfers require client to manually add buy details via discrepancy flow (**A8**).

**Gift transfer out:** Zerodha uses the gift transfer date as exit date in sender's account; closing price on transfer date as exit price.

**Off-market transfer out:** No automatic exit entry posted — client must provide reversal details or manually edit Tax P&L.

---

### A10 — Pledging in Holdings

`margin` field = pledged/blocked qty; still in client demat.

**Sell without unpledge:** Yes — CNC sell order on Kite; collateral reduces proportionally.

**Temporary collateral reduction:** Selling free qty of a stock that also has pledged qty → collateral temporarily reduces (system considers pledged shares first) → restored automatically next trading day after end-of-day process. No action needed.

**Buyback:** Pledged shares must be unpledged first before buyback tendering.

---

### A11 — Links

| Topic | URL / Path |
|---|---|
| Update buy average (discrepancy) | Console → Portfolio → Holdings → View discrepancy → Add trade |
| Approved securities list | zerodha.com/approved-securities |
| Holdings on Console | console.zerodha.com/portfolio/holdings |
| Redeeming fractional units of LIQUIDBEES | https://support.zerodha.com/category/mutual-funds/understanding-mutual-funds/selling/articles/redeeming-fractional-units |
| NSE historical prices | nseindia.com (search company → Historical Data) |
| BSE historical prices | bseindia.com (search company → Historical Prices) |

---

### A12 — Escalation Data Template

When escalating, always include: **client ID, tradingsymbol(s), specific issue description, and relevant data** (e.g., expected vs actual values, entry details from `console_eq_external_trades`, screenshots if available).

---

### A13 — Discrepancy Diagnostic Checklist

When a client reports a discrepancy or a specific purchase that doesn't match holdings data:

1. Use `console_eq_tradebook_prepared` to fetch all trades from 1-4-2017 to date for that tradingsymbol.
2. Calculate total quantity after applying FIFO (subtract sell qty from buy qty chronologically).
3. Check the `ledger_report` for corresponding credit entries if the client describes a sale or redemption event.
4. Compare calculated qty with `available` qty in `console_eq_holdings`:
   - **If calculated qty = available qty:** Stocks were bought on Zerodha, discrepancy is a display/sync issue → ESCALATE to Support agent with client ID, tradingsymbol, calculated qty, and available qty.
   - **If calculated qty ≠ available qty AND no matching sale proceeds in ledger:** Stocks likely transferred/gifted/IPO/off-market → proceed to self-resolution path (Rule 5).

---

## Section B: Decision Flow

---

### Preflight (run on every query)

```
1. Check `failure_date`
   └─ Has any value → ESCALATE TO SM with client ID, tradingsymbol,
      failure_date. STOP.

2. If client reports qty mismatch or holdings not visible:
   └─ Cross-reference: compare `available` qty in console_eq_holdings
      with `available` qty in console_eq_pseudo_holdings for same ISIN.
      ├─ Both match → qty correct; display-only issue.
      │   Ask client for screenshot of holdings page.
      └─ Mismatch → escalate with both values, client ID, tradingsymbol.
```

### Route

```
Intent / Condition                                        → Rule
────────────────────────────────────────────────────────────────────
Employer-mandated account deactivation or closure         → Escalate to human agent immediately.
  (client mentions employer restrictions, compliance
  requirements, or inability to trade due to employer)

Buy average differs from expected                         → Rule 1
Buy average showing N/A                                   → Rule 2
Buy average showing ₹0                                    → Rule 3
Buy average wrong after corporate action                  → Rule 4
Discrepancy — transferred/gift/ESOP shares                → Rule 5
Discrepancy — error when adding entry                     → Rule 6
Bonus shares not credited / not visible                   → Rule 7
Stock split — qty/price query                             → Rule 8
Demerger — new shares or avg query                        → Rule 9
Merger — share swap query                                 → Rule 10
Holdings not visible / qty mismatch                       → Rule 11
Investment value mismatch                                 → Rule 12
Pledged qty in holdings                                   → Rule 13
Dividend or debt instrument interest query                → Rule 14
Corporate action eligibility                              → Rule 15
T1 / settlement query                                     → Rule 16
Gift / off-market transfer (P&L / avg)                    → Rule 17
Fractional unit redemption (LIQUIDBEES)                   → Rule 18
```

### Scope

- Address the client's query about their equity holdings, buy averages, corporate actions, discrepancies, dividends, debt instrument interest, or pledged stock.
- Employer-mandated account deactivation or closure queries (employer compliance, empanelment) are outside protocol scope — escalate to a human agent immediately.

### Fallback

If no route matches, interpret the holdings data using Section A reference data. If no root cause is found, escalate per **A12**.

---

## Section C: Rules

---

### Rule 1 — Buy Average Differs from Expected

1. Explain the FIFO method (mandated by Income Tax Department, per **A5**). Point client to View breakdown on Kite or Console for detailed calculation.
2. If client sold from holdings and bought back same day → intraday exception: average unchanged because this is treated as a speculative transaction, not delivery (per **A5**).
3. If the client's complaint is about investment value or buy average changing today, check Kite Order History and Kite Positions for same-day executed sell trades. If a sell order was executed today → explain same-day sell FIFO impact (per **A5**).

---

### Rule 2 — Buy Average Showing N/A

1. If `buy_average` is null/N/A AND `discrepant` > 0:
   a. **If client reports a specific purchase (mentions date, quantity, or price of a buy that doesn't match current holdings data), ALWAYS run A13 checklist before proceeding with standard diagnostics.**
   b. Check Kite holdings or instrument search to verify whether the stock is currently listed and tradeable on an exchange. If the stock has since been listed, proceed with standard discrepancy resolution (Rule 5) — do not apply the unlisted exception from Rule 6.
   c. Check `console_eq_external_trades` for an existing entry for this ISIN.
   d. If entry exists AND still processing → inform client that purchase details have been recorded and buy average will update within 24 hours (per **A4**).
   e. If entry exists AND processed but avg still N/A → escalate per **A12** with entry details from `console_eq_external_trades`.
   f. If no entry exists AND A13 confirms stocks NOT bought on Zerodha → guide client through the discrepancy self-resolution path (per **A8**) including entry rules: date ≤ demat credit date, 1 entry per ISIN per date, no holidays/weekends, same-date multiple buys = weighted average with total qty, entries lock once processed within 24 hours.
   g. If client confirms shares were purchased before 31 Jan 2018 and original purchase records are unavailable → guide client per grandfather clause in **A5**: Section 112A provision, cost = higher of actual price or stock's high on NSE/BSE on 31 Jan 2018, enter trade date as 31 Jan 2018 with the high price.

2. If `buy_average` is null AND `discrepant` = 0 AND `pending` > 0:
   → Corporate action buy average adjustment in progress, typically ~2 weeks from the corporate action date (per **A4**).

---

### Rule 3 — Buy Average Showing ₹0

1. If `buy_average` = 0 AND `total_quantity` > 0:
   a. Check `console_eq_holdings_breakdown` for the same stock/ISIN — look for entries where `exchange` field = "BONUS".
   b. If confirmed → explain that all originally purchased shares have been sold via FIFO, and only bonus shares remain. Bonus shares are credited at zero cost, so the average of remaining holdings becomes ₹0. This is correct as per FIFO accounting (per **A5**).
   c. If no BONUS entry found → investigate further (may be a system issue or other CA type). Escalate per **A12** if unexplained.

---

### Rule 4 — Buy Average Wrong After Corporate Action

1. Check if CA was within last 2 weeks → corporate action buy average adjustment in progress, typically ~2 weeks (per **A4**).
2. If CA was 3+ weeks ago and avg still appears wrong → escalate per **A12** with client ID, tradingsymbol, and expected vs actual buy average.

---

### Rule 5 — Discrepancy (Transferred / Gift / ESOP Shares)

**Preflight (before executing Rule 5):**

If client reports a discrepancy or a specific purchase (mentions date, quantity, or price) that doesn't match holdings data, run **A13** checklist first. Only proceed with self-resolution guidance if A13 confirms stocks were NOT bought on Zerodha.

**If client confirms shares were received via Zerodha gift transfer:**

1. Check `console_eq_external_trades` for `external_trade_type` = gift.
2. If entry found → inform client that gift shares have been recorded in the system at the closing price on the transfer date (per **A9**). No further action needed from the client. Buy average will reflect once processed.
3. If no entry found → escalate per **A12**. The system should have auto-posted this entry.

**If client confirms shares were transferred from another broker / ESOP / off-market:**

1. Check `console_eq_external_trades` for an existing entry for this ISIN.
2. If entry exists AND still processing → inform client that purchase details have been recorded and buy average will update within 24 hours (per **A4**).
3. If entry exists AND processed but discrepancy not resolved → route to Console Eq External Trades protocol Rule 2 for post-entry diagnostics.
4. If no entry exists → guide client through the discrepancy self-resolution path (per **A8**) including entry rules.

**If the client states they have already added external trade details:**

1. Check `console_eq_external_trades` for the entry before guiding them to add it again.
2. If the entry exists → route to Console Eq External Trades protocol Rule 2 for post-entry diagnostics.
3. If no entry exists → guide client through the discrepancy self-resolution path (per **A8**) including entry rules.

**If the instrument is an NCD or bond transferred from another broker:**

1. Check `discrepant` field. If > 0, guide the client through the standard discrepancy self-resolution path per **A8**. Note: NCDs do not display their current market value on Kite because they are debt instruments that trade infrequently and lack continuous market pricing. The invested value will reflect correctly once the client updates purchase details. Share links: https://support.zerodha.com/category/console/portfolio/articles/i-see-a-few-holdings-under-the-discrepancy-tab-what-does-it-mean and https://support.zerodha.com/category/console/portfolio/articles/how-do-i-add-external-trades-on-console

**If client says they don't have purchase details:** → advise client to obtain purchase details from their previous broker. Only the units are transferred — the purchase history is not carried over automatically (per **A8**).

---

### Rule 6 — Discrepancy (Cannot Resolve / Error)

1. First check `console_eq_external_trades` — the entry may have been posted successfully despite the error.
2. If entry found → inform client that purchase details have been recorded and buy average will update within 24 hours (per **A4**).
3. If no entry found → check against **A8** cannot-resolve conditions. Before applying the unlisted/inactive exception, verify the stock's current exchange status by checking Kite holdings or instrument search. If the stock has since been listed, proceed with standard discrepancy resolution (Rule 5). Respond with the applicable reason:
   - Trading holiday → "Today is a trading holiday — you can add the entry on the next trading day."
   - Inactive/suspended stock (confirmed still inactive/suspended after verification) → "This stock is currently inactive/suspended on the exchange. However, it is still visible on Console (console.zerodha.com/portfolio/holdings) as Console shows all securities in your demat, including suspended and inactive ones. Once it becomes active on the exchange, you'll be able to resolve the discrepancy."
   - Unlisted stock (confirmed still unlisted after verification) → "This stock is currently unlisted on any exchange. However, it is still visible on Console (console.zerodha.com/portfolio/holdings) as Console shows all securities in your demat, including unlisted ones. Once the stock becomes listed on an exchange, you'll be able to resolve the discrepancy."
   - CA within 10 days → "[tradingsymbol] had a corporate action within the last 10 days. The system will auto-adjust during this period. Please try again after 10 days from the corporate action date."
   - IPO within 3 days → "[tradingsymbol] was listed via IPO within the last 3 days. The system needs up to 3 days to process. Please try again after that."

---

### Rule 7 — Bonus Shares Not Credited / Not Visible

1. Check `console_eq_external_trades` for a system-posted CA credit entry (external_trade_type = devolved or CA-related entry) for this ISIN.
2. If CA credit entry found but not yet reflecting in holdings → "Your bonus shares of [tradingsymbol] have been processed and the credit entry is in our system. The holdings will update shortly — this can take up to 1 trading day to reflect."
3. If no CA credit entry found AND shares yet to be credited → bonus shares are typically credited within T+2 days from the record date. They initially appear under a temporary ISIN and become tradeable after 4–5 days once the exchange grants trading approval. CDSL will send an SMS when credited (per **A4**, **A6**). Also note: the temporary drop in P&L is expected and will auto-correct once bonus shares are credited to the demat account.
4. If more than 5 trading days since record date AND shares still not credited → escalate per **A12**.

---

### Rule 8 — Stock Split (Qty / Price Query)

1. Use `total_quantity`, `available`, and `pending` from `console_eq_holdings` as the basis — do not derive quantity from recent trade history.
2. Check `kite_holdings` to verify whether split shares have already been credited.
3. If `kite_holdings` shows the full post-split quantity → confirm the split shares have been credited. Share the available and total quantity. Note: buy average may take 2–3 working days to update, but client can sell in the meantime without P&L impact (per **A4**, **A6**).
4. If `kite_holdings` does not show the full post-split quantity AND Console shows shares still being processed → inform client of the available and pending quantities. Shares are typically credited within T+2 days from the record date and become tradeable after 4–5 days once the exchange grants trading approval. CDSL will notify via SMS once credited (per **A4**, **A6**).
5. If more than 5 trading days since record date AND split shares still not credited → escalate per **A12**.

---

### Rule 9 — Demerger (New Shares / Avg Update)

1. Shares not credited → new entity's shares are typically credited within 30–45 days from the record date. CDSL will notify via SMS/email once credited (per **A4**, **A6**).
2. Avg not updated → the buy average for both the original company and the new entity will be split based on the Cost of Acquisition (COA) ratio announced by the company. Once announced, Zerodha will update the buy average (per **A6**).
3. If COA announced but avg still not updated after 3 weeks → escalate per **A12**.

---

### Rule 10 — Merger (Share Swap)

1. Shares exchanged at the defined swap ratio. Old shares debited, new shares credited per ratio. If the swap ratio results in fractional shares, the cash equivalent will be credited to the client's primary bank account by the company-appointed trustee (per **A6**).

---

### Rule 11 — Holdings Not Visible / Qty Mismatch

1. Apply Preflight step 2 first (cross-reference `console_eq_pseudo_holdings`).
2. **If the stock was recently purchased (within last 90 days), check `console_eq_tradebook` for a subsequent sell trade for that instrument before concluding the shares are missing.** If a sell trade is found → inform client that the shares were sold, share the trade date, quantity, and price per share. The sale proceeds have been credited to their account — this is why the shares no longer appear in holdings. Do not proceed with further missing-holdings diagnostics.
3. Additionally check each quantity field and respond accordingly:
   - `t1` > 0 → shares were purchased yesterday and are currently in T+1 settlement. They will move to the available balance by end of today and be visible in regular holdings from the next trading day (per **A3**, **A4**).
   - `pending` > 0 → "You have [pending] shares yet to be credited from a corporate action. These will be credited once processed." Timeline per **A4** (bonus credit).
   - `margin` > 0 → "[margin] shares are pledged as collateral. They are in your demat account but blocked for margin. They appear under the margin/pledged section."
   - `loan` > 0 → "[loan] shares are under stock lending or pledged outside Zerodha."
   - All fields = 0 and stock not found → stock does not appear in holdings. Ask client to confirm the tradingsymbol or ISIN, and whether the purchase has settled (shares appear from T+1 day onwards).

---

### Rule 12 — Investment Value Mismatch

1. Explain: invested value = buy_average × total_quantity. Share the current values from the tool data (per **A1**).
2. Common causes:
   - Recent CA → average adjustment in progress (per **A4**).
   - `discrepant` > 0 → invested value inaccurate until purchase details added. This applies to all instrument types including NCDs and bonds (per **A8**). If the instrument was transferred from another broker, guide the client through the discrepancy self-resolution path. For NCDs specifically: NCDs do not display current market value on Kite (illiquid instruments), but invested value will reflect correctly once purchase details are updated. Share the discrepancy resolution links from Rule 5 NCD section.
   - "Ensure you're comparing equity holdings only — Console dashboard may include mutual fund values separately."

---

### Rule 13 — Pledged Qty in Holdings

1. The `margin` shares are pledged as collateral for trading margin. They remain in the client's demat account — they are not moved elsewhere (per **A10**).
2. If client asks about selling pledged shares → can sell directly using a CNC sell order on Kite without placing an unpledge request. Collateral margin will reduce by the value of shares sold (per **A10**).
3. If client reports collateral reduced after selling → this is a temporary reduction. When selling free (unpledged) shares of a stock that also has pledged quantities, the collateral temporarily reduces because the system considers pledged shares first. This is restored automatically the next trading day after the end-of-day process — no action needed (per **A10**).

---

### Rule 14 — Dividend & Debt Instrument Interest Queries

1. Dividend not received → dividends are credited to the primary bank account (not trading account), 30–45 days after ex/record date. Contact company's RTA — Zerodha does not process dividend payments. RTA lookup per **A7**.
2. Dividend amount less than expected → companies deduct TDS before crediting. TDS rules per **A7**.
3. Dividend tracking → Kite: Portfolio → select stock → View dividends. Console: Reports → Downloads → Dividend statement (per **A7**).
4. G-Sec, NCD, or bond interest query → interest is credited by RBI/paying agent directly to primary bank account, not through Zerodha. Details per **A7** debt instrument interest section.

---

### Rule 15 — Corporate Action Eligibility

1. General eligibility → must hold shares in demat on ex-date/record date. Buy at least 1 trading day before ex-date due to T+1 settlement (per **A6** eligibility).
2. Sold on ex-date → still eligible. Shares are debited from demat on T+1 day. Since client held them on the ex-date, they qualify (per **A6** eligibility).
3. Pledged shares → eligible for all corporate action benefits. However, for buyback tendering, shares must be unpledged first (per **A6**, **A10**).
4. Bought before ex-date but no CA benefit → in rare cases, a settlement holiday falling on the ex-date or a short delivery by the seller can delay or prevent share credit to demat by the record date, affecting eligibility despite a timely purchase (per **A6** eligibility, **A6** short delivery).
5. If client asks what short delivery means or reports missing shares due to short delivery → explain per **A6** short delivery section.

---

### Rule 16 — T1 / Settlement Queries

1. If `t1` > 0 → shares were purchased yesterday and are currently in T+1 settlement. They will move to the available balance by end of today and be visible in regular holdings from the next trading day (per **A3**, **A4**).

---

### Rule 17 — Gift / Off-Market Transfer (P&L / Avg)

1. **Gift in** (received via gift, asks about avg or P&L) → entry price = closing price on transfer date (per **A9**). Client can update via discrepancy resolution flow on Console if they need the actual acquisition cost. For income tax returns, may need to manually adjust Tax P&L — advise consulting a CA (per **A9**).
2. **Off-market transfer in** (asks about avg or P&L) → no automatic buy price assigned. Client must manually add purchase details via the discrepancy resolution flow on Console (per **A8**, **A9**).
3. **Gift out** → Zerodha uses the gift transfer date as the exit date and the closing price on that date as the exit price. This reflects in P&L accordingly (per **A9**).
4. **Off-market transfer out** → no automatic exit entry is posted since the transaction happens outside the platform. Client can either share transfer details for a reversal entry, or manually update their Tax P&L report while filing returns (per **A9**).

---

### Rule 18 — Fractional Unit Redemption (LIQUIDBEES)

1. Fractional units of LIQUIDBEES cannot be sold on the secondary market. They can only be redeemed by making an off-market transfer to the AMC's demat account via CDSL Easiest. Step-by-step process: https://support.zerodha.com/category/mutual-funds/understanding-mutual-funds/selling/articles/redeeming-fractional-units
2. If the client's account is currently dormant due to inactivity for over 24 months, they will need to complete Re-KYC online to reactivate their account (24–48 working hours after IPV) before they can initiate the off-market transfer.
