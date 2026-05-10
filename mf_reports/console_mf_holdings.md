# console_mf_holdings

## Description

WHEN TO USE:

When need to cross-check:
- Units available for redemption or SWP (`available` field)
- Latest demat credit date (`holdings_date`)
- Total quantity of units held (`total_quantity`)
- Mismatch between demat records and Coin-facing holdings

**This is the SECONDARY tool. Always check console_mf_pseudo_holdings first for MF holdings queries. Invoke this tool only for the specific fields listed above.**

TRIGGER KEYWORDS: "available units", "demat holdings", "units for redemption", "coin"

TAGS: investments, holdings

## Protocol

# CONSOLE MF HOLDINGS PROTOCOL

## Section A: Reference Data

### A1 — Fundamentals

- ETF FOF is an MF — appears in Coin holdings. Pure ETFs appear in Kite holdings only.

### A2 — Settlement Timelines

| Fund Type | Units Visible |  
|---|---|  
| Liquid funds | T day by 7 PM |  
| Non-liquid funds | T+1 day by 7 PM |

### A3 — NAV Display Differences

| Platform | NAV Date |  
|---|---|  
| Console | T-2 days |  
| Coin | T-1 day |

-This difference in NAV dates causes P&L values to appear different between platforms. For latest valuation, refer to Coin. See **A5** for support article.

### A4 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |  
|---|---|  
| `tradingsymbol` | Fund name |  
| `buy_average` | Buy average |  
| `buy_value` | Total invested value |  
| `total_quantity` | Total units held |

**Non-shareable:**

| Field | Interpretation |  
|---|---|  
| `holdings_date` | Latest demat credit — internal |  
| `failure_date` | invoke console_mf_pseudo_holdings |  
| `available` | Critical for redemption/SWP checks — internal reasoning |  
| `discrepant` | Cross-check only |  
| `loan` | Internal |  
| `closing_price` | Internal |  
| `name` | Internal |  
| `client_id` | Internal client identifier |  
| `isin` | Internal ISIN |  
| `instrument_id` | Internal instrument id |  
| `t1` | Internal |  
| `pending` | Internal |

### A5 — Links

| Topic | URL |  
|---|---|  
| MF NAV display difference (Console T-2, Coin T-1) | https://support.zerodha.com/category/mutual-funds/coin-general/coin-reports/articles/mf-nav-of-t-2-days-on-console |

## Section B: Decision Flow

### Routing

```  
Route by scenario  
   ├─ Need to verify units available for redemption/SWP → Rule 1  
   ├─ Units not visible after allotment → Rule 2  
   ├─ Discrepancy cross-check (requested by console_mf_pseudo_holdings) → Rule 3  
   ├─ Buy average incorrect (flagged by console_mf_pseudo_holdings) → Rule 4  
   ├─ failure_date seen in data → Rule 5  
   └─ Console vs Coin value difference → Rule 6  
```

### Fallback

Route to console_mf_pseudo_holdings.

## Section C: Rules

### Rule 1 — Units Available for Redemption/SWP

1. Check `available` field.  
2. If `available` = 0 or insufficient → inform client units not available for redemption/SWP.  
3. If `available` > 0 but redemption is failing → check pledged status via console_mf_pseudo_holdings (`margin` field).

### Rule 2 — Units Not Visible After Allotment

1. Invoke `console_mf_pseudo_holdings` for discrepancy diagnosis.  
2. Use this tool only to verify `holdings_date` (latest demat credit) and `total_quantity`.  
3. If within settlement timeline per **A2** → units will be visible by the timeline.  
4. If beyond timeline → check `holdings_date` for latest credit date. Route full discrepancy diagnosis to console_mf_pseudo_holdings.

### Rule 3 — Discrepancy Cross-Check

1. Invoke `console_mf_pseudo_holdings` — compare `available` and `discrepant` values.  
2. If mismatch → invoke `console_mf_tradebook` for missing trade entries.  
3. If trade entry exists but mismatch persists → escalate to human agent.

### Rule 4 — Buy Average Incorrect

1. Invoke `console_mf_external_trades` — verify all entries are correct and complete.  
2. If units were transferred in, verify external trade entries have been added.  
3. If all entries correct and `failure_date` is empty → escalate to human agent.

### Rule 5 — Failure Date

1. Invoke `console_mf_pseudo_holdings`.  
2. Escalate to human agent.

### Rule 6 — Console vs Coin Value Difference

1. Per **A3**, explain the NAV date difference as the cause and direct client to Coin for latest valuation.  
2. Share link from **A5**.
