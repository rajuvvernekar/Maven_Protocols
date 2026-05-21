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

TAGS: charges

## Protocol

# AMC CHARGES PROTOCOL

---

## Section A: Reference Data

### A1 — AMC Fundamentals

- Report provides AMC charge history by account: charge dates, amounts, BSDA flag, demat type.
- AMC charged quarterly — every 91 days from account opening date.
- Advance payment option: Clients can prepay AMC for 1–5 years. This does not change the quarterly billing cycle or BSDA eligibility assessment.
- Standard AMC: ₹300/year + 18% GST = ₹354/year, in quarterly installments.
- AMC based on the highest holdings value recorded during the billing quarter. `client_holdings` = this peak value for the quarter.
- AMC charged regardless of trading activity or holdings — as long as demat account is active.
- AMC debited from trading account — may create debit balance if insufficient funds.
- AMC is charged separately for each demat account (primary and secondary).
- Format all amounts with ₹ and Indian comma notation. Format dates as DD MMM YYYY.

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

BSDA status is determined and updated periodically by the depository (CDSL). Clients are enrolled automatically when eligible.

Eligible account types: individual resident accounts only. NRI and non-individual accounts fall under standard (non-BSDA) AMC.

### A4 — Charge Inference Table

Infer BSDA status and applicable slab from `charge_after_gst` and `client_holdings`.

| `charge_after_gst` | `client_holdings` | Inferred BSDA Status | Inferred Slab |
|---|---|---|---|
| ₹0 | ≤ ₹4,00,000 | BSDA | Slab 1 |
| ₹29.50 | ₹4,00,001 – ₹10,00,000 | BSDA | Slab 2 |
| ₹29.50 | ≤ ₹4,00,000 | BSDA | Slab 2 (holdings peaked above ₹4,00,000 during the quarter) |
| ₹88.50 | ≤ ₹4,00,000 | Not BSDA | Standard |
| ₹88.50 | ₹4,00,001 – ₹10,00,000 | Not BSDA | Standard |
| ₹88.50 | > ₹10,00,000 | Ambiguous — see note | Slab 3 or Standard |

**Disambiguation note — ₹88.50 with > ₹10L holdings:** This combination is consistent with both BSDA Slab 3 and standard non-BSDA AMC. Presence of ₹0 or ₹29.50 charges in adjacent quarters indicates prior BSDA status (Slab 3 applies). Absence of such charges suggests non-BSDA status (Standard applies).

### A5 — Field Rules

In client-facing language, express BSDA status as "eligible for BSDA benefits" or "not categorised as BSDA."

| Field | Classification |
|---|---|
| `charged_date` | Shareable |
| `previous_charge_date` | Shareable (use as billing period start) |
| `charged_amount` | Shareable |
| `charge_after_gst` | Shareable |
| `type_of_demat` | Shareable |
| `client_holdings` | Shareable when explaining which slab applied or when the client questions the charged amount; internal only for Not BSDA accounts |
| `client_id` | Internal only |
| `demat_number` | Internal only |
| `demat_only_clientid` | Internal only |
| `bsda_flag` | Internal only |

### A6 — Links

| Topic | URL |
|---|---|
| BSDA account opening / eligibility | https://support.zerodha.com/category/account-opening/resident-individual/ri-online/articles/how-to-open-a-basic-service-demat-account-at-zerodha |
| Upfront / advance AMC payment | https://support.zerodha.com/category/account-opening/resident-individual/ri-charges/articles/upfront-amc |

### A7 — Cross-Reference Protocols

| Topic | Protocol |
|---|---|
| Debit balance from AMC → DPC interest risk | Delayed Payment Charges protocol |
| AMC debit entry on ledger | Ledger Report protocol |

---

## Section B: Decision Flow

> Before routing: apply field rules from **A5**. Infer BSDA status and slab from `charge_after_gst` and `client_holdings` per **A4**.

```
Query relates to AMC charges →
│
├─ Client asks what AMC was charged / wants a charge explanation → Rule 1
├─ Client asks about billing cycle or charge frequency → Rule 2
├─ Client questions the charged amount, asks why BSDA / why not BSDA, or asks about their slab → Rule 3
├─ Client says no holdings / no activity but AMC was charged → Rule 4
├─ Client has both primary and secondary demat / multiple AMC charges in the same period → Rule 5
├─ Client account is NRI or non-individual → Rule 6
├─ AMC has created a debit balance → Rule 7 (mandatory add-on to all routes above when a debit balance is detected)
└─ Client asks about paying AMC upfront or annually → Rule 8
```

**Fallback:** If the AMC amount does not match any expected slab or data appears inconsistent, escalate with client ID, `charged_date`, `charged_amount`, and a description of the discrepancy.

---

## Section C: Rules

### Rule 1 — AMC Charge Explanation

1. Respond: "AMC of ₹[charge_after_gst] was charged on [charged_date] for the billing period [previous_charge_date] to [charged_date]. This is for your [Primary/Secondary] demat account."

2. Check for a debit balance in the trading account resulting from the AMC charge. If present → apply Rule 7.

### Rule 2 — AMC Billing Cycle

1. Respond: "AMC is charged quarterly — every 91 days from your account opening date. The standard AMC is ₹300/year + 18% GST = ₹354/year, charged in quarterly installments."

### Rule 3 — BSDA Eligibility and AMC Slab Explanation

1. Infer BSDA status and slab from **A4**. Share `client_holdings` per field rules in **A5**.

2. Respond based on the inferred combination:

   | Inferred Status | Inferred Slab | Response |
   |---|---|---|
   | BSDA | Slab 1 | "No AMC was charged for the quarter as your account is eligible for Basic Services Demat Account (BSDA) benefits and your holdings were within the ₹4,00,000 limit." |
   | BSDA | Slab 2 — holdings ₹4,00,001–₹10,00,000 | "AMC of ₹29.50 was charged as your account is eligible for BSDA benefits and your holdings reached ₹[client_holdings] during the quarter." |
   | BSDA | Slab 2 — holdings ≤ ₹4,00,000 but peaked above | "AMC of ₹29.50 was charged as your holdings crossed ₹4,00,000 during the billing quarter, even though they may be lower now. AMC is based on the highest holdings value during the quarter." |
   | Not BSDA | Standard | "AMC of ₹88.50 was charged for the quarter. Your account is not categorised as a Basic Services Demat Account (BSDA), so the standard AMC applies." |
   | BSDA | Slab 3 | "AMC of ₹88.50 was charged as your holdings reached ₹[client_holdings] during the quarter, which exceeded ₹10,00,000." |

3. For the ambiguous ₹88.50 + > ₹10L case, apply the disambiguation logic from **A4**. If still unclear after checking adjacent quarters, explain both possibilities: the charge could reflect BSDA Slab 3 or standard non-BSDA AMC, and CDSL determines the categorisation.

4. If the client disputes the charge and says their investment was lower: "AMC is based on the highest value your holdings reached during the billing quarter, which was ₹[client_holdings]. Even if your current holdings are lower, the charge is calculated on this peak value."

5. If the client asks why they are not BSDA-eligible or how to qualify: share eligibility criteria from **A3** and the BSDA support article from **A6**.

6. If the client asks specifically about nil-AMC eligibility: the nil-AMC threshold is ₹4,00,000 (Slab 1 per **A2**), applicable only to BSDA accounts. Lead with this figure and clarify that BSDA status is required first.

7. If the account has a debit balance: include a brief breakdown of all debit entries per the Ledger Report protocol (**A7**), explaining each debit entry separately (settlement charges, DP charges, etc.) before summarising the AMC portion.

### Rule 4 — AMC on Inactive / Zero Holdings Account

1. Respond: "AMC is charged for maintaining an active demat account. This applies even if the account has zero holdings or no recent trading activity."

2. Add: "If you maintain a single demat account with a holdings value of less than ₹4,00,000, you can avail of BSDA (Basic Services Demat Account) benefits, where AMC is not charged. If you have demat accounts with other brokers, closing those accounts so that only one demat is registered against your PAN can help you qualify for BSDA." Share eligibility criteria from **A3** and the BSDA support article from **A6**.

### Rule 5 — AMC for Primary and Secondary Demat

1. Respond: "AMC is charged separately for each demat account — primary and secondary. If you see multiple AMC charges in the same period, verify whether they are for different demat accounts using the account type field."

### Rule 6 — NRI / Non-Individual AMC

1. Respond: "NRI and non-individual accounts are not eligible for BSDA. The standard AMC of ₹88.50 per quarter applies."

### Rule 7 — AMC Creating Debit Balance

This rule applies as a mandatory add-on whenever a debit balance is present in the account, regardless of the primary routing path.

1. Check cashier payins to verify whether the client has added funds today or recently.

2. If no recent payin → respond: "The AMC charge of ₹[charge_after_gst] has resulted in a debit balance in your account. A debit balance may attract delayed payment charges (interest at 0.05% per day). To avoid further interest, please add funds to clear the debit balance."

3. If a recent payin is found → respond: "We can see that you have added ₹[payin_amount] on [payin_date]. This should cover the debit balance created by the AMC charge."

4. For DPC details, refer to the Delayed Payment Charges protocol per **A7**.

### Rule 8 — Advance AMC Payment

1. First apply Rule 3 to confirm the current AMC rate applicable to the account.

2. Respond: "You can prepay your AMC for 1 to 5 years. This prepays future quarterly charges but does not change your billing cycle or BSDA eligibility." Share the upfront AMC article from **A6**.
