# console_fno_tradebook_prepared

## Description

WHEN TO USE:

- Client asks about F&O trade history older than 100 days
- Client needs full F&O tradebook for tax filing, audit, or compliance
- Client requests F&O tradebook since account inception or for a past financial year
- Agent needs to verify old F&O trades to explain historical P&L or position
- Account is closed and client requests historical F&O trade data

TRIGGER KEYWORDS: "old F&O trades", "last year F&O", "FY F&O tradebook", "historical F&O trades", "F&O since inception", "full derivative tradebook", "closed account F&O"

## Protocol

# CONSOLE FNO TRADEBOOK PREPARED PROTOCOL

## PROTOCOL

<knowledge_base>

<facts>
- This tool has no date range limitation — can fetch F&O trades since account inception
- Identical schema and data as `console_fno_tradebook` — same fields, same data source
- Required inputs: Client ID, From Date, To Date, Segment (FO/CDS/COM)
- Use this tool ONLY when date range exceeds 100 days; for recent trades use `console_fno_tradebook`
- For closed accounts, this is the only way to retrieve historical F&O trade data
- All business rules from `console_fno_tradebook` (Rules 1-7) apply here equally
</facts>

<field_usage>
  <share>trade_date | order_execution_time | tradingsymbol | exchange | segment | trade_type | quantity | price | order_id | trade_id | strike | expiry_date | instrument_type</share>
  <banned>client_id</banned>
</field_usage>

<cross_reference>
  <console_fno_tradebook>Same schema, limited to last 100 days. Use for recent F&O trades.</console_fno_tradebook>
  <console_fno_pnl>Realized P&L computed from tradebook entries.</console_fno_pnl>
</cross_reference>

</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
**NEVER expose:** `client_id`
**ALWAYS share when relevant:** `trade_date`, `order_execution_time`, `tradingsymbol`, `exchange`, `segment`, `trade_type`, `quantity`, `price`, `order_id`, `trade_id`, `strike`, `expiry_date`, `instrument_type`

### Rule 1: When to Use This Tool
**if:** Requested date range is within last 100 days
**then:** Use `console_fno_tradebook` instead — faster and same data.

**if:** Requested date range exceeds 100 days OR client needs full F&O history
**then:** Use this tool. Enter Client ID, From Date, To Date, and Segment.

### Rule 2: Full Tradebook Requests (Tax/Audit/Compliance)
**if:** Client requests full F&O tradebook for tax filing, audit, or compliance AND account is active
**then:** Do NOT generate and share the report directly. Instead, guide the client to download it themselves:

"You can download your F&O tradebook and other reports from Console. Here are the guides:
- How to download trade and funds reports: https://support.zerodha.com/category/console/reports/other-queries/articles/how-to-download-trade-and-funds-reports-in-pdf
- Where to see trades for a particular period: https://support.zerodha.com/category/console/reports/other-queries/articles/where-can-i-see-all-the-trades-i-ve-taken-for-a-particular-period"

**if:** Client asks for formatted PDF → share the same links above.

### Rule 3: Closed Account Trade Data
**if:** Client's account is closed and they need historical F&O trade data
**then:** This tool can still retrieve data using the client ID. Generate report for the requested period. (This is the only scenario where the agent shares report data directly.)

### Rule 4: Contract Note Queries for Old Dates
**if:** Client asks about charges, MTM, or obligation details for old F&O trades
**then:** **AGENT HAS TO MANUALLY HANDLE.** This tool does not contain charge or obligation data.

### Rule 5: Escalation Criteria
**if:** Any of the following:
- Report fails to load or times out for large date ranges
- Trade expected but not found in either tradebook tool
**then:** Escalate with: client ID, date range, segment, tradingsymbol if specific, and error details.
