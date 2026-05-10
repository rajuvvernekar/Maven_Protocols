# stp_report

## Description

WHEN TO USE:

When clients:
- Ask about STP status, configuration, or schedule
- Report STP not transferring funds between schemes
- Ask about STP source fund (SWP leg) or target fund (SIP leg)

TRIGGER KEYWORDS: "STP", "systematic transfer", "transfer between funds", "coin"

TAGS: investments

## Protocol

# STP REPORT PROTOCOL

## Section A: Reference Data

### A1 — STP Fundamentals

- STP = SWP (redeem from source fund) + SIP (invest in target fund via mandate).
- Up to 5 target funds per STP.
- STP target fund must already be in client's holdings. Cannot create STP if target fund is not currently held — client must make a lumpsum purchase in the target fund first.
- Scheme name: source fund from `view_swp`, target funds from `view_sips`.

### A2 — STP Trigger Times

| Leg | Trigger Time |
|---|---|
| SWP leg (redemption from source) | 10:10 AM |
| SIP leg — eNACH mandate | 11:00 AM / 1:00 PM / 6:00 PM |
| SIP leg — UPI mandate | 11:10 AM / 1:10 PM / 6:10 PM |

**Post-redemption debit timing:**
- SIP order triggers on the day the SWP redemption is completed; may take up to 1 day from the redemption date if not triggered same day.
- UPI autopay mandate: debit at T+1 from redemption credit date.
- eNACH mandate: debit at T+2 from redemption credit date.

### A3 — T-PIN / DDPI Authorization

To verify DDPI status: check `primary_ddpi_flag` in `get_all_client_data` — Active = DDPI enabled.

| Account Type | Requirement |
|---|---|
| Non-DDPI/POA | Must authorize CDSL T-PIN on the same day the SWP leg is placed, before 3 PM. If missed → order rejected. |
| DDPI enabled | No T-PIN required — automatic debit of units. Recommend as permanent fix. |

### A4 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |
|---|---|
| `created` | STP creation date |
| `modified` | STP last modification date |
| `view_sips` | Target funds |
| `view_swp` | Source fund |

**Non-shareable:**

| Field | Interpretation |
|---|---|
| `status` | true = active, false = paused/cancelled — say "active" or "inactive" |
| `fund_source` | Internal mandate type indicator |
| `mandate_type` | Internal mandate type |
| `id` | Internal STP id — pass as `sip_id` to `sip_modification_log` |
| `name` | Internal |
| `tag` | Internal |
| `trigger_status` | Internal |

### A5 — STP Setup Navigation

To set up an STP on Coin: Dashboard → Mutual Funds → select the source fund (the fund to transfer FROM) in holdings → click the menu icon → select Create STP. The STP must be initiated from the source fund, not the target fund.

## Section B: Decision Flow

### Routing

```
Route by scenario
   ├─ STP not transferring funds / not working → Rule 1
   ├─ STP partially executing / one leg working, one not → Rule 2
   └─ Client can't create STP — target fund missing or setup navigation error → Rule 3
```

### Fallback

If no root cause found after completing all diagnostic steps → escalate to human agent with screenshot.

## Section C: Rules

### Rule 1 — STP Not Working: Sequential Diagnostic

1. **STP status check:**
   Check `status`. If false → STP is currently inactive.

2. **Modification check:**
   Invoke `sip_modification_log` using `id` as `sip_id`. Check for `stp_edit` or `stp_delete` entries within T-2 of the trigger date. If found → cycle was skipped due to modification; will trigger from next cycle.

3. **SWP leg check:**
   Check `view_swp` to get the fund name → invoke `swp_report` for that fund. Check status and redemption execution. If SWP failed → check T-PIN status, pledged units, and available units.

4. **SIP leg check:**
   Check `view_sips` to get the fund name → invoke `sip_report` for that fund. Check status and mandate linkage. If mandate not linked → SIP order will fail.

5. **T-PIN check:**
   Invoke `mf_order_history`. If SWP order rejected with "UNRID" or "UNITS NOT AUTHORISED" → per **A3**: T-PIN authorization must be completed on trigger day between 10:00 AM and 3:00 PM. Direct client to place a fresh redemption request. Recommend DDPI to avoid in future.

6. **Source fund units check:**
   Invoke `console_mf_pseudo_holdings` — check `margin`. Invoke `console_mf_holdings` — check `available`.
   - `margin` > 0 → units pledged; client must unpledge first: Console → Portfolio → Holdings → [fund] → Unpledge.
   - `available` = 0 → no free units for redemption.

### Rule 2 — Partially Executing

Check both legs independently — SWP executing does not confirm STP is working.

1. Invoke `mf_order_history` for SWP leg (variety = regular, transaction_type = SELL) on trigger date — confirm status. Check `order_timestamp` — should be close to SWP trigger time per **A2**.
2. Invoke `mf_order_history` for SIP leg (variety = SIP) on same date — confirm status.

**SWP executed, SIP not yet triggered:**

Check mandate type against post-redemption debit timeline per **A2**.

- Within expected timeline (UPI: T+1, eNACH: T+2 from redemption credit) → inform client; purchase leg will trigger per mandate type.
- Beyond expected timeline → invoke `sip_report` to check mandate linkage and invoke `mandate_debit_report`.

**SWP failed, SIP not triggered:**
Fix SWP first — check T-PIN status, pledged units, insufficient units.

**Both failed:**
Invoke `console_mf_pseudo_holdings` (`margin`) and `console_mf_holdings` (`available`). Check T-PIN status.

**SIP leg repeatedly fails:**

1. Check for recent modifications: get `fund_source` from ‘stp_report’. Compare `created` and `modified` timestamps.
   - If `modified` differs from `created` AND `modified` is within last 5 days → STP was recently modified. Modifications within 5 days of trigger date cause purchase leg to fail for that cycle. Next cycle will execute normally.

2. If no recent modification (or modification older than 5 days), verify funds were debited:
   - Invoke `mandate_debit_report` for debit entries matching the STP trigger date.
   - Get `cashier_reference` from mandate_debit_report.
   - Match `cashier_reference` with `fund_allocation_report` → get respective `order_number`.
   - Match `order_number` with `exchange_order_id` in `mf_order_history`.
   - Verify `fund` in ‘stp_report’ matches `fund` in mf_order_history.
   - If all matches confirmed → funds debited and purchase order placed at AMC; order is being processed.

3. If no entries in mandate_debit_report:
   - Invoke `sip_report` via `view_sips` for mandate linkage status.
   - If no mandate linked → ensure an active mandate is linked to the target fund.
   - If mandate linked but no debit → escalate with STP details, source fund, target fund(s), and "STP purchase leg repeated rejection — mandate linked but no debit attempt found."

### Rule 3 — STP Creation Issues

1. Invoke `console_mf_holdings` to check funds in client's holdings.

**Target fund not in holdings:**
If target fund not present → STP cannot be created per **A1**. Direct client to make a lumpsum purchase in the target fund first; once units appear in holdings, set up STP. STP allows up to 5 target funds — all must be existing holdings before selection.

**Target fund in holdings, setup error:**
Check source fund in `console_mf_holdings`:
- `available` > 0 AND `margin` = 0 → source fund ready; issue is likely navigation. Guide per **A5**.
- `margin` > 0 → unpledge source fund units first: Console → Portfolio → Holdings → [fund] → Unpledge. Then retry.
- `available` = 0 → no available units in source fund; verify source fund selection.

If error persists after correct navigation → escalate with screenshot.
