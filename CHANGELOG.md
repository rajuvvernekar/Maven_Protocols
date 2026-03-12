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

### 2026-03-12 — mf_order_history
- [Modified]: Cancel status value — added allotment guard
- [Modified]: Rule 0 — removed redundant example for token efficiency
- [Modified]: Rule 0.1 — added multiple orders for same fund handling
- [Modified]: Rule 1 — expanded Cancel status with payment_confirmed breakdown
- [Modified]: Rule 2 Step 1 — expanded NFO check with allotment/listing flow
- [Modified]: Rule 2 Step 3 — added payment_updated_at not-available case
- [Modified]: Rule 2 Step 4 — split settled_flag=N into within-T+1 vs beyond-T+2
- [Modified]: Rule 2.5 — fund-by-fund initial investment check with FRESH order status
- [Modified]: Rule 4 — added ledger guard for MF payment confirmation
- [Added]: Rule 6 — CDSL authorization loop (repeated OTP redirect) handling
- [Modified]: Rule 16 — simplified NRI exit load handling
- Issues resolved: 11
- Archive: archive/2026-03-12_mf_order_history.md

### 2026-03-12 — fund_allocation_report
- [Added]: Facts — settled_flag and allotment_flag definitions
- [Modified]: Rule 1 — split settled_flag=N into within-T+1 vs beyond-T+2 with refund_utr check
- [Modified]: Rule 2 — updated refund response to keep date_of_refund, added no-hallucination guard and no 5-7 day disclaimer when refund already initiated
- Issues resolved: 3
- Archive: archive/2026-03-12_fund_allocation_report.md

### 2026-03-12 — sip_report
- [Modified]: Rule 1 Step 1 — reordered to check pseudo_holdings first, added multi-SIP per-fund handling
- [Added]: Rule 1 Step 6.7 — stale next_sip_date check for all SIP frequencies
- [Added]: Rule 4 — NRI PIS Account mandate restriction
- [Modified]: Rule 6 — simplified escalation wording
- Issues resolved: 4
- Archive: archive/2026-03-12_sip_report.md

### 2026-03-12 — stp_report
- [Modified]: Rule 5 — minor wording clarification
- [Added]: Rule 6 — STP setup error / source fund navigation flow
- Issues resolved: 2
- Archive: archive/2026-03-12_stp_report.md

### 2026-03-06 — Initial Setup
- All 62 tool protocols extracted from Maven CSV export
- Repository structure created
- Categories: Console Reports (15), MF Reports (13), CRUX Reports (13), Kite Admin (7), CRM (4), Cashier Reports (4), Miscellaneous (5)
- System prompt extracted to root level
- Tools with sparse/no protocol: demat_freeze_status, referral_payout, conditional_orders, get_client_contact, get_client_interactions, st_reports, get_call_info
