# client_retention_dates

## Description

WHEN TO USE:

- Client asks why funds were transferred out during quarterly settlement (QS) and wants breakdown
- Client reports QS amount doesn't match their expected balance
- Agent needs to verify how much was released, retained, and why during a settlement cycle
- Client asks what "max retention amount" means or why some funds were retained
- Client asks about obligations or margin retained during settlement
- Agent needs to trace settlement-wise payout history for a client
- Client disputes partial QS payout — expected full balance but only received partial amount
- Client asks about settlement for different companies (Zerodha, Zerodha Securities, Zerodha Commodities)

TRIGGER KEYWORDS: "quarterly settlement breakdown", "settlement payout details", "retention amount", "funds retained", "why partial settlement", "settlement breakdown", "max retention", "settlement obligation", "funds released amount", "QS payout amount", "settlement history", "settlement cycle details"

## Protocol

# CLIENT RETENTION DATES PROTOCOL

## Business Rules

### Rule 0: Field Protection
**NEVER expose:** `client_id`, `company`, `securities_released`, `eq_margin`, `turnover`, `previous_obligation`, `security_obligation`, `previous_security_obligation`, `unencumbered_balance`, `collateral_amount`, `mode_of_settlement`
**ALWAYS share when relevant:** `settlement_date`, `funds_released`, `max_retention_amount`, `margin` (as "margin retained"), `obligation` (as "pending obligation")

### Rule 1: QS Payout Breakdown
**if:** Client asks how much was paid out during QS and why
**then:** "Here's the breakdown for the settlement on [settlement_date]:
- Funds released to your bank: ₹[funds_released]
- Margin retained for open positions: ₹[margin]
- Pending obligations: ₹[obligation]
- Maximum retention amount: ₹[max_retention_amount]

The maximum retention amount is the total your broker can retain per SEBI regulations to cover your open positions and pending obligations. The remaining balance was released to your registered bank account."

### Rule 2: Partial QS Payout
**if:** Client expected full balance payout but received less
**then:** "Not all funds may be released during quarterly settlement. Funds are retained for:
- Open F&O or commodity positions requiring margin (₹[margin] retained)
- Pending trade obligations from recent settlements (₹[obligation] pending)
- Collateral adjustments

Your actual payout was ₹[funds_released]. The retained amount of ₹[max_retention_amount] covers your current margin and obligation requirements."

### Rule 3: Zero Payout
**if:** funds_released = 0 for a settlement date
**then:** "No funds were released during the [settlement_date] quarterly settlement. Your entire balance was retained because:
- Margin required for open positions: ₹[margin]
- Pending obligations: ₹[obligation]

These amounts exceed or equal your available balance, so there were no free funds to release. Once your positions are closed or obligations settled, the funds become available."

### Rule 4: QS Payout Not Received in Bank
**if:** Client says QS funds not received in bank despite funds_released > 0
**then:** "The settlement report shows ₹[funds_released] was released on [settlement_date]. QS payouts are typically credited to your registered bank account within 1-2 working days of the settlement date.

If it has been more than 3 working days and the amount has not been credited, please check with your bank. If still not received, we'll investigate further." (Escalate after 3 working days)

### Rule 5: Multiple Company Settlements
**if:** Client has positions across segments (equity, commodity, currency)
**then:** "Settlement happens separately for each segment:
- Equity and F&O: processed under Zerodha
- Commodity: processed under Zerodha Commodities

The settlement amounts and dates may differ per segment. Your total QS payout is the sum of releases across all segments."

Check both company entries if applicable.

### Rule 6: Obligation Explanation
**if:** Client asks what "obligation" means in settlement context
**then:** "Obligation is the net amount due from or to you for recent trades that are in the settlement cycle. For example, if you bought shares on the trading day before settlement, the payment obligation for those shares is still pending. This amount is retained until the trade settles (T+1)."

### Rule 7: Escalation Criteria
**if:** Any of the following:
- Funds released > 0 but not credited to bank after 3 working days (Rule 4)
- Max retention amount seems incorrect — exceeds visible margin + obligations
- No settlement entry exists for a QS date when client was eligible
**then:** Escalate with: client ID, settlement_date, funds_released, max_retention_amount, and specific issue.
