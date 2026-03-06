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
- Non-DDPI/POA: authorize CDSL T-PIN after 10 AM trigger before 3 PM
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
**then:** Check:
1. `created` within 2 working days of instalment → starts next cycle
2. Was it modified? → **sip_modification_log** (swp_edit)
3. Check **mf_order_history** for SELL order on trigger date → if Failed, check `status_message`
4. No order → **console_mf_holdings** (`margin`, `available`) for pledged/insufficient units
5. All normal, no order → backend issue. Suggest manual redemption.

### Rule 2: Amount Differs
**if:** SWP redeemed different amount
**then:** "SWP calculates units using T-1 NAV, but redemption happens at T day NAV. Small difference is normal."

### Rule 3: T-PIN Required
**if:** SWP order rejected with "units not authorized"
**then:** "CDSL T-PIN authorization needed between 10 AM and 3 PM on trigger day. Authorize and place manual redemption."

### Rule 4: Cross-Tool
- SWP modification history → **sip_modification_log** (swp_edit/swp_delete)
- SWP order status → **mf_order_history**
- Unit availability → **console_mf_holdings** (`available`, `margin`)
