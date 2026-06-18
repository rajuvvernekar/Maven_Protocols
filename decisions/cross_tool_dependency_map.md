# Cross-Tool Reference Map (dependency requirement)

Generated from current protocols. For each tool, these are the other tools its protocol invokes — each MUST be present in that tool's configured dependencies in the Maven platform. Also add `get_all_client_data` to every tool (no longer a default fetch).

In-repo check: 0 references to invalid or disabled tools.

| Tool (owner) | # | Must depend on |
|---|---|---|
| `account_modification_report` | 8 | console_eq_holdings, console_mf_holdings, get_all_client_data, kite_orders, kite_positions, ledger_report, pan_status, settlement_date_calculator |
| `amc_charges` | 3 | cashier_payins, get_all_client_data, ledger_report |
| `auto_debit_payins` | 6 | e_mandate_report, e_mandate_schedule_report, get_all_client_data, kite_order_history, ledger_report, mandate_report |
| `cashier_payins` | 5 | crux_qs_payouts, get_all_client_data, kite_margins, ledger_report, settlement_date_calculator |
| `client_retention_dates` | 2 | get_all_client_data, ledger_report |
| `clientwise_margin_report` | 3 | delayed_payment_charges, get_all_client_data, ledger_report |
| `conditional_orders` | 2 | get_all_client_data, mf_order_history |
| `console_eq_external_trades` | 6 | console_eq_holdings, console_eq_holdings_breakdown, console_eq_pnl, console_eq_tradebook_prepared, get_all_client_data, ledger_report |
| `console_eq_holdings` | 8 | console_eq_external_trades, console_eq_holdings_breakdown, console_eq_pseudo_holdings, console_eq_tradebook_prepared, get_all_client_data, kite_holdings, ledger_report, settlement_date_calculator |
| `console_eq_holdings_breakdown` | 2 | console_eq_external_trades, console_eq_holdings |
| `console_eq_pnl` | 4 | console_eq_external_trades, console_eq_holdings, console_eq_holdings_breakdown, console_eq_tradebook_prepared |
| `console_eq_pseudo_holdings` | 3 | console_eq_external_trades, console_eq_holdings, kite_holdings |
| `console_eq_tradebook` | 4 | console_eq_external_trades, console_eq_holdings_breakdown, console_eq_tradebook_prepared, ledger_report |
| `console_eq_tradebook_prepared` | 4 | console_eq_external_trades, console_eq_holdings_breakdown, kite_order_history, ledger_report |
| `console_fno_pnl` | 2 | console_eq_pnl, get_all_client_data |
| `console_fno_positions` | 2 | console_fno_pnl, get_all_client_data |
| `console_fno_tradebook` | 3 | console_fno_pnl, console_fno_positions, console_fno_tradebook_prepared |
| `console_fno_tradebook_prepared` | 1 | get_all_client_data |
| `console_instant_pledge` | 5 | account_modification_report, console_eq_holdings, console_eq_pseudo_holdings, console_mtf_holdings, get_all_client_data |
| `console_mf_external_trades` | 1 | console_mf_tradebook |
| `console_mf_holdings` | 41 | account_modification_report, amc_charges, auto_debit_payins, cashier_payins, console_eq_external_trades, console_eq_holdings, console_eq_holdings_breakdown, console_eq_pnl, console_eq_pseudo_holdings, console_eq_tradebook_prepared, console_fno_positions, console_fno_tradebook_prepared, console_instant_pledge, console_mf_external_trades, console_mf_pseudo_holdings, console_mf_tradebook, console_mtf_conversion, console_mtf_holdings, crux_qs_payouts, e_mandate_report, e_mandate_schedule_report, fund_allocation_report, get_all_client_data, kite_holdings, kite_margins, kite_order_history, kite_orders, kite_positions, ledger_report, mandate_report, mf_order_history, pan_status, pledge_request_report, settlement_date_calculator, sip_report, stock_gift_requests, stock_transfers, stp_report, swp_report, tradewise_charges_report, withdrawal_request |
| `console_mf_pseudo_holdings` | 6 | console_mf_external_trades, console_mf_holdings, console_mf_tradebook, get_all_client_data, mf_order_history, settlement_date_calculator |
| `console_mf_tradebook` | 2 | console_mf_external_trades, console_mf_pseudo_holdings |
| `console_mtf_conversion` | 3 | console_eq_holdings, console_mtf_holdings, kite_order_history |
| `console_mtf_holdings` | 4 | console_eq_holdings, console_eq_holdings_breakdown, console_mtf_conversion, ledger_report |
| `corporate_action_orders` | 3 | console_eq_external_trades, console_eq_holdings, get_all_client_data |
| `crux_qs_payouts` | 4 | client_retention_dates, kite_order_history, ledger_report, withdrawal_request |
| `e_mandate_report` | 2 | get_all_client_data, mandate_report |
| `e_mandate_schedule_report` | 2 | auto_debit_payins, kite_order_history |
| `fund_allocation_report` | 3 | mandate_debit_report, mf_order_history, settlement_date_calculator |
| `get_all_client_data` | 1 | pan_status |
| `ipo_application` | 1 | get_all_client_data |
| `kite_gtt` | 6 | get_all_client_data, kite_gtt_archived, kite_holdings, kite_margins, kite_order_history, kite_positions |
| `kite_gtt_archived` | 5 | get_all_client_data, kite_gtt, kite_holdings, kite_margins, kite_order_history |
| `kite_holdings` | 12 | console_eq_external_trades, console_eq_holdings, console_eq_pseudo_holdings, console_eq_tradebook_prepared, get_all_client_data, kite_gtt, kite_margins, kite_order_history, kite_orders, kite_positions, ledger_report, pledge_request_report |
| `kite_margins` | 14 | account_modification_report, cashier_payins, console_eq_holdings, console_fno_positions, console_instant_pledge, get_all_client_data, kite_holdings, kite_order_history, kite_orders, kite_positions, ledger_report, pledge_request_report, settlement_date_calculator, withdrawal_request |
| `kite_order_history` | 9 | console_eq_holdings, get_all_client_data, kite_gtt, kite_gtt_archived, kite_holdings, kite_margins, kite_orders, kite_positions, settlement_date_calculator |
| `kite_orders` | 8 | console_eq_holdings, get_all_client_data, kite_holdings, kite_margins, kite_order_history, kite_positions, pan_status, settlement_date_calculator |
| `kite_positions` | 10 | console_eq_holdings, console_fno_positions, console_fno_tradebook_prepared, get_all_client_data, kite_holdings, kite_margins, kite_order_history, kite_orders, ledger_report, settlement_date_calculator |
| `ledger_report` | 12 | amc_charges, client_retention_dates, console_mtf_holdings, contract_note_charges, crux_qs_payouts, delayed_payment_charges, get_all_client_data, kite_margins, kite_order_history, pledge_request_report, settlement_date_calculator, withdrawal_request |
| `mandate_debit_report` | 6 | fund_allocation_report, mandate_report, mf_order_history, settlement_date_calculator, sip_modification_log, sip_report |
| `mandate_report` | 3 | get_all_client_data, settlement_date_calculator, sip_report |
| `mf_order_history` | 11 | console_eq_external_trades, console_mf_holdings, console_mf_pseudo_holdings, console_mf_tradebook, fund_allocation_report, get_all_client_data, mandate_debit_report, mandate_report, settlement_date_calculator, sip_modification_log, sip_report |
| `minor_account_opening` | 1 | get_all_client_data |
| `pan_status` | 1 | get_all_client_data |
| `pledge_request_report` | 1 | console_instant_pledge |
| `sip_report` | 8 | console_mf_pseudo_holdings, console_mf_tradebook, get_all_client_data, mandate_debit_report, mandate_report, mf_order_history, settlement_date_calculator, sip_modification_log |
| `stock_gift_requests` | 2 | console_eq_external_trades, console_eq_holdings |
| `stock_transfers` | 2 | account_modification_report, console_eq_external_trades |
| `stp_report` | 9 | console_mf_holdings, console_mf_pseudo_holdings, fund_allocation_report, get_all_client_data, mandate_debit_report, mf_order_history, sip_modification_log, sip_report, swp_report |
| `swp_report` | 5 | console_mf_holdings, console_mf_pseudo_holdings, get_all_client_data, mf_order_history, sip_modification_log |
| `tradewise_charges_report` | 2 | get_all_client_data, ledger_report |
| `withdrawal_request` | 8 | get_all_client_data, kite_holdings, kite_margins, kite_order_history, kite_orders, kite_positions, ledger_report, settlement_date_calculator |

Total: 53 tools invoke others; 281 reference edges.
