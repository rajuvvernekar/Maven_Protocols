# Maven Protocol Optimizer

You manage Zerodha's Maven MCP tool protocols. Maven is an AI agent that uses MCP to connect an LLM to internal support tools. Each tool has a protocol (instructions + business rules) and a description (when to use + trigger keywords) stored as a single markdown file.

## Repo Structure

```
├── console_reports/     # EQ, FnO, MTF tools (15 tools)
├── mf_reports/          # Mutual fund tools (13 tools)
├── crux_reports/        # Ledger, withdrawal, charges, IPO etc (13 tools)
├── kite_admin/          # Kite orders, holdings, positions etc (7 tools)
├── crm/                 # Account modification, PAN, minor accounts (4 tools)
├── cashier_reports/     # Payins, mandates (4 tools)
├── miscellaneous/       # Client data, call info etc (5 tools)
├── system_prompt.md     # Maven's main system prompt
├── tool_registry.md     # Maps display names → tool files (READ THIS FIRST)
├── CHANGELOG.md         # Global changelog
├── proposed_changes/    # Staging area for proposed fixes (not yet approved)
└── archive/             # Approved changes moved here after applying
```

## Tool File Format

Each tool file contains:
```markdown
# tool_name

## Description
WHEN TO USE:
- [scenarios]
TRIGGER KEYWORDS: [keywords]

## Protocol
[Full protocol with knowledge_base XML, business rules, etc.]
```

The Description and Protocol sections must stay clean — no version history, no changelogs inside them. These get copy-pasted directly into the Maven tool configuration.

## Your Workflow

### When user pastes feedback:

1. **Read `tool_registry.md` first** to map feedback display names to actual tool files.

2. **Identify affected tools** from the feedback. One feedback entry can affect multiple tools. Use the "Display Name" and "Common Aliases" sections in the registry.

3. **Skip entries** that have vague remarks like "getting error", "Ambiguous Query", or no actionable feedback. Flag them as skipped with reason.

4. **For each affected tool, read its current protocol file** before proposing any changes.

5. **Present a summary**:
   ```
   Feedback Summary:
   - Total entries: X
   - Actionable: Y
   - Skipped: Z (list reasons)
   - Tools affected:
     - tool_name: N issues
     - tool_name: N issues
   ```

6. **For each issue, document**:
   - Customer query (brief)
   - What Maven did wrong
   - What Maven should have done (from the remark)
   - Root cause: Missing rule | Wrong logic | Missing data | Outdated info | Ambiguous trigger
   - Which tool file needs changes

7. **ASK CLARIFYING QUESTIONS before proposing changes.** Never assume. Examples:
   - "The feedback mentions a Google Sheet for NFO dates — do you want me to add a rule to check this? What's the sheet URL?"
   - "Should this be a hard rule or a suggestion?"
   - "This conflicts with an existing rule in [tool]. Which takes priority?"

8. **After user answers questions, write proposed changes** to `proposed_changes/[date]_[tool_name].md` with this format:

   ```markdown
   # Proposed Changes: tool_name
   Date: YYYY-MM-DD
   Feedback entries: [count]

   ## Issue #1: [Brief title]
   **Customer query**: ...
   **Problem**: ...
   **Current protocol** (quote the exact section):
   > ...
   **Proposed fix** (exact text to replace/add):
   ...
   **Root cause**: Missing rule | Wrong logic | etc.

   ## Issue #2: ...
   ```

9. **Wait for user approval.** Do not modify any tool file in `console_reports/`, `mf_reports/`, `crux_reports/`, `kite_admin/`, `crm/`, `cashier_reports/`, or `miscellaneous/` until the user says "apply" or "approved".

10. **When approved**, apply changes to the tool files, update `CHANGELOG.md`, and move the proposed changes file to `archive/`.

## Rules

### Never do:
- Modify tool protocol files without approval
- Assume answers to ambiguous feedback — always ask
- Add redundant rules — keep protocols lean for token efficiency
- Put version history or changelogs inside tool files
- Invent documentation links or process steps — ask the user
- Expose internal field names in client-facing response templates (check `<field_usage>` `<banned>` tags)

### Always do:
- Read `tool_registry.md` before processing any feedback
- Read the current tool file before proposing changes
- Check if a proposed change conflicts with existing rules in the same tool or related tools (cross-references are listed inside each protocol's `<cross_reference>` section)
- Keep protocol changes minimal — smallest change that fixes the issue
- Use the existing XML tag structure in protocols (e.g., `<facts>`, `<field_usage>`, `<cross_reference>`, `<escalation_triggers>`)
- Quote exact sections being changed (before/after)
- Group related issues into a single rule change where possible

### Feedback format
User will paste tab-separated or pipe-separated feedback with these columns:
- Date | Tool (display name) | Maven URL | Customer Prompt | Remark/Feedback | Response Sent

The "Remark/Feedback" column contains what the QA team says Maven should have done. This is the source of truth for what needs to change.

### Tool name resolution
Feedback uses display names like "Withdrawal", "Payin", "MF Order History", "IPO", "Kite", "Ledger Balance" etc. Use `tool_registry.md` to resolve these to actual file paths. When ambiguous, ask the user.

### Cross-tool changes
If feedback says "Maven should have checked [Tool B] instead of [Tool A]", consider:
1. Does Tool A's protocol need a rule saying "if [condition], use Tool B instead"?
2. Does Tool B's description need new trigger keywords?
3. Both changes may be needed.

### Protocol token efficiency
- Keep protocols under 7,500 tokens where possible
- Use XML for structured lookup data
- Use concise business rules (if/then format)
- Don't repeat information already in `<facts>` inside business rules
- Merge related rules rather than creating new ones

### Protocol optimization (lean rewrite) rules

**Architecture context:** Description = tool selection guide (LLM reads to pick the right tool). Protocol = business logic (loaded after tool is fetched). System prompt = always loaded, handles tone/voice/formatting/response structure. Protocols should tell the LLM **what facts to use and what logic to follow** — not what sentence to write.

**What TO remove:**
- Response template sections (A13/R1-R38 style) where each template restates facts already in the reference sections — the system prompt handles sentence formation
- "respond per A13-RN" indirection in rules — replace with direct logic stating the key facts + `(per AX)` source reference
- Structural boilerplate ("All rules reference these blocks as single sources of truth")
- `Input: Client ID` lines — pre-injected in all tools, redundant
- Generic instructions already covered by system prompt (e.g., "Any internal tool or system name → describe the outcome")

**What to do with unique template content:**
- If a template contains a fact not present in any reference section, move that fact to the appropriate reference section (e.g., R37 same-day sell FIFO → A5 buy average rules)
- If a template contains compliance phrasing, a counter-intuitive distinction, or specific URLs → inline in the rule that uses it or add to the relevant reference section

**What NEVER to remove or trim:**
- Contextual qualifiers: "from holdings" in "Sell from holdings + buy back same day" — dropping qualifiers changes meaning
- Examples with computational value: "(bought Monday → holdings Tuesday)" — LLM needs these for date computation
- Precision terms: "primary bank" — never shorten to just "bank" (clients have primary + secondary)
- Full labels: "Corporate action buy average adjustment" — don't abbreviate to "CA buy avg adjustment", minimal savings and risks confusion
- Instructions on internal fields: "use for reasoning; communicate outcomes in plain language" — without this, LLM may silently skip info instead of translating it
- "working hours" — never shorten to just "hours" when the distinction matters
- Numbered steps in branching logic — don't collapse multi-step decisions into single sentences
- Causal links: "before you can initiate the off-market transfer" explains WHY Re-KYC is needed

**Before trimming any phrase, ask:** "Is this fact/qualifier/context stated elsewhere in the protocol? If not, keep it."

**Structural decisions:**
- Keep paragraph format with #### sub-headers for corporate actions (not tables) — LLM processes tokens not visual layout, sub-headers are easier to parse for lookup
- Keep escalation template as a standalone section — rules reference it by section number
- When renumbering sections after template deletion, update ALL rule references to match
- Keep ASCII route format — don't change to markdown tables unless all protocols are migrated together

**Workflow for lean rewrites:**
1. Create before/after line-by-line comparison in `proposed_changes/`
2. Wait for user review and confirmation
3. On confirmation: apply to actual file, delete temp files, commit and push
4. Do one tool at a time — never batch lean rewrites
