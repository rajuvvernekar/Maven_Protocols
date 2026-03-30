# amc_charges

## Description

WHEN TO USE:

When clients:
- Ask about AMC (Annual Maintenance Charges) debited from their account
- Question why AMC was charged, the amount, or billing cycle
- Ask if their account qualifies for BSDA (Basic Services Demat Account) benefits
- Report AMC charged twice or incorrect amount
- Ask about AMC for primary vs secondary demat account
- Dispute AMC saying they have no holdings or aren't using the account
- NRI or non-individual clients asking about AMC charges

TRIGGER KEYWORDS: "AMC charges", "annual maintenance charges", "demat charges", "BSDA", "basic services demat", "AMC deducted", "maintenance charges", "yearly charges", "demat AMC", "AMC waiver", "AMC reversed", "AMC for secondary", "NRI AMC", "account maintenance"

## Protocol

# AMC CHARGES PROTOCOL

---

## Section A: Reference Data

All rules reference these blocks as single sources of truth.

### A1 — AMC Fundamentals

- Report provides AMC charge history by account: charge dates, amounts, BSDA flag, demat type.
- AMC charged quarterly — every 91 days from account opening date.
- Standard AMC: ₹300/year + 18% GST = ₹354/year, in quarterly installments.
- AMC based on highest holdings value during the billing quarter — not current value. `client_holdings` = highest holdings value recorded during the billing quarter.
- AMC charged regardless of trading activity or holdings — as long as demat account is active.
- AMC debited from trading account — may create debit balance if insufficient funds.
- AMC is charged separately for each demat account (primary and secondary).

### A2 — AMC Slabs

| Slab | Holdings Condition | AMC (quarterly) | AMC with 18% GST |
|---|---|---|---|
| Slab 1 (BSDA) | ≤ ₹4,00,000 | ₹0 | ₹0 |
| Slab 2 (BSDA) | ₹4,00,001 – ₹10,00,000 | ₹25 | ₹29.50 |
| Slab 3 (Non-BSDA or > ₹10L) | > ₹10,00,000 OR non-BSDA account | ₹75 | ₹88.50 |

### A3 — BSDA Eligibility (post 1 Sep 2024)

To qualify for BSDA:
- Only 1 demat account across all brokers and depositories, AND
- Total holdings value must not have exceeded ₹10,00,000 during the quarter.

Not eligible: NRI accounts, non-individual accounts.

### A4 — Slab Inference & Response Logic

Infer slab from `charged_amount` (pre-GST), then cross-check with `client_holdings` internally:

| charged_amount (pre-GST) | client_holdings | Response |
|---|---|---|
| ₹0 | ≤ ₹4L | "No AMC was charged as your holdings were within the ₹4,00,000 limit." |
| ₹25 (₹29.50 with GST) | ₹4L–₹10L | "AMC of ₹29.50 was charged as your holdings were ₹[client_holdings]." |
| ₹75 (₹88.50 with GST) | > ₹10L | "AMC of ₹88.50 was charged as your holdings were ₹[client_holdings]." |
| ₹75 (₹88.50 with GST) | ≤ ₹4L | "AMC of ₹88.50 was charged because your account is not eligible for BSDA." + BSDA criteria from **A3**. |
| ₹75 (₹88.50 with GST) | ₹4L–₹10L | "AMC of ₹88.50 was charged because your account is not eligible for BSDA." + BSDA criteria from **A3**. |
| ₹25 (₹29.50 with GST) | ≤ ₹4L | "AMC of ₹29.50 was charged as your holdings crossed ₹4,00,000 during the quarter." |

### A5 — Field Rules

**Shareable with client:** `charged_date`, `previous_charge_date` (as billing period), `charged_amount`, `charge_after_gst`, `type_of_demat`.

**Internal reasoning only (never share with client):** `client_id`, `demat_number`, `demat_only_clientid`, `client_holdings` (use internally for slab verification), `bsda_flag` (use internally for eligibility check).

### A6 — Cross-Reference Protocols

| Topic | Refer to |
|---|---|
| Debit balance from AMC → DPC interest risk | Delayed Payment Charges protocol |
| AMC debit entry on ledger | Ledger Report protocol |

---

## Section B: Decision Flow

### Preflight (run on every query)

1. Fetch the AMC charges report for the client.
2. Apply field protection per **A5** — shareable fields are used in responses, internal-only fields are used for reasoning only.
3. Use `bsda_flag` and `client_holdings` internally to determine BSDA status and slab — these feed into Rule 3 logic.
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
├─ Client asks about BSDA or questions a specific AMC amount
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
└─ AMC created a debit balance
   → Rule 7 (also apply as add-on to any route above when a debit balance is detected)
```

### Scope

- Address: AMC charge explanations, billing cycles, BSDA eligibility, slab verification, and debit balance impact.
- Do not volunteer: internal field values (per **A5**) or raw holdings amounts unless explaining a slab.

### Fallback

If the AMC amount doesn't match any expected slab or the data seems inconsistent → escalate with client ID, charged_date, charged_amount, and the discrepancy.

---

## Section C: Rules

Rules reference Section A blocks. They do not redefine what is already defined there.

### Rule 1 — AMC Charge Explanation

1. Respond: "AMC of ₹[charge_after_gst] was charged on [charged_date] for the billing period [previous_charge_date] to [charged_date]. This is for your [Primary/Secondary] demat account."

### Rule 2 — AMC Billing Cycle

1. Respond: "AMC is charged quarterly — every 91 days from your account opening date. The standard AMC is ₹300/year + 18% GST = ₹354/year, charged in quarterly installments." (Per **A1**.)

### Rule 3 — BSDA Eligibility & AMC Slab Explanation

1. Check `bsda_flag` internally (per **A5**):
   - If `bsda_flag` = NO → client is non-BSDA. Slab 3 applies regardless of holdings. Proceed to Step 3 to explain non-BSDA status.
   - If `bsda_flag` = YES → client is BSDA-eligible. Infer the applicable slab from `charged_amount` and cross-check with `client_holdings` (highest value recorded during the billing quarter, per **A1**) using **A4**. A BSDA-eligible client may still be charged ₹88.50 if their holdings peaked above ₹10,00,000 during the quarter — current holdings are not the basis for the charge.

2. Respond with the matching response from **A4**.

3. If `bsda_flag` = NO, explain BSDA eligibility criteria from **A3** using this framing: "To qualify for BSDA, you must have only one demat account across all brokers and depositories, and your total holdings value must not have exceeded ₹10,00,000 during the quarter. The nil-AMC threshold is ₹4,00,000 (Slab 1) — holdings between ₹4,00,001 and ₹10,00,000 attract a reduced AMC of ₹29.50 per quarter (Slab 2 per **A2**). Since your account is not BSDA-eligible, the standard AMC of ₹88.50 applies."

   Always distinguish: ₹4,00,000 = nil-AMC threshold (Slab 1). ₹10,00,000 = outer BSDA eligibility boundary. Lead with ₹4,00,000 as the nil-AMC figure when clients ask about nil-AMC eligibility.

4. If the account has a debit balance, fetch the ledger report (per **A6**) and include a brief breakdown of all debit entries in the response. This ensures the client is not conflating other debits (settlement charges, DP charges, etc.) with the AMC charge. Explain each debit entry separately before summarising the AMC portion.

### Rule 4 — AMC on Inactive/Zero Holdings Account

1. Respond: "AMC is charged for maintaining the demat account, regardless of whether you hold any securities or have any trading activity. As long as the demat account is active, AMC will apply." (Per **A1**.)
2. Add: "If you don't plan to use the account, you may consider closing the demat account to stop future AMC charges."

### Rule 5 — AMC for Primary and Secondary Demat

1. Respond: "AMC is charged separately for each demat account — primary and secondary. If you see multiple AMC charges in the same period, verify whether they are for different demat accounts using the account type field." (Per **A1**.)

### Rule 6 — NRI / Non-Individual AMC

1. Respond: "AMC charges for NRI and non-individual accounts may differ from standard individual account rates. These are as per Zerodha's tariff. Non-individual accounts are not eligible for BSDA benefits." (Per **A3**.)

### Rule 7 — AMC Creating Debit Balance

This rule applies as a mandatory add-on whenever a debit balance is present in the account, regardless of the primary routing path. Apply it on top of whichever rule handles the main query.

1. Respond: "The AMC charge of ₹[charge_after_gst] has resulted in a debit balance in your account. A debit balance may attract delayed payment charges (interest at 0.05% per day). To avoid further interest, please add funds to clear the debit balance."
2. For DPC details, refer to the Delayed Payment Charges protocol (per **A6**).

