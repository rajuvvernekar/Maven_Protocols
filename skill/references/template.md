# [Tool Name] Protocol

## Section A: Reference Data

### A1 — [Data Type, e.g., Timelines]

| Scenario | Timeline |
|----------|----------|
| ... | ... |

### A2 — [Data Type, e.g., Field Display Rules]

**Share with client:** field_1, field_2, field_3
**Do not surface:** internal_field_1, internal_field_2

### A3 — [Data Type, e.g., Charges]

| Action | Charge | Note |
|--------|--------|------|
| ... | ... | ... |

### A4 — [Data Type, e.g., URLs and Links]

| Purpose | URL | Anchor Text |
|---------|-----|-------------|
| ... | ... | ... |

### A5 — Response Templates

**R1 — [Scenario Name]**
[Exact response text with {placeholders} for dynamic data]

**R2 — [Scenario Name]**
[Exact response text]

### A6 — Escalation Details

**When to escalate:** [conditions]
**Include:** [required information]
**Channel:** [email/ticket/etc.]

---

## Section B: Decision Flow

### Preflight
1. [Check condition] → if true, [action]
2. [Check condition] → if true, [action]

### Routing
- [Scenario description] → **Rule 1**
- [Scenario description] → **Rule 2**
- [Scenario description] → **Rule 3**

### Scope
- Address: [what this protocol covers]
- Out of scope: [what belongs to other tools]

### Fallback
If no rule matches: [fallback behavior]

---

## Section C: Rules

### Rule 1 — [Scenario Name]

[Logic starts here. No trigger line.]

If [condition]:
  → Respond per **A5-R1**

If [other condition]:
  → Check **A1** for timeline, include in response per **A5-R2**

### Rule 2 — [Scenario Name]

[Logic starts here.]

### Rule 3 — [Scenario Name]

[Logic starts here.]
