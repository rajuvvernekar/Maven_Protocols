# Protocol Conventions (v2)

These conventions apply to all Maven MCP protocols. Every build, edit, and
fix must conform to them.

## Structure

### Section A: Reference Data
- Each A-block contains one type of reference data (A1 for timelines,
  A2 for field rules, A3 for charges, etc. — numbering is protocol-specific)
- If new data is referenced by multiple rules, it belongs in an A-block
- Rules reference A-blocks by ID (e.g., "per **A4**"), never restate
  A-block content inline
- Header is just: `## Section A: Reference Data` — nothing after it

### Section B: Decision Flow
- Contains preflight checks (conditions checked before any rule fires),
  the routing tree (if X → Rule N), scope, and fallback behavior
- This is the model's entry point into the protocol
- Every rule in Section C must have a route in Section B
- Header is just: `## Section B: Decision Flow` — nothing after it

### Section C: Rules
- Business logic that references A-blocks for data
- Rules start directly with logic — no "Trigger:" preambles
- Steps within rules are for domain-specific logic only (things the model
  cannot derive from training data)
- Header is just: `## Section C: Rules` — nothing after it

### No Section D
- There is no "General Notes" or "Additional Notes" section
- If a fact applies to multiple rules → put it in an A-block
- If a fact applies to one rule → put it in that rule
- If a note is already covered by an A-block or rule → delete it

## Response Templates
- Response templates belong in A-blocks (e.g., A8 — Response Templates)
- Rules reference templates by ID (e.g., "respond per **A10-R1**")
- Each template is a single canonical response for a scenario
- One template per scenario is sufficient
- Do not add "Example response:" blocks that restate or paraphrase an
  existing template. The template is the example.

## Data Scope

Protocols never contain data fetching or data range instructions.
Pre-processing handles tool initiation — it determines which tool to call,
what data range to fetch, and delivers the response into the model's
context before the protocol runs. By the time the protocol is active, all
tool data is already present.

Protocols tell the model how to interpret and reason about data that's
there. They do not tell the model how to get it.

Remove any instructions like:
- "Fetch data for the last 5 days"
- "Pull transactions from T-2 to T+3"
- "Check the last 30 days of orders"
- "Initiate the SIP report tool"
- "Call the fund allocation API"

Instead, write rules that reason about whatever data is present:
- "If the SIP date has no matching order → respond per **A5-R2**"
- "If the order status shows 'rejected' → check rejection reason field"

## Framing

### Positive Framing
- State the correct behavior directly
- "Share only fields per **A2**" — not "Do not share internal fields"
- "Use client-facing terms per **A3**" — not "Never use internal jargon"
- Exception: keep a negative guard only when the incorrect behavior is so
  intuitive the model would default to it even with a clear positive rule
- When both are needed, lead with the positive; add the negative as brief
  reinforcement

### Banned Terminology
- Convert "Do not say X" lists into translation tables:
  `Internal Term → Client-Facing Alternative`
- Place translation tables in an A-block, not inline in rules

### CRITICAL/NEVER/MANDATORY Markers
- Remove markers that restate what the positive rule already says
- Keep only for genuinely counterintuitive behavior
- Test: "Would the model still get this wrong with just the positive rule?"
  If no → remove the marker. If yes → keep it.

## Redundancy Rules

### Single Source of Truth
- Every fact exists in exactly one place
- If the same timeline appears in a rule and an A-block → keep in A-block,
  rule says "per **A[N]**"
- If the same template appears in two rules → move to a template A-block,
  both rules reference it
- If escalation details appear in a rule and an escalation A-block →
  keep in A-block, rule says "escalate per **A[N]**"

### What Counts as Redundancy
- Same data in A-block + rule = redundant (keep in A-block)
- Same data in two A-blocks = redundant (consolidate)
- Same data in A-block + scope = redundant (keep in A-block)
- "Example response:" that paraphrases an R-template = redundant (delete)
- Escalation details in rule + A-block = redundant (keep in A-block)

### What Does NOT Count as Redundancy
- A rule referencing an A-block by ID is not redundancy — it's a pointer
- Two rules handling different scenarios that reference the same A-block
  are not redundant — they're separate logic paths

## Header and Fluff Rules

### Lines to Remove
These are handled by the system prompt and waste tokens in protocols:
- "All rules reference these blocks as single sources of truth."
- "Rules reference Section A blocks. They do not redefine what is already
  defined there."
- "If a definition exists here, rules must not restate it — only cite
  the block ID."
- Any meta-commentary explaining how the protocol structure works

### Lines to Keep
- Protocol-specific scope guidance (e.g., "Address: SWP trigger issues,
  amount discrepancies, T-PIN authorization")
- Protocol-specific routing notes that aren't covered by Section B

## Data Preservation

### Never Modify Without Explicit Request
- Response template wording, punctuation, and placeholders
- URLs and their anchor text
- Charges, fees, and penalty amounts
- Timelines and processing windows
- Field names (internal and client-facing)
- Escalation paths and contact details
- A-block numbering (renumber only if restructuring the entire protocol)

### When Data Looks Outdated
- Flag it to the user: "A3 shows processing time as T+2, but current
  SEBI guidelines may require T+1. Please confirm before I change this."
- Never silently update data you suspect is wrong
