# delayed_payment_charges

## Description

WHEN TO USE:

- Client asks about delayed payment charges (DPC) or interest debited from their account
- Client questions why interest was charged despite having a positive balance (excess collateral scenario)
- Client asks for breakdown of how DPC was calculated for a specific period
- Agent needs to verify debit balance interest, margin shortfall interest, or excess collateral interest
- Client reports DPC amount doesn't match their own calculation
- Client asks about 0.05% per day or interest rate on debit balance
- Client asks how to avoid delayed payment charges
- Client disputes DPC saying they had sufficient collateral/liquid holdings

TRIGGER KEYWORDS: "delayed payment charges", "DPC", "interest charges", "debit balance interest", "margin shortfall interest", "excess collateral interest", "collateral interest", "0.05% per day", "interest deducted", "why interest charged", "penalty interest", "shortfall charge", "how to avoid interest"

## Protocol

# DELAYED PAYMENT CHARGES PROTOCOL

## PROTOCOL

<knowledge_base>

<facts>
- DPC report provides daily breakdown of interest calculation for a selected date range
- Three types of interest: debit_balance_interest, margin_shortfall_interest, excess_collateral_interest
- Debit balance interest: 0.05% per day on negative ledger balance (18.25% annualized)
- Excess collateral interest: 0.035% per day on collateral used beyond available cash to meet margin
- Margin shortfall interest: charged when margin required exceeds total available (cash + collateral)
- Interest calculated daily including weekends and holidays (based on position held, not trading days)
- DPC debited to ledger monthly (typically first week of following month)
- interest_amount = total daily interest = sum of debit_balance_interest + margin_shortfall_interest + excess_collateral_interest
- Positive ledger balance does NOT mean zero DPC — if margin requirement exceeds cash, excess collateral is used and interest applies
- 50% of margin must come from cash; remaining 50% can come from collateral — if cash < 50% of margin, excess collateral interest applies
- Liquid collateral (LIQUIDBEES etc.) valued at 100% for margin; equity collateral valued at ~50% (haircut-dependent)
</facts>

<field_usage>
  <share>interest_amount (as "interest charged") | collateral_amount (if asked) | liquidbees_collateral (if asked) | margin_shortfall_interest (as "margin shortfall interest") | excess_collateral_interest (as "excess collateral utilization interest")</share>
  <banned>client_id | posting_date (internal) | company | ledger_balance | unapplied_interest | margin_blocked | margin_after_collateral | qs_payout_amount | debit_balance_interest (use excess_collateral_interest instead per doc instruction) | excess_collateral_utilized | remaining_collateral_amount | remaining_cash_collateral_amount</banned>
</field_usage>

<interest_calculation>
  <debit_balance>
    <condition>ledger_balance less than 0 (debit)</condition>
    <rate>0.05% per day (0.0005 × abs(ledger_balance))</rate>
    <field>debit_balance_interest</field>
  </debit_balance>
  <excess_collateral>
    <condition>ledger_balance positive BUT margin_blocked exceeds cash + collateral available → collateral used beyond cash to cover margin</condition>
    <rate>0.035% per day (0.00035 × excess_collateral_utilized)</rate>
    <field>excess_collateral_interest</field>
    <explanation>When margin requirement exceeds your cash balance, the system uses your pledged collateral to cover the gap. Interest is charged on the collateral amount used beyond your available cash.</explanation>
  </excess_collateral>
  <margin_shortfall>
    <condition>Total margin required exceeds cash + collateral combined</condition>
    <rate>Charged on shortfall amount</rate>
    <field>margin_shortfall_interest</field>
  </margin_shortfall>
</interest_calculation>

<cross_reference>
  <ledger_report>DPC debit entry appears on ledger — use to show the actual debit posting</ledger_report>
  <pledge_request_report>Verify collateral holdings if client disputes collateral amount used in DPC</pledge_request_report>
</cross_reference>

<escalation_triggers>
  <dpc_mismatch>DPC report values don't match ledger debit entry for the same period</dpc_mismatch>
  <collateral_wrong>Collateral amount in DPC report differs from pledged holdings report for same date</collateral_wrong>
  <margin_wrong>Margin blocked in DPC doesn't match ledger "With Margin" margin entries</margin_wrong>
  <waiver_request>Client requests waiver, reversal, or reimbursement of DPC for any reason</waiver_request>
</escalation_triggers>

</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
**NEVER expose:** `client_id`, `posting_date`, `company`, `ledger_balance`, `unapplied_interest`, `margin_blocked`, `margin_after_collateral`, `qs_payout_amount`, `excess_collateral_utilized`, `remaining_collateral_amount`, `remaining_cash_collateral_amount`
**Share with client:** `interest_amount` (as "interest charged"), `excess_collateral_interest` (as "excess collateral utilization interest"), `margin_shortfall_interest`, `collateral_amount` and `liquidbees_collateral` (only if client specifically asks about collateral).

**CRITICAL:** Use `excess_collateral_interest` field value when sharing interest charged with client. Do NOT share `debit_balance_interest` field value separately — use `interest_amount` as the total.

### Rule 1: Debit Balance Interest Explanation
**if:** Client asks why interest was charged AND ledger_balance < 0 (debit) for the period
**then:** "Interest was charged because your account had a debit balance during this period. Interest is calculated at 0.05% per day on the debit balance amount. The total interest for [period] was ₹[interest_amount].

To avoid debit balance interest, ensure your account maintains a positive cash balance by adding funds or reducing positions."

### Rule 2: Excess Collateral Interest Explanation
**if:** Client asks why interest was charged AND ledger_balance > 0 BUT excess_collateral_interest > 0
**then:** "Even though your account had a positive cash balance, interest was charged because your margin requirement exceeded your available cash. Your pledged collateral was used to cover the additional margin, and interest of ₹[excess_collateral_interest] was charged on the collateral amount utilized beyond your cash balance.

This happens when less than 50% of your total margin requirement is covered by cash. The interest rate is 0.035% per day on the excess collateral utilized."

### Rule 3: Margin Shortfall Interest Explanation
**if:** margin_shortfall_interest > 0
**then:** "A margin shortfall was detected — your total available margin (cash + collateral) was less than the required margin for your positions. Interest of ₹[margin_shortfall_interest] was charged on the shortfall amount.

To avoid this, ensure sufficient funds or pledged collateral to cover your position margins."

### Rule 4: DPC Calculation Breakdown
**if:** Client asks for detailed calculation or says amount doesn't match
**then:** Provide daily breakdown:
"Your interest charges for [period]:
- Total interest charged: ₹[sum of interest_amount across days]
- This includes [debit balance interest / excess collateral utilization interest / margin shortfall interest — whichever applies]

Interest is calculated daily (including weekends and holidays when positions are held) and debited to your ledger monthly."

**if:** Client provides their own calculation and it differs → verify the daily values from the report. If the report values are correct per the calculation formula → explain that interest accrues on weekends/holidays too. If report values themselves seem incorrect → escalate.

### Rule 5: Weekend/Holiday Interest
**if:** Client asks why interest charged for Saturday/Sunday or holidays
**then:** "Interest on debit balances, margin shortfalls, and excess collateral utilization is calculated for every calendar day, including weekends and market holidays. This is because your positions and margin obligations continue to exist even when markets are closed."

### Rule 6: How to Avoid DPC
**if:** Client asks how to avoid delayed payment charges
**then:**
- Debit balance: "Maintain a positive cash balance by adding funds before charges or obligations are debited."
- Excess collateral: "Ensure at least 50% of your margin requirement is covered by cash (not just collateral). You can add funds or reduce your F&O positions to lower margin requirements."
- Margin shortfall: "Ensure total margin (cash + collateral) covers your position requirements. Add funds or pledge additional approved securities."

### Rule 7: DPC vs MTF Interest
**if:** Client confuses DPC with MTF interest
**then:** "Delayed payment charges and MTF interest are different:
- DPC is charged on debit balances, margin shortfalls, or excess collateral utilization in your trading account (0.05% per day on debit balance, 0.035% on excess collateral).
- MTF interest is charged on the funded amount for shares bought under Margin Trading Facility (0.04% per day).

Your MTF interest details are available in the MTF Interest Statement on Console."

### Rule 8: Monthly DPC Debit on Ledger
**if:** Client asks when DPC is debited or sees a lump sum interest debit on ledger
**then:** "Delayed payment charges are calculated daily but debited to your ledger as a monthly total, typically in the first week of the following month. The entry will appear in your ledger as an interest charge."

For the ledger entry → use `ledger_report` to show the actual debit posting.

### Rule 9: Collateral Amount Dispute
**if:** Client says their collateral was sufficient but DPC was still charged
**then:** Check the collateral_amount and liquidbees_collateral values.
"Your total collateral on that date was ₹[collateral_amount] (including ₹[liquidbees_collateral] in liquid collateral). However, only up to 50% of margin can be covered by equity collateral — the remaining must come from cash or liquid collateral. If your cash was insufficient to cover the remaining 50%, excess collateral interest applies."

If client still disputes → compare with `pledge_request_report` for the same dates. If mismatch → escalate.

### Rule 10: Escalation Criteria
**if:** Any of the following:
- DPC report values don't match ledger debit entry amount for same period
- Collateral amount in DPC report differs significantly from pledged holdings for same date
- Margin blocked in DPC report doesn't match ledger "With Margin" entries
- Client has valid calculation showing different amount from report
**then:** Escalate with: client ID, date range, specific discrepancy, and DPC report values.

### Rule 11: DPC Waiver or Reversal Request
**if:** Client requests a waiver, reversal, or reimbursement of delayed payment charges for any reason (including AMC-induced debit, lack of notification, or account inactivity)
**then:** ESCALATE TO AGENT. Do not attempt to approve, deny, or calculate reversal amounts. Escalate with: client ID, charge dates, interest amounts, and client's stated reason for dispute.
