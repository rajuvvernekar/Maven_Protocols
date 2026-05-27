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

TAGS: holdings, demat, corporate-actions

## Protocol

# CONSOLE EQ HOLDINGS PROTOCOL

---

## Section A: Reference Data

### A1 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |
|---|---|
| `tradingsymbol` | Exchange trading symbol of the instrument |
| `isin` | ISIN code of the instrument |
| `buy_average` | Average cost per share (FIFO basis) |
| `buy_value` | `buy_average` × `total_quantity` |
| `available` | Free qty available for trading/selling |
| `t1` | Qty bought yesterday; settles end of today |
| `margin` | Qty pledged or blocked as collateral; still in client demat |
| `pending` | Qty expected from a corporate action; not yet credited to demat — communicate as "being processed for credit" or "yet to be credited" |
| `discrepant` | Qty mismatch between tradebook and demat holdings file (transfers, IPOs, off-market, gifts, ESOPs, CA delays) |
| `loan` | Qty pledged outside Zerodha via LAS or lent externally to an NBFC |
| `total_quantity` | Sum of `available` + `t1` + `margin` + `pending` + `discrepant` + `loan` |

**Non-shareable:**

| Field | Interpretation |
|---|---|
| `name` | Full name of the instrument — internal reference only |
| `instrument_id` | Internal instrument mapping identifier |
| `holdings_date` | Internal modification timestamp of the holdings record |
| `closing_price` | Closing price of the instrument — used for internal calculations |
| `failure_date` | Date on which a processing failure occurred for this holding |

---

### A2 — Timelines

| Event | Timeline |
|---|---|
| T+1 settlement (shares visible in holdings) | T+1 day (bought Monday → holdings Tuesday) |
| Bonus share credit | T+2 from record date; tradeable after 4–5 days (temp ISIN → perm ISIN) |
| Corporate action buy average adjustment | ~2 weeks from CA date |
| Demerger new entity share credit | 30–45 days from record date |
| Discrepant entry buy average update | Within 24 hours of adding entry |
| Gift transfer-in buy average update | 3–4 working days from transfer date; shares may show as discrepant until then |
| Dividend credit to primary bank | 30–45 days after ex-date/record date |
| Split share buy average update | 2–3 working days after split shares are credited |
| G-Sec / NCD / bond interest credit | Semi-annually to primary bank; typically within 5–7 working days of payment date |
| G-Sec interest eligibility | Must hold the G-Sec at least 15 days before the interest date |

---

### A3 — Buy Average Methodology

- **FIFO basis:** Sell oldest lots first (mandated by Income Tax Department).
- **Same-date multiple buys:** Multiple purchases on the same date are combined into a single lot using weighted average price and total qty.
- **Intraday exception (EQ stocks):** Sell from holdings + buy back same day → subsequent buy is treated as intraday (speculative, not delivery) → shares are not debited/credited to demat → buy average of holdings unchanged.
- **T2T exception:** Trade-to-Trade stocks have no intraday exception — all trades are compulsory delivery. Sell from holdings + buy back same day → sold shares are debited from demat; newly purchased shares settle to demat separately → buy average updates to reflect the new purchase price and qty.
- **Transfer-in:** Appears as discrepancy; entry price added via self-resolution path (see A7).
- **Partial sell FIFO impact:** When shares are partially sold, buy average of remaining shares may change if earliest FIFO lots differed from current market price. Updated invested value and buy average reflect after end-of-day processing. Verifiable via View breakdown on Kite or Console.
- **Grandfather clause (Section 112A, Income Tax Act):** For shares purchased before 31 Jan 2018 with no purchase records available, cost of acquisition = higher of (a) actual purchase price or (b) stock's high price on NSE or BSE on 31 Jan 2018. Trade date entered as 31 Jan 2018, with the high price from that date.
- **`buy_average` null reasons:** Discrepant without entry | Transfer without manual update | CA in progress | ESOP/off-market without entry.
- **`buy_average` ₹0 reason:** Only bonus shares remain after client sold all originally purchased shares; bonus shares carry ₹0 cost since no purchase price was paid for them.

---

### A4 — Corporate Action Eligibility

- Must hold shares in demat on the ex-date/record date.
- Must buy at least 1 trading day before ex-date (T+1 settlement).
- Selling on ex-date still qualifies — shares debited T+1, held on ex-date.
- Pledged shares are eligible for all CA benefits.
- Settlement holiday on ex-date, or short delivery by seller, can delay/prevent share credit by record date — affecting eligibility despite a timely purchase.

---

### A5 — Corporate Actions

| Type | Description |
|---|---|
| Bonus | Free shares in a ratio (e.g., 2:1 = 2 bonus shares for every 1 share held). Qty increases; price adjusts proportionally so total value is unchanged; bonus shares at cost ₹0. Credit under temporary ISIN. |
| Split | Shares divided by reducing face value (e.g., 1:5 = 1 becomes 5). Qty multiplied; price divided by ratio; total value unchanged. Client can sell original qty immediately; newly credited shares tradeable after credit. |
| Consolidation (Reverse Split) | Shares combined in a ratio (e.g., 1:5 = 1 new share for every 5 shares held). Qty reduces; price increases proportionally so total value is unchanged; fractional shares settled in cash. |
| Merger | Two companies combine; shares exchanged at defined swap ratio. Old debited, new credited per ratio. |
| Demerger | Company splits into separate entities; new shares credited proportionally. Original retained; new entity credited. Buy average split per Cost of Acquisition (COA) ratio announced by the company. |

---

### A6 — Short Delivery

Short delivery occurs when the seller of shares does not deliver by settlement deadline. Use the short delivery explanation article in A13 for detailed reference when handling short delivery queries.

Two scenarios:

- **Counter-party default:** Buyer purchased shares, but the counter-party (seller) had no shares and defaulted. Exchange conducts an auction on T+1 to source the shares; shares are credited to the buyer by T+2 EOD. Buyer may raise a query in this window about missing shares.
- **Intraday short sell stuck in upper circuit:** Trader short sold intraday but could not buy back to close the position because the stock hit an upper circuit (no sellers available). Exchange conducts an auction on T+1; Zerodha blocks 120% of the settlement value (closing price on the day of short sell × qty). Auction settlement entry is posted on T+2. If the exchange cannot source shares in the auction → close-out procedure applies and cash settlement is done at close-out price.

---

### A7 — Discrepancy

- **Common causes:** Transfer from other broker | IPO | Off-market | Gift | ESOP | CA system delay.
- **Self-resolution path:** See A13 — Update buy average (discrepancy). To navigate to holdings, share A13 — Holdings on Console.
- **Entry rules:**
  - Date ≤ demat credit date
  - 1 entry per ISIN per date
  - Trade date cannot be a weekend or a holiday
- **Locking:** Entries editable only while status is "Pending"; locked once buy average updates (per A2).
- **Cannot resolve:** Discrepancy entries cannot be added for inactive, suspended, or unlisted stocks. Entering a trade date that falls on a trading holiday will throw an error — use the next valid trading day. Also not possible: CA within 10 days | IPO within 3 days.
- **Scope:** Applies to all instrument types — equity, NCDs, bonds, and other securities.
- **Transfer-in behavior:** Only units are transferred from the previous broker; purchase history is not carried over automatically.
- **NCDs / bonds:** Do not display current market value on Kite (illiquid, no continuous pricing). Invested value reflects correctly once purchase details are updated.

---

### A8 — Gift and Off-Market Transfers

| Event | Behavior |
|---|---|
| Gift transfer in | Closing price on transfer date used as entry price. System auto-posts entry (`console_eq_external_trades`, `external_trade_type` = gift). |
| Zerodha-gifted shares (shares gifted by Zerodha to client) | Buy average updated automatically by Zerodha. Verify via `stock_gift_requests`. If client has also added an external trades entry for the same ISIN → double entry risk; escalate. Do not draft any client-facing response. |
| Gift transfer out | Gift transfer date = exit date; closing price on that date = exit price. |
| Off-market transfer in | No automatic buy price assigned. Purchase details must be added manually via discrepancy flow. |
| Off-market transfer out | No automatic exit entry. Escalate. |

---

### A9 — Pledging

- Pledged shares can be sold via CNC sell order on Kite without an unpledge request; collateral reduces proportionally.
- **Temporary collateral reduction:** Selling free qty of a stock that also has pledged qty → collateral temporarily reduces (system considers pledged shares first) → restored automatically next trading day after end-of-day processing.
- **Buyback:** Pledged shares must be unpledged before buyback tendering.

---

### A10 — Loan (LAS)

- LAS = Loan Against Securities; not processed through Zerodha.

---

### A11 — Dividends and Debt Instrument Interest

- **Dividends**

  - **Credit:** Primary bank (not trading account); timeline per A2.
  - **Non-receipt / processing:** Contact the company's Registrar and Transfer Agent (RTA). Zerodha does not process dividend payments and does not receive credit details.
  - **RTA lookup:** See A13 — NSE / BSE (search company → Corporate information → Transfer Agent Details).
  - **Failed credit:** RTA issues dividend warrant by courier to registered address.
  - **TDS:** Resident 10% above ₹10,000/FY (from FY25-26) | NRI 20%, no threshold | No PAN 20%.
  - **Tracking:**
    - Kite: Portfolio → select stock → View dividends
    - Console: Reports → Downloads → Dividend statement

- **G-Sec / NCD / Bond Interest**

  - **Credit:** Credited directly by RBI or paying agent to primary bank; not through Zerodha. Timeline and eligibility per A2.
  - **RBI interest schedule:** See A13 — RBI G-Sec interest schedule → "Auction for Sale (Issue/Re-issue) of Government Stock (GS)" under Notifications (Archives for older issues).
  - **Client tracking options:** (1) Bank statements | (2) CDSL Consolidated Account Statement (CAS) | (3) RBI Retail Direct portal (if applicable).

---

### A12 — LIQUIDBEES Fractional Redemption

- Fractional units cannot be sold on the secondary market.
- Redeemable only via off-market transfer to the AMC's demat account through CDSL Easiest. Share A13 — LIQUIDBEES fractional redemption for step-by-step process.
- Dormant account (inactive > 24 months) → Re-KYC required before initiating off-market transfer (reactivation takes 24–48 working hours after IPV).

---

### A13 — Links

| Topic | URL / Path |
|---|---|
| Update buy average (discrepancy) | https://support.zerodha.com/category/console/portfolio/console-holdings/articles/how-to-update-buy-average |
| Holdings on Console | console.zerodha.com/portfolio/holdings |
| Discrepancy explanation | https://support.zerodha.com/category/trading-and-markets/alerts-and-nudges/kite-error-messages/articles/discrepant-holdings |
| Add external trades on Console | https://support.zerodha.com/category/console/portfolio/console-holdings/articles/how-to-update-buy-average |
| LIQUIDBEES fractional redemption | https://support.zerodha.com/category/mutual-funds/understanding-mutual-funds/selling/articles/redeeming-fractional-units |
| SOT / SOH holding statement | https://support.zerodha.com/category/your-zerodha-account/transfer-of-shares-and-conversion-of-shares/cdsl-easi-easiest/articles/will-zerodha-send-me-holding-statements-for-my-investments |
| NSE historical prices | nseindia.com (search company → Historical Data) |
| BSE historical prices | bseindia.com (search company → Historical Prices) |
| RBI G-Sec interest schedule | rbi.org.in/Scripts/NotificationUser.aspx |
| Short delivery explanation | https://support.zerodha.com/category/trading-and-markets/trading-faqs/general/articles/what-is-short-delivery-and-what-are-its-consequences |

## Section B: Decision Flow

### Routing

```
Route by scenario
   ├─ failure_date populated (any value)                                    → Rule 1
   ├─ tradingsymbol appears as ISIN-format alphanumeric string in holdings
   │    data (shares are unlisted)                                          → Rule 1
   ├─ Employer-mandated account deactivation / closure                      → Rule 1
   ├─ Rights issue query                                                    → Rule 1
   ├─ Rights entitlement (RE) / Partly Paid (PP) share query                → Rule 1
   ├─ Unlisted / suspended stock discrepancy (confirmed)                    → Rule 1
   ├─ Buy average query
   │    (differs from expected / N/A / ₹0 / wrong post-CA / invested value) → Rule 2
   ├─ Corporate action query
   │    (bonus / split / consolidation / demerger / merger / eligibility)   → Rule 3
   ├─ Holdings not visible / qty mismatch                                   → Rule 4
   ├─ Pledged qty in holdings                                               → Rule 5
   ├─ T1 / settlement query                                                 → Rule 6
   ├─ Discrepancy
   │    (transferred / gift / ESOP / off-market / entry error /
   │     wrong / incorrect entry by client / P&L / avg)                    → Rule 7
   ├─ Zerodha-gifted shares — client mentions buy average updated for
   │    gifted stock, or stock name mentioned and recently gifted by Zerodha → Rule 7h
   ├─ Loan (LAS) query                                                      → Rule 8
   ├─ Short delivery query                                                  → Rule 9
   ├─ Dividend / G-Sec / NCD / bond interest query                          → Rule 10
   ├─ LIQUIDBEES fractional redemption                                      → Rule 11
   └─ Holding statement / SOT / SOH / Statement of Transaction              → Rule 12
```

### Fallback

If no route matches, interpret holdings data using Section A. If no root cause is identified → escalate.

---

## Section C: Rules

### Rule 1 — Escalation Triggers

Escalate.

| Trigger | Data to include |
|---|---|
| `failure_date` populated (any value) | Client ID, `tradingsymbol`, `failure_date`. |
| `tradingsymbol` appears as ISIN-format alphanumeric string in holdings data — shares are unlisted | Client ID and the ISIN entry. |
| Unlisted stock (confirmed after verification) | Client ID, `tradingsymbol`, ISIN. |
| Suspended / inactive stock (confirmed after verification) | Client ID, `tradingsymbol`, ISIN. |
| Rights entitlement (RE) / Partly Paid (PP) share query | Client ID, `tradingsymbol`, query details. |
| REs or PPs found during bonus credit investigation — no bonus issued; REs or PPs present instead | Client ID, `tradingsymbol`, query details. |
| Rights issue query | Client ID, `tradingsymbol`, query details. |
| Employer-mandated account deactivation / closure (employer restrictions, compliance, empanelment) | Client ID and client's stated reason. |
| Client requests SOT / SOH / Holding Statement / Statement of Transaction for visa purposes, or requests a signed / stamped copy | Client ID and stated purpose. |
| Zerodha-gifted shares — client has added external trades entry for the same ISIN (double entry risk; Zerodha also auto-updates buy average) | Client ID, `tradingsymbol`, ISIN, `stock_gift_requests` details. |

---

### Rule 2 — Buy Average Handling

**2a. Buy average differs from expected**
1. Explain FIFO basis (A3). Point to View breakdown on Kite / Console.
2. Sold + bought back same day → intraday exception (A3).
3. Same-day change in invested value / buy average → check Kite Order History and Kite Positions for today's executed sell trades. If found → partial sell FIFO impact (A3).

**2b. `buy_average` is null / N/A**
- `discrepant` > 0:
  1. If client reports a specific purchase (date, qty, or price) → run diagnostic checklist in Rule 4 first.
  2. Verify current exchange status via Kite holdings or instrument search. If listed → continue; if still unlisted/suspended → Rule 1.
  3. Invoke `console_eq_external_trades` for an entry for this ISIN:
     - Entry exists AND processing → buy average updates per A2.
     - Entry exists AND processed but avg still N/A → escalate.
     - No entry AND client did not buy on Zerodha → route to Rule 7.
  4. Client confirms purchase before 31 Jan 2018 with no records → apply grandfather clause (A3).
- `discrepant` = 0 AND `pending` > 0 → CA buy average adjustment in progress (A2).

**2c. `buy_average` = ₹0 AND `total_quantity` > 0**
1. Invoke `console_eq_holdings_breakdown`; check for entries with `exchange` = "BONUS".
2. Found → apply ₹0 buy average reason per A3.
3. Not found → escalate.

**2d. Buy average wrong after corporate action**
- Within 2 weeks of CA → adjustment in progress (A2).
- 3+ weeks post-CA → escalate.

**2e. Investment value mismatch**
- Common causes:
  - Recent CA → adjustment in progress (A2).
  - `discrepant` > 0 → invested value inaccurate until purchase details added (A7). For NCDs/bonds, note A7 market-value behavior and share A13 links.
  - Ensure equity-only comparison; Console dashboard may include mutual fund values separately.

---

### Rule 3 — Corporate Action Handling

**3a. Bonus — not credited / not visible**
1. Invoke `console_eq_external_trades`; check for a system-posted CA credit entry (e.g., `external_trade_type` = devolved or CA-related) for this ISIN.
   - If investigation at any step reveals REs (Rights Entitlements) or PPs (Partly Paid shares) instead of bonus shares → escalate. Do not proceed further. Do not draft any response.
2. Entry found but not in holdings → credit is in system; holdings update within ~1 trading day.
3. Invoke `console_eq_pseudo_holdings`; cross-reference `available` qty with this report for the same ISIN:
   - Both match → qty is correct; display-only issue. Request screenshot of the holdings page and continue with the checks below.
   - Mismatch → escalate.
4. No entry AND within bonus credit window (A2) → temp ISIN → perm ISIN conversion pending; CDSL SMS on credit. Temporary P&L drop is expected and auto-corrects.
5. Beyond 5 trading days from record date → escalate.

**3b. Split — qty / price**
1. Use `total_quantity`, `available`, `pending` from this report as source of truth — do not derive from recent trade history.
2. Invoke `kite_holdings`; check for post-split credit.
3. Full post-split qty in `kite_holdings` → split credit confirmed. Avg update timeline per A2; client can sell in the interim without P&L impact.
4. Partial / not credited → credit timeline per A2.
5. Beyond 5 trading days from record date → escalate.

**3c. Demerger — new shares or avg**
1. Shares not credited → new entity credit timeline per A2.
2. Avg not updated → split per Cost of Acquisition (COA) ratio announced by company (A5); Zerodha updates the buy average once the Cost of Acquisition is announced by the company.
3. COA announced but avg still not updated after 3 weeks → escalate.

**3d. Merger — share swap**
- Explain swap mechanics per A5. Fractional shares → cash to primary bank (A4).

**3e. Corporate action eligibility**
- Answer from A4 (general, sold-on-ex-date, pledged, settlement holiday / short delivery exceptions).
- If client reports missing CA benefit due to short delivery → route to Rule 9.

---

### Rule 4 — Quantity Mismatch Handling

1. Invoke `console_eq_pseudo_holdings`; cross-reference `available` qty with this report for the same ISIN:
   - Both match → qty is correct; display-only issue. Request screenshot of the holdings page and continue with the checks below.
   - Mismatch → escalate.
2. If stock was purchased within the last 90 days → invoke `console_eq_tradebook_prepared`; check for a subsequent sell trade:
   - Sell trade found → inform client of sale (date, qty, price); proceeds credited. Stop.
3. Diagnose by quantity field:
   - `t1` > 0 → T+1 settlement in progress (A1, A2).
   - `pending` > 0 → CA credit pending; timeline per A2.
   - `margin` > 0 → pledged as collateral (A9).
   - `loan` > 0 → LAS or external NBFC lending (A10); escalate.
   - All fields = 0 and stock not found → confirm `tradingsymbol` / ISIN and whether purchase has settled.

**Diagnostic checklist** (when client reports a discrepancy or a specific purchase that doesn't match holdings):
1. Invoke `console_eq_tradebook_prepared`; fetch all trades from 1-Apr-2017 to date for that `tradingsymbol`.
2. Apply FIFO to compute net qty (buy − sell chronologically).
3. If client describes a sale/redemption event, invoke `ledger_report`; check for matching credit entries.
4. Compare calculated qty with `available` qty in this report:
   - Calculated = available → bought on Zerodha, display/sync issue → escalate.
   - Calculated ≠ available AND no matching sale proceeds → likely transferred/gifted/IPO/off-market → route to Rule 7.

---

### Rule 5 — Pledge Handling

1. Describe `margin` field per A9 — pledged but still in client demat.
2. Selling pledged shares → CNC sell on Kite allowed without unpledge (A9).
3. Collateral reduced after selling → temporary reduction; auto-restored next trading day (A9).
4. Buyback tendering → unpledge first (A9).

---

### Rule 6 — T1 Handling

- `t1` > 0 → T+1 settlement; moves to `available` by end of today; visible in regular holdings from next trading day (A1, A2).

---

### Rule 7 — Discrepancy Handling

**7a. Transferred / ESOP / off-market shares**
1. Invoke `console_eq_external_trades`; check for an existing entry for this ISIN.
2. Entry exists AND processing → buy average updates per A2.
3. Entry exists AND processed but discrepancy not resolved → continue with `console_eq_external_trades` (that protocol's routing handles the appropriate path).
4. No entry:
   - Client says they already added details → go to 7d.
   - Client got an error when adding entry → go to 7g.
   - Client has no purchase details → go to 7f.
   - Otherwise → guide through self-resolution path per A7 (include entry rules).

**7b. Gift transfer in**
1. Invoke `console_eq_external_trades`; check for `external_trade_type` = gift.
2. Entry found → gift shares recorded at closing price on transfer date (A8); buy average reflects once processed.
3. No entry → escalate.

**7c. Gift / off-market P&L or avg queries**
- Gift in (avg/P&L) → A8; client can use discrepancy flow for actual acquisition cost; advise CA for tax filing.
- Off-market in (avg/P&L) → A8; manual add via discrepancy flow (A7).
- Gift out → A8 (exit date = transfer date, exit price = closing price).
- Off-market out → A8 (share transfer details for reversal, or update Tax P&L manually).

**7d. Client says they already added details**
1. Invoke `console_eq_external_trades` first.
2. Entry exists → continue with `console_eq_external_trades` (that protocol's routing handles the appropriate path: recalc-stuck, incorrect entry by client, or deletion).
3. No entry → guide through self-resolution path per A7.

**7e. NCD / bond transferred from another broker**
- `discrepant` > 0 → self-resolution path per A7. Note NCD market-value behavior (A7). Share A13 links (discrepancy explanation, add external trades).

**7f. Client doesn't have purchase details**
- Advise client to obtain details from previous broker (A7).

**7g. Error when adding entry**
1. Invoke `console_eq_external_trades` first — entry may have posted despite the error.
2. Entry found → buy average updates per A2.
3. No entry → evaluate A7 cannot-resolve conditions. Verify current exchange status via Kite holdings / instrument search before applying the unlisted/inactive exception:
   - Trading holiday → try next trading day.
   - Inactive / suspended (confirmed) → route to Rule 1.
   - Unlisted (confirmed) → route to Rule 1.
   - CA within 10 days → try after 10 days from CA date.
   - IPO within 3 days → try after 3 days from listing.

**7h. Zerodha-gifted shares — buy average double entry**
1. Invoke `stock_gift_requests`; verify Zerodha gift for this ISIN / stock.
2. Gift confirmed → invoke `console_eq_external_trades`; check for a client-added entry for the same ISIN.
3. Client-added entry exists → double entry risk (Zerodha auto-updates buy average; client has also added an entry manually) → escalate. Do not draft any client-facing response.
4. No client-added entry → buy average will be updated automatically by Zerodha; no further action required.

---

### Rule 8 — Loan (LAS) Handling

- `loan` > 0 → shares are either pledged via LAS or lent externally to an NBFC (A10). Escalate.

---

### Rule 9 — Short Delivery Handling

- Explain per A6 (two scenarios; auction vs close-out).
- Specific short delivery case reported by client → escalate.

---

### Rule 10 — Dividend and Debt Instrument Interest Handling

**10a. Dividend not received**
- Credited to primary bank; timeline per A2.
- Contact RTA (lookup per A11) — Zerodha does not process dividend payments. Escalate.

**10b. Dividend amount less than expected**
- TDS deducted before credit (rates per A11).

**10c. Dividend tracking**
- Kite and Console paths per A11.

**10d. G-Sec / NCD / bond interest**
- Credited by RBI / paying agent to primary bank; not through Zerodha.
- Timeline and eligibility per A2.
- RBI schedule and client tracking options per A11.

---

### Rule 11 — LIQUIDBEES Fractional Redemption

- Fractional units not sellable on secondary market → off-market transfer to AMC via CDSL Easiest (A12).
- Share A13 link for step-by-step process.
- Dormant account (> 24 months inactive) → Re-KYC required first (A12).

---

### Rule 12 — Holding Statement / SOT / SOH Request

1. If client requests for visa purposes or requests a signed / stamped copy → escalate.
2. Console holdings statement for a specific date is available at console.zerodha.com/portfolio/holdings.
3. For a PDF-based statement covering both holdings and transactions, the client can download the SOT / SOH (Statement of Transactions / Statement of Holdings) directly — share A13 — SOT / SOH holding statement article.
