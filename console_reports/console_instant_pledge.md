# console_instant_pledge

## Description

WHEN TO USE:

When clients:
- Ask about the status of a pledge or unpledge request
- Report pledge request failed or showing as pending
- Report pledged shares not showing collateral margin
- Report "Something went wrong" error while pledging
- Ask about overdue pledge requests
- Ask about pledge history for a specific security
- Report unpledge request rejected

TRIGGER KEYWORDS: "pledge status", "pledge failed", "pledge request", "unpledge status", "unpledge failed", "pledge pending", "pledge overdue", "collateral not showing", "pledge success", "pledge error", "something went wrong pledge", "pledge history", "re-pledge"

## Protocol

# CONSOLE INSTANT PLEDGE PROTOCOL


---

### A1 — Fundamentals

This tool shows instant pledge/unpledge request history — status, qty, date, and security details. Pledging creates collateral margin; unpledging releases it. Collateral is reflected after CDSL confirmation (usually instant, can take up to 30 minutes).

`previous_quantity` shows pledged qty before the transaction — useful to track incremental pledges.

MTF shares are auto-pledged — those are separate from client-initiated pledges in this tool.


### A2 — Field Usage Rules

**Shareable fields:**

`pledge_date` | `tradingsymbol` | `isin` | `status` | `pledge_type` | `quantity` | `previous_quantity` | `pledge_creation`

**Internal-only fields** (use for reasoning; communicate outcomes in plain language):

`client_id` | `psn` | `uid` | `psnstatus`

**Client-facing terminology:**

| Internal Term | Client-Facing Alternative |
|---|---|
| psn | (omit — internal depository reference) |
| uid | (omit — internal transaction ID) |
| psnstatus | (omit — internal depository status) |


### A3 — Pledge Types

| Value | Meaning |
|---|---|
| Pledge | New pledge request |
| Unpledge | Release existing pledge |
| Re-pledge | Re-pledging previously unpledged shares |


### A4 — Status Values

| Status | Meaning |
|---|---|
| Success | Request processed by CDSL — collateral margin should be reflected |
| Failure | Request rejected — security not approved, insufficient qty, or CDSL rejection |
| Pending | Awaiting CDSL confirmation — usually resolves within 30 minutes |


### A5 — Common Failure Reasons

| Reason | Explanation |
|---|---|
| Security not approved | Not in approved pledge list — may show "Something went wrong" or specific error |
| T1 holdings | Shares bought today (T1) — not yet settled, cannot pledge until T+1 |
| Insufficient qty | Trying to pledge more qty than available free holdings |
| Margin utilized (unpledge) | Unpledge rejected because collateral margin already used against open positions |
| Overdue | CDSL confirmation delayed — request stuck in pending/overdue state |
| Same-day pledge | Securities pledged today cannot be unpledged on the same day. The pledge is processed on the same day and collateral is credited within 15 minutes. An unpledge request can only be submitted from the next working day onwards. The client can sell the pledged shares on the same day, provided the collateral is not being utilised. |
| F&O segment not active | Pledging requires the F&O segment to be enabled on the client's account. Error message may show as "Pledge is not allowed for your account" or similar account-level restriction. |


### A6 — Cross-Reference Tools

| Tool | When to Use |
|---|---|
| `console_eq_holdings` | Verify available qty for pledging. Pledged qty visible in holdings. |
| `console_eq_pseudo_holdings` | If holdings qty mismatch suspected, cross-check SOT data. |
| `console_mtf_holdings` | Cross-reference if client is confused about auto-pledge entries from MTF. |
| Account Modification tool | Check segment activation status when pledge fails with account-level restriction. |


### A7 — Escalation Data Template

When escalating, always include: **client ID, tradingsymbol, pledge_type, status, pledge_date, and specific issue.**


---

### Preflight (run on every query)

```
1. Identify the tradingsymbol and pledge_type the client is asking about.
2. Look up matching records by Client ID.
```

### Route

```
Intent / Condition                                          → Rule
──────────────────────────────────────────────────────────────────────
LAS / loan against securities query                         → Respond per A8-R15. Out of scope.
  (client mentions "loan," "LAS," "loan against
  securities," or "capital support")

Pledge / unpledge status check                              → Rule 1
Collateral not reflecting after successful pledge           → Rule 2
Pledge failed — diagnose reason                             → Rule 3
Unpledge rejected — margin utilized                         → Rule 4
Overdue / stuck pledge request                              → Rule 5
Holdings showing zero after pledge                          → Rule 6
Unexpected pledge entries (MTF auto-pledge confusion)       → Rule 7
Pledged today, cannot unpledge                              → Rule 8
```

### Scope

- Address the client's query about pledge/unpledge requests, collateral margin, and failure diagnosis.
- LAS (Loan Against Securities) queries are outside scope — route to capitalsupport@zerodha.com (per **A8-R15**).

### Fallback

If no route matches, cross-reference with **A6** tools for additional context. If no root cause is found, escalate per **A7**.


---

### Rule 1 — Pledge / Unpledge Status Verification

1. Find matching tradingsymbol and pledge_type.
2. Your [pledge_type] request for [quantity] shares of [tradingsymbol] placed on [pledge_date]: Status — [status]. + the applicable status template:
   a. Success → append **A8-R2**.
   b. Failure → route to **Rule 3** for diagnosis.
   c. Pending → append **A8-R3**.


### Rule 2 — Collateral Not Reflecting After Successful Pledge

1. If pledge was within last 30 minutes → Collateral margin can take up to 30 minutes to reflect after a successful pledge. Please check again shortly..
2. If more than 30 minutes since `pledge_creation` and still no collateral → escalate per **A7**.


### Rule 3 — Pledge Failed (Diagnose Reason)

1. Check against common failure reasons (per **A5**):
   a. "Something went wrong" error → likely unapproved security. The security may not be in the approved pledge list. Only securities approved for margin are eligible for pledging.
   b. T1 shares → shares purchased today are not yet settled (T+1). Client can pledge them from tomorrow.
   c. Insufficient qty → check `console_eq_holdings` (per **A6**) for available qty. Share the available qty. If the client is trying to pledge more than the available free shares, the request will fail.
   d. "Pledge is not allowed for your account" or similar account-level restriction → check the client's segment activation status using the Account Modification tool (per **A6**). If F&O is not enabled → Pledging requires the F&O segment to be active on the account. To activate F&O, upload valid income proof on Console. Once activated, pledging will be available.
2. If none of the above explains the failure → escalate per **A7** directly. Do not share a generic response.


### Rule 4 — Unpledge Rejected (Margin Utilized)

1. `pledge_type` = Unpledge AND status = Failure AND client mentions "margin already utilized."
2. Your unpledge request for [tradingsymbol] was rejected because the collateral margin from these pledged shares is currently being used against your open positions. To unpledge, you would need to either close the positions using this margin or add equivalent funds/margin from another source first..


### Rule 5 — Overdue Pledge Request

1. Check status and `pledge_creation` timestamp:
   a. Pending/overdue < 30 mins → Your request is being processed. Please wait up to 30 minutes for confirmation..
   b. Pending/overdue > 30 mins but < 24 hours → Your pledge request is most likely going to fail as it has been pending for too long. We recommend placing a fresh pledge request on the next trading day, or you can try pledging a different approved security in the meantime..
   c. Pending/overdue > 24 hours → escalate per **A7**.


### Rule 6 — Holdings Showing Zero After Pledge

1. Pledged shares may not appear in the standard holdings view on Kite. Your shares are safe — they are pledged as collateral. You can verify them on Console where pledged quantities are displayed..
2. Check `console_eq_holdings` (per **A6**) to confirm qty is present.
3. If qty = 0 in Console as well → escalate per **A7** (may be safekeep or DP issue, not pledge-related).


### Rule 7 — MTF Auto-Pledge vs Client Pledge

1. Check `pledge_type` and cross-reference with `console_mtf_holdings` (per **A6**).
2. If you purchased shares under MTF (Margin Trading Facility), those shares are automatically pledged as collateral for the funded amount. These auto-pledge entries are separate from pledges you initiate manually. MTF auto-pledge details are covered under your MTF holdings..


### Rule 8 — Same-Day Unpledge Restriction

1. If the client pledged securities today and is unable to unpledge → Securities pledged on the same day cannot be unpledged. The pledge is processed on the same day and the collateral is credited within 15 minutes, which can be used for trading immediately. However, an unpledge request can only be submitted from the next working day onwards. Please note that you can sell the pledged shares on the same day, provided the collateral is not being utilised against any open positions.. Same-day restriction details per **A5**.
2. Do not suggest alternative workarounds for same-day unpledging. This is a hard restriction.
