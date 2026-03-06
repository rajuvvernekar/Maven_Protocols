# console_mf_pseudo_holdings

## Description

WHEN TO USE:

When need to:
- Compare Pseudo Holdings with Console MF Holdings to detect discrepancy
- Investigate holdings mismatch between the two reports
- Verify if failure_date is populated (PnL calculation failure)
- Check buy average / buy value as per Pseudo Holdings
- NFO units not visible — check if credited in Pseudo Holdings

TRIGGER KEYWORDS: "discrepancy", "units don't match", "fix discrepancy", "PnL calculation failed", "coin"

## Protocol

# CONSOLE MF PSEUDO HOLDINGS PROTOCOL

## Knowledge Base

<knowledge_base>

<facts>
- Second holdings report used alongside console_mf_holdings
- If available/discrepant units differ between the two reports → mismatch needs investigation
- failure_date populated → PnL calculation failed due to unit/trade mismatch → escalate
- discrepant > 0 → units exist but no matching trade entries in Tradebook
- Transferred-in units appear as discrepant until external entries added
- Scheme name field is `tradingsymbol`
</facts>

<field_usage>
  <share>tradingsymbol (as fund name) | buy_average (if asked) | buy_value (if asked) | dividend_type (if asked) | margin (if asked) | loan (if asked)</share>
  <internal>failure_date (CRITICAL) | available | discrepant (CRITICAL)</internal>
  <banned>client_id | isin | instrument_id | t1 | pending</banned>
</field_usage>

</knowledge_base>
---
## Business Rules

### Rule 0: Field Protection
Never share `<banned>` fields. Use `<internal>` fields for reasoning only.

### Rule 1: Failure Date — Immediate Escalation
**if:** `failure_date` populated
**then:** Escalate to human immediately. "Data inconsistency requires backend investigation for [tradingsymbol]."

### Rule 2: Discrepancy Detection
**if:** `discrepant` > 0
**then:** Compare with **console_mf_holdings** `discrepant`:
- Both show discrepant → no matching trade entry. Check **console_mf_external_trades** for missing entries.
- Transferred from another platform → "Add external trades: Console → Portfolio → Holdings → fund → Add External Trade."
- NFO recently allotted → "May auto-resolve in 48-72 hours."

### Rule 3: Mismatch Between Reports
**if:** `available` here ≠ `available` in **console_mf_holdings**
**then:** Check **console_mf_tradebook** for missing trade entries. If trade entry exists but mismatch persists → escalate.

### Rule 4: Buy Average / Investment Value
**if:** Customer questions buy average
**then:** If `buy_average` or `buy_value` differs from **console_mf_holdings** → likely missing external trade entries. If investment not updated → may be settlement delay (liquid T day, non-liquid T+1).

### Rule 5: Cross-Tool
- Missing trade entries → **console_mf_tradebook** + **console_mf_external_trades**
- Holdings comparison → **console_mf_holdings** (compare `available`, `discrepant`)
