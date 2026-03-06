# console_mtf_holdings

## Description

WHEN TO USE:

- Client asks about MTF holdings quantity, buy average, or unrealized P&L
- Client reports MTF holdings not visible or showing wrong quantity
- Client asks about MTF buy average mismatch between Kite and Console
- Client asks about MTF interest charges or how interest is calculated
- Client asks about MTF auto square-off rules or why shares were squared off
- Client asks about converting MTF position to CNC (delivery) or vice versa
- Client asks about MTF margin, funded amount, or initial margin
- Client asks about MTF obligation or settlement calculation
- Client asks about MTF P&L not matching expectations
- Client asks about corporate action impact on MTF holdings (bonus/split credited to MTF)
- Client asks about MTF discrepancy after selling MTF shares

TRIGGER KEYWORDS: "MTF", "margin trading", "funded", "MTF holdings", "MTF interest", "MTF charges", "MTF square off", "auto square off", "MTF conversion", "convert to delivery", "convert to CNC", "MTF buy average", "MTF obligation", "MTF margin", "MTF P&L", "initial margin", "funded amount", "80% breach", "MTF pledge", "MTF brokerage"

## Protocol

# CONSOLE MTF HOLDINGS PROTOCOL

## Knowledge Base

<knowledge_base>

<facts>
- MTF (Margin Trading Facility) allows clients to buy shares by paying only initial margin (~20-50% depending on stock); Zerodha funds the rest
- MTF interest: 0.04%/day (~14.6% p.a.) on the funded amount, charged daily to MTF ledger
- Interest charged on total funded amount, NOT per stock — scrip-wise interest breakdown not available
- Interest accrues on weekends and holidays too — charged on funded closing balance daily
- MTF brokerage: ₹20 + GST per executed order (same as regular delivery)
- MTF pledge/unpledge charges: MTF shares are auto-pledged; ₹30 + GST per ISIN for pledge, ₹30 + GST for unpledge
- Auto square-off: triggered when margin shortfall exceeds 80% of funded value (stock price drops significantly)
- RMS team squares off minimum qty needed to restore margin — not all shares necessarily sold
- After auto square-off, remaining shares continue as MTF; discrepancy may show temporarily (~24-28 working hours to fix)
- MTF conversion to CNC: client can convert MTF position to regular delivery if sufficient funds available in account
- Conversion requires full funded amount to be available as free cash; insufficient margin = conversion fails (may show processed but not actually converted)
- Conversions on ex-date of corporate actions are NOT processed — client must retry after ex-date
- MTF shares under corporate action (bonus/split): corporate action adjustments and credits behave the same regardless of position type (MTF or regular) — no separate timing for MTF
- Console P&L does NOT calculate separately for MTF — uses FIFO across all holdings (CNC + MTF combined)
- Kite MTF filter shows buy average calculated only from MTF product type trades — will differ from Console FIFO avg
- MTF obligation in contract note: shows full purchase value (not just initial margin) — this is correct; CN records gross obligation
- Net settlement for MTF exit: funded amount reversed from MTF ledger, only P&L (exit value - entry value) settled in equity ledger
- When stock is removed from MTF approved list, existing MTF positions are NOT auto-squared-off unless margin breach occurs
- Backedated MTM available on Console MTF holdings — client can select date to view historical MTM
</facts>

<field_usage>
  <share>tradingsymbol | isin | quantity_available | buy_average | holdings_buy_value | closing_value | unrealized_profit | unrealized_profit_percentage</share>
  <banned>close_price (use closing_value instead for client communication)</banned>
</field_usage>

<mtf_charges>
  <interest>0.04%/day on funded amount (~14.6% p.a.) | Charged daily | Includes weekends/holidays | On total funded balance, not per scrip</interest>
  <brokerage>₹20 + GST per order</brokerage>
  <pledge>₹30 + GST per ISIN (auto-pledge on buy) | ₹30 + GST per ISIN (unpledge on sell/conversion)</pledge>
  <stt>0.1% on buy value + 0.1% on sell value (delivery rate, same as CNC)</stt>
</mtf_charges>

<square_off_rules>
  <trigger>Margin shortfall exceeds 80% of funded value</trigger>
  <action>RMS team sells minimum qty needed to restore margin — partial square-off possible</action>
  <timing>Can happen anytime during market hours when breach detected</timing>
  <post_squareoff>Remaining MTF shares continue; temporary discrepancy may appear for 24-28 working hours</post_squareoff>
  <removed_from_list>Stocks removed from MTF approved list: existing positions NOT auto-squared-off unless margin breach</removed_from_list>
</square_off_rules>

<conversion_rules>
  <mtf_to_cnc>Client must have sufficient free cash equal to funded amount | Place conversion request on Console or Kite</mtf_to_cnc>
  <insufficient_margin>Conversion fails silently — status may show "Processed" but shares remain under MTF (display issue)</insufficient_margin>
  <ex_date>Conversions on ex-date of corporate action are NOT processed — retry after ex-date</ex_date>
  <short_delivery>If MTF position is short-delivered and auto-converted to CNC, interest should stop — if not, escalate for reversal</short_delivery>
</conversion_rules>

<buy_average_difference>
  <console>FIFO across ALL holdings (CNC + MTF combined) — mandated by Income Tax Department</console>
  <kite_mtf_filter>Calculates avg only from MTF product type trades — will show different value</kite_mtf_filter>
  <explanation>Both are correct for their purpose: Console = tax reporting (FIFO), Kite MTF filter = MTF-specific cost tracking</explanation>
</buy_average_difference>

<cross_reference>
  <console_eq_holdings>For regular equity holdings qty, buy avg, discrepancy. MTF qty also appears in console_eq_holdings total_quantity.</console_eq_holdings>
  <console_mtf_conversion>For tracking MTF-to-CNC conversion request status, converted qty, and remarks.</console_mtf_conversion>
  <console_eq_holdings_breakdown>For transaction-level view of MTF trades impacting holdings.</console_eq_holdings_breakdown>
</cross_reference>

<escalation_triggers>
  <mtf_interest_overcharge>Client claims interest charged after position fully exited — verify MTF ledger closing balance was zero on claimed dates</mtf_interest_overcharge>
  <conversion_display_bug>Conversion shows "Processed" but shares still in MTF after 2+ trading days</conversion_display_bug>
  <holdings_not_visible>MTF holdings not visible in Console/Kite but MTF interest still being charged</holdings_not_visible>
  <post_squareoff_discrepancy>Discrepancy persists more than 2 trading days after auto square-off</post_squareoff_discrepancy>
  <ca_not_updated>Corporate action credits to MTF holdings not reflected after 2+ trading days from credit date</ca_not_updated>
</escalation_triggers>

<links>
  <mtf_approved_list>zerodha.com/margin/mtf</mtf_approved_list>
  <mtf_interest_console>Console → Reports → MTF Interest Statement</mtf_interest_console>
</links>

</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
**NEVER expose:** `close_price` directly — use `closing_value` (which = close_price × quantity) for client communication.
**ALWAYS share when relevant:** `tradingsymbol`, `isin`, `quantity_available`, `buy_average`, `holdings_buy_value`, `closing_value`, `unrealized_profit`, `unrealized_profit_percentage`

### Rule 1: MTF Buy Average Mismatch (Console vs Kite MTF Filter)
**if:** Client says MTF buy average on Kite differs from Console
**then:** "The buy average on Console is calculated using FIFO across all your holdings of [tradingsymbol] — both regular delivery (CNC) and MTF combined. This is mandated by the Income Tax Department for tax reporting.

The buy average shown under the MTF filter on Kite is calculated only from your MTF trades for that stock. Both values are correct for their respective purposes — Console reflects your tax-reportable average, while the Kite MTF filter shows your MTF-specific cost."

### Rule 2: MTF Holdings Not Visible
**if:** Client says MTF holdings not visible on Kite or Console
**then:** Check `quantity_available` in this tool.
- If qty > 0 in tool data → display issue. "Your [quantity_available] shares of [tradingsymbol] are showing correctly in our records. Please try logging out and back in, or use a different browser/device."
- If qty = 0 but client insists → check `console_eq_holdings` for the same stock (MTF qty may appear in combined holdings). If found there but not here → possible conversion already processed.
- If not found in either tool AND MTF interest still being charged → escalate per `<escalation_triggers>`.

### Rule 3: MTF Interest Calculation
**if:** Client questions MTF interest amount
**then:** "MTF interest is charged at 0.04% per day (approximately 14.6% per annum) on the total funded amount. Interest accrues daily, including weekends and holidays, based on the funded closing balance.

Please note that interest is calculated on the total funded amount across all your MTF positions combined — a per-stock interest breakdown is not available. You can view your interest statement on Console → Reports → MTF Interest Statement."

**if:** Client asks why interest charged on weekends → "Interest accrues on all calendar days since the funded amount remains outstanding regardless of whether markets are open."

**if:** Client says interest charged after selling all MTF positions → verify MTF ledger closing balance was zero on the dates in question. If balance was non-zero (e.g., due to settlement timing), explain. If balance was zero and interest still charged → escalate.

### Rule 4: Auto Square-Off
**if:** Client asks why MTF shares were auto-squared-off
**then:** "MTF positions are auto-squared-off by our risk management team when the margin shortfall exceeds 80% of the funded value. This typically happens when the stock price drops significantly, reducing the value of your collateral below the required threshold.

Only the minimum quantity needed to restore your margin is sold — not necessarily all your MTF shares. Your remaining [quantity_available] shares of [tradingsymbol] continue as MTF holdings."

**if:** Client reports discrepancy after square-off → "After an auto square-off, a temporary discrepancy may appear in your holdings. This is automatically resolved within 24-28 working hours. If the discrepancy persists beyond 2 trading days, we will investigate further."

### Rule 5: MTF Conversion (MTF to CNC)
**if:** Client asks about converting MTF to delivery
**then:** "You can convert your MTF position to regular delivery (CNC) through Kite or Console. To convert, you need sufficient free cash in your account equal to the funded amount for those shares.

If you don't have enough funds, the conversion will fail — it may show as 'Processed' in the status but the shares will remain under MTF. Please verify your available balance before placing the conversion request."

**if:** Conversion shows Processed but shares still in MTF → check `console_mtf_conversion` for actual converted_quantity. If converted_quantity = 0 → "The conversion was not processed due to insufficient margin. The 'Processed' status is a display issue. Please add the required funds and place a new conversion request."
If conversion was 2+ trading days ago and status unclear → escalate.

**if:** Conversion failed on ex-date → "MTF conversions on the ex-date of a corporate action are not processed to avoid complications with the credit handling. Please place the conversion request again after the ex-date."

### Rule 6: MTF P&L Not Matching
**if:** Client says MTF P&L is wrong or doesn't match expectations
**then:** "Console calculates P&L using FIFO across all your holdings of [tradingsymbol] — both regular delivery and MTF combined. If you held [tradingsymbol] shares as CNC before purchasing under MTF, the FIFO calculation will use the oldest shares first when you sell, which can affect the realized P&L differently than expected.

The P&L figures in your ledger reflect the net settlement (exit value minus entry value for the specific MTF position), while Console P&L reflects FIFO-based accounting. These may differ but both are calculated correctly."

### Rule 7: MTF Obligation in Contract Note
**if:** Client says contract note shows full purchase value debited instead of just initial margin
**then:** "The contract note records the gross obligation — the full purchase value of the shares — which is the standard format. The initial margin you paid and the funded amount from Zerodha together make up this total. Your MTF ledger will show the breakup: initial margin from your equity ledger and the funded portion as a debit in your MTF ledger."

### Rule 8: Corporate Action Impact on MTF Holdings
**if:** Client asks about bonus/split shares not reflected in MTF holdings
**then:** "Corporate action adjustments and credits behave the same for MTF and regular holdings — there is no separate or delayed timeline for MTF positions. Your MTF holdings should reflect the updated quantity once the corporate action credit is processed.

If the update hasn't happened after 2 trading days from credit date, we'll escalate this for investigation."

### Rule 9: MTF Charges Breakdown
**if:** Client asks about MTF charges or unexpected debits
**then:** Refer to `<mtf_charges>` and explain:
- "Interest: 0.04% per day on total funded amount (includes weekends/holidays)"
- "Brokerage: ₹20 + GST per order (same as regular delivery)"
- "Auto-pledge on buy: ₹30 + GST per ISIN"
- "Unpledge on sell or conversion: ₹30 + GST per ISIN"
- "STT: 0.1% on both buy and sell value (delivery rate)"

### Rule 10: Stock Removed from MTF Approved List
**if:** Client asks what happens when a stock is removed from MTF approved list
**then:** Two scenarios:

**Reclassification (removed from Group 1 securities):** "If a stock you hold under MTF is reclassified and removed from Group 1 securities, Zerodha will notify you on the same day. You have until 4 PM to either sell the stock during market hours or convert it to CNC (delivery). If you don't sell or convert by 4 PM, Zerodha will convert your MTF position to CNC on the same day."

**General removal from MTF approved list (not reclassification):** "If a stock is removed from the MTF approved list without reclassification, your existing MTF position is NOT automatically squared off. You can continue to hold the position. However, you cannot buy more of that stock under MTF. The position will only be squared off if a margin breach occurs as per standard square-off rules."

### Rule 11: Unrealized P&L Verification
**if:** Client questions unrealized P&L shown in MTF holdings
**then:** "Your unrealized P&L is calculated as: current market value (₹[closing_value]) minus invested value (₹[holdings_buy_value]) = ₹[unrealized_profit] ([unrealized_profit_percentage]%).

Note: This does not include MTF interest charges, brokerage, or other transaction costs. Your actual profit on exit will be lower after accounting for these charges."

### Rule 12: Escalation Criteria
**if:** Any of the following:
- MTF interest charged after position fully exited and MTF ledger balance was zero (Rule 3)
- Conversion shows "Processed" but shares still in MTF after 2+ trading days (Rule 5)
- MTF holdings not visible but interest still being charged (Rule 2)
- Discrepancy after auto square-off persists beyond 2 trading days (Rule 4)
- Corporate action credits to MTF not reflected after 2+ trading days (Rule 8)
**then:** Escalate with: client ID, tradingsymbol(s), specific issue, dates involved, and screenshots if available.
