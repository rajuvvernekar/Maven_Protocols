# console_mf_tradebook

## Description

WHEN TO USE:

When clients:
- Ask about ELSS lock-in period or when they can redeem ELSS
- Report order shows Allotted but units missing
- Ask about exact NAV/price at which units were allotted
- Need P&L verification using FIFO
- Ask about trade entry existence for allotted/redeemed orders

TRIGGER KEYWORDS: "lock-in", "ELSS unlock", "when can I redeem ELSS", "allotment date", "trade date", "FIFO", "allotted but not visible", "coin"

## Protocol

# CONSOLE MF TRADEBOOK PROTOCOL


### A1 — Tool Purpose & Scope

- Contains executed orders only (allotment/redemption completed).
- P&L is calculated from this tool's data using FIFO.
- If a trade entry is missing for an allotted order → P&L and holdings issues will result.
- Zerodha fund house WhatsApp orders → trade entries posted here if allotted.
- Scheme name field is `tradingsymbol`.

### A2 — ELSS Lock-in Rules

- ELSS lock-in: exactly 3 calendar years from `trade_date` (allotment date) per BUY entry, on a FIFO basis.
- `trade_date` = allotment date — not the order placement date or payment date.
- Example: allotted on 15-Mar-2022 → unlocks on 15-Mar-2025.
- If lock-in ends today → units redeemable from tomorrow (T+1 settlement).

### A3 — Field Rules

**Shareable with client (if asked):** `trade_date` (as allotment date), `tradingsymbol` (as fund name), `trade_type`, `quantity`, `price`.

**Internal reasoning only (use for analysis, never share):** `order_execution_time` (NAV cutoff check), `order_id`, `trade_id`, `client_id`.

**Suppress (no client use, only reasoning  purpose): exchange, instrument_id, isin, scheme_code, settlement_type

### A4 — Cross-Reference Protocols

| Topic | Refer to |
|---|---|
| Units missing after allotment — discrepancy diagnosis | console_mf_pseudo_holdings (primary source) |
| Transferred-in units affecting P&L / buy average | console_mf_external_trades |
| Redeemable units verification | console_mf_holdings (`available` field) |

### Preflight (run on every query)

1. Fetch the MF tradebook data for the client and relevant date range/fund.
2. Apply field protection per **A3** — identify shareable, internal, and banned fields.
3. Identify the fund using `tradingsymbol`.
4. Format amounts with ₹ and Indian comma notation. Format dates as DD MMM YYYY.

### Routing Tree

```
Query relates to MF tradebook →
│
├─ Client asks when ELSS units can be redeemed
│  → Rule 1
│
├─ Order allotted but units missing (flagged by mf_order_history)
│  → Rule 2
│
├─ Client disputes MF P&L
│  → Rule 3
│
└─ General tradebook query
   → Check data, apply field protection, respond with shareable fields
```

### Scope

- Address: ELSS lock-in dates, allotment verification, P&L FIFO calculations, and trade entry verification.

### Fallback

If trade data seems inconsistent or missing entries cannot be explained → escalate with client ID, fund name, trade dates, and the specific discrepancy.


### Rule 1 — ELSS Lock-in

1. Filter `tradingsymbol` for the ELSS fund, `trade_type` = BUY.
2. Sort by `trade_date` ascending (FIFO). Calculate lock-in end = `trade_date` + exactly 3 calendar years per entry (per **A2**).
3. If only one lot: "Your [X units] allotted on [date] will unlock on [unlock date]."
4. If multiple lots — show earliest unlocking lot first:
   "Your earliest [X units] (allotted [date]) unlock on [unlock date]. Remaining lots unlock on: [date] ([Y units]), [date] ([Z units])."
5. If earliest lock-in ends today: "Your units will be redeemable from tomorrow. ELSS redemption follows T+1 settlement." (Per **A2**.)

### Rule 2 — Allotment Verification

1. Triggered when mf_order_history shows an order as allotted but units are missing.
2. Check if a trade entry exists here for the matching fund and date.
3. Trade entry exists → units are allotted. Check console_mf_pseudo_holdings (per **A4**) for discrepancy diagnosis.
4. Trade entry missing:
   - NFO (new fund offer): wait for listing + T+1 day.
   - Regular fund: escalate.

### Rule 3 — P&L FIFO Verification

1. List BUY entries sorted by `trade_date` ascending. Match SELL entries against the oldest BUY first (FIFO).
2. Always cross-reference console_mf_external_trades (per **A4**) for any transferred-in units — missing external entries will skew P&L regardless of whether tradebook entries look complete.
3. If calculation still differs after both checks → escalate.
