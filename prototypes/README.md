# Protocol Viewer (prototype)

A self-contained HTML viewer for the Maven tool protocols — for **human review/QA**, not for Maven.
Markdown in the repo stays the **source of truth**; this is a read + light-edit layer over it.

## Use it
Just open **`protocol_viewer.html`** in any browser (no server needed — all protocols are embedded).
Clone the repo and double-click the file.

- **Dropdown** (top-left): pick any of the 54 active tools, grouped by category.
- **Dependency chips:** every tool the selected protocol `invoke`s (matches the SOT dependency list).
- **Section B** renders as a routing flow — `→ Rule N` links jump to the rule; `escalate` routes are red.
- **Rules** are cards with `invoke` (green) / `escalate` (red) highlighted, so gaps stand out.
- **Edit rules** → inline textareas (raw markdown). **Export → Markdown** regenerates the file with
  only your edits changed (untouched text stays byte-identical) — copy it back into the `.md`.

## Regenerate after protocol changes
The viewer embeds a snapshot of the protocols, so re-run the build after editing any `.md`:

```
python3 prototypes/build_viewer.py
```

This reads all active protocols (excludes the 8 disabled tools) and rewrites `protocol_viewer.html`.

## Files
- `protocol_viewer.html` — the generated, self-contained viewer (commit + share).
- `protocol_viewer_template.html` — the template (HTML/CSS/JS); `__DATA__` is replaced at build.
- `build_viewer.py` — build script.
- `cashier_payins.html` — the original single-tool prototype (superseded by the viewer).

## Scope note
This is for authoring/review only. Do **not** feed HTML to Maven — protocols must stay lean markdown
(the LLM consumes them as tool config; HTML there is pure token cost).
