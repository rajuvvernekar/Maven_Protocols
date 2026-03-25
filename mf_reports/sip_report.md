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

# SIP REPORT PROTOCOL

---

## Section A: Reference Data

All rules reference these blocks as single sources of truth.

### A1 — SIP Fundamentals

- This report contains all SIPs: active, paused, cancelled, completed, and failed.
- SIP types: `sip` (Zerodha — modifiable), `amc_sip` (BSE — delete-only), `stp`.
- Zerodha SIP triggers at 1:30 AM; AMC SIP triggers at 3:15 AM.
- SIPs trigger 2 days prior to the `preferred_date`.
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
| `pool` or blank | No mandate linked to this SIP |

Auto-debit is confirmed only when `fund_source` = `digio-mandates` or `upi-mandates` on the specific SIP record. A mandate existing elsewhere does not mean it is linked to this SIP.

### A5 — SIP Not Triggered: Diagnostic Sequence

Run these checks in order — each step may resolve the issue or lead to the next:

| Step | Check | Condition | Action |
|---|---|---|---|
| 0 | Account type | `client_acc_type` ≠ Individual AND `account_statuses` = deactivated | **ESCALATE** — MF team review needed. Account type conversion may require fresh SIP setup. |
| 1 | Initial investment (Zerodha SIP only) | Check console_mf_pseudo_holdings for units in the specific fund | See **A6** for full initial investment diagnostic |
| 2 | SIP status | `sip_status` ≠ Active | That's the answer — SIP is not active |
| 3 | AMC auto-cancel | `sip_type` = amc_sip AND cancelled | Check `remarks` for consecutive rejection (3-failure rule per **A2**) |
| 4 | Future trigger date | `next_sip_date` is in the future | Hasn't reached trigger date yet |
| 5 | Mandate linkage | `fund_source` = blank or pool | No mandate linked — see **A4** and Rule 5 for full mandate check |
| 5.5 | AMC SIP pending mandate | Mandate-linked AMC SIP showing "Pending mandate verification" | Check mandate_debit_report for debit status AND fund_allocation_report for payment mapping |
| 6 | AMC SIP setup timing | `sip_type` = amc_sip AND `created_at` < 2 days before `preferred_date` | "AMC SIP must be set up ≥2 days before execution date." |
| 6.5 | Initial allotment timing (Zerodha SIP) | FRESH order allotted on/after `preferred_date`, or `preferred_date` within 2 days of FRESH order | "Initial investment allotted after SIP date / too close to SIP date — instalment skipped. Pause and resume to reset." |
| 6.6 | Upcoming SIP check | `next_sip_date` within 5 days | Check mf_order_history for already-placed order (triggers 2 days prior). Report actual status. |
| 6.7 | Stale next_sip_date | `sip_status` = Active AND `next_sip_date` before today | SIP has stalled. "Pause and resume your SIP on Coin to re-sync the trigger date." Share link: [How to modify, pause or delete a SIP](https://support.zerodha.com/category/mutual-funds/coin-web-app/articles/modify-pause-delete-sip-coin) |
| 7 | Order exists, payment issue | All checks above normal — check mf_order_history for SIP order on trigger date | If order exists: check `fund_source` on this SIP per **A4**. If `fund_source` = `digio-mandates` or `upi-mandates` → mandate is linked, check mandate_debit_report for debit status. If debit status = Created (SIP date passed) or Failed → the SIP order has failed for this cycle. Advise the client to place a manual lumpsum order (Zerodha SIP only — per mandate_debit_report A3, AMC SIP clients cannot place manual orders). If `fund_source` = blank or pool → mandate is not linked to this SIP, even if an active mandate exists in mandate_report. Advise linking per Rule 5. |
| 8 | Recent modification | No order found | Get `public_id` → check sip_modification_log for recent pause/modify. If modification within T-2 of trigger → "Instalment was skipped due to modification within 2 days of execution date." |

### A6 — Zerodha SIP Initial Investment Diagnostic

Perform for each affected Zerodha SIP (`sip_type` = sip):

1. Check console_mf_pseudo_holdings for the specific fund.
2. **Units found** → initial investment confirmed. Continue to Step 2 in **A5**.
3. **No units found** → check mf_order_history for a FRESH order (purchase_type = FRESH) for that fund:
   - No FRESH order → initial investment never placed.
   - FRESH order Processing/Placed → initial investment still settling.
   - FRESH order Failed/Cancelled → initial investment was not completed.
4. Name the fund explicitly in the response. Do not give a generic "place a lumpsum" message.
5. If multiple SIPs affected: perform this check for each fund separately. List every fund missing initial investment by name: "We checked your SIPs and found that the following funds are missing an initial investment: [fund 1], [fund 2], [fund 3]. Please place a lumpsum order for each of these funds. Once the units are allotted and settled (T+2), the respective SIPs will begin triggering automatically."

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
- Account type conversion detected (Step 0 in **A5**): `client_acc_type` ≠ Individual AND deactivated → **ESCALATE** — MF team review needed.
- AMC SIP deletion technically failing (client followed correct steps but deletion not succeeding) → **ESCALATE** — MF team review needed immediately. Do not ask for screenshots or troubleshoot further.
- SIP deletion failing for any SIP type → **ESCALATE** — agent review needed immediately.
- Any unresolvable SIP trigger issue after completing all diagnostic steps in **A5**.

---

**Escalation behavior:** When any rule in this protocol says **ESCALATE**, do not draft a customer-facing response. Instead, output only: **HUMAN AGENT ACTION REQUIRED** — followed by the reason from the rule. The human agent will handle the query manually.

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
- Do not volunteer: internal field values (per **A7**), SIP type distinctions unless relevant, or information the client hasn't asked about.

### Fallback

If no root cause is identified after completing all diagnostic steps → **ESCALATE** per **A10**.

---

## Section C: Rules

Rules reference Section A blocks. They do not redefine what is already defined there.

### Rule 1 — SIP Not Triggered: Sequential Diagnostic

1. Run through the diagnostic sequence in **A5** in order.
2. For Step 1 (Zerodha SIP initial investment): follow the full diagnostic in **A6** for each affected fund. Name every fund explicitly.
3. For Step 5 (mandate linkage): follow the full mandate verification in Rule 5.
4. For Step 6.5 (initial allotment timing): if FRESH order allotted on/after `preferred_date` or within 2 days → advise to pause and resume.
5. For Step 6.7 (stale next_sip_date): if Active and `next_sip_date` is past → advise pause and resume to re-sync. Share link from **A8**.
6. For Step 8 (recent modification): always check sip_modification_log when the expected trigger date falls within 2 days of any modification. If modification found within T-2 of trigger → "Your SIP was [modified/paused] on [date], within 2 days of the execution date. The current instalment was skipped. It will trigger from the next SIP date." Do not rely on mf_order_history alone.

### Rule 2 — AMC SIP Auto-Cancelled

1. Confirm: `sip_type` = amc_sip AND `sip_status` = Cancelled AND customer didn't cancel.
2. Cross-check mf_order_history (per **A9**) for 3 consecutive failed/rejected orders for this SIP.
3. If confirmed: "Your AMC SIP was cancelled due to 3 consecutive payment rejections. The status will update within 24–48 hours. Please create a new AMC SIP."
4. Do not suggest creating a Zerodha SIP for AMC SIP funds.

### Rule 3 — AMC vs Zerodha SIP

1. Check `sip_type` and respond using the comparison in **A2**.
2. For AMC SIP modification/pause requests: "AMC SIPs cannot be modified or paused. They can only be deleted. To change the amount, date, or fund, delete the existing AMC SIP and create a new one with the desired values. Deletion must be done at least 2 days before the next instalment date."
3. If AMC SIP deletion is technically failing (client followed correct steps) → **ESCALATE** — MF team review needed immediately per **A10**. "We are unable to process this deletion from our end and are escalating this to our team. You can expect a resolution within 24–48 hours."
4. `last_sip_at` is the date of the last SIP order — not the pause/modify date. For pause/modify dates, check sip_modification_log using the SIP's `public_id` (per **A1** and **A9**).
5. If client wants to switch funds → suggest Systematic Transfer Plan (STP) via stp_report (per **A9**) as an alternative to stopping one SIP and starting another.

### Rule 4 — NRI PIS Account: Mandate Not Available

1. Confirm: account type is NRI PIS (NRE account) and client reports they cannot create a mandate.
2. Respond: "Mandates for SIPs cannot be created for NRI PIS accounts. For SIP payments, each instalment will need to be paid manually using NEFT or RTGS. The payment must be made to the ICCL account unique to your Zerodha account."
3. Share link from **A8**: NRI PIS NEFT/RTGS payments.

### Rule 5 — SIP Mandate Linkage Check

**Step 1 — Verify mandate linkage on each SIP individually:**
If multiple SIPs exist, check `fund_source` per **A4** on each SIP record separately. Report linkage status per SIP — a mandate linked to one SIP does not mean it is linked to others. An active mandate in mandate_report also does not mean it is linked to any specific SIP. The only authoritative source for linkage is the `fund_source` field on the individual SIP record.

For each SIP, check `fund_source`:
- `digio-mandates` or `upi-mandates` → mandate is linked to this SIP. Check mandate_report (per **A9**) for current status:
  - success/register_success → active. Check mandate_debit_report for debit attempt and mf_order_history for allotment status.
  - created/pending → "Your mandate is currently being verified. eNACH takes up to 3 working days; UPI autopay is typically immediate. Auto-debit will begin once verification is complete."
  - failed/register_failed → "Your mandate registration failed. Please create a new mandate. UPI autopay activates within minutes."
- blank or pool → mandate is not linked to this SIP. Check mandate_report for whether an active mandate exists elsewhere:
  - Mandate active → "Your mandate is active but not yet linked to your [fund name] SIP. Please link it." Share link from **A8**.
  - No active mandate → "No mandate linked. Please create and link a mandate for auto-debit." Share link from **A8**.

**Example:** mandate_report shows status = success for mandate ZERODHA1349031599. Client has three SIPs. sip_report shows: SIP 1 (ICICI Multi Asset Fund) → fund_source = pool. SIP 2 (Axis Bluechip) → fund_source = upi-mandates. SIP 3 (HDFC Flexi Cap) → fund_source = pool. Correct diagnosis: mandate is linked only to SIP 2. SIPs 1 and 3 require mandate linking.

**Step 2 — Daily SIPs specifically:**
Orders for daily SIPs are placed on T-1 day in the system. Before concluding a daily SIP instalment is missing, check mf_order_history for T-1 day.

### Rule 6 — SIP Deletion Failures

1. If client reports they cannot delete a SIP → **ESCALATE** — agent review needed immediately per **A10**.
2. Respond: "We are escalating this to our team for resolution. You can expect an update within 24–48 hours."

---

## Section D: General Notes

1. The SIP not triggered diagnostic (**A5**) is the core of this protocol — it handles the most common and most complex queries. Always run it in order; many issues are caught at Step 1 (initial investment) or Step 5 (mandate linkage).
2. `last_sip_at` is a frequent source of confusion — it is the last order execution date, not the pause/modify date. Always use sip_modification_log for modification history.
3. Auto-debit confirmation requires verifying `fund_source` on the specific SIP record (per **A4**). A mandate existing in mandate_report does not mean it is linked to the SIP in question — this distinction catches many misdiagnoses.
4. AMC SIPs are the most restrictive: no modify, no pause, delete-only, and auto-cancel after 3 failures. Always check `sip_type` before advising any action.
