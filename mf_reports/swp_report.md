# swp_report

## Description

WHEN TO USE:

When clients:
- Ask about SWP status, schedule, or amount
- Report SWP not triggered on expected date
- Ask about next/last SWP date
- Report SWP redemption amount differs from expected

TRIGGER KEYWORDS: "SWP", "systematic withdrawal", "withdrawal plan", "SWP not triggered", "coin"

## Protocol

# SWP REPORT PROTOCOL

---

## Section A: Reference Data

All rules reference these blocks as single sources of truth.

### A1 — SWP Fundamentals

- SWP triggers at 10:00 AM on the scheduled date.
- Units redeemed = instalment_amount ÷ T-1 NAV. Actual redemption happens at T day NAV (may differ from estimate).
- SWP created within 2 working days of next instalment → starts from the next cycle, not the current one.
- Scheme name field is `fund`.

### A2 — T-PIN / DDPI Authorization

| Account Type | Requirement |
|---|---|
| Non-DDPI/POA | Must authorize CDSL T-PIN after 10 AM trigger, before 3 PM on trigger day. If missed → order rejected with "UNRID" or "UNITS NOT AUTHORISED". |
| DDPI enabled | No T-PIN required — automatic debit of units each cycle. Recommend as permanent fix. |

SWP orders trigger at 10:00 AM. The client receives a T-PIN authorization request after the trigger. Authorization must be completed the same day before 3:00 PM. If not completed, the SWP order for that cycle is cancelled. The rejection shows as "UNRID" in mf_order_history.

### A3 — Field Rules

**Shareable with client:** `fund`, `frequency`, `instalment_day`, `instalment_amount` (if asked), `next_instalment`, `last_instalment`, `created`.

**Internal reasoning only:** `swp_id` (pass as `sip_id` to sip_modification_log for modification history), `completed_instalments`.

**Never share with client:** `tradingsymbol`, `transaction_type` (deprecated), `tag`.

### A4 — SWP Not Triggered: Diagnostic Sequence

Run these checks in order — complete all steps before concluding:

| Step | Check | Condition | Action |
|---|---|---|---|
| 1 | Creation timing | `created` within 2 working days of instalment | "Your SWP was created too close to the instalment date. It will start from the next cycle." |
| 2 | Modification | Get `swp_id` → pass as `sip_id` to sip_modification_log. Check for swp_edit within T-2 of trigger. | If modified within T-2 → "Your SWP was modified on [date], within 2 days of the execution date. This cycle was skipped. It will trigger from the next cycle." |
| 3 | Order status | Check mf_order_history for SELL order on trigger date | Failed → check status_message: if "UNRID" or "UNITS NOT AUTHORISED" → T-PIN not completed. Respond per Rule 3 (T-PIN window: 10:00 AM to 3:00 PM on trigger day). If "free_qty_less" or other → apply relevant rule. Redeemed → SWP did trigger, clarify with client. No order → proceed to Step 4. |
| 4 | Pledged/available units (always complete this step) | Check console_mf_pseudo_holdings (`margin`) and console_mf_holdings (`available`) | `margin` > 0 → "Units are pledged. Unpledge first: Console → Portfolio → Holdings → [fund] → Unpledge." `available` = 0 or insufficient → "Units not available for redemption." |
| 5 | All checks normal, no order | Backend issue | Suggest manual redemption for this cycle. |

### A5 — Cross-Reference Protocols

| Topic | Refer to |
|---|---|
| SWP modification history | sip_modification_log (use `swp_id` as `sip_id` input; look for swp_edit entries) |
| SWP order status on trigger date | mf_order_history (SELL order) |
| Pledged units (`margin`) | console_mf_pseudo_holdings |
| Available units for redemption (`available`) | console_mf_holdings |

---

**Escalation behavior:** When any rule in this protocol says **ESCALATE**, do not draft a customer-facing response. Instead, output only: **HUMAN AGENT ACTION REQUIRED** — followed by the reason from the rule. The human agent will handle the query manually.

## Section B: Decision Flow

### Preflight (run on every query)

1. Fetch the SWP report for the client.
2. Apply field protection per **A3** — identify shareable, internal, and banned fields.
3. Note `swp_id` for potential sip_modification_log lookup.
4. Format amounts with ₹ and Indian comma notation. Format dates as DD MMM YYYY.

### Routing Tree

```
Query relates to SWP →
│
├─ SWP didn't trigger / missed instalment
│  → Rule 1 (Full diagnostic per A4)
│
├─ SWP redeemed different amount than expected
│  → Rule 2
│
├─ SWP order rejected with "units not authorized" / T-PIN issue
│  → Rule 3
│
└─ General SWP status query
   → Check data, respond with shareable fields
```

### Scope

- Address: SWP trigger issues, amount discrepancies, T-PIN authorization, and pledged/available unit checks.
- Do not volunteer: internal field values (per **A3**), raw rejection codes, or information the client hasn't asked about.

### Fallback

If no root cause found after completing all diagnostic steps → suggest manual redemption and escalate if issue recurs.

---

## Section C: Rules

Rules reference Section A blocks. They do not redefine what is already defined there.

### Rule 1 — SWP Not Triggered: Sequential Diagnostic

1. Run through all steps in **A4** sequentially — complete every step before concluding.
2. Step 1: check `created` timing (per **A1** — within 2 working days → starts next cycle).
3. Step 2: check sip_modification_log via `swp_id` (per **A5**) for swp_edit near trigger date (per **A4** Step 2).
4. Step 3: check mf_order_history (per **A5**) for SELL order on trigger date.
   - Failed with "UNRID" or "UNITS NOT AUTHORISED" → route to Rule 3.
   - Failed with other reason → inform based on `status_message`.
   - Redeemed → SWP did trigger, clarify with client.
   - No order → proceed to Step 4.
5. Step 4 (always complete): check pledged units via console_mf_pseudo_holdings and available units via console_mf_holdings (per **A5**).
   - `margin` > 0 → "Some of your units are pledged and cannot be redeemed. Please unpledge first: Console → Portfolio → Holdings → [fund] → Unpledge."
   - `available` = 0 or insufficient → "Units are not available for redemption."
6. Step 5: all checks normal, no order found → backend issue. Suggest manual redemption for this cycle.

### Rule 2 — Amount Differs

1. Respond: "The final amount credited to your bank account may differ from your intended SWP amount because the calculation uses the previous day's NAV (T-1), but the actual redemption uses the current day's NAV (T). You receive more if the current day's NAV is higher, and less if it is lower." (Per **A1**.)

### Rule 3 — T-PIN Authorization Required

1. Respond using **A2**: "CDSL T-PIN authorization must be completed on the same day the SWP triggers, between 10:00 AM and 3:00 PM. Since it was not completed on time, the order was rejected. Please place a fresh manual redemption request for this cycle."
2. Recommend DDPI: "To avoid this every cycle, we recommend enabling DDPI on your account — this allows automatic debit of units without requiring T-PIN authorization each time."

---

## Section D: General Notes

1. The SWP diagnostic (**A4**) must be completed in full — especially Step 4 (pledged/available units). Skipping this step misses one of the most common causes: pledged units blocking redemption while the SWP itself appears correctly configured.
2. T-1 NAV vs T day NAV is the primary cause of amount discrepancies. The estimate uses yesterday's NAV but the actual redemption uses today's — this is expected behavior, not an error.
3. The sip_modification_log is shared across SIP/SWP/STP. When checking modifications for an SWP, use `swp_id` as the `sip_id` input and look for `swp_edit` or `swp_delete` type entries.
