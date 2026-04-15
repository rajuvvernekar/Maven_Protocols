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

## Protocol

# PLEDGE REQUEST REPORT PROTOCOL 

### A1 — Tool Modes

This tool has two modes, accessed via a dropdown:

| Mode | Purpose | Use When |
|---|---|---|
| Pledge Request Report | Historical pledge/unpledge requests for a date range — shows each request with status, qty, security, date | Investigating past requests, tracing status, checking what happened on a specific date |
| Pledged Holdings Report | Snapshot of currently pledged securities with value and collateral margin per security | Checking current state, verifying total collateral, investigating collateral reduction |

### A2 — Pledge Fundamentals

- Pledge charges: ₹30+18% GST= ₹35.4 standard. A Journal Entry may appear on the ledger for specific pledge types (some instruments).
- Collateral margin = market value × (1 − haircut%). Haircut varies by security — typically 50% for equity, ~10% for liquid ETFs/LIQUIDBEES.
- Collateral value changes daily based on market price and haircut updates.
- MF pledge/unpledge: handled via Coin (Zerodha's MF platform) — same status tracking but different flow. This tool does not cover MF pledge details.

### A3 — Status Values (Pledge Request Report)

| Status | Meaning | Action |
|---|---|---|
| Processed | Request completed successfully | Collateral should be reflected (pledge) or shares released (unpledge) |
| Pending | Awaiting CDSL processing | If pledge → collateral not yet reflected. If unpledge → shares not yet released. |
| Rejected / Failed | Request did not complete | Investigate cause — security not approved, insufficient qty, margin utilized, or technical issue |

A Pending status older than 30 days is abnormal → escalate (per Rule 9).

### A4 — Collateral Haircut Reference

| Security Type | Typical Haircut | Collateral Margin Example (₹1,00,000 market value) |
|---|---|---|
| Liquid ETFs (LIQUIDBEES, LIQUIDCASE etc.) | ~10% | ~₹90,000 |
| Large-cap equity | ~50% (varies) | ~₹50,000 |
| Mid/small-cap equity | Higher than 50% (varies) | Less than ₹50,000 |

Haircut percentages are set by the exchange and can change. The collateral margin shown in Pledged Holdings reflects the current applied haircut.

### A5 — Field Rules

**Pledge Request Report:**

| Shareable (if client asks) | Internal reasoning only (never share) |
|---|---|
| `pledge_date`, `tradingsymbol`, `quantity`, `status` (translated per **A3**) | `pledge_time`, `client_id`, `isin`, `previous_quantity`, `pledge_type` (use internally to determine pledge vs unpledge), `remarks`, `cdsl_status`, `pledge_verification_date` |

**Pledged Holdings Report:**

| Shareable | Internal reasoning only (No client use) |
|---|---|
| `tradingsymbol`, `quantity`, `value`, `collateral_margin` (share only when client complains about collateral reduction) | `pledge_date`, `client_id`, `isin`, `status`, `creation` |

**Collateral holdings breakup:** Share per-security collateral details only when the client specifically complains about collateral reduction or asks about a particular stock's collateral value. Provide a summary total by default — not the full list. (This is counterintuitive — the model may default to sharing detailed data when it's available. Always summarize unless the client explicitly asks for per-security detail or reports a collateral reduction.)

### A6 — Collateral Reduction Causes

Check in this order when a client reports reduced collateral:

| Cause | How to Verify | Client-Facing Explanation |
|---|---|---|
| Unpledge processed | Check Pledge Request Report for recent unpledge requests | "An unpledge of [qty] shares of [tradingsymbol] was processed on [date], which reduced your collateral." |
| Market price drop | Compare current value against prior period | "The market value of your pledged securities has decreased, which reduced the collateral margin." |
| Haircut change | Collateral margin changed without qty or price change | "The haircut percentage for [tradingsymbol] may have been updated, affecting collateral value." |
| Stock removed from approved list | Security no longer generating collateral margin | "If [tradingsymbol] was removed from the approved pledge list, it would no longer count as collateral." |

Share the specific security and reduction amount only when the client asks.

### A7 — Pledge Failure Reasons

| Reason | Client-Facing Explanation |
|---|---|
| Security not on approved list | "Some securities are not approved for pledging. If [tradingsymbol] is not on the approved list, the pledge request will fail. You can check the list of approved securities on Zerodha's pledge page." |
| T1 holdings (bought today, not settled) | "Shares bought today haven't settled yet and cannot be pledged until settlement is complete." |
| Insufficient free qty | "You don't have enough free (unpledged) shares of [tradingsymbol] to complete this pledge request." |
| Technical issue | "If the security is approved and you have sufficient free qty, try re-logging and placing the request again." |

### A8 — Cross-Reference Protocols

| Topic | Refer to |
|---|---|
| Recent pledge requests (last 30 days) | Console Instant Pledge — use instead of this tool for recent data |
| DPC collateral verification (client disputes DPC collateral amount) | Delayed Payment Charges protocol |
| Pledge/unpledge charge entries on ledger | Ledger Report protocol |
| Pledged shares vs free shares in holdings | Console EQ Holdings |

### A9 — Escalation Triggers (Consolidated)

Escalate when any of the following occur:
- Pledge status = Processed but collateral margin not reflected after 24+ hours.
- Pledged Holdings qty differs from what client actually pledged per request history.
- Collateral margin in Pledged Holdings significantly differs from expected (market value × expected haircut).
- External pledge shares stuck in Console (client pledged with another institution).
- Pledge/unpledge page persistently failing for an approved security with sufficient free qty (after basic troubleshooting).
- Pending status stuck for more than 30 days.
- MF pledge/unpledge issue (handled via Coin — escalate directly).

Include in escalation: client ID, tradingsymbol, pledge_date, status, and the specific issue.


### Preflight (run on every query)

1. Determine which tool mode is needed: Pledge Request Report (historical) or Pledged Holdings Report (current state). Use **A1** to decide.
2. Fetch the relevant report data.
3. Apply field protection per **A5** — identify shareable vs internal-only fields for the active mode.
4. Translate status values using **A3** for client communication.
5. Format amounts with ₹ and Indian comma notation. Format dates as DD MMM YYYY.

### Routing Tree

```
Query relates to pledge/unpledge/collateral →
│
├─ Client asks about a specific past pledge/unpledge request
│  → Rule 1
│
├─ Client reports collateral margin reduced
│  → Rule 2
│
├─ Client asks what is currently pledged / total collateral value
│  → Rule 3
│
├─ Client asks why collateral margin is less than market value
│  → Rule 4
│
├─ Client asks about mutual fund pledge / reports MF pledge issue
│  → Rule 5 (Escalate)
│
├─ Client reports "Pledging is not allowed" or similar error
│  → Rule 6
│
├─ Unpledge rejected with "Margin already utilized"
│  → Rule 7
│
├─ External pledge (pledged with another institution)
│  → Rule 8
│
└─ Data mismatch / no root cause found
   → Rule 9 (Escalation)
```

### Scope

- Address: pledge/unpledge request status, collateral margin queries, pledge errors, and collateral reduction investigations.

### Fallback

If no root cause is identified after checking all relevant rules → escalate per Rule 9.


### Rule 1 — Historical Pledge/Unpledge Status

1. For requests older than 30 days, use the Pledge Request Report. For recent requests (last 30 days), prefer Console Instant Pledge (per **A8**).
2. Find the matching `tradingsymbol` in the report.
3. Respond: "Your [pledge/unpledge] request for [quantity] shares of [tradingsymbol] on [pledge_date]: Status — [Processed / Pending / Rejected]."
4. If Processed: "The request was completed successfully."
5. If Pending and the request is older than 30 days → escalate per Rule 9.
6. If Rejected/Failed → investigate cause using **A7** and advise accordingly.

### Rule 2 — Collateral Reduced: Trace Cause

1. Check both reports: Pledged Holdings (current state) and Pledge Request Report (recent unpledge activity).
2. Work through the causes in **A6** in order: unpledge processed → market price drop → haircut change → stock removed from approved list.
3. Respond with the identified cause using the client-facing explanation from **A6**.
4. Share the specific security and reduction amount only when the client asks for detail.

### Rule 3 — Pledged Holdings Snapshot

1. Use the Pledged Holdings Report.
2. Respond with a summary: "Your total collateral margin from pledged securities is ₹[sum of collateral_margin]. This is based on [N] pledged securities."
3. Share per-security details only if the client specifically asks about a particular stock's collateral value. Do not volunteer the full list (per **A5**).

### Rule 4 — Collateral Margin Calculation Explanation

1. Respond using the haircut reference from **A4**:
   "The collateral margin is the market value of your pledged shares minus a haircut percentage. The haircut varies by security:
   - Liquid ETFs (LIQUIDBEES, LIQUIDCASE etc.): ~10% haircut
   - Large-cap equity: ~50% haircut (varies)
   - Mid/small-cap: higher haircut

   So if you pledged shares worth ₹1,00,000 with a 50% haircut, your collateral margin would be approximately ₹50,000."

### Rule 5 — MF Pledge/Unpledge via Coin

1. Escalate directly. MF pledge/unpledge is handled through Coin (per **A2**) and this tool does not cover MF pledge details.
2. Include in escalation: client ID, MF scheme name if provided, and the specific issue.

### Rule 6 — Pledge Not Allowed Error

1. Check if the security is on the approved pledge list.
2. Work through the failure reasons in **A7**: security not approved → T1 holdings → insufficient free qty → technical issue.
3. Respond with the applicable explanation from **A7**.
4. If the issue persists after basic troubleshooting (re-login, retry) and the security is approved with sufficient free qty → escalate per Rule 9.

### Rule 7 — Unpledge Rejected: Margin Utilized

1. Respond: "Your unpledge request for [tradingsymbol] was rejected because the collateral margin from these pledged shares is currently being used against your open positions. To unpledge, you would need to either close positions using this margin or add equivalent funds first."

### Rule 8 — External Pledge

1. Respond: "If you pledged your shares with another institution (external pledge), the shares may still appear in Console as holdings. However, they are encumbered and cannot be traded or transferred. For external pledge-related queries, please check with the DP team."
2. If the client needs external pledge shares removed from Console view → escalate per Rule 9.

### Rule 9 — Escalation

Escalate when any trigger in **A9** is met.

Include in escalation: client ID, tradingsymbol, pledge_date, status, and the specific issue.

