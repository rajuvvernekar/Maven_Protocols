# corporate_action_orders

## Description

WHEN TO USE:

When clients:
- Ask about the status of a buyback, rights issue, or open offer order they placed
- Ask whether their buyback/rights/open offer application was accepted or rejected
- Question allotment price or investment amount for a CA order
- Ask about buyback proceeds or when shares will be debited/credited
- Report applying for a CA but order not showing
- Ask about rights issue allotment status or payment details
- Question why CA order was rejected

TRIGGER KEYWORDS: "buyback order", "buyback status", "rights issue order", "rights issue applied", "open offer order", "tender status", "buyback applied", "buyback accepted", "buyback rejected", "allotment status", "CA order", "corporate action order", "rights allotment", "buyback proceeds", "tender offer"

## Protocol

# CORPORATE ACTION ORDERS PROTOCOL 

---

## Section A: Reference Data

---

### A1 — Tool Purpose & Fundamentals

This tool shows client orders placed for **buybacks and open offers**. It returns all CA orders for a client.

Rights issue applications are not tracked in this tool — they are submitted through the client's bank (ASBA) or the company's registrar (see **Rule 3**).

**Input:** Client ID only.

---

### A2 — Field Usage Rules

**Shareable fields:**

`creation` | `trading_symbol` | `isin` | `price` | `quantity` | `status` | `allotment_price` | `investment_amount` | `trade_type`

**Internal-only fields** (use for reasoning; communicate outcomes in plain language):

`client_id` | `modified`

**Client-facing terminology:**

| Internal Value | Client-Facing Alternative |
|---|---|
| allotment_price = 0 | "The allotment price has not been updated yet" (not "₹0") |
| trade_type | Describe as "buyback", "rights issue", or "open offer" |

---

### A3 — Status Values

| Status | Meaning |
|---|---|
| Placed | Order submitted — pending processing by company/exchange |
| Processed | Order accepted and executed — shares debited (buyback/open offer) or allotted (rights) |
| Rejected | Order not accepted — shares returned, no debit |

---

### A4 — Cross-Reference Tools

| Tool | When to Use |
|---|---|
| `console_eq_holdings` | Check if tendered shares debited from holdings (buyback) or allotted shares credited (rights). |
| `console_eq_external_trades` | Buyback exit entries and rights issue allotment entries appear here. |
| `console_eq_pnl` | Buyback P&L reflected here — may need manual Tax P&L editing for post-Oct 2024 buybacks. |

---

### A5 — Buyback Tax Treatment (Post Oct 2024)

From 1st October 2024, buyback proceeds are taxed as **capital gains** in the hands of the shareholder (previously the company paid dividend distribution tax). Tax P&L may need manual editing for buybacks processed after this date — editable on Console (Reports → Tax P&L → Edit).

If Tax P&L shows profit instead of expected loss for buyback → known issue for recent buybacks. Client can edit Tax P&L manually.

---

### A6 — Escalation Data Template

When escalating, always include: **client ID, trading_symbol, trade_type, status, and specific issue.**

---

### A7 — Key Timelines

| Event | Expected Timeline |
|---|---|
| Buyback proceeds credited to primary bank | 5–15 working days after acceptance (paid by the company, not Zerodha) |
| Status stuck at "Placed" → escalate | Beyond CA closure date + 5 working days |
| Rights allotment discrepancy → escalate | Beyond listing date + 3 days |

---

### A8 — Response Templates

**R1 — Order status (generic):**
"Your [trade_type] order for [trading_symbol]: [quantity] shares at ₹[price] per share, placed on [creation]. Current status: [status]."

**R2 — Status: Placed:**
"Your order has been submitted and is pending processing by the company. Processing timelines depend on the corporate action schedule."

**R3 — Status: Rejected:**
"Your order was not accepted. Your shares have not been debited and no further action is needed from your side."

**R4 — Buyback processed:**
"Your buyback tender of [quantity] shares of [trading_symbol] at ₹[allotment_price > 0 ? allotment_price : price] has been accepted. The tendered shares have been debited from your holdings. Buyback proceeds will be credited to your primary bank account by the company — this typically takes 5–15 working days after acceptance.

Note: If only part of your tendered shares were accepted (partial acceptance), the remaining shares will continue in your holdings."

**R5 — Open offer processed:**
"Your open offer tender of [quantity] shares of [trading_symbol] at ₹[allotment_price > 0 ? allotment_price : price] has been accepted. The tendered shares will be debited and proceeds credited to your bank account by the acquirer."

**R6 — Rights issue redirect:**
"Rights issue applications are submitted directly through your bank's ASBA facility or the company's registrar — they are not tracked in this tool. Please check with your bank for the ASBA application status, or with the company's RTA (Registrar and Transfer Agent) for allotment status."

**R7 — Allotment price not yet updated:**
"The allotment price has not been updated yet. This does not mean your order was rejected — it will be updated once the company confirms the final allotment details."

**R8 — Order not found:**
"I don't see a [buyback/rights issue/open offer] order for [trading_symbol] in your account. This could mean:
- The application was not submitted successfully
- The application was placed from a different platform or process

Could you confirm how and when you placed the application? If you have a confirmation screenshot, that would help us investigate further."

**R9 — Buyback tax treatment (post Oct 2024):**
"From 1st October 2024, buyback proceeds are taxed as capital gains in the hands of the shareholder (previously the company paid dividend distribution tax). Your Tax P&L may need manual editing for buybacks processed after this date — you can edit the Tax P&L on Console (Reports → Tax P&L → Edit) to reflect the correct capital loss/gain."

---

## Section B: Decision Flow

---

### Preflight (run on every query)

```
1. Identify the CA type the client is asking about
   (buyback, rights issue, or open offer)

2. If rights issue → respond per A8-R6 immediately.
   This tool does not track rights issue applications.
```

### Route

```
Intent / Condition                                          → Rule
──────────────────────────────────────────────────────────────────────
Order status verification (buyback / open offer)            → Rule 1
Buyback order — processed                                   → Rule 2
Rights issue query                                          → Rule 3
Open offer order — processed                                → Rule 4
Allotment price showing as 0                                → Rule 5
Order not found                                             → Rule 6
Buyback tax treatment / Tax P&L issue                       → Rule 7
```

### Scope

- Address the client's query about their corporate action orders (buyback, open offer).
- Use **A2** field rules and client-facing terminology in all client communication.
- Redirect rights issue queries per Rule 3 — this tool does not track them.

### Fallback

If no route matches, cross-reference with **A4** tools for additional context. If no root cause is found, escalate per **A6**.

---

## Section C: Rules

---

### Rule 1 — Order Status Verification

1. Look up by Client ID and find matching `trading_symbol`.
2. Respond per **A8-R1** + the applicable status template:
   a. Placed → append **A8-R2**.
   b. Processed → route to **Rule 2** (buyback) or **Rule 4** (open offer) for type-specific details.
   c. Rejected → append **A8-R3**.

---

### Rule 2 — Buyback Order (Processed)

1. Respond per **A8-R4**. Proceeds timeline per **A7**.
2. If client says shares still showing in holdings despite status = Processed → check `console_eq_holdings` (per **A4**). If shares still there → escalate per **A6**.

---

### Rule 3 — Rights Issue (Not Available on This Tool)

1. Respond per **A8-R6**.
2. Rights issue applications are tracked through the client's bank (ASBA) or company registrar — this tool has no data for them.


---

### Rule 4 — Open Offer Order (Processed)

1. Respond per **A8-R5**.

---

### Rule 5 — Allotment Price = 0

1. If `allotment_price` = 0 AND status = Placed or Processed → respond per **A8-R7**. Per **A2** terminology table, communicate as "not yet updated," not "₹0."

---

### Rule 6 — Order Not Found

1. Respond per **A8-R8**.
2. If client confirms they applied → escalate per **A6**.

---

### Rule 7 — Buyback Tax Treatment (Post Oct 2024)

1. Respond per **A8-R9**. Tax details per **A5**.

---

## Section D: General Notes

- This tool tracks buyback and open offer orders only. Rights issue applications go through the client's bank (ASBA) or company registrar.
- Allotment price defaults to 0.0 if not yet allotted — this does not mean rejection.
- Buyback proceeds are credited by the company to the client's primary bank account, not by Zerodha. Typically 5–15 working days.
- Buyback accepted shares are removed from holdings; partial acceptance leaves remaining shares in holdings.
- Rights issue shares may show as discrepant initially until listing — resolved after listing date.
- Buyback tax treatment changed from 1 Oct 2024: now capital gains for shareholder. Tax P&L may need manual editing.
