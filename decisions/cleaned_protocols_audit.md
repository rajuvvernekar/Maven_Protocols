# Audit: `Cleaned Protocols.md` (current draft, 11,778 lines, 54 protocols)

This audit replaces the earlier one. The file has improved markedly since the (1) version — most critical bugs are fixed. What's left below is small and surgical.

Since you'll push to git and copy from there into Frappe, I've split findings into:
- **Strip-before-git** — GDocs export artifacts (escapes, `(Tharun)` markers, duplicate H1) that must not enter the repo.
- **Real content/structure issues** — should be fixed in the markdown source whether you go via GDocs or directly to git.

---

## What's already fixed (vs the earlier audit)

| Item | Status |
|---|---|
| CONSOLE EQ TRADEBOOK PREPARED routing tree (was copy-pasted from PLEDGE REQUEST REPORT) | ✓ Fixed — now correctly routes to tradebook rules |
| CONSOLE FNO TRADEBOOK PREPARED A5 corrupted Futures CA line | ✓ Fixed — line 75 reads cleanly |
| CLIENT RETENTION DATES tool-purpose preamble in A1 | ✓ Removed |
| CLIENT RETENTION DATES Rule 6 verbose body | ✓ Trimmed to `Apply A2.` |
| `### Routing Tree` → `### Routing` everywhere | ✓ Standardised |
| Most `## Section B — Routing` / `## Section C — Rules` em-dash variants | ✓ Mostly canonical (3 stragglers below) |
| Hyphen-attached bold lines | ✓ Down to 2 instances |
| Section A → A1 stray `---` separators | ✓ Mostly removed |

---

## STRIP-BEFORE-GIT (cleanup pass)

These are GDocs export artifacts and editor metadata. None of them belong in the maven-protocols repo.

### 1. Escaped markdown — global pass
Every `#`, `*`, `-`, `_`, `=`, `&`, `(`, `)`, `[`, `]`, `>`, `.`, `` ` ``, etc. is backslash-escaped. Frappe stores raw text and shows monospace, so escapes appear literally and waste tokens. Run before pushing to git:

```python
import re
text = open("Cleaned Protocols.md").read()
for pat, repl in [
    (r'\\#', '#'), (r'\\\*', '*'), (r'\\-', '-'), (r'\\_', '_'),
    (r'\\=', '='), (r'\\&', '&'), (r'\\\(', '('), (r'\\\)', ')'),
    (r'\\\[', '['), (r'\\\]', ']'), (r'\\>', '>'), (r'\\\.', '.'),
    (r'\\`', '`'), (r'\\<', '<'), (r'\\\\', '\\'),
]:
    text = re.sub(pat, repl, text)
open("Cleaned Protocols cleaned.md", "w").write(text)
```

Verify: `grep '\\\\' "Cleaned Protocols cleaned.md"` returns nothing.

### 2. `(Tharun)` markers — strip
53 of 54 protocol H1s start with `# (Tharun)\# X PROTOCOL`. After unescape this becomes `# (Tharun)# X PROTOCOL` — the `(Tharun)` is sneaked into the H1 text, presumably as your "I have reviewed this" marker. ACCOUNT MODIFICATION REPORT (line 11140) doesn't have it.

Strip it. Regex (run after the unescape pass):

```python
text = re.sub(r'^# \(Tharun\)\s*# ', '# ', text, flags=re.MULTILINE)
```

### 3. Duplicate H1 per protocol
Every protocol has the title twice — line N: `# (Tharun)\# X PROTOCOL`, line N+2: `\# X PROTOCOL`. After the (Tharun) strip, both lines become `# X PROTOCOL`. Keep one, delete the other. Regex (after the two passes above):

```python
text = re.sub(r'^# ([A-Z][A-Z0-9 &\\-/]+(?:PROTOCOL|REPORT|PROTOCOLS))\s*\n\s*\n# \1\s*\n', r'# \1\n\n', text, flags=re.MULTILINE)
```

Spot-check after the pass — should leave exactly one H1 per protocol.

---

## REAL CONTENT/STRUCTURE ISSUES

### A. Critical syntax bug — unclosed code block in `GET ALL CLIENT DATA PROTOCOL`

Line 179 opens a ` ``` ` for the Section B routing tree. Lines 180–184 contain the routing content. **Line 185 should close the code block with ` ``` ` but doesn't** — the file jumps straight to `\---` at line 186.

```
\`\`\`
Route by scenario
   ├─ account_blocks non-empty → Rule 1
   ...
   └─ Orbis account ... → Rule 4

\---                          <- code block never closed before this
```

Add the closing ` ``` ` between the last route bullet and the `---` separator. Without it, every line until the next code block reads as code-block content, breaking section parsing.

### B. CLIENT RETENTION DATES — em-dash on its own line (line 1703)

```
Include in escalation: client ID, ...

—                              <- this should be `\---` (HR), not `—` (em-dash)

\#\# Section B: Decision Flow
```

Replace `—` with `\---` (or just `---` after the unescape pass). Editing artifact from the GDocs round-trip.

### C. CONSOLE MTF HOLDINGS — three header/format issues

| Line | Current | Fix |
|---|---|---|
| 3896 | `## Section A — Reference Data` | `## Section A: Reference Data` |
| 3900 | `### A1 — Tool Purpose & Fundamentals` | `### A1 — Fundamentals` |
| 3907 | `- Input: Client ID.` | Delete (pre-injected by every tool) |
| 3902 (first bullet of A1) | "MTF allows clients to buy shares by paying only initial margin (~20–50% depending on stock); Zerodha funds the rest." | Either drop entirely (pure preamble) or trim to "MTF position = initial margin paid by client + funded amount from Zerodha." |
| 4016 | `## Section C — Rules` | `## Section C: Rules` |

### D. CONSOLE EQ P&L — two header issues

| Line | Current | Fix |
|---|---|---|
| 7479 | `### A1 — Tool Purpose & Fundamentals` | `### A1 — Fundamentals` |
| 7611 | `## Section B — Decision Flow` | `## Section B: Decision Flow` |

### E. Two hyphen-attached bold lines (broken bullets)

| Line | File context | Current | Fix |
|---|---|---|---|
| 138 | GET ALL CLIENT DATA, A4 Segment Statuses, after the kill-switch table | `\-\*\*Kill switch:\*\*` | Add space: `\- \*\*Kill switch:\*\*` (or just `**Kill switch:**` as a paragraph) |
| 1482 | PAN STATUS, A1 Fundamentals, second item | `\-\*\*pan_status inputs:\*\*` | Same — add space |

### F. H1 title inconsistencies (after the strip-before-git pass these affect the canonical title)

| Line | Current | Should be |
|---|---|---|
| 4753 | `# Cashier Payins Protocol` (Title Case) | `# CASHIER PAYINS PROTOCOL` (uppercase, per CLAUDE.md canonical) |
| 5399 | `# WITHDRAWAL PROTOCOLS` (plural) | `# WITHDRAWAL PROTOCOL` (singular) |
| 10263 | `# CONSOLE MF PSEUDO HOLDINGS` (no "PROTOCOL") | `# CONSOLE MF PSEUDO HOLDINGS PROTOCOL` |
| 11140 | `# ACCOUNT MODIFICATION REPORT` (no "PROTOCOL") | `# ACCOUNT MODIFICATION REPORT PROTOCOL` |

### G. In-content tool-purpose phrases — judgement calls (3 instances)

These aren't pure preambles; they're scope clarifiers embedded in actual rule/scenario content. Each is borderline. My recommendation noted next to each — but you can call.

| Line | Protocol / Section | Current | Recommendation |
|---|---|---|---|
| 8544 | CONSOLE FNO POSITIONS A5 (MTM bullet) | "This tool shows position snapshots only — day-by-day MTM breakdown is not available here." | **Keep** — useful constraint that explains why a follow-up rule escalates day-by-day MTM queries. |
| 8811 | CONSOLE FNO TRADEBOOK PREPARED Rule 8 | "This tool provides trade-level execution data only — no charge, MTM, or obligation data." | **Keep** — answers a real client query category and gates the rule. |
| 8897 | CONSOLE FNO PNL A5 (Charges/MTM scenario) | "This report shows realized P&L only — brokerage, STT, and other charges are not included…" | **Keep** — it's the scenario's actual answer, not a preamble. |

All three are doing scope-clarification work tied to specific rules. Leave them.

---

## RECOMMENDED FIX ORDER

1. **Backup the current file.**
2. **Strip-before-git pass** (§1, §2, §3). One Python script does all three. After this the file is in canonical maven-protocols format minus the small content fixes below.
3. **Fix the unclosed code block** in GET ALL CLIENT DATA (§A). One-line edit.
4. **Fix the em-dash separator** in CLIENT RETENTION DATES (§B). One-line edit.
5. **Fix the 5 CONSOLE MTF HOLDINGS edits** (§C). Five surgical edits.
6. **Fix the 2 CONSOLE EQ P&L edits** (§D). Two surgical edits.
7. **Fix the 2 broken bullets** (§E).
8. **Fix the 4 H1 titles** (§F).
9. **Push to maven-protocols git.** Each protocol body replaces the body inside `## Protocol` of its corresponding tool file (e.g., the CLIENT RETENTION DATES body goes into `crux_reports/client_retention_dates.md` between the existing `## Protocol` line and EOF).

After this the file is ready for git. From git, you copy into Frappe; Frappe stores clean text; LLM reads clean tokens.

---

## Want me to do the cleanup pass?

If you want, I can:
- Run the strip-before-git pass programmatically and produce `Cleaned Protocols cleaned.md` next to the original.
- Apply the 14 surgical edits (§A through §F) to the cleaned file.
- Diff each protocol body against the corresponding maven-protocols tool file so you can see exactly what changes per file before pushing.

Or just hand the cleaned file to you and you take it from there. Tell me which.
