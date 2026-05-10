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

TAGS: corporate-actions, orders

## Protocol

# CORPORATE ACTION ORDERS PROTOCOL

---

## Section A: Reference Data

---

### A1 — Fundamentals

- OFS (Offer for Sale) orders are not handled in this tool — escalate to human agent for all OFS queries without checking the tool.  
- Rights Issue orders are not tracked in this tool. Clients should check their bank for ASBA status, or the company's RTA for allotment status.  
- Reasons an order may not appear in this tool: application was not submitted successfully, or it was placed from a different platform or process.  
- Delisting and Takeover: only one closing window — cancel and refile is the only option to change quantity.  
- Buyback: multiple windows may be available; one order allowed per window. To change quantity, cancel and refile within the same window.

---

### A2 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |  
|---|---|  
| `creation` | Order creation date |  
| `trading_symbol` | Trading symbol of the instrument |  
| `isin` | ISIN code of the instrument |  
| `price` | Price per share |  
| `quantity` | Number of shares |  
| `status` | Current order status |  
| `allotment_price` | Allotment price. Value of 0 means the company has not yet updated the allotment price — use `price` as the placed price until updated. |  
| `investment_amount` | Total investment amount |

**Non-shareable:**

| Field | Interpretation |  
|---|---|  
| `modified` | Reflects status updates, not client-initiated edits — clients cannot modify CA orders; cancel and refile to change quantity |  
| `client_id` | Internal client identifier |  
| `trade_type` | Translate to "buyback", "delisting", or "takeover/open offer" when communicating with the client |

---

### A3 — Status Values

| Status | Meaning |  
|---|---|  
| Placed | Order submitted and forwarded to the exchange. Acceptance by the company/RTA is not guaranteed. |  
| Processed | Order accepted and executed — shares debited from holdings. |  
| Rejected | Order not accepted — shares not debited. Two scenarios: (1) Zerodha-level rejection: no free shares available in the client's demat on the window closing date. (2) RTA non-acceptance: order was placed successfully at Zerodha/exchange level but was not accepted by the RTA. |

---

### A4 — Buyback Tax Treatment (Post Oct 2024)

- From 1st October 2024, buyback proceeds are taxed as capital gains in the hands of the shareholder (previously the company paid dividend distribution tax).  
- For buybacks processed after this date, Tax P&L may show incorrect classification. The Tax P&L report is editable on Console (Reports → Tax P&L → Edit) to allow cost basis and gain/loss corrections.

---

### A5 — Escalation Data

Include when escalating to human agent: client ID, trading_symbol, trade_type, status, specific issue.

---

### A6 — Key Timelines

| Event | Expected Timeline |  
|---|---|  
| Buyback proceeds credited to primary bank | 5–15 working days after acceptance (paid by the company, not Zerodha) |  
| Order status stuck at "Placed" | Up to CA closure date \+ 5 working days |  
| Rights allotment discrepancy | Up to listing date \+ 3 days |

- If actual timing exceeds these thresholds → escalate to human agent per A5.

- **CA data retention in this tool:** see table below.

| CA Type | Data Visible in This Tool |  
|---|---|  
| Buyback | \~7 days |  
| Takeover | \~14 days |  
| Delisting | 5–7 days |

If the corporate action is older than the above window, data will not be available in this tool. In that case, invoke `console_eq_external_trades` and look under the buyback section there.

---

### A7 — Processed State Details by CA Type

| CA Type | What Happens on Processed Status |  
|---|---|  
| Buyback | Shares debited from holdings. Proceeds credited to client's primary bank by the company (not Zerodha) — timeline per A6. Partial acceptance possible; remaining shares stay in holdings. |  
| Delisting | Shares debited from holdings. Proceeds credited to client's bank account by the company. |  
| Takeover | Shares debited from holdings. Proceeds credited to client's bank account by the acquirer. |

---

## Section B: Decision Flow

### Routing

```  
Route by scenario  
   ├─ OFS query → Rule 3  
   ├─ Rights issue query → Rule 3  
   ├─ Order status verification (buyback / delisting / takeover) → Rule 1  
   ├─ Buyback order — status = Processed → Rule 2  
   ├─ Delisting or Takeover order — status = Processed → Rule 4  
   ├─ Allotment price showing as 0 → Rule 5  
   ├─ Order not found in the tool → Rule 6  
   └─ Buyback tax treatment / Tax P&L issue → Rule 7  
```

### Fallback

If no route matches and no root cause is found → escalate to human agent.

---

## Section C: Rules

---

### Rule 1 — Order Status Verification

1. Look up by client ID and find the matching `trading_symbol`.  
2. Communicate order details: trade_type, trading_symbol, quantity, price, creation date, and status.  
3. Apply status handling per A3:  
   - Placed → order pending; processing timeline depends on corporate action schedule. If beyond CA closure date \+ 5 working days per A6 → escalate to human agent.  
   - Processed → route to Rule 2 (buyback) or Rule 4 (delisting/takeover).  
   - Rejected → shares not debited; identify rejection scenario per A3.

---

### Rule 2 — Buyback Order (Processed)

1. Apply buyback processed details per A7. Use `allotment_price` if populated; otherwise use `price` per A2.  
2. If client says shares still showing in holdings despite status = Processed → invoke `console_eq_holdings`. If shares still present → escalate to human agent.

---

### Rule 3 — Rights Issue and OFS (Not Handled in This Tool)

Apply A1:  
- OFS query → escalate to human agent immediately, without checking the tool.  
- Rights Issue query → direct client per A1 (bank for ASBA, RTA for allotment).

---

### Rule 4 — Delisting / Takeover Order (Processed)

1. Apply delisting/takeover processed details per A7. Use `allotment_price` if populated; otherwise use `price` per A2.

---

### Rule 5 — Allotment Price = 0

1. If `allotment_price` = 0 → communicate per A2 that the company has not yet updated the allotment price. Do not present the value as ₹0 to the client.

---

### Rule 6 — Order Not Found

1. Communicate possible reasons per A1.  
2. Ask client to confirm how and when the application was placed; a confirmation screenshot aids investigation.  
3. If client confirms they applied → escalate to human agent.

---

### Rule 7 — Buyback Tax Treatment (Post Oct 2024)

1. Apply buyback tax treatment per A4.  
2. If Tax P&L shows incorrect classification for a post-Oct 2024 buyback → advise the client to edit via Console → Reports → Tax P&L → Edit.  
3. If client cannot edit or the issue persists → escalate to human agent.
