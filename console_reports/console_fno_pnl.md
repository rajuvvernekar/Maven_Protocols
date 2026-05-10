# console_fno_pnl

## Description

WHEN TO USE:

When clients:
- Question realized F&O P&L (profit or loss from closed/expired contracts)
- Report F&O P&L values (buy value, sell value, profit) appearing wrong
- Ask why a contract shows profit when they expected loss, or vice versa
- Ask about P&L for physically settled contracts (ITM options/futures at expiry)
- Question F&O P&L in Tax P&L report vs Console P&L
- Report expired contract not showing in P&L
- Report asterisk (*) mark on P&L entries after contract symbol change

TRIGGER KEYWORDS: "F&O P&L", "FnO profit", "FnO loss", "futures P&L", "options P&L", "realized F&O", "F&O buy value", "F&O sell value", "derivative P&L", "contract P&L", "expiry P&L", "physical delivery P&L", "F&O tax P&L", "options turnover"

TAGS: reports, holdings

## Protocol

# CONSOLE FNO PNL PROTOCOL

---

## Section A: Reference Data

---

### A1 — Fundamentals

- Realized P&L only — no charge or MTM breakdown.

---

### A2 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |  
|---|---|  
| `tradingsymbol` | Trading symbol of the instrument |  
| `quantity` | Number of contracts traded |  
| `buy_value` | Total buy value |  
| `buy_average` | Average buy price |  
| `sell_value` | Total sell value |  
| `sell_average` | Average sell price |  
| `realized_profit` | Realized P&L |  
| `realized_profit_percentage` | Realized P&L as a percentage |

**Non-shareable:**

| Field | Interpretation |  
|---|---|  
| `client_id` | Internal client identifier |

---

### A3 — Segment Mapping

| Segment Code | Covers |  
|---|---|  
| FO | Equity F&O (NSE futures & options) |  
| CDS | Currency derivatives |  
| COM | Commodities |

---

### A4 — Escalation Data

Include when escalating to human agent: client ID, tradingsymbol, segment, date range, specific discrepancy.

---

### A5 — Scenarios & Interpretations

- **P&L verification:**  
The fields `buy_value`, `buy_average`, `sell_value`, `sell_average`, `realized_profit`, and `realized_profit_percentage` together represent the client's realized position on a contract. A positive `realized_profit` is a gain; negative is a loss.

- **Physical delivery P&L:**  
When an ITM stock option or futures contract is physically settled at expiry, the F&O P&L closes the contract at intrinsic value (or zero), which may show as a loss on the F&O side. The actual shares are delivered or received, and the delivery P&L appears in equity P&L as an intraday delivery trade. Total P&L on the position requires combining both the F&O P&L entry and the corresponding equity delivery P&L entry from `console_eq_pnl`.

- **OTM expired (long position):**  
When a long options position expires OTM, the option becomes worthless. The entire premium paid (`buy_value`) is reflected as a realized loss.

- **OTM expired (short position):**  
When a short options position expires OTM, the option expires worthless. The full premium received (`sell_value`) is reflected as realized profit.

- **Asterisk (*) on P&L entry:**  
The asterisk indicates the contract symbol was changed during the series due to a corporate action on the underlying stock (e.g., lot size change, symbol rename). The system closed the old contract and opened a new one with adjusted terms. This appears only on the adjustment day — subsequent days show normally. P&L is calculated correctly across both contract versions.

- **Tax P&L vs Console F&O P&L:**  
Differences between the two reports arise because Tax P&L classifies trades by type (futures, options) and calculates turnover as the absolute value of profit per contract, while Console F&O P&L shows aggregate realized profit per contract for the selected date range. Physical delivery contracts may appear split between F&O and equity sections in Tax P&L. Intraday contracts on certain dates may be excluded from one tab — a known issue for specific dates. For income tax filing, the Tax P&L report is the correct reference.

- **Charges / MTM query:**  
This report shows realized P&L only — brokerage, STT, and other charges are not included. For a full breakdown including charges, the Tax P&L report is available on Console under Reports → Tax P&L. For live MTM on open positions, Kite is the correct reference.

---

## Section B: Decision Flow

### Routing

```  
Route by scenario  
   ├─ Realized F&O P&L verification for a contract → Rule 1  
   ├─ Physical delivery P&L (ITM stock option / futures at expiry) → Rule 2  
   ├─ OTM options expired worthless → Rule 3  
   ├─ Asterisk (*) on P&L entry → Rule 4  
   ├─ Expired contract not showing in P&L → Rule 5  
   ├─ Tax P&L vs Console F&O P&L difference → Rule 6  
   └─ Charges / brokerage / STT / MTM query → Rule 7  
```

### Fallback

If no root cause is found → escalate to human agent.

---

## Section C: Rules

---

### Rule 1 — P&L Verification

1. Refer to A5 (P&L verification) for scenario context and interpretation.

---

### Rule 2 — Physical Delivery P&L

1. Refer to A5 (Physical delivery P&L) for scenario context.  
2. If client reports double quantity in equity P&L after physical settlement → escalate to human agent.

---

### Rule 3 — OTM Options Expired Worthless

1. Determine position direction:  
   - Long (bought options) → refer to A5 (OTM expired — long position) for scenario context.  
   - Short (sold options) → refer to A5 (OTM expired — short position) for scenario context.

---

### Rule 4 — Asterisk (*) on P&L Entry

1. Refer to A5 (Asterisk on P&L entry) for scenario context and interpretation.

---

### Rule 5 — Expired Contract Not in P&L

1. Verify:  
   - Correct segment is selected per A3.  
   - Date range covers the expiry date.  
2. Both correct and contract still missing → escalate to human agent per A4.

---

### Rule 6 — Tax P&L vs Console F&O P&L

1. Refer to A5 (Tax P&L vs Console F&O P&L) for scenario context and interpretation.  
2. If client reports a significant unexplained difference between the F&O tab and tradewise exits tab → escalate to human agent.

---

### Rule 7 — Charges and MTM Queries

1. Refer to A5 (Charges / MTM query) for scenario context and interpretation.  
2. If client needs the Tax P&L report for charges → direct to Console → Reports → Tax P&L.  
3. If client needs live MTM on open positions → direct to Kite positions screen.  
4. If client needs historical day-wise MTM → this tool does not provide it; escalate to human agent if further investigation is needed.
