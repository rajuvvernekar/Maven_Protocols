# swp_report

## Description

WHEN TO USE:

When clients:
- Ask about SWP status, schedule, or amount
- Report SWP not triggered on expected date
- Ask about next/last SWP date
- Report SWP redemption amount differs from expected

TRIGGER KEYWORDS: "SWP", "systematic withdrawal", "withdrawal plan", "SWP not triggered", "coin"

TAGS: investments

## Protocol

# SWP REPORT PROTOCOL

## Section A: Reference Data

### A1 — SWP Fundamentals

- SWP triggers at 10:00 AM on the scheduled date. For non-DDPI/POA accounts, client receives a T-PIN authorization request after the trigger. Authorization must be completed before 3:00 PM the same day. If not completed, the SWP order for that cycle is cancelled — rejection shows as "UNRID" or "UNITS NOT AUTHORISED" in mf_order_history.  
- Units redeemed = instalment_amount ÷ T-1 NAV. Actual redemption happens at T day NAV (may differ from estimate).  
- SWP created within 2 working days of next instalment → starts from the next cycle, not the current one.

### A2 — T-PIN / DDPI Authorization

To verify DDPI status: check `primary_ddpi_flag` in `get_all_client_data` — Active = DDPI enabled.

| Account Type | Requirement |  
|---|---|  
| Non-DDPI/POA | Must authorize CDSL T-PIN on trigger day per **A1**. |  
| DDPI enabled | No T-PIN required — automatic debit of units each cycle. Recommend as permanent fix. |

### A3 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |  
|---|---|  
| `fund` | Fund name |  
| `frequency` | SWP frequency |  
| `instalment_day` | Instalment day |  
| `instalment_amount` | Share if asked |  
| `next_instalment` | Next instalment date |  
| `last_instalment` | Last instalment date |  
| `created` | SWP creation date |

**Non-shareable:**

| Field | Interpretation |  
|---|---|  
| `swp_id` | Internal — pass as `sip_id` to `sip_modification_log` for modification history |  
| `completed_instalments` | Internal |  
| `tradingsymbol` | Internal |  
| `transaction_type` | Internal |  
| `tag` | Internal |

### A4 — Links

| Topic | URL |  
|---|---|  
| How to activate DDPI | https://support.zerodha.com/category/your-zerodha-account/your-profile/ddpi/articles/activate-ddpi |

## Section B: Decision Flow

### Routing

```  
Route by scenario  
   ├─ SWP didn't trigger / missed instalment → Rule 1  
   ├─ SWP redeemed different amount than expected → Rule 2  
   └─ SWP order rejected with "units not authorized" / T-PIN issue → Rule 3  
```

### Fallback

If no root cause found after completing all diagnostic steps → suggest manual redemption and escalate to human agent if issue recurs.

## Section C: Rules

### Rule 1 — SWP Not Triggered: Sequential Diagnostic

1. **Creation timing check:**  
   Check `created`. If within 2 working days of the instalment date per **A1** → SWP created too close to the instalment; will start from the next cycle.

2. **Modification check:**  
   Invoke `sip_modification_log` using `swp_id` as `sip_id`. Check for `swp_edit` entries within T-2 of the trigger date. If found → cycle skipped due to modification; will trigger from next cycle.

3. **Order status check:**  
   Invoke `mf_order_history` for a SELL order on the trigger date.  
   - Rejected with "UNRID" or "UNITS NOT AUTHORISED" → route to Rule 3.  
   - Rejected with other reason → inform based on `status_message`.  
   - Redeemed → SWP did trigger; clarify with client.  
   - No order → proceed to step 4.

4. **Pledged/available units check (always complete):**  
   Invoke `console_mf_pseudo_holdings` — check `margin`. Invoke `console_mf_holdings` — check `available`.  
   - `margin` > 0 → units pledged; client must unpledge first: Console → Portfolio → Holdings → [fund] → Unpledge.  
   - `available` = 0 or insufficient → units not available for redemption.

5. **No issue found:**  
   All checks normal, no order found → backend issue. Suggest manual redemption for this cycle.

### Rule 2 — Amount Differs

1. Per **A1**: final amount credited may differ from intended SWP amount. Calculation uses previous day's NAV (T-1), but actual redemption uses current day's NAV (T). Client receives more if T NAV is higher; less if lower.

### Rule 3 — T-PIN Authorization Required

1. Per **A1**: CDSL T-PIN authorization must be completed on the same day SWP triggers, between 10:00 AM and 3:00 PM. Order was rejected because not completed on time. Direct client to place a fresh manual redemption request for this cycle.  
2. Recommend DDPI: enabling DDPI allows automatic debit of units without T-PIN authorization each time. Share activation link per **A4**.
