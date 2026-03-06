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

# KITE_HOLDINGS PROTOCOL

## Knowledge Base

<knowledge_base>
<facts>
- Holdings = settled shares in demat. Positions = open trades (intraday/derivatives/same-day delivery)
- Shares bought today appear under Positions → move to Holdings on T+1 after settlement
- T1 tag = shares awaiting settlement (bought on T day, settling by T+1 end of day)
- India uses T+1 rolling settlement for equity
- Kite shows only actively traded/listed instruments — suspended, delisted, unlisted, GSM 3+, locked-in ESOP may not appear. Console shows all
- Holdings LTP and exchange shown from whichever exchange has higher previous closing price — not where shares were bought. Demat shares not mapped to a specific exchange
- P&L during market hours uses LTP; after 3:30 PM switches to exchange closing price (weighted avg of last 30 min)
- Day's P&L = (LTP - previous close) × quantity. Net change = ((LTP - avg_cost) / avg_cost) × 100
- Buy avg on Kite fetched from Console using FIFO method. If not on Console → N/A on Kite
- Selling and rebuying same stock same day = intraday trade, does NOT change buy avg. Exception: T2T stocks
- If LTP is N/A, invested value excluded from total to avoid incorrect P&L
- Sold stocks appear as negative positions during trading day (tagged HOLDING) — normal. Debited from demat by end of day if not bought back
- Smallcase vs Kite avg price mismatch: Kite uses FIFO, Smallcase uses simple average
</facts>

<field_usage>
  <share>instrument_name | quantity | avg_cost | t1_t2_holdings | mtf_quantity | mtf_average_price | mtf_value | mtf_initial_margin | pnl | net_change_percentage | daily_percentage_change | last_close_price | days_pnl | authorised_quantity | collateral_quantity | invested_value | total_current_value</share>
  <internal>ltp</internal>
  <banned>None</banned>
</field_usage>

<settlement_schedule>
  <equity>T+1 — bought Monday, in demat by Tuesday evening</equity>
  <fo_physical>ITM options/futures expiry: T+1 delivery. Short delivery: up to T+2</fo_physical>
  <bonus>~T+2 from record date; initially under temp ISIN, trading approved in 4-5 days</bonus>
  <split>Up to 2 working days from ex-date; if not credited after 4 days → escalate</split>
  <ipo>Visible after listing; may take a day to reflect on Kite</ipo>
</settlement_schedule>

<t1_btst_rules>
- T1 shares can be sold (BTST) but credit from selling T1 is unavailable same day
- BTST sale proceeds available from next trading day (after EPI process)
- Settlement holiday: BTST credit may take T+2
- BTST carries short delivery risk if original seller defaults
- DP charges apply for BTST trades
</t1_btst_rules>

<corporate_actions>
  <bonus>Credited ~T+2 from record date under temp ISIN. P&L shows artificial drop until credited. Trading approval 4-5 days. Buy avg auto-adjusted (~2 weeks)</bonus>
  <split>New shares credited within 2 working days from ex-date. P&L temporarily distorted. If not credited after 4 days → escalate</split>
  <demerger>New entity shares credited post-record date. Timelines vary by company/RTA. Buy avg updated manually by Zerodha</demerger>
  <eligibility>Must hold on or before day before ex-date/record date (T+1 settlement). Pledged shares still eligible</eligibility>
</corporate_actions>

<shares_not_visible_reasons>
- Short delivery by seller → may arrive T+2 or cash settled. Zerodha notifies via SMS/email
- Pending settlement (T1) → check t1_t2_holdings field
- Corporate action in progress (bonus/split/demerger) → wait per timelines
- ESOP with lock-in → not shown on Kite, verify on CDSL statement
- Suspended/delisted → may not appear on Kite. Check Console
- Transfer from other broker pending → check CDSL Easiest status
- IPO allotment not yet credited → check CDSL SMS/email
</shares_not_visible_reasons>

<buy_avg_issues>
- N/A: transferred shares (update manually on Console), corporate action pending, ESOP/off-market
- Incorrect after corporate action: auto-adjusted within ~2 weeks from record date
- Sell + rebuy same day: avg unchanged (intraday = speculative). Exception: T2T stocks
- Update path: refer `<links><update_buy_avg>`
</buy_avg_issues>

<links>
  <update_buy_avg>https://support.zerodha.com/category/console/portfolio/console-holdings/articles/how-to-update-buy-average</update_buy_avg>
  <generate_tpin>https://support.zerodha.com/category/trading-and-markets/trading-faqs/general/articles/generate-cdsl-tpin</generate_tpin>
  <activate_ddpi>https://support.zerodha.com/category/your-zerodha-account/your-profile/ddpi/articles/activate-ddpi</activate_ddpi>
  <pledge_list>https://zerodha.com/margin/pledge</pledge_list>
</links>
</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
**NEVER expose:** `ltp` (use customer-facing descriptions like "current market price" if needed)
**Always share when relevant:** All other fields per `<field_usage><share>`

### Rule 1: First Check — Locate Holding
**if:** Customer asks about a specific stock
**then:**
1. Search kite_holdings by `instrument_name`
2. If found: check `quantity`, `t1_t2_holdings`, `avg_cost`, `collateral_quantity`, `pnl`, `days_pnl`
3. If found AND `mtf_quantity` > 0: holding is under Margin Trading Facility → redirect to **mtf_protocol** for MTF-specific queries (charges, interest, conversion)
4. If NOT found: check if shares were bought today → invoke **kite_positions** (today's purchases appear as positions, not holdings). If not in positions either, proceed to Rule 6 (shares not visible)

### Rule 2: P&L Questions
**if:** Customer asks about P&L discrepancy or confusion
**then:**

**2.1 Day's P&L vs Net P&L:** "Day's P&L shows today's change from yesterday's closing price (₹[days_pnl]). Net change shows the total change from your buy average (₹[pnl], [net_change_percentage]%). These are different calculations."

**2.2 P&L changed after 3:30 PM:** "After 3:30 PM, Kite switches from the last traded price to the official closing price (weighted average of trades between 3:00–3:30 PM). This causes P&L to shift slightly — it's normal."

**2.3 Total P&L seems wrong:** Check if any holdings have `avg_cost` = 0 or N/A → those holdings' invested_value is excluded from totals. "Some holdings have no buy average recorded, so their invested value is excluded from the total calculation. Update the buy average on Console to fix this: [How to update the buy average on Console?](https://support.zerodha.com/category/console/portfolio/console-holdings/articles/how-to-update-buy-average)"

If customer asks about intraday or F&O position P&L → invoke **kite_positions**.

### Rule 3: Buy Average Issues
**if:** Customer reports buy average N/A, incorrect, or unexpected
**then:**

**3.1 avg_cost = N/A or 0:** "Buy average shows N/A because [check reason]:
- Shares transferred from another broker → [update manually on Console](https://support.zerodha.com/category/console/portfolio/console-holdings/articles/how-to-update-buy-average)
- Corporate action (bonus/split/demerger) pending adjustment → auto-updates within ~2 weeks from record date
- Received via ESOP or off-market transfer → [update manually on Console](https://support.zerodha.com/category/console/portfolio/console-holdings/articles/how-to-update-buy-average)"

**3.2 avg_cost incorrect after corporate action:** "After corporate actions like bonus, split, or demerger, buy average may temporarily be incorrect. Zerodha adjusts this within approximately 2 weeks from the record date. If it's been longer, please raise a ticket."

**3.3 Sell + rebuy same day, avg unchanged:** "When you sell shares from holdings and buy them back the same day, the buy average stays unchanged. This is treated as an intraday trade — shares don't physically move in/out of your demat. [Exception: T2T stocks — buy average updates to latest buy price.]"

If customer wants to verify original purchase price or order details → invoke **kite_order_history**.

### Rule 4: T1 / Settlement / BTST
**if:** Customer asks about T1 tag, settlement, or BTST proceeds
**then:**

**4.1 T1 meaning:** Check `t1_t2_holdings`. "You have [t1_t2_holdings] shares of [instrument_name] marked as T1, meaning they were purchased and are awaiting settlement. They'll be credited to your demat account by end of T+1 day ([next trading day])."

**4.2 BTST proceeds not available:** "When you sell T1 shares (BTST), the sale proceeds are unavailable on the same day. The credit becomes available from the next trading day after the Early Pay-In process completes. [If settlement holiday: may take T+2.]"
If customer asks why proceeds aren't reflected in their balance → invoke **kite_margins** to check `available_cash` and `payin`.

### Rule 5: Pledge / Collateral Status
**if:** Customer asks about pledge status, P symbol, or collateral
**then:**

**5.1 P symbol / collateral_quantity:** "You have [collateral_quantity] shares of [instrument_name] pledged as collateral. The P symbol shows this pledged quantity. Your remaining [quantity] shares are available for trading."

**5.2 Can I sell pledged shares?** "Yes, pledged shares can be sold instantly without placing an unpledge request. However, selling pledged holdings will reduce your collateral margin."

**5.3 Collateral reduced after selling:** "When you sell holdings that were pledged, the collateral margin reduces accordingly." Cross-check **kite_margins** for current `equity_collateral` and `total_collateral`.

If customer asks how to pledge, unpledge, or why they can't pledge a specific stock → redirect to **pledge_protocol**.

### Rule 6: Shares Not Visible
**if:** Customer says shares missing from holdings AND stock not found in kite_holdings
**then:** Systematically check causes from `<shares_not_visible_reasons>`:

**6.1 Recently purchased:** "Shares bought today appear under Positions, not Holdings. They'll move to Holdings on T+1 day after settlement." Invoke **kite_positions** to confirm. If customer asks about the buy order status → invoke **kite_orders**.

**6.2 Corporate action (bonus/split/demerger):** Check if customer mentions recent corporate action. "After a [bonus/split/demerger], new shares are credited within [refer `<corporate_actions>` timelines]. P&L may show a temporary drop until credited. If it's been longer than the expected timeline, please raise a ticket."

**6.3 Short delivery:** "If shares were purchased but not delivered by the seller, this is a short delivery. Zerodha notifies via SMS/email. Shares may arrive on T+2, or the exchange will settle in cash. Check your registered email for notifications."

**6.4 ESOP with lock-in:** "ESOP shares with lock-in periods may not appear on Kite. They're still in your demat account — verify via your CDSL statement (SOT/SOH)."

**6.5 Suspended/delisted:** "Suspended or delisted stocks may not display on Kite. Check Console for a complete view of all holdings including non-tradeable instruments."

**6.6 Transfer from another broker:** "If you transferred shares from another broker, check the transfer status on CDSL Easiest. Once credited to your Zerodha demat, they'll appear in holdings. You'll also need to [update the buy average manually on Console](https://support.zerodha.com/category/console/portfolio/console-holdings/articles/how-to-update-buy-average)."

**6.7 IPO allotment:** "IPO shares appear after listing. Check CDSL SMS/email for credit confirmation. If allotment is confirmed but shares aren't visible on Kite, wait until end of listing day."

If customer confirms order was placed but shares not showing → invoke **kite_order_history** to verify execution status.

### Rule 7: CDSL TPIN / DDPI — Can't Sell
**if:** Customer cannot sell shares due to authorisation issue
**then:** Check `authorised_quantity` for the stock.

**7.1 TPIN not generated / authorisation failed:** "To sell shares, you need to authorise them via CDSL TPIN. Here's how to generate your TPIN: [generate_tpin](https://support.zerodha.com/category/trading-and-markets/trading-faqs/general/articles/generate-cdsl-tpin)"

**7.2 DDPI not activated:** "You can avoid daily TPIN authorisation by activating DDPI (Demat Debit and Pledge Instruction). Learn more: [activate_ddpi](https://support.zerodha.com/category/your-zerodha-account/your-profile/ddpi/articles/activate-ddpi)"

If customer's sell order was rejected (not an authorisation issue) → invoke **kite_orders** to check rejection reason. If customer has a GTT sell order that didn't trigger → invoke **kite_gtt**.

### Rule 8: Exchange / LTP Mismatch
**if:** Customer reports holdings LTP different from marketwatch, or wrong exchange shown
**then:** "Kite displays holdings from the exchange with the higher previous closing price — not necessarily where you bought the shares. Your demat shares are not mapped to a specific exchange, so you can sell on either NSE or BSE. Check prices on both exchanges before selling to get the best price."

### Rule 9: Sold Stocks as Negative Positions
**if:** Customer sees sold stocks as negative positions or negative quantity
**then:** "When you sell stocks from holdings during the trading day, they appear as a negative position (tagged HOLDING) in the Positions tab. This is normal — it allows intraday traders to buy them back. If you don't intend to rebuy, ignore the negative position. The shares will be debited from your demat by end of day."
If customer asks about the sell order details → invoke **kite_orders**.

### Rule 10: Console vs Kite Mismatch
**if:** Customer reports different values on Console vs Kite
**then:** "Kite shows only actively traded, listed instruments. Console shows everything including suspended, delisted, unlisted shares, GSM 3+ stocks, and locked-in ESOP shares. The value difference is typically from these instruments that Kite cannot price accurately."

### Rule 11: Smallcase vs Kite Mismatch
**if:** Customer reports Smallcase holdings not matching Kite
**then:** "Kite and Smallcase may show different average prices because Kite uses the FIFO method while Smallcase uses simple average. Also, if you sold Smallcase stocks directly on Kite, the Smallcase platform may not reflect this — contact help@smallcase.com for Smallcase-specific discrepancies."
