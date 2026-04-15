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

## Protocol

# CONSOLE EQ PSEUDO HOLDINGS PROTOCOL

---

## Section A: Reference Data

---

### A1 — Fundamentals

This tool looks up a client's SOT-based (Statement of Transaction) equity holdings — an independent source of truth separate from the tradebook-backed `console_eq_holdings`. It is primarily used for **cross-validation** of holdings quantities. The two systems should match; discrepancies indicate data issues requiring investigation.


---

### A2 — Field Usage Rules

**Shareable fields:**

`tradingsymbol` | `isin` | `buy_average` | `buy_value` | `available` | `t1` | `margin` | `pending` | `discrepant` | `loan`

**Internal-only fields** (use for reasoning; communicate outcomes in plain language):

`instrument_id` | `failure_date`

**Client-facing terminology:**

| Internal Term | Client-Facing Alternative |
|---|---|
| pseudo holdings | "your holdings" / "our records" |
| SOT / SOT data | (describe the data in plain language, e.g., "our records") |
| failure date | (omit — use for internal escalation only) |
| pending | "being processed for credit" or "yet to be credited" |
| Any internal tool or system name | (describe the outcome, not the tool) |

---

### A3 — Cross-Validation Logic Summary

| Scenario | Meaning | Action |
|---|---|---|
| Pseudo `available` = Holdings `available` (same ISIN) | Qty confirmed correct across both systems | Display issue only — advise logout/cache clear |
| Pseudo `available` ≠ Holdings `available` (same ISIN) | Genuine discrepancy | Escalate with both values |
| Stock in Holdings but not in Pseudo | T1 settlement, CA credit not in SOT yet, or sync issue | Check t1/CA first; if no match on ISIN → escalate |
| Stock in Pseudo but not in Holdings | Transfer/CA credit not yet processed, or suspended/delisted stock | Check external trades; if no clear cause → escalate |
| Pseudo shows zero/no record but Holdings shows active | Possible transferred-out without reversal | Escalate with full holdings list |
| Tradingsymbol mismatch between tools | NSE vs BSE naming, post-CA rename, or temp ISIN | Compare by ISIN, not tradingsymbol |

---

### A4 — Discrepancy Resolution Path

Shares with `discrepant` > 0 follow the same resolution as `console_eq_holdings` — shares received via transfer, gift, IPO, ESOP, or CA rearrangement without matching tradebook entry. Guide client to: **Console → Portfolio → Holdings → View discrepancy → Add trade.** Refer to `console_eq_holdings` protocol Rule 5 for detailed instructions.

---

### A5 — Escalation Data Template

When escalating, always include: **client ID, tradingsymbol(s), ISIN(s), qty from each tool (pseudo_holdings and console_eq_holdings), and screenshots if available.**

---

## Section B: Decision Flow

---

### Preflight (run on every query)

```
1. Check `failure_date`
   └─ Has any value → ESCALATE TO SM with client ID, tradingsymbol,
      failure_date. STOP.
```

### Route

```
Intent / Condition                                          → Rule
──────────────────────────────────────────────────────────────────────
Qty validation — both tools match                           → Rule 1
Qty validation — mismatch found                             → Rule 2
Stock in Holdings but not in Pseudo                         → Rule 3
Stock in Pseudo but not in Holdings                         → Rule 4
Pseudo shows zero but Holdings shows active holdings        → Rule 5
Tradingsymbol name mismatch between tools                   → Rule 6
Stock split — qty/price query                               → Rule 7
Discrepant qty in pseudo holdings                           → Rule 8
Transfer-in overlapping with T1 purchase                    → Rule 9
Safekeep / frozen shares (CDSL statement mismatch)          → Rule 10
```

### Scope

- This tool is used for cross-validation against `console_eq_holdings`. Address the client's query about holdings quantity accuracy, display discrepancies, or system mismatches.
- Use **A2** field rules and client-facing terminology in all client communication.
- Do not expose the existence of two separate systems to the client.

### Fallback

If no route matches, cross-reference with `console_eq_holdings` and `console_eq_external_trades` for additional context. If no root cause is found, escalate per **A5**.

---

## Section C: Rules

---

### Rule 1 — Qty Validation: Match Found

1. Confirm `available` qty in `console_eq_pseudo_holdings` = `available` qty in `console_eq_holdings` for same ISIN.
2. Quantity is correct across both systems.
3. If client still reports a display issue → Your holdings quantity of [available] shares of [tradingsymbol] is confirmed correct in our records. Please try logging out and back in, clearing your browser cache, or using a different browser/device..

---

### Rule 2 — Qty Validation: Mismatch Found

1. Confirm `available` qty in `console_eq_pseudo_holdings` ≠ `available` qty in `console_eq_holdings` for same ISIN.
2. Genuine discrepancy detected.
3. We've identified a discrepancy in your [tradingsymbol] holdings and have raised this for investigation. Our team will review and update your holdings. You'll be notified once resolved.. Do not tell the client "there is a system mismatch."
4. Escalate per **A5** with qty from each tool.

---

### Rule 3 — Stock in Holdings but Not in Pseudo

1. Check `console_eq_holdings` for the stock:
   a. `t1` > 0 → shares bought yesterday, SOT may not reflect until settlement. Your shares are in T+1 settlement and will appear once settled..
   b. Shares yet to be credited from corporate action → CA credit not yet in SOT. Advise client to wait.
   c. Neither a nor b → possible sync issue or tradingsymbol name difference. Check if same ISIN exists under a different tradingsymbol in pseudo_holdings (e.g., company renamed, NSE vs BSE symbol per **A3**).
   d. If no match on ISIN → Escalate per **A5**.

---

### Rule 4 — Stock in Pseudo but Not in Holdings

1. SOT shows shares but tradebook-backed system does not. Common causes:
   a. Shares transferred in but not yet reflected in Console → check `console_eq_external_trades` for transfer entry awaiting processing.
   b. Corporate action credit (rearrangement, unclaimed shares) not yet processed.
   c. Suspended/delisted stock visible in SOT but removed from active Console holdings.
2. We can see your [tradingsymbol] shares in our records. They may be awaiting system processing. We're investigating and will update you..
3. If no clear cause → Escalate per **A5**.

---

### Rule 5 — Pseudo Shows Zero but Holdings Shows Active

1. `console_eq_pseudo_holdings` has no record for client OR all quantities are 0 AND `console_eq_holdings` shows active holdings.
2. Possible transferred-out shares without reversal entry in Console.
3. Escalate per **A5** with: client ID, full list of holdings showing in `console_eq_holdings`, note that pseudo_holdings shows zero.

---

### Rule 6 — Tradingsymbol Name Mismatch

1. Compare by ISIN, not tradingsymbol. Stocks can appear under different names across tools:
   - NSE vs BSE naming (e.g., SPEL vs SPICELEC)
   - Post-corporate action rename (e.g., old name in SOT, new name in Console)
   - Temporary ISIN for bonus/rights shares
2. If ISIN matches across tools → same stock, name difference only.
3. If ISIN not found in either tool → Escalate per **A5**.

---

### Rule 7 — Stock Split (Qty / Price Query)

1. Use `total_quantity`, `available`, and `pending` from `console_eq_pseudo_holdings` as the basis for explaining the split — do not derive quantity from recent trade history.
2. Check `kite_holdings` to verify whether split shares have already been credited.
3. If `kite_holdings` shows the full post-split quantity → For split share responses, use the templates from `console_eq_holdings` protocol (**A13-R11** for credited, **A13-R12** for still processing). (credited template).
4. If `kite_holdings` does not show the full post-split quantity AND Console shows shares still being processed → For split share responses, use the templates from `console_eq_holdings` protocol (**A13-R11** for credited, **A13-R12** for still processing). (processing template).
5. If more than 5 trading days since record date AND split shares still not credited → Escalate per **A5**.

---

### Rule 8 — Discrepant Qty in Pseudo Holdings

1. `discrepant` > 0 in `console_eq_pseudo_holdings`.
2. Same logic as `console_eq_holdings` discrepancy — guide client to self-resolution path per **A4**.
3. Refer to `console_eq_holdings` protocol Rule 5 for detailed discrepancy resolution instructions.

---

### Rule 9 — Transfer-In with Overlapping T1

1. Transfer credit date = T1 purchase date for same stock AND discrepant qty appears partial.
2. When shares are transferred on the same date as a purchase, the discrepancy quantity may appear partial until the T1 shares settle. The full transferred quantity will show correctly after settlement (next trading day)..

---

### Rule 10 — Safekeep / Frozen Shares

1. Client reports shares visible in their CDSL statement but not in Kite/Console, and mentions "Safekeep Bal" or "Freeze".
2. Maven cannot download or read the client's SOT/CDSL statement directly.
3. We've noted that your [tradingsymbol] shares appear to be in safekeeping or frozen status in the depository records. We're escalating this to our depository team for investigation. They will review and update you on the status..
4. Escalate to **Support team** with: client ID, tradingsymbol, ISIN, and note that client's CDSL statement shows safekeep/frozen balance.

