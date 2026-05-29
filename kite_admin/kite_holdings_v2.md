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
- SGB interest missing or delayed
- LIQUIDBEES fractional units — cannot sell

TRIGGER KEYWORDS: "holdings", "portfolio", "shares missing", "shares not visible", "not showing", "buy average", "avg cost", "N/A", "invested value", "P&L", "day's P&L", "net change", "T1", "T1 holdings", "settlement", "BTST", "pledge", "collateral", "P symbol", "TPIN", "DDPI", "authorise", "can't sell", "bonus not credited", "split shares", "demerger", "short delivery", "sold stocks negative", "Console Kite mismatch", "Smallcase", "exchange mismatch", "LTP different", "IPO shares", "ESOP", "transferred shares", "broker transfer", "SGB interest", "liquidbees", "fractional units"

## Protocol

# KITE HOLDINGS PROTOCOL

---

## Section A: Reference Data

---

### A1 — Fundamentals

Holdings = settled shares in demat on Kite. Positions = open trades (intraday / derivatives / same-day delivery buys).

Shares bought today appear under Positions, not Holdings — they move to Holdings on T+1 after settlement.

Kite shows only actively traded and listed instruments. Suspended, delisted, unlisted, GSM 3+, and locked-in ESOP shares may not appear on Kite. Console shows all instruments including non-tradeable ones; invoke `console_eq_holdings` when a complete view is needed.

Holdings LTP and exchange are shown from whichever exchange has the higher previous closing price — not where shares were bought. Demat shares are not mapped to a specific exchange, so the client can sell on either NSE or BSE.

Buy average on Kite is fetched from Console using FIFO. If not on Console → N/A on Kite.

When shares are sold from holdings during the trading day, they appear as a negative position (tagged HOLDING) in the Positions tab. This is normal — it allows intraday traders to buy them back. Shares are debited from demat by end of day.

---

### A2 — Field Usage Rules

**Shareable fields:**

`instrument_name` | `quantity` | `avg_cost` | `t1_t2_holdings` | `mtf_quantity` | `mtf_average_price` | `mtf_value` | `mtf_initial_margin` | `pnl` | `net_change_percentage` | `daily_percentage_change` | `last_close_price` | `days_pnl` | `authorised_quantity` | `collateral_quantity` | `invested_value` | `total_current_value`

**Internal-only:** `ltp` — refer to clients as "current market price"

---

### A3 — Settlement Schedule

T = trading day.

| Event | Timeline |
|---|---|
| Equity settlement | T+1 — shares settle in demat by end of T+1 |
| F&O physical delivery (ITM options / futures expiry) | T+1 delivery. Short delivery: up to T+2. |
| Bonus shares | ~T+2 from record date; initially under temp ISIN, trading approved in 4–5 days |
| Split shares | Up to 2 working days from ex-date; if not credited after 4 days → escalate to support agent |
| IPO allotment | Visible after listing |

---

### A4 — T1 / BTST Rules

- T1 shares can be sold (BTST) but credit from selling T1 is unavailable same day.
- BTST sale proceeds available from the next trading day.
- Settlement holiday: BTST credit may take T+2.
- BTST carries short delivery risk if the original seller defaults.
- DP charges apply for BTST trades.

For BTST sales, a ledger 'net settlement' credit posted on the sale date does not mean funds are usable. Funds become available only from the next trading day.

---

### A5 — Corporate Action Impact on Holdings

| CA Type | Impact |
|---|---|
| Bonus | Credited ~T+2 from record date under temp ISIN. P&L shows artificial drop until credited — auto-corrects. Trading approval 4–5 days. Buy avg auto-adjusted (~2 weeks). |
| Split | New shares credited within 2 working days from ex-date. P&L temporarily distorted — auto-corrects. If not credited after 4 days → escalate to support agent. |
| Demerger | New entity shares credited post-record date. Timelines vary by company/RTA. Buy avg updated manually by Zerodha. |

CA eligibility: must hold shares on or before the day before ex-date/record date (T+1 settlement applies). Pledged shares are still eligible.

---

### A6 — Shares Not Visible: Possible Reasons

| Reason | Explanation |
|---|---|
| Privacy Mode enabled | Client has Privacy Mode turned on — hides holdings, positions, P&L, and balances on screen. Data is intact; only display is hidden. To disable: tap user ID (top-right on Kite web, or profile icon on the app) → toggle Privacy Mode off. Links per A12. |
| Shares already sold | Client may have sold shares. |
| Short delivery by seller | Zerodha notifies the client via SMS/email. |
| Pending settlement (T1) | Shares are awaiting settlement — check `t1_t2_holdings`. |
| Corporate action in progress | New shares pending per A5 timelines. P&L may show a temporary drop until credited — auto-corrects. |
| ESOP with lock-in | Not shown on Kite. Shares are still in demat — verify via CDSL statement (SOT/SOH). |
| Suspended/delisted | May not appear on Kite. Console shows all instruments including non-tradeable ones. |
| Transfer from other broker pending | Shares appear in holdings once credited to Zerodha demat. Client must update buy average manually on Console — link in A12. |
| IPO allotment not yet credited | Check CDSL SMS/email for credit confirmation. |

---

### A7 — Buy Average Issues

| Scenario | Cause & Resolution |
|---|---|
| avg_cost = N/A or 0 | Transferred shares (update manually on Console), CA pending adjustment, ESOP/off-market. Update path in A12. |
| Incorrect after CA | Auto-adjusted within ~2 weeks from record date. If longer → raise a support ticket. |
| Sell + rebuy same day = avg unchanged | Intraday = speculative, not delivery — shares don't physically move in/out of demat. Exception: T2T stocks (avg updates to latest buy). |

---

### A8 — P&L Calculations

**Day's P&L** = (LTP − previous close) × quantity.

**Net change** = ((LTP − avg_cost) / avg_cost) × 100.

After 3:30 PM: Kite switches from LTP to official closing price (weighted avg of last 30 min). P&L shifts slightly — normal.

If LTP is N/A: Invested value excluded from total to avoid incorrect P&L. Client should update buy average on Console to fix total P&L calculation.

Kite uses FIFO for buy average; Smallcase uses simple average — prices may differ when both platforms hold the same stock. If the client sold Smallcase stocks directly on Kite, the Smallcase platform may not reflect this.

---

### A9 — Sovereign Gold Bonds (SGBs)

SGBs held in demat are managed by RBI, not Zerodha.

- Interest is paid by RBI directly to the client's registered bank account, typically semi-annually at 2.5% per annum.
- For missing or delayed SGB interest credits, the client can write to CDSL at `gsec@cdslindia.com`. CDSL is the RTA for SGBs. Zerodha cannot resolve SGB interest issues directly.
- RBI issue dates and interest payout schedules are available on TradingQnA and RBI publications.
- Reference article per A12.

---

### A10 — LIQUIDBEES Fractional Units

LIQUIDBEES holdings often include fractional units created through daily dividend reinvestment (e.g., 0.44 units).

Fractional units cannot be sold on the exchange. Exchange trading requires whole units only. Redemption path for fractionals: off-market transfer to the AMC's demat account. A normal sell order will be rejected for fractional units.

Reference article per A12.

---

### A11 — Escalation Data Template

When escalating, include: **client ID, instrument_name, and specific issue.**

---

### A12 — Links

| Topic | URL |
|---|---|
| Update buy average | https://support.zerodha.com/category/console/portfolio/console-holdings/articles/how-to-update-buy-average |
| Generate CDSL TPIN | https://support.zerodha.com/category/trading-and-markets/trading-faqs/general/articles/generate-cdsl-tpin |
| Activate DDPI | https://support.zerodha.com/category/your-zerodha-account/your-profile/ddpi/articles/activate-ddpi |
| Pledge approved list | https://zerodha.com/approved-securities/#tab-noncash_equity |
| Short delivery info | https://support.zerodha.com/category/trading-and-markets/trading-faqs/general/articles/what-is-short-delivery-and-what-are-its-consequences |
| T1 holdings proceeds | https://support.zerodha.com/category/trading-and-markets/general-kite/kite-holdings/articles/t1-holdings-proceeds |
| What are SGBs | https://support.zerodha.com/category/console/portfolio/console-holdings/articles/what-are-sgbs |
| How to redeem fractional LIQUIDBEES units | https://support.zerodha.com/category/console/portfolio/console-holdings/articles/how-to-redeem-fractional-units-of-liquidbees |
| Privacy Mode on Kite web | https://support.zerodha.com/category/trading-and-markets/general-kite/others-kite/articles/privacy-mode-on-kite-web |
| Privacy Mode on Kite app | https://support.zerodha.com/category/trading-and-markets/general-kite/others-kite/articles/privacy-mode-on-kite-app |

---

## Section B: Decision Flow

---

### Preflight

```
1. Search kite_holdings by instrument_name.
2. If found and mtf_quantity > 0 → redirect to MTF protocol for MTF-specific queries.
3. If NOT found:
   ├─ If shares bought today → invoke kite_positions
   └─ If not in positions either → route to Rule 5
```

### Route

```
Query relates to holdings →
│
├─ Day's P&L / net P&L / total P&L / P&L after 3:30 PM → Rule 1
├─ Buy average or invested value issues → Rule 2
├─ T1 / settlement / BTST / sale proceeds missing → Rule 3
├─ Pledge / collateral status → Rule 4
├─ Shares not visible → Rule 5
├─ CDSL TPIN / DDPI — can't sell → Rule 6
├─ Exchange or LTP shown from unexpected exchange → Rule 7
├─ Sold stocks showing as negative positions → Rule 8
├─ Console vs Kite value mismatch → Rule 9
├─ Smallcase vs Kite mismatch → Rule 10
├─ SGB interest missing or delayed → Rule 11
└─ LIQUIDBEES fractional units — cannot sell → Rule 12
```

### Fallback

If no route matches, investigate using Section A reference data. If no root cause is found, escalate to a human agent per A11.

---

## Section C: Rules

---

### Rule 1 — P&L Questions

1. Day's P&L vs Net P&L confusion → explain per A8 that Day's P&L shows today's change from yesterday's closing price, while Net change shows the total change from the client's buy average.
2. P&L changed after 3:30 PM → explain per A8 that after 3:30 PM, Kite switches from LTP to the official closing price (weighted average of trades between 3:00–3:30 PM). This causes P&L to shift slightly and is normal.
3. Total P&L seems wrong → check for `avg_cost` = 0 or N/A. Per A7 and A8, holdings with no buy average recorded have their invested value excluded from the total calculation. Guide client to update buy average on Console per A12.
4. Intraday or F&O position P&L → invoke `kite_positions`.

---

### Rule 2 — Buy Average Issues

1. Incorrect portfolio value or invested amount → invoke `console_eq_pseudo_holdings` and `console_eq_holdings` for the instrument(s). Compare breakdown quantities and buy averages with `kite_holdings`. If discrepancies are found in specific holdings, proceed to Step 2 for those holdings.
2. `avg_cost` = N/A or 0 → follow Rule 14 first. If Rule 14 does not apply, diagnose reason per A7:
   a. Transferred shares → shares transferred from another broker show N/A because no purchase record exists. Guide client to update manually on Console per A12.
   b. CA pending adjustment → buy average is being adjusted following a recent corporate action. Auto-updates within ~2 weeks from the record date per A5.
   c. ESOP/off-market → shares received via ESOP or off-market transfer show N/A. Guide client to update manually on Console per A12.
3. Incorrect after CA → explain per A5 and A7 that Zerodha auto-adjusts buy average within ~2 weeks from the record date. If longer, raise a support ticket.
4. Sell + rebuy same day, avg unchanged → explain per A7 that this is treated as an intraday trade — shares do not physically move in/out of demat, so buy average stays unchanged. Exception: T2T stocks, where buy average updates to the latest buy price.
5. Original purchase verification → invoke `kite_order_history`.

---

### Rule 3 — T1 / Settlement / BTST / Missing Sale Proceeds

1. T1 meaning → check `t1_t2_holdings`. Per A3 and A4, T1 shares were purchased on the previous trading day and are awaiting settlement. They will be credited to the client's demat by end of T+1.

2. **BTST detection:**

   Per A4, a ledger 'net settlement' credit on T-day does not mean funds are usable for BTST sales.

   a. Invoke `kite_order_history` for the sell date and one previous trading day (account for holidays).
   b. If the stock was bought on the previous trading day and sold today → this is a BTST trade. Proceed with BTST handling.
   c. Additional confirmation — invoke `console_eq_holdings` for the sell date. Only the quantity under `t1` is BTST; remaining quantity is from older settled holdings.
   d. Blocked value: `filled_quantity × average_price` (from the sell order for the BTST quantity).
   e. Communicate to the client:
      - The sold shares were purchased on the previous trading day (T1/BTST).
      - Sale proceeds are blocked and will be available from the next trading day.
      - If a settlement holiday falls in between, it may take an additional day.
      - Share the BTST quantity and blocked value.
      - Any ledger credit posted on T-day for this BTST sale does not mean funds are usable yet.
      - Link per A12 (T1 holdings proceeds).
   f. If detection shows the sale was NOT BTST (shares were bought earlier, not the previous trading day) → per A4, proceeds from normal CNC sales are available same day. If the client still reports missing funds, invoke `ledger_report` to investigate other debits (charges, MTM, auction).

3. If client asks why proceeds are not reflected in balance after BTST detection → invoke `kite_margins`.

---

### Rule 4 — Pledge / Collateral Status

1. P symbol / `collateral_quantity` → explain per A1 that the client has pledged shares as collateral. The P symbol shows the pledged quantity. The remaining shares (total minus collateral) are available for trading.
2. Selling pledged shares → pledged shares can be sold instantly without placing an unpledge request. Selling pledged holdings reduces the collateral margin.
3. Collateral reduced after selling → invoke `kite_margins` for current `equity_collateral` and `total_collateral`.
4. Pledge / unpledge process or why a specific stock cannot be pledged → redirect to pledge protocol.
5. Using collateral margin for equity delivery (CNC) → collateral margin from pledged shares can be used for equity intraday, futures, and options (buying and writing). Cash or cash-equivalent margin is required for equity delivery (CNC) purchases — collateral alone is not sufficient.

---

### Rule 5 — Shares Not Visible

**Privacy Mode:**
If client reports holdings / positions / P&L as hidden or not visible on screen → Privacy Mode may be enabled. Guide client to disable per A6 Privacy Mode row.

**Verify client still holds the shares:**
Invoke `console_eq_tradebook` for the instrument within the relevant date range. Compute net quantity using FIFO: sum all BUY quantities and subtract all SELL quantities in chronological order. If net remaining quantity is zero or negative → client has sold all shares. Communicate the buy/sell summary with dates, quantities, and prices. If net remaining quantity is positive but less than expected → communicate the actual remaining quantity with FIFO breakdown, then investigate the missing portion.

**Diagnose per A6:**
a. Recently purchased → per A1 and A3, shares bought today appear under Positions, not Holdings. They move to Holdings on T+1. Invoke `kite_positions`.
b. CA in progress (bonus / split / demerger) → new shares are credited per A5 timelines. P&L may show a temporary drop until credited — auto-corrects per A5.
c. Short delivery → follow Rule 13 before responding.
d. ESOP with lock-in → per A6, ESOP shares with lock-in may not appear on Kite. Shares are still in demat — verify via CDSL statement (SOT/SOH).
e. Suspended/delisted → per A1 and A6, may not appear on Kite. Check Console for complete view including non-tradeable instruments.
f. Transfer from another broker → check CDSL Easiest transfer status. Once credited to Zerodha demat, shares appear in holdings. Guide client to update buy average manually on Console per A12.
g. IPO allotment → per A3 and A6, IPO shares appear after listing. Check CDSL SMS/email for credit confirmation.

**Order not executed:**
If client confirms an order was placed → invoke `kite_order_history` to verify execution.

---

### Rule 6 — CDSL TPIN / DDPI (Can't Sell)

1. Check `authorised_quantity` for the stock.
2. TPIN not generated / authorisation failed → to sell shares, the client needs to authorise them via CDSL TPIN. Guide to generate TPIN per A12.
3. DDPI not activated → the client can avoid daily TPIN authorisation by activating DDPI (Demat Debit and Pledge Instruction). Guide to activate DDPI per A12.
4. Sell order rejected (not authorisation issue) → invoke `kite_orders` for rejection reason.
5. GTT sell order didn't trigger → invoke `kite_gtt`.

---

### Rule 7 — Exchange / LTP Mismatch

Per A1, Kite displays holdings from the exchange with the higher previous closing price — not necessarily where the shares were bought. Demat shares are not mapped to a specific exchange, so the client can sell on either NSE or BSE. Advise checking prices on both exchanges before selling.

---

### Rule 8 — Sold Stocks as Negative Positions

1. Per A1, when shares are sold from holdings during the trading day, they appear as a negative position tagged HOLDING in the Positions tab. This is normal — it allows intraday traders to buy them back. If the client does not intend to rebuy, the negative position can be ignored. Shares are debited from demat by end of day.
2. Sell order details → invoke `kite_orders`.

---

### Rule 9 — Console vs Kite Mismatch

Per A1, Kite shows only actively traded, listed instruments. Console shows everything including suspended, delisted, unlisted shares, GSM 3+ stocks, and locked-in ESOP shares. The value difference is typically from instruments that Kite cannot price.

---

### Rule 10 — Smallcase vs Kite Mismatch

Per A8, Kite and Smallcase may show different average prices because Kite uses FIFO while Smallcase uses simple average. If the client sold Smallcase stocks directly on Kite, the Smallcase platform may not reflect this — the client should contact help@smallcase.com for Smallcase-specific discrepancies.

---

### Rule 11 — SGB Interest Missing or Delayed

1. Per A9, SGB interest is paid by RBI directly to the client's registered bank account, not routed through Zerodha.
2. Direct the client to write to CDSL at `gsec@cdslindia.com` — CDSL is the RTA for SGBs per A9. Zerodha cannot resolve SGB interest issues directly.
3. Share the SGB reference article per A12 for context on interest frequency and credit timeline.
4. Issue date / interest payout schedule → direct the client to TradingQnA or RBI publications per A9.

---

### Rule 12 — LIQUIDBEES Fractional Units

1. Per A10, fractional LIQUIDBEES units (created through daily dividend reinvestment) cannot be sold on the exchange. Exchange trading requires whole units only.
2. Redemption path: off-market transfer to the AMC's demat account per A10.
3. Share the redemption reference article per A12.

---

### Rule 13 — Short Delivery Investigation

**Confirm short delivery:**
Invoke `get_all_client_data` and check `communications` for a `campaign_name` containing "Short delivery" or "Upper Circuit". The date in the communication (format: DDMMYYYY, e.g., 20032026 = 20th March 2026) identifies when the short delivery occurred. The `content` field provides details for cross-verification.

**Determine buy-side or sell-side:**
Invoke `ledger_report` and search for a `remarks` entry: "Short delivery margin blocked for sale of till exchange auction settlement".

- **Ledger entry NOT found** — buy-side short delivery: the client purchased shares but the seller did not deliver. Use the `content` from the communications to share details with the client. Two outcomes: (1) If the exchange can procure shares via auction, they will be credited to the client's demat by T+2. (2) If shares cannot be procured, the client's account will be credited with cash based on the close-out price. Client will receive an email confirming which outcome applies.

- **Ledger entry found** — sell-side short delivery: the client's sold shares are going through auction. Use the `posting_date` and `debit` amount from the ledger entry. The debit amount is 120% of the closing price on the date of the sell trade. Two outcomes: (1) If the exchange completes the auction, the blocked amount is used for settlement and any excess is refunded. (2) If the auction does not result in delivery, settlement is done at close-out price. Client will receive an email with the final outcome.

Reference: short delivery info per A12.

---

### Rule 14 — Buy Average Discrepancy Investigation

**Discrepant shares check:**
Invoke `console_eq_pseudo_holdings` for the instrument. If `discrepant` = 0 → this rule does not apply; diagnose per A7.

**Trade history vs holdings quantity:**
Invoke `console_eq_tradebook_prepared` for the instrument. Count the total traded quantity and compare with `quantity` from `kite_holdings`. If quantity matches → this rule does not apply; diagnose per A7.

**Client-added external trade entries:**
Invoke `console_eq_external_trades` for the instrument. Check the `discrepant` column.

- **No data found** → escalate to a human agent per A11. Include client ID, instrument, holdings quantity, and tradebook quantity.
- **Client has added an entry — date more than 3 days ago** → escalate to a human agent per A11. The update should have reflected by now. Include client ID, instrument, entry date, and discrepant quantity.
- **Client has added an entry — date within 3 days** → buy average is being updated. External trade entries typically reflect within 2 working days. If the average still shows N/A after 2 working days, raise a support ticket.
