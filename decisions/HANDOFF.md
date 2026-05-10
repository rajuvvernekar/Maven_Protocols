# Maven auto-tagging + protocol cleanup — handoff

Single entry point for another Claude Code session to pick up this work. Read this first, then the linked files only as needed.

## What this is

Two intertwined workstreams for **Zerodha Maven** (the AI agent that uses MCP to connect an LLM to internal support tools):

1. **MAVEN-12 (Ponnuru's ask):** Wrong-tool selection. Two-step fix — sharpen the 18 ticket tag descriptions in beta-supporttools (so the tag predictor classifies right), then add tag→tool links to each tool's description (so the tool-selection LLM gets a tighter shortlist).
2. **Protocol cleanup:** A 54-protocol Google-Docs export (`Cleaned Protocols (2).md`) that needs its escapes stripped, structural quirks fixed, and contents pushed into the per-tool files in the `maven-protocols` git repo.

The two streams meet in step 3 of MAVEN-12 (adding `TAGS:` lines into each tool's `## Description` block in maven-protocols).

## The 18-tag taxonomy

Replaces 1,293 free-form tags. Each tag answers "what kind of problem is this ticket about?" Granularity moves to summary (free-text) + metadata (structured fields).

`account-closure`, `account`, `investments`, `funds`, `platform`, `margins`, `orders`, `holdings`, `corporate-actions`, `ipo`, `reports`, `general`, `demat`, `settlement`, `compliance`, `nri`, `charges`, `non-individual` — covers 94.3% of tickets. Remaining 5.7% (Tracking/Partner/Business/Orbis/Escalation) are excluded; they go to separate queues or become priority flags.

Source: `Tagging consolidation.md`. Detailed per-tool mapping rationale: `tag_tool_mapping_FINAL.md`.

## Workstreams and status

### Step 1 — Sharpen 11 tag descriptions in beta-supporttools

**Status: DONE by user.** They applied the 11 description edits from `step1_tag_descriptions.md` directly in the beta-supporttools UI. Tag-prediction accuracy should improve over the next 24–48h on the four worst-rated tags (`nri`, `non-individual`, `ipo`, `compliance`).

### Step 2 — `always_include` for utility tools

**Status: SOLVED.** Engineering hard-coded `get_all_client_data` to fire on every ticket — stronger guarantee than `always_include`. The other four utility tools (`get_call_info`, `get_client_contact`, `get_client_interactions`, `st_reports`) are lower-volume; the user is comfortable not specifically auditing those.

User also rewrote `get_all_client_data` protocol to remove the "invoke X for Y" routing prose and keep only field reference data + escalation rules. Architecturally cleaner — routing now lives in each downstream tool's description, which is exactly what step 3's `TAGS:` mapping supports.

### Step 3 — Add `TAGS:` line to each tool's `## Description` block

**Status: PENDING — blocked on git cleanup (see "Current git state" below).**

Engineering is providing an input field in the Maven tool config UI; user will paste from the CSV directly. The CSV is `tool_tags.csv` — 60 rows, `category,tool_name,tag_1,tag_2,tag_3` format, primary tag first, max 3, blanks where intentionally unmapped.

5 utility tools are unmapped on purpose (always-on context). 6 of the 18 tags map to no tool (`account-closure`, `platform`, `general`, `settlement`, `compliance`, `nri` — informational/process; system prompt + handoff handles them).

The same `TAGS:` line should also be added to each tool's `## Description` block in the maven-protocols repo so the live MCP config reads them. Format:

```
TAGS: orders, holdings
```

### Step 4 — Description rewrites for 6 underperforming tools

**Status: PROPOSED, NOT APPLIED.** See `step4_tool_description_fixes.md`. Targets: `get_client_contact` (3.1% upvote), `console_eq_tradebook_prepared` (10.9%), `corporate_action_orders` (11.1%), `swp_report` (15.6%), `console_mf_external_trades` (24.3%), `auto_debit_payins` (33.3%).

Approach is **positive scope only** for 4 tools (sharper WHEN TO USE + cleaned trigger keywords); explicit "use other_tool instead" callouts retained for the 2 cousin-tool cases (`auto_debit_payins` vs `mandate_debit_report`, `swp_report` vs `stp_report`/`sip_report`).

This is design preference: do NOT enumerate DO-NOT bullets. See `~/.claude/projects/-home-tharun-m/memory/feedback_positive_scope_over_donts.md`. Also note: `maven_project_skill.md` had a "counter-examples help the model more than rules" line — that line was removed from the doc per user feedback.

### Step 5 — Open questions

1. **Where does the `TAGS:` line live structurally?** Inside `## Description` is what the proposal assumes. Engineering may have a dedicated tags field in the Frappe schema; if so, `TAGS:` belongs there instead.
2. **Is stage 4's predicted tag plumbed into stage 5's tool selector today?** The mapping only delivers value if the selector either receives the predicted tag OR the descriptions literally contain the tag string so the selector LLM picks up on it. Worth confirming.
3. **`referral_payout`** is the only tool wholly outside the 18-tag taxonomy (partner queue). Does it need a partner-queue tag outside the 18?

### Protocol audit on `Cleaned Protocols (2).md`

**Status: DONE.** Findings in `cleaned_protocols_audit.md`. The file is significantly cleaner than the (1) version that came before — most critical bugs are fixed (CONSOLE EQ TRADEBOOK PREPARED routing tree, CONSOLE FNO TRADEBOOK PREPARED corrupted Futures CA line, CLIENT RETENTION DATES tool-purpose preamble + Rule 6, `Routing Tree` → `Routing` standardised, em-dash section headers mostly canonical).

What remains: the GDocs export noise (escapes, `(Tharun)` editor markers in 53 of 54 H1s, duplicate H1 per protocol) plus ~10 small surgical fixes:
- Unclosed code block in GET ALL CLIENT DATA Section B routing (line 184)
- Em-dash on its own line in CLIENT RETENTION DATES (line 1703 — should be `---`)
- 3 Section header em-dash variants (`Section A —`, `Section C —` at 3896, 4016 in CONSOLE MTF HOLDINGS; `Section B —` at 7611 in CONSOLE EQ P&L)
- 2 "Tool Purpose & Fundamentals" titles (3900, 7479 — rename to "Fundamentals" and trim 1 preamble bullet)
- 1 `Input: Client ID` line at 3907 (delete)
- 2 broken bullets at 138 and 1482 (no space between `\-` and `\*\*`)
- 4 H1 title fixes (Cashier Payins title case, WITHDRAWAL plural, CONSOLE MF PSEUDO HOLDINGS / ACCOUNT MODIFICATION REPORT missing PROTOCOL suffix)

Audit also documents a global cleanup script (Python regex pass) for the escapes, `(Tharun)` markers, and duplicate H1 collapse.

## Current git state in `/home/tharun.m/maven-protocols/`

**This is the blocker for step 3 and the protocol push.**

Branch: `main`. Remote: `github.com/TharunIyer/maven-protocols`.

**30 tool files modified but uncommitted.** The user has been pasting `Cleaned Protocols (2)` content into individual tool files manually (e.g., `crux_reports/client_retention_dates.md`, `mf_reports/sip_report.md`, `crux_reports/withdrawal_request.md`). The pasted content **still has the GDocs escapes** (`\=`, `\---`, `\*\*`, etc.). Without a cleanup pass, a `git commit && git push` would push escape-laden files into the live config.

Also untracked: `proposed_changes/`, `bulk_cleanup_2026-05-07.md`, `format.png`, `maven_project_skill.md`, `Kite menu box.png`, `Support portal redo.png`.

Two recent commits relate to `crux_qs_payouts` (lean rewrite + protocol description updates).

## Open decisions blocking the next push

1. **Disable strategy for `console_eq_tradebook` and `console_fno_tradebook`.** User said Maven now uses the `_prepared` variants for all date ranges, so the non-prepared tools should be disabled. Three options:
   - (a) Delete the .md files outright.
   - (b) Keep with a deprecation note in the description.
   - (c) Remove from `tool_registry.md` only; keep .md files in git history.
   Recommendation: (c) plus a small deprecation note at top of each file.
2. **Description of the `_prepared` tools.** Currently they say "STRICTLY older than 100 days." If they're now used for all date ranges, that line needs to come out of `console_eq_tradebook_prepared.md` and `console_fno_tradebook_prepared.md`.

User has not answered these yet. Until they do, do not proceed with the push.

## Files in this folder

| File | Purpose |
|---|---|
| `HANDOFF.md` | This file. Read first. |
| `Tagging consolidation.md` | Original 18-tag taxonomy design (1,293→18 reasoning). |
| `Maven auto tagging.txt` | Tab-separated dump of the 18 tags as currently loaded in beta-supporttools. |
| `tag_queries_final.csv` | 271k rows of `tag,query` from production tickets — the dataset behind the taxonomy. |
| `tag_tool_mapping_FINAL.md` | Per-tool tag mapping + 5-step rollout plan + data validation. Source of truth for step 3. |
| `tool_tags.csv` | Paste-ready CSV: `category,tool_name,tag_1,tag_2,tag_3`. 60 tools, max 3 tags each. |
| `step1_tag_descriptions.md` | Paste-ready 11 tag description edits for beta-supporttools (DONE — kept as record). |
| `step4_tool_description_fixes.md` | Proposed description rewrites for 6 underperforming tools (PENDING). |
| `cleaned_protocols_audit.md` | Audit of `/home/tharun.m/Downloads/Cleaned Protocols (2).md` — findings + cleanup plan. |
| `tag_tool_mapping_proposal.md` | Earlier draft, **superseded** by FINAL. Kept for history. |
| `tag_tool_mapping_validation.md` | Earlier validation against 5,779-ticket dataset, **superseded** by FINAL. Kept for history. |
| `Ponnurus ask.png` | Original Plane comment from Ponnuru triggering MAVEN-12. |

The 5 Support Assist Feedback CSVs in `/home/tharun.m/Downloads/Support Assist Feedback*.csv` were the source for the data validation in `tag_tool_mapping_validation.md` (and rolled forward into FINAL). 5,779 tickets, 54% upvote / 46% downvote baseline.

## Next session: do this

If the user has answered the two open decisions (disable strategy + >100-day constraint):

1. Confirm `git status` in `/home/tharun.m/maven-protocols/` — note the 30 modified files.
2. Run a Python regex pass to unescape the modified files in place. Patterns: `\#`, `\*`, `\-`, `\_`, `\=`, `\&`, `\(`, `\)`, `\[`, `\]`, `\>`, `\.`, `` \` ``, `\<`, `\\`. Order matters — do `\\` last.
3. Apply the ~10 small surgical fixes from `cleaned_protocols_audit.md` (unclosed code block, em-dash separator, em-dash section headers, "Tool Purpose & Fundamentals" → "Fundamentals", `Input: Client ID` deletion, broken bullets, H1 title fixes).
4. Add `TAGS:` line to each tool's `## Description` block per `tool_tags.csv`. Skip the 5 utility tools and `referral_payout`.
5. Apply the `console_eq_tradebook` / `console_fno_tradebook` disable per the user's chosen option, plus drop the >100-day constraint from `_prepared` if confirmed.
6. Apply the `step4_tool_description_fixes.md` rewrites to the 6 underperforming tools.
7. Copy the rationale docs (`tag_tool_mapping_FINAL.md`, `cleaned_protocols_audit.md`, `step1_tag_descriptions.md`, `step4_tool_description_fixes.md`, `tool_tags.csv`) into a `decisions/` folder in the repo.
8. Commit with a single coherent message covering all the above.
9. Push to `origin/main`.

If the user has NOT answered the two open decisions: ask them, and don't push until both are settled.

## Memory references

The user's persistent memory at `/home/tharun.m/.claude/projects/-home-tharun-m/memory/`:

- `feedback_positive_scope_over_donts.md` — Maven tool descriptions: positive WHEN TO USE only; no enumerated DO-NOT bullets except for cousin-tool disambiguation.
- `feedback_protocol_optimization_rules.md` — What to cut vs keep when making Maven protocols lean.
- `feedback_audit_over_react.md` — Audit the whole surface on bug reports in code I just refactored.
- `feedback_spoken_script_style.md` — Indian English, no em-dashes for SPOKEN scripts only (these protocols are LLM-facing and em-dashes are fine).
