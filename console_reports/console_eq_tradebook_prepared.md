# console_eq_tradebook_prepared

## Description

WHEN TO USE:

- Client asks about equity trade history older than 100 days
- Client needs full tradebook for tax filing, audit, employer compliance, or legal purposes
- Client requests tradebook since account inception or for a past financial year
- Agent needs to verify old trades to explain historical buy average, P&L, or corporate action impact
- Account is closed and client requests historical trade data
- Client questions tax P&L values and agent needs to verify old trades beyond 100-day window

TRIGGER KEYWORDS: "old trades", "last year trades", "FY 2023-24", "FY 2024-25", "since inception", "full tradebook", "trade history more than 100 days", "historical trades", "closed account tradebook", "tax filing tradebook", "audit", "old tradebook"

## Protocol

# CONSOLE EQ TRADEBOOK PREPARED

## PROTOCOL

<knowledge_base>

<facts>
- This tool has no date range limitation — can fetch trades since account inception
- Identical schema and data as `console_eq_tradebook` — same fields, same data source
- Use this tool ONLY when date range exceeds 100 days; for recent trades use `console_eq_tradebook`
- P&L is calculated from tradebook using FIFO (First In First Out)
- For closed accounts, this is the only way to retrieve historical trade data
- Large date ranges with high trade volume may take longer to load
- All facts about series, T2T, FIFO, CN from `console_eq_tradebook` apply here equally
</facts>

<field_usage>
  <share>trade_date | order_execution_time | tradingsymbol | exchange | order_id | trade_id | trade_type | quantity | price | isin | series</share>
  <banned>instrument_id | settlement_type | client_id</banned>
</field_usage>

<cross_reference>
  <console_eq_tradebook>Same schema, limited to last 100 days. Use for recent trade queries.</console_eq_tradebook>
  <console_eq_external_trades>Off-platform trades. If trade not found here, check external trades.</console_eq_external_trades>
  <console_eq_pnl>Realized P&L computed from tradebook FIFO.</console_eq_pnl>
</cross_reference>

<escalation_triggers>
  <data_not_loading>Report fails to load or times out for large date ranges</data_not_loading>
  <trade_missing>Trade expected but not found in either tradebook or external trades</trade_missing>
</escalation_triggers>

</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
**NEVER expose:** `instrument_id`, `settlement_type`, `client_id`
**ALWAYS share when relevant:** `trade_date`, `order_execution_time`, `tradingsymbol`, `exchange`, `order_id`, `trade_id`, `trade_type`, `quantity`, `price`, `isin`, `series`

### Rule 1: When to Use This Tool
**if:** Requested date range is within last 100 days
**then:** Use `console_eq_tradebook` instead — faster and same data.

**if:** Requested date range exceeds 100 days OR client needs full history
**then:** Use this tool. Enter Client ID, From Date, and To Date.

### Rule 2: Full Tradebook Requests (Tax/Audit/Compliance)
**if:** Client requests full tradebook for tax filing, audit, employer compliance, or legal purposes AND account is active
**then:** Do NOT generate and share the report directly. Instead, guide the client to download it themselves:

"You can download your tradebook and other reports from Console. Here are the guides:
- How to download trade and funds reports: https://support.zerodha.com/category/console/reports/other-queries/articles/how-to-download-trade-and-funds-reports-in-pdf
- Where to see trades for a particular period: https://support.zerodha.com/category/console/reports/other-queries/articles/where-can-i-see-all-the-trades-i-ve-taken-for-a-particular-period"

**if:** Client asks for tradebook in PDF format → share the same links above.

### Rule 3: Closed Account Trade Data
**if:** Client's account is closed and they need historical trade data
**then:** This tool can still retrieve data using the client ID. Generate the report for the requested period and share trade details. (This is the only scenario where the agent shares report data directly.)

### Rule 4: Trade Verification for Old Dates
**if:** Agent needs to verify old trades (for buy avg, P&L, or CA impact explanation)
**then:** Same rules as `console_eq_tradebook` — verify trade existence, check series for T2T, explain FIFO. All business rules from `console_eq_tradebook` (Rules 2-10) apply identically here.

### Rule 5: Contract Note Queries for Old Dates
**if:** Client asks about charges, MTM, or obligation details for old trades
**then:** **AGENT HAS TO MANUALLY HANDLE.** This tool does not contain charge or obligation data. Agent must refer to the actual contract note.

### Rule 6: Tradebook vs Tax P&L Difference
**if:** Client says tradebook sell value doesn't match Tax P&L for a financial year
**then:** "The tradebook shows gross trade values for each individual trade. The Tax P&L applies FIFO matching across financial years and may exclude intraday trades from delivery P&L. Both reports are correct for their respective purposes. The Tax P&L is the report to use for income tax filing."

### Rule 7: Escalation Criteria
**if:** Any of the following:
- Report fails to load or times out for large date ranges
- Trade expected but not found in both tradebook tools and external trades
**then:** Escalate with: client ID, date range requested, tradingsymbol if specific, and error details.
