# pledge_request_report

## Description

WHEN TO USE:

When clients:
- Ask about a specific pledge or unpledge request status from weeks/months ago
- Report collateral margin reduced and need to trace which unpledge caused it
- Dispute collateral amount shown in DPC report (need to verify what was pledged on specific dates)
- Ask why collateral margin value changed (need to check current pledged holdings breakdown)
- Report pledged shares not showing collateral (need to verify pledge status in historical records)
- Need older pledge/unpledge request history (more than 30 days old)
- Need pledge/unpledge history for a date range (e.g., for DPC dispute or margin audit)
- Need Pledged Holdings snapshot (current pledged securities, qty, value, collateral margin)

TRIGGER KEYWORDS: "pledge history", "old pledge request", "unpledge history", "pledge last month", "collateral reduced why", "pledged holdings", "collateral value", "collateral margin breakdown", "pledge charges history", "pledge from [date]", "what is pledged currently", "pledged securities list"

TAGS: margins

## Protocol

# PLEDGE REQUEST REPORT PROTOCOL

---

## Section A: Reference Data

---

### A1 — Pledge Fundamentals

- Pledge charges: ₹30 \+ 18% GST = ₹35.4 standard. A Journal Entry may appear on the ledger for specific pledge types (some instruments).  
- Collateral margin = market value × (1 − haircut%). Haircut varies by security.  
- Collateral value changes daily based on market price and haircut updates.  
- MF pledge/unpledge requests are initiated via Coin (Zerodha's MF platform) and appear in this report alongside equity, with the same `pledge_type` values, statuses, and process.

---

### A2 — Status Values

| Status | Meaning |  
|---|---|  
| Processed | Request completed successfully — collateral reflected (pledge) or shares released (unpledge). |  
| Pending | Awaiting CDSL processing — collateral not yet reflected (pledge) or shares not yet released (unpledge). |  
| Rejected / Failed | Request did not complete. |

---

### A3 — Collateral Haircut Reference

| Security Type | Typical Haircut | Collateral Margin Example (₹1,00,000 market value) |  
|---|---|---|  
| Liquid ETFs (LIQUIDBEES, LIQUIDCASE etc.) | \~10% | \~₹90,000 |  
| Large-cap equity | \~50% (varies) | \~₹50,000 |  
| Mid/small-cap equity | Higher than 50% (varies) | Less than ₹50,000 |

Haircut percentages are set by the exchange and can change. The collateral margin shown when using `pledge_type = Pledge Holdings` reflects the current applied haircut.

---

### A4 — Field Rules

**Shareable with client:**

| Field | Interpretation |  
|---|---|  
| `pledge_date` | Date the pledge or unpledge was processed |  
| `tradingsymbol` | Trading symbol of the pledged instrument |  
| `quantity` | Number of shares |  
| `status` | Translate per A2 before sharing |

**Non-shareable:**

| Field | Interpretation |  
|---|---|  
| `pledge_time` | Timestamp of the pledge action |  
| `isin` | ISIN code of the instrument |  
| `previous_quantity` | Quantity pledged before the latest change |  
| `pledge_type` | Internal pledge type classification |  
| `remarks` | Internal remarks |  
| `cdsl_status` | CDSL processing status |  
| `pledge_verification_date` | Date of pledge verification at CDSL |  
| `value` | Market value of the pledged holding |  
| `collateral_margin` | Collateral margin available against the pledge |  
| `creation` | Record creation timestamp |  
| `client_id` | Internal client identifier |

---

### A5 — Collateral Reduction Causes

| Cause | Meaning |  
|---|---|  
| Unpledge processed | An unpledge request for the matching `tradingsymbol` was processed, reducing the pledged quantity and therefore the collateral margin. |  
| Market price drop | The market value of the pledged security has decreased, reducing the collateral margin even though pledged quantity is unchanged. |  
| Haircut change | The haircut % applied to the security was updated by the exchange, changing the collateral margin without any change in qty or price. |  
| Stock removed from approved list | The security no longer appears on the approved pledge list, so it no longer contributes to collateral margin. |

---

### A6 — Pledge Failure Reasons

| Reason | Meaning |  
|---|---|  
| Security not on approved list | The security is not on the exchange-approved list for pledging, so the request will be rejected outright. |  
| T1 holdings | Shares bought today have not yet settled and cannot be pledged until settlement is complete (T+1). |  
| Insufficient free qty | The client does not have enough free (unpledged) shares of the security to fulfil the requested pledge quantity. |  
| Technical issue | The security is approved and free qty is sufficient, but the request is still failing — likely a platform-side issue. |

---

### A7 — Escalation Triggers

- Escalate to human agent when any of the following occur:

- Pledge status = Processed but collateral margin not reflected after 24+ hours.  
- Qty in `Pledge Holdings` output differs from what client actually pledged per request history.  
- Collateral margin in `Pledge Holdings` output significantly differs from expected (market value × expected haircut).  
- External pledge shares stuck in Console (client pledged with another institution).  
- Pledge/unpledge page persistently failing for an approved security with sufficient free qty (after basic troubleshooting).  
- Pending status stuck for more than 30 days.

---

## Section B: Decision Flow

### Routing

```  
Route by scenario  
   ├─ Specific past pledge/unpledge request status → Rule 1  
   ├─ Collateral margin reduced → Rule 2  
   ├─ Currently pledged / total collateral value query → Rule 3  
   ├─ Collateral margin less than market value → Rule 4  
   ├─ MF pledge / unpledge query → Rule 5  
   ├─ "Pledging is not allowed" or similar error → Rule 6  
   ├─ Unpledge rejected with "Margin already utilized" → Rule 7  
   └─ External pledge (pledged with another institution) → Rule 8  
```

### Fallback

- If no root cause is found → escalate to human agent.

---

## Section C: Rules

---

### Rule 1 — Historical Pledge/Unpledge Status

1. For requests older than 30 days, invoke this tool with `pledge_type = Pledge` (for pledge queries) or `pledge_type = Unpledge` (for unpledge queries). For recent requests (last 30 days), invoke `console_instant_pledge`.  
2. Find the matching `tradingsymbol` for which the client has raised the query.  
3. If **Processed:** Request completed successfully.  
4. If **Pending** and request is older than 30 days → escalate to human agent.  
5. If **Rejected/Failed** → identify cause using A6.

---

### Rule 2 — Collateral Reduced: Trace Cause

1. Invoke this tool twice: `pledge_type = Pledge Holdings` (current state) and `pledge_type = Unpledge` (recent unpledge activity).  
2. Work through the causes in A5 in order:  
   - **Unpledge processed:** Check `pledge_type = Unpledge` results for recent entries matching `tradingsymbol`. If found, refer to A5.  
   - **Market price drop:** Compare current `value` in `Pledge Holdings` output against prior period. If decreased, refer to A5.  
   - **Haircut change:** Check if `collateral_margin` changed without a change in qty or price in the `Pledge Holdings` output. Current haircut values can be verified at https://zerodha.com/approved-securities/#tab-noncash_equity  
   - **Stock removed from approved list:** If the security no longer generates collateral margin, refer to A5.  
3. Share the specific security name and reduction amount only when the client asks for that level of detail.

---

### Rule 3 — Pledged Holdings Snapshot

1. Invoke this tool with `pledge_type = Pledge Holdings`.  
2. Sum the `collateral_margin` across all securities to get the total collateral margin.  
3. Default to sharing the summary total only. Share per-security `tradingsymbol`, `quantity`, and `collateral_margin` breakdown only if the client specifically asks about a particular stock or requests the full breakdown.

---

### Rule 4 — Collateral Margin Calculation Explanation

1. Explain the collateral margin formula and haircut variation per A1 and A3.  
2. If the client has pledged securities, invoke this tool with `pledge_type = Pledge Holdings` and use the actual `value` and `collateral_margin` fields to explain the calculation specific to their holdings.

---

### Rule 5 — MF Pledge/Unpledge

MF queries follow the same rules as equity per A1. Apply Rule 1 (status), Rule 2 (collateral reduced), or Rule 3 (holdings snapshot) based on the query type.

---

### Rule 6 — Pledge Not Allowed Error

1. Work through the failure reasons in A6 in order: security not on approved list → T1 holdings → insufficient free qty → technical issue.  
2. If the issue persists after basic troubleshooting (re-login, retry) and the security is confirmed approved with sufficient free qty → escalate to human agent.

---

### Rule 7 — Unpledge Rejected: Margin Utilized

- The unpledge request was rejected because the collateral margin from the pledged shares is currently being utilised against open positions. Unpledge cannot be processed until the positions using this margin are closed or equivalent cash is added.

---

### Rule 8 — External Pledge

1. Shares pledged with another institution (external pledge) remain visible in Console as holdings but are encumbered and cannot be traded or transferred.  
2. If the client needs external pledge shares removed from Console → escalate to human agent.
