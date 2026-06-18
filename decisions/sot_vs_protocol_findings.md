# SOT vs Protocol — Tool Dependency Findings

Date: 2026-06-17
Compares the frontend Maven **SOT** (`Tool dependencies SOT.csv`, source of truth for configured
dependencies) against the **protocol-invoked** set (what each protocol actually `invoke`s, derived
from the live repo). Full row-level diff: `decisions/sot_vs_protocol_diff.csv`.

**Headline: 81 to ADD to SOT, 36 in-SOT-not-invoked (6 clearly stale, ~17 protocol gaps, ~13 likely stale).**

---

## Key rule change (recorded separately)
`get_all_client_data` is **no longer a default/auto-fetch tool** and is **not** a dependency on every
tool — only where a protocol actually invokes it. This reverses the earlier doc-3 "add to all tools"
instruction. See `decisions/get_all_client_data_dependency.md`.

---

## 1) ADD to SOT — invoked by protocol but not configured (81 edges)
The bulk are the two "newly non-default" tools:
- **`get_all_client_data` → 22 tools** need it added. It used to be the default fetch, so it was never
  configured as a dependency anywhere; now that it is a normal tool, every protocol that invokes it
  must list it in SOT.
- **`settlement_date_calculator` → ~13 tools** (the working-day calculator, wired in across recent feedback).
- Recent protocol additions, e.g.:
  - `console_eq_holdings` → `kite_order_history`, `kite_positions`
  - `console_eq_holdings_breakdown` → `console_eq_tradebook_prepared`
  - `console_eq_tradebook_prepared` → `console_eq_holdings`, `console_eq_holdings_breakdown`, `kite_order_history`, `ledger_report`
  - `kite_margins` → `account_modification_report`, `cashier_payins`, `console_eq_holdings`, `console_fno_positions`, `console_instant_pledge`, `pledge_request_report`, `withdrawal_request` (+ get_all_client_data, settlement_date_calculator)

(Full per-tool ADD list in `sot_vs_protocol_diff.csv`, Direction = `invoked-not-in-SOT`.)

---

## 2) REMOVE from SOT — stale (6)
- **Disabled tools:**
  - `console_eq_tradebook` — in `console_eq_external_trades`, `console_eq_holdings_breakdown`, `console_eq_tradebook_prepared`
  - `console_fno_tradebook` — in `console_fno_positions`, `console_fno_tradebook_prepared`
- **Self-reference (data error):** `stock_gift_requests` lists itself.

---

## 3) PROTOCOL GAPS — referenced in prose but never invoked (the important category)
These SOT dependencies are mentioned in the protocol's prose but the protocol does not `invoke` the
tool. Fix = add an explicit `invoke` in the protocol (then it becomes a clean ADD to SOT). Each needs a
quick context read before editing ("order" etc. are common words → some may be false positives).

| Tool | Should invoke | Evidence / note |
|---|---|---|
| `cashier_payins` | `kite_order_history` | Rule 9.2 "If orders exist on the payin date…" — **confirmed gap** |
| `cashier_payins` | `delayed_payment_charges` | DPC mentioned, but pulled via ledger_report — likely covered (weak) |
| `tradewise_charges_report` | `kite_order_history` | references order data without invoking |
| `withdrawal_request` | `crux_qs_payouts` | QS payout referenced in prose |
| `kite_holdings` | `console_mtf_holdings` | MTF holdings referenced |
| `sip_report` | `fund_allocation_report` | allotment check in prose |
| `mandate_report` | `mandate_debit_report` | debit referenced |
| `corporate_action_orders` | `console_eq_pnl` | P&L referenced |
| `kite_gtt` | `kite_orders` | GTT/orders cross-reference |
| `kite_orders` | `kite_gtt` | GTT cross-reference |
| `e_mandate_report` | `e_mandate_schedule_report` | schedule cross-reference |
| `e_mandate_schedule_report` | `e_mandate_report` | mandate cross-reference |
| `pledge_request_report` | `ledger_report` | ledger referenced |
| `stp_report` | `mandate_report` | mandate referenced |
| `console_mf_external_trades` | `console_mf_pseudo_holdings` | holdings referenced |

---

## 4) Likely stale — in SOT, no prose proxy in protocol (~13, probably remove)
e.g. `console_fno_tradebook_prepared`→`console_fno_pnl`; `sip_report`→`stp_report`/`swp_report`;
`stock_transfers`→`console_eq_holdings`/`stock_gift_requests`; `contract_note_charges`→`ledger_report`;
`console_mf_external_trades`→`console_mf_holdings`; `console_mf_tradebook`→`console_mf_holdings`;
`swp_report`→`stp_report`; `pledge_request_report`→`delayed_payment_charges`;
`crux_qs_payouts`→`get_all_client_data` (not invoked → remove per the get_all_client_data rule).

---

## Related open structural issues (from the protocol consistency audit)
- `mandate_debit_report` — routing points to a **non-existent Rule 5** (Rule 4 handles pending+failed; Rule 6 should renumber to 5).
- `client_retention_dates` — references a **non-existent A4** + stray "client retension statement" fragment.
- A-section numbering gaps (escalation-consolidation leftovers): `console_instant_pledge` (no A6), `kite_margins` (no A8), `kite_orders` (no A17), `kite_positions` (no A12).
- Colon-style headers (should be em-dash): `cashier_payins`, `withdrawal_request`.

---

## Suggested next steps
1. Fix the **protocol gaps** (Section 3) — read each in context, add explicit `invoke`, push. Then they become clean SOT ADDs.
2. In Maven SOT config: apply the 81 ADDs (`sot_vs_protocol_diff.csv`) and the 6 stale REMOVEs (Section 2).
3. Separately, fix the structural issues (broken Rule 5 / A4 refs, A-gaps, colon headers).
