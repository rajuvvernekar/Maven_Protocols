# sip_report

## Description

WHEN TO USE:

When clients:
- Ask about SIP status (active/paused/cancelled/completed/failed)
- Report SIP not triggered or deducted this month
- Ask about SIP next date, frequency, or amount
- Report step-up not applied
- Ask about mandate linked to SIP
- Ask about AMC SIP vs Zerodha SIP behavior
- Report SIP cancelled without their action

TRIGGER KEYWORDS: "SIP", "SIP not triggered", "SIP cancelled", "SIP paused", "SIP amount", "step-up", "AMC SIP", "next SIP date", "coin"

TAGS: investments

## Protocol

# SIP REPORT PROTOCOL

---

## Section A: Reference Data

### A1 — SIP Fundamentals

- SIP types: `sip` (Zerodha — modifiable), `amc_sip` (BSE — delete-only).
- Zerodha SIP triggers at 1:30 AM. AMC SIP triggers at 3:15 AM.
- Standard SIP trigger: 2 days prior to `preferred_date`. UPI mandate SIPs (`fund_source` = `upi-mandates`): trigger on T-1 instead of T-2.
- **Microsavings SIP:** Zerodha Nifty Largemidcap 250 Index Fund supports daily SIP frequency only. `sip_type` = `amc_sip`. See Rule 9.

---

### A2 — SIP Type Comparison

| Feature | Zerodha SIP (`sip`) | AMC SIP (`amc_sip`) |
|---|---|---|
| Modify | Yes (amount, date, step-up, frequency) | Cannot modify |
| Pause | Yes | Cannot pause |
| Delete | Yes | Yes — deletion is the only way to change an AMC SIP |
| To change amount/date/fund | Modify directly | Delete existing, create new |
| Deletion timing | Any time | Must be ≥2 days before next instalment date |
| Auto-cancel | Does not auto-cancel | After 3 consecutive payment failures (SEBI circular Apr 2024) |
| Initial investment | Required — lumpsum must be allotted (T+1) and updated (T+2) before SIP triggers | Not required |
| Setup timing | — | Must be ≥2 days before `preferred_date` to trigger in current month |
| Trigger time | 1:30 AM | 3:15 AM |

---

### A3 — SIP Status Values

| Status | Meaning |
|---|---|
| Active | SIP is currently active |
| Paused | Stopped by client or AMC (scheme suspended lumpsum) |
| Cancelled | Deleted by the client |
| Completed | All instalments completed |
| Failed | SIP creation failed |

---

### A4 — Mandate / Fund Source Rules

| `fund_source` value | Meaning |
|---|---|
| `digio-mandates` | eNACH mandate linked |
| `upi-mandates` | UPI autopay mandate linked |
| `rp-pg` | Payment gateway — no mandate linked |
| `pool` or blank | No mandate linked to this SIP |

Authoritative source for SIP-mandate linkage is `fund_source` on the SIP record.

**NRI PIS mandate restriction:** Mandates for SIPs cannot be created on NRI PIS (NRE PIS) accounts. For SIP payments on these accounts, each instalment must be paid manually via NEFT or RTGS to the ICCL account unique to the client's Zerodha account.

---

### A5 — Mandate Debit Status Values

When checking `mandate_debit_report` for a SIP's debit attempt:

| Status | Meaning |
|---|---|
| draft | Debit request created, to be debited on the scheduled date |
| success | Bank debited successfully — payment will be mapped to the order |
| pending | Debit pending or has an issue — check `remark` |
| failed | Bank rejected the debit — order will not process this cycle |

---

### A6 — Mandate Status Check

When checking `mandate_report`, only `status` = `success` indicates a usable, active mandate. Any other status means the mandate is not currently usable for SIP debits.

---

### A7 — Field Rules

**Shareable with client:**

| Field | Interpretation |
|---|---|
| `name` | Fund/scheme name — scheme name lives in `name`, not in any field called `fund` |
| `amount` | SIP instalment amount |
| `sip_status` | Current SIP status — see A3 |
| `frequency` | Instalment frequency |
| `preferred_date` | Client's chosen execution date |
| `next_sip_date` | Next scheduled trigger date |
| `last_sip_at` | Date of last SIP order execution — not pause/modify date; for those, invoke `sip_modification_log` |
| `created_at` | SIP creation date |
| `sip_type` | See A2 for type comparison |

**Non-shareable:**

| Field | Interpretation |
|---|---|
| `id` | Internal SIP record identifier |
| `client_id` | Internal client identifier |
| `transaction_mode` | Internal transaction mode classification |
| `nav` | NAV at time of order — internal pricing reference |
| `intervals` | Total number of SIP instalments configured |
| `pending_intervals` | Number of remaining instalments |
| `status` | Deprecated status field — use `sip_status` instead |
| `tag` | Internal tag |
| `sip_reg_num` | SIP registration number assigned by the exchange/AMC |
| `mandate_details` | Raw mandate data linked to the SIP |
| `fund_source` | Mandate linkage check per A4 |
| `public_id` | Input for `sip_modification_log` (mapped to `sip_id` there) |
| `remarks` | Cancellation cause and other system notes |

---

### A8 — Links

| Topic | URL |
|---|---|
| Mandate creation and SIP linkage | https://support.zerodha.com/category/mutual-funds/payments-and-orders/coin-mandates/articles/sip-mandate-on-coin#:~:text=Linking%20a%20mandate%20to%20an%20existing%20SIP |
| Modify, pause, or delete SIP | https://support.zerodha.com/category/mutual-funds/features-on-coin/systematic-investment-plan/articles/modify-cancel-sip-coin-app |
| NRI PIS NEFT/RTGS payments on Coin | https://support.zerodha.com/category/mutual-funds/payments-and-orders/payment-methods/articles/neft-rtgs-coin |
| Redeem on Coin | https://support.zerodha.com/category/mutual-funds/understanding-mutual-funds/selling/articles/redeem-on-coin-app |
| Microsavings SIP | https://support.zerodha.com/category/mutual-funds/features-on-coin/systematic-investment-plan/articles/microsavings-sip |

## Section B: Decision Flow

### Routing

```
Route by scenario
   ├─ SIP didn't trigger / missed instalment → Rule 1
   ├─ AMC SIP cancelled (client didn't cancel) → Rule 2
   ├─ Client wants to modify or delete AMC SIP → Rule 3
   ├─ NRI PIS account: cannot create mandate → Rule 4
   ├─ SIP mandate linkage / auto-debit / "pending mandate verification" → Rule 5
   ├─ SIP deletion failing → Rule 6
   ├─ Account type conversion suspected → Rule 7
   ├─ Client asks about refund / getting money back after cancelling SIP → Rule 8
   ├─ Client wants to create SIP in Zerodha Nifty Largemidcap 250 Index Fund → Rule 9
   └─ SIP cancelled but payment was still debited → Rule 10
```

### Fallback

If no rule matches and no root cause is identified after checks → escalate.

---

## Section C: Rules

### Rule 1 — SIP Not Triggered

**Account conversion check:**

If status from `get_all_client_data` ≠ "approved" → account type conversion is in progress. Escalate. Stop.

**SIP status check:**

If `sip_status` ≠ Active → communicate the status per A3 and stop. The SIP will not trigger while in a non-active state.

**AMC SIP — auto-cancel check:**

If `sip_type` = `amc_sip` AND `sip_status` = Cancelled → invoke `mf_order_history` and check for 3 consecutive failed/rejected orders for this SIP. If confirmed, route to Rule 2.

**AMC SIP — setup timing check:**

If `sip_type` = `amc_sip` AND `created_at` is less than 2 days before `preferred_date` → AMC SIP setup was too close to the execution date. Communicate the gap (state both `created_at` and `preferred_date`) and advise deleting and creating a new SIP at least 2 days before the next preferred date.

**Future trigger date:**

Compare `next_sip_date` to today. SIPs trigger 2 days prior to `next_sip_date` (1 day prior for UPI mandates per A1). If today is still before the trigger day (i.e., `next_sip_date` is more than 2 days away, or more than 1 day away for UPI mandates) → the SIP has not reached its trigger date yet. Communicate the next trigger date and stop.

**Stale `next_sip_date`:**

If `sip_status` = Active AND `next_sip_date` is before today → the SIP has stalled. Advice depends on `sip_type`:
- Zerodha SIP (`sip_type` = `sip`) → advise the client to pause and resume the SIP on Coin to re-sync the trigger date. Share the modify/pause/delete link from A8.
- AMC SIP (`sip_type` = `amc_sip`) → AMC SIPs cannot be paused (per A2). Advise the client to delete the existing AMC SIP and create a new one to re-sync the trigger. Share the modify/pause/delete link from A8.

**Recent modification check:**

Use `public_id` from this SIP's record. Invoke `sip_modification_log`. Check for any pause, modify, or delete action within T-2 of the expected trigger date. If a recent modification is found, the SIP behavior is explained by that modification — communicate accordingly.

**Initial investment check (Zerodha SIPs only, `sip_type` = `sip`):**

Zerodha SIP will not trigger until the initial lumpsum is allotted and settled. (AMC SIPs do not require initial investment per A2 — skip this check for AMC SIPs.)

Invoke `console_mf_pseudo_holdings` for the specific fund:

- **Units found** → initial investment is confirmed. Invoke `mf_order_history` to verify the FRESH order timing. If the FRESH order was allotted on or after the SIP's `preferred_date`, or `preferred_date` is within 2 days of FRESH allotment, the current cycle was skipped due to allotment timing. Check `next_sip_date`: if it has updated to the next month's expected date → SIP is reset and will trigger next cycle. If `next_sip_date` has not updated → advise the client to pause and resume the Zerodha SIP to reset the trigger date.

- **No units found** → invoke `mf_order_history` for a FRESH order (`purchase_type` = FRESH) for that fund:
  - **FRESH Processing/Placed** → the initial investment is still being processed. Communicate that the SIP will trigger once units are allotted and settled. If `next_sip_date` falls before the expected allotment+settlement date (T+2 from `exchange_timestamp` or `payment_updated_at`), the upcoming instalment will be skipped — communicate this and advise the client to pause and resume the Zerodha SIP once settlement completes.
  - **FRESH Failed/Cancelled** → initial investment was not completed. Advise placing a fresh lumpsum order; once allotted, pause and resume the Zerodha SIP to reset the trigger date.
  - **No FRESH order found** → invoke `console_mf_tradebook` for an allotment entry (`trade_type` = BUY, `purchase_type` = FRESH) for this fund. If found → initial investment is confirmed; proceed to the mandate linkage check below. If not found → initial investment was never placed. Advise placing a lumpsum order; once allotted and settled (T+2), pause and resume the Zerodha SIP on Coin to reset the trigger date.

If multiple SIPs are affected, check each fund separately and name every fund explicitly in the response.

**Mandate linkage check:**

Check `fund_source` per A4. If `fund_source` = `rp-pg`, `pool`, or blank → no mandate is linked to this SIP. Route to Rule 5.

**Order placed but payment issue:**

If the SIP order exists in `mf_order_history` for the trigger date, check `fund_source`:
- `fund_source` = `digio-mandates` or `upi-mandates` → mandate linked. Invoke `mandate_debit_report` and apply A5 status interpretation. If status = `failed` or `pending` (with execution issue), the SIP order has failed for this cycle. For Zerodha SIPs, advise placing a manual lumpsum order to cover the missed cycle. For AMC SIPs, communicate the failure cause from the debit `remark`; the next AMC SIP cycle will retry automatically.
- `fund_source` = `rp-pg`, `pool`, or blank → mandate not linked. Route to Rule 5.

**Fallback:** If none of the above resolves the issue → escalate.

---

### Rule 2 — AMC SIP Auto-Cancelled

1. Confirm: `sip_type` = `amc_sip` AND `sip_status` = Cancelled.

2. Verify the client did not cancel: invoke `sip_modification_log` using `public_id`. If `type` = `sip_delete` exists → the client deleted the SIP; this is not auto-cancellation. Communicate the deletion accordingly and stop.

3. If no `sip_delete` action is found, invoke `mf_order_history` and check for 3 consecutive failed/rejected orders for this SIP.

4. If confirmed: communicate that the AMC SIP was auto-cancelled per the SEBI 3-failure rule (per A2). The status will reflect within 24–48 hours. The client can create a new AMC SIP.

---

### Rule 3 — AMC SIP Modification or Deletion Request

1. Communicate the relevant facts from A2: AMC SIPs cannot be modified or paused. The only option is deletion. To change the amount, date, or fund, the client must delete the existing AMC SIP and create a new one. Deletion must be done at least 2 days before the next instalment date.

2. If the client reports deletion is technically failing → route to Rule 6.

---

### Rule 4 — NRI PIS Account: Mandate Restriction

1. If all three conditions match in `get_all_client_data` → NRI PIS account confirmed:
  - `client_acc_type` is one of NRO, NRE, or NRI
  - `bo_sub_status` contains "RepatriableWith" (NRE)
  - `pis_bank_1_name` or `pis_bank_2_name` is populated (PIS)

Communicate the NRI PIS mandate restriction per A4. Share the NRI PIS NEFT/RTGS link from A8.

2. If the client has an NRI account but is not PIS, mandates can be created normally — proceed with standard SIP mandate handling per Rule 5.

---

### Rule 5 — SIP Mandate Linkage Check

For each SIP in scope, check `fund_source`:

**`fund_source` = `digio-mandates` or `upi-mandates` (mandate linked to this SIP):**

The mandate is linked. To check what happened with the debit:

- Invoke `mandate_debit_report` for the SIP date. Apply A5 status interpretation.
- If `success` → debit succeeded. Invoke `mf_order_history` for the order status.
- If `draft` → scheduled, not yet executed.
- If `pending` → check `remark` for the cause (e.g., insufficient balance, mandate notification issue).
- If `failed` → bank rejected the debit. Communicate the rejection cause from `remark`. For Zerodha SIPs, advise placing a manual lumpsum order to cover the missed cycle. For AMC SIPs, communicate the cause; the next AMC SIP cycle will retry automatically.

**`fund_source` = `rp-pg`, `pool`, or blank (no mandate linked to this SIP):**

The SIP has no mandate linked. To advise the client correctly, check whether they have any active mandate:

- Invoke `mandate_report`. Apply A6 status interpretation.
- If a mandate exists with `status` = `success` → the client has an active mandate but it is not linked to this SIP. Advise linking it. Share the mandate-linkage link from A8.
- If no mandate exists with `status` = `success` → the client has no usable mandate. Advise creating one and linking it. Share the link from A8.

If the client has multiple SIPs, check each one separately. A mandate linked to one SIP does not automatically link to others.

---

### Rule 6 — SIP Deletion Failing

1. Confirm: the client reports they followed the deletion steps but deletion is not succeeding.
2. Escalate.

---

### Rule 7 — Account Type Conversion Check

If status from `get_all_client_data` ≠ "approved" → account type conversion is in progress. SIP-related actions may not work correctly until conversion completes. Escalate.

---

### Rule 8 — Redemption After SIP Cancellation

Cancelling a SIP stops future instalments only — it does not redeem existing units or credit funds back to the bank account. To receive the invested money, the client must place a separate redemption request.

1. Invoke `console_mf_pseudo_holdings` for the fund linked to the cancelled SIP.
2. Units found → guide client to place a redemption request per the Redeem on Coin link from A8.
3. No units found → inform client that no units are held in this fund; nothing to redeem.

---

### Rule 9 — Microsavings SIP: Zerodha Nifty Largemidcap 250 Index Fund

This fund supports daily SIP frequency only. The client must select daily when creating the SIP. `sip_type` will be `amc_sip`. Share the microsavings SIP link from A8.

---

### Rule 10 — Cancelled SIP: Payment Still Debited

1. Confirm `sip_status` = Cancelled for the SIP the client is referring to.
2. Check `fund_source` per A4. If no mandate was linked (`fund_source` = `rp-pg`, `pool`, or blank) → no auto-debit could have occurred; inform client accordingly.
3. If mandate was linked (`fund_source` = `digio-mandates` or `upi-mandates`) → invoke `mandate_debit_report` for the date the client reports the debit. Apply A5 status interpretation.
4. Debit not initiated (no record or `draft`) → no payment was processed; inform client.
5. Debit initiated (`success`, `pending`, or `failed`) → invoke `mf_order_history` for the fund and guide based on order status
