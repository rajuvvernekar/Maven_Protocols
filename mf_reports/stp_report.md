# stp_report

## Description

WHEN TO USE:

When clients:
- Ask about STP status, configuration, or schedule
- Report STP not transferring funds between schemes
- Ask about STP source fund (SWP leg) or target fund (SIP leg)

TRIGGER KEYWORDS: "STP", "systematic transfer", "transfer between funds", "coin"

## Protocol

# STP REPORT PROTOCOL


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
