# Fix Guide: Diagnosing and Fixing Protocol Issues

Use this when the user says something is wrong with model responses but
doesn't have a specific change request. The input will be:
- Protocol + examples of bad model responses
- Protocol + description of the problem ("Maven keeps showing internal
  fields" or "responses are too long with bullet points")

## Diagnosis Process

### Step 1: Identify the Symptom Category

**Wrong data in response** — Model shares incorrect information or
internal fields.
→ Check: Are A-block field rules (share/hide lists) clear? Is there a
  competing rule that contradicts the field rules? Is the data the model
  used actually in the protocol, or did it hallucinate from training data?

**Wrong tool initiated** — Model used this tool when it should have used
a different one.
→ This is a description/trigger issue, not a protocol issue. Flag to user
  that the tool description and trigger keywords need adjustment. No
  protocol change needed.

**Out of context response** — Model answered something the protocol doesn't
cover.
→ Check: Does Section B scope clearly define what this protocol does NOT
  cover? Is there a fallback instruction? The model may be filling gaps
  with training data because the protocol doesn't explicitly exclude the
  topic.

**Model ignores a rule** — The rule exists but the model doesn't follow it.
→ Check these in order:
  1. Is the rule buried deep in a long sequence of steps? Move it earlier.
  2. Is the rule in negative framing? Convert to positive.
  3. Does another rule contradict it? Clarify the boundary.
  4. Is the rule too vague? Add a specific condition and outcome.
  5. Is the rule's data inline instead of in an A-block? The model may
     miss inline data in long rules.

**Format/style issues** — Bullet points, headers, bold text, structured
lists in client-facing responses.
→ This is usually a system prompt issue (the protocol's internal structure
  is leaking into responses). Check if the protocol has response templates
  — if so, the model should be using them. If not, templates may be
  needed for the most common scenarios.

### Step 2: Locate the Root Cause

For each symptom, trace backward:
1. What did the model output?
2. What should it have output?
3. Which rule should have governed this?
4. Read that rule — does it clearly lead to the correct output?
5. If yes → the rule is fine, the issue is elsewhere (system prompt,
   tool data, model behavior). Flag to user.
6. If no → identify what's unclear, missing, or contradictory.

### Step 3: Apply the Fix

Use the smallest change that fixes the root cause:

- Repositioning a condition within a rule → move, don't duplicate
- Adding a missing condition → extend the existing rule
- Clarifying ambiguity → rewrite the unclear sentence
- Adding a response template → add to the template A-block, reference
  from the rule
- Fixing a contradiction between rules → clarify Section B routing
  boundaries

Do not:
- Add CRITICAL/IMPORTANT markers as a fix. If the model isn't following
  a rule, emphasis markers don't help. Clarity does.
- Add a new rule that restates an existing rule differently. Modify the
  existing rule.
- Add negative guards alongside existing positive framing. If the
  positive framing isn't working, rewrite it to be more specific.

### Step 4: Verify the Fix Addresses the Symptom

Walk through the bad example again with the fixed protocol:
- Would Section B route to the correct rule?
- Does the rule now clearly lead to the correct output?
- Is the response template (if applicable) the right one?

## Output

1. The complete updated protocol
2. Diagnosis summary — symptom, root cause, fix applied
3. Verification statement (three checks)
4. If the issue is not a protocol problem (system prompt, tool data,
   description/trigger) — say so clearly. No protocol change in that case.
