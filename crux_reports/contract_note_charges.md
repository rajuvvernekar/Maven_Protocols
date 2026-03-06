# contract_note_charges

## Description

WHEN TO USE:

- Client asks for total charges summary for a specific date range, exchange, or segment
- Client wants aggregate charges breakdown (not per-trade, but totals by charge type)
- Agent needs to verify total brokerage, STT, stamp duty, GST, exchange charges for a period
- Client comparing aggregate charges across months or segments
- Client asks about clearing charges, IPTF charges, or other CN-specific charge heads

TRIGGER KEYWORDS: "contract note charges", "total charges", "aggregate charges", "charges summary", "total brokerage", "total STT", "total stamp duty", "charges for the month", "charges breakdown summary", "CN charges", "contract note"

## Protocol

# CONTRACT NOTE CHARGES PROTOCOL

## PROTOCOL

<knowledge_base>

<facts>
- Report provides aggregate charges by account_head (charge type) for a selected date range, exchange, and segment
- Required: Client ID, Exchange (NSE/BSE), Segment (EQ/FO/CDS/COM), From/To Date
- Each row = one charge component (account_head) with its total charge amount
- Total row provides sum of all charges for the period
- Account heads: Stamp Duty, Exchange Transaction Charges, STT, SEBI Turnover Fees, Brokerage, Clearing Charges, CGST, SGST, IGST, Investor Protection Fund Tax (IPTF)
- This is a SUMMARY tool — for order-level breakdown use tradewise_charges_report
- Clearing charges: charges for clearing and settlement of trades (separate from exchange charges)
- IPTF: contribution towards investor protection mechanisms — small amount per trade
- XML contract notes may show slightly different charges than PDF CN due to IPFT inclusion timing
</facts>

<field_usage>
  <share>account_head (as charge component name) | charge (as amount) | Total</share>
  <banned>client_id | exchange (use internally) | segment (use internally)</banned>
</field_usage>

<account_heads>
  <stamp_duty>Government stamp duty on trade value</stamp_duty>
  <exchange_txn_charges>Exchange charges for trade execution</exchange_txn_charges>
  <stt>Securities Transaction Tax — government tax on securities transactions</stt>
  <sebi_turnover_fees>SEBI regulatory fee based on turnover</sebi_turnover_fees>
  <brokerage>Zerodha's brokerage charges for executing trades</brokerage>
  <clearing_charges>Charges for clearing and settlement</clearing_charges>
  <cgst>Central GST (9%) on brokerage + exchange charges</cgst>
  <sgst>State GST (9%) on brokerage + exchange charges</sgst>
  <igst>Integrated GST (for inter-state — usually zero)</igst>
  <iptf>Investor Protection Fund Tax</iptf>
</account_heads>

<cross_reference>
  <tradewise_charges_report>Per-trade charge breakdown — use for order-level detail (snake_case TBD)</tradewise_charges_report>
  <ledger_report>Charge debit entries on ledger</ledger_report>
</cross_reference>

</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
**NEVER expose:** `client_id`, `exchange` (use internally), `segment` (use internally)
**Share:** `account_head` (translated to client-friendly name), `charge`, `Total`

### Rule 1: Charges Summary
**if:** Client asks for total charges for a period
**then:** "Here's your charges summary for [period]:
- Brokerage: ₹[brokerage]
- Exchange transaction charges: ₹[exchange_txn]
- STT: ₹[stt]
- SEBI turnover fee: ₹[sebi]
- Stamp duty: ₹[stamp_duty]
- Clearing charges: ₹[clearing]
- GST (CGST + SGST): ₹[cgst + sgst]
- Investor Protection Fund: ₹[iptf]
- **Total charges: ₹[Total]**"

### Rule 2: Per-Trade Redirect
**if:** Client asks for per-order or per-trade breakdown from this aggregate view
**then:** "This report shows the total charges for the period. For a per-trade breakdown showing charges for each individual order, I can check the tradewise charges report instead."

Use tradewise_charges_report for per-order detail.

### Rule 3: Charge Component Explanation
**if:** Client asks what a specific charge head means
**then:** Use `<account_heads>` to explain the component in client-friendly language.

### Rule 4: PDF vs XML CN Difference
**if:** Client reports charge difference between PDF and XML contract note
**then:** "The PDF contract note includes the most up-to-date charges. The XML version may occasionally differ slightly, particularly for exchange transaction charges and IPTF, as these may be adjusted after the initial CN generation. The PDF version is the authoritative document."

### Rule 5: Escalation Criteria
**if:** Total charges seem significantly wrong compared to trading volume for the period, or specific charge head shows unusual amount
**then:** Escalate with: client ID, date range, exchange, segment, and specific discrepancy.
