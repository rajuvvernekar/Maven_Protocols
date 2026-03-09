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

<knowledge_base>

<facts>
- Report provides AMC charge history by account: charge dates, amounts, BSDA flag, demat type
- AMC charged quarterly (every 91 days from account opening date)
- Standard AMC: ₹300/year + 18% GST = ₹354/year, in quarterly installments
- AMC based on highest holdings value during the billing quarter — not current value
- client_holdings = highest holdings value recorded during the billing quarter
- BSDA eligibility (post 1 Sep 2024): only 1 demat account across all brokers/depositories AND holdings never exceeded ₹10,00,000 during the quarter
- NRI and non-individual accounts not eligible for BSDA
- AMC charged regardless of trading activity or holdings — as long as demat account is active
- AMC debited from trading account — may create debit balance if insufficient funds
</facts>

<amc_slabs>
- Slab 1: holdings ≤ ₹4,00,000 → ₹0 AMC
- Slab 2: holdings ₹4,00,001–₹10,00,000 → ₹25/quarter + 18% GST = ₹29.50
- Slab 3: holdings > ₹10,00,000 OR non-BSDA account → ₹75/quarter + 18% GST = ₹88.50
</amc_slabs>

<field_usage>
  <share>charged_date | previous_charge_date (as billing period) | charged_amount | charge_after_gst | type_of_demat</share>
  <banned>client_id | demat_number | demat_only_clientid | client_holdings (use internally) | bsda_flag (use internally)</banned>
</field_usage>

</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
**NEVER expose:** `client_id`, `demat_number`, `demat_only_clientid`, `client_holdings` (use internally), `bsda_flag` (use internally)
**Share:** `charged_date`, `previous_charge_date` (as billing period), `charged_amount`, `charge_after_gst`, `type_of_demat`

### Rule 1: AMC Charge Explanation
**if:** Client asks about an AMC debit
**then:** "AMC of ₹[charge_after_gst] was charged on [charged_date] for the billing period [previous_charge_date] to [charged_date]. This is for your [Primary/Secondary] demat account."

### Rule 2: AMC Billing Cycle
**if:** Client asks about AMC frequency or timing
**then:** "AMC is charged quarterly — every 91 days from your account opening date. The standard AMC is ₹300/year + 18% GST = ₹354/year, charged in quarterly installments."

### Rule 3: BSDA Eligibility & AMC Slab Explanation
**if:** Client asks about BSDA or why a specific AMC amount was charged

**Step 1 — Infer slab from charged_amount (pre-GST):**
- ₹0 → Slab 1: holdings ≤ ₹4,00,000 — full BSDA benefit applied
- ₹25 (₹29.50 with GST) → Slab 2: holdings were ₹4,00,001–₹10,00,000 during the quarter
- ₹75 (₹88.50 with GST) → Slab 3: holdings exceeded ₹10,00,000 during the quarter OR account is non-BSDA

**Step 2 — Cross-check with client_holdings internally, then respond:**
- client_holdings ≤ ₹4L AND charged ₹0 → "No AMC was charged as your holdings were within the ₹4,00,000 limit."
- client_holdings ₹4L–₹10L AND charged ₹29.50 → "AMC of ₹29.50 was charged as your holdings were ₹[client_holdings]."
- client_holdings > ₹10L AND charged ₹88.50 → "AMC of ₹88.50 was charged as your holdings were ₹[client_holdings]."
- client_holdings ≤ ₹4L BUT charged ₹88.50 → "AMC of ₹88.50 was charged because your account is not eligible for BSDA. To qualify for BSDA, you must have only one demat account across all brokers and depositories, and your total holdings value must not have exceeded ₹10,00,000 during the quarter."
- client_holdings ₹4L–₹10L BUT charged ₹88.50 → "AMC of ₹88.50 was charged because your account is not eligible for BSDA. To qualify for BSDA, you must have only one demat account across all brokers and depositories, and your total holdings value must not have exceeded ₹10,00,000 during the quarter."
- client_holdings ≤ ₹4L BUT charged ₹29.50 → "AMC of ₹29.50 was charged as your holdings crossed ₹4,00,000 during the quarter."

**BSDA eligibility criteria (for client education):**
- Only 1 demat account across all brokers and depositories (verify via CAS)
- Total holdings value must not have exceeded ₹10,00,000 during the quarter

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
