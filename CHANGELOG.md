# Changelog

All protocol changes are logged here. Each entry links back to the proposed_changes file (archived after applying).

## Format
```
### YYYY-MM-DD — tool_name
- [Added/Modified/Removed]: Brief description of change
- Issues resolved: [count]
- Archive: archive/YYYY-MM-DD_tool_name.md
```

---

### 2026-03-06 — account_modification_report
- [Added]: `<facts>` — ReKYC auto re-enables Coin/MF bullet
- [Added]: `<account_closure>` — `<post_closure_new_account_error>` tag (escalate to human agent)
- [Modified]: Rule 3 — Added explicit contact detail timeline example (mobile/email → activation)
- [Modified]: Rule 4 — Mandatory pre-check for existing ReKYC request before giving guidance; rejected ReKYC escalates to KYC team
- [Added]: Rule 5 — Post-closure new account error handling (escalate to agent)
- [Modified]: Rule 7 Dormancy step 3 — Coin/MF excluded from segment activation guidance; added get_all_client_data cross-check
- Issues resolved: 4

---

### 2026-03-06 — Initial Setup
- All 62 tool protocols extracted from Maven CSV export
- Repository structure created
- Categories: Console Reports (15), MF Reports (13), CRUX Reports (13), Kite Admin (7), CRM (4), Cashier Reports (4), Miscellaneous (5)
- System prompt extracted to root level
- Tools with sparse/no protocol: demat_freeze_status, referral_payout, conditional_orders, get_client_contact, get_client_interactions, st_reports, get_call_info
