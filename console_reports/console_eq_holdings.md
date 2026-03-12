# console_eq_holdings

## Description

WHEN TO USE:

- Client asks about equity holdings quantity, buy average, or invested value
- Client reports shares not visible, missing, or showing wrong quantity
- Client reports buy average is wrong, showing N/A, or showing 0
- Client reports discrepancy in holdings (transferred shares, IPO, off-market, gift, ESOP)
- Client asks about corporate action impact on holdings (bonus, split, merger, demerger, rights)
- Client asks why bonus/split/demerger shares not credited yet
- Client asks about pledged quantity showing in holdings
- Client asks about T1 holdings or settlement timing
- Client asks about dividend credit, tracking, or TDS on dividends
- Client asks about corporate action eligibility (ex-date, record date)
- Client asks about investment value mismatch in holdings

TRIGGER KEYWORDS: "holdings", "buy average", "average price", "discrepancy", "not visible", "missing shares", "bonus not credited", "split", "demerger", "merger", "pledged", "T1", "settlement", "dividend", "invested value", "buy value", "wrong price", "showing 0", "showing N/A", "transferred shares", "gift shares", "ESOP", "corporate action", "record date", "ex-date", "fractional shares"

## Protocol

# CONSOLE EQ HOLDINGS PROTOCOL

## Knowledge Base

<knowledge_base>

<facts>
- Buy average uses FIFO (First In First Out) — mandated by Income Tax Department
- Intraday trades (sell from holdings + buy back same day) do NOT affect buy average — treated as separate speculative transactions
- Exception: Trade-to-Trade (T2T) stocks — buy average updates to latest purchase price since all T2T trades are delivery
- Shares visible in holdings from T+1 day (bought Monday → visible Tuesday)
- T1 quantity = shares bought yesterday, not yet settled
- Holdings = available + t1 + margin + pending + discrepant + loan (total_quantity)
- buy_value = buy_average × total_quantity
- Corporate action adjustments take ~2 weeks from CA date for buy average update
- Bonus shares credited T+2 from record date, initially under temporary ISIN, tradeable after 4-5 days approval
- P&L shows artificial drop until bonus/split shares are credited — this is expected
- Stock split changes face value + qty proportionally — total investment value unchanged
- Consolidation (reverse split) reduces qty, increases price proportionally
- Fractional shares from CA settled in cash by company-appointed trustee → credited to primary bank
- Pledged stocks remain eligible for all corporate action benefits
- Must buy shares at least 1 trading day before ex-date/record date for CA eligibility (T+1 settlement)
- Selling on ex-date/record date still qualifies for CA benefits (shares debited T+1)
- Short delivery or settlement holiday can cause ineligibility even if bought before ex-date
- Shares transferred from another broker show as discrepancy — client must manually enter buy average on Console
- Only 1 discrepant entry per ISIN per date allowed; trade date entered cannot be a holiday/weekend
- Discrepant entries editable only while status is Pending; locked once buy average updated (within 24 hours)
- Cannot resolve discrepancies for: inactive/suspended/unlisted stocks, stocks with CA in last 10 days, IPOs in last 3 days
- Dividends credited to primary bank account, not trading account — 30-45 days after ex-date/record date
- Dividend queries → contact company's Registrar and Transfer Agent (RTA), not Zerodha
- TDS on dividends: 10% for residents (above ₹10,000/FY from FY25-26), 20% for NRIs, 20% if no PAN
- Can sell pledged holdings without unpledging (CNC order on Kite)
- Collateral margin temporarily reduces when selling free qty of a stock that also has pledged qty — restored next day
- Gift transfer in: closing price on transfer date used as entry price for P&L tracking (only for gifts — off-market transfers require client to manually add buy details via discrepancy flow)
- Gift transfer out: Zerodha uses the gift transfer date as exit date in sender's account; closing price on transfer date as exit price
- Off-market transfer out: no automatic exit entry posted — client must provide reversal details or manually edit Tax P&L
</facts>

<field_usage>
  <share>tradingsymbol | isin | buy_average | buy_value | available | t1 | margin | pending | discrepant | loan | total_quantity</share>
  <banned>name | instrument_id | holdings_date | closing_price | failure_date</banned>
</field_usage>

<timelines>
  <t1_settlement>T+1 day (bought Monday → holdings Tuesday)</t1_settlement>
  <bonus_credit>T+2 from record date; tradeable after 4-5 days (temp ISIN → perm ISIN)</bonus_credit>
  <ca_avg_adjustment>~2 weeks from corporate action date</ca_avg_adjustment>
  <demerger_credit>30-45 days from record date for new entity shares</demerger_credit>
  <discrepant_entry_update>Within 24 hours of adding entry</discrepant_entry_update>
  <dividend_credit>30-45 days after ex-date/record date</dividend_credit>
</timelines>

<quantity_fields>
  <available>Free qty for trading/selling</available>
  <t1>Yesterday's buy — settles end of today</t1>
  <margin>Pledged or blocked for collateral; still in client demat</margin>
  <pending>Qty expected from corporate action — not yet credited to demat</pending>
  <discrepant>Qty mismatch between tradebook and demat holdings file; common for transfers, IPOs, off-market, gifts</discrepant>
  <loan>Qty lent via SLB or pledged outside Zerodha (NBFC/LAS)</loan>
  <total_quantity>Sum of all above fields</total_quantity>
</quantity_fields>

<buy_average_rules>
  <method>FIFO — sell oldest shares first</method>
  <intraday_exception>Sell holdings + buy back same day → avg unchanged (speculative, not delivery)</intraday_exception>
  <t2t_exception>T2T stocks: avg = latest purchase price (all trades are delivery)</t2t_exception>
  <transfer_in>Shows discrepancy → client adds buy avg via Console → Portfolio → Holdings → View discrepancy → Add trade</transfer_in>
  <transfer_in_rules>Date ≤ demat credit date | 1 entry per ISIN per date | No holidays/weekends | Same date multiple buys = weighted avg, total qty</transfer_in_rules>
  <gift_transfer>Entry price = closing price on transfer date (gift only — off-market transfers require manual discrepancy entry)</gift_transfer>
  <null_reasons>Discrepant without entry | Transfer without manual update | CA in progress | ESOP/off-market without entry</null_reasons>
  <zero_reasons>Only bonus shares remain after FIFO sold all original bought shares (bonus cost = ₹0)</zero_reasons>
</buy_average_rules>

<corporate_actions>
  <bonus>
    <definition>Free shares to existing shareholders in a ratio (e.g., 2:1)</definition>
    <impact>Qty increases; price adjusts proportionally; total value unchanged; bonus shares at cost ₹0</impact>
    <credit>T+2 from record date; temp ISIN; tradeable after 4-5 days</credit>
    <pnl_drop>P&L shows artificial drop until credited — expected, auto-corrects</pnl_drop>
  </bonus>
  <split>
    <definition>Shares divided by reducing face value (e.g., 1:5 = 1 becomes 5)</definition>
    <impact>Qty multiplied, price divided by ratio; total value unchanged</impact>
    <sellable>Can sell original qty immediately; wait for additional credited shares</sellable>
    <buy_avg_update>Buy average update may take 2–3 working days after split shares are credited; client can sell in the meantime without P&L impact</buy_avg_update>
  </split>
  <consolidation>
    <definition>Reverse split — fewer shares at higher price</definition>
    <impact>Qty reduces, price increases; fractional shares settled in cash to primary bank</impact>
  </consolidation>
  <merger>
    <definition>Two companies combine; shares exchanged at defined swap ratio</definition>
    <impact>Old debited, new credited per ratio; fractional shares = cash to bank</impact>
  </merger>
  <demerger>
    <definition>Company splits into separate entities; new shares credited proportionally</definition>
    <impact>Original retained; new entity credited; avg split per COA ratio announced by company</impact>
    <credit>New entity shares within 30-45 days from record date</credit>
  </demerger>
  <rights>
    <definition>Existing shareholders buy additional shares at discounted price</definition>
    <re>REs credited as temp securities before issue; lapse if not used/sold; RE premium not in rights share avg</re>
  </rights>
  <eligibility>
    <rule>Hold in demat on ex-date/record date | Buy ≥1 day before ex-date | Selling on ex-date still qualifies | Pledged shares eligible</rule>
    <exceptions>Settlement holiday or short delivery can cause ineligibility</exceptions>
  </eligibility>
</corporate_actions>

<discrepancy_resolution>
  <causes>Transfer from other broker | IPO | Off-market | Gift | ESOP | CA system delay</causes>
  <path>Console → Portfolio → Holdings → View discrepancy → Select stock → Add trade → Enter date, price, qty</path>
  <cannot_resolve>Trading holidays | Inactive/suspended/unlisted stocks | CA within 10 days | IPO within 3 days</cannot_resolve>
</discrepancy_resolution>

<dividends>
  <credit>Primary bank account; 30-45 days after ex-date/record date</credit>
  <not_received>Contact company's RTA — Zerodha has no dividend credit details</not_received>
  <rta_lookup>NSE: nseindia.com → company → Corporate information → Transfer Agent | BSE: bseindia.com → company → Corp Information</rta_lookup>
  <failed_credit>RTA issues dividend warrant via courier to registered address</failed_credit>
  <tds>Resident: 10% above ₹10,000/FY (FY25-26) | NRI: 20% no threshold | No PAN: 20%</tds>
  <tracking>Kite: Portfolio → Stock → View dividends | Console: Reports → Downloads → Dividend statement</tracking>
</dividends>

<pledging_in_holdings>
  <margin_field>Pledged/blocked qty; still in client demat</margin_field>
  <sell_without_unpledge>Yes — CNC sell on Kite; collateral reduces proportionally</sell_without_unpledge>
  <temp_reduction>Selling free qty of stock with pledged qty → collateral reduces (pledged considered first) → restored next day</temp_reduction>
</pledging_in_holdings>

<links>
  <update_buy_avg>Console → Portfolio → Holdings → View discrepancy → Add trade</update_buy_avg>
  <approved_securities>zerodha.com/approved-securities</approved_securities>
  <holdings_console>console.zerodha.com/portfolio/holdings</holdings_console>
</links>

</knowledge_base>

---

## Business Rules

### Rule 0: Failure Date Check
**if:** `failure_date` field has any value (not blank)
**then:** Escalate to support manager immediately with client ID, tradingsymbol, and failure_date. Do not attempt to resolve.

### Rule 0.5: Cross-Reference Qty Validation
**if:** Client reports qty mismatch or holdings not visible
**then:** Compare `available` qty in `console_eq_holdings` with `available` qty in `console_eq_pseudo_holdings` (SOT-based qty, independent of tradebook) for the same ISIN.
- If both match → qty is correct; issue is display-only. Ask the client to share a screenshot of their holdings page so we can check further.
- If mismatch → escalate with both values, client ID, and tradingsymbol.

### Rule 1: Field Protection
**NEVER expose:** `name`, `instrument_id`, `holdings_date`, `closing_price`, `failure_date`
**ALWAYS share when relevant:** `tradingsymbol`, `isin`, `buy_average`, `buy_value`, `available`, `t1`, `margin`, `pending`, `discrepant`, `loan`, `total_quantity`
**NEVER use the word "pending"** when communicating with clients — use "being processed for credit" or "yet to be credited" instead.

### Rule 2: Buy Average — FIFO Explanation
**if:** Client questions why buy average differs from expected price
**then:** "Your buy average is calculated using the FIFO (First In, First Out) method, which is mandated by the Income Tax Department. When you sell shares, the oldest purchased shares are considered sold first, which changes the average of remaining shares. You can check the detailed calculation under View breakdown on Kite or Console."

**Note:** If client sold and bought back same day — "Intraday transactions don't affect your buy average since those are treated as separate speculative trades. Your delivery holdings average remains unchanged."

### Rule 3: Buy Average Showing N/A
**if:** `buy_average` is null/N/A AND `discrepant` > 0
**then:** First check `console_eq_external_trades` (off-platform entries: discrepant, gift, ESOP, IPO, transfer) for an existing entry for this ISIN.

- If entry exists AND still processing → "Your purchase details have been recorded and are being processed. Your buy average will update within 24 hours."
- If entry exists AND processed but avg still N/A → escalate with client ID, tradingsymbol, and entry details from `console_eq_external_trades`.
- If no entry exists → "Your [tradingsymbol] shares are showing as a discrepancy because the purchase details are not available in our system. This typically happens when shares are transferred from another broker, received via off-market transfer, ESOP, or IPO. To update your buy average, go to Console → Portfolio → Holdings → View discrepancy → select [tradingsymbol] → Add trade → enter the original purchase date, price, and quantity."

**if:** `buy_average` is null AND `discrepant` = 0 AND `pending` > 0
**then:** "Your [tradingsymbol] buy average is being adjusted due to a recent corporate action. This update typically takes about 2 weeks from the corporate action date. Refer `<ca_avg_adjustment>`."

### Rule 3.5: Buy Average Showing ₹0
**if:** `buy_average` = 0 AND `total_quantity` > 0
**then:** Check `console_eq_holdings_breakdown` (transaction-level view of all entries) for the same stock/ISIN — look for entries where the `exchange` field = "BONUS". If confirmed:

"Your [tradingsymbol] buy average is showing ₹0 because all your originally purchased shares have been sold (as per FIFO), and only bonus shares remain. Bonus shares are credited at zero cost, so the average of remaining holdings becomes ₹0. This is correct as per FIFO accounting."

If no BONUS entry found in breakdown → investigate further (may be a system issue or other CA type). Escalate if unexplained.

### Rule 4: Buy Average Wrong After Corporate Action
**if:** Client says buy average is incorrect AND stock had recent bonus/split/merger/demerger
**then:**
- Check if CA was within last 2 weeks → "The buy average for [tradingsymbol] is being adjusted following the recent [corporate action type]. This adjustment typically takes about 2 weeks. Refer `<ca_avg_adjustment>`."
- If CA was 3+ weeks ago and avg still appears wrong → escalate with client ID, tradingsymbol, and expected vs actual buy average.

### Rule 5: Discrepancy — Transferred/Gift/ESOP Shares
**if:** `discrepant` > 0 AND client confirms shares were received via Zerodha gift transfer
**then:** Check `console_eq_external_trades` for external_trade_type = gift.
- If entry found → "Your gift shares of [tradingsymbol] have been recorded in our system at ₹[price] per share (closing price on transfer date). No further action is needed from your side. Your buy average will reflect this once processed."
- If no entry found → escalate. The system should have auto-posted this entry — it has not been recorded.

**if:** `discrepant` > 0 AND client confirms shares were transferred from another broker / ESOP / off-market
**then:** First check `console_eq_external_trades` for an existing entry for this ISIN.
- If entry exists AND still processing → "Your purchase details have been recorded and are being processed. Your buy average will update within 24 hours."
- If entry exists AND processed but discrepancy not resolved → escalate with client ID, tradingsymbol, and entry details.
- If no entry exists → "Your [discrepant] shares of [tradingsymbol] are showing as a discrepancy because the purchase details aren't in our system. You can add the details on Console → Portfolio → Holdings → View discrepancy → select [tradingsymbol] → Add trade.

Please note:
- Enter the original purchase date (must be on or before the date shares were credited to your Zerodha demat)
- Only one entry per date is allowed; if you bought on multiple dates, add separate entries for each
- If you bought multiple times on the same date, enter the total quantity with the weighted average price
- Entries cannot be made on holidays or weekends
- Once the buy average is updated (within 24 hours), the entry cannot be modified"

**if:** Client says they don't have purchase details → "You can obtain the purchase details from your previous broker. Only the units are transferred — the purchase history is not carried over automatically."

### Rule 6: Discrepancy — Cannot Resolve (Error)
**if:** Client reports error when trying to add discrepant entry
**then:** First check `console_eq_external_trades` — the entry may have been posted successfully despite the error.
- If entry found → "Your purchase details have already been recorded successfully. Your buy average will update within 24 hours."
- If no entry found → check `<discrepancy_resolution><cannot_resolve>` and respond:
  - "Today is a trading holiday — you can add the entry on the next trading day."
  - "This stock is currently inactive/suspended/unlisted. Once it becomes active on the exchange, you'll be able to resolve the discrepancy."
  - "[tradingsymbol] had a corporate action within the last 10 days. The system will auto-adjust during this period. Please try again after 10 days from the corporate action date."
  - "[tradingsymbol] was listed via IPO within the last 3 days. The system needs up to 3 days to process. Please try again after that."

### Rule 7: Bonus Shares Not Credited / Not Visible
**if:** Client says bonus shares not in holdings after record date
**then:** Check `console_eq_external_trades` for a system-posted CA credit entry (external_trade_type = devolved or CA-related entry) for this ISIN.

- If CA credit entry found but not yet reflecting in holdings → "Your bonus shares of [tradingsymbol] have been processed and the credit entry is in our system. The holdings will update shortly — this can take up to 1 trading day to reflect."
- If no CA credit entry found AND shares are yet to be credited in Console → "Your [pending] bonus shares of [tradingsymbol] are being processed for credit. Bonus shares are typically credited within T+2 days from the record date. They initially appear under a temporary ISIN and become tradeable after 4–5 days once the exchange grants trading approval. CDSL will send you an SMS when the shares are credited."

"The temporary drop in your P&L is expected — it will auto-correct once the bonus shares are credited to your demat account."

**if:** More than 5 trading days since record date AND shares still not credited → escalate.

### Rule 8: Stock Split — Qty/Price Query
**if:** Client asks about stock split impact on holdings OR reports split shares not reflecting in Kite
**then:** Use `total_quantity`, `available`, and `pending` from `console_eq_holdings` as the basis for explaining the split — do NOT derive quantity from recent trade history. Then check `kite_holdings` to verify whether split shares have already been credited.

- **If `kite_holdings` shows the full post-split quantity** → "Your split shares have been successfully credited to your account. You currently have [available] shares of [tradingsymbol] available for trading, totalling [total_quantity] shares after the split. Please note that the buy average may take 2–3 working days to update, but you can sell your shares in the meantime — this will not impact your P&L."

- **If `kite_holdings` does not show the full post-split quantity** AND Console shows shares still being processed for credit → "You currently have [available] shares of [tradingsymbol], with [pending] shares being processed for credit, totalling [total_quantity] shares after the split. These are typically credited within T+2 days from the record date and will become tradeable after 4–5 days once the exchange grants trading approval. CDSL will notify you via SMS once the shares are credited to your demat account."

**if:** More than 5 trading days since record date AND split shares still not credited → escalate.

### Rule 9: Demerger — New Shares / Avg Update
**if:** Client asks about demerger shares not credited or avg not updated
**then:**
- Shares not credited: "After a demerger, the new entity's shares are typically credited within 30-45 days from the record date. Refer `<demerger_credit>`. CDSL will notify you via SMS/email once credited."
- Avg not updated: "The buy average for both [original company] and [new entity] will be split based on the Cost of Acquisition (COA) ratio announced by the company. Once the company announces the ratio, we will update the buy average accordingly. Refer `<ca_avg_adjustment>`."
- If COA announced but avg still not updated after 3 weeks → escalate.

### Rule 10: Merger — Share Swap
**if:** Client asks about merger impact on holdings
**then:** "After the merger, your [old company] shares have been exchanged for [new company] shares at the [ratio] swap ratio. If the swap ratio results in fractional shares, the cash equivalent will be credited to your primary bank account by the company-appointed trustee."

### Rule 11: Holdings Not Visible / Qty Mismatch
**if:** Client says shares not visible or wrong qty on Kite/Console
**then:** Apply Rule 0.5 first (cross-reference `console_eq_pseudo_holdings`).

Additionally check:
- `t1` > 0 → "Your [t1] shares of [tradingsymbol] were purchased yesterday and are in T+1 settlement. They will appear in your available holdings by end of today."
- Shares yet to be credited from corporate action → "You have [pending] shares yet to be credited from a corporate action. These will be credited once processed. Refer `<bonus_credit>`."
- `margin` > 0 → "[margin] shares are pledged as collateral. They are in your demat account but blocked for margin. They appear under the margin/pledged section."
- `loan` > 0 → "[loan] shares are under stock lending or pledged outside Zerodha."
- If all fields are 0 and stock not found → "This stock does not appear in your holdings. Please confirm the tradingsymbol or ISIN, and whether the purchase has settled (shares appear from T+1 day onwards)."

### Rule 12: Investment Value Mismatch
**if:** Client says invested value is wrong
**then:** "Your invested value is calculated as buy average × total quantity. Current values: buy average = ₹[buy_average], total quantity = [total_quantity], invested value = ₹[buy_value]."

Common causes of mismatch:
- "If a recent corporate action (bonus/split/demerger/merger) occurred, the buy average adjustment may be in progress. Refer `<ca_avg_adjustment>`."
- "If you have discrepant holdings ([discrepant] shares), the invested value won't be accurate until you add the purchase details."
- "Please ensure you're comparing equity holdings only — Console dashboard may include mutual fund values separately."

### Rule 13: Pledged Qty in Holdings
**if:** Client asks about margin/pledged quantity in holdings
**then:** "Your [margin] shares of [tradingsymbol] are pledged as collateral for trading margin. These shares remain in your demat account — they are not moved elsewhere."

**if:** Client asks about selling pledged shares → "You can sell pledged shares directly using a CNC sell order on Kite without placing an unpledge request. Your collateral margin will reduce by the value of shares sold."

**if:** Client reports collateral reduced after selling → "When you sell free (unpledged) shares of a stock that also has pledged quantities, the collateral temporarily reduces because the system considers pledged shares first. This is restored automatically the next trading day after the end-of-day process — no action needed from your side."

### Rule 14: Dividend Queries
**if:** Client asks about dividend not received
**then:** "Dividends are credited directly to your primary bank account (not your Zerodha trading account) within 30-45 days after the ex-date/record date. Refer `<dividend_credit>`.

If you haven't received your dividend within this period, please contact the company's Registrar and Transfer Agent (RTA). Zerodha does not process dividend payments and does not receive details about dividend credits. You can find the RTA details on NSE (nseindia.com → search company → Corporate information → Transfer Agent Details) or BSE (bseindia.com → search company → Corp Information)."

**if:** Client says dividend amount is less than expected → "Companies deduct TDS before crediting dividends. For resident individuals, TDS of 10% applies on total dividend income exceeding ₹10,000 in a financial year. For NRIs, TDS is 20% with no threshold. If PAN is not linked, TDS is 20%. You can verify TDS in Form 26AS on the income tax portal and claim credit when filing ITR."

**if:** Client asks to track dividends → "You can track dividends on Kite (Portfolio → select stock → View dividends) or download the dividend statement from Console (Reports → Downloads → Dividend statement)."

### Rule 15: Corporate Action Eligibility
**if:** Client asks whether they're eligible for a corporate action
**then:** "To be eligible for corporate action benefits, you must hold the shares in your demat account on the ex-date/record date. Since shares settle on T+1, you need to buy at least one trading day before the ex-date."

**if:** Client sold on ex-date → "You are still eligible. When you sell on the ex-date, the shares are debited from your demat on T+1 day. Since you held them on the ex-date, you qualify."

**if:** Client has pledged shares → "Pledged shares are eligible for all corporate action benefits. However, for buyback tendering, you must unpledge the shares first."

**if:** Client bought before ex-date but didn't receive CA benefit → "In rare cases, a settlement holiday falling on the ex-date or a short delivery by the seller can delay or prevent share credit to your demat by the record date. This would affect eligibility despite a timely purchase."

### Rule 16: T1 / Settlement Queries
**if:** `t1` > 0 AND client asks about recently purchased shares
**then:** "Your [t1] shares of [tradingsymbol] were purchased yesterday and are currently in T+1 settlement. They will move to your available balance by end of today and be visible in your regular holdings from the next trading day."

### Rule 17: Gift / Off-Market Transfer
**if:** Client received shares via **gift** AND asks about buy average or P&L
**then:** "For shares received via gift, the system uses the closing price on the transfer date as the entry price for P&L tracking purposes. If you need to update this with the actual acquisition cost, you can add the details via the discrepancy resolution flow on Console. Refer `<discrepancy_resolution>`.

Please note: While filing income tax returns, you may need to manually adjust the Tax P&L report to reflect the correct cost of acquisition as per your preferred tax treatment. Consult a Chartered Accountant for guidance."

**if:** Client received shares via **off-market transfer** AND asks about buy average or P&L
**then:** "For shares received via off-market transfer, the system does not automatically assign a buy price. You will need to manually add the purchase details via the discrepancy resolution flow on Console. Refer `<discrepancy_resolution>`."

**if:** Client **gifted shares OUT** → "For gifted shares, Zerodha uses the gift transfer date as the exit date and the closing price on that date as the exit price in your account. This will reflect in your P&L accordingly."

**if:** Client transferred shares **OUT via off-market** → "When shares are transferred out via off-market, no automatic exit entry is posted in our system since the transaction happens outside the platform. You can either share the transfer details so we can post a reversal entry, or manually update your Tax P&L report while filing returns."

### Rule 18: Escalation Criteria
**if:** Any of the following:
- `failure_date` has a value (Rule 0)
- Qty mismatch between `console_eq_holdings` and `console_eq_pseudo_holdings` after cross-check (Rule 0.5)
- Bonus/split shares not credited 5+ trading days after record date (Rules 7, 8)
- Buy average not updated 3+ weeks after corporate action (Rule 4)
- Console and Kite show different qty/avg (Rule 11)
- Client requests full reconciliation of holdings/funds
**then:** Escalate with: client ID, tradingsymbol(s), specific discrepancy details, and screenshots if available.

### Rule 19: Protect Internal Fields
**NEVER share with client:** `name` (internal ID), `instrument_id` (system mapping), `holdings_date` (internal modification date), `closing_price` (mostly null, internal), `failure_date` (escalation trigger only).
**NEVER say:** "failure date", "holdings date", "instrument ID", "pending" (use "being processed for credit"), or reference any internal system names.
