# Maven Tool Protocols

Zerodha Maven MCP tool protocols and descriptions. Used with Claude Code for iterative protocol optimization based on QA feedback.

## Structure

| Folder | Contents | Tools |
|---|---|---|
| `console_reports/` | EQ, FnO, MTF console tools | 15 |
| `mf_reports/` | Mutual fund tools (Coin) | 13 |
| `crux_reports/` | Ledger, withdrawal, charges, IPO | 13 |
| `kite_admin/` | Kite orders, holdings, positions, GTT | 7 |
| `crm/` | Account modification, PAN, minor accounts | 4 |
| `cashier_reports/` | Payins, e-mandates | 4 |
| `miscellaneous/` | Client data, call info, ST reports | 5 |

**Total: 61 tools + 1 system prompt**

## Workflow

1. Paste QA feedback into Claude Code
2. Claude Code identifies affected tools and proposes changes in `proposed_changes/`
3. Review and approve
4. Claude Code applies changes to tool files and logs in `CHANGELOG.md`
5. Applied proposals are moved to `archive/`

## Key Files

- `CLAUDE.md` — Instructions for Claude Code (auto-read)
- `tool_registry.md` — Maps display names to tool files
- `CHANGELOG.md` — All change history
- `system_prompt.md` — Maven's main system prompt
