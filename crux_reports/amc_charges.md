# amc_charges

## Description

WHEN TO USE:

- Client asks about AMC (Annual Maintenance Charges) debited from their account
- Client questions why AMC was charged, amount, or billing cycle
- Agent needs to verify AMC charge history, dates, and BSDA applicability
- Client asks if their account qualifies for BSDA (Basic Services Demat Account) benefits
- Client reports AMC charged twice or incorrect amount
- Client asks about AMC for primary vs secondary demat account
- Client disputes AMC saying they have no holdings or aren't using the account
- NRI or non-individual client asks about AMC charges

TRIGGER KEYWORDS: "AMC charges", "annual maintenance charges", "demat charges", "BSDA", "basic services demat", "AMC deducted", "maintenance charges", "yearly charges", "demat AMC", "AMC waiver", "AMC reversed", "AMC for secondary", "NRI AMC", "account maintenance"

## Protocol

# AMC CHARGES PROTOCOL

## Business Rules

### Rule 0: Field Protection
**NEVER expose:** `client_id`, `demat_number`, `demat_only_clientid`, `client_holdings`
**Share:** `charged_date`, `previous_charge_date` (as billing period), `charged_amount`, `charge_after_gst`, `bsda_flag`, `type_of_demat`

### Rule 1: AMC Charge Explanation
**if:** Client asks about an AMC debit
**then:** "AMC (Account Maintenance Charges) of ₹[charge_after_gst] was charged on [charged_date] for the billing period [previous_charge_date] to [charged_date]. This is for your [Primary/Secondary] demat account.

BSDA benefit applied: [Yes/No]. [If No and client asks why → see Rule 3]"

### Rule 2: AMC Billing Cycle
**if:** Client asks about AMC frequency or timing
**then:** "AMC is charged quarterly. Each charge covers the period from the previous charge date to the current charge date. The standard AMC is ₹300/year + 18% GST = ₹354/year, charged in quarterly installments."

### Rule 3: BSDA Eligibility
**if:** Client asks about BSDA or why BSDA benefit not applied
**then:** "BSDA (Basic Services Demat Account) offers reduced or zero AMC if:
- Your total holdings value is ≤ ₹4 lakhs
- You have only one demat account across all depositories and DPs

If your bsda_flag shows 'No', it means either your holdings exceeded ₹4 lakhs during the billing period or you hold multiple demat accounts. BSDA status is determined by CDSL based on these criteria."

If client says they meet criteria but flag shows NO → check CDSL BSDA flag vs Zerodha flag. If mismatch → escalate.

### Rule 4: AMC on Inactive/Zero Holdings Account
**if:** Client says they have no holdings or no trading activity but AMC was charged
**then:** "AMC is charged for maintaining the demat account, regardless of whether you hold any securities or have any trading activity. As long as the demat account is active, AMC will apply.

If you don't plan to use the account, you may consider closing the demat account to stop future AMC charges."

### Rule 5: AMC for Primary and Secondary Demat
**if:** Client has both primary and secondary demat accounts
**then:** "AMC is charged separately for each demat account — primary and secondary. If you see multiple AMC charges in the same period, verify whether they are for different demat accounts using the account type field."

### Rule 6: NRI / Non-Individual AMC
**if:** Client is NRI or non-individual and questions AMC amount
**then:** "AMC charges for NRI and non-individual accounts may differ from standard individual account rates. These are as per Zerodha's tariff. Non-individual accounts are not eligible for BSDA benefits."

### Rule 7: AMC Creating Debit Balance
**if:** AMC charged created a negative balance in the account
**then:** "The AMC charge of ₹[charge_after_gst] has resulted in a debit balance in your account. A debit balance may attract delayed payment charges (interest at 0.05% per day). To avoid further interest, please add funds to clear the debit balance."

### Rule 8: Escalation Criteria
**if:** Any of the following:
- BSDA flag mismatch between CDSL and Zerodha (Rule 3)
- Two AMC charges for same demat account within same quarter
- AMC amount doesn't match standard tariff
**then:** Escalate with: client ID, charged_date, charge_after_gst, bsda_flag, type_of_demat, and specific issue.
