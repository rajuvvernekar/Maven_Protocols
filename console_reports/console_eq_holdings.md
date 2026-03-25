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

### A1 — Tool Purpose & Fundamentals

This tool looks up a client's equity holdings. Buy average uses FIFO (First In, First Out) — mandated by the Income Tax Department. Holdings = available + t1 + margin + pending + discrepant + loan (`total_quantity`). `buy_value` = `buy_average` × `total_quantity`.

**Input:** Client ID.

---

### A2 — Field Usage Rules

**Shareable fields:**

`tradingsymbol` | `isin` | `buy_average` | `buy_value` | `available` | `t1` | `margin` | `pending` | `discrepant` | `loan` | `total_quantity`

**Internal-only fields** (use for reasoning; communicate outcomes in plain language):

`name` | `instrument_id` | `holdings_date` | `closing_price` | `failure_date`

**Client-facing terminology:**

| Internal Term | Client-Facing Alternative |
|---|---|
| pending | "being processed for credit" or "yet to be credited" |
| failure date | (omit — use for internal escalation only) |
| holdings date | (omit — internal modification timestamp) |
| instrument ID | (omit — internal system mapping) |
| Any internal tool or system name | (describe the outcome, not the tool) |

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

**Method:** FIFO — sell oldest shares first.

**Intraday exception:** Sell from holdings + buy back same day → average unchanged (treated as separate speculative transactions, not delivery).

**T2T exception:** Trade-to-Trade stocks — buy average updates to latest purchase price since all T2T trades are delivery.

**Transfer in:** Shows as discrepancy → client adds buy average via the self-resolution path in **A8**.

**Transfer-in entry rules:** Date must be ≤ demat credit date. Only 1 entry per ISIN per date. No holidays/weekends. Same-date multiple buys = weighted average, total qty.

**Gift transfer in:** Closing price on transfer date used as entry price (gift only — off-market transfers require manual discrepancy entry).

**Buy average null reasons:** Discrepant without entry | Transfer without manual update | CA in progress | ESOP/off-market without entry.

**Buy average ₹0 reason:** Only bonus shares remain after FIFO sold all original bought shares (bonus cost = ₹0).

---

### A6 — Corporate Actions

#### Bonus

Free shares to existing shareholders in a ratio (e.g., 2:1). Qty increases; price adjusts proportionally; total value unchanged; bonus shares at cost ₹0. Credit: T+2 from record date; temp ISIN; tradeable after 4–5 days. P&L shows artificial drop until credited — expected, auto-corrects.

#### Split

Shares divided by reducing face value (e.g., 1:5 = 1 becomes 5). Qty multiplied, price divided by ratio; total value unchanged. Client can sell original qty immediately; wait for additional credited shares. Buy average update may take 2–3 working days after split shares are credited; client can sell in the meantime without P&L impact.

#### Consolidation (Reverse Split)

Fewer shares at higher price. Qty reduces, price increases; fractional shares settled in cash to primary bank by company-appointed trustee.

#### Merger

Two companies combine; shares exchanged at defined swap ratio. Old debited, new credited per ratio; fractional shares = cash to bank.

#### Demerger

Company splits into separate entities; new shares credited proportionally. Original retained; new entity credited; average split per COA ratio announced by company. New entity shares within 30–45 days from record date (per **A4**).

#### Rights Issue

Existing shareholders buy additional shares at discounted price. REs credited as temp securities before issue; lapse if not used/sold. RE premium not included in rights share average.

#### Eligibility

Hold shares in demat on ex-date/record date. Buy at least 1 trading day before ex-date (T+1 settlement). Selling on ex-date still qualifies (shares debited T+1). Pledged shares eligible for all CA benefits. Exceptions: settlement holiday or short delivery can cause ineligibility even if bought before ex-date.

#### Fractional Shares

Fractional shares from any CA settled in cash by company-appointed trustee → credited to primary bank.

---

### A7 — Dividends

**Credit:** Primary bank account (not trading account); 30–45 days after ex-date/record date (per **A4**).

**Not received:** Contact company's Registrar and Transfer Agent (RTA) — Zerodha does not process dividend payments and does not receive details about dividend credits.

**RTA lookup:** NSE: nseindia.com → search company → Corporate information → Transfer Agent Details. BSE: bseindia.com → search company → Corp Information.

**Failed credit:** RTA issues dividend warrant via courier to registered address.

**TDS:** Resident: 10% above ₹10,000/FY (from FY25-26). NRI: 20%, no threshold. No PAN: 20%.

**Tracking:** Kite: Portfolio → select stock → View dividends. Console: Reports → Downloads → Dividend statement.

---

### A8 — Discrepancy Resolution

**Common causes:** Transfer from other broker | IPO | Off-market | Gift | ESOP | CA system delay.

**Self-resolution path:** Console → Portfolio → Holdings → View discrepancy → Select stock → Add trade → Enter date, price, qty.

**Entry rules:** Date must be ≤ demat credit date. Only 1 entry per ISIN per date. No holidays/weekends. Same-date multiple buys = weighted average, total qty.

**Locking:** Entries editable only while status is "Pending"; locked once buy average updated (within 24 hours per **A4**).

**Cannot resolve:** Trading holidays | Inactive/suspended/unlisted stocks | CA within 10 days | IPO within 3 days.

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

---

### A12 — Escalation Data Template

When escalating, always include: **client ID, tradingsymbol(s), specific issue description, and relevant data** (e.g., expected vs actual values, entry details from `console_eq_external_trades`, screenshots if available).

---

### A13 — Response Templates

**R1 — FIFO explanation:**
"Your buy average is calculated using the FIFO (First In, First Out) method, which is mandated by the Income Tax Department. When you sell shares, the oldest purchased shares are considered sold first, which changes the average of remaining shares. You can check the detailed calculation under View breakdown on Kite or Console."

**R2 — Intraday no-impact:**
"Intraday transactions don't affect your buy average since those are treated as separate speculative trades. Your delivery holdings average remains unchanged."

**R3 — Discrepancy self-resolution guidance:**
"Your [tradingsymbol] shares are showing as a discrepancy because the purchase details are not available in our system. This typically happens when shares are transferred from another broker, received via off-market transfer, ESOP, or IPO. To update your buy average, go to Console → Portfolio → Holdings → View discrepancy → select [tradingsymbol] → Add trade → enter the original purchase date, price, and quantity."

**R4 — Discrepancy entry rules (append to R3 when guiding client):**
"Please note:
- Enter the original purchase date (must be on or before the date shares were credited to your Zerodha demat)
- Only one entry per date is allowed; if you bought on multiple dates, add separate entries for each
- If you bought multiple times on the same date, enter the total quantity with the weighted average price
- Entries cannot be made on holidays or weekends
- Once the buy average is updated (within 24 hours), the entry cannot be modified"

**R5 — No purchase details available:**
"You can obtain the purchase details from your previous broker. Only the units are transferred — the purchase history is not carried over automatically."

**R6 — Entry pending processing:**
"Your purchase details have been recorded and are being processed. Your buy average will update within 24 hours."

**R7 — CA average adjustment in progress:**
"Your [tradingsymbol] buy average is being adjusted due to a recent corporate action. This update typically takes about 2 weeks from the corporate action date."

**R8 — Buy average ₹0 (bonus only remaining):**
"Your [tradingsymbol] buy average is showing ₹0 because all your originally purchased shares have been sold (as per FIFO), and only bonus shares remain. Bonus shares are credited at zero cost, so the average of remaining holdings becomes ₹0. This is correct as per FIFO accounting."

**R9 — Bonus not yet credited:**
"Your [pending] bonus shares of [tradingsymbol] are being processed for credit. Bonus shares are typically credited within T+2 days from the record date. They initially appear under a temporary ISIN and become tradeable after 4–5 days once the exchange grants trading approval. CDSL will send you an SMS when the shares are credited."

**R10 — P&L temporary drop (bonus/split):**
"The temporary drop in your P&L is expected — it will auto-correct once the bonus shares are credited to your demat account."

**R11 — Split shares credited:**
"Your split shares have been successfully credited to your account. You currently have [available] shares of [tradingsymbol] available for trading, totalling [total_quantity] shares after the split. Please note that the buy average may take 2–3 working days to update, but you can sell your shares in the meantime — this will not impact your P&L."

**R12 — Split shares still processing:**
"You currently have [available] shares of [tradingsymbol], with [pending] shares being processed for credit, totalling [total_quantity] shares after the split. These are typically credited within T+2 days from the record date and will become tradeable after 4–5 days once the exchange grants trading approval. CDSL will notify you via SMS once the shares are credited to your demat account."

**R13 — Demerger shares not credited:**
"After a demerger, the new entity's shares are typically credited within 30–45 days from the record date. CDSL will notify you via SMS/email once credited."

**R14 — Demerger average not updated:**
"The buy average for both [original company] and [new entity] will be split based on the Cost of Acquisition (COA) ratio announced by the company. Once the company announces the ratio, we will update the buy average accordingly."

**R15 — Merger share swap:**
"After the merger, your [old company] shares have been exchanged for [new company] shares at the [ratio] swap ratio. If the swap ratio results in fractional shares, the cash equivalent will be credited to your primary bank account by the company-appointed trustee."

**R16 — Investment value explanation:**
"Your invested value is calculated as buy average × total quantity. Current values: buy average = ₹[buy_average], total quantity = [total_quantity], invested value = ₹[buy_value]."

**R17 — T1 settlement:**
"Your [t1] shares of [tradingsymbol] were purchased yesterday and are currently in T+1 settlement. They will move to your available balance by end of today and be visible in your regular holdings from the next trading day."

**R18 — CA eligibility:**
"To be eligible for corporate action benefits, you must hold the shares in your demat account on the ex-date/record date. Since shares settle on T+1, you need to buy at least one trading day before the ex-date."

**R19 — Sold on ex-date, still eligible:**
"You are still eligible. When you sell on the ex-date, the shares are debited from your demat on T+1 day. Since you held them on the ex-date, you qualify."

**R20 — Pledged shares CA eligibility:**
"Pledged shares are eligible for all corporate action benefits. However, for buyback tendering, you must unpledge the shares first."

**R21 — Bought before ex-date but no CA benefit:**
"In rare cases, a settlement holiday falling on the ex-date or a short delivery by the seller can delay or prevent share credit to your demat by the record date. This would affect eligibility despite a timely purchase."

**R22 — Dividend not received:**
"Dividends are credited directly to your primary bank account (not your Zerodha trading account) within 30–45 days after the ex-date/record date.

If you haven't received your dividend within this period, please contact the company's Registrar and Transfer Agent (RTA). Zerodha does not process dividend payments and does not receive details about dividend credits. You can find the RTA details on NSE (nseindia.com → search company → Corporate information → Transfer Agent Details) or BSE (bseindia.com → search company → Corp Information)."

**R23 — Dividend TDS:**
"Companies deduct TDS before crediting dividends. For resident individuals, TDS of 10% applies on total dividend income exceeding ₹10,000 in a financial year. For NRIs, TDS is 20% with no threshold. If PAN is not linked, TDS is 20%. You can verify TDS in Form 26AS on the income tax portal and claim credit when filing ITR."

**R24 — Dividend tracking:**
"You can track dividends on Kite (Portfolio → select stock → View dividends) or download the dividend statement from Console (Reports → Downloads → Dividend statement)."

**R25 — Pledged qty explanation:**
"Your [margin] shares of [tradingsymbol] are pledged as collateral for trading margin. These shares remain in your demat account — they are not moved elsewhere."

**R26 — Sell pledged shares:**
"You can sell pledged shares directly using a CNC sell order on Kite without placing an unpledge request. Your collateral margin will reduce by the value of shares sold."

**R27 — Temporary collateral reduction:**
"When you sell free (unpledged) shares of a stock that also has pledged quantities, the collateral temporarily reduces because the system considers pledged shares first. This is restored automatically the next trading day after the end-of-day process — no action needed from your side."

**R28 — Gift in (P&L/avg):**
"For shares received via gift, the system uses the closing price on the transfer date as the entry price for P&L tracking purposes. If you need to update this with the actual acquisition cost, you can add the details via the discrepancy resolution flow on Console.

Please note: While filing income tax returns, you may need to manually adjust the Tax P&L report to reflect the correct cost of acquisition as per your preferred tax treatment. Consult a Chartered Accountant for guidance."

**R29 — Off-market transfer in (P&L/avg):**
"For shares received via off-market transfer, the system does not automatically assign a buy price. You will need to manually add the purchase details via the discrepancy resolution flow on Console."

**R30 — Gift out:**
"For gifted shares, Zerodha uses the gift transfer date as the exit date and the closing price on that date as the exit price in your account. This will reflect in your P&L accordingly."

**R31 — Off-market transfer out:**
"When shares are transferred out via off-market, no automatic exit entry is posted in our system since the transaction happens outside the platform. You can either share the transfer details so we can post a reversal entry, or manually update your Tax P&L report while filing returns."

**R32 — Stock not in holdings:**
"This stock does not appear in your holdings. Please confirm the tradingsymbol or ISIN, and whether the purchase has settled (shares appear from T+1 day onwards)."

**R33 — Gift entry found in system:**
"Your gift shares of [tradingsymbol] have been recorded in our system at ₹[price] per share (closing price on transfer date). No further action is needed from your side. Your buy average will reflect this once processed."

---

**Escalation behavior:** When any rule in this protocol says **ESCALATE**, do not draft a customer-facing response. Instead, output only: **HUMAN AGENT ACTION REQUIRED** — followed by the reason from the rule. The human agent will handle the query manually.

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
Dividend query                                            → Rule 14
Corporate action eligibility                              → Rule 15
T1 / settlement query                                     → Rule 16
Gift / off-market transfer (P&L / avg)                    → Rule 17
```

### Scope

- Address the client's query about their equity holdings, buy averages, corporate actions, discrepancies, dividends, or pledged stock.
- Use **A2** field rules and client-facing terminology in all client communication.
- Do not volunteer information about unrelated holdings topics unless directly relevant.

### Fallback

If no route matches, interpret the holdings data using Section A reference data. If no root cause is found, **ESCALATE** per **A12**.

---

## Section C: Rules

---

### Rule 1 — Buy Average Differs from Expected

1. Respond per **A13-R1** (FIFO explanation).
2. If client sold and bought back same day → respond per **A13-R2** (intraday no-impact).

---

### Rule 2 — Buy Average Showing N/A

1. If `buy_average` is null/N/A AND `discrepant` > 0:
   a. Check `console_eq_external_trades` for an existing entry for this ISIN.
   b. If entry exists AND still processing → respond per **A13-R6**.
   c. If entry exists AND processed but avg still N/A → **ESCALATE** per **A12** with entry details from `console_eq_external_trades`.
   d. If no entry exists → respond per **A13-R3** + **A13-R4**.

2. If `buy_average` is null AND `discrepant` = 0 AND `pending` > 0:
   → Respond per **A13-R7**. Timeline per **A4**.

---

### Rule 3 — Buy Average Showing ₹0

1. If `buy_average` = 0 AND `total_quantity` > 0:
   a. Check `console_eq_holdings_breakdown` for the same stock/ISIN — look for entries where `exchange` field = "BONUS".
   b. If confirmed → respond per **A13-R8**.
   c. If no BONUS entry found → investigate further (may be a system issue or other CA type). **ESCALATE** per **A12** if unexplained.

---

### Rule 4 — Buy Average Wrong After Corporate Action

1. Check if CA was within last 2 weeks → respond per **A13-R7**. Timeline per **A4**.
2. If CA was 3+ weeks ago and avg still appears wrong → **ESCALATE** per **A12** with client ID, tradingsymbol, and expected vs actual buy average.

---

### Rule 5 — Discrepancy (Transferred / Gift / ESOP Shares)

**If client confirms shares were received via Zerodha gift transfer:**

1. Check `console_eq_external_trades` for `external_trade_type` = gift.
2. If entry found → respond per **A13-R33**.
3. If no entry found → **ESCALATE** per **A12**. The system should have auto-posted this entry.

**If client confirms shares were transferred from another broker / ESOP / off-market:**

1. Check `console_eq_external_trades` for an existing entry for this ISIN.
2. If entry exists AND still processing → respond per **A13-R6**.
3. If entry exists AND processed but discrepancy not resolved → **ESCALATE** per **A12** with entry details.
4. If no entry exists → respond per **A13-R3** + **A13-R4**.

**If client says they don't have purchase details:** → respond per **A13-R5**.

---

### Rule 6 — Discrepancy (Cannot Resolve / Error)

1. First check `console_eq_external_trades` — the entry may have been posted successfully despite the error.
2. If entry found → respond per **A13-R6**.
3. If no entry found → check against **A8** cannot-resolve conditions and respond with the applicable reason:
   - Trading holiday → "Today is a trading holiday — you can add the entry on the next trading day."
   - Inactive/suspended/unlisted stock → "This stock is currently inactive/suspended/unlisted. Once it becomes active on the exchange, you'll be able to resolve the discrepancy."
   - CA within 10 days → "[tradingsymbol] had a corporate action within the last 10 days. The system will auto-adjust during this period. Please try again after 10 days from the corporate action date."
   - IPO within 3 days → "[tradingsymbol] was listed via IPO within the last 3 days. The system needs up to 3 days to process. Please try again after that."

---

### Rule 7 — Bonus Shares Not Credited / Not Visible

1. Check `console_eq_external_trades` for a system-posted CA credit entry (external_trade_type = devolved or CA-related entry) for this ISIN.
2. If CA credit entry found but not yet reflecting in holdings → "Your bonus shares of [tradingsymbol] have been processed and the credit entry is in our system. The holdings will update shortly — this can take up to 1 trading day to reflect."
3. If no CA credit entry found AND shares yet to be credited → respond per **A13-R9**. Append **A13-R10** (P&L temporary drop).
4. If more than 5 trading days since record date AND shares still not credited → **ESCALATE** per **A12**.

---

### Rule 8 — Stock Split (Qty / Price Query)

1. Use `total_quantity`, `available`, and `pending` from `console_eq_holdings` as the basis — do not derive quantity from recent trade history.
2. Check `kite_holdings` to verify whether split shares have already been credited.
3. If `kite_holdings` shows the full post-split quantity → respond per **A13-R11**.
4. If `kite_holdings` does not show the full post-split quantity AND Console shows shares still being processed → respond per **A13-R12**.
5. If more than 5 trading days since record date AND split shares still not credited → **ESCALATE** per **A12**.

---

### Rule 9 — Demerger (New Shares / Avg Update)

1. Shares not credited → respond per **A13-R13**. Timeline per **A4**.
2. Avg not updated → respond per **A13-R14**. Timeline per **A4**.
3. If COA announced but avg still not updated after 3 weeks → **ESCALATE** per **A12**.

---

### Rule 10 — Merger (Share Swap)

1. Respond per **A13-R15**.

---

### Rule 11 — Holdings Not Visible / Qty Mismatch

1. Apply Preflight step 2 first (cross-reference `console_eq_pseudo_holdings`).
2. Additionally check each quantity field and respond accordingly:
   - `t1` > 0 → respond per **A13-R17**.
   - `pending` > 0 → "You have [pending] shares yet to be credited from a corporate action. These will be credited once processed." Timeline per **A4** (bonus credit).
   - `margin` > 0 → "[margin] shares are pledged as collateral. They are in your demat account but blocked for margin. They appear under the margin/pledged section."
   - `loan` > 0 → "[loan] shares are under stock lending or pledged outside Zerodha."
   - All fields = 0 and stock not found → respond per **A13-R32**.

---

### Rule 12 — Investment Value Mismatch

1. Respond per **A13-R16**.
2. Common causes:
   - Recent CA → average adjustment in progress (per **A4**).
   - `discrepant` > 0 → invested value inaccurate until purchase details added.
   - "Ensure you're comparing equity holdings only — Console dashboard may include mutual fund values separately."

---

### Rule 13 — Pledged Qty in Holdings

1. Respond per **A13-R25**.
2. If client asks about selling pledged shares → respond per **A13-R26**.
3. If client reports collateral reduced after selling → respond per **A13-R27**.

---

### Rule 14 — Dividend Queries

1. Dividend not received → respond per **A13-R22**. RTA details per **A7**.
2. Dividend amount less than expected → respond per **A13-R23**.
3. Dividend tracking → respond per **A13-R24**.

---

### Rule 15 — Corporate Action Eligibility

1. General eligibility → respond per **A13-R18**. Rules per **A6** eligibility.
2. Sold on ex-date → respond per **A13-R19**.
3. Pledged shares → respond per **A13-R20**. Buyback exception per **A10**.
4. Bought before ex-date but no CA benefit → respond per **A13-R21**.

---

### Rule 16 — T1 / Settlement Queries

1. If `t1` > 0 → respond per **A13-R17**.

---

### Rule 17 — Gift / Off-Market Transfer (P&L / Avg)

1. **Gift in** (received via gift, asks about avg or P&L) → respond per **A13-R28**. Price rules per **A9**.
2. **Off-market transfer in** (asks about avg or P&L) → respond per **A13-R29**. Resolution path per **A8**.
3. **Gift out** → respond per **A13-R30**. Rules per **A9**.
4. **Off-market transfer out** → respond per **A13-R31**. Rules per **A9**.

---

## Section D: General Notes

- Shares are visible in holdings from T+1 day (bought Monday → visible Tuesday).
- Corporate action adjustments take ~2 weeks from CA date for buy average update.
- P&L shows artificial drop until bonus/split shares are credited — this is expected and auto-corrects.
- Pledged stocks remain eligible for all corporate action benefits.
- Dividends are credited to primary bank account, not trading account.
- Dividend queries should be directed to the company's RTA, not Zerodha.
- Shares transferred from another broker always show as discrepancy — purchase history is not carried over automatically.
- Only 1 discrepant entry per ISIN per date allowed.
- Gift transfer in uses closing price on transfer date; off-market transfer in requires manual discrepancy entry.
- Off-market transfer out has no automatic exit entry — client must provide details or edit Tax P&L manually.
