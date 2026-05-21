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

TAGS: margins

## Protocol

# CONSOLE INSTANT PLEDGE PROTOCOL

---

## Section A: Reference Data

### A1 — Fundamentals

- `previous_quantity` shows pledged qty before the transaction — used to track incremental pledges.

- MTF shares are auto-pledged and are separate from client-initiated pledges.

---

### A2 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |
|---|---|
| `pledge_date` | Date the pledge action was processed |
| `tradingsymbol` | Trading symbol of the pledged instrument |
| `isin` | ISIN code of the pledged instrument |
| `status` | Current status of the pledge request |
| `pledge_type` | Type of pledge action (e.g., pledge, unpledge) |
| `quantity` | Current quantity pledged |
| `previous_quantity` | Quantity pledged before the latest change |
| `pledge_creation` | Timestamp when the pledge was originally created |

**Non-shareable:**

| Field | Interpretation |
|---|---|
| `psn` | Internal pledge sequence number |
| `uid` | Internal unique identifier for the pledge record |
| `psnstatus` | Internal pledge sequence status |
| `client_id` | Internal client identifier |

---

### A3 — Pledge Types

| Value | Meaning |
|---|---|
| Pledge | New pledge request |
| Unpledge | Release existing pledge |
| Re-pledge | Re-pledging previously unpledged shares |

---

### A4 — Status Values

| Status | Meaning |
|---|---|
| Success | Request processed by CDSL — collateral margin should be reflected |
| Failure | Request rejected — security not approved, insufficient qty, or CDSL rejection |
| Pending | Awaiting CDSL confirmation — usually resolves within 30 minutes |

---

### A5 — Common Failure Reasons

| Reason | Explanation |
|---|---|
| Security not approved | "Something went wrong" error or a security-specific error |
| T1 holdings | Shares purchased today |
| Insufficient qty | Pledging more than available free holdings |
| Margin utilized (unpledge) | Unpledge on shares whose collateral is in use |
| Overdue | CDSL confirmation delayed — request stuck in pending/overdue state |
| Same-day unpledge | Securities pledged today cannot be unpledged on the same day. The pledge is processed on the same day and collateral is credited within 15 minutes. An unpledge request can only be submitted from the next working day onwards. The client can sell the pledged shares on the same day, provided the collateral is not being utilised. |
| F&O segment not active — request pending | "Pledge is not allowed for your account" or similar; activation request already found in `account_modification` |
| F&O segment not active — no request placed | "Pledge is not allowed for your account" or similar; no activation request found in `account_modification` |

---

### A6 — Escalation Data

- **When escalating to a human agent, provide:** client ID, tradingsymbol, pledge_type, status, pledge_date, specific issue.

---

### A7 — Scenarios

| Scenario | Meaning / Interpretation |
|---|---|
| Collateral not reflecting within 30 mins of pledge | Normal delay — collateral margin can take up to 30 minutes to reflect after a successful pledge |
| Pledge failure: unapproved security | Security may not be in the approved pledge list — only securities approved for margin are eligible |
| Pledge failure: T1 shares | Shares purchased today are not yet settled (T+1) — cannot be pledged until the next trading day |
| Pledge failure: insufficient qty | Client is attempting to pledge more than the available free quantity |
| Unpledge rejected: margin utilized | Collateral margin from pledged shares is currently in use against open positions — cannot unpledge until positions are closed or equivalent margin is available from another source |
| Overdue < 30 mins | Request is still being processed — within normal window |
| Overdue > 30 mins, < 24 hours | Request has been pending too long and is likely to fail — client should retry on next trading day or pledge a different approved security |
| Holdings showing zero after pledge | Pledged shares do not appear in standard holdings view — shares are safe and pledged as collateral; visible on Console |
| MTF auto-pledge | Shares purchased under MTF are automatically pledged as collateral — these are separate from client-initiated pledges |
| F&O segment not active — request pending | F&O activation request is already in progress — client should wait for it to be processed |
| F&O segment not active — no request placed | F&O segment must be active for pledging — client needs to activate F&O via income proof upload on Console |

---

## Section B: Decision Flow

### Routing

```
Route by scenario
├─ LAS / loan against securities query (mentions "loan", "LAS", "capital support") → Rule 1
├─ Pledge / unpledge status check → Rule 2
├─ Collateral not reflecting after successful pledge → Rule 3
├─ Pledge failed — diagnose reason → Rule 4
├─ Unpledge rejected — margin utilized → Rule 5
├─ Overdue / stuck pledge request → Rule 6
├─ Holdings showing zero after pledge → Rule 7
├─ Unexpected pledge entries (MTF auto-pledge confusion) → Rule 8
└─ Pledged today, cannot unpledge → Rule 9
```

### Fallback

- If no route matches, escalate to human agent per A6.

---

## Section C: Rules

### Rule 1 — LAS Early Exit

1. If client mentions "loan", "LAS", "loan against securities", or "capital support" → direct to `capitalsupport@zerodha.com`.
2. No further tool query needed.

---

### Rule 2 — Pledge / Unpledge Status Verification

1. Find the matching tradingsymbol and pledge_type.
2. Apply A4 by status:
   - Success → per A4.
   - Failure → route to Rule 4 for diagnosis.
   - Pending → per A4.

---

### Rule 3 — Collateral Not Reflecting After Successful Pledge

1. If pledge was within the last 30 minutes → per A7.
2. If more than 30 minutes since `pledge_creation` and still no collateral → escalate to human agent per A6.

---

### Rule 4 — Pledge Failed (Diagnose Reason)

1. Identify failure reason per A5 and apply per A7:
   - "Something went wrong" error → unapproved security.
   - T1 shares.
   - Insufficient qty → invoke `console_eq_holdings` for available qty.
   - "Pledge is not allowed for your account" or similar account-level restriction → check Segments in `get_all_client_data`. If F&O is not active → invoke `account_modification` to check if an activation request is already placed:
     - Request found → per A7: F&O segment not active — request pending.
     - No request found → per A7: F&O segment not active — no request placed.
2. If none of the above explains the failure → escalate to human agent per A6.

---

### Rule 5 — Unpledge Rejected (Margin Utilized)

- `pledge_type` = Unpledge AND status = Failure AND margin is in use → per A7.

---

### Rule 6 — Overdue Pledge Request

1. Check status and `pledge_creation` timestamp and apply per A7.
2. If overdue > 24 hours → escalate to human agent per A6.

---

### Rule 7 — Holdings Showing Zero After Pledge

1. Apply per A7.
2. Invoke `console_eq_holdings` to confirm qty is present.
3. If holdings qty mismatch suspected → invoke `console_eq_pseudo_holdings` to cross-check SOT data.
4. If qty = 0 in Console as well → escalate to human agent per A6.

---

### Rule 8 — MTF Auto-Pledge vs Client Pledge

1. Check `pledge_type` and invoke `console_mtf_holdings` to cross-reference.
2. Apply per A7.

---

### Rule 9 — Same-Day Unpledge Restriction

1. Client pledged securities today and cannot unpledge → refer to A5: Same-day unpledge.
2. Do not suggest alternative workarounds for same-day unpledging.
