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

## Section A: Reference Data

### A1 — AMC Fundamentals

- AMC charged quarterly — every 91 days from account opening date.
- Advance payment option: Clients can prepay AMC for 1-5 years. This does not change the quarterly billing cycle or BSDA eligibility assessment.
- Standard AMC: ₹75/quarter \+ 18% GST = ₹88.50/quarter (₹354/year).
- AMC based on the highest holdings value recorded during the billing quarter. `client_holdings` = this peak value for the quarter.
- AMC charged regardless of trading activity or holdings — as long as demat account is active.
- AMC debited from trading account — may create debit balance if insufficient funds.
- AMC is charged separately for each demat account (primary and secondary).

### A2 — AMC Slabs

**BSDA accounts only.** Non-BSDA accounts are charged a flat ₹75/quarter \+ 18% GST = ₹88.50 regardless of holdings.

| Slab | Holdings Condition (highest value in billing quarter) | AMC (quarterly) | AMC with 18% GST |
|---|---|---|---|
| Slab 1 | ≤ ₹4,00,000 | ₹0 | ₹0 |
| Slab 2 | ₹4,00,001 – ₹10,00,000 | ₹25 | ₹29.50 |
| Slab 3 | > ₹10,00,000 | ₹75 | ₹88.50 |

### A3 — BSDA Eligibility

BSDA eligibility requires **both** conditions:
1. Only 1 demat account registered with the client's PAN across all brokers and depositories, AND
2. Holdings value in the demat account has not exceeded ₹10,00,000.

- Both conditions must be met for BSDA status. BSDA status is determined and updated periodically by the depository (CDSL). Clients are enrolled automatically when eligible.

- Eligible account types: individual resident accounts only. NRI and non-individual accounts fall under standard (non-BSDA) AMC.

Support article: see **A5**

### A4 — Field Rules
**Shareable with client:**

| Field | Interpretation |
|---|---|
| `charged_date` | Date of the AMC charge |
| `previous_charge_date` | Previous charge date — communicate as the start of the billing period |
| `charged_amount` | Charged amount before GST |
| `charge_after_gst` | Final charged amount including GST |
| `type_of_demat` | Type of demat account (BSDA or regular) |
| `client_holdings` | Client's holding value — share when explaining which slab applied or when client questions the charged amount; use for internal verification only for non-BSDA accounts per Rule 1 |

**Non-shareable:**

| Field | Interpretation |
|---|---|
| `client_id` | Internal client identifier |
| `demat_number` | Demat account number |
| `demat_only_clientid` | Internal identifier for demat-only accounts |
| `bsda_flag` | BSDA status flag — used for Rule 1 classification |

### A5 — Links

| Topic | URL |
|---|---|
| Upfront / advance AMC payment | https://support.zerodha.com/category/account-opening/resident-individual/ri-charges/articles/upfront-amc |
| BSDA account opening | https://support.zerodha.com/category/account-opening/resident-individual/ri-online/articles/how-to-open-a-basic-service-demat-account-at-zerodha |

### A6 — Cross-Reference Protocols

| Topic | Refer to |
|---|---|
| Debit balance from AMC → DPC interest risk | Delayed Payment Charges protocol |
| AMC debit entry on ledger | Ledger Report protocol |

---

## Section B: Decision Flow

### Routing

```
Route by scenario
   ├─ Client questions a specific AMC charge or asks why AMC was charged → Rule 1
   ├─ Client asks about BSDA status, slab, or how to reduce / avoid AMC → Rule 2
   ├─ Client has zero holdings or no trading activity but AMC still charged → Rule 3
   ├─ Client sees multiple AMC charges in the same period → Rule 4
   ├─ NRI or non-individual account — AMC eligibility query → Rule 5
   ├─ AMC charge created a debit balance → Rule 6
   └─ Client asks about prepaying or paying AMC upfront → Rule 7
```

### Fallback

If the AMC amount doesn't match any expected slab or the data seems inconsistent → escalate with client ID, `charged_date`, `charged_amount`, and the discrepancy.

---

## Section C: Rules

### Rule 1 — AMC Charge Explanation

- Communicate: AMC of `charge_after_gst` was charged on `charged_date` for the billing period `previous_charge_date` to `charged_date`, for the demat account per `type_of_demat`.

-Use the inference table below to determine BSDA status, applicable slab, and what to communicate about the charge.

**Inference Table**

| `charge_after_gst` | `client_holdings` | BSDA Status | Slab | What to communicate |
|---|---|---|---|---|
| ₹0 | ≤ ₹4,00,000 | BSDA | Slab 1 | No AMC charged — BSDA Slab 1 applies; holdings within ₹4,00,000 limit |
| ₹29.50 | ₹4,00,001 – ₹10,00,000 | BSDA | Slab 2 | AMC of ₹29.50 — BSDA Slab 2; holdings reached `client_holdings` during the quarter |
| ₹29.50 | ≤ ₹4,00,000 | BSDA | Slab 2 | AMC of ₹29.50 — holdings crossed ₹4,00,000 during the billing quarter; charge is based on peak value, not current holdings |
| ₹88.50 | ≤ ₹4,00,000 | Not BSDA | Standard | AMC of ₹88.50 — account not on BSDA; standard AMC applies |
| ₹88.50 | ₹4,00,001 – ₹10,00,000 | Not BSDA | Standard | AMC of ₹88.50 — account not on BSDA; standard AMC applies |
| Any | Client disputes amount; says investment was less | — | — | Charge is based on peak holdings value during the billing quarter (`client_holdings`), not current value |
| Any | Client asks why not BSDA / how to get lower AMC | — | — | Share BSDA eligibility criteria and BSDA support article from **A5** |

**If `charge_after_gst` = ₹88.50 and `client_holdings` > ₹10,00,000:**
1. Check adjacent quarters in the report for ₹0 or ₹29.50 charges.
2. If found → BSDA Slab 3; holdings exceeded ₹10,00,000 during the quarter.
3. If not found → standard non-BSDA AMC applies.
4. If the report has insufficient history → communicate both possibilities and note that CDSL determines the BSDA categorisation.

### Rule 2 — BSDA Eligibility & AMC Slab Explanation

-Determine BSDA status and slab from `charge_after_gst` and `client_holdings` per Rule 1 inference table. Communicate the matching row's determination.

-If the client asks how to become BSDA-eligible: share eligibility criteria from **A3** and the BSDA support article from **A5**.

-If the client asks about nil-AMC eligibility specifically: nil AMC applies under BSDA Slab 1 (holdings ≤ ₹4,00,000 per **A2**); BSDA status is required first.

### Rule 3 — AMC on Inactive / Zero Holdings Account

-AMC is charged for maintaining an active demat account regardless of trading activity or holdings (per **A1**).

-If the client asks how to avoid AMC: communicate BSDA eligibility conditions from **A3** — single demat across all brokers and depositories, holdings not exceeding ₹4,00,000 for nil AMC (Slab 1 per **A2**). Share the BSDA support article from **A5**.

### Rule 4 — Multiple AMC Charges

-Check `primary_dp_status`, `secondary_dp_status`, and `tertiary_dp_status` from ‘get_all_client_data’. Communicate one AMC charge per active demat account — each active demat is billed separately per **A1**.

### Rule 5 — NRI / Non-Individual AMC

- Check `category` and `client_acc_type` from ‘get_all_client_data’ per **A4**..

-If any value other than "Individual" → NRI or non-individual; not eligible for BSDA (per **A3**). Standard AMC of ₹88.50 per quarter applies (per **A2**).

### Rule 6 — AMC Debit Balance

-Communicate that AMC was debited from the trading account (per **A1**). Invoke `delayed_payment_charges` to check for any DPC interest on the resulting debit balance.

### Rule 7 — Advance AMC Payment

-Communicate the applicable AMC rate (via Rule 2) before explaining the prepayment option.

-Clients can prepay AMC for 1 to 5 years. Prepayment covers future quarterly charges but does not change the billing cycle or BSDA eligibility (per **A1**). Share the advance AMC article from **A5**.
