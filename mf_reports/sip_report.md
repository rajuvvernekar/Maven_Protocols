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
   - No FRESH order in mf_order_history → mf_order_history covers only the last 30 days. Check console_mf_tradebook for an allotment entry (trade_type = BUY, purchase_type = FRESH) for this fund. If an allotment entry exists → initial investment was completed but is older than 30 days. Proceed to Step 1.5 in **A5**. If no entry in console_mf_tradebook either → initial investment was never placed. "Please place a lumpsum order for [fund name]. Once allotted and settled (T+2), the SIP will begin triggering."
4. Name the fund explicitly in the response.
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
2. For Step 1 (Zerodha SIP initial investment): follow the full diagnostic in **A6** for each affected fund. Name every fund explicitly.
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




---
---


# CONSOLE MF EXTERNAL TRADES PROTOCOL

---

## Section A: Reference Data

### A1 — Tool Purpose & Scope

- Contains orders executed outside Coin (transferred-in units, external platform purchases).
- `trade_id` and `order_id` always show as "DISCREPANT" — this is expected behavior for external entries.
- Transferred-in units always show as discrepant until external entries are added by the client.
- External entries cannot be deleted by the client — requires backend deletion.
- Scheme name field is `tradingsymbol`.

### A2 — Coin-Only Purchase Rule

If all purchases for a fund were made through Coin (no transfer from another platform), external trade entries should not exist for that fund. If found, they were incorrectly entered and need deletion via backend + data rerun. This is the most important diagnostic check in this protocol — always verify Coin-only vs transferred before advising any action.

### A3 — Recalculation Status

| `pending_recalc` Value | Meaning |
|---|---|
| false | P&L has been recalculated — entries are reflected |
| true | Recalculation pending — check again in 24 hours |

### A4 — Field Rules

**Shareable with client (if asked):** `trade_date`, `tradingsymbol` (as fund name), `quantity`, `price`, `trade_type`, `order_execution_time`.

**Internal reasoning only (use for analysis, never share):** `pending_recalc`, `creation`, `external_trade_type`.

**Suppress (no client use, only for reasoning purpose):** `pk`, `client_id`, `isin`, `instrument_id`, `trade_id`, `order_id`, `exchange`, `series`, `segment`, `settlement_type`.

### A5 — External Trade Addition Path

Console → Portfolio → Holdings → select fund → Add External Trade.

### A6 — Cross-Reference Protocols

| Topic | Refer to |
|---|---|
| Tradebook entries for duplicate detection / FIFO P&L | console_mf_tradebook |
| Holdings discrepancy diagnosis | console_mf_pseudo_holdings |
| Redeemable units verification | console_mf_holdings (`available` field) |

### A7 — Escalation Triggers (Consolidated)

Escalate to support agent when any of the following occur:
- External trade entries incorrectly added for a Coin-only fund — need deletion + data rerun (Rule 3).
- Client needs an external entry deleted (cannot self-serve) — provide fund name, trade_date, quantity, price, trade_type.
- All external entries correct, `pending_recalc` = false, but buy average still wrong (Rule 2).
- Duplicate entries found between this tool and console_mf_tradebook (Rule 4).

Include in escalation: fund name, trade_date, quantity, price, trade_type, and the specific issue.

## Section B: Decision Flow

### Preflight (run on every query)

1. Fetch the external trades data for the client and relevant fund.
2. Apply field protection per **A4** — identify shareable, internal, and banned fields.
3. **Coin-only check:** Determine whether the client transferred units from another platform or all purchases were made through Coin. This determines the entire diagnostic path (per **A2**).
4. Format amounts with ₹ and Indian comma notation. Format dates as DD MMM YYYY.

### Routing Tree

```
Query relates to MF external trades →
│
├─ Preflight: All purchases through Coin (no external transfer)?
│  ├─ YES, and external entries exist here
│  │  → Rule 3 (Wrongly entered — escalate for deletion)
│  └─ NO (units transferred from another platform)
│     ├─ External entries missing → Rule 1a (Guide to add)
│     ├─ Entries exist, pending_recalc = true → Rule 1b (Wait)
│     └─ Entries exist, still wrong → Rule 2 (Verify and escalate)
│
├─ Client needs to delete an external entry
│  → Rule 3 (Escalate for deletion)
│
├─ Client reports doubled value / duplicate entries
│  → Rule 4
│
├─ XIRR incorrect
│  → Rule 5
│
└─ Data inconsistency / no root cause found
   → Escalate per A7
```

### Scope

- Address: external trade entry management, discrepancy diagnosis from transferred units, buy average correction, duplicate detection, and XIRR verification.

### Fallback

If no root cause is identified after checking all relevant rules → escalate per **A7**.

---

## Section C: Rules

### Rule 1 — Discrepancy After Transfer

1. Confirm: client transferred units from another platform (not Coin-only — verified in Preflight step 3 per **A2**).

**1a — External entries missing:**
"To correct the buy average for transferred units, please add external trade entries: [path from **A5**]. Enter the original purchase date, quantity, and price for each lot transferred."

**1b — Entries exist, recalculation pending:**
Check `pending_recalc` (per **A3**). If true: "The recalculation is pending. Please check again in 24 hours."

### Rule 2 — Wrong Buy Average (Entries Exist)

1. Verify all purchase lots are entered correctly: dates, quantities, prices.
2. If all correct and `pending_recalc` = false → escalate per **A7**.

### Rule 3 — Wrongly Entered External Trades / Deletion Required

**Coin-only fund with external entries (per A2):**
The external trades were incorrectly entered. Do not advise adding more entries. Escalate to support agent: "External trade entries were incorrectly added for [fund name]. These need to be deleted and a data rerun is required. Client should not add any trade details for purchases made through Coin."

**Client requests deletion of any external entry:**
"External entries cannot be deleted from Console." Escalate to support agent with: fund name, trade_date, quantity, price, trade_type (per **A7**).

### Rule 4 — Duplicate Entry Detection

1. Compare entries here with console_mf_tradebook entries (per **A6**) for the same fund, date, and quantity.
2. If duplicate found: "We have identified a duplicate entry. We will remove it. Your P&L will be corrected within 24–48 hours."
3. Escalate to support agent with: fund name, trade_date, quantity, price (per **A7**).

### Rule 5 — XIRR Incorrect

1. XIRR requires complete buy/sell history across both console_mf_tradebook and this tool (per **A6**).
2. Any missing entry skews XIRR results.
3. Verify all entries in both tools are present and correct. If entries are complete but XIRR still wrong → escalate.


---
---


# CONSOLE MF HOLDINGS PROTOCOL

---

## Section A: Reference Data

### A1 — Tool Purpose & Scope

- This is a **secondary** holdings tool — backed by Tradebook + demat records.
- Invoke only for: `available` (units free for redemption/SWP), `holdings_date` (latest demat credit), `total_quantity`.
- For all other MF holdings queries → use console_mf_pseudo_holdings first.
- All MF holdings queries start with console_mf_pseudo_holdings. This tool is invoked only when specific fields above are needed.
- ETF FOF is an MF — appears in Coin holdings (use console_mf_pseudo_holdings). Pure ETFs appear in Kite holdings only.

### A2 — Settlement Timelines

| Fund Type | Units Visible |
|---|---|
| Liquid funds | T day by 7 PM |
| Non-liquid funds | T+1 day by 7 PM |

### A3 — NAV Display Differences

| Platform | NAV Date |
|---|---|
| Console | T-2 days |
| Coin | T-1 day |

This difference in NAV dates causes P&L values to appear different between platforms. For the latest valuation, refer to Coin.

Reference: [Why does Console show a different MF NAV?](https://support.zerodha.com/category/mutual-funds/coin-general/coin-reports/articles/mf-nav-of-t-2-days-on-console)

### A4 — Field Rules

**Shareable with client (if asked):** `tradingsymbol` (as fund name), `buy_average`, `buy_value`, `total_quantity`.

**Internal reasoning only (use for analysis, never share):** `holdings_date` (latest demat credit), `failure_date` (passive — if seen, route to console_mf_pseudo_holdings), `available` (critical for redemption/SWP checks), `discrepant` (cross-check only), `loan`, `closing_price`.

**Suppress (no client use, only reasoning purpose).** `name` (not applicable for MF), `client_id`, `isin`, `instrument_id`, `t1`, `pending`.

**Client communication rules:** Scheme name field is `tradingsymbol`. Never mention "pseudo holdings", "backend systems", or any internal tool/system names to the client. Never share the `discrepant` field value with the client.

### A5 — Tool Routing Reference

| Query Type | Primary Tool | This Tool's Role |
|---|---|---|
| All MF holdings queries (default) | console_mf_pseudo_holdings | Do not use this tool as starting point |
| Units available for redemption/SWP | **This tool** (`available` field) | Authoritative source |
| Latest demat credit date | **This tool** (`holdings_date` field) | Authoritative source |
| Total quantity verification | **This tool** (`total_quantity` field) | Authoritative source |
| Pledged units / margin | console_mf_pseudo_holdings | Margin is authoritative there |
| failure_date investigation | console_mf_pseudo_holdings | Authoritative source; route escalation from there |
| Discrepancy diagnosis | console_mf_pseudo_holdings (start) → this tool (cross-check) | Cross-check role only |
| Buy average issues | console_mf_pseudo_holdings → console_mf_external_trades | Cross-check external entries |
| Missing trade entries | console_mf_tradebook | Verify trade exists |
| Pure ETF holdings | Kite equity holdings | Not an MF query |
| ETF FOF holdings | console_mf_pseudo_holdings | ETF FOF is treated as MF |

### A6 — Cross-Reference Protocols

| Topic | Refer to |
|---|---|
| Primary MF holdings, discrepancy diagnosis, pledged units, failure_date | console_mf_pseudo_holdings |
| Missing trade entries verification | console_mf_tradebook |
| Buy average correction / external trade entries | console_mf_external_trades |
| Pure ETF holdings | Kite equity holdings |

## Section B: Decision Flow

### Preflight (run on every query)

1. Determine if this tool is needed: check if the query requires `available`, `holdings_date`, or `total_quantity`. If not → route to console_mf_pseudo_holdings per **A5**.
2. If this tool is needed, fetch the MF holdings data.
3. Apply field protection per **A4** — identify shareable, internal, and banned fields.
4. Check for `failure_date` — if present, note it but do not escalate from this tool (route to console_mf_pseudo_holdings per Rule 5).
5. Format amounts with ₹ and Indian comma notation.

### Routing Tree

```
Query relates to MF holdings →
│
├─ Need to verify units available for redemption/SWP
│  → Rule 1
│
├─ Units not visible after allotment
│  → Rule 2
│
├─ Discrepancy cross-check (requested by console_mf_pseudo_holdings)
│  → Rule 3
│
├─ Buy average incorrect (flagged by console_mf_pseudo_holdings)
│  → Rule 4
│
├─ failure_date seen in data
│  → Rule 5 (Route to console_mf_pseudo_holdings)
│
├─ Console vs Coin value difference
│  → Rule 6
│
└─ General MF holdings query (not requiring available/holdings_date/total_quantity)
   → Route to console_mf_pseudo_holdings per A5
```

### Scope

- Address: redeemable unit verification, demat credit dates, total quantity checks, and cross-check support for console_mf_pseudo_holdings.

### Fallback

If query doesn't match any rule and doesn't require this tool's specific fields → route to console_mf_pseudo_holdings per **A5**.

---

## Section C: Rules

### Rule 1 — Units Available for Redemption/SWP

1. Check the `available` field — this is the authoritative source for redeemable units.
2. If `available` = 0 or insufficient → inform client that units are not available for redemption/SWP.
3. If `available` > 0 but redemption is failing → check if units are pledged via console_mf_pseudo_holdings (`margin` field, per **A5**).

### Rule 2 — Units Not Visible After Allotment

1. Check console_mf_pseudo_holdings first for discrepancy diagnosis (per **A5**).
2. Use this tool only to verify `holdings_date` (latest demat credit) and `total_quantity`.
3. If within settlement timeline (per **A2**: liquid T day 7 PM, non-liquid T+1 7 PM) → "Units will be visible by [timeline]."
4. If beyond timeline → check `holdings_date` for latest credit date. Route full discrepancy diagnosis to console_mf_pseudo_holdings (per **A5**).

### Rule 3 — Discrepancy Cross-Check

1. Triggered when console_mf_pseudo_holdings shows `discrepant` > 0 and requests cross-check.
2. Compare `available` and `discrepant` here with console_mf_pseudo_holdings values.
3. If mismatch → check console_mf_tradebook for missing trade entries (per **A6**).
4. If trade entry exists but mismatch persists → escalate.

### Rule 4 — Buy Average Incorrect

1. Triggered when console_mf_pseudo_holdings flags wrong buy average.
2. Cross-check console_mf_external_trades (per **A6**) — verify all entries are correct and complete.
3. If units were transferred in, verify external trade entries have been added.
4. If all entries correct and `failure_date` is empty → escalate.

### Rule 5 — Failure Date: Passive Route

1. If `failure_date` is present in this tool's data → do not escalate from this tool.
2. Route to console_mf_pseudo_holdings — it is the authoritative source for `failure_date` (per **A5**).
3. Escalation for failure_date must be triggered from console_mf_pseudo_holdings, not from here.

### Rule 6 — Console vs Coin Value Difference

1. Respond using **A3**: "Console displays the NAV as of T-2 days, while Coin displays the NAV as of T-1 day. This difference in NAV dates causes the P&L values to appear different. For the latest valuation, please refer to Coin."
2. Share link from **A3**.


---
---




# CONSOLE MF TRADEBOOK PROTOCOL

---

## Section A: Reference Data

### A1 — Tool Purpose & Scope

- Contains executed orders only (allotment/redemption completed).
- P&L is calculated from this tool's data using FIFO.
- If a trade entry is missing for an allotted order → P&L and holdings issues will result.
- Zerodha fund house WhatsApp orders → trade entries posted here if allotted.
- Scheme name field is `tradingsymbol`.

### A2 — ELSS Lock-in Rules

- ELSS lock-in: exactly 3 calendar years from `trade_date` (allotment date) per BUY entry, on a FIFO basis.
- `trade_date` = allotment date — not the order placement date or payment date.
- Example: allotted on 15-Mar-2022 → unlocks on 15-Mar-2025.
- If lock-in ends today → units redeemable from tomorrow (T+1 settlement).

### A3 — Field Rules

**Shareable with client (if asked):** `trade_date` (as allotment date), `tradingsymbol` (as fund name), `trade_type`, `quantity`, `price`.

**Internal reasoning only (use for analysis, never share):** `order_execution_time` (NAV cutoff check), `order_id`, `trade_id`, `client_id`.

**Suppress (no client use, only reasoning  purpose): exchange, instrument_id, isin, scheme_code, settlement_type

### A4 — Cross-Reference Protocols

| Topic | Refer to |
|---|---|
| Units missing after allotment — discrepancy diagnosis | console_mf_pseudo_holdings (primary source) |
| Transferred-in units affecting P&L / buy average | console_mf_external_trades |
| Redeemable units verification | console_mf_holdings (`available` field) |

## Section B: Decision Flow

### Preflight (run on every query)

1. Fetch the MF tradebook data for the client and relevant date range/fund.
2. Apply field protection per **A3** — identify shareable, internal, and banned fields.
3. Identify the fund using `tradingsymbol`.
4. Format amounts with ₹ and Indian comma notation. Format dates as DD MMM YYYY.

### Routing Tree

```
Query relates to MF tradebook →
│
├─ Client asks when ELSS units can be redeemed
│  → Rule 1
│
├─ Order allotted but units missing (flagged by mf_order_history)
│  → Rule 2
│
├─ Client disputes MF P&L
│  → Rule 3
│
└─ General tradebook query
   → Check data, apply field protection, respond with shareable fields
```

### Scope

- Address: ELSS lock-in dates, allotment verification, P&L FIFO calculations, and trade entry verification.

### Fallback

If trade data seems inconsistent or missing entries cannot be explained → escalate with client ID, fund name, trade dates, and the specific discrepancy.

---

## Section C: Rules

### Rule 1 — ELSS Lock-in

1. Filter `tradingsymbol` for the ELSS fund, `trade_type` = BUY.
2. Sort by `trade_date` ascending (FIFO). Calculate lock-in end = `trade_date` + exactly 3 calendar years per entry (per **A2**).
3. If only one lot: "Your [X units] allotted on [date] will unlock on [unlock date]."
4. If multiple lots — show earliest unlocking lot first:
   "Your earliest [X units] (allotted [date]) unlock on [unlock date]. Remaining lots unlock on: [date] ([Y units]), [date] ([Z units])."
5. If earliest lock-in ends today: "Your units will be redeemable from tomorrow. ELSS redemption follows T+1 settlement." (Per **A2**.)

### Rule 2 — Allotment Verification

1. Triggered when mf_order_history shows an order as allotted but units are missing.
2. Check if a trade entry exists here for the matching fund and date.
3. Trade entry exists → units are allotted. Check console_mf_pseudo_holdings (per **A4**) for discrepancy diagnosis.
4. Trade entry missing:
   - NFO (new fund offer): wait for listing + T+1 day.
   - Regular fund: escalate.

### Rule 3 — P&L FIFO Verification

1. List BUY entries sorted by `trade_date` ascending. Match SELL entries against the oldest BUY first (FIFO).
2. Always cross-reference console_mf_external_trades (per **A4**) for any transferred-in units — missing external entries will skew P&L regardless of whether tradebook entries look complete.
3. If calculation still differs after both checks → escalate.


---
---




# SIP MODIFICATION LOG PROTOCOL

---

## Section A: Reference Data

### A1 — Tool Purpose & Scope

- Shows historical modifications for a specific SIP/SWP/STP.
- Requires `public_id` from sip_report as input (field here is `sip_id`, same value). This tool cannot be queried without it.
- All modifications are initiated from the client's device (no system pauses except AMC SIP auto-cancel).
- This tool is the only authoritative source for SIP/SWP/STP pause/modify/delete dates.

### A2 — last_sip_at Distinction

`last_sip_at` in sip_report is the date of the last SIP order execution — not the pause, modification, or deletion date. Never use `last_sip_at` as the pause/modify date.

To find when a SIP was paused/modified/deleted → use `modified_at` from this tool only. If this tool shows no modification entries → the SIP was not paused or modified. Do not infer a modification date from any other field (including `last_sip_at` or `next_sip_date`).

### A3 — Type Translations

| Internal Value | Client-Facing Language |
|---|---|
| sip_edit | "Your SIP was modified" |
| sip_delete | "Your SIP was deleted/cancelled" |
| swp_edit | "Your SWP was modified" |
| swp_delete | "Your SWP was deleted/cancelled" |
| stp_edit | "Your STP was modified" |
| stp_delete | "Your STP was deleted/cancelled" |

Never share raw `type` values with the client.

### A4 — Modification Timing Impact

A modification within 1–2 days of the trigger date means the current instalment will not be placed. The SIP/SWP/STP starts from the next cycle date.

### A5 — Field Rules

**Shareable with client (in plain language):** `type` (translated per **A3**), `modified_at` (date of change).

**Internal reasoning only:** `sip_id` (= `public_id` from sip_report).

**Never share with client:** `client_id`, `status` (null), `swp_status` (null), `timestamp`.

### A6 — Cross-Reference Protocols

| Topic | Refer to |
|---|---|
| Get public_id for this tool | sip_report (`public_id` field) |
| SIP-not-triggered sequential diagnostic | sip_report Rule 1 |
| last_sip_at field (order execution date, not modification) | sip_report |

## Section B: Decision Flow

### Preflight (run on every query)

1. **public_id gate (hard block):** Verify `public_id` is available from sip_report before querying this tool. If not available → fetch sip_report first. Do not query this tool without `public_id` — results will be incorrect or empty.
2. Fetch the SIP modification log using `public_id` as `sip_id`.
3. Apply field protection per **A5**.
4. **Date verification:** When reading `modified_at`, verify the full date (day, month, year) carefully before sharing. Common errors include confusing months or years. Double-check before including in the response.
5. Format dates as DD MMM YYYY.

### Routing Tree

```
Query relates to SIP/SWP/STP modification history →
│
├─ Preflight: public_id available?
│  ├─ NO → Fetch sip_report first (STOP)
│  └─ YES → Continue
│
├─ Modification found near trigger date
│  → Rule 1
│
├─ Client claims they didn't modify
│  → Rule 2
│
├─ No modification entries found
│  → Rule 3
│
└─ General modification history query
   → Translate type per A3, share modified_at
```

### Scope

- Address: SIP/SWP/STP modification history, timing impact on instalments, and modification date verification.

### Fallback

If no entries found → report that no modifications were made and route back to sip_report Rule 1 for continued diagnosis.

---

## Section C: Rules

### Rule 1 — Modification Near Trigger Date

1. Translate `type` to plain language per **A3**.
2. Respond: "Your [SIP/SWP/STP] was [modified/deleted] on [modified_at], within 1–2 days of the execution date. Your current instalment will not be placed. It will start from the next cycle." (Per **A4**.)

### Rule 2 — Client Claims No Change

1. Respond: "Our records show a change was made to your [SIP/SWP/STP] on [modified_at] from your account. SIP changes can only be made from the Coin app or web." (Per **A1** — all modifications initiated from client's device.)
2. Never expose internal IDs or raw field values.

### Rule 3 — No Modification Found

1. Respond: "Our records show no modifications, pauses, or cancellations were made to this [SIP/SWP/STP]."
2. If investigating SIP-not-triggered → route back to sip_report Rule 1 sequential diagnostic (per **A6**) to continue diagnosis (mandate, order status, etc.).
3. Do not infer a modification from any other field (per **A2**).


---




---
