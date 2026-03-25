# mandate_report

## Description

WHEN TO USE:

When clients:
- Ask about mandate status (created/pending/active/failed/cancelled)
- Report mandate not activating or stuck
- Ask about mandate activation timeline
- Ask which bank mandate is linked to

TRIGGER KEYWORDS: "mandate status", "mandate pending", "mandate failed", "eNACH", "autopay setup", "coin"

## Protocol

# MANDATE REPORT PROTOCOL

---

## Section A: Reference Data

All rules reference these blocks as single sources of truth.

### A1 — Tool Purpose & Scope

- This report shows all MF/Coin mandates with current status.
- This report is for MF/Coin mandates only. Console/equity mandates are a separate report and not interchangeable. If a client asks about a mandate for SIP/Coin, always use this tool — not Console eMandate.
- `mandate_id` prefix identifies type: `ZERODHA*` = UPI autopay; `ENA*` = Digio eNACH.
- Mandate must be linked to SIP for auto-debit to work.
- To delete a mandate: unlink all active/paused SIPs first (see Mandate Debit Report protocol — A5 for full deletion process).

### A2 — Mandate Type Comparison

| Feature | UPI Autopay (`ZERODHA*`) | eNACH (`ENA*`) |
|---|---|---|
| Activation time | Within 2 minutes of UPI PIN confirmation | Up to 3 working days (may take up to 5) |
| Activation requirement | Client must complete UPI PIN confirmation | Bank approval |
| If not activated | Auto-cancelled by 11 PM same day if PIN not completed | Pending until bank approves or rejects |
| Escalation | — | If pending > 5 working days → escalate |

### A3 — Tool Routing

| Client Asks About | Use This Tool | Do NOT Use |
|---|---|---|
| Mandate for SIP, Coin, or mutual fund | **This tool** (MF Mandate Report) | Console eMandate report |
| Mandate for equity, F&O, or Console trading | Console eMandate report | This tool |
| Unclear context | Default to this tool; verify using `mandate_id` prefix | — |

Prefix identification: `ZERODHA*` or `ENA*` = Coin/MF mandate. Other prefixes = Console mandate.

### A4 — Status Translations

| Internal Status | Meaning | Client-Facing Communication |
|---|---|---|
| created | Creation initiated, pending verification | See Rule 1 for type-specific guidance |
| pending | Awaiting bank approval | See Rule 1 for type-specific guidance |
| success | Active — ready for auto-debit | "Your mandate is active." |
| register_success | Registered at bank | "Your mandate is active." |
| failed | Creation/registration failed | "Your mandate registration failed. Please create a new one." |
| register_failed | Registration failed at bank | "Your mandate registration failed. Please create a new one." |
| pending_cancellation | Cancellation in progress | "Your mandate cancellation is being processed." |
| waiting_confirm_cancellation | Awaiting bank cancellation confirmation | "Your mandate cancellation is awaiting bank confirmation." |
| cancelled | Cancelled | "Your mandate has been cancelled." |
| paused | Paused | "Your mandate is paused." |

### A5 — NRI Account Mandate Rules

- Mandate setup restrictions apply to NRI PIS accounts only (NRE PIS).
- NRO Non-PIS account holders can set up mandates for SIPs. Do not inform NRO Non-PIS clients that they cannot set up a mandate.

### A6 — Field Rules

**Shareable with client:** `status` (translated per **A4** — use friendly phrases only), `time_created`.

**Internal reasoning only (use for analysis, not client language):** `mandate_id` (type identification: ZERODHA*/ENA*), `time_updated`, `bank_name`.

Suppress (no client use, only internal reasoning use): client_id, umrn, merchant_name, bank_account_number, bank_ifsc_code, verification_date, cancellation_date.
### A7 — Cross-Reference Protocols

| Topic | Refer to |
|---|---|
| SIP mandate linkage (fund_source check) | sip_report |
| Debit attempts and status | mandate_debit_report |
| Mandate deletion process (unlink SIPs first) | Mandate Debit Report protocol — A5 |

---

**Escalation behavior:** When any rule in this protocol says **ESCALATE**, do not draft a customer-facing response. Instead, output only: **HUMAN AGENT ACTION REQUIRED** — followed by the reason from the rule. The human agent will handle the query manually.

## Section B: Decision Flow

### Preflight (run on every query)

1. **Tool routing check:** Determine if this is an MF/Coin mandate or Console/equity mandate per **A3**. If Console/equity → route to Console eMandate report.
2. Fetch the mandate report for the client.
3. Apply field protection per **A6** — identify shareable, internal, and banned fields.
4. Identify mandate type from `mandate_id` prefix per **A1**.
5. Translate status per **A4**.

### Routing Tree

```
Query relates to MF/Coin mandate →
│
├─ Preflight: Is this an MF/Coin or Console/equity mandate?
│  ├─ Console/equity → Route to Console eMandate report (STOP)
│  └─ MF/Coin → Continue
│
├─ Client asks when mandate activates / activation status
│  → Rule 1
│
├─ Mandate active but SIP not debiting
│  → Rule 2
│
└─ General mandate status query
   → Translate status per A4, respond
```

### Scope

- Address: MF/Coin mandate status, activation timelines, and SIP linkage issues.
- Not part of client-facing responses: internal field values (per **A6**), mandate IDs, bank account details, or information the client hasn't asked about.

### Fallback

If mandate status doesn't match any expected value or activation is stuck beyond expected timelines → escalate with mandate type, time_created, and current status.

---

## Section C: Rules

Rules reference Section A blocks. They do not redefine what is already defined there.

### Rule 1 — Activation Status

1. Check `status` and identify mandate type from `mandate_id` prefix (per **A2**).

**Created/Pending + eNACH (`ENA*`):**
"Your eNACH mandate was created on [time_created]. eNACH activation takes up to 3 working days."
If pending > 5 working days → escalate.

**Created/Pending + UPI (`ZERODHA*`):**
Check `time_created`:
- Created within last 2 minutes: "Your UPI mandate is being activated. Please wait a moment and check again."
- Created more than 2 minutes ago: "UPI mandate activation requires completing the UPI PIN confirmation. If you did not complete the PIN step, the mandate will be auto-cancelled by 11 PM today. Please create a new mandate and ensure you complete the UPI PIN confirmation to activate it." (Per **A2**.)

**Success / Register_success:**
"Your mandate is active." (Per **A4**.)

**Failed / Register_failed:**
"Your mandate registration failed. Please create a new one. Try UPI autopay for faster activation — it activates within 2 minutes of PIN confirmation." (Per **A2**.)

### Rule 2 — Active Mandate But SIP Not Debiting

1. Confirm: mandate status = success or register_success.
2. Check sip_report (per **A7**) for `fund_source` on the affected SIP:
   - `fund_source` = blank or pool → mandate is not linked to the SIP. "Your mandate is active but not linked to your SIP. Please link it on Coin."
   - `fund_source` = digio-mandates or upi-mandates → mandate is linked. Check mandate_debit_report (per **A7**) for debit attempt status.

---

## Section D: General Notes

1. MF/Coin mandates and Console/equity mandates are completely separate systems. The most common routing error is using Console eMandate for SIP queries or vice versa. Always verify context per **A3** before proceeding.
2. UPI mandates that are not PIN-confirmed are auto-cancelled by 11 PM the same day. If a client reports their mandate disappeared, this is the most likely cause — advise creating a new one and completing PIN confirmation.
3. NRI mandate restrictions apply only to NRI PIS (NRE) accounts. NRO Non-PIS clients can set up mandates normally — do not restrict them (per **A5**).
