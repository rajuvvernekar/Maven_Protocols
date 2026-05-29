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

- AMC charged quarterly — every 91 days from account opening date.
- Advance payment option: Clients can prepay AMC for 1–5 years. This does not change the quarterly billing cycle or BSDA eligibility assessment.
- Standard AMC: ₹300/year + 18% GST = ₹354/year, in quarterly installments.
- AMC based on the highest holdings value recorded during the billing quarter. `client_holdings` = this peak value for the quarter.
- AMC charged regardless of trading activity or holdings — as long as demat account is active.
- AMC debited from trading account — may create debit balance if insufficient funds.
- AMC is charged separately for each demat account (primary and secondary).
- `charged_date` is the date the AMC charge is assessed. The actual ledger debit entry is recorded on a separate date.
- Debit balance created by AMC attracts DPC interest at 0.05% per day until cleared.

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
| `charged_date` | Shareable — assessment date; actual debit date is the ledger entry date for the billing period |
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
| NRI PIS AMC and DP charges | https://support.zerodha.com/category/account-opening/nri-account-opening/nri-charges/articles/pis-amc-dp-charges |

---

## Section B: Decision Flow

### Routing

```
Route by scenario
   ├─ Client asks what AMC was charged / wants a charge explanation → Rule 1
   ├─ Client asks about billing cycle or charge frequency → Rule 2
   ├─ Client questions the charged amount, asks why BSDA / why not BSDA, or asks about their slab → Rule 3
   ├─ Client says no holdings / no activity but AMC was charged → Rule 4
   ├─ Client has both primary and secondary demat / multiple AMC charges in the same period → Rule 5
   ├─ Client account is NRI or non-individual → Rule 6
   ├─ AMC has created a debit balance → Rule 7 (mandatory add-on to all routes above when a debit balance is detected)
   ├─ Client asks about paying AMC upfront or annually → Rule 8
   ├─ Client claims AMC debited after closing other demat accounts → Rule 9
   └─ NRI PIS account — AMC or DP charge payment query → Rule 10
```

### Fallback

If the query does not match any route above → escalate.

---

## Section C: Rules

### Rule 1 — AMC Charge Explanation

1. Invoke `ledger_report` and locate the AMC debit entry for the billing period `previous_charge_date` to `charged_date`. Use the ledger entry date as the actual debit date.

2. Communicate: AMC amount (`charge_after_gst`), billing period (`previous_charge_date` to `charged_date`), actual debit date from ledger, and whether it is for the primary or secondary demat account.

3. Check for a debit balance in the trading account resulting from the AMC charge. If present → apply Rule 7.

---

### Rule 2 — AMC Billing Cycle

1. Communicate: billing cycle and standard AMC rate per **A1**.

---

### Rule 3 — BSDA Eligibility and AMC Slab Explanation

1. Infer BSDA status and slab from **A4**. Share `client_holdings` per field rules in **A5**.

2. Communicate based on the inferred combination:

   | Inferred Status | Inferred Slab | Communicate |
   |---|---|---|
   | BSDA | Slab 1 | Account is BSDA-eligible; no AMC charged as holdings were within the ₹4,00,000 limit per **A2**. |
   | BSDA | Slab 2 — holdings ₹4,00,001–₹10,00,000 | Account is BSDA-eligible; AMC per **A2** Slab 2 charged because holdings reached `client_holdings` during the quarter. |
   | BSDA | Slab 2 — holdings ≤ ₹4,00,000 but peaked above | Account is BSDA-eligible; AMC per **A2** Slab 2 charged because holdings crossed ₹4,00,000 during the billing quarter. AMC is based on peak holdings value per **A1**. |
   | Not BSDA | Standard | Account is not categorised as BSDA; standard AMC per **A2** applies. |
   | BSDA | Slab 3 | Account is BSDA-eligible; AMC per **A2** Slab 3 charged because holdings reached `client_holdings`, exceeding ₹10,00,000. |

3. For the ambiguous ₹88.50 + > ₹10L case, apply the disambiguation logic from **A4**. If still unclear after checking adjacent quarters, communicate both possibilities: the charge could reflect BSDA Slab 3 or standard non-BSDA AMC, and CDSL determines the categorisation.

4. If the client disputes the charge and says their investment was lower: communicate that AMC is based on the peak holdings value during the billing quarter per **A1**; share `client_holdings` as the peak value that triggered the charge.

5. If the client asks why they are not BSDA-eligible or how to qualify: share eligibility criteria from **A3** and the BSDA support article from **A6**.

6. If the client asks specifically about nil-AMC eligibility: the nil-AMC threshold is ₹4,00,000 (Slab 1 per **A2**), applicable only to BSDA accounts; BSDA status is required first.

7. If the account has a debit balance: include a brief breakdown of all debit entries per the Ledger Report protocol, explaining each debit entry separately (settlement charges, DP charges, etc.) before summarising the AMC portion.

8. If the client cites a specific demat account number: check `primary_dp_id` and `secondary_dp_id` from `get_all_client_data`. If the cited number does not match either → communicate that Zerodha can only address charges for the Zerodha-linked demat account; direct the client to the respective broker for charges on other accounts.

---

### Rule 4 — AMC on Inactive / Zero Holdings Account

1. Communicate: AMC is charged for maintaining an active demat account regardless of holdings or trading activity per **A1**.

2. Communicate: BSDA eligibility criteria per **A3** — a single demat account across all brokers with holdings under ₹4,00,000 qualifies for nil AMC. Share the BSDA support article from **A6**.

---

### Rule 5 — AMC for Primary and Secondary Demat

1. Communicate: AMC is charged per demat account per **A1**; if multiple charges appear in the same period, confirm each is for a different demat account using the `type_of_demat` field.

---

### Rule 6 — NRI / Non-Individual AMC

1. Communicate: NRI and non-individual accounts are not BSDA-eligible per **A3**; standard AMC per **A2** applies.

2. If account is NRI PIS → apply Rule 10 for payment mechanics.

---

### Rule 7 — AMC Creating Debit Balance

1. Invoke `cashier_payins` to check for recent fund additions.

2. If no recent payin → communicate: AMC charge (`charge_after_gst`) has created a debit balance; DPC interest at 0.05% per day per **A1** applies until cleared. Advise client to add funds.

3. If a recent payin is found → communicate: payin amount and date observed; confirm it should cover the debit balance from the AMC charge.

4. For DPC details, refer to the Delayed Payment Charges protocol.

---

### Rule 8 — Advance AMC Payment

1. First apply Rule 3 to confirm the current AMC rate applicable to the account.

2. Communicate: advance payment covers 1–5 years of future quarterly charges without changing the billing cycle or BSDA eligibility. Share the upfront AMC article from **A6**.

---

### Rule 9 — BSDA Claim After Closing Other Demat Accounts

Determine BSDA status per Rule 3.
- Non-BSDA: communicate that if all other demat accounts registered against their PAN have been closed, BSDA status will apply from the upcoming billing quarter once CDSL updates the status; the current charge reflects the BSDA status at the time of billing. Zerodha cannot verify closure of other demat accounts — advise the client to confirm directly with CDSL.
- BSDA: communicate that upcoming AMC will be per the applicable BSDA slab in **A2**.

---

### Rule 10 — NRI PIS AMC and DP Charge Payment

From `get_all_client_data`, confirm all three conditions are true: `client_acc_type` is NRO, NRE, or NRI; `bo_sub_status` contains "RepatriableWith"; `pis_bank_1_name` or `pis_bank_2_name` is populated.

If confirmed:
- Communicate: AMC and DP charges must be paid by adding funds directly to the Kite trading account via NEFT or IMPS. The PIS bank account does not settle these charges through the PIS account.
- Share the NRI PIS AMC and DP charges article from **A6**.
