# console_eq_holdings_breakdown

## Description

WHEN TO USE:

When clients:
- Question buy average and need to walk through the FIFO calculation entry by entry
- Ask to see the breakdown of their holdings for a specific stock
- Report breakdown not matching tradebook or missing entries
- Ask about LIQUIDBEES or ETF dividend reinvestment entries (fractional units at price 0)
- Need verification if a corporate action entry (bonus, split, dividend reinvestment, merger, demerger) was posted
- Need confirmation if an external/discrepant trade entry is reflected in the breakdown
- Need to check if a specific buy/sell trade is included in the holdings calculation

TRIGGER KEYWORDS: "breakdown", "view breakdown", "holdings breakdown", "FIFO calculation", "how average calculated", "trade entries", "dividend reinvestment", "LIQUIDBEES dividend", "bonus entry", "split entry", "breakdown missing", "breakdown not showing"

TAGS: holdings, demat

## Protocol

# CONSOLE EQ HOLDINGS BREAKDOWN PROTOCOL

---

## Section A: Reference Data

---

### A1 — Fundamentals

- Buy average is calculated from these entries using FIFO.  
- Breakdown reflects the same data that drives buy average and P&L on Console — if breakdown is correct, avg and P&L are correct.  
- Breakdown entries may take up to 1 trading day to reflect after a trade.

---

### A2 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |  
|---|---|  
| `tradingsymbol` | Stock symbol |  
| `isin` | ISIN identifier |  
| `price` | Entry price |  
| `quantity` | Entry quantity |  
| `exchange` | Exchange (NSE / BSE / DIVIDEND) |  
| `order_execution_time` | Execution timestamp |  
| `trade_type` | Buy or sell |  
| `trade_id` | Trade reference |  
| `order_id` | Order reference |  
| `external_trade_type` | External entry type (IPO, gift, ESOP, buyback, transfer, discrepant) |

**Non-shareable:**

| Field | Interpretation |  
|---|---|  
| `client_id` | Internal client identifier |  
| `instrument_id` | Internal instrument id |  
| `pseudo_trade` | True = system-generated entry (corporate action or dividend reinvestment); false = regular trade |  
| `corporate_action_id` | Internal corporate action reference |  
| `pledged` | True = holding is pledged; false = unpledged |

---

### A3 — Entry Type Identification

| Detection Logic | Entry Type | Description |  
|---|---|---|  
| `exchange` = NSE/BSE, `pseudo_trade` = false, `external_trade_type` = blank | Regular trade | Shares purchased and sold on Kite |  
| `exchange` = DIVIDEND, `price` = 0, fractional qty, `pseudo_trade` = true | Dividend reinvestment | ETF/MF dividend unit credit (e.g., LIQUIDBEES, GOLDBEES). Directly impacts avg price. |  
| `price` = 0, `pseudo_trade` = true, `corporate_action_id` populated | Bonus credit | Bonus shares credited at zero cost |  
| `pseudo_trade` = true, `corporate_action_id` populated (qty/price adjusted) | Split adjustment | Qty multiplied, price divided per split ratio |  
| `external_trade_type` populated (discrepant/buyback/IPO/gift/ESOP/internal_transfer) | External entry | Came from external trades system |

---

### A4 — CA Entry Timelines

| Corporate Action | Expected Entry Timeline |  
|---|---|  
| Bonus | T+2 from record date |  
| Split | Immediate (on record date) |  
| Demerger | 30–45 days from record date |

---

### A5 — Escalation Data

- Include when escalating to human agent: client ID, tradingsymbol, ISIN, specific missing or incorrect entries, and dates.

---

## Section B: Decision Flow

### Routing

```  
Route by scenario  
   ├─ Buy average verification (walk through FIFO) → Rule 1  
   ├─ Entries with price = 0 or fractional qty (dividend / ETF) → Rule 2  
   ├─ "Why is there a ₹0 entry I didn't make?" (bonus/split) → Rule 3  
   ├─ Trade in tradebook but missing from breakdown → Rule 4  
   ├─ Strange / unexplained entry in holdings breakdown → Rule 5  
   ├─ Holdings breakdown won't load → Rule 6  
   ├─ Buy average dispute — prove against `console_eq_holdings` → Rule 7  
   └─ Specific corporate action verification in breakdown → Rule 8  
```

### Fallback

- If no rule matches → escalate to human agent per A5.

---

## Section C: Rules

---

### Rule 1 — Walk Through FIFO Calculation

1. List all entries for the tradingsymbol chronologically. For each entry, share: date, trade_type (buy/sell), quantity, price, and source identified via A3 (regular trade / corporate action / external entry / dividend reinvestment).  
2. Buy average is calculated using FIFO — when the client sells, the oldest purchased shares are consumed first, changing the average of remaining shares.  
3. If sell entries exist → identify which buy lots each sell consumed (oldest first) and include this in the explanation.

---

### Rule 2 — Dividend Reinvestment Entries

1. Identify dividend reinvestment entries per A3.  
2. Explain to client: ETFs like LIQUIDBEES reinvest dividends as additional units at zero cost, which directly impacts buy average.

---

### Rule 3 — Bonus / Split Entries in Breakdown

1. Identify entry type per A3.  
2. Bonus (price = 0, CA entry) → bonus share credit at zero cost, which reduces overall buy average.  
3. Split (qty/price adjusted, CA entry) → quantity was multiplied and price per share proportionally reduced. Total investment value remains unchanged.

---

### Rule 4 — Entry Missing from Breakdown

1. If the trade was executed within the last 1 trading day → inform client per A1; trade is in the tradebook and will appear in the breakdown shortly. Buy average and P&L are not affected.  
2. If trade was 2+ trading days ago and still not in breakdown → escalate to human agent per A5.

---

### Rule 5 — Unrecognized Entries in Breakdown

1. Identify the entry type per A3:  
   a. `external_trade_type` populated → external entry for shares received via transfer/gift/IPO/ESOP/buyback. Invoke `console_eq_external_trades` for details.  
   b. `exchange` = DIVIDEND → dividend reinvestment (per Rule 2).  
   c. Corporate action entry (price = 0, system entry) → bonus/split/merger/demerger.  
   d. None of the above → escalate to human agent per A5 as potential breakdown-tradebook mismatch.

---

### Rule 6 — Breakdown Not Loading / Error

1. Try a different stock to confirm whether the issue is stock-specific or account-wide.  
2. Stock-specific → escalate to human agent per A5 with client ID and tradingsymbol.  
3. Account-wide → temporary issue; suggest retrying after some time or using a different browser. If the issue persists beyond 24 hours → escalate to human agent per A5.

---

### Rule 7 — Buy Average Cross-Check Against Holdings

1. Walk through FIFO per Rule 1 — list buy entries chronologically, consume oldest-first against any sell entries, and compute the average of remaining quantity.  
2. If the FIFO-derived average matches `console_eq_holdings` → confirm to client that buy average is correct.  
3. If the FIFO-derived average does not match `console_eq_holdings` → escalate to human agent per A5.

---

### Rule 8 — Corporate Action Entry Verification

1. Identify the CA entry per A3 (price = 0 for bonus, or adjusted qty/price around CA date for split/merger/demerger).  
2. CA entry found → share date, qty, price.  
3. CA entry not found → compare against expected timeline per A4. If beyond expected timeline → escalate to human agent per A5.
