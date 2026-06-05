# Protocol Skills — Feedback Fixing & Regression Workflow

This file documents the end-to-end pattern for fixing Maven v2 protocols based on feedback, and the regression checks that must accompany every edit.

---

## Governing Files

| File | Role |
|------|------|
| `/home/raju.v/Downloads/skills_file_final.md` | Canonical rules for authoring and editing all v2 protocols. Every edit must comply with this file. |
| `REGRESSION_LOG.md` | Tracks which rules and sections have been modified before. Check before every edit. |
| `CHANGELOG.md` | Records every change applied to every tool. Updated after every session. |
| `skill/SKILL.md` | The Claude skill definition — detects Build / Edit / Fix mode and loads the right guide. |

---

## Feedback → Fix Pattern

### Step 1 — Read the feedback

Feedback arrives as triage output (Bucket 1 / Bucket 2), a support QA note, or a direct instruction. Identify:

- **Which tool** the feedback targets.
- **Which rule or section** is implicated (Rule N, Section B routing, an A-block).
- **What went wrong** — wrong response, missing logic, slop, bad field handling.

### Step 2 — Check REGRESSION_LOG before touching anything

Open `REGRESSION_LOG.md`. Find the tool + section in the table.

- **Row exists** → a prior fix was applied. Read what it was. Check `Regression?` column.
  - If `Yes` → the same fix was needed twice. Understand root cause before re-applying.
  - If `No` → a different area was fixed before. Proceed, but note this new change.
- **No row** → first time this section is being edited. Add a row after the fix.

Tools on the **Watch List** (3+ prior modifications) need extra care — read the surrounding rules before changing anything.

### Step 3 — Apply the fix per skills_file_final.md

Every edit must follow the rules in `skills_file_final.md`. Before writing:

1. Identify which section of the protocol needs the change (Section A, B, or C).
2. Check whether any of the 22 slop patterns apply to the area being changed — fix any found, don't leave them for the reviewer.
3. Apply only what the feedback specifies. Do not refactor adjacent content unless it's a direct slop pattern triggered by the edit.

Key rules most often relevant to feedback fixes:

- **Pattern #4** — Domain facts belong in A-blocks, not rules.
- **Pattern #5** — Do not restate A-block content inline after referencing it.
- **Pattern #10** — Remove data-fetching language for preprocessing-loaded data. Use `invoke` for model-invoked tools.
- **Pattern #20** — Every escalation path must name the recipient. Generic fallback uses `escalate`; team-specific uses `escalate to the [team] team`.

### Step 4 — Run the three verification checks

Every edit runs all three before being presented:

#### Regression Check
- Every existing rule still exists with the same logic unless explicitly modified.
- Every A-block still has the same data unless explicitly modified.
- Every routing entry points to a rule that exists AND handles the stated scenario.
- All A-block references in rules still point to correct data after any renumbering.
- Response templates altered only when explicitly requested; domain facts relocated before any template is deleted.

#### Redundancy Check
- No fact, timeline, charge, or instruction appears in two places.
- No URL appears in more than one A-block.
- Escalation details stated in one location only.
- No routing entry is a 1:1 restatement of the target rule's name.

#### Convention Check
- Positive framing. Negative guards only for counterintuitive defaults.
- New rules start with logic — no "Trigger:" lines.
- New reference data in an A-block, not inline.
- No header fluff or justification sentences.
- Section A, B, and C headers present.
- Plain language throughout — no "verbatim," "aforementioned," math/set notation.

### Step 5 — Diff and CHANGELOG

Present the edit as a before/after diff for every modified line (per Diff Requirement in skills_file_final.md). Then update `CHANGELOG.md` and `REGRESSION_LOG.md`.

---

## Escalation Convention

The current convention (effective 2026-06-01):

- Generic fallback: `escalate` — no "to human agent" suffix.
- Team-specific: `escalate to the settlements team`, `escalate to the [team] team`.
- Escalation data A-block canonical phrase: `Include when escalating:` (not "Include when escalating to human agent:").
- All-caps forms normalize to sentence-case: `ESCALATE` → `escalate`.

---

## Common Feedback Fix Recipes

| Feedback type | Where to look | Likely fix |
|---------------|---------------|------------|
| Model ignores a rule condition | Section C rule structure | Check if the condition is buried after a response block; move it before. |
| Model shares internal fields | Section A field reference | Confirm field is in Non-shareable table; add if missing. |
| Wrong escalation wording | Every rule's fallback step | Update to `escalate` or `escalate to the [team] team` per A-block. |
| Model fetches stale or wrong data | Section B preflight or rule | Remove data-fetching slop (pattern #10); confirm preprocessing loads it. |
| Duplicate response across two rules | Section C | One rule owns the response; the other cross-references it. |
| Routing sends wrong rule | Section B routing | Fix the routing entry — verify target rule name matches scenario. |
| Model gives a drafted sentence that wasn't requested | Section C inline template | Remove; convert to domain-fact instruction per pattern #3 / #5. |
