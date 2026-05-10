# console_mf_pseudo_holdings

## Description

WHEN TO USE:

When clients:
- Ask about current holdings, invested value, or number of units
- Report units not visible after allotment
- Report buy average incorrect
- Ask about pledged or locked units
- Ask about free units available for redemption/SWP
- Report "Fix discrepancy" message on Coin
- Report P&L calculation failure

This is the PRIMARY tool for ALL MF holdings queries. Always check this tool first.

TRIGGER KEYWORDS: "holdings", "units", "buy average", "portfolio", "pledged", "not visible", "XIRR", "invested value", "discrepancy", "fix discrepancy", "PnL calculation failed", "coin"

TAGS: investments, holdings

## Protocol

# CONSOLE MF PSEUDO HOLDINGS PROTOCOL
---

## Section A: Reference Data

### A1 — Scope & Domain Facts

- ETF FOF (Fund of Funds, e.g., "Silver ETF FoF", "Gold ETF FoF") is an MF and appears here. Pure ETFs appear in Kite holdings only.
- **Scheme name field:** `tradingsymbol`.
- **NAV and units:** `price` = NAV per unit (per-unit cost at allotment). `quantity` = number of units allotted.
- **Regular plan holdings:** Coin supports direct mutual fund plans only. If a client holds a regular plan (transferred from another platform), SIP and lumpsum purchase options will not be available for that fund on Coin. Regular plans can be identified when `tradingsymbol` does not contain "DIRECT" in the scheme name. Direct plan variant available on Coin. Existing regular plan units can be held or redeemed through Coin.
- **Stamp duty:** 0.005% is deducted from the investment amount before units are allotted. The client receives units based on the post-stamp-duty amount, while the investment summary shows the full amount. Example: ₹10,000 investment → stamp duty ₹0.50 → ₹9,999.50 invested → at NAV ₹10, client receives 999.95 units instead of 1,000. Stamp duty is not displayed under charges on Console. Stamp duty is separate from the discrepancy diagnostic in **Rule 2**.

---

### A2 — NAV Display Differences

| Platform | NAV Date |
|---|---|
| Console | T-2 days |
| Coin | T-1 day |

This difference causes P&L values to differ between the two platforms. For the latest valuation, refer to Coin.

Reference: NAV difference link from **A8**.

---

### A3 — Internal Flags

| Flag | Meaning |
|---|---|
| `failure_date` populated | P&L calculation failed |
| `discrepant` > 0 | Units exist but no matching trade entries in tradebook |
| `margin` > 0 | Units are pledged |
| `dividend_type` = payout AND `discrepant` > 0 | Payout dividend fund with discrepancy |

---

### A4 — Field Rules

**Shareable with client:**

| Field | Interpretation |
|---|---|
| `tradingsymbol` | Fund name (communicate as fund name, not as a trading symbol) |
| `buy_average` | Average buy price per unit (share if asked) |
| `buy_value` | Total buy value of the holding (share if asked) |
| `dividend_type` | Dividend type — growth or IDCW (share if asked) |
| `margin` | Margin pledged against this holding (share if asked) |

**Non-shareable:**

| Field | Interpretation |
|---|---|
| `failure_date` | Date the holding entered a failed state |
| `available` | Units available for trading or redemption |
| `discrepant` | Units with a discrepancy between exchange and depository records |
| `loan` | Units pledged as collateral against a loan |
| `client_id` | Internal client identifier |
| `isin` | Fund's ISIN code |
| `instrument_id` | Internal instrument identifier |
| `t1` | Units in T+1 settlement — not yet credited to available holdings |
| `pending` | Units pending credit or processing |

---

### A5 — MF Unit Transfer (Inward and Outward)

**Inward — non-demat:** Dematerialization required before transfer to Zerodha. Units in physical mode or Statement of Account must be dematerialised before transfer. Charges: ₹150 \+ 18% GST per scheme (ELSS: ₹150 per investment within scheme); ₹100 courier charges (one-time). Timeline: up to 4 days after submitting documents. Links: transfer MF article and dematerialization article from **A8**.

**Inward — demat (CDSL Easiest):** For MF units held in demat with another broker. CDSL Easiest for CDSL-to-CDSL transfers. ELSS locked units: closure cum transfer process only (same account holder). Free (unlocked) ELSS units transferable without restriction. Timeline: up to 4 days after submitting documents. Link: transfer shares article from **A8**.

**Outward:** Three destination methods — another CDSL demat account (CDSL Easiest online), NSDL demat (off-market transfer), non-demat (rematerialisation required). ELSS lock-in: NSDL destination requires rematerialisation first; CDSL destination via closure cum transfer (same PAN only). Check `margin` > 0 before initiating — pledged units must be unpledged first: Console → Portfolio → Holdings → [fund] → Unpledge. Charges: ₹25 per security \+ 18% GST; 0.015% stamp duty on considered amount; rematerialisation ₹150 \+ 18% GST per scheme (₹150 per investment for ELSS); DIS booklet: first 10 slips free; additional booklets ₹100 \+ 18% GST \+ ₹100 \+ 18% GST courier. Link: outward transfer article from **A8**.

---

### A6 — Holdings Verification Alternatives

Holdings can be verified via:
- Coin app or Console.
- Monthly CAS (Consolidated Account Statement) email.
- Statement of Holdings (SOH) — sent to registered email monthly.
- Transaction cum holding statement from CDSL Easi portal.

Link: CAS statement article from **A8**.

---

### A7 — XIRR Display Behavior

Portfolio XIRR will not display if the majority of investments are less than one year old. The system shows '–' to avoid displaying disproportionately high or misleading XIRR values.

Reference: XIRR article from **A8**.

---

### A8 — Links

| Topic | URL |
|---|---|
| Why does Console show a different MF NAV? | https://support.zerodha.com/category/mutual-funds/coin-general/coin-reports/articles/mf-nav-of-t-2-days-on-console |
| Why are newly allotted units shown as NA on the Coin app? | https://support.zerodha.com/category/mutual-funds/payments-and-orders/orders-on-coin/articles/coin-app-na-new-units |
| How to transfer mutual funds from other platforms to Coin? | https://support.zerodha.com/category/mutual-funds/coin-general/transferring-mf/articles/how-do-i-move-my-existing-mutual-fund-investments-to-coin |
| What is dematerialization and how to dematerialise MF investments? | https://support.zerodha.com/category/mutual-funds/coin-general/transferring-mf/articles/what-and-how-i-de-materialize-mutual-fund-investments |
| How to transfer shares from another demat account to Zerodha? | https://support.zerodha.com/category/your-zerodha-account/transfer-of-shares-and-conversion-of-shares/transfer-securities/articles/how-do-i-transfer-shares-from-another-derodha-demat#H1 |
| Transfer mutual funds out of Coin | https://support.zerodha.com/category/mutual-funds/coin-general/transferring-mf/articles/transfer-mutual-funds-out-of-coin |
| Transaction cum holding statement | https://support.zerodha.com/category/console/portfolio/console-holdings/articles/transaction-cum-holding-statement |
| Portfolio XIRR | https://support.zerodha.com/category/console/portfolio/console-holdings/articles/portfolio-xirr |
| Capital support team (LAS queries) | capitalsupport@zerodha.com |

---

## Section B: Decision Flow

### Routing

```
Query relates to MF holdings →
│
├─ failure_date populated → Rule 1
├─ Discrepancy signals (discrepant > 0, "fix discrepancy" message, or "NA" invested amount) → Rule 2
├─ Mismatch between this tool and console_mf_holdings → Rule 3
├─ Pledged units blocking redemption/SWP, or collateral margin query → Rule 5
├─ Client asks about transferring MF units to or from Zerodha (demat or non-demat) → Rule 7
├─ Fund still showing in portfolio after full redemption (residual decimal units) → Rule 8
├─ Client asks about verifying holdings outside Coin (CAS, SOH, CDSL statement) → Rule 11
└─ General MF holdings query → Check data here first; invoke console_mf_holdings only if `available`, `holdings_date`, or `total_quantity` is needed
```

### Fallback

If no root cause is identified after the diagnostic steps → escalate to Human Agent with fund name, `discrepant` value (internal), and the specific issue.

---

## Section C: Rules

### Rule 1 — `failure_date`: Immediate Escalation

If `failure_date` is populated → escalate to Human Agent.

---

### Rule 2 — Discrepancy Detection & Diagnosis

**Payout dividend check:**
If `dividend_type` = payout AND `discrepant` > 0 → escalate to Human Agent.

**Tradebook verification:**
Invoke console_mf_tradebook for the fund. Sum all BUY `quantity` entries; subtract all SELL `quantity` entries. Result must equal `available` from this tool.

If result matches `available` → discrepancy; escalate to Human Agent.

If result does not match,

1. **Late allotment:** Recent order found in ‘mf_order_history’ with `exchange_timestamp` within T+3 working days (excluding weekends and trading/settlement holidays). If no Coin purchase history exists and the fund is present, ask whether units were transferred from another platform before continuing.
   - Units may arrive late to demat. NA shows on T+2 for one day; rectified on T+3. This is late delivery of units, not a longer allotment window.
   - If units are confirmed allotted (in ‘mf_order_history’ or console_mf_tradebook) but invested value is NA or incorrect: settlement files are processed in stages; resolves within 24–48 hours.
   - Share the late allotment link from **A8**.

2. **Late allotment — escalation:** `exchange_timestamp` beyond T+3 working days (excluding weekends and trading/settlement holidays) → escalate to Human Agent.

3. **Wrongly entered external trades:** All purchases through Coin but external entries exist in console_mf_external_trades → escalate to Human Agent.

4. **Transferred from another platform:** No Coin purchase history, no external entries → guide to add external trades: Console → Portfolio → Holdings → [fund] → Add External Trade.

5. **NFO recently allotted:** NFO order found → auto-resolves in 3–5 days.

6. **`failure_date` populated → Rule 1.**

---

### Rule 3 — Mismatch Between Reports

1. If `available` or `discrepant` in console_mf_pseudo_holdings does not match the corresponding values in `console_mf_holdings` → invoke `console_mf_tradebook` to identify missing trade entries.
2. If trade entries exist but the mismatch persists → escalate to Human Agent.

---

### Rule 4 — Buy Average / Investment Value

1. If values differ from the client's expectation → invoke console_mf_external_trades for missing or incorrect external entries.
2. If investment value has not updated → settlement delay (liquid: T-day by 7 PM; non-liquid: T+1 by 7 PM).

---

### Rule 5 — Pledged Units

1. Confirm: `margin` > 0.
2. Check the client's Silo classification from ‘get_all_client_data’. If Silo = K → collateral margins from pledged mutual funds update at end of day. Communicate: pledge processed; collateral margin available from the next trading day.
3. For all other Silos or when the query is about redemption/SWP: communicate the number of pledged units and the unpledge path — Console → Portfolio → Holdings → [fund] → Unpledge.

---

### Rule 6 — Console vs Coin Value Difference

1. Communicate the NAV date difference per **A2** — Console shows T-2, Coin shows T-1, so P&L values differ. Refer to Coin for the latest valuation.
2. Share the NAV difference link from **A8**.

---

### Rule 7 — MF Unit Transfer (Inward and Outward)

**Inward transfers (to Zerodha):**

1. Non-demat units (physical or Statement of Account) → guide per **A5** (inward — non-demat). Share charges, timeline, and links from **A5**.
2. Demat units from another broker → guide per **A5** (inward — demat). Share charges, timeline, and link from **A5**.
3. Once units are transferred, the client may need to add external trade entries for correct buy average and P&L: Console → Portfolio → Holdings → [fund] → Add External Trade.

**Outward transfers (from Zerodha):**

4. Check `margin` > 0. If pledged → advise unpledging first per **A5** (outward).
5. Guide per **A5** (outward) based on destination (CDSL demat / NSDL demat / non-demat), including lock-in and PAN conditions. Share charges and link from **A5**.
6. Share the client's DP ID and Client ID from ‘get_all_client_data’.

---

### Rule 8 — Residual Decimal Units After Full Redemption

1. Check `quantity` here. Invoke console_mf_holdings for `total_quantity` of the same fund.
2. If the fund exists here but not in console_mf_holdings (or units mismatch between the two) → residual decimal unit display issue requiring backend data rerun.
3. Escalate to Human Agent.

---

### Rule 9 — LAS / Loan Against Securities Redirect

Redirect to the capital support team at the contact from **A8**.

---

### Rule 10 — XIRR Not Displaying

1. Invoke console_mf_tradebook for the fund. Sum BUY `quantity` entries; check `trade_date` for each. If ≥50% of `available` units have `trade_date` within the last year → XIRR will not display.
2. Communicate per **A7** — portfolio XIRR does not display when the majority of investments are less than one year old; the system shows '–' to avoid disproportionately high or misleading values.
3. Share the XIRR link from **A8**.

---

### Rule 11 — Holdings Verification Alternatives

1. Holdings can be verified via monthly CAS email, Statement of Holdings (SOH sent monthly to registered email), or transaction cum holding statement from CDSL Easi. Per **A6**.
2. Share the CAS statement link from **A8**.
