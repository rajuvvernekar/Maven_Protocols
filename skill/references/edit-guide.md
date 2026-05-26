# Edit Guide: Updating an Existing Protocol

Use this when a v2 protocol exists and needs a specific change. The input
will be one of:
- Protocol + feedback triage output (Bucket 1/2 recommendations)
- Protocol + team member's change request (plain language)
- Protocol + feedback triage output + team member's additional context

## Understanding Feedback Triage Output

The feedback triage project classifies agent feedback into buckets:

**Bucket 1 — Protocol Gap:** Rule doesn't exist for this scenario. The
recommendation will specify where to add new content (new rule, new A-block
row, or extension to an existing rule).

**Bucket 2 — Rule Not Followed:** Rule exists but the model didn't follow
it. The recommendation will identify the existing rule and why it failed
(buried, ambiguous, competing with another rule, lacks a specific condition).

**Bucket 3 — Format/Tone:** System prompt issue, not a protocol issue.
Flag this back to the user — no protocol change needed.

**Bucket 4 — Tool/Data Issue:** The tool returned wrong data or the data
source has a problem. Flag this back to the user — no protocol change
needed.

Only Bucket 1 and Bucket 2 require protocol changes.

## Process

### For Bucket 1 (Gap — Adding New Content)

1. Read the recommendation. It specifies what's missing and where.
2. Determine the right location:
   - New data → new A-block row or new A-block
   - New scenario → new rule in Section C + new route in Section B
   - Extension of existing scenario → extend existing rule
3. Write the new content following conventions (positive framing, reference
   A-blocks for data, no trigger lines, no fluff)
4. Update Section B routing if a new rule was added
5. Check that no existing content was duplicated

### For Bucket 2 (Rule Not Followed — Strengthening)

The recommendation identifies why the model ignored the rule. Common causes
and fixes:

**Rule is buried among too many steps.**
→ Move the critical condition earlier in the rule. Reposition, don't add
  emphasis markers.

**Rule is ambiguous.**
→ Add a specific condition or outcome. "Check segment status" becomes
  "If segment field = 'inactive', respond per **A8-R3**."

**Competing rules.**
→ Two rules cover overlapping scenarios. Clarify the boundary in Section B
  routing so the model hits the right rule.

**Negative framing that the model ignores.**
→ Convert to positive framing. "Do not share UTR numbers" becomes "Share
  only the fields listed in **A2**."

In all cases: modify the existing rule text. Do not add a parallel
instruction alongside the existing one.

### For Plain Language Change Requests

The team member describes what needs to change. Apply the same logic:
1. Identify whether it's new content (Bucket 1 pattern) or a
   strengthening (Bucket 2 pattern)
2. Locate the right place in the protocol
3. Make the change following conventions
4. Verify

## Output

1. The complete updated protocol (full document, not a diff)
2. Change summary referencing the feedback S.No or change request
3. Verification statement (three checks)
