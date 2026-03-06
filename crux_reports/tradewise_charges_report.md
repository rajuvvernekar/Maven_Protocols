# tradewise_charges_report

## Description

WHEN TO USE:

- Client asks for a breakdown of charges applied to a specific trade or order
- Client questions why brokerage, STT, stamp duty, or exchange charges are a certain amount
- Client wants order-wise charges for trades executed on a specific date
- Agent needs to verify total charges for a trade (brokerage + statutory levies)
- Client reports charges don't match their calculation or the Zerodha brokerage calculator
- Client asks about exchange transaction charges, SEBI fees, or GST on brokerage
- Client wants to understand what each charge component means
- Client reports discrepancy between contract note charges and tradewise charges

TRIGGER KEYWORDS: "tradewise charges", "trade charges", "charges breakdown", "brokerage calculation", "brokerage per trade", "STT charges", "stamp duty", "exchange transaction charges", "SEBI charges", "GST on brokerage", "order charges", "charges for my trade", "why brokerage higher", "total charges for order", "charges per order"

## Protocol

<knowledge_base>

<facts>
- Report shows per-trade breakdown of ALL charges: brokerage, exchange txn charges, SEBI fees, STT, stamp duty, CGST, SGST, IGST
- Required: Client ID, From/To Date. Optional: Exchange, Segment. Select "View orderwise" checkbox for order-level grouping.
- Multiple rows with same order_no = multiple fills for one order — sum charges by order_no for total per order
- trade_process_type: "normal" or null — ignore this field, do not share
- Trade value = quantity × price (from tradebook) — charges calculated on this value
- Brokerage can be null/0 for some trades (e.g., no brokerage charged)
- IGST is typically null (only for inter-state; standard is CGST + SGST)
- GST (CGST 9% + SGST 9% = 18%) applied on brokerage + exchange transaction charges
- Charges may differ slightly from Zerodha calculator due to rounding and per-trade vs per-order calculation
- Exchange charges updated periodically — recent rate changes may cause different charges for same trade type on different dates
- SENSEX options: exchange charges have specific rates that differ from NIFTY options
- CN (Contract Note) charges may not include later adjustments posted directly to ledger
</facts>

<field_usage>
  <share>trading_symbol | order_time (as date/time) | brokerage | turnover (as "exchange transaction charges") | sebi (as "SEBI turnover fee") | stamp_duty | stt (as "STT") | sgst | cgst</share>
  <banned>trade_process_type | order_no (use internally to group) | exchange (use internally) | igst (typically null)</banned>
</field_usage>

<charge_components>
  <brokerage>Flat ₹20 per executed order or 0.03% (whichever is lower) for intraday/F&O. Delivery: 0% (zero). Can be null.</brokerage>
  <exchange_txn_charges>Charged by exchange on turnover. Rate varies by exchange and segment — NSE equity ~0.00297%, BSE equity varies, NSE F&O varies by contract type.</exchange_txn_charges>
  <stt>Securities Transaction Tax — buy+sell for delivery equity (0.1%), sell-side for intraday (0.025%), sell-side for F&O (varies by instrument type).</stt>
  <stamp_duty>State stamp duty on buy-side transactions. Varies by state — typically 0.015% for delivery, 0.003% for intraday/F&O.</stamp_duty>
  <sebi>SEBI turnover fee — ₹10 per crore of turnover (0.0001%).</sebi>
  <gst>18% GST (9% CGST + 9% SGST) on brokerage + exchange transaction charges.</gst>
</charge_components>

<cross_reference>
  <contract_note_charges>Summary of total charges per contract note period — use for aggregate view</contract_note_charges>
  <ledger_report>Charge debits appear as ledger entries — use to trace when charges were debited</ledger_report>
</cross_reference>

<escalation_triggers>
  <rate_mismatch>Exchange transaction charge rate significantly differs from published rate for that exchange/segment</rate_mismatch>
  <brokerage_overcharge>Brokerage exceeds ₹20 cap for F&O/intraday or exceeds 0.03% threshold</brokerage_overcharge>
  <cn_vs_tradewise_mismatch>Contract note charges differ from tradewise charges sum for same date/exchange/segment</cn_vs_tradewise_mismatch>
</escalation_triggers>

</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
**NEVER expose:** `trade_process_type`, `order_no` (use internally to group), `exchange` (use internally), `igst` (typically null)
**ALWAYS share when relevant:** `trading_symbol`, `order_time`, `brokerage`, `turnover` (call it "exchange transaction charges"), `sebi` (call it "SEBI turnover fee"), `stamp_duty`, `stt`, `sgst`, `cgst`
**NEVER** use internal field names with the client — translate to client-friendly terms.

### Rule 1: Single Trade Charges Breakdown
**if:** Client asks about charges for a specific trade
**then:** Find the trade by trading_symbol and order_time. If multiple rows share same order_no → sum all charge fields.

"Here's the charges breakdown for your [trading_symbol] trade on [order_time]:
- Brokerage: ₹[brokerage]
- Exchange transaction charges: ₹[turnover]
- STT: ₹[stt]
- SEBI turnover fee: ₹[sebi]
- Stamp duty: ₹[stamp_duty]
- GST (CGST + SGST): ₹[cgst + sgst]
- Total charges: ₹[sum of all]"

### Rule 2: Multiple Fills Per Order
**if:** Client asks about charges for one order but multiple rows exist with same order_no
**then:** "Your order for [trading_symbol] was executed in [N] parts (fills). The charges are calculated per fill. Here's the combined total for the entire order:
[Show combined charges as in Rule 1]"

Do not expose order_no — just say "your order was executed in multiple parts."

### Rule 3: Brokerage Calculation Verification
**if:** Client questions brokerage amount or says it doesn't match expectations
**then:** Check:
- Delivery (CNC): brokerage should be ₹0 (zero brokerage on delivery)
- Intraday/F&O: ₹20 per executed order OR 0.03% of trade value, whichever is lower
- If brokerage = null/0 → "No brokerage was charged for this trade."
- If brokerage > ₹20 for a single F&O/intraday order → verify if multiple fills (sum per order_no). If still > ₹20 per order → escalate.

"Zerodha charges a flat ₹20 per executed order for intraday and F&O trades, or 0.03% of trade value — whichever is lower. Delivery trades have zero brokerage."

### Rule 4: Exchange Transaction Charges Dispute
**if:** Client says exchange charges seem wrong
**then:** "Exchange transaction charges are set by the exchange and vary by segment and instrument type. The rates are updated periodically. For your [exchange — use internally] [segment] trade, the applicable rate was applied on the trade value."

If the rate significantly differs from known rates → escalate. Known issue: SENSEX options have specific rates different from NIFTY. BSE equity rates may differ from NSE.

### Rule 5: STT Explanation
**if:** Client asks about STT or questions STT amount
**then:** "Securities Transaction Tax (STT) is a government tax on securities transactions:
- Equity delivery: 0.1% on both buy and sell value
- Equity intraday: 0.025% on sell-side only
- Futures: 0.02% on sell-side
- Options: 0.1% on sell-side (on premium value)

STT for your trade: ₹[stt] on [trading_symbol]."

### Rule 6: GST Calculation
**if:** Client asks about GST or questions CGST/SGST amounts
**then:** "GST at 18% is charged on the total of brokerage + exchange transaction charges.
- CGST (9%): ₹[cgst]
- SGST (9%): ₹[sgst]
- Total GST: ₹[cgst + sgst]

GST base = brokerage (₹[brokerage]) + exchange charges (₹[turnover]) = ₹[sum]. GST = 18% of ₹[sum] = ₹[result]."

### Rule 7: Calculator vs Actual Charges Difference
**if:** Client says charges differ from Zerodha brokerage calculator
**then:** "The Zerodha brokerage calculator provides an estimate. Slight differences can occur due to:
- Rounding at trade level vs order level
- Exchange rate updates not yet reflected in the calculator
- Multiple fills for a single order being charged separately

The tradewise charges report shows the actual charges applied to your trades."

If difference is significant (>10% or >₹5 for a single order) → verify and escalate if needed.

### Rule 8: Contract Note vs Tradewise Charges Mismatch
**if:** Client reports difference between CN charges and tradewise charges
**then:** "The contract note shows charges as of the trade date. In some cases, exchange transaction charges are updated after the trade date and the difference is posted directly to your ledger. This means the contract note may show the original charges while your ledger reflects the updated amount.

Check your ledger for any adjustment entries posted after the trade date."

If no adjustment found and mismatch persists → escalate.

### Rule 9: Auction Trade Charges
**if:** trade_process_type = "auction" or client asks about auction charges
**then:** "Auction trades have different charge structures. Auction charges are applied when a trade goes to exchange auction (e.g., short delivery). The charges for auction trades may include additional penalties beyond standard trade charges."

**AGENT HAS TO MANUALLY HANDLE** detailed auction charge calculations.

### Rule 10: Escalation Criteria
**if:** Any of the following:
- Brokerage exceeds ₹20 per order for F&O/intraday after summing all fills (Rule 3)
- Exchange transaction charge rate significantly wrong (Rule 4)
- Contract note vs tradewise mismatch with no ledger adjustment (Rule 8)
**then:** Escalate with: client ID, trading_symbol, order_time, specific charge values, and the discrepancy.
