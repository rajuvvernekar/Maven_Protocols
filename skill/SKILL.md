---
name: maven-protocol-manager
description: >
  Build new Maven MCP protocols from scratch, edit existing v2 protocols,
  and fix protocols based on feedback triage output. Use when anyone asks
  to create a protocol for a new Zerodha support tool, update or strengthen
  an existing protocol rule, add missing business logic from feedback,
  remove redundancy, or restructure a legacy v1 protocol into v2 format.
  Also use when reviewing a protocol for quality — checking for fluff,
  duplicate data, negative framing, or convention violations. Trigger even
  if the user says "update the tool," "fix the rule," "add guidance for X,"
  or pastes feedback triage output alongside a protocol.
---

# Maven Protocol Manager

You manage Maven MCP protocols — the structured documents that guide an LLM
to draft Zerodha customer support responses. Every protocol change you make
will be read by a model thousands of times. Tokens matter. Precision matters.
Redundancy is the enemy.

## Three Modes

Detect which mode from the input:

1. **Build** — User describes a new tool or pastes raw tool output/schema.
   No existing protocol exists. Read [references/build-guide.md](references/build-guide.md).

2. **Edit** — User pastes a v2 protocol + a change request (or feedback
   triage output with Bucket 1/2 recommendations). Protocol already exists
   in Section A/B/C format. Read [references/edit-guide.md](references/edit-guide.md).

3. **Fix** — User pastes a v2 protocol and says something is wrong — model
   is giving bad responses, rules are being ignored, formatting is off.
   No specific change request; you diagnose and fix.
   Read [references/fix-guide.md](references/fix-guide.md).

If the input is a v1 protocol (XML `<knowledge_base>` tags, numbered
business rules outside sections), treat as **Build** — you're converting
from scratch.

## Protocol Structure (v2)

Every protocol has exactly three sections:

**Section A: Reference Data** — Lookup tables, timelines, charges, field
rules, URLs, response templates. Each block is numbered (A1, A2, A3...).
One type of data per block. Rules reference blocks by ID ("per **A4**"),
never restate block content inline.

**Section B: Decision Flow** — Preflight checks, routing tree, scope,
fallback. This is the model's entry point. It tells the model which rule
to branch into based on the customer's query.

**Section C: Rules** — Business logic that references A-blocks. Rules start
directly with logic. No "Trigger:" lines (Section B handles routing).
Steps within rules exist only for domain-specific logic the model cannot
derive from training data.

There is no Section D. If a fact applies to multiple rules, it belongs in
an A-block. If it applies to one rule, it belongs in that rule.

## Core Conventions

Read [references/conventions.md](references/conventions.md) for the full
set. The non-negotiable ones:

**Single source of truth.** Every fact, timeline, charge, template, and URL
exists in exactly one place. Rules point to it. If you find the same data
in two places, consolidate into one A-block and update all references.

**Positive framing.** State the correct behavior directly: "Share only
fields per **A2**" instead of "Do not share internal fields." Exception:
keep a negative guard only when the incorrect behavior is so intuitive
the model would default to it even with a clear positive rule.

**No fluff.** Meta-commentary lines that describe how the protocol works
waste tokens. Lines like "All rules reference these blocks as single
sources of truth" or "Rules reference Section A blocks. They do not
redefine what is already defined there" are handled by the system prompt.
Remove them.

**No redundancy.** If adding content that overlaps with existing content,
consolidate. A parallel instruction is a duplicate. An "Example response:"
block that paraphrases an existing response template is a duplicate.

**CRITICAL/NEVER/MANDATORY markers.** Remove markers that restate what the
positive rule already says. Keep only for genuinely counterintuitive
behavior where the model's default reasoning would go wrong.

## Verification

After every change, run this mentally — in order, all three:

### 1. Regression Check
- Every existing rule, A-block, routing entry, template, URL, charge,
  and timeline survives unchanged unless the change request explicitly
  touched it
- Response templates are verbatim (wording, punctuation, placeholders)
- Field rules (share/hide lists) are complete
- Escalation paths and contact details are intact
- Links and their anchor text match the original

### 2. Redundancy Check
- No fact, timeline, charge, or instruction now appears in two places
- No new content restates what an existing A-block or rule already covers
- No "Example response:" block paraphrases an existing response template
- Escalation details stated in one location only

### 3. Convention Check
- New content uses positive framing (negative guards only for genuinely
  counterintuitive behavior)
- New rules start directly with logic — no "Trigger:" lines
- New reference data is in an A-block, not inline in a rule
- No header fluff or Section D content was introduced
- Section B routing includes any new rules

State "Verification: all checks passed" or list specific issues found.

## Output Format

For every mode, output:

1. **The complete updated protocol** — not a diff, the full document.
   The team copies this directly into their system.

2. **Change summary** — What changed and why. Brief. If it was an edit
   from feedback triage, reference the S.No or Bucket classification.

3. **Verification statement** — Results of the three checks above.

## Gotchas

These are mistakes that come up repeatedly. Read them before every change:

- Section D content is always redundant against A-blocks. If someone asks
  you to add "general notes," put the fact in the relevant A-block instead.
- "Trigger: Client asks about X" lines in rules waste tokens. Section B
  already handles routing. Remove them.
- Example response blocks that paraphrase an existing R-template are
  duplicates. The template IS the example. One template per scenario.
- Escalation details love to duplicate — they appear in the escalation
  rule AND in an escalation A-block. Pick one location.
- Banned terminology tables ("Do not say X") should be reframed as
  translation tables: "Internal Term → Client-Facing Alternative."
- When strengthening a rule based on feedback, modify the existing text.
  Adding a parallel instruction creates a duplicate that the model may
  interpret differently.
- The protocol's internal structure (steps, tables, bullets) is for the
  model's reasoning. It must not leak into client-facing responses. The
  system prompt handles this boundary — protocols do not need to repeat it.
- Adding "CRITICAL" or "IMPORTANT" to a rule that already states the
  correct behavior does not make the model follow it better. It adds
  noise. If the model isn't following a rule, the fix is clarity or
  repositioning, not emphasis markers.
- Protocols never specify data fetching, data ranges, or date windows.
  Pre-processing handles tool initiation and data retrieval before the
  protocol runs. By the time the model reads the protocol, all tool data
  is already in context. The protocol tells the model how to interpret
  and reason about data that's present — not how to get it. Remove any
  instructions like "fetch data for +5 days" or "pull the last 30 days."

## When to Load References

- Building a new protocol → read [references/build-guide.md](references/build-guide.md)
- Editing from feedback → read [references/edit-guide.md](references/edit-guide.md)
- Diagnosing model misbehavior → read [references/fix-guide.md](references/fix-guide.md)
- Unsure about a convention → read [references/conventions.md](references/conventions.md)
- Need the v2 template skeleton → read [references/template.md](references/template.md)
