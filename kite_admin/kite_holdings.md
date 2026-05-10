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

TAGS: holdings, demat, corporate-actions

## Protocol

# KITE HOLDINGS PROTOCOL

## Section A: Reference Data

### A1 — Fundamentals

- Holdings = settled shares. Positions = open trades (intraday/derivatives/same-day delivery buys).  
- Shares bought today appear under Positions, not Holdings — they move to Holdings on T+1 after settlement.  
- Kite shows only actively traded/listed instruments. Suspended, delisted, unlisted, GSM 3+, locked-in ESOP may not appear. Console shows all.  
- Holdings LTP and exchange shown from whichever exchange has the higher previous closing price — not where shares were bought. Demat shares are not mapped to a specific exchange, so client can sell on either NSE or BSE.  
- Buy average on Kite is fetched from Console using FIFO. If not on Console → N/A on Kite.  
- **Sold stocks during the day:** When shares are sold from holdings during the trading day, they appear as a negative position (tagged HOLDING) in the Positions tab. This is normal — it allows intraday traders to buy them back. If the client doesn't intend to rebuy, the negative position can be ignored. Shares are debited from demat by end of day.

### A2 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |  
|---|---|  
| `instrument_name` | Stock symbol |  
| `quantity` | Quantity held |  
| `avg_cost` | Buy average |  
| `t1_t2_holdings` | T1 quantity (BTST eligible) |  
| `mtf_quantity` | MTF quantity |  
| `mtf_average_price` | MTF avg price |  
| `mtf_value` | MTF value |  
| `mtf_initial_margin` | MTF initial margin |  
| `pnl` | P&L |  
| `net_change_percentage` | Net % change |  
| `daily_percentage_change` | Day % change |  
| `last_close_price` | Previous close |  
| `days_pnl` | Today's P&L |  
| `authorised_quantity` | Quantity authorised for selling |  
| `collateral_quantity` | Pledged qty (collateral) |  
| `invested_value` | Total invested value |  
| `total_current_value` | Current value |

**Non-shareable:**

| Field | Interpretation |  
|---|---|  
| `ltp` | Use as "current market price" |

### A3 — Settlement Schedule

| Event | Timeline |  
|---|---|  
| Equity settlement | T+1 — bought Monday, in demat by Tuesday evening |  
| F&O physical delivery (ITM options/futures expiry) | T+1 delivery. Short delivery: up to T+2 |  
| Bonus shares | \~T+2 from record date; initially under temp ISIN, trading approved in 4–5 days |  
| Split shares | Up to 2 working days from ex-date |  
| IPO allotment | Visible after listing; may take a day to reflect on Kite |

### A4 — T1 / BTST Rules

- T1 shares can be sold (BTST) but credit from selling T1 is unavailable same day.  
- BTST sale proceeds available from next trading day (after EPI process).  
- Settlement holiday: BTST credit may take T+2.  
- BTST carries short delivery risk if original seller defaults.  
- DP charges apply for BTST trades.

Example: Client had 50 shares (settled) and bought 100 more yesterday. Today they sell 150 shares. 100 are BTST (under t1), 50 are settled. Proceeds for the 100 BTST shares are blocked; proceeds for the 50 settled shares are available immediately.

### A5 — Corporate Action Impact on Holdings

| CA Type | Impact |  
|---|---|  
| Bonus | Credited \~T+2 from record date under temp ISIN. P&L shows artificial drop until credited. Trading approval 4–5 days. Buy avg auto-adjusted (\~2 weeks). |  
| Split | New shares credited within 2 working days from ex-date. P&L temporarily distorted. |  
| Demerger | New entity shares credited post-record date. Timelines vary by company/RTA. Buy avg updated manually by Zerodha. |  
| Eligibility | Must hold on or before day before ex-date/record date (T+1 settlement). Pledged shares still eligible. |

### A6 — Shares Not Visible: Possible Reasons

| Reason | Explanation |  
|---|---|  
| Privacy Mode enabled | Client has Privacy Mode turned on — hides holdings, positions, P&L, and balances on screen. Data is intact; only display is hidden. To disable: tap user ID (top-right on Kite web, or profile icon on the app) → toggle Privacy Mode off. Links per **A9**. |  
| Shares already sold | Client may have sold shares — verify via tradebook before other checks. Share the FIFO buy/sell trail. |  
| Short delivery by seller | Investigate per **Rule 11**. Zerodha notifies via SMS/email. |  
| Pending settlement (T1) | Check `t1_t2_holdings` field. |  
| Corporate action in progress | Wait per **A5** timelines. P&L may show a temporary drop until new shares are credited — auto-corrects. |  
| ESOP with lock-in | Not shown on Kite. Still in demat account — verify via CDSL statement (SOT/SOH). |  
| Suspended/delisted | May not appear on Kite. Check Console for a complete view. |  
| Transfer from other broker pending | Check CDSL Easiest status. Once credited, shares appear; client must update buy average manually on Console (link per **A9**). |  
| IPO allotment not yet credited | Check CDSL SMS/email for credit confirmation. If allotment confirmed but shares not visible on Kite, wait until end of listing day. |

### A7 — Buy Average Issues

| Scenario | Cause & Resolution |  
|---|---|  
| avg_cost = N/A or 0 | Transferred shares (update manually on Console), CA pending adjustment, ESOP/off-market. Update path link per **A9**. |  
| Incorrect after CA | Auto-adjusted within \~2 weeks from record date. If longer → raise a ticket. |  
| Sell \+ rebuy same day = avg unchanged | Intraday = speculative, not delivery — shares don't physically move in/out of demat. Exception: T2T stocks (avg updates to latest buy). |

### A8 — P&L Calculations

- Day's P&L = (LTP − previous close) × quantity.  
- Net change = ((LTP − avg_cost) / avg_cost) × 100.  
- After 3:30 PM: Kite switches from LTP to official closing price (weighted avg of last 30 min). P&L shifts slightly — normal.  
- If LTP is N/A: Invested value excluded from total to avoid incorrect P&L. Client should update buy average on Console to fix total P&L calculation.  
- Smallcase vs Kite: Kite uses FIFO, Smallcase uses simple average — prices may differ. If client sold Smallcase stocks directly on Kite, Smallcase platform may not reflect this — contact help@smallcase.com for Smallcase-specific discrepancies.

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

### A10 — Escalation Triggers

Include when escalating to human agent: client ID, instrument_name, and specific issue.

## Section B: Decision Flow

### Routing

```  
Route by scenario  
   ├─ P&L questions (day's P&L, net P&L, total, post-3:30) → Rule 1  
   ├─ Buy average / portfolio valuation / invested amount issues → Rule 2  
   ├─ Shares sold — funds not credited / T1 / BTST → Rule 3  
   ├─ Pledge / collateral status → Rule 4  
   ├─ Holdings/positions/P&L hidden on screen (Privacy Mode) → Rule 5  
   ├─ Shares bought today not in holdings → Rule 5  
   ├─ Shares not visible → Rule 5  
   ├─ CDSL TPIN / DDPI — can't sell → Rule 6  
   ├─ Exchange / LTP mismatch → Rule 7  
   ├─ Sold stocks showing as negative positions → Rule 8  
   ├─ Console vs Kite value mismatch → Rule 9  
   ├─ Smallcase vs Kite mismatch → Rule 10  
   └─ Holding has mtf_quantity > 0 → redirect to MTF protocol for MTF-specific queries  
```

### Fallback

If no route matches, investigate using Section A reference data. If no root cause is found, escalate per **A10**.

## Section C: Rules

### Rule 1 — P&L Questions

1. Day's P&L vs Net P&L confusion → Day's P&L shows today's change from yesterday's closing price. Net change shows total change from buy average. Different calculations per **A8**.  
2. P&L changed after 3:30 PM → Kite switches from last traded price to the official closing price (weighted average of trades 3:00–3:30 PM). P&L shifts slightly — normal per **A8**.  
3. Total P&L seems wrong → check for `avg_cost` = 0 or N/A. Some holdings have no buy average recorded, so invested value is excluded from the total. Direct client to update buy average on Console per **A7**, **A8**, link in **A9**.  
4. If client asks about intraday or F&O position P&L → invoke `kite_positions`.

### Rule 2 — Buy Average Issues

1. If client reports incorrect portfolio value or invested amount: invoke `console_eq_pseudo_holdings` and `console_eq_holdings`. Compare breakdown quantities and buy averages with `kite_holdings`. Calculate expected invested value (sum of qty × avg_cost) and compare. If discrepancies found, proceed to step 2 for those holdings.  
2. `avg_cost` = N/A or 0 → investigate per **Rule 12** first. If `discrepant` > 0 and quantity mismatch confirmed, follow **Rule 12** through to resolution or escalation. If **Rule 12** does not apply, diagnose:  
   a. Transferred shares → buy average shows N/A; update manually on Console per **A7**, link in **A9**.  
   b. CA pending adjustment → buy average being adjusted; auto-updates within \~2 weeks per **A5**, **A7**.  
   c. ESOP/off-market → update manually on Console per **A7**.  
3. Incorrect after CA → adjusted within \~2 weeks; if longer, raise a ticket per **A5**, **A7**.  
4. Sell \+ rebuy same day, avg unchanged → intraday — shares don't physically move; buy average stays unchanged. Exception: T2T stocks (avg updates to latest buy) per **A7**.  
5. If client wants to verify original purchase → invoke `kite_order_history`.

### Rule 3 — Shares Sold — Funds Not Credited

1. T1 meaning → check `t1_t2_holdings`. T1 shares purchased yesterday, awaiting settlement; credited to demat by end of T+1 day per **A3**, **A4**.  
2. When client reports sale proceeds not available or funds not credited after selling shares, check for BTST first per **A4**:  
   a. Invoke `kite_order_history` for sell date and one previous trading day.  
   b. If stock was bought previous trading day and sold today, BTST trade.  
   c. Invoke `console_eq_holdings` for sell date — only `t1` quantity is BTST.  
   d. Calculate blocked value: `filled_quantity × average_price` from sell order.  
   e. Inform: shares sold were purchased previous trading day (T1/BTST). Sale proceeds blocked, available from next trading day after EPI completes. Settlement holiday in between → may take an additional day. Share BTST quantity and blocked value. Link per **A9** T1 holdings proceeds.  
3. If client asks why proceeds not reflected in balance → invoke `kite_margins`.

### Rule 4 — Pledge / Collateral Status

1. P symbol / `collateral_quantity` → client has pledged shares as collateral. P symbol shows pledged quantity. Remaining (total minus collateral) is available for trading per **A1**.  
2. Can pledged shares be sold? → yes, can be sold instantly without unpledge request. Selling pledged holdings reduces collateral margin.  
3. Collateral reduced after selling → cross-check `kite_margins` for current `equity_collateral` and `total_collateral`.  
4. For pledge/unpledge process or why pledge fails for a stock → redirect to pledge protocol.  
5. Can collateral margin be used for CNC purchases? → collateral margin from pledged shares can be used for equity intraday trading, futures, and options (buying and writing). For CNC purchases, available cash or cash-equivalent margin is required — collateral alone is not sufficient.

### Rule 5 — Shares Not Visible

1. **Check Privacy Mode:**  
   If client reports holdings/positions/P&L hidden → Privacy Mode may be enabled. Direct client: tap user ID (top-right on Kite web, or profile icon on app) → toggle Privacy Mode off. Data is intact — display only. Links per **A9** (Privacy Mode rows).

2. **Verify client still holds the shares:**  
   Invoke `console_eq_tradebook` for the instrument within the relevant date range. Compute net quantity using FIFO: sum all BUY quantities and subtract all SELL quantities chronologically. If net remaining ≤ 0 → client has sold all shares. Share buy/sell summary (dates, quantities, prices) so client can see the FIFO trail. If net remaining is positive but less than expected → inform client of actual remaining quantity, then investigate the missing portion.

3. Systematically check causes from **A6**:  
   a. Recently purchased → shares bought today appear under Positions per **A1**, **A3**. Invoke `kite_positions`.  
   b. CA in progress → new shares credited within timelines per **A5**. For split shares not credited after 4 working days → escalate to a human agent per **A10**. P&L may show temporary drop until credited per **A6**.  
   c. Short delivery → complete **Rule 11**. Respond based on buy-side or sell-side findings.  
   d. ESOP with lock-in → may not appear on Kite; still in demat — verify via CDSL statement (SOT/SOH) per **A6**.  
   e. Suspended/delisted → may not appear on Kite. Check Console for complete view per **A1**, **A6**.  
   f. Transfer from another broker → check CDSL Easiest status. Once credited, appears in holdings. Update buy average manually on Console per **A6**, link in **A9**.  
   g. IPO allotment → appears after listing. Check CDSL SMS/email for credit confirmation. If confirmed but not visible on Kite, wait until end of listing day per **A3**, **A6**.

4. If client confirms order was placed → invoke `kite_order_history` to verify execution.

### Rule 6 — CDSL TPIN / DDPI (Can't Sell)

1. Check `authorised_quantity` for the stock.  
2. TPIN not generated / authorisation failed → to sell, client must authorise via CDSL TPIN. Link per **A9**.  
3. DDPI not activated → client can avoid daily TPIN authorisation by activating DDPI. Link per **A9**.  
4. If sell order rejected (not authorisation issue) → invoke `kite_orders` for rejection reason.  
5. If GTT sell order didn't trigger → invoke `kite_gtt`.

### Rule 7 — Exchange / LTP Mismatch

1. Kite displays holdings from the exchange with the higher previous closing price — not necessarily where shares were bought. Demat shares are not mapped to a specific exchange; client can sell on either NSE or BSE. Advise checking prices on both exchanges per **A1**.

### Rule 8 — Sold Stocks as Negative Positions

1. When shares sold from holdings during the trading day, they appear as a negative position (tagged HOLDING) in Positions per **A1**. Normal — allows intraday traders to buy back. If no rebuy, ignore. Shares debited from demat by EOD.  
2. If client asks about sell order details → invoke `kite_orders`.

### Rule 9 — Console vs Kite Mismatch

1. Kite shows only actively traded, listed instruments. Console shows everything including suspended, delisted, unlisted, GSM 3+ stocks, and locked-in ESOP. Value difference is typically from these instruments per **A1**.

### Rule 10 — Smallcase vs Kite Mismatch

1. Kite uses FIFO; Smallcase uses simple average — average prices differ. If client sold Smallcase stocks directly on Kite, Smallcase platform may not reflect this — contact help@smallcase.com for Smallcase-specific discrepancies per **A8**.

### Rule 11 — Short Delivery Investigation

1. **Confirm short delivery occurred:**  
   Use `get_all_client_data` and check `communications` for a `campaign_name` containing "Short delivery" or "Upper Circuit". The date in the communication (format: DDMMYYYY, e.g., 20032026 = 20th March 2026) identifies when the short delivery occurred. The `content` field provides details.

2. **Determine buy-side or sell-side:**  
   Invoke `ledger_report` (last 2 weeks) and search for `remarks` "Short delivery margin blocked for sale of till exchange auction settlement".

   - If ledger entry NOT found → buy-side: client purchased shares but seller did not deliver. Use `content` from communications. Two outcomes: (1) Exchange procures shares via auction → credited to demat by T+2. (2) Shares cannot be procured → cash credited at close-out price. Client receives email confirming outcome.  
   - If ledger entry IS found → sell-side: client's sold shares are going through auction. Use `posting_date` and `debit` amount from ledger entry. Debit is 120% of closing price on sell trade date. Two outcomes: (1) Auction completed → blocked amount used for settlement; excess refunded. (2) No delivery → settled at close-out price. Client receives email with final outcome.

   Reference: per **A9** (Short delivery info).

### Rule 12 — Buy Average Discrepancy Investigation

1. **Check for discrepant shares:**  
   Invoke `console_eq_pseudo_holdings`. If `discrepant` = 0, this rule does not apply — fall through to **A7**.

2. **Verify trade history matches holdings:**  
   Invoke `console_eq_tradebook_prepared`. Count total traded quantity vs `quantity` from `kite_holdings`. If matches, fall through to **A7**.

3. **Check client-added external trade entries:**  
   If quantity does not match, invoke `console_eq_external_trades`. Check `discrepant` column.

   - No data found in external trades → escalate to support agent. Include client ID, instrument, holdings quantity, tradebook quantity.  
   - Client has added an entry → check date:  
     - Entry date >3 days from current → escalate to support agent. Include client ID, instrument, entry date, discrepant quantity.  
     - Entry date <3 days → buy average is being updated; typically reflects within 2 working days. If still N/A after 2 working days, raise a support ticket.
