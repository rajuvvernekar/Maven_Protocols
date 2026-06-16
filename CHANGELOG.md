# Changelog

All protocol changes are logged here. Each entry links back to the proposed_changes file (archived after applying).

## Format
```
### YYYY-MM-DD — tool_name
- [Added/Modified/Removed]: Brief description of change
- Issues resolved: [count]
- Archive: archive/YYYY-MM-DD_tool_name.md
```

### 2026-06-05 — Date range limit bullet added to console_eq_tradebook_prepared

- [Added]: `Date range limit: 100 days per call.` to A1. Completes the date-range coverage from the 2026-06-04 rollout — this tool was in the original error CSV (100-day cap) but omitted from that batch's tool list.

### 2026-06-04 — Feedback batch from "Protocols - Changes to Push (2)" (16 tools + 1 description)

Applied June-1 Protocol-body feedback to 16 tools + a new Description for mandate_report. Team-confirmed final, no regression.

Tools: mf_order_history, account_modification_report, console_mf_pseudo_holdings, kite_margins, kite_order_history, kite_positions, kite_orders, sip_report, console_eq_holdings, pan_status, withdrawal_request, stock_gift_requests, ledger_report, console_instant_pledge, console_eq_tradebook_prepared, console_eq_pnl. Description: mandate_report (WHEN TO USE + TRIGGER KEYWORDS; TAGS retained).

Re-applied this thread's prior work that the June-1 doc predated:
- Re-added `Date range limit` A1 bullets the doc omitted: mf_order_history (180d), kite_order_history (30d), withdrawal_request (30d), console_instant_pledge (30d).
- console_eq_holdings: re-grafted 4 `settlement_date_calculator` invocations the doc dropped (A4 eligibility, Rule 3 t1, Rule 5 T1 rollover, Rule 8 short-delivery auction) — team confirmed these "got missed". Migrated a reverted `console_eq_tradebook` → `console_eq_tradebook_prepared`.
- ledger_report: normalised `Settlement_date_calculator` → lowercase `settlement_date_calculator` (3×). Rule 7/BTST removal (and its calculator ref) is intentional per team; Rule 4/5 retain it.
- console_eq_pnl: migrated reverted `console_eq_tradebook` → `_prepared`.

### 2026-06-04 — Tool-selection improvements (system prompt + get_all_client_data)

Aimed at increasing tool-selection accuracy (reduce stopping early after the default client-data fetch).

**system_prompt.md**
- [Added]: `## Tool Use` section below Voice & Persona — call every relevant available tool; don't stop after `get_all_client_data` if another tool answers part of the query.
- [Modified]: Moved `<thinking_summary>` out of `<response_format>` (now a sibling block, not nested) — it is a separate reasoning-trace channel, not part of the client-facing response.

**miscellaneous/get_all_client_data.md**
- [Removed]: Description block (WHEN TO USE). The tool is now fetched by default from code, so a selection description is redundant — removing it cuts token waste and routing noise. Protocol (field interpretation logic) retained.

### 2026-06-04 — Date range limit handling (11 tools + system prompt)

Tools whose API caps a single call's date range now declare it, and the system prompt defines a bounded retry/chunk strategy so long-range queries don't hard-fail on `ValidationException`.

**system_prompt.md**
- [Added]: `## Date Range Limit Handling` section (between Escalation Output Format and Final Reminder). On a date-range cap or `ValidationException`, fetch the most recent chunk within the cap, backdate for previous chunks, max 3 chunks, merge; escalate if 3 chunks still don't cover the window.

**Per-tool `Date range limit` bullet added to A1:**
- 30 days: console_instant_pledge, withdrawal_request, tradewise_charges_report, kite_order_history, crux_qs_payouts
- 31 days: console_mtf_conversion
- 90 days: delayed_payment_charges
- 100 days: mandate_debit_report
- 180 days: console_mf_tradebook, mf_order_history
- 365 days: mandate_report

### 2026-05-29 — Feedback batch from "Protocols - Changes to Push (1)" (12 tools)

Applied Protocol-body feedback (dated 25th/27th) to 12 tools. All Description blocks preserved (body-only changes). Tools updated: account_modification_report, mf_order_history, ledger_report, console_eq_holdings, amc_charges, kite_margins, kite_positions, kite_holdings, cashier_payins, console_eq_tradebook_prepared, console_eq_pnl, kite_orders.

While applying, re-applied this session's earlier cleanups so the feedback did not regress them:
- Collapsed reintroduced "escalate to a human agent" wording (MF Order History, Kite Holdings) to bare `escalate`.
- Deleted the reintroduced `A10 — Escalation Triggers` Section-A reference block from kite_holdings (the handoff format lives in the system prompt; Section-C "Rule N — Escalation Triggers" rules are untouched).
- `cashier_payin` → `cashier_payins`; `console_eq_tradebook` → `console_eq_tradebook_prepared` (disabled tool).

New: feedback introduces `settlement_date_calculator` as an invokable tool (working-day / holiday-shift computation) across several protocols — kept verbatim per product confirmation that it is now a live tool.

### 2026-05-21 — Escalation handoff consolidation (full rollout, 55 tools)

Completes the consolidation begun in the account_modification_report pilot. System prompt now owns the escalation handoff format; tool rules just say `escalate`.

**Section A sub-section deletions (51 tools)**

Removed the `### Ax — Escalation Output` / `Escalation Required Data` / `Escalation Data` / `Escalation Data Template` / `Escalation Behavior` sub-sections from every tool. 7 of these required downstream A-section renumbering (sections that moved up + all in-body cross-references updated): `console_fno_positions`, `console_fno_pnl`, `console_eq_tradebook_prepared`, `corporate_action_orders`, `console_mtf_holdings`, `console_eq_pnl`, `pan_status`.

**In-rule wording standardised**
- Every escalation directive collapses to `escalate.` / `Escalate.` / `→ escalate`.
- Dropped: "to a human agent" / "to human agent" / "to support agent" / "human support agent" everywhere.
- Dropped trailing qualifiers next to the verb: "with X data", "include X", "per Ax" (referencing now-deleted sections), "for the funds team to check", inline `**HUMAN AGENT ▎ ACTION REQUIRED**` directives.
- Preserved separate sentences and trigger conditionals.

**Files unchanged** (no escalation directives existed): `amc_charges`, `referral_payout`, `get_call_info`, `get_client_contact`, `get_client_interactions`, `st_reports`.

Proposal archived: `archive/2026-05-21_escalation_consolidation.md`.

### 2026-05-21 — Escalation handoff format moved to system prompt (pilot: account_modification_report)

System-level change with a single-tool pilot. Broader rollout to the other 41 tools with their own Escalation Output section is deferred (see `proposed_changes/2026-05-21_escalation_consolidation.md`).

**system_prompt.md**
- [Added]: `## Escalation Output Format` section between Writing Style and Final Reminder. Defines the HOW of escalations: opener literal `HUMAN SUPPORT MANAGER TO HANDLE THIS —`, Checked + Blocker fields, no client-facing voice.

**crm/account_modification_report.md**
- [Modified]: 21 in-rule escalation directives standardised to uniform `escalate.` (or `Escalate.` at sentence start, `→ escalate` in routing trees). Dropped "to human agent" phrasing and per-line qualifiers ("with X", "include X", "without addressing the query") — all of these are now covered by the system prompt's format.

### 2026-05-21 — Batch update (15 tools)

Source: `Protocols - Changes to Push.md`. Protocol bodies rewritten for 15 tools; Description (WHEN TO USE + TRIGGER KEYWORDS) rewritten for 2 tools. Existing TAGS lines preserved. Source-doc bullet typos (`\-Word` with missing space) corrected across 6 files (37 bullets total).

**Description + Protocol updated:**
- kite_positions
- kite_margins

**Protocol-only updated:**
- cashier_payins
- withdrawal_request
- console_eq_holdings
- console_instant_pledge
- mf_order_history
- kite_holdings
- account_modification_report
- amc_charges
- sip_report
- console_mf_pseudo_holdings
- kite_orders
- kite_gtt
- mandate_debit_report

### 2026-04-13 — Batch update (25 tools)

**cashier_payins**
- [Added]: A2 NRI PIS preflight early exit guard (do not use A2 row to frame responses)
- [Added]: A3 alternate bank details (numerical account 57500000302010) for banks rejecting ZERNSE
- [Added]: Rule 2 status note — netbanking "Unknown" = pending, not failed
- [Added]: A8 HDFC eCMS transfer link

**withdrawal_request**
- [Added]: Preflight DETERMINE QUERY DATE step — anchor all analysis to client's query date
- [Added]: A12/A13 Payout Rejection Reasons tables (Regular: 14 reasons, Instant: 11 reasons)
- [Modified]: Rule 2 restructured — bank rejection check (A12/A13) before ledger signals
- [Modified]: Rule 8 — use query date from Preflight, not current date
- [Added]: A4 Standard T+1 response template
- [Modified]: Rule 1, 7, 9, 10 — explicit response templates added

**ledger_report**
- [Added]: A3/A12 MTF interest entry type + identification rule
- [Added]: A11 SGB interest out-of-scope cross-reference + routing
- [Added]: Rule 3 Step 4 — trade breakdown for settlement entries (fetch kite_order_history)
- [Modified]: Rule 8 — complete rewrite with BTST detection (Step 1) + standard response (Step 2)
- [Added]: Rule 16a — MTF Interest Charges (7-step rule for date/range/total/disputes)
- [Modified]: Rule 17 references updated to include 16a
- [Added]: Rule 18 MTF interest dispute escalation trigger

**amc_charges**
- [Modified]: A4 restructured — unified inference table from charge_after_gst + client_holdings
- [Modified]: A5 simplified — BSDA determination now references A4
- [Modified]: Preflight and Rule 3 — use A4 inference table instead of bsda_flag branching

**console_eq_holdings**
- [Added]: A5 Grandfather clause (Section 112A, pre-2018 holdings)
- [Added]: A7 Debt Instrument Interest section (G-Secs, NCDs, Bonds)
- [Added]: A11 NSE/BSE historical price links
- [Added]: R37 Same-day sell FIFO impact, R38 Grandfather clause, R39 Short delivery, R40 G-Sec interest
- [Added]: Route — employer-mandated account deactivation → escalate to human agent
- [Added]: Route — Rule 14 broadened to "Dividend & Debt Instrument Interest"
- [Modified]: Rule 1 step 3 — same-day sell FIFO check (R37)
- [Modified]: Rule 2.1.g — grandfather clause path (R38)
- [Modified]: Rule 6 — Console visibility mention for inactive/unlisted stocks
- [Modified]: Rule 15 step 5 — short delivery explanation (R39)

**console_eq_external_trades**
- [Modified]: Rule 2 step 3 — added sub-case c for wrong entry details (client mistake)

**console_instant_pledge**
- [Added]: A5 F&O segment not active failure reason
- [Added]: A6 Account Modification tool cross-reference
- [Added]: R14 F&O segment not active response, R15 LAS query routing
- [Added]: Route — LAS queries out of scope
- [Modified]: Rule 3 step d — F&O segment check via Account Modification tool

**console_mtf_holdings**
- [Modified]: A7 MTF interest statement path corrected (Reports → Funds)
- [Added]: A7 full-year statement unavailability disclaimer
- [Added]: R17 Same-day sell and re-buy netoff (EQ category)
- [Added]: Rule 5 step 4 — same-day sell/re-buy diagnostic

**kite_orders**
- [Added]: A12 Multiple sell orders margin rejection row + CO on ETF row
- [Added]: R24 Negative opening balance rejection, R25 Multiple sell orders rejection
- [Modified]: Rule 4 — structured margin rejection flow (negative opening_balance first)
- [Modified]: Rule 9 — cross-reference to kite_positions Rule 11 for ban delta rules

**kite_holdings**
- [Modified]: A12 Short delivery campaign search now includes "Upper Circuit"
- [Modified]: Route Rule 2 broadened to cover portfolio valuation/invested amount
- [Added]: Rule 2 Step 0 — portfolio/invested value investigation
- [Modified]: Rule 5 — explicit short delivery investigation instructions

**kite_positions**
- [Added]: A14 F&O Ban Period Delta Rules (position-type to allowed/blocked trade matrix)
- [Added]: R27 F&O ban period delta rules response
- [Added]: Preflight Step 4 — historical trade queries redirect to kite_order_history
- [Added]: Rule 7 Step 0 — index vs stock F&O check (prevents physical delivery for index)
- [Added]: Rule 11 — F&O ban period delta exposure rules
- [Modified]: Rule 3 — upper circuit short delivery cross-refs Holdings A12

**kite_margins**
- [Modified]: Rule 2 — negative opening_balance flagged prominently with option_premium context

**get_all_client_data**
- [Added]: A2 Interactions/Communications tabs off-limits; Documents tab access rules
- [Added]: Preflight Step 3a — third_party_demat escalation
- [Removed]: A7 Bank Field Mapping section
- [Removed]: 4 routing entries (Bank details, Withdrawal, Payin, Fund transfer)

**account_modification_report**
- [Added]: New trigger keywords for segment activation issues
- [Modified]: A2 DDPI charge expanded to online + offline
- [Added]: A4 Commodity segment cross-check (zbl_mcx + nse_com)
- [Added]: A12 ReKYC Process Details (Aadhaar OTP vs eSign)
- [Added]: Preflight third_party_demat escalation
- [Modified]: Rule 4 — pre-check for existing closure request
- [Modified]: Rule 6 — F&O-only dormancy handling expanded

**tradewise_charges_report**
- [Modified]: A2 Delivery brokerage corrected — ₹0 for Individual only
- [Added]: A6 Non-Standard Account Brokerage (Non-Individual, NRI PIS, NRI Non-PIS rates)
- [Added]: Preflight Step 1A — get_all_client_data for account type
- [Modified]: Rule 3 — complete rewrite for account-type-aware verification

**console_mf_pseudo_holdings**
- [Added]: A1 Regular plan holdings rule
- [Added]: A3 Payout dividend + discrepant → immediate escalation
- [Modified]: A4 Delay allotment rewrite — T+3 working days, exchange_timestamp reference
- [Added]: A4 Steps 1a, 1b for allotted-but-not-updated and escalation
- [Modified]: A8 split into A8a (non-demat) + A8b (demat CDSL Easiest transfer)
- [Added]: A9 Response templates R1/R2 for delay allotment
- [Modified]: Rule 5 — Silo K collateral margin timing
- [Modified]: Rule 7 — expanded for demat + non-demat MF transfers
- [Added]: Rule 9 — LAS queries out of scope

**mandate_debit_report**
- [Added]: A7 Bank penalty charges fact
- [Added]: Rule 5 Bank-applied penalty charges handling

**mf_order_history**
- [Added]: A2 Working day check, Holiday shift scope, Naming holidays subsections
- [Modified]: A7 `tag` field moved from Banned to Internal (for NFO detection)
- [Added]: A8 T+3 allotment timeline fact
- [Modified]: Rule 1 — NFO detection via `tag` field; SIP mandate check; settled_flag=N order_number null check
- [Modified]: Rule 3 — expanded with SIP mandate checks
- [Added]: Rule 11 — Duplicate/extra payment claims
- [Modified]: Field usage — `payment_method` replaces `fund_source` for bank identification

**sip_report**
- [Added]: A1 UPI trigger timing clarification (T-1 vs T-2)
- [Added]: A4 `rp-pg` fund_source value
- [Modified]: A5 Diagnostic sequence reordered — modification check moved to Step 2
- [Modified]: A6 FRESH processing — SIP skip logic when next_sip_date before allotment

**pan_status**
- [Added]: R5 "Name mismatch, client states ITD already updated" template
- [Modified]: Preflight — use Zerodha's registered name, not client's stated name
- [Modified]: Rule 1 — conditional branching to R5 when client says ITD updated

**Unchanged tools:** console_mf_external_trades, console_mf_holdings, console_mf_tradebook, swp_report, stp_report

### 2026-03-09 — account_modification_report
- [Modified]: Rule 3 — Added second CRITICAL: cross-reference actual segment fields in get_all_client_data before communicating activation status
- [Modified]: Rule 6 — Added raw segment identifiers (NSE_COM, NSE_FO, BSE_EQ, MCX_FO) to banned fields; added NSE_COM → "NSE Commodity" translation
- [Modified]: Rule 7 `Activated` — Made timestamp check mandatory for 0 funds/order rejection; added "do NOT state any other reason" guard
- [Modified]: `<nomination>` KB — Added online/offline modification paths, ReKYC ban, support article link
- [Modified]: Rule 10 — Added explicit ReKYC ban for nominee modifications with support article redirect
- [Modified]: `<account_closure>` KB — Simplified post_closure_new_account_error escalation text
- Issues resolved: 4

### 2026-03-09 — withdrawal_request
- [Modified]: `<facts>` — Replaced primary-only bank rule with multi-bank withdrawal support (primary, secondary, tertiary); added penny-drop verification requirement for non-primary accounts
- [Added]: `<bank_update_links>` — Added `<bank_verification>` link for account verification steps
- [Added]: Rule 15 — Unresolved Fallback for all withdrawal types (screenshot request when no root cause identified)
- [Modified]: Rule 8 Step 3 — Screenshot fallback now references Rule 15 instead of inline text
- Issues resolved: 3

---

### 2026-03-06 — ledger_report
- [Modified]: `<facts>` — Added T+1 settlement grouping rule; distinct settlement numbers per trading day; share settlement numbers only when explicitly asked
- Issues resolved: 1

### 2026-03-06 — kite_order_history
- [Modified]: `<field_usage>` — Moved `gtt` and `app_id` from banned to internal for GTT origin verification
- [Modified]: Rule 0 — Updated field protection to document `gtt` and `app_id` internal usage
- [Modified]: Rule 1 — Added GTT field check step; scope investigation to trigger date only
- Issues resolved: 1

### 2026-03-06 — kite_gtt
- [Modified]: Rule 3.3 — Anchor order investigation to GTT trigger date only; use `gtt` field for order linkage confirmation; do not attribute subsequent orders to GTT
- Issues resolved: 1

---

### 2026-03-06 — account_modification_report
- [Added]: `<facts>` — ReKYC auto re-enables Coin/MF bullet
- [Added]: `<account_closure>` — `<post_closure_new_account_error>` tag (escalate to human agent)
- [Modified]: Rule 3 — Added explicit contact detail timeline example (mobile/email → activation)
- [Modified]: Rule 4 — Mandatory pre-check for existing ReKYC request before giving guidance; rejected ReKYC escalates to KYC team
- [Added]: Rule 5 — Post-closure new account error handling (escalate to agent)
- [Modified]: Rule 7 Dormancy step 3 — Coin/MF excluded from segment activation guidance; added get_all_client_data cross-check
- Issues resolved: 4

---

### 2026-03-12 — mf_order_history
- [Modified]: Cancel status value — added allotment guard
- [Modified]: Rule 0 — removed redundant example for token efficiency
- [Modified]: Rule 0.1 — added multiple orders for same fund handling
- [Modified]: Rule 1 — expanded Cancel status with payment_confirmed breakdown
- [Modified]: Rule 2 Step 1 — expanded NFO check with allotment/listing flow
- [Modified]: Rule 2 Step 3 — added payment_updated_at not-available case
- [Modified]: Rule 2 Step 4 — split settled_flag=N into within-T+1 vs beyond-T+2
- [Modified]: Rule 2.5 — fund-by-fund initial investment check with FRESH order status
- [Modified]: Rule 4 — added ledger guard for MF payment confirmation
- [Added]: Rule 6 — CDSL authorization loop (repeated OTP redirect) handling
- [Modified]: Rule 16 — simplified NRI exit load handling
- Issues resolved: 11
- Archive: archive/2026-03-12_mf_order_history.md

### 2026-03-12 — fund_allocation_report
- [Added]: Facts — settled_flag and allotment_flag definitions
- [Modified]: Rule 1 — split settled_flag=N into within-T+1 vs beyond-T+2 with refund_utr check
- [Modified]: Rule 2 — updated refund response to keep date_of_refund, added no-hallucination guard and no 5-7 day disclaimer when refund already initiated
- Issues resolved: 3
- Archive: archive/2026-03-12_fund_allocation_report.md

### 2026-03-12 — sip_report
- [Modified]: Rule 1 Step 1 — reordered to check pseudo_holdings first, added multi-SIP per-fund handling
- [Added]: Rule 1 Step 6.7 — stale next_sip_date check for all SIP frequencies
- [Added]: Rule 4 — NRI PIS Account mandate restriction
- [Modified]: Rule 6 — simplified escalation wording
- Issues resolved: 4
- Archive: archive/2026-03-12_sip_report.md

### 2026-03-12 — stp_report
- [Modified]: Rule 5 — minor wording clarification
- [Added]: Rule 6 — STP setup error / source fund navigation flow
- Issues resolved: 2
- Archive: archive/2026-03-12_stp_report.md

### 2026-03-06 — Initial Setup
- All 62 tool protocols extracted from Maven CSV export
- Repository structure created
- Categories: Console Reports (15), MF Reports (13), CRUX Reports (13), Kite Admin (7), CRM (4), Cashier Reports (4), Miscellaneous (5)
- System prompt extracted to root level
- Tools with sparse/no protocol: demat_freeze_status, referral_payout, conditional_orders, get_client_contact, get_client_interactions, st_reports, get_call_info
