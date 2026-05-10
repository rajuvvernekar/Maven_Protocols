# console_eq_pseudo_holdings

## Description

WHEN TO USE:

When clients:
- Report quantity mismatch between Kite and Console
- Report holdings visible on one platform but not the other
- Report Console shows inflated or zero holdings that don't match Kite
- Report split shares not reflecting in Kite after receiving CDSL confirmation
- Need cross-reference or validation of equity holdings quantities against SOT (Statement of Transactions) data
- Need verification if a discrepancy is genuine (system-level) or display-only
- Need confirmation whether transferred/credited shares are reflected in SOT
- Need a second source of truth for holdings qty before escalating

TRIGGER KEYWORDS: "quantity mismatch", "Kite shows different", "Console shows different", "not matching", "cross-check holdings", "verify holdings", "SOT", "pseudo", "holdings don't match", "wrong quantity on Kite", "wrong quantity on Console", "shares visible on Kite but not Console", "shares visible on Console but not Kite", "split shares not showing", "split not reflecting"

TAGS: holdings

## Protocol

# CONSOLE EQ PSEUDO HOLDINGS PROTOCOL

---

## Section A: Reference Data

---

### A1 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |  
|---|---|  
| `tradingsymbol` | Exchange trading symbol of the instrument |  
| `isin` | ISIN code of the instrument |  
| `buy_average` | Average cost per share |  
| `buy_value` | `buy_average` × total quantity |  
| `available` | Free qty available for trading/selling |  
| `t1` | Qty bought yesterday; settles end of today |  
| `margin` | Qty pledged or blocked as collateral; still in client demat |  
| `pending` | Qty expected from a corporate action; not yet credited to demat — communicate as "being processed for credit" or "yet to be credited" |  
| `discrepant` | Qty mismatch between tradebook and demat holdings file |  
| `loan` | Qty pledged outside Zerodha via LAS or lent externally to an NBFC |

**Non-shareable:**

| Field | Interpretation |  
|---|---|  
| `instrument_id` | Internal instrument mapping identifier |  
| `failure_date` | Date on which a processing failure occurred for this holding |

---

### A2 — Tradingsymbol Matching Rules

- Always compare positions by **ISIN**, not by `tradingsymbol`. Names can differ across tools for the same instrument.  
- Common causes of name difference:  
  - NSE vs BSE naming (e.g., SPEL vs SPICELEC)  
  - Post-corporate action rename (old name in SOT, new name in Console)  
  - Temporary ISIN for bonus / rights shares

---

### A3 — Escalation Data

- Include when escalating to human agent: client ID and `tradingsymbol`(s).

---

## Section B: Decision Flow

### Routing

```  
Route by scenario  
   ├─ failure_date populated (any value)                                    → Rule 12  
   ├─ tradingsymbol contains ISIN-format alphanumeric entry  
   │    (client asking about this instrument)                               → Rule 12  
   ├─ Qty validation between pseudo and holdings  
   │    (match or mismatch on same ISIN)                                    → Rule 1  
   ├─ Stock present in one tool but not the other  
   │    (Holdings-not-Pseudo / Pseudo-not-Holdings / Pseudo-zero-H-active)  → Rule 2  
   ├─ Tradingsymbol name differs across tools  
   │    (ISIN resolution or ISIN-not-found)                                 → Rule 3  
   ├─ Stock split query (using pseudo data as source of truth)              → Rule 4  
   ├─ Discrepant qty (`discrepant` > 0 in pseudo)                           → Rule 5  
   ├─ Transfer-in overlapping with T1 purchase                              → Rule 6  
   ├─ Safekeep / frozen shares (CDSL statement mismatch)                    → Rule 7  
   ├─ T1 / settlement query                                                 → Rule 8  
   ├─ Pending CA credit query                                               → Rule 9  
   ├─ Pledged qty (`margin`) query                                          → Rule 10  
   └─ Loan (LAS) query                                                      → Rule 11  
```

### Fallback

- If no route matches, invoke `console_eq_holdings` and `console_eq_external_trades` for additional context. If no root cause is identified → escalate to human agent per A3.

---

## Section C: Rules

---

### Rule 1 — Qty Validation

Always compare by ISIN per A2.

**1a. Match**  
1. Invoke `console_eq_holdings`.  
2. `available` in this report = `available` in `console_eq_holdings` for same ISIN → qty confirmed correct across both systems. Display-only issue on the client's end — advise logout / cache clear / different browser or device.

**1b. Mismatch**  
- `available` in this report ≠ `available` in `console_eq_holdings` for same ISIN → genuine discrepancy. Escalate to human agent per A3 with qty from each tool.

---

### Rule 2 — Stock Present in One Tool but Not the Other

Always resolve by ISIN per A2 before concluding a stock is "missing."

**2a. Stock in Holdings but not in Pseudo**  
1. Invoke `console_eq_holdings`; check for `t1` > 0 on this ISIN → SOT may not reflect until settlement. Route to Rule 8 for timeline.  
2. Invoke `console_eq_holdings`; check for `pending` > 0 on this ISIN → CA credit not yet in SOT. Route to Rule 9.  
3. Neither → check whether the same ISIN appears in pseudo under a different `tradingsymbol` (per A2).  
4. No match by ISIN in pseudo → escalate to human agent per A3.

**2b. Stock in Pseudo but not in Holdings**  
1. Invoke `console_eq_external_trades`; check for a transfer entry awaiting processing for this ISIN.  
2. Check for a CA rearrangement or unclaimed-shares credit not yet processed in Console.  
3. Check whether the stock is suspended / delisted — visible in SOT but removed from active Console holdings.  
4. No clear cause → escalate to human agent per A3.

**2c. Pseudo shows zero / no record, Holdings shows active qty**  
1. Possible transferred-out without reversal entry in Console.  
2. Invoke `console_eq_holdings`; escalate to human agent per A3 with the full holdings list and note that this report shows zero.

---

### Rule 3 — Tradingsymbol Name Differences

1. Apply A2 — compare by ISIN, not `tradingsymbol`.  
2. ISIN matches across tools → same stock, name difference only. No further action needed.  
3. ISIN not found in either tool → escalate to human agent per A3.

---

### Rule 4 — Stock Split Handling

1. Use `total_quantity`, `available`, and `pending` from this report as the source of truth for the split — do not derive quantity from recent trade history.  
2. Invoke `kite_holdings`; check for post-split credit.  
3. Full post-split qty in `kite_holdings` → split credit confirmed. Invoke `console_eq_holdings` and check the avg update timeline.  
4. Partial / not credited → invoke `console_eq_holdings` and check the credit timeline.  
5. Beyond 5 trading days since record date and still uncredited → escalate to human agent per A3.

---

### Rule 5 — Discrepancy Handling

1. `discrepant` > 0 in this report → invoke `console_eq_holdings` and check the `discrepant` qty for the same ISIN.  
2. Follow the discrepancy resolution steps in `console_eq_holdings` for detailed diagnostics and client guidance.

---

### Rule 6 — Transfer-in Overlapping with T1

1. Transfer credit date = T+1 purchase date for the same stock AND the `discrepant` qty appears partial.  
2. Explain: when shares are transferred on the same date as a purchase, the discrepancy qty may appear partial until the T+1 shares settle. Full transferred qty appears correctly the next trading day.

---

### Rule 7 — Safekeep / Frozen Shares

1. Client reports shares visible in their CDSL statement but not in Kite/Console, and mentions "Safekeep Bal" or "Freeze."  
2. SOT / CDSL statements cannot be parsed directly by this tool.  
3. Escalate to human agent (Support team — depository) per A3, including: client ID, `tradingsymbol`, ISIN, and a note that the client's CDSL statement shows a safekeep / frozen balance.

---

### Rule 8 — T1 Handling

- `t1` > 0 in this report → shares purchased yesterday; currently in T+1 settlement. Moves to `available` by end of today; visible in regular holdings from next trading day.

---

### Rule 9 — Pending CA Credit Handling

- `pending` > 0 in this report → qty expected from a corporate action, not yet credited to demat (per A1).  
- Invoke `console_eq_holdings` and check CA-specific timelines:  
  - Bonus → T+2 from record date; tradeable after 4–5 days (temp ISIN → perm ISIN).  
  - Split → invoke `console_eq_holdings` and check the credit timeline; buy average updates 2–3 working days after credit.  
  - Demerger → new entity credit 30–45 days from record date.

---

### Rule 10 — Pledged Qty (`margin`) Handling

- `margin` > 0 in this report → shares pledged as collateral; still in client demat.  
- Invoke `console_eq_holdings` and check pledging behavior details.

---

### Rule 11 — Loan (LAS) Handling

- `loan` > 0 in this report → shares are either pledged via LAS or lent externally to an NBFC (per A1). Escalate to human agent per A3.

---

### Rule 12 — Escalation Triggers

Escalate to human agent immediately for any of the triggers below. Include data per A3.

| Trigger |  
|---|  
| `failure_date` populated (any value) |  
| `tradingsymbol` contains an ISIN-format alphanumeric entry (client asking about this instrument) |
