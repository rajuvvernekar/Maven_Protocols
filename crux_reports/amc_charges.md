# amc_charges

## Description

WHEN TO USE:

When clients:
- Ask about AMC (Annual Maintenance Charges) debited from their account
- Question why AMC was charged, the amount, or billing cycle
- To check if an account is BSDA
- Report AMC charged twice or incorrect amount
- Ask about AMC for primary vs secondary demat account
- Dispute AMC saying they have no holdings or aren't using the account
- NRI or non-individual clients asking about AMC charges

TRIGGER KEYWORDS: "AMC charges", "annual maintenance charges", "demat charges", "BSDA", "basic services demat", "AMC deducted", "maintenance charges", "yearly charges", "demat AMC", "AMC waiver", "AMC reversed", "AMC for secondary", "NRI AMC", "account maintenance"

## Protocol


### A1 — AMC Fundamentals

- Report provides AMC charge history by account: charge dates, amounts, BSDA flag, demat type.
- AMC charged quarterly — every 91 days from account opening date.
- Advance payment option: Clients can prepay AMC for 1-5 years. This does not change the quarterly billing cycle or BSDA eligibility assessment.
- Standard AMC: ₹300/year + 18% GST = ₹354/year, in quarterly installments.
- AMC based on the highest holdings value recorded during the billing quarter. `client_holdings` = this peak value for the quarter.
- AMC charged regardless of trading activity or holdings — as long as demat account is active.
- AMC debited from trading account — may create debit balance if insufficient funds.
- AMC is charged separately for each demat account (primary and secondary).

### A2 — AMC Slabs

**BSDA accounts only.** Non-BSDA accounts are charged a flat ₹75/quarter + 18% GST = ₹88.50 regardless of holdings.

| Slab | Holdings Condition (highest value in billing quarter) | AMC (quarterly) | AMC with 18% GST |
|---|---|---|---|
| Slab 1 | ≤ ₹4,00,000 | ₹0 | ₹0 |
| Slab 2 | ₹4,00,001 – ₹10,00,000 | ₹25 | ₹29.50 |
| Slab 3 | > ₹10,00,000 | ₹75 | ₹88.50 |

### A3 — BSDA Eligibility

BSDA eligibility requires **both** conditions:
1. Only 1 demat account registered with the client's PAN across all brokers and depositories, AND
2. Holdings value in the demat account has not exceeded ₹10,00,000.

Both conditions must be met for BSDA status. BSDA status is determined and updated periodically by the depository (CDSL). Clients are enrolled automatically when eligible.

Eligible account types: individual resident accounts only. NRI and non-individual accounts fall under standard (non-BSDA) AMC.

Support article: https://support.zerodha.com/category/account-opening/resident-individual/ri-online/articles/how-to-open-a-basic-service-demat-account-at-zerodha

### A4 — Charge Inference & Response Logic

Determine the client's BSDA status and applicable slab from `charge_after_gst` and `client_holdings` using the inference table below. Respond based on the matching row.

**Inference Table**

| `charge_after_gst` | `client_holdings` | BSDA Status | Slab | Response |
|---|---|---|---|---|
| ₹0 | ≤ ₹4,00,000 | BSDA | Slab 1 | "No AMC was charged for the quarter as your account is eligible for Basic Services Demat Account (BSDA) benefits and your holdings were within the ₹4,00,000 limit." |
| ₹29.50 | ₹4,00,001 – ₹10,00,000 | BSDA | Slab 2 | "AMC of ₹29.50 was charged as your account is eligible for BSDA benefits and your holdings reached ₹[client_holdings] during the quarter." |
| ₹29.50 | ≤ ₹4,00,000 | BSDA | Slab 2 | "AMC of ₹29.50 was charged as your holdings crossed ₹4,00,000 during the billing quarter, even though they may be lower now. AMC is based on the highest holdings value during the quarter." |
| ₹88.50 | ≤ ₹4,00,000 | Not BSDA | Standard | "AMC of ₹88.50 was charged for the quarter. Your account is not categorised as a Basic Services Demat Account (BSDA), so the standard AMC applies." |
| ₹88.50 | ₹4,00,001 – ₹10,00,000 | Not BSDA | Standard | "AMC of ₹88.50 was charged for the quarter. Your account is not categorised as a Basic Services Demat Account (BSDA), so the standard AMC applies." |
| ₹88.50 | > ₹10,00,000 | BSDA | Slab 3 | "AMC of ₹88.50 was charged as your holdings reached ₹[client_holdings] during the quarter, which exceeded ₹10,00,000." |
| Any | Client disputes charge, says investment was less | — | — | "AMC is based on the highest value your holdings reached during the billing quarter, which was ₹[client_holdings]. Even if your current holdings are lower, the charge is calculated on this peak value." |
| Any | Client asks why not BSDA / how to get lower AMC | — | — | "BSDA status is determined by the depository (CDSL). To qualify, you must have only one demat account across all brokers and your holdings must not exceed ₹10,00,000." + link from **A3**. |

**Disambiguation — ₹88.50 with > ₹10L holdings:** Check the inferred BSDA status from the table above. If the status is BSDA (Slab 3), the charge is due to high holdings on a BSDA account. If the status is Not BSDA, the charge is due to standard non-BSDA AMC. When both ₹88.50 and > ₹10L holdings appear, determine which applies by checking whether other indicators (e.g., ₹0 or ₹29.50 charges in adjacent quarters) suggest the account was previously BSDA. If unclear, explain both possibilities to the client: the charge could reflect BSDA Slab 3 or standard non-BSDA AMC, and CDSL determines the categorisation.

### A5 — Field Rules

Determine BSDA status from `charge_after_gst` and `client_holdings` per **A4**. In client-facing language, express BSDA status as "eligible for BSDA benefits" or "not categorised as BSDA."

**Shareable with client:** `charged_date`, `previous_charge_date` (as billing period), `charged_amount`, `charge_after_gst`, `type_of_demat`.

**Conditionally shareable:** `client_holdings` — share with the client when explaining which slab applied or when the client questions the charged amount. For accounts inferred as Not BSDA per **A4**, use for internal verification only.

**Internal reasoning only:** `client_id`, `demat_number`, `demat_only_clientid`, `bsda_flag`. These fields are for internal logic and stay out of client-facing responses.

### A6 — Cross-Reference Protocols

| Topic | Refer to |
|---|---|
| Debit balance from AMC → DPC interest risk | Delayed Payment Charges protocol |
| AMC debit entry on ledger | Ledger Report protocol |


### Preflight (run on every query)

1. Fetch the AMC charges report for the client.
2. Apply field protection per **A5** — shareable fields are used in responses, internal-only fields are used for reasoning only.
3. Determine BSDA status and slab from `charge_after_gst` and `client_holdings` per **A4**.
4. Format all amounts with ₹ and Indian comma notation. Format dates as DD MMM YYYY.

### Routing Tree

```
Query relates to AMC charges →
│
├─ Client asks about an AMC debit
│  → Rule 1
│
├─ Client asks about AMC frequency or timing
│  → Rule 2
│
├─ Client asks about BSDA, questions a specific AMC amount, or asks why AMC was charged
│  → Rule 3
│
├─ Client says no holdings / no activity but AMC charged
│  → Rule 4
│
├─ Client has both primary and secondary demat accounts
│  → Rule 5
│
├─ NRI or non-individual account AMC query
│  → Rule 6
│
├─ AMC created a debit balance
│  → Rule 7 (also apply as add-on to any route above when a debit balance is detected)
│
└─ Client asks about paying AMC annually or in advance
   → Rule 8
```

### Scope

- Address: AMC charge explanations, billing cycles, BSDA eligibility, slab verification, and debit balance impact.
- Share only fields marked as shareable in **A5**. Holdings amounts are used in responses only when explaining a BSDA slab.

### Fallback

If the AMC amount doesn't match any expected slab or the data seems inconsistent → escalate with client ID, charged_date, charged_amount, and the discrepancy.


### Rule 1 — AMC Charge Explanation

1. Respond: "AMC of ₹[charge_after_gst] was charged on [charged_date] for the billing period [previous_charge_date] to [charged_date]. This is for your [Primary/Secondary] demat account."

### Rule 2 — AMC Billing Cycle

1. Respond: "AMC is charged quarterly — every 91 days from your account opening date. The standard AMC is ₹300/year + 18% GST = ₹354/year, charged in quarterly installments." (Per **A1**.)

### Rule 3 — BSDA Eligibility & AMC Slab Explanation

1. Determine BSDA status and slab from `charge_after_gst` and `client_holdings` per **A4**. Respond using the matching row in the **A4** inference table.

2. If the inferred status is Not BSDA and the client asks how to become BSDA-eligible, share BSDA eligibility criteria from **A3** and the support article link.

3. If the client asks about nil-AMC eligibility specifically: the nil-AMC threshold is ₹4,00,000 (Slab 1 per **A2**), applicable only to BSDA accounts. Lead with this figure and clarify that BSDA status is required first.

4. If the account has a debit balance, fetch the ledger report (per **A6**) and include a brief breakdown of all debit entries in the response. This ensures the client is not conflating other debits (settlement charges, DP charges, etc.) with the AMC charge. Explain each debit entry separately before summarising the AMC portion.

### Rule 4 — AMC on Inactive/Zero Holdings Account

1. Respond: "AMC is charged for maintaining an active demat account. This applies even if the account has zero holdings or no recent trading activity." (Per **A1**.)
2. Add: "If you maintain a single demat account with a holdings value of less than ₹4,00,000, you can avail of BSDA (Basic Services Demat Account) benefits, where AMC is not charged. If you have demat accounts with other brokers, closing those accounts so that only one demat is registered against your PAN can help you qualify for BSDA." Share BSDA eligibility criteria from **A3** and the support article link.

### Rule 5 — AMC for Primary and Secondary Demat

1. Respond: "AMC is charged separately for each demat account — primary and secondary. If you see multiple AMC charges in the same period, verify whether they are for different demat accounts using the account type field." (Per **A1**.)

### Rule 6 — NRI / Non-Individual AMC

1. Respond: "NRI and non-individual accounts are not eligible for BSDA. The standard AMC of ₹88.50 per quarter applies." (Per **A3**, **A2**.)

### Rule 7 — AMC Creating Debit Balance

This rule applies as a mandatory add-on whenever a debit balance is present in the account, regardless of the primary routing path. Apply it on top of whichever rule handles the main query.

1. Respond: "The AMC charge of ₹[charge_after_gst] has resulted in a debit balance in your account. A debit balance may attract delayed payment charges (interest at 0.05% per day). To avoid further interest, please add funds to clear the debit balance."
2. For DPC details, refer to the Delayed Payment Charges protocol (per **A6**).

### Rule 8 — Advance AMC Payment

1. If the client asks about paying AMC annually or in advance:
   Respond: "You can prepay your AMC for 1 to 5 years. This prepays future quarterly charges but does not change your billing cycle or BSDA eligibility. Refer to the AMC article for setup details."

2. Always clarify the current AMC rate applicable to their account using Rule 3 before explaining the advance payment option.
