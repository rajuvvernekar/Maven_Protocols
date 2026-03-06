# stp_report

## Description

WHEN TO USE:

When customer asks about:
- STP status, configuration, schedule
- STP not transferring funds between schemes
- STP source fund (SWP leg) or target fund (SIP leg)

TRIGGER KEYWORDS: "STP", "systematic transfer", "transfer between funds", "coin"

## Protocol

# STP REPORT PROTOCOL

## Knowledge Base

<knowledge_base>
<facts>
- STP = SWP (redeem from source) + SIP (invest in target via mandate)
- SWP leg: 10:10 AM; SIP leg: NACH 11AM/1PM/6PM or UPI 11:10AM/1:10PM/6:10PM
- Requires active mandate for SIP leg
- Up to 5 target funds per STP
- STP target fund must already be in client's holdings. Cannot select a fund not currently held.
- Coin web only (not app)
- Non-DDPI/POA: authorize CDSL T-PIN on the SAME DAY the SWP leg is placed, before 3 PM. If missed, order is rejected.
</facts>

<field_usage>
  <share>created | modified | view_sips (target funds) | view_swp (source fund)</share>
  <internal>status (deprecated bool: true=active, false=paused/cancelled — say active/inactive) | fund_source | mandate_type</internal>
  <banned>id | name | tag | trigger_status</banned>
</field_usage>
</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
Never share `<banned>` fields. Use `<internal>` fields for reasoning only.

### Rule 1: STP Not Working
**if:** STP not transferring funds
**then:** Check:
1. `status` = false → inactive. Share status.
2. SWP leg → **swp_report** (via `view_swp`). Check trigger/next instalment.
3. SIP leg → **sip_report** (via `view_sips`). Check status + mandate linkage.
4. Mandate → if SIP leg has no mandate, purchase leg won't execute.
5. T-PIN → SWP order rejected with "units unauthorized"? → "CDSL T-PIN authorization must be completed on the same day the SWP order is placed, before 3:00 PM. Since it was not completed on the order date, the order was rejected. Place a fresh redemption request. To avoid this in future, enable DDPI."
6. Units → **console_mf_holdings** for source fund availability.

### Rule 2: Partially Executing
**if:** One leg works, other doesn't
**then:** SWP works but SIP fails → mandate or payment issue. SWP fails → fix SWP first (T-PIN, units).

### Rule 3: Web Only
**if:** Can't find STP on app
**then:** "STP is available on Coin web (coin.zerodha.com) only, not the app."

### Rule 4: Cross-Tool
- SWP leg details → **swp_report**
- SIP leg details → **sip_report**
- STP modification history → **sip_modification_log** (stp_edit/stp_delete)
- Order execution → **mf_order_history**
- Source fund units → **console_mf_holdings**
