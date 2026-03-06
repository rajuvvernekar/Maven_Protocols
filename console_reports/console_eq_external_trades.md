# console_eq_external_trades

## Description

WHEN TO USE:

- Agent needs to check if external trade entries (discrepant, buyback, IPO, gift, ESOP, internal transfer, off-market) exist for a stock
- Client has discrepancy in holdings and agent needs to verify if a manual entry was posted
- Client says they added discrepancy details but buy average still not updated
- Client reports wrong price/qty entered in discrepancy fix and wants correction
- Agent needs to verify buyback, IPO allotment, or gift entries in the system
- Client reports P&L discrepancy and agent suspects missing external trade entries
- Agent needs to check if a reversal or exit entry was posted for transferred-out shares
- Client's holdings show discrepant qty and agent needs to trace the source (transfer, gift, ESOP, IPO, CA credit)

TRIGGER KEYWORDS: "external trade", "discrepancy entry", "discrepant entry", "add trade", "fix discrepancy", "buyback entry", "IPO entry", "gift entry", "ESOP entry", "internal transfer entry", "off-market entry", "wrong discrepancy price", "wrong entry", "pending recalc", "external trade type"

## Protocol

# CONSOLE EQ EXTERNAL TRADES PROTOCOL

## PROTOCOL

<knowledge_base>

<facts>
- External trades are entries recorded outside normal exchange trading — manual or system-generated
- These entries directly affect buy average and P&L via FIFO
- Missing external trade entries are a primary cause of holdings and P&L discrepancies
- Client adds discrepant entries via Console → Portfolio → Holdings → View discrepancy → Add trade
- Once added and processed (pending_recalc = false), entries are locked — cannot be edited by client
- Wrong entries can only be corrected by Console team (backend fix)
- Input parameter: Client ID + External Trade Type filter (discrepant, buyback, internal transfer, IPO, etc.)
- Gift shares: system uses closing price on transfer date as entry price; client may want actual acquisition cost instead
- ESOP shares: client should enter exercise price as buy price; if not listed on exchange, cannot add entry until listed
- Buyback entries: posted when tendered shares are accepted; includes exit entry at buyback price
- Internal transfer: shares moved between client's own primary and secondary demat accounts at Zerodha
- pending_recalc = true → entry posted but holdings/P&L not yet recalculated (wait up to 24 hours)
</facts>

<field_usage>
  <share>trade_date | tradingsymbol | isin | quantity | price | trade_type | external_trade_type | exchange | series | order_execution_time</share>
  <banned>pk | instrument_id | client_id | settlement_type | creation | pending_recalc (internal processing flag — do not expose, but use to diagnose)</banned>
</field_usage>

<external_trade_types>
  <discrepant>Client-added entry for transferred/gifted/ESOP/off-market shares with no matching tradebook record</discrepant>
  <buyback>System-posted SELL entry for accepted buyback quantities — trade_type always SELL, order_id = BUYBACK</buyback>
  <devolved>System-posted BUY entry for shares received under physical delivery settlement — exchange = PHY, series = AF</devolved>
  <ipo>Entry for IPO allotment shares credited to demat — tradingsymbol may be temporary until listing, exchange may be UNKNOWN</ipo>
  <internal_transfer>Entry for shares moved between client's own demat accounts (primary ↔ secondary)</internal_transfer>
  <gift>Entry for shares received or sent as gift; entry price = closing price on transfer date by default</gift>
  <esop>Entry for ESOP exercised shares; client enters exercise price</esop>
  <ofs>Entry for trades related to Offer for Sale (OFS) transactions</ofs>
  <reversal>System-posted reversal trade against short deliveries</reversal>
  <rightsissue>Entry for shares allotted under a rights issue</rightsissue>
  <takeover>Entry for shares tendered or received under an open offer/takeover</takeover>
  <transferout>System-posted gift-out and transfer-out entries when client provides transfer details via ticket or call</transferout>
</external_trade_types>

<cross_reference>
  <console_eq_holdings>Check discrepant field — if > 0, external entry may be missing or pending. Discrepancy resolution steps are in this tool's protocol (Rule 5).</console_eq_holdings>
  <console_eq_tradebook>Regular exchange-executed trades. If trade not found here, check external trades.</console_eq_tradebook>
  <console_eq_holdings_breakdown>Transaction-level view showing both tradebook and external entries combined. Use to verify if external entry is reflected in breakdown.</console_eq_holdings_breakdown>
  <console_eq_pnl>P&L computed from all trades (tradebook + external). Missing external entries cause wrong P&L.</console_eq_pnl>
</cross_reference>

<escalation_triggers>
  <wrong_entry>Client entered wrong price/qty/date in discrepancy — locked after processing, needs backend fix</wrong_entry>
  <entry_not_reflecting>External entry added but pending_recalc still true after 24+ hours</entry_not_reflecting>
  <missing_system_entry>Buyback/IPO/CA credit entry expected but not posted by system</missing_system_entry>
  <isin_not_listed>Client cannot add entry because ISIN not yet listed on exchange (ESOP, pre-IPO, unlisted)</isin_not_listed>
</escalation_triggers>

</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
**NEVER expose:** `pk`, `instrument_id`, `client_id`, `settlement_type`, `creation`, `pending_recalc`
**ALWAYS share when relevant:** `trade_date`, `tradingsymbol`, `isin`, `quantity`, `price`, `trade_type`, `external_trade_type`, `exchange`, `series`

### Rule 1: Verify External Entry Exists
**if:** Agent needs to check if an external trade entry was posted for a stock
**then:** Look up by Client ID and filter by appropriate external_trade_type.
- If entry found → share trade_date, tradingsymbol, quantity, price, trade_type. Do NOT share the raw `external_trade_type` value — translate to client-friendly language: discrepant → "manual entry", buyback → "buyback entry", ipo → "IPO allotment", internal_transfer → "account transfer", gift → "gift transfer", esop → "ESOP entry", devolved → "physical settlement", ofs → "OFS allotment", reversal → "short delivery reversal", rightsissue → "rights allotment", takeover → "open offer/takeover", transferout → "transfer out".
- If no entry found → "No [client-friendly type] entry exists for [tradingsymbol] in your account. This may be why the shares are showing as discrepant or the buy average is not available."

### Rule 2: Entry Added but Buy Average Not Updated
**if:** Client says they added discrepancy details but buy average still shows N/A or wrong
**then:** Check `pending_recalc` field (internal use only — do not share).
- If pending_recalc = true → "Your entry for [tradingsymbol] has been recorded and is being processed. The buy average will update within 24 hours."
- If pending_recalc = false AND buy average still wrong in `console_eq_holdings` → verify the entry details (price, qty, date) are correct. If entry looks correct but avg still wrong → escalate.

### Rule 3: Wrong Entry — Client Made a Mistake
**if:** Client says they entered wrong price, quantity, or date in their discrepancy fix
**then:** "Once a discrepancy entry is processed, it cannot be edited from your end. We'll need to correct this on the backend."

Escalate with: client ID, tradingsymbol, ISIN, current wrong entry details (from this tool), and the correct values the client wants.

### Rule 4: Gift Shares — Entry Price
**if:** Client questions the price shown for gift shares OR wants to change it
**then:** Check external_trade_type = gift.
- If entry exists → check `exchange` field: if exchange = "NSE", this entry was added by Zerodha (system-generated). If the client has also made a separate discrepant entry for the same stock, escalate — there may be duplicate entries causing wrong buy average.
- "Your gift shares of [tradingsymbol] were recorded at ₹[price] per share, which is the closing price on the transfer date ([trade_date]). This is the default entry price used for P&L tracking."
- If client wants actual acquisition cost instead → "The default price for gifted shares is the closing price on transfer date. If you need this updated to reflect the original acquisition cost for tax purposes, we can request a backend correction." Escalate with client ID, tradingsymbol, and requested price.

### Rule 5: ESOP Shares — Cannot Add Entry
**if:** Client reports error adding discrepancy for ESOP shares
**then:** Check if the ISIN is listed on exchange.
- If ISIN not listed → "Your ESOP shares ([tradingsymbol]) are not yet listed on the exchange. Discrepancy entries can only be added once the ISIN is active on NSE or BSE. Please try again after the stock is listed."
- If ISIN is listed but error persists → check `console_eq_holdings` protocol Rule 6 (cannot resolve conditions: CA within 10 days, IPO within 3 days, holiday, inactive stock). If none apply → escalate.

### Rule 6: Buyback Entry Verification
**if:** Client asks about buyback share status or entry
**then:** Filter by external_trade_type = buyback.
- If sell entry found → "Your [quantity] shares of [tradingsymbol] were tendered in the buyback at ₹[price] per share on [trade_date]. The buyback proceeds will be credited to your primary bank account by the company."
- If no entry found → "The buyback entry has not been posted yet. Buyback entries are posted on the day the net settlement entry is created in the ledger, after the company processes and confirms acceptance. If the buyback acceptance was confirmed more than 5 trading days ago, we'll investigate further." Escalate if client confirms acceptance was completed and no entry exists after 5 trading days.

### Rule 7: IPO Allotment Entry
**if:** Client's IPO allotted shares show as discrepant and agent checks external trades
**then:** Filter by external_trade_type = ipo.
- If entry found → "Your IPO allotment of [quantity] shares of [tradingsymbol] at ₹[price] has been recorded. If the buy average still shows N/A, the entry may be pending processing (up to 24 hours)."
- If no entry found AND IPO was within last 3 days → "IPO allotment entries take up to 3 days to be posted in the system. Please check back after 3 trading days from the listing date."
- If no entry found AND IPO was more than 3 days ago → escalate.

### Rule 8: Internal Transfer Entry
**if:** Client transferred shares between own demat accounts (primary ↔ secondary) and entry is missing or wrong
**then:** Filter by external_trade_type = internal_transfer.
- If entry found → share details.
- If no entry found → "The transfer entry between your accounts has not been posted yet. We'll raise this for investigation." Escalate.

### Rule 9: No External Trades but Shares Show Discrepant
**if:** No external trade entries found for a stock that shows discrepant in `console_eq_holdings`
**then:** The client needs to add the entry manually. Refer to `console_eq_holdings` protocol Rule 5 for discrepancy resolution steps (Console → Portfolio → Holdings → View discrepancy → Add trade).

If the shares were credited via corporate action (convertible debenture, rearrangement, unclaimed shares), the source may not be obvious to the client → escalate for Console team to investigate and post the correct entry.

### Rule 10: P&L Wrong Due to Missing External Entry
**if:** Client reports wrong P&L AND agent finds no external trade entry for shares that were transferred/gifted/ESOP
**then:** "The P&L for [tradingsymbol] appears incorrect because there is no purchase entry in the system for the [discrepant] shares you hold. P&L is calculated using FIFO from all available trade entries. Without a buy entry, the system cannot compute the correct cost of acquisition.

To fix this, you need to add the purchase details via Console → Portfolio → Holdings → View discrepancy → Add trade. Once the entry is processed, the P&L will recalculate automatically."

### Rule 11: Escalation Criteria
**if:** Any of the following:
- Client entered wrong details in discrepancy fix — needs backend correction (Rule 3)
- Entry added but pending_recalc still true after 24+ hours (Rule 2)
- Buyback/IPO/CA entry expected but not posted after expected timeline (Rules 6, 7)
- ISIN not listed on exchange — client cannot add entry (Rule 5)
- Shares from corporate action credit (convertible debenture, rearrangement) with no clear source for client to self-add (Rule 9)
- Gift shares entry price needs backend correction (Rule 4)
**then:** Escalate with: client ID, tradingsymbol, ISIN, specific issue, and current entry details if applicable.
