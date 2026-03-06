# console_eq_pseudo_holdings

## Description

WHEN TO USE:

- Agent needs to cross-reference or validate equity holdings quantities against SOT (Statement of Transactions) data
- Client reports quantity mismatch between Kite and Console
- Client says holdings visible on one platform but not the other
- Agent needs to verify if a discrepancy is genuine (system-level) or display-only
- Agent needs to confirm whether transferred/credited shares are reflected in SOT
- Agent needs a second source of truth for holdings qty before escalating
- Client's Console shows inflated or zero holdings that don't match Kite

TRIGGER KEYWORDS: "quantity mismatch", "Kite shows different", "Console shows different", "not matching", "cross-check holdings", "verify holdings", "SOT", "pseudo", "holdings don't match", "wrong quantity on Kite", "wrong quantity on Console", "shares visible on Kite but not Console", "shares visible on Console but not Kite"

## Protocol

# Console EQ PSEUDO HOLDINGS PROTOCOL

## Business Rules

### Rule 0: Failure Date Check
**if:** `failure_date` field has any value (not blank)
**then:** Escalate to support manager immediately with client ID, tradingsymbol, and failure_date. Do not attempt to resolve.

### Rule 1: Field Protection
**NEVER expose:** `instrument_id`, `failure_date`
**ALWAYS share when relevant:** `tradingsymbol`, `isin`, `buy_average`, `buy_value`, `available`, `t1`, `margin`, `pending`, `discrepant`, `loan`
**NEVER say:** "pseudo holdings", "SOT data", "failure date", or reference internal tool/system names to the client.

### Rule 2: Qty Validation — Match Found
**if:** `available` qty in `console_eq_pseudo_holdings` = `available` qty in `console_eq_holdings` for same ISIN
**then:** Quantity is confirmed correct across both systems. If client still reports a display issue on Kite or Console, it is cosmetic — advise: "Your holdings quantity of [available] shares of [tradingsymbol] is confirmed correct in our records. Please try logging out and back in, clearing your browser cache, or using a different browser/device."

### Rule 3: Qty Validation — Mismatch Found
**if:** `available` qty in `console_eq_pseudo_holdings` ≠ `available` qty in `console_eq_holdings` for same ISIN
**then:** Genuine discrepancy detected. Escalate with: client ID, tradingsymbol, ISIN, qty from console_eq_pseudo_holdings, qty from console_eq_holdings, and any relevant screenshots.

Do NOT tell the client "there is a system mismatch." Say: "We've identified a discrepancy in your [tradingsymbol] holdings and have raised this for investigation. Our team will review and update your holdings. You'll be notified once resolved."

### Rule 4: Stock Not Found in Pseudo but Exists in Console EQ Holdings
**if:** Stock appears in `console_eq_holdings` but not in `console_eq_pseudo_holdings`
**then:** Check:
- `t1` > 0 in console_eq_holdings → shares bought yesterday, SOT may not reflect until settlement. "Your shares are in T+1 settlement and will appear once settled."
- `pending` > 0 → corporate action credit pending, not yet in SOT.
- Neither → possible sync issue or tradingsymbol name difference. Check if same ISIN exists under a different tradingsymbol in pseudo_holdings (e.g., company renamed, NSE vs BSE symbol). If no match on ISIN → escalate.

### Rule 5: Stock Found in Pseudo but Not in Console EQ Holdings
**if:** Stock appears in `console_eq_pseudo_holdings` but not in `console_eq_holdings`
**then:** SOT shows shares but tradebook-backed system doesn't recognize them. Common causes:
- Shares transferred in but not yet reflected in Console → check `console_eq_external_trades` for pending transfer entry.
- Corporate action credit (rearrangement, unclaimed shares) not yet processed.
- Suspended/delisted stock visible in SOT but removed from active Console holdings.

Advise: "We can see your [tradingsymbol] shares in our records. They may be pending system processing. We're investigating and will update you." If no clear cause → escalate.

### Rule 6: SOT Shows Zero but Console/Kite Shows Holdings
**if:** `console_eq_pseudo_holdings` has no record for client OR all quantities are 0 AND `console_eq_holdings` shows active holdings
**then:** Possible transferred-out shares without reversal entry in Console. Escalate with: client ID, full list of holdings showing in console_eq_holdings, note that pseudo_holdings shows zero.

### Rule 7: Tradingsymbol Name Mismatch
**if:** Agent cannot find stock in one tool but client confirms they hold it
**then:** Compare by ISIN (not tradingsymbol). Stocks can appear under different names across tools:
- NSE vs BSE naming (e.g., SPEL vs SPICELEC)
- Post-corporate action rename (e.g., old name in SOT, new name in Console)
- Temporary ISIN for bonus/rights shares

If ISIN matches across tools → same stock, name difference only. If ISIN not found in either tool → escalate.

### Rule 8: Discrepant Qty in Pseudo Holdings
**if:** `discrepant` > 0 in `console_eq_pseudo_holdings`
**then:** Same logic as `console_eq_holdings` discrepancy — shares received via transfer, gift, IPO, ESOP, or corporate action rearrangement without matching tradebook entry. Guide client to add purchase details via Console → Portfolio → Holdings → View discrepancy → Add trade. Refer to `console_eq_holdings` protocol Rule 5 for detailed discrepancy resolution instructions.

### Rule 9: Transfer-In with Overlapping T1
**if:** Transfer credit date = T1 purchase date for same stock AND discrepant qty appears partial
**then:** "When shares are transferred on the same date as a purchase, the discrepancy quantity may appear partial until the T1 shares settle. The full transferred quantity will show correctly after settlement (next trading day)."

### Rule 10: Safekeep / Frozen Shares
**if:** Client reports shares visible in their CDSL statement but not in Kite/Console, and mentions "Safekeep Bal" or "Freeze"
**then:** Maven cannot download or read the client's SOT/CDSL statement directly. Escalate to DP team with: client ID, tradingsymbol, ISIN, and note that client's CDSL statement shows safekeep/frozen balance.

Response to client: "We've noted that your [tradingsymbol] shares appear to be in safekeeping or frozen status in the depository records. We're escalating this to our depository team for investigation. They will review and update you on the status."

### Rule 11: Escalation Criteria
**if:** Any of the following:
- `failure_date` has a value (Rule 0)
- Qty mismatch between tools after ISIN-level comparison (Rule 3)
- SOT shows zero but Console shows holdings (Rule 6)
- Console shows zero but SOT shows holdings with no clear cause (Rule 5)
- Stock not found by ISIN in either tool (Rule 7)
**then:** Escalate with: client ID, tradingsymbol(s), ISIN(s), qty from each tool, and screenshots if available.
