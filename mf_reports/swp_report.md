# swp_report

## Description

WHEN TO USE:

When customer asks about:
- SWP status, schedule, amount
- SWP not triggered on expected date
- Next/last SWP date
- SWP redemption amount differs from expected

TRIGGER KEYWORDS: "SWP", "systematic withdrawal", "withdrawal plan", "SWP not triggered", "coin"

## Protocol

# SWP REPORT PROTOCOL

## Knowledge Base

<knowledge_base>
<facts>
- SWP triggers at 10:00 AM on scheduled date
- Units = instalment_amount ÷ T-1 NAV; actual redemption at T day NAV (may differ)
- Non-DDPI/POA: authorize CDSL T-PIN after 10 AM trigger before 3 PM on trigger day. If missed, order is rejected.
- Enabling DDPI avoids T-PIN requirement every cycle — recommend as permanent fix
- SWP created within 2 working days of next instalment → starts next cycle
- Scheme name field is `fund`
</facts>

<field_usage>
  <share>fund | frequency | instalment_day | instalment_amount (if asked) | next_instalment | last_instalment | created</share>
  <internal>swp_id | completed_instalments</internal>
  <banned>tradingsymbol | transaction_type (deprecated) | tag</banned>
</field_usage>
</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
Never share `<banned>` fields. Use `<internal>` fields for reasoning only.

### Rule 1: SWP Not Triggered
**if:** Customer says SWP didn't trigger
**then:** Complete ALL steps sequentially before concluding:
1. `created` within 2 working days of instalment → starts next cycle. Inform client.
2. Was it modified? → Get `swp_id` from this report → pass as `sip_id` to **sip_modification_log** (swp_edit). If modified within T-2 of trigger → skipped this cycle. Inform client.
3. Check **mf_order_history** for SELL order on trigger date:
   - Order found, status = Failed → check `status_message` for rejection reason (T-PIN, free_qty_less, etc.) → apply relevant rule.
   - Order found, status = Redeemed → SWP did trigger. Clarify with client.
   - No order found → proceed to Step 4.
4. **CRITICAL — always complete this step:** Check pledged units via **console_mf_pseudo_holdings** (`margin`) and available units via **console_mf_holdings** (`available`):
   - `margin` > 0 → units pledged. "Some of your units are pledged and cannot be redeemed. Please unpledge first: Console → Portfolio → Holdings → [fund] → Unpledge."
   - `available` = 0 or insufficient → units not available for redemption. Inform client.
5. All checks normal, no order found → backend issue. Suggest manual redemption.

### Rule 2: Amount Differs
**if:** SWP redeemed different amount than expected
**then:** "The final amount credited to your bank account may differ from your intended SWP amount because the calculation uses the previous day's NAV (T-1), but the actual redemption uses the current day's NAV (T). You receive more if the current day's NAV is higher, and less if it is lower."

### Rule 3: T-PIN Required
**if:** SWP order rejected with "units not authorized"
**then:** "CDSL T-PIN authorization must be completed on the same day the SWP triggers, between 10:00 AM and 3:00 PM. Since it was not completed on time, the order was rejected. Please place a fresh manual redemption request for this cycle.
To avoid this every cycle, we recommend enabling DDPI on your account — this allows automatic debit of units without requiring T-PIN authorization each time."
