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

## Protocol

---

## Section A: Reference Data

### A1 — SIP Fundamentals

- This report contains all SIPs: active, paused, cancelled, completed, and failed.
- SIP types: `sip` (Zerodha — modifiable), `amc_sip` (BSE — delete-only), `stp`.
- Zerodha SIP triggers at 1:30 AM; AMC SIP triggers at 3:15 AM.
- SIPs trigger 2 days prior to the `preferred_date`. This is the standard trigger timeline. For UPI mandate-based SIPs (`fund_source` = `upi-mandates`), the actual trigger date may be T-1 rather than T-2. Always verify against `order_timestamp` and `last_sip_at` in sip_report — use the actual data over the general rule when explaining trigger timing to the client.
- Scheme name field is `name` (not `fund`).
- `last_sip_at` is the date of the last SIP order execution — not the pause/modify date. Always use sip_modification_log for pause/modify dates.
- `public_id` is needed as input for sip_modification_log (mapped to `sip_id` there).

### A2 — SIP Type Comparison

| Feature | Zerodha SIP (`sip`) | AMC SIP (`amc_sip`) |
|---|---|---|
| Modify | Yes (amount, date, step-up, frequency) | Cannot modify |
| Pause | Yes | Cannot pause |
| Delete | Yes | Yes (only option for changes) |
| To change amount/date/fund | Modify directly | Delete existing, create new |
| Deletion timing | Any time | Must be ≥2 days before next instalment date |
| Auto-cancel | — | After 3 consecutive payment failures (SEBI circular Apr 2024) |
| Initial investment | Required — lumpsum must be allotted (T+1) and updated (T+2) before SIP triggers | — |
| Setup timing | — | Must be ≥2 days before preferred_date to trigger in current month |
| Trigger time | 1:30 AM | 3:15 AM |

### A3 — SIP Status Values

| Status | Meaning |
|---|---|
| Active | Currently active, will trigger on next_sip_date |
| Paused | Stopped by client or AMC (scheme suspended lumpsum) |
| Cancelled | Deleted by client |
| Completed | All instalments completed |
| Failed | SIP creation failed, never activated |

### A4 — Mandate / Fund Source Rules

| `fund_source` Value | Meaning |
|---|---|
| `digio-mandates` | eNACH mandate linked |
| `upi-mandates` | UPI autopay mandate linked |
| `rp-pg` | Payment gateway (no mandate linked) |
| `pool` or blank | No mandate linked to this SIP |

Auto-debit is confirmed only when `fund_source` = `digio-mandates` or `upi-mandates` on the specific SIP record. A mandate existing in mandate_report does not mean it is linked to this SIP — the `fund_source` field on the individual SIP record is the only authoritative source for linkage.

### A5 — SIP Not Triggered: Diagnostic Sequence

Run these checks in order — each step may resolve the issue or lead to the next:

| Step | Check | Condition | Action |
|---|---|---|---|
| 0 | Account type | `client_acc_type` ≠ Individual AND `account_statuses` = deactivated | Escalate to support agent. Account type conversion may require fresh SIP setup. |
| 1 | Initial investment (Zerodha SIP only) | Check console_mf_pseudo_holdings for units in the specific fund | See **A6** for full initial investment diagnostic |
| 1.5 | Initial allotment timing (Zerodha SIP) | FRESH order allotted on/after `preferred_date`, or `preferred_date` within 2 days of FRESH order allotment | "Your initial investment was allotted too close to the SIP date. The current instalment was skipped. Please pause and resume the SIP to reset the trigger date." |
| 2 | Recent modification | Get `public_id` → check sip_modification_log for recent pause/modify/delete. Check for any modification within T-2 of the expected trigger date. | If modification found within T-2 of trigger → "Your SIP was [modified/paused] on [date], within 2 days of the execution date. The current instalment was skipped. It will trigger from the next SIP date." |
| 3 | SIP status | `sip_status` ≠ Active | That's the answer — SIP is not active |
| 4 | AMC auto-cancel | `sip_type` = amc_sip AND cancelled | Check `remarks` for consecutive rejection (3-failure rule per **A2**) |
| 5 | Future trigger date | `next_sip_date` is in the future | Hasn't reached trigger date yet |
| 6 | Mandate linkage | `fund_source` = blank, pool, or rp-pg | No mandate linked — see **A4** and Rule 5 for full mandate check |
| 6.5 | AMC SIP pending mandate | Mandate-linked AMC SIP showing "Pending mandate verification" | Check mandate_debit_report for debit status AND fund_allocation_report for payment mapping |
| 7 | AMC SIP setup timing | `sip_type` = amc_sip AND `created_at` < 2 days before `preferred_date` | "AMC SIP must be set up ≥2 days before execution date." |
| 7.5 | Upcoming SIP check | `next_sip_date` within 5 days | Check mf_order_history for already-placed order (triggers 2 days prior). Report actual status. |
| 7.6 | Stale next_sip_date | `sip_status` = Active AND `next_sip_date` before today | SIP has stalled. "Pause and resume your SIP on Coin to re-sync the trigger date." Share link: [How to modify, pause or delete a SIP](https://support.zerodha.com/category/mutual-funds/coin-web-app/articles/modify-pause-delete-sip-coin) |
| 8 | Order exists, payment issue | All checks above normal — check mf_order_history for SIP order on trigger date | If order exists: check `fund_source` on this SIP per **A4**. If `fund_source` = `digio-mandates` or `upi-mandates` → mandate is linked, check mandate_debit_report for debit status. If debit status = Created (SIP date passed) or Failed → the SIP order has failed for this cycle. Advise the client to place a manual lumpsum order (Zerodha SIP only — per mandate_debit_report A3, AMC SIP clients cannot place manual orders). If `fund_source` = blank, pool, or rp-pg → mandate is not linked to this SIP, even if an active mandate exists in mandate_report. Advise linking per Rule 5. |

### A6 — Zerodha SIP Initial Investment Diagnostic

Perform for each affected Zerodha SIP (`sip_type` = sip):

1. Check console_mf_pseudo_holdings for the specific fund.
2. **Units found** → initial investment is confirmed. Proceed to Step 1.5 in **A5** (check if allotment was too close to SIP date). If allotment timing is fine, proceed to Step 2 in **A5**. No further initial investment checks are needed regardless of what mf_order_history shows.
3. **No units found** → check mf_order_history for a FRESH order (purchase_type = FRESH) for that fund:
   - FRESH Processing/Placed → "Initial investment is still being processed. SIP will trigger once units are allotted and settled." If the next SIP date (`next_sip_date` from sip_report) falls before the expected allotment and settlement date (T+2 from `exchange_timestamp` or `payment_updated_at`), the upcoming instalment will be skipped. State: "Your initial investment is still being processed and will not be settled before your next SIP date. The upcoming SIP instalment will be skipped. Once the initial investment is allotted and settled, please pause and resume the SIP on Coin to reset the trigger date for the next cycle."
   - FRESH Failed/Cancelled → "Initial investment was not completed. Place a fresh lumpsum order. Once allotted, pause and resume the SIP to reset the trigger date."
   - No FRESH order in mf_order_history → mf_order_history covers only the last 180 days. Check console_mf_tradebook for an allotment entry (trade_type = BUY, purchase_type = FRESH) for this fund. If an allotment entry exists → initial investment was completed but is older than 180 days. Proceed to Step 1.5 in **A5**. If no entry in console_mf_tradebook either → initial investment was never placed. "Please place a lumpsum order for [fund name]. Once allotted and settled (T+2), the SIP will begin triggering."
4. Name the fund explicitly in the response.
5. If multiple SIPs affected: perform this check for each fund separately. List every fund missing initial investment by name: "We checked your SIPs and found that the following funds are missing an initial investment: [fund 1], [fund 2], [fund 3]. Please place a lumpsum order for each of these funds. Once the units are allotted and settled (T+2), the respective SIPs will begin triggering automatically."
6. **Mandate linkage check (always perform after initial investment diagnostic):** After diagnosing the initial investment issue, also check `fund_source` per **A4** for mandate linkage on each affected SIP. If `fund_source` = `rp-pg`, `pool`, or blank → inform the client that no mandate is linked to this SIP and advise creating and linking one. Share link from **A8**. Communicate both issues together — the client needs to resolve both the initial investment and mandate linkage for the SIP to trigger automatically.

### A7 — Field Rules

**Shareable with client:** `name` (fund name), `amount`, `sip_status`, `frequency`, `preferred_date`, `next_sip_date`, `last_sip_at`, `created_at`.

**Internal reasoning only (use for analysis, never share):** `sip_type`, `fund_source` (mandate check per **A4**), `public_id` (input for sip_modification_log), `remarks`.

**Suppress (no client use and only reasoning purpose): id, client_id, transaction_mode, nav, intervals, pending_intervals, status (deprecated), tag, sip_reg_num, mandate_details.

### A8 — Links

| Topic | URL |
|---|---|
| Mandate creation and SIP linkage | https://support.zerodha.com/category/mutual-funds/payments-and-orders/coin-mandates/articles/sip-mandate-on-coin#:~:text=Linking%20a%20mandate%20to%20an%20existing%20SIP |
| Modify, pause, or delete SIP | https://support.zerodha.com/category/mutual-funds/coin-web-app/articles/modify-pause-delete-sip-coin |
| NRI PIS NEFT/RTGS payments on Coin | https://support.zerodha.com/category/mutual-funds/payments-and-orders/payment-methods/articles/neft-rtgs-coin |

### A9 — Cross-Reference Protocols

| Topic | Refer to |
|---|---|
| SIP order status, allotment confirmation | mf_order_history |
| SIP pause/modify/delete history | sip_modification_log (use `public_id` as input) |
| Mandate status and details | mandate_report |
| Mandate debit attempts | mandate_debit_report |
| Payment mapping for AMC SIP | fund_allocation_report |
| Holdings verification (initial investment) | console_mf_pseudo_holdings |
| STP as alternative to stopping/starting SIPs | stp_report |

### A10 — Escalation Triggers

Escalate when:
- Account type conversion detected (Step 0 in **A5**): `client_acc_type` ≠ Individual AND deactivated → escalate to support agent.
- AMC SIP deletion technically failing (client followed correct steps but deletion not succeeding) → escalate to support agent immediately. Do not ask for screenshots or troubleshoot further.
- SIP deletion failing for any SIP type → escalate to support agent immediately.
- Any unresolvable SIP trigger issue after completing all diagnostic steps in **A5**.

## Section B: Decision Flow

### Preflight (run on every query)

1. Fetch the SIP report for the client.
2. Apply field protection per **A7** — identify shareable, internal, and banned fields.
3. Identify `sip_type` for the relevant SIP(s) — this determines available actions per **A2**.
4. Check `fund_source` for mandate linkage status per **A4**.
5. Format amounts with ₹ and Indian comma notation. Format dates as DD MMM YYYY.

### Routing Tree

```
Query relates to SIP →
│
├─ SIP didn't trigger / missed instalment
│  → Rule 1 (Sequential diagnostic per A5)
│
├─ AMC SIP auto-cancelled (client didn't cancel)
│  → Rule 2
│
├─ Client confused about SIP type / asks to modify AMC SIP
│  → Rule 3
│
├─ NRI PIS account — mandate not available
│  → Rule 4
│
├─ Mandate linkage / auto-debit / "pending mandate verification"
│  → Rule 5
│
├─ SIP deletion failing
│  → Rule 6 (Escalate)
│
└─ General SIP status query
   → Check data, translate status per A3, respond
```

### Scope

- Address: SIP trigger issues, mandate linkage, AMC vs Zerodha SIP differences, initial investment verification, and SIP modification/deletion guidance.

### Fallback

If no root cause is identified after completing all diagnostic steps → escalate per **A10**.

---

## Section C: Rules

### Rule 1 — SIP Not Triggered: Sequential Diagnostic

1. Run through the diagnostic sequence in **A5** in order.
2. For Step 1 (Zerodha SIP initial investment): follow the full diagnostic in **A6** for each affected fund. Name every fund explicitly. After diagnosing the initial investment issue, also check mandate linkage per **A6** Step 6 and communicate both issues together.
3. For Step 1.5 (initial allotment timing): if FRESH order allotted on/after `preferred_date` or within 2 days → advise to pause and resume.
4. For Step 2 (recent modification): get `public_id` from sip_report → check sip_modification_log. If any modification is found within T-2 of the expected trigger date → "Your SIP was [modified/paused] on [date], within 2 days of the execution date. The current instalment was skipped. It will trigger from the next SIP date."
5. For Step 6 (mandate linkage): follow the full mandate verification in Rule 5.
6. For Step 7.6 (stale next_sip_date): if Active and `next_sip_date` is past → advise pause and resume to re-sync. Share link from **A8**.
7. For Step 8 (order exists, payment issue): check `fund_source` per **A4** to determine mandate linkage before diagnosing payment. If `fund_source` = `digio-mandates` or `upi-mandates` → check mandate_debit_report. If `fund_source` = blank, pool, or rp-pg → mandate is not linked, advise linking per Rule 5.

### Rule 2 — AMC SIP Auto-Cancelled

1. Confirm: `sip_type` = amc_sip AND `sip_status` = Cancelled AND customer didn't cancel.
2. Cross-check mf_order_history (per **A9**) for 3 consecutive failed/rejected orders for this SIP.
3. If confirmed: "Your AMC SIP was cancelled due to 3 consecutive payment rejections. The status will update within 24–48 hours. Please create a new AMC SIP."
4. Do not suggest creating a Zerodha SIP for AMC SIP funds.

### Rule 3 — AMC vs Zerodha SIP

1. Check `sip_type` and respond using the comparison in **A2**.
2. For AMC SIP modification/pause requests: "AMC SIPs cannot be modified or paused. They can only be deleted. To change the amount, date, or fund, delete the existing AMC SIP and create a new one with the desired values. Deletion must be done at least 2 days before the next instalment date."
3. If AMC SIP deletion is technically failing (client followed correct steps) → escalate to support agent immediately per **A10**. "We are unable to process this deletion from our end and are escalating this to our team. You can expect a resolution within 24–48 hours."
4. `last_sip_at` is the date of the last SIP order — not the pause/modify date. For pause/modify dates, check sip_modification_log using the SIP's `public_id` (per **A1** and **A9**).
5. If client wants to switch funds → suggest Systematic Transfer Plan (STP) via stp_report (per **A9**) as an alternative to stopping one SIP and starting another.

### Rule 4 — NRI PIS Account: Mandate Not Available

1. Confirm: account type is NRI PIS (NRE account) and client reports they cannot create a mandate.
2. Respond: "Mandates for SIPs cannot be created for NRI PIS accounts. For SIP payments, each instalment will need to be paid manually using NEFT or RTGS. The payment must be made to the ICCL account unique to your Zerodha account."
3. Share link from **A8**: NRI PIS NEFT/RTGS payments.

### Rule 5 — SIP Mandate Linkage Check

**Step 1 — Verify mandate linkage on each SIP individually:**
Check `fund_source` per **A4** on each SIP record first. This is the only authoritative source for linkage — check this before consulting mandate_report or mandate_debit_report. Report linkage status per SIP — a mandate linked to one SIP does not mean it is linked to others.

For each SIP, check `fund_source`:
- `digio-mandates` or `upi-mandates` → mandate is linked to this SIP. Check mandate_report (per **A9**) for current status:
  - success/register_success → active. Check mandate_debit_report for debit attempt and mf_order_history for allotment status.
  - created/pending → "Your mandate is currently being verified. eNACH takes up to 3 working days; UPI autopay is typically immediate. Auto-debit will begin once verification is complete."
  - failed/register_failed → "Your mandate registration failed. Please create a new mandate. UPI autopay activates within minutes."
- `rp-pg`, blank, or pool → mandate is not linked to this SIP. Check mandate_report for whether an active mandate exists elsewhere:
  - Mandate active → "Your mandate is active but not yet linked to your [fund name] SIP. Please link it." Share link from **A8**.
  - No active mandate → "No mandate linked. Please create and link a mandate for auto-debit." Share link from **A8**.

**Example:** mandate_report shows status = success for mandate ZERODHA1349031599. Client has three SIPs. sip_report shows: SIP 1 (ICICI Multi Asset Fund) → fund_source = pool. SIP 2 (Axis Bluechip) → fund_source = upi-mandates. SIP 3 (HDFC Flexi Cap) → fund_source = pool. Correct diagnosis: mandate is linked only to SIP 2. SIPs 1 and 3 require mandate linking.

**Step 2 — Daily SIPs specifically:**
Orders for daily SIPs are placed on T-1 day in the system. Before concluding a daily SIP instalment is missing, check mf_order_history for T-1 day.

### Rule 6 — SIP Deletion Failures

1. If client reports they cannot delete a SIP → escalate to support agent immediately per **A10**.
2. Respond: "We are escalating this to our team for resolution. You can expect an update within 24–48 hours."
