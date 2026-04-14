# console_mf_tradebook

## Description

WHEN TO USE:

When clients:
- Ask about ELSS lock-in period or when they can redeem ELSS
- Report order shows Allotted but units missing
- Ask about exact NAV/price at which units were allotted
- Need P&L verification using FIFO
- Ask about trade entry existence for allotted/redeemed orders

TRIGGER KEYWORDS: "lock-in", "ELSS unlock", "when can I redeem ELSS", "allotment date", "trade date", "FIFO", "allotted but not visible", "coin"

## Protocol

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


# SWP REPORT PROTOCOL

---

## Section A: Reference Data

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

### Fallback

If no root cause found after completing all diagnostic steps → suggest manual redemption and escalate if issue recurs.

---

## Section C: Rules

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
---




# STP REPORT PROTOCOL

---

## Section A: Reference Data

### A1 — STP Fundamentals

- STP = SWP (redeem from source fund) + SIP (invest in target fund via mandate).
- Up to 5 target funds per STP.
- STP target fund must already be in client's holdings. Cannot create STP if target fund is not currently held — client must make a lumpsum purchase in the target fund first.
- Available on Coin web only (coin.zerodha.com) — not the app.
- Scheme name: source fund from `view_swp`, target funds from `view_sips`.

### A2 — STP Trigger Times

| Leg | Trigger Time |
|---|---|
| SWP leg (redemption from source) | 10:10 AM |
| SIP leg — eNACH mandate | 11:00 AM / 1:00 PM / 6:00 PM |
| SIP leg — UPI mandate | 11:10 AM / 1:10 PM / 6:10 PM |

**Post-redemption debit timing:** The SIP order triggers on the day the redemption is completed. If the SIP order was not triggered on that day, it may take up to 1 day from the redemption date. After the redemption amount is credited to the client's bank account, the mandate debit timing depends on the mandate type: UPI autopay = T+1 day from redemption credit; eNACH = T+2 days from redemption credit. When the SWP leg has executed but the SIP leg has not yet triggered, inform the client of this timeline.

### A3 — T-PIN / DDPI Authorization

| Account Type | Requirement |
|---|---|
| Non-DDPI/POA | Must authorize CDSL T-PIN on the same day the SWP leg is placed, before 3 PM. If missed → order rejected. |
| DDPI enabled | No T-PIN required — automatic debit of units. Recommend as permanent fix. |

### A4 — Field Rules

**Shareable with client:** `created`, `modified`, `view_sips` (target funds), `view_swp` (source fund).

**Internal reasoning only:** `status` (deprecated boolean: true = active, false = paused/cancelled — say "active" or "inactive" to client), `fund_source`, `mandate_type`.

**Never share with client:** `id`, `name`, `tag`, `trigger_status`.

### A5 — STP Not Working: Diagnostic Sequence

Run these checks in order:

| Step | Check | Condition | Action |
|---|---|---|---|
| 1 | STP status | `status` = false | Inactive. Inform client. |
| 2 | Recent modification | Get `id` → pass as `sip_id` to sip_modification_log. Check for stp_edit/stp_delete. | If modified within T-2 of trigger → "This cycle was skipped due to modification." |
| 3 | SWP leg | Check swp_report (via `view_swp`) for trigger/next instalment | If SWP issue found → diagnose per SWP Report protocol |
| 4 | SIP leg | Check sip_report (via `view_sips`) for status + mandate linkage | If SIP issue found → diagnose mandate/linkage |
| 5 | Mandate | Check mandate_report for mandate status | If SIP leg has no mandate → purchase leg won't execute |
| 6 | T-PIN | SWP order rejected with "UNRID" or "UNITS NOT AUTHORISED" | Guide per **A3**. "Complete T-PIN between 10:00 AM and 3:00 PM on trigger day. Recommend enabling DDPI." |
| 7 | Units | Check console_mf_pseudo_holdings (`margin`) and console_mf_holdings (`available`) for source fund | `margin` > 0 → pledged, unpledge first. `available` = 0 → no free units. |

### A6 — Partial Execution Diagnosis

Always check both legs independently before concluding:

| Finding | Diagnosis | Action |
|---|---|---|
| SWP executed, SIP not yet triggered | If within debit timeline per **A2** (UPI: T+1, eNACH: T+2 from redemption credit), this is expected timing — inform client. If beyond timeline, check sip_report mandate linkage + mandate_debit_report | Check mandate type first per **A2** debit timing. If beyond expected timeline, check sip_report mandate linkage + mandate_debit_report |
| SWP failed, SIP not triggered | Source fund issue — fix SWP first | Check T-PIN status, pledged units, insufficient units |
| Both failed | Source fund + authorization issue | Check console_mf_pseudo_holdings (margin), console_mf_holdings (available), T-PIN status |

Never conclude STP is working based on the SWP leg alone. Both legs must be verified independently.

### A7 — STP Setup Navigation

To set up an STP on Coin web: Dashboard → Mutual Funds → select the **source fund** (the fund to transfer FROM) in holdings → click the menu icon → select Create STP. The STP must be initiated from the source fund, not the target fund.

### A8 — Cross-Reference Protocols

| Topic | Refer to |
|---|---|
| STP modification history | sip_modification_log (use `id` as `sip_id`; look for stp_edit/stp_delete) |
| SWP leg status and diagnostics | swp_report (via `view_swp`) |
| SIP leg status and mandate linkage | sip_report (via `view_sips`) |
| Mandate status | mandate_report |
| Mandate debit attempts | mandate_debit_report |
| Source fund pledged units (`margin`) | console_mf_pseudo_holdings |
| Source fund available units (`available`) | console_mf_holdings |
| Order status for both legs on trigger date | mf_order_history (SWP leg: variety = SWP; SIP leg: variety = SIP) |

## Section B: Decision Flow

### Preflight (run on every query)

1. Fetch the STP report for the client.
2. Apply field protection per **A4** — identify shareable, internal, and banned fields.
3. Translate `status` boolean: true → "active"; false → "inactive".
4. Note `id` for potential sip_modification_log lookup.
5. Format dates as DD MMM YYYY.

### Routing Tree

```
Query relates to STP →
│
├─ STP not transferring funds / not working
│  → Rule 1 (Full diagnostic per A5)
│
├─ STP partially executing / one leg working, one not
│  → Rule 2 (Both legs per A6)
│
├─ Client can't find STP on app
│  → Rule 3
│
├─ Client can't create STP / target fund not selectable
│  → Rule 4
│
├─ STP setup error / can't find Create STP option
│  → Rule 5
│
└─ General STP status query
   → Check data, respond with shareable fields
```

### Scope

- Address: STP trigger issues (both legs), partial execution diagnosis, setup guidance, and T-PIN/mandate requirements.

### Fallback

If no root cause found after completing all diagnostic steps → escalate with screenshot.

---

## Section C: Rules

### Rule 1 — STP Not Working: Sequential Diagnostic

1. Run through all steps in **A5** in order.
2. Step 1: check `status`. If false → "Your STP is currently inactive."
3. Step 2: check sip_modification_log via `id` (per **A8**) for stp_edit/stp_delete near trigger. If modified within T-2 → "This cycle was skipped."
4. Step 3: check SWP leg via swp_report (per **A8**). Diagnose trigger/next instalment.
5. Step 4: check SIP leg via sip_report (per **A8**). Diagnose status + mandate linkage.
6. Step 5: check mandate_report (per **A8**). If no mandate → "The purchase leg requires an active mandate for auto-debit."
7. Step 6: if SWP order rejected with "UNRID" or "UNITS NOT AUTHORISED" → respond per **A3**: "CDSL T-PIN authorization must be completed on the same day the SWP leg triggers, between 10:00 AM and 3:00 PM. Since it was not completed on time, the order was rejected. Place a fresh redemption request. To avoid this in future, enable DDPI."
8. Step 7: check source fund — console_mf_pseudo_holdings for `margin` and console_mf_holdings for `available` (per **A8**). If pledged → "Unpledge first: Console → Portfolio → Holdings → [fund] → Unpledge." If no available units → inform client.

### Rule 2 — Partially Executing

1. Always check both legs independently before concluding (per **A6**).
2. Check mf_order_history (per **A8**) for SWP leg (variety = SWP) on trigger date → confirm status.
3. Check mf_order_history for SIP leg (variety = SIP) on same date → confirm status.
4. If SWP executed but SIP not yet triggered → first check the mandate type and compare against the post-redemption debit timeline in **A2** (UPI: T+1, eNACH: T+2 from redemption credit). If within the expected timeline, inform the client: "Your redemption has been processed. The purchase leg debit depends on your mandate type — [UPI autopay debits on the next day / eNACH debits within 2 days] after the redemption amount is credited to your bank." If beyond the expected timeline, diagnose using the findings matrix in **A6**.
5. Diagnose other scenarios using the findings matrix in **A6**:
   - SWP failed, SIP not triggered → fix SWP first (T-PIN, pledged, insufficient units).
   - Both failed → check source fund units and T-PIN status.

**Step 5 — STP Purchase Leg Repeated Rejections (if SIP leg repeatedly fails):**

When the SIP leg (purchase) of an STP repeatedly fails:

1. **Check for recent modifications:** Get `fund_source` value from stp_report. Compare `created` and `modified` timestamps.
   - If `modified` differs from `created` AND `modified` is within the last 5 days from current date → "Your STP was recently modified. Modifications within 5 days of a trigger date cause the purchase leg to fail for that cycle. The next cycle will execute normally."

2. **If no recent modification** (or modification is older than 5 days), verify funds were debited and order placed at AMC:
   - Check mandate_debit_report for the latest debit entries matching the STP trigger date.
   - Get `cashier_reference` from mandate_debit_report.
   - Match `cashier_reference` with fund_allocation_report → get the respective `order_number`.
   - Match `order_number` (from fund_allocation_report) with `exchange_order_id` in mf_order_history.
   - Verify the `fund` field in stp_report matches the `fund` field in mf_order_history.
   - If all matches confirmed → "The funds were debited from your mandate and the purchase order was placed at the AMC. The order is being processed."

3. **If no entries in mandate_debit_report** (no debit attempt found):
   - Check sip_report (via `view_sips` from stp_report) for mandate linkage status.
   - If no mandate linked → "The SIP leg of your STP requires an active mandate for auto-debit. Please ensure a mandate is linked to the target fund."
   - If mandate linked but no debit → escalate to support agent with STP details, source fund, target fund(s), and "STP purchase leg repeated rejection — mandate linked but no debit attempt found."

### Rule 3 — Web Only

1. Respond: "STP is available on Coin web (coin.zerodha.com) only, not the app." (Per **A1**.)

### Rule 4 — Target Fund Not in Holdings

1. Respond: "STP cannot be created unless the target fund is already in your holdings. Please make a lumpsum purchase in [target fund] first. Once the units are allotted and appear in your Coin holdings, you can proceed to set up the STP." (Per **A1**.)
2. Note: STP allows up to 5 target funds — all must be existing holdings before they can be selected.

### Rule 5 — STP Setup Error: Source Fund Navigation

1. Confirm: target fund is already in holdings (if not → Rule 4).
2. Check console_mf_holdings for the intended source fund (per **A8**):
   - `available` > 0 AND `margin` = 0 → source fund is ready. Issue is likely navigation. Guide per **A7**: "To set up an STP on Coin web, go to Dashboard → Mutual Funds → select the source fund (the fund you want to transfer FROM) in your holdings → click the menu icon → select Create STP. The STP must be initiated from the source fund — not the target fund."
   - `margin` > 0 → "Please unpledge units in [source fund] first before creating an STP: Console → Portfolio → Holdings → [fund] → Unpledge. Once unpledged, try creating the STP again."
   - `available` = 0 → "The fund you are trying to transfer from has no available units. Please check the source fund selection."
3. If error persists after correct navigation → escalate with screenshot.
