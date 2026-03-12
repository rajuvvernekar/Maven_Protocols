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
- STP target fund must already be in client's holdings. STP cannot be created if target fund is not currently held — client must make a lumpsum purchase in the target fund first.
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
2. Modified recently? → Get `id` from this report → pass as `sip_id` to **sip_modification_log** for stp_edit/stp_delete events. If modified within T-2 of trigger → skipped this cycle.
3. SWP leg → **swp_report** (via `view_swp`). Check trigger/next instalment.
4. SIP leg → **sip_report** (via `view_sips`). Check status + mandate linkage.
5. Mandate → check **mandate_report** for mandate status. If SIP leg has no mandate, purchase leg won't execute.
6. T-PIN → SWP order rejected with "units unauthorized"? → "CDSL T-PIN authorization must be completed on the same day the SWP order is placed, before 3:00 PM. Since it was not completed on the order date, the order was rejected. Place a fresh redemption request. To avoid this in future, enable DDPI."
7. Units → **console_mf_pseudo_holdings** for source fund margin/pledged check; **console_mf_holdings** for `available` units.

### Rule 2: Partially Executing
**if:** Client reports STP not fully working, OR any STP execution query
**then:** ALWAYS check both legs independently before concluding:
1. Check **mf_order_history** for SWP leg (variety = SWP) on trigger date → confirm status.
2. Check **mf_order_history** for SIP leg (variety = SIP) on same date → confirm status.
3. Diagnose based on findings:
   - SWP executed, SIP failed → mandate or payment issue on purchase leg. Check **sip_report** mandate linkage + **mandate_debit_report**.
   - SWP failed, SIP not triggered → fix SWP first (T-PIN, pledged units, insufficient units).
   - Both failed → check source fund units via **console_mf_pseudo_holdings** (margin/pledged) and **console_mf_holdings** (`available`) and T-PIN status.
**CRITICAL:** Never conclude STP is working based on the SWP leg alone. Both legs must be verified independently.

### Rule 3: Web Only
**if:** Can't find STP on app
**then:** "STP is available on Coin web (coin.zerodha.com) only, not the app."

### Rule 5: Target Fund Not in Holdings
**if:** Client cannot create STP, OR setup fails because target fund is not available to select
**then:** "STP cannot be created unless the target fund is already in your holdings. Please make a lumpsum purchase in [target fund] first. Once the units are allotted and appear in your Coin holdings, you can proceed to set up the STP."
Note: STP allows up to 5 target funds — all must be existing holdings before they can be selected.

### Rule 6: STP Setup Error — Source Fund Navigation
**if:** Client reports an error when trying to set up an STP, OR cannot find the Create STP option, AND target fund is already in holdings (Rule 5 does not apply)
**then:**
1. Check **console_mf_holdings** for the intended source fund (the fund from which money will be transferred):
   - `available` units > 0 AND `margin` = 0 → source fund is ready. Issue is likely navigation. Guide client: "To set up an STP on Coin web, go to Dashboard → Mutual Funds → select the **source fund** (the fund you want to transfer FROM) in your holdings → click the menu icon → select Create STP. The STP must be initiated from the source fund — not the target fund."
   - `margin` > 0 → pledged units present. "Please unpledge units in [source fund] first before creating an STP: Console → Portfolio → Holdings → [fund] → Unpledge. Once unpledged, try creating the STP again."
   - `available` = 0 → no free units. "The fund you are trying to transfer from has no available units. Please check the source fund selection."
2. If error persists after correct navigation → escalate with screenshot.
