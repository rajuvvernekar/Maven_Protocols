# Build Guide: Creating a New Protocol

Use this when no v2 protocol exists for the tool. The input will be one of:
- A description of what the tool does + sample tool output/schema
- A v1 protocol (XML `<knowledge_base>` tags) that needs full conversion
- Raw feedback/documentation about a new tool being added

## Process

### Step 1: Identify Reference Data

Read the input and extract every piece of data that rules will need to
look up: timelines, charges, field rules (which fields to share/hide),
URLs, response templates, escalation paths, terminology translations.

Each distinct data type becomes an A-block. Number them sequentially.

Common A-block types (not every protocol needs all of these):
- Timelines and processing windows
- Charges, fees, penalties
- Field display rules (share list / hide list)
- URLs and support links
- Response templates
- Escalation details
- Status codes and their meanings
- Terminology translation table (internal → client-facing)

### Step 2: Build the Routing Tree

Identify the distinct scenarios the tool handles. Each scenario maps to
a rule. The routing tree in Section B tells the model: "If the customer
asks about X → go to Rule N."

Start with preflight checks — conditions that must be true before any
rule fires (e.g., "If account is in a specific state, handle that first
before checking order status").

Then map each scenario to a rule number.

Add scope: what this protocol covers and what it explicitly does not
(to prevent the model from overreaching).

Add fallback: what to do if no rule matches.

### Step 3: Write the Rules

For each scenario in the routing tree, write a rule. Each rule:
- Starts directly with logic (no "Trigger:" preamble)
- References A-blocks for data instead of restating it
- Contains only domain-specific logic the model cannot derive from
  training data
- Uses positive framing by default

### Step 4: Verify Completeness

Walk through every data point in the original input:
- Is it in an A-block? Which one?
- Is it referenced by at least one rule?
- Is it in exactly one place (no duplicates)?

If converting from v1, produce a comparison checklist:

| # | Data Point | Original Location | v2 Location | Status |
|---|-----------|-------------------|-------------|--------|
| 1 | Processing time: T+2 | Business Rule 3 | A1 row 2 | ✅ |
| 2 | Escalation email | Knowledge Base > Escalation | A6 | ✅ |

Every row must show ✅. Flag any ⚠️ items and resolve them before
delivering.

### Step 5: Output

Deliver:
1. The complete v2 protocol
2. If converting from v1: the comparison checklist
3. Verification statement (three checks from SKILL.md)

## Converting v1 to v2

v1 protocols use XML `<knowledge_base>` blocks and numbered business rules
outside any section structure. The conversion process:

1. Extract all data from `<knowledge_base>` → becomes Section A blocks
2. Identify the routing logic scattered across business rules → becomes
   Section B decision flow
3. Extract business logic from numbered rules → becomes Section C rules
   that reference A-blocks
4. Identify and remove: duplicate data across knowledge base and rules,
   header fluff, trigger lines, negative framing, excessive CRITICAL
   markers, Section D equivalent content
5. Run the comparison checklist to verify zero data loss

## Template

See [template.md](template.md) for the skeleton structure to start from.
