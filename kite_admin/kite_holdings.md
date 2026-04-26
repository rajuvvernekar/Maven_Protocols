# kite_holdings

## Description

WHEN TO USE:

Customer asks about:
- Holdings quantity, invested value, or current value of stocks in their portfolio
- Shares not visible in holdings — missing after purchase, IPO allotment, ESOP, broker transfer, corporate action, or short delivery
- Buy average showing N/A, incorrect, or not updating after a corporate action (bonus/split/demerger)
- Buy average unchanged after selling and rebuying the same stock on the same day
- P&L discrepancy — day's P&L vs net P&L difference, P&L changing after 3:30 PM, total P&L seeming wrong
- T1 holdings — what T1 means, when T1 shares settle, or T1 quantity showing
- BTST (Buy Today Sell Tomorrow) — sale proceeds not available or short delivery risk
- Pledge and collateral — P symbol meaning, collateral quantity, whether pledged shares can be sold
- Unable to sell shares — CDSL TPIN authorisation failure or DDPI not activated
- Holdings LTP or exchange showing differently from marketwatch
- Sold stocks appearing as negative positions during the day
- Console vs Kite holdings value or quantity mismatch
- Smallcase vs Kite average price or holdings mismatch
- Bonus/split/demerger shares not credited or taking longer than expected
- Short delivery — shares not received, fund balance increased instead of shares

TRIGGER KEYWORDS: "holdings", "portfolio", "shares missing", "shares not visible", "not showing", "buy average", "avg cost", "N/A", "invested value", "P&L", "day's P&L", "net change", "T1", "T1 holdings", "settlement", "BTST", "pledge", "collateral", "P symbol", "TPIN", "DDPI", "authorise", "can't sell", "bonus not credited", "split shares", "demerger", "short delivery", "sold stocks negative", "Console Kite mismatch", "Smallcase", "exchange mismatch", "LTP different", "IPO shares", "ESOP", "transferred shares", "broker transfer"

## Protocol

# KITE HOLDINGS PROTOCOL


---

### A1 — Fundamentals

This tool shows a client's **settled equity holdings in demat** on Kite. Holdings = settled shares. Positions = open trades (intraday/derivatives/same-day delivery buys).

Shares bought today appear under Positions, not Holdings — they move to Holdings on T+1 after settlement.

Kite shows only actively traded/listed instruments. Suspended, delisted, unlisted, GSM 3+, locked-in ESOP may not appear. Console shows all.

Holdings LTP and exchange shown from whichever exchange has the higher previous closing price — not where shares were bought. Demat shares are not mapped to a specific exchange, so client can sell on either NSE or BSE.

Buy average on Kite is fetched from Console using FIFO. If not on Console → N/A on Kite.

**Sold stocks during the day:** When shares are sold from holdings during the trading day, they appear as a negative position (tagged HOLDING) in the Positions tab. This is normal — it allows intraday traders to buy them back. If the client doesn't intend to rebuy, the negative position can be ignored. Shares are debited from demat by end of day.


### A2 — Field Usage Rules

**Shareable fields:**

`instrument_name` | `quantity` | `avg_cost` | `t1_t2_holdings` | `mtf_quantity` | `mtf_average_price` | `mtf_value` | `mtf_initial_margin` | `pnl` | `net_change_percentage` | `daily_percentage_change` | `last_close_price` | `days_pnl` | `authorised_quantity` | `collateral_quantity` | `invested_value` | `total_current_value`

**Internal-only fields** (use for reasoning; communicate outcomes in plain language):

`ltp`

**Client-facing terminology:**

| Internal Term | Client-Facing Alternative |
|---|---|
| `ltp` | "current market price" |


### A3 — Settlement Schedule

| Event | Timeline |
|---|---|
| Equity settlement | T+1 — bought Monday, in demat by Tuesday evening |
| F&O physical delivery (ITM options/futures expiry) | T+1 delivery. Short delivery: up to T+2 |
| Bonus shares | ~T+2 from record date; initially under temp ISIN, trading approved in 4–5 days |
| Split shares | Up to 2 working days from ex-date; if not credited after 4 days → escalate |
| IPO allotment | Visible after listing; may take a day to reflect on Kite |


### A4 — T1 / BTST Rules

- T1 shares can be sold (BTST) but credit from selling T1 is unavailable same day.
- BTST sale proceeds available from next trading day (after EPI process).
- Settlement holiday: BTST credit may take T+2.
- BTST carries short delivery risk if original seller defaults.
- DP charges apply for BTST trades.

**BTST detection method:**

1. Check `kite_order_history` for the sell date and one previous trading day (account for holidays in between).
2. If the stock was bought on the previous trading day and sold today → this is a BTST trade.
3. As an additional confirmation, check `console_eq_holdings` for the sell date and check if the quantity exists under `t1`. Only the quantity under `t1` is considered BTST — remaining quantity is from older settled holdings.
4. Blocked value for BTST = `filled_quantity × average_price` (from the sell order).

**Example:** Client had 50 shares (settled) and bought 100 more yesterday. Today they sell 150 shares. 100 shares are BTST (bought yesterday, showing under t1), 50 are settled holdings. Proceeds for the 100 BTST shares are blocked; proceeds for the 50 settled shares are available immediately.

For details: [T1 holdings proceeds](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-holdings/articles/t1-holdings-proceeds)


### A5 — Corporate Action Impact on Holdings

| CA Type | Impact |
|---|---|
| Bonus | Credited ~T+2 from record date under temp ISIN. P&L shows artificial drop until credited. Trading approval 4–5 days. Buy avg auto-adjusted (~2 weeks). |
| Split | New shares credited within 2 working days from ex-date. P&L temporarily distorted. If not credited after 4 days → escalate. |
| Demerger | New entity shares credited post-record date. Timelines vary by company/RTA. Buy avg updated manually by Zerodha. |
| Eligibility | Must hold on or before day before ex-date/record date (T+1 settlement). Pledged shares still eligible. |


### A6 — Shares Not Visible: Possible Reasons

| Reason | Explanation |
|---|---|
| Privacy Mode enabled | Client has Privacy Mode turned on — hides holdings, positions, P&L, and balances on screen. Data is intact; only display is hidden. To disable: tap user ID (top-right on Kite web, or profile icon on the app) → toggle Privacy Mode off. Links: [Kite web](https://support.zerodha.com/category/trading-and-markets/general-kite/others-kite/articles/privacy-mode-on-kite-web) / [Kite app](https://support.zerodha.com/category/trading-and-markets/general-kite/others-kite/articles/privacy-mode-on-kite-app) |
| Shares already sold | Client may have sold shares — verify via tradebook before other checks. Share the FIFO buy/sell trail with dates, quantities, and prices so the client can see the breakdown. |
| Short delivery by seller | Investigate per **A12** checklist. Zerodha notifies via SMS/email. |
| Pending settlement (T1) | Check `t1_t2_holdings` field. |
| Corporate action in progress | Wait per **A5** timelines. P&L may show a temporary drop until new shares are credited — this auto-corrects. |
| ESOP with lock-in | Not shown on Kite. Still in demat account — verify via CDSL statement (SOT/SOH). |
| Suspended/delisted | May not appear on Kite. Check Console for a complete view of all holdings including non-tradeable instruments. |
| Transfer from other broker pending | Check CDSL Easiest status. Once credited to Zerodha demat, shares appear in holdings. Client will need to update buy average manually on Console: [How to update buy average](https://support.zerodha.com/category/console/portfolio/console-holdings/articles/how-to-update-buy-average) |
| IPO allotment not yet credited | Check CDSL SMS/email for credit confirmation. If allotment is confirmed but shares aren't visible on Kite, wait until end of listing day. |


### A7 — Buy Average Issues

| Scenario | Cause & Resolution |
|---|---|
| avg_cost = N/A or 0 | Transferred shares (update manually on Console), CA pending adjustment, ESOP/off-market. Update path: [How to update buy average](https://support.zerodha.com/category/console/portfolio/console-holdings/articles/how-to-update-buy-average) |
| Incorrect after CA | Auto-adjusted within ~2 weeks from record date. If longer → raise a ticket. |
| Sell + rebuy same day = avg unchanged | Intraday = speculative, not delivery — shares don't physically move in/out of demat. Exception: T2T stocks (avg updates to latest buy). |


### A8 — P&L Calculations

**Day's P&L** = (LTP − previous close) × quantity.

**Net change** = ((LTP − avg_cost) / avg_cost) × 100.

**After 3:30 PM:** Kite switches from LTP to official closing price (weighted avg of last 30 min). P&L shifts slightly — normal.

**If LTP is N/A:** Invested value excluded from total to avoid incorrect P&L. Client should update buy average on Console to fix total P&L calculation.

**Smallcase vs Kite:** Kite uses FIFO, Smallcase uses simple average — prices may differ. If client sold Smallcase stocks directly on Kite, Smallcase platform may not reflect this — contact help@smallcase.com for Smallcase-specific discrepancies.


### A9 — Links

| Topic | URL |
|---|---|
| Update buy average | https://support.zerodha.com/category/console/portfolio/console-holdings/articles/how-to-update-buy-average |
| Generate CDSL TPIN | https://support.zerodha.com/category/trading-and-markets/trading-faqs/general/articles/generate-cdsl-tpin |
| Activate DDPI | https://support.zerodha.com/category/your-zerodha-account/your-profile/ddpi/articles/activate-ddpi |
| Pledge approved list | https://zerodha.com/approved-securities/#tab-noncash_equity |
| Short delivery info | https://support.zerodha.com/category/trading-and-markets/trading-faqs/general/articles/what-is-short-delivery-and-what-are-its-consequences |
| T1 holdings proceeds | https://support.zerodha.com/category/trading-and-markets/general-kite/kite-holdings/articles/t1-holdings-proceeds |
| Privacy Mode (Kite web) | https://support.zerodha.com/category/trading-and-markets/general-kite/others-kite/articles/privacy-mode-on-kite-web |
| Privacy Mode (Kite app) | https://support.zerodha.com/category/trading-and-markets/general-kite/others-kite/articles/privacy-mode-on-kite-app |


### A10 — Escalation Data Template

When escalating, always include: **client ID, instrument_name, and specific issue.**


### A11 — Short Delivery Investigation Checklist

Use this checklist when a client reports shares missing or unexpected debit related to short delivery.

**Step 1 — Confirm short delivery occurred:**
Invoke `get_all_client_data` and check `communications` for a `campaign_name` containing "Short delivery" or "Upper Circuit". The date in the communication (format: DDMMYYYY, e.g., 20032026 = 20th March 2026) identifies when the short delivery occurred. The `content` field provides details for cross-verification.

**Step 2 — Determine buy-side or sell-side:**
Invoke `ledger_report` (check the last 2 weeks) and search for a `remarks` entry stating "Short delivery margin blocked for sale of till exchange auction settlement".

- **If ledger entry is NOT found:** This is a buy-side short delivery — the client purchased shares but the seller did not deliver. Use the `content` from the communications (Step 1) to share details with the client. Two possible outcomes: (1) If the exchange can procure shares via auction, they will be credited to the client's demat by T+2. (2) If shares cannot be procured, the client's account will be credited with cash based on the close-out price. Client will receive an email confirming which outcome applies.

- **If ledger entry IS found:** This is a sell-side short delivery — the client's sold shares are going through auction. Use the `posting_date` and `debit` amount from the ledger entry. The debit amount is 120% of the closing price on the date of the sell trade. Two possible outcomes: (1) If the exchange completes the auction, the blocked amount is used for settlement and any excess is refunded. (2) If the auction does not result in delivery, the settlement is done at close-out price. Client will receive an email with the final outcome.

**Reference:** [What is short delivery and what are its consequences?](https://support.zerodha.com/category/trading-and-markets/trading-faqs/general/articles/what-is-short-delivery-and-what-are-its-consequences)


### A12 — Buy Average Discrepancy Investigation Checklist

Use this checklist when `avg_cost` = N/A and the client's holdings quantity may not match their trade history (e.g., client reports N/A average, partial sale left remaining shares with no average, or quantity seems inconsistent with order history).

**Step 1 — Check for discrepant shares:**
Invoke `console_eq_pseudo_holdings` for the instrument. Check if the `discrepant` entry is greater than 0. If `discrepant` = 0, this checklist does not apply — fall through to standard A7 diagnostics (transferred/CA/ESOP).

**Step 2 — Verify trade history matches holdings quantity:**
Invoke `console_eq_tradebook_prepared` for the instrument. Count the total traded quantity and check if it matches the `quantity` from `kite_holdings`. If the quantity matches, this checklist does not apply — fall through to standard A7 diagnostics.

**Step 3 — Check for client-added external trade entries:**
If quantity does not match (from Step 2), invoke `console_eq_external_trades` for the instrument. Check the `discrepant` column to see if the client has added any entry.

- **If no data found for the stock in external trades:** escalate to support agent — the discrepancy cannot be resolved via available tools. Include client ID, instrument, holdings quantity, and tradebook quantity in escalation.

- **If client has added an entry:** Check the date of the entry.
  - **If the entry date is more than 3 days from the current date:** escalate to support agent — the update should have reflected by now but hasn't. Include client ID, instrument, entry date, and discrepant quantity in escalation.
  - **If the entry date is less than 3 days from the current date:** the buy average is being updated. The external trade entry typically reflects within 2 working days. If the average still shows N/A after 2 working days, raise a support ticket.


---

### Preflight (run on every query)

```
0. If client reports holdings/positions/P&L not visible or showing as hidden
   → Privacy Mode may be enabled. Check per A6 Privacy Mode row.
1. Search kite_holdings by instrument_name.
2. If found:
   ├─ Check quantity, t1_t2_holdings, avg_cost, collateral_quantity, pnl, days_pnl
   └─ If mtf_quantity > 0 → holding under MTF. Redirect to MTF protocol
      for MTF-specific queries (charges, interest, conversion).
3. If NOT found:
   ├─ Check if shares bought today → invoke kite_positions
   └─ If not in positions either → route to Rule 5 (shares not visible)
```

### Route

```
Intent / Condition                                          → Rule
──────────────────────────────────────────────────────────────────────
P&L questions (day's P&L, net P&L, total, post-3:30)       → Rule 1
Buy average / portfolio valuation / invested amount issues  → Rule 2
T1 / settlement / BTST query                               → Rule 3
Pledge / collateral status                                  → Rule 4
Shares not visible                                          → Rule 5
CDSL TPIN / DDPI — can't sell                               → Rule 6
Exchange / LTP mismatch                                     → Rule 7
Sold stocks showing as negative positions                   → Rule 8
Console vs Kite value mismatch                              → Rule 9
Smallcase vs Kite mismatch                                  → Rule 10
```

### Scope

- Address the client's query about their settled equity holdings on Kite — visibility, P&L, buy average, settlements, pledges, and authorisation.
- Use **A2** field rules and client-facing terminology in all client communication.
- For intraday/F&O position queries, redirect to `kite_positions`. For MTF-specific queries, redirect to MTF protocol.

### Fallback

If no route matches, investigate using Section A reference data. If no root cause is found, escalate per **A10**.


---

### Rule 1 — P&L Questions

1. Day's P&L vs Net P&L confusion → Day's P&L shows today's change from yesterday's closing price. Net change shows the total change from the client's buy average. These are different calculations (per **A8**).
2. P&L changed after 3:30 PM → after 3:30 PM, Kite switches from the last traded price to the official closing price (weighted average of trades between 3:00–3:30 PM). This causes P&L to shift slightly — it's normal (per **A8**).
3. Total P&L seems wrong → check for `avg_cost` = 0 or N/A. Some holdings have no buy average recorded, so their invested value is excluded from the total calculation. Guide client to update buy average on Console (per **A7**, **A8**, link in **A9**).
4. If client asks about intraday or F&O position P&L → invoke `kite_positions`.


### Rule 2 — Buy Average Issues

0. If client reports incorrect portfolio value or invested amount: check `console_eq_pseudo_holdings` and `console_eq_holdings` for the instrument(s). Compare breakdown quantities and buy averages with `kite_holdings`. Calculate expected invested value (sum of qty × avg_cost for each holding) and compare with the displayed value. If discrepancies are found in specific holdings, proceed to Step 1 for those holdings.
1. `avg_cost` = N/A or 0 → investigate per **A12** checklist first (check for discrepant shares via `console_eq_pseudo_holdings`). If `discrepant` > 0 and quantity mismatch confirmed, follow A12 through to resolution or escalation. If A12 does not apply (discrepant = 0 or quantity matches), diagnose reason:
   a. Transferred shares → buy average shows N/A because shares were transferred from another broker. Guide client to update manually on Console (per **A7**, link in **A9**).
   b. CA pending adjustment → buy average is being adjusted following a recent corporate action. Auto-updates within ~2 weeks from the record date (per **A5**, **A7**).
   c. ESOP/off-market → buy average shows N/A for shares received via ESOP or off-market transfer. Guide client to update manually on Console (per **A7**, link in **A9**).
2. Incorrect after CA → after corporate actions like bonus, split, or demerger, buy average may temporarily be incorrect. Zerodha adjusts this within ~2 weeks from the record date. If it's been longer, raise a ticket (per **A5**, **A7**).
3. Sell + rebuy same day, avg unchanged → this is treated as an intraday trade — shares don't physically move in/out of demat, so buy average stays unchanged. Exception: T2T stocks where buy average updates to latest buy price (per **A7**).
4. If client wants to verify original purchase → invoke `kite_order_history`.


### Rule 3 — T1 / Settlement / BTST

1. T1 meaning → check `t1_t2_holdings`. The T1 shares were purchased yesterday and are awaiting settlement. They'll be credited to the client's demat account by end of T+1 day (per **A3**, **A4**).
2. When a client reports sale proceeds not available or funds not credited after selling shares, check for BTST first:
   a. Check `kite_order_history` for the sell date and one previous trading day (account for any holidays in between).
   b. If the stock was bought on the previous trading day and sold today, this is a BTST trade.
   c. Check `console_eq_holdings` for the sell date. Check if the quantity exists under `t1` — only the `t1` quantity is BTST.
   d. Calculate blocked value: `filled_quantity × average_price` (from the sell order for the BTST quantity).
   e. Inform client: the shares sold were purchased on the previous trading day (T1/BTST). The sale proceeds are blocked and will be available from the next trading day after the Early Pay-In process completes. If a settlement holiday falls in between, it may take an additional day. Share the BTST quantity and blocked value. Link: **A9** T1 holdings proceeds (per **A4**).
   f. Settlement holiday: if a settlement holiday falls between the buy and sell dates, settlement extends — BTST credit may take an additional day.
3. If client asks why proceeds not reflected in balance → invoke `kite_margins`.


### Rule 4 — Pledge / Collateral Status

1. P symbol / `collateral_quantity` → the client has pledged shares as collateral. The P symbol shows the pledged quantity. The remaining shares (total minus collateral) are available for trading (per **A1**).
2. Can I sell pledged shares? → yes, pledged shares can be sold instantly without placing an unpledge request. However, selling pledged holdings will reduce the client's collateral margin.
3. Collateral reduced after selling → cross-check `kite_margins` for current equity_collateral and total_collateral.
4. For pledge/unpledge process or why can't pledge a specific stock → redirect to pledge protocol.
5. Can collateral margin be used for equity delivery (CNC) purchases? → collateral margin from pledged shares can be used for equity intraday trading, futures, and options (buying and writing). For equity delivery (CNC) purchases, available cash or cash-equivalent margin is required — collateral margin alone is not sufficient for buying shares for delivery (per Kite Margins **A6**).


### Rule 5 — Shares Not Visible

**Step 0 — Check Privacy Mode:**
If client reports holdings/positions/P&L as hidden or not visible on screen → Privacy Mode may be enabled. Guide client to disable: tap user ID (top-right on Kite web, or profile icon on the app) → toggle Privacy Mode off. Data is intact — Privacy Mode only hides the display. Links per **A6** Privacy Mode row.

**Step 1 — Verify client still holds the shares:**
Invoke `console_eq_tradebook` for the instrument within the relevant date range. Compute the net quantity using FIFO: sum all BUY quantities and subtract all SELL quantities in chronological order. If the net remaining quantity is zero or negative → the client has sold all shares. Share the buy/sell summary (dates, quantities, prices) so the client can see the FIFO trail — this is why the shares no longer appear in holdings. If the net remaining quantity is positive but less than what the client expects → inform the client of the actual remaining quantity with the FIFO breakdown, then proceed to investigate the missing portion using the steps below.

2. Systematically check causes from **A6**:
   a. Recently purchased → shares bought today appear under Positions, not Holdings. They'll move to Holdings on T+1 day after settlement (per **A1**, **A3**). Invoke `kite_positions`.
   b. CA in progress (bonus/split/demerger) → new shares are credited within the timelines per **A5**. P&L may show a temporary drop until credited — this auto-corrects (per **A6**).
   c. Short delivery → invoke `get_all_client_data` and check `communications` for a `campaign_name` containing "Short delivery" or "Upper Circuit" to confirm whether a short delivery occurred. Complete the full **A11** checklist before responding. Respond based on buy-side or sell-side findings from **A11**.
   d. ESOP with lock-in → ESOP shares with lock-in periods may not appear on Kite. They're still in the client's demat account — verify via CDSL statement (SOT/SOH) (per **A6**).
   e. Suspended/delisted → may not appear on Kite. Check Console for a complete view of all holdings including non-tradeable instruments (per **A1**, **A6**).
   f. Transfer from another broker → check CDSL Easiest transfer status. Once credited to Zerodha demat, shares appear in holdings. Client will need to update buy average manually on Console (per **A6**, link in **A9**).
   g. IPO allotment → IPO shares appear after listing. Check CDSL SMS/email for credit confirmation. If allotment is confirmed but shares aren't visible on Kite, wait until end of listing day (per **A3**, **A6**).
3. If client confirms order was placed → invoke `kite_order_history` to verify execution.


### Rule 6 — CDSL TPIN / DDPI (Can't Sell)

1. Check `authorised_quantity` for the stock.
2. TPIN not generated / authorisation failed → to sell shares, the client needs to authorise them via CDSL TPIN. Guide to generate TPIN (link in **A9**).
3. DDPI not activated → the client can avoid daily TPIN authorisation by activating DDPI (Demat Debit and Pledge Instruction). Guide to activate DDPI (link in **A9**).
4. If sell order was rejected (not authorisation issue) → invoke `kite_orders` for rejection reason.
5. If GTT sell order didn't trigger → invoke `kite_gtt`.


### Rule 7 — Exchange / LTP Mismatch

1. Kite displays holdings from the exchange with the higher previous closing price — not necessarily where the client bought the shares. Demat shares are not mapped to a specific exchange, so the client can sell on either NSE or BSE. Advise checking prices on both exchanges before selling to get the best price (per **A1**).


### Rule 8 — Sold Stocks as Negative Positions

1. When shares are sold from holdings during the trading day, they appear as a negative position (tagged HOLDING) in the Positions tab. This is normal — it allows intraday traders to buy them back. If the client doesn't intend to rebuy, the negative position can be ignored. Shares are debited from demat by end of day (per **A1**).
2. If client asks about sell order details → invoke `kite_orders`.


### Rule 9 — Console vs Kite Mismatch

1. Kite shows only actively traded, listed instruments. Console shows everything including suspended, delisted, unlisted shares, GSM 3+ stocks, and locked-in ESOP shares. The value difference is typically from these instruments that Kite cannot price accurately (per **A1**).


### Rule 10 — Smallcase vs Kite Mismatch

1. Kite and Smallcase may show different average prices because Kite uses the FIFO method while Smallcase uses simple average. Also, if the client sold Smallcase stocks directly on Kite, the Smallcase platform may not reflect this — contact help@smallcase.com for Smallcase-specific discrepancies (per **A8**).
