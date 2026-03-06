# console_eq_pnl

## Description

WHEN TO USE:

- Client questions realized equity P&L (profit or loss from sold shares)
- Client reports P&L values (buy value, sell value, profit) appearing wrong for a stock
- Client asks why a stock shows profit when they expected loss, or vice versa
- Agent needs to verify realized P&L for a specific stock or date range
- Client asks about FIFO impact on P&L (e.g., sold newer shares but FIFO used older cost)
- Client reports P&L mismatch between Console and Kite
- Client asks about intraday vs delivery P&L classification
- Client asks about P&L impact from corporate actions (bonus, split, demerger, merger)
- Client questions Tax P&L values vs Console P&L (different reports, different purposes)
- Client asks about unrealized P&L discrepancy between Console and Kite

TRIGGER KEYWORDS: "P&L", "profit and loss", "realized profit", "realized loss", "buy value", "sell value", "PnL report", "PnL wrong", "showing profit", "showing loss", "capital gain", "STCG", "LTCG", "tax P&L", "intraday P&L", "speculative", "delivery P&L", "unrealized P&L"

## Protocol

## PROTOCOL

<knowledge_base>

<facts>
- Realized P&L = sell_value − buy_value (per FIFO matching of sell qty against oldest buys)
- Only shows P&L for stocks that have been SOLD — no P&L for holdings still held
- FIFO: when client sells, oldest buy is consumed first — affects which cost price is used
- Console P&L does NOT separate MTF and CNC — FIFO applies across all product types combined
- Intraday trades (buy + sell same stock same day) classified as speculative — separate from delivery P&L
- Exception: T2T stocks (series BE/BT/BZ) — same-day buy + sell treated as delivery, not speculative
- Unrealized P&L on Console = (closing price − buy avg) × qty; on Kite = (LTP − buy avg) × qty — will differ due to price source
- Tax P&L is a separate report with additional classifications (STCG/LTCG, delivery/speculative) and may show different values than Console P&L
- Tax P&L report is editable by client on Console for gift shares, cost basis adjustments
- P&L affected by missing/wrong external trade entries — if discrepant shares sold without buy entry, cost = 0 → inflated profit
- Corporate action P&L impact: bonus credited at ₹0 → selling bonus shares shows full sell value as profit (correct per FIFO); split adjusts qty+price proportionally → P&L unchanged; demerger splits cost per COA ratio
- Fractional shares from CA (split/consolidation) settled in cash → appears as realized P&L entry
- Verified P&L (console.zerodha.com/verified) — third-party verified report for ITR filing
</facts>

<field_usage>
  <share>tradingsymbol | isin | quantity | buy_value | sell_value | profit</share>
  <banned>name | client_id | instrument_id</banned>
</field_usage>

<pnl_calculations>
  <realized>profit = sell_value − buy_value | Positive = profit, Negative = loss</realized>
  <buy_value_source>FIFO matched — oldest buy entries consumed first regardless of product type (CNC/MTF/MIS)</buy_value_source>
  <unrealized_console>Unrealized = (closing price − buy avg) × qty | Uses previous day's closing price</unrealized_console>
  <unrealized_kite>Unrealized = (LTP − buy avg) × qty | Uses live last traded price</unrealized_kite>
</pnl_calculations>

<tax_pnl_vs_console_pnl>
  <console_pnl>Realized P&L per FIFO for selected date range — no STCG/LTCG classification</console_pnl>
  <tax_pnl>Classified into delivery STCG, delivery LTCG, speculative (intraday), and charges — used for ITR filing</tax_pnl>
  <differences>Tax P&L may exclude intraday from delivery section; turnover = absolute P&L for speculative; Tax P&L editable for cost adjustments (gifts, transfers)</differences>
</tax_pnl_vs_console_pnl>

<cross_reference>
  <console_eq_holdings>Current buy avg and holdings qty. If buy avg wrong → P&L will also be wrong.</console_eq_holdings>
  <console_eq_tradebook>Verify actual trade prices and dates feeding into P&L.</console_eq_tradebook>
  <console_eq_holdings_breakdown>Walk through FIFO entry by entry to explain P&L calculation.</console_eq_holdings_breakdown>
  <console_eq_external_trades>Missing external entries cause wrong P&L (cost = 0 for discrepant shares).</console_eq_external_trades>
</cross_reference>

<escalation_triggers>
  <pnl_wrong_after_ca>P&L shows incorrect values after corporate action and CA adjustment period has passed (3+ weeks)</pnl_wrong_after_ca>
  <verified_pnl_error>Verified P&L page shows error or values differ from Console P&L</verified_pnl_error>
  <fractional_entry_wrong>Fractional share cash settlement entry has wrong value</fractional_entry_wrong>
  <orphan_entry>Stock shows in unrealized P&L despite all shares being sold long ago</orphan_entry>
</escalation_triggers>

</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
**NEVER expose:** `name`, `client_id`, `instrument_id`
**ALWAYS share when relevant:** `tradingsymbol`, `isin`, `quantity`, `buy_value`, `sell_value`, `profit`

### Rule 1: P&L Verification
**if:** Client questions realized P&L for a stock
**then:** "Your realized P&L for [tradingsymbol]: you sold [quantity] shares with a total buy value (cost of acquisition) of ₹[buy_value] and total sell value (sale proceeds) of ₹[sell_value], resulting in a [profit > 0 ? 'profit' : 'loss'] of ₹[profit].

This is calculated using the FIFO method — when you sold, the cost of the oldest purchased shares was used as the buy value."

### Rule 2: FIFO Causing Unexpected P&L
**if:** Client says "I bought at X and sold at Y but P&L doesn't match"
**then:** "Your P&L is calculated using FIFO (First In, First Out). The buy value used is not necessarily your most recent purchase price — it's the cost of the oldest shares you held at the time of selling.

If you had older shares bought at a different price, FIFO consumes those first. You can verify the exact FIFO matching in the holdings breakdown on Console or Kite (View breakdown)."

If agent needs to prove the calculation → use `console_eq_holdings_breakdown` to walk through entries.

### Rule 3: Discrepant Shares Causing Inflated Profit
**if:** P&L shows unexpectedly high profit AND `console_eq_holdings` shows discrepant > 0 for that stock (or showed before selling)
**then:** "The P&L for [tradingsymbol] may appear inflated because the shares were recorded without a purchase entry (discrepant). When discrepant shares are sold, the system uses ₹0 as the buy value since no cost of acquisition is available, which makes the entire sell value appear as profit.

To correct this, the original purchase details need to be added. If the shares have already been sold, the buy average cannot be updated from your end — we'll need to investigate this further." Escalate if shares already sold with wrong cost.

### Rule 4: Console P&L vs Kite P&L
**if:** Client says P&L differs between Console and Kite
**then:** Check if they're comparing realized or unrealized:
- Realized → should match. If different → check date range used. Console P&L requires specific date range; Kite shows current FY by default.
- Unrealized → "Console uses the previous day's closing price to calculate unrealized P&L, while Kite uses the live last traded price (LTP). This is why the values differ during and after market hours."

### Rule 5: MTF P&L — No Separate Calculation
**if:** Client asks about MTF-specific P&L or says MTF P&L doesn't match expectations
**then:** "Console does not calculate P&L separately for MTF and CNC positions. FIFO is applied across all your holdings of [tradingsymbol] regardless of whether shares were bought under MTF or regular delivery. This means the buy value used in P&L may include both MTF and CNC purchase prices.

Your MTF ledger settlements (net settlement entries) reflect the MTF-specific funding and margin — these are separate from the FIFO-based P&L shown on Console."

### Rule 6: Intraday vs Delivery P&L
**if:** Client questions why same-day buy+sell appears as delivery P&L or vice versa
**then:** Check series field in tradebook:
- Series EQ → "Same-day buy and sell of [tradingsymbol] in EQ series is treated as an intraday (speculative) trade. It will appear under the speculative section in Tax P&L, separate from delivery P&L."
- Series BE/BT/BZ (T2T) → "Since [tradingsymbol] is in the Trade-to-Trade category, same-day buy and sell is treated as a delivery trade, not intraday. Both transactions are considered separate delivery trades."

### Rule 7: Corporate Action Impact on P&L
**if:** Client questions P&L after bonus, split, demerger, or merger
**then:**
- Bonus: "After a bonus issue, the bonus shares are credited at ₹0 cost. If you sell bonus shares, FIFO may consume these zero-cost entries, showing the entire sell value as profit. This is correct per FIFO accounting."
- Split: "A stock split adjusts quantity and price proportionally — your total investment value and P&L remain unchanged."
- Demerger: "After a demerger, the cost of acquisition is split between the original and new entity per the COA ratio announced by the company. P&L is calculated based on this split cost. If the ratio has not been applied yet, P&L may appear incorrect temporarily."
- Merger: "After a merger, shares are swapped at the defined ratio. P&L is calculated using the original acquisition cost carried over to the new shares."
- Fractional shares: "Fractional shares from the corporate action were settled in cash. This appears as a realized P&L entry for the fractional quantity."

If CA was 3+ weeks ago and P&L still appears wrong → escalate.

### Rule 8: Tax P&L vs Console P&L
**if:** Client says Tax P&L report values differ from Console P&L
**then:** "The Tax P&L report and Console P&L serve different purposes:
- Console P&L shows aggregate realized P&L per stock for the selected date range
- Tax P&L classifies trades into delivery STCG, delivery LTCG, and speculative (intraday) with applicable charges

The values may differ because Tax P&L separates intraday trades from delivery, applies holding period classification, and includes charges. For income tax filing, please use the Tax P&L report."

**if:** Client wants to edit Tax P&L → "You can edit the Tax P&L report on Console (Reports → Tax P&L → Edit) to adjust cost of acquisition for gifted shares, transferred shares, or other special cases."

### Rule 9: Unrealized P&L — Orphan Entry
**if:** Client reports a stock showing in unrealized P&L despite having sold all shares
**then:** Check `console_eq_holdings` for that stock. If no holdings found but P&L still shows unrealized entry → escalate as orphan lot. "We've identified that [tradingsymbol] is appearing in your unrealized P&L despite no active holdings. This is a data issue and we'll have it corrected."

### Rule 10: Escalation Criteria
**if:** Any of the following:
- P&L wrong after CA and adjustment period passed (3+ weeks) (Rule 7)
- Verified P&L page error or mismatch (KB escalation trigger)
- Discrepant shares already sold with ₹0 cost — needs backend correction (Rule 3)
- Orphan stock in unrealized P&L (Rule 9)
- Fractional cash settlement entry with wrong value (KB escalation trigger)
**then:** Escalate with: client ID, tradingsymbol, ISIN, expected vs actual P&L values, and date range.
