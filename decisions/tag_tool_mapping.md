# Maven Tag → Tool Mapping — Final (MAVEN-12)

Single source of truth. Supersedes `tag_tool_mapping_proposal.md` and `tag_tool_mapping_validation.md`. Backed by 5,779 tickets across 5 Support Assist Feedback CSVs (54% up / 46% down).

## Why this exists

Ponnuru flagged wrong-tool selection in MAVEN-12. Two-step fix:
1. Sharpen the 18 tag descriptions in beta-supporttools → better tag prediction (pipeline stage 4).
2. Inside each tool's `## Description` block, list the 1–3 tags that tool serves → tool selection (stage 5) gets a tighter shortlist when the tag fires.

## Action checklist

1. **Step 1** — Sharpen 11 of the 18 tag descriptions (beta-supporttools UI).
2. **Step 2** — Confirm the 5 utility tools are in `always_include` (engineer task, blocking step before Step 3).
3. **Step 3** — Add `TAGS:` line to each of the 55 mappable tool descriptions in maven-protocols.
4. **Step 4** — Send 6 underperforming tools to the protocol owner for description rewrites (independent of tagging).
5. **Step 5** — Resolve 3 open questions before merging.

---

## Step 1 — Tag description edits (11 of 18 tags)

Apply these in beta-supporttools at https://beta-supporttools.zerodha.net/app/maven-interaction-tag/view/list. Numbers in brackets are bad-rating evidence from the 5,779 ticket dataset.

### 1.1 `funds` — disambiguate "mandate" from MF mandate [165 bad]
**Add:** *"Excludes MF SIP/ZSIP mandates (use `investments`). This is for cashier eMandates that auto-debit money into the Kite trading balance."*

### 1.2 `investments` — disambiguate Coin errors from `platform` [38 bad]
**Replace** *"MF-specific login issues, Coin platform errors"* **with** *"Coin app errors that block an MF action (mandate creation, SIP placement, redemption). Generic platform/app crashes that aren't MF-specific go to `platform`."*

### 1.3 `orders` — disambiguate stock SIP from MF SIP [206 bad]
**Replace** *"bids, stock SIP"* **with** *"bids, stock SIP (Kite equity SIP only — MF SIP/ZSIP goes to `investments`)."*

### 1.4 `corporate-actions` — disambiguate from `orders` [20 bad]
**Add:** *"Includes the order placed for the CA (buyback application, rights bid). A 'buyback order rejected' query is `corporate-actions`, not `orders`."*

### 1.5 `platform` — broaden the exclusion (last-resort guard) [290 bad — top remarks: "Not related" 92×, "query was about funds payin" 12×]
**Replace** *"app crashes, UI glitches, funds page field explanations"* **with** *"app crashes and UI glitches that aren't tied to a specific business action. If the query is about a payin/payout/mandate/QS/MF/holdings/order operation that happens to be on a screen, use the relevant business tag, not `platform`. Use `platform` as the last resort when nothing else fits."*

### 1.6 `nri` — restrict to NRI operations [144 bad — "resident individual" 14×]
**Add:** *"Customer must hold an NRE/NRO/NRI account, OR the query must be about an NRI-specific operation (PIS, NRE-NRO conversion, repatriation, NRI AMC). Resident-Indian customers whose payment happens to be from an NRO bank are NOT `nri`."*

### 1.7 `non-individual` — restrict to corporate accounts [92 bad — "Individual account" / "Resident Individual" 6×]
**Add:** *"The Zerodha account itself must be company/HUF/LLP/Partnership. Individual accounts asking generic questions are NOT `non-individual`."*

### 1.8 `ipo` — exclude rights/FPO/OFS/NFO [51 bad — 31.7% bad rate]
**Add:** *"`ipo` = mainboard or SME equity IPO bidding/allotment only. Rights issue, FPO, OFS go to `corporate-actions`. MF NFO and MF refund/allotment go to `investments`."*

### 1.9 `compliance` — exclude KYC/charges [83 bad — "REKYC" 4×]
**Add:** *"`compliance` requires an external notice (exchange surveillance, SEBI circular, legal/arbitration, fraud/PMLA, unauthorised trade). KYC/ReKYC issues are `account`. Brokerage/charge disputes are `charges`."*

### 1.10 `general` — last-resort guard [197 bad — "Not related" 67×]
**Add:** *"Use only when the query genuinely doesn't map to any other tag. If the query mentions a specific operation, use the operation's tag instead. Do not use as a default."*

### 1.11 `settlement` — separate from QS payout [178 bad — "funds payin" 6×, "withdrawal" 4×]
**Add:** *"`settlement` = exchange settlement (T+1/T+2/BTST/auction/short-delivery/physical/sale-credit). Quarterly settlement (QS) is `funds`. Payment-method failures are `funds`."*

The remaining 7 tags (`account-closure`, `account`, `holdings`, `margins`, `reports`, `charges`, `demat`) have ≤11% bad rates — leave alone.

---

## Step 2 — Confirm utility tools in `always_include`

These 5 tools must NOT be tag-gated. They're universal context (`get_all_client_data` alone fires on 94% of tickets).

- `get_all_client_data`
- `get_call_info`
- `get_client_contact`
- `get_client_interactions`
- `st_reports`

**Engineer action:** verify all 5 are in the deployment-owned `always_include` list before Step 3 ships. If missing, add them. If they aren't always-included and we add `TAGS:` lines to other tools, these utilities will get starved.

---

## Step 3 — Tool description tag mapping (55 tools)

Append a `TAGS:` line at the bottom of each tool's `## Description` block, after `TRIGGER KEYWORDS:`. Format:

```
TAGS: orders, holdings
```

Primary tag first. Max 3. Use the slugs verbatim.

### Console Reports (15 tools)

| Tool | TAGS |
|---|---|
| console_eq_external_trades | `holdings`, `demat` |
| console_eq_holdings | `holdings`, `demat`, `corporate-actions` |
| console_eq_pnl | `reports`, `holdings` |
| console_eq_pseudo_holdings | `holdings` |
| console_eq_holdings_breakdown | `holdings`, `demat` |
| console_mtf_holdings | `margins`, `holdings` |
| console_eq_tradebook | `orders`, `reports` |
| console_eq_tradebook_prepared | `orders`, `reports` |
| console_fno_pnl | `reports`, `holdings` |
| console_fno_positions | `holdings` |
| console_fno_tradebook | `orders`, `reports` |
| console_fno_tradebook_prepared | `orders`, `reports` |
| corporate_action_orders | `corporate-actions`, `orders` |
| console_instant_pledge | `margins` |
| console_mtf_conversion | `margins`, `holdings` |

### MF Reports (13 tools)

| Tool | TAGS |
|---|---|
| console_mf_holdings | `investments`, `holdings` |
| console_mf_tradebook | `investments`, `reports` |
| console_mf_external_trades | `investments`, `holdings` |
| console_mf_pseudo_holdings | `investments`, `holdings` |
| mf_order_history | `investments` |
| sip_report | `investments` |
| mandate_debit_report | `investments`, `funds` |
| mandate_report | `investments`, `funds` |
| fund_allocation_report | `investments`, `funds` |
| sip_modification_log | `investments` |
| swp_report | `investments` |
| stp_report | `investments` |
| conditional_orders | `investments` |

### CRUX Reports (13 tools)

| Tool | TAGS |
|---|---|
| ledger_report | `funds`, `charges`, `reports` |
| withdrawal_request | `funds` |
| delayed_payment_charges | `charges`, `margins` |
| pledge_request_report | `margins` |
| tradewise_charges_report | `charges`, `reports` |
| ipo_application | `ipo` |
| client_retention_dates | `funds` |
| stock_gift_requests | `general` |
| stock_transfers | `demat` |
| contract_note_charges | `charges`, `reports` |
| crux_qs_payouts | `funds` |
| amc_charges | `charges` |
| demat_freeze_status | `demat` |

### Kite Admin (7 tools)

| Tool | TAGS |
|---|---|
| kite_orders | `orders`, `margins` |
| kite_holdings | `holdings`, `demat`, `corporate-actions` |
| kite_positions | `holdings`, `margins` |
| kite_margins | `margins` |
| kite_gtt | `orders` |
| kite_order_history | `orders` |
| kite_gtt_archived | `orders` |

### CRM (4 tools)

| Tool | TAGS |
|---|---|
| account_modification_report | `account`, `nri`, `non-individual` |
| minor_account_opening | `account` |
| referral_payout | *(none — partner queue, outside taxonomy)* |
| pan_status | `account` |

### Cashier Reports (4 tools)

| Tool | TAGS |
|---|---|
| cashier_payins | `funds` |
| auto_debit_payins | `funds`, `investments` |
| e_mandate_report | `funds` |
| e_mandate_schedule_report | `funds`, `investments` |

### Miscellaneous (5 tools) — UNMAPPED on purpose

| Tool | TAGS | Why |
|---|---|---|
| get_all_client_data | *(none)* | Always-include utility (94% of tickets). |
| get_call_info | *(none)* | Always-include utility. |
| get_client_contact | *(none)* | Always-include utility. |
| get_client_interactions | *(none)* | Always-include utility. |
| st_reports | *(none)* | Always-include utility. |

### Tags that map to NO tool (6 of 18)

`account-closure`, `platform`, `general`, `settlement`, `compliance`, `nri` — informational/process tags. The system prompt + handoff path handles these. Forcing tools onto them re-introduces the wrong-selection problem.

(`compliance` and `nri` are also referenced in `account_modification_report` for non-routine cases; otherwise unmapped.)

---

## Step 4 — Tools that need protocol review (out of scope here)

These 6 tools have low upvote rates that no tag-mapping fix will repair. Send to the protocol owner.

| Tool | Up % | Vol | What's wrong | Suggested description fix |
|---|---:|---:|---|---|
| `get_client_contact` | 3.1% | 32 | Picked for "send me CMR / send me email"; only returns contact info. | "look up email/phone for outbound communication, NOT for sending statements". |
| `console_eq_tradebook_prepared` | 10.9% | 55 | Picked for sub-100-day requests where regular tradebook would do. | Lead with "Use only when date range > 100 days". |
| `corporate_action_orders` | 11.1% | 18 | Picked for general CA questions; tool is for status checks of existing applications. | "checks status of existing CA orders only — not for how-to/eligibility questions". |
| `swp_report` | 15.6% | 32 | Confused with cashier `withdrawal_request`. | Lead with "MF SWP only — not for trading-account withdrawal". |
| `console_mf_external_trades` | 24.3% | 37 | Confused with regular MF holdings tools. | "externally-bought MF units only (units bought outside Coin and visible in Coin)". |
| `auto_debit_payins` | 33.3% | 27 | Confused with `cashier_payins` and `e_mandate_report`. | Distinguish: this = mandate-debit attempt status; cashier_payins = manual payin; e_mandate_report = mandate creation/cancellation. |

---

## Step 5 — Open questions before applying

1. **Where does the `TAGS:` line live structurally?** I put it inside `## Description`. If the Maven Frappe schema has a separate "tags" field, it should go there instead.
2. **Is stage-4's predicted tag actually plumbed into stage-5's selector today?** The mapping only delivers value if the selector either receives the predicted tag OR the descriptions literally contain the tag string so the selector LLM picks up on it.
3. **`referral_payout` — does it need a partner-queue tag outside the 18?** It's the only tool wholly outside the taxonomy.

---

## Roll-out order (least risk first)

1. Tag description edits (Step 1) — UI-only, low blast radius. Watch tag-prediction logs for 24h, expect drop in misclassification on the 4 high-bad tags.
2. `always_include` audit (Step 2) — engineer task. Blocking for Step 3.
3. `TAGS:` lines in tool descriptions (Step 3) — ship in batches per category so any regression is bisectable.
4. Open questions (Step 5) — answer in parallel with Step 3.
5. Tool-protocol review (Step 4) — separate workstream, hand off to owner.
