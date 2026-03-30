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

## Protocol

# CONSOLE FNO PNL PROTOCOL 

---

## Section A: Reference Data

---

### A1 — Tool Purpose & Fundamentals

This tool looks up a client's realized F&O P&L per contract. It shows realized P&L only — no charge or MTM breakdown.

**Segment selection is critical:** FO for equity F&O, CDS for currency, COM for commodities. Wrong segment = no results or incomplete data.

**Input:** Client ID + segment + date range.

---

### A2 — Field Usage Rules

**Shareable fields:**

`tradingsymbol` | `quantity` | `buy_value` | `buy_average` | `sell_value` | `sell_average` | `realized_profit` | `realized_profit_percentage`

**Internal-only fields** (use for reasoning; communicate outcomes in plain language):

`client_id`

---

### A3 — Segment Mapping

| Segment Code | Covers |
|---|---|
| FO | Equity F&O (NSE futures & options) |
| CDS | Currency derivatives |
| COM | Commodities |

---

### A4 — Escalation Data Template

When escalating, always include: **client ID, tradingsymbol, segment, date range, and specific discrepancy.**

---

### A5 — Response Templates

**R1 — P&L verification:**
"Your realized P&L for [tradingsymbol]: [quantity] contracts with buy value ₹[buy_value] (avg ₹[buy_average]) and sell value ₹[sell_value] (avg ₹[sell_average]), resulting in a [profit/loss] of ₹[realized_profit] ([realized_profit_percentage]%)."

**R2 — Physical delivery P&L:**
"Your [tradingsymbol] contract was physically settled at expiry. In F&O P&L, the ITM contract is closed at intrinsic value (or zero), which may show as a loss on the F&O side. However, the actual shares were delivered/received, and the delivery P&L is reflected in your equity P&L as an intraday delivery trade.

To see your total P&L on this position, you need to combine the F&O P&L entry with the corresponding equity delivery P&L entry in `console_eq_pnl`."

**R3 — OTM expired (long position):**
"Your [tradingsymbol] option expired out-of-the-money (OTM) and became worthless. The entire premium paid (₹[buy_value]) is reflected as a realized loss."

**R4 — OTM expired (short position):**
"Your [tradingsymbol] option expired OTM. The full premium received (₹[sell_value]) is reflected as realized profit since the option expired worthless."

**R5 — Asterisk on P&L entry:**
"The asterisk (*) mark indicates that the contract symbol was changed during the series due to a corporate action on the underlying stock (e.g., lot size change, symbol rename). The system closed the old contract and opened a new one with adjusted terms. This appears only on the adjustment day — subsequent days will show normally. Your P&L is calculated correctly across both contract versions."

**R6 — Tax P&L vs Console F&O P&L:**
"The Tax P&L report and Console F&O P&L may show different values because:
- Tax P&L classifies trades by type (futures, options) and calculates turnover as the absolute value of profit per contract
- Console F&O P&L shows aggregate realized profit per contract for the selected date range
- Physical delivery contracts may appear split between F&O and equity sections in Tax P&L
- Intraday contracts on certain dates may be excluded from one tab — known issue for specific dates

For income tax filing, use the Tax P&L report."

---

## Section B: Decision Flow

---

### Preflight (run on every query)

```
1. Confirm correct segment selected (per A3)
   └─ FO for equity F&O, CDS for currency, COM for commodities.
      Wrong segment = no results or incomplete data.
```

### Route

```
Intent / Condition                                          → Rule
──────────────────────────────────────────────────────────────────────
Client questions realized F&O P&L for a contract            → Rule 1
Physical delivery P&L (ITM stock option / futures at expiry)→ Rule 2
OTM options expired worthless                               → Rule 3
Asterisk (*) on P&L entry                                   → Rule 4
Expired contract not showing in P&L                         → Rule 5
Tax P&L vs Console F&O P&L difference                       → Rule 6
Charges / brokerage / STT / MTM query                       → Rule 7
```

### Scope

- Address the client's query about their F&O realized P&L, physical delivery impact, expired contracts, and tax report differences.
- Use **A2** field rules in all client communication.

### Fallback

If no route matches, investigate using the tool data and Section A references. If no root cause is found, escalate per **A4**.

---

## Section C: Rules

---

### Rule 1 — P&L Verification

1. Respond per **A5-R1**.

---

### Rule 2 — Physical Delivery P&L

1. Respond per **A5-R2**. Client needs to combine F&O P&L with equity delivery P&L in `console_eq_pnl`.
2. If client reports double quantity in equity P&L after physical settlement → escalate per **A4**.

---

### Rule 3 — OTM Options Expired Worthless

1. Determine if long or short position:
   a. Long position (bought options) → respond per **A5-R3**.
   b. Short position (sold options) → respond per **A5-R4**.

---

### Rule 4 — Asterisk (*) on P&L Entry

1. Respond per **A5-R5**.

---

### Rule 5 — Expired Contract Not in P&L

1. Verify internally:
   a. Correct segment selected (per Preflight / **A3**).
   b. Date range covers the expiry date.
2. If both correct and contract still missing → escalate per **A4** immediately with: client ID, tradingsymbol, expiry date, segment, date range used.
3. Escalate directly 

---

### Rule 6 — Tax P&L vs Console F&O P&L

1. Respond per **A5-R6**.
2. If client reports significant unexplained difference between F&O tab and tradewise exits tab → escalate per **A4**.

---

### Rule 7 — Charges and MTM Queries

This tool shows realized P&L only — no charge or MTM breakdown.

