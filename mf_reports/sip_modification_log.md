# sip_modification_log

## Description

WHEN TO USE:

When need to:
- Verify when a SIP was paused, resumed, modified, or deleted
- Investigate SIP not triggering — check if modification near trigger date
- Confirm customer did/didn't make SIP changes
- SWP or STP modification verification

REQUIRES: SIP `public_id` from sip_report as input (mapped to `sip_id` here).

TRIGGER KEYWORDS: "modified SIP", "changed SIP date", "paused SIP", "who changed my SIP", "when was SIP cancelled", "coin"

## Protocol

# SIP MODIFICATION LOG PROTOCOL

---

## Section A: Reference Data

All rules reference these blocks as single sources of truth.

### A1 — Tool Purpose & Scope

- Shows historical modifications for a specific SIP/SWP/STP.
- Requires `public_id` from sip_report as input (field here is `sip_id`, same value). This tool cannot be queried without it.
- All modifications are initiated from the client's device (no system pauses except AMC SIP auto-cancel).
- This tool is the only authoritative source for SIP/SWP/STP pause/modify/delete dates.

### A2 — last_sip_at Distinction

`last_sip_at` in sip_report is the date of the last SIP order execution — not the pause, modification, or deletion date. Never use `last_sip_at` as the pause/modify date.

To find when a SIP was paused/modified/deleted → use `modified_at` from this tool only. If this tool shows no modification entries → the SIP was not paused or modified. Do not infer a modification date from any other field (including `last_sip_at` or `next_sip_date`).

### A3 — Type Translations

| Internal Value | Client-Facing Language |
|---|---|
| sip_edit | "Your SIP was modified" |
| sip_delete | "Your SIP was deleted/cancelled" |
| swp_edit | "Your SWP was modified" |
| swp_delete | "Your SWP was deleted/cancelled" |
| stp_edit | "Your STP was modified" |
| stp_delete | "Your STP was deleted/cancelled" |

Never share raw `type` values with the client.

### A4 — Modification Timing Impact

A modification within 1–2 days of the trigger date means the current instalment will not be placed. The SIP/SWP/STP starts from the next cycle date.

### A5 — Field Rules

**Shareable with client (in plain language):** `type` (translated per **A3**), `modified_at` (date of change).

**Internal reasoning only:** `sip_id` (= `public_id` from sip_report).

**Never share with client:** `client_id`, `status` (null), `swp_status` (null), `timestamp`.

### A6 — Cross-Reference Protocols

| Topic | Refer to |
|---|---|
| Get public_id for this tool | sip_report (`public_id` field) |
| SIP-not-triggered sequential diagnostic | sip_report Rule 1 |
| last_sip_at field (order execution date, not modification) | sip_report |

## Section B: Decision Flow

### Preflight (run on every query)

1. **public_id gate (hard block):** Verify `public_id` is available from sip_report before querying this tool. If not available → fetch sip_report first. Do not query this tool without `public_id` — results will be incorrect or empty.
2. Fetch the SIP modification log using `public_id` as `sip_id`.
3. Apply field protection per **A5**.
4. **Date verification:** When reading `modified_at`, verify the full date (day, month, year) carefully before sharing. Common errors include confusing months or years. Double-check before including in the response.
5. Format dates as DD MMM YYYY.

### Routing Tree

```
Query relates to SIP/SWP/STP modification history →
│
├─ Preflight: public_id available?
│  ├─ NO → Fetch sip_report first (STOP)
│  └─ YES → Continue
│
├─ Modification found near trigger date
│  → Rule 1
│
├─ Client claims they didn't modify
│  → Rule 2
│
├─ No modification entries found
│  → Rule 3
│
└─ General modification history query
   → Translate type per A3, share modified_at
```

### Scope

- Address: SIP/SWP/STP modification history, timing impact on instalments, and modification date verification.

### Fallback

If no entries found → report that no modifications were made and route back to sip_report Rule 1 for continued diagnosis.

---

## Section C: Rules

Rules reference Section A blocks. They do not redefine what is already defined there.

### Rule 1 — Modification Near Trigger Date

1. Translate `type` to plain language per **A3**.
2. Respond: "Your [SIP/SWP/STP] was [modified/deleted] on [modified_at], within 1–2 days of the execution date. Your current instalment will not be placed. It will start from the next cycle." (Per **A4**.)

### Rule 2 — Client Claims No Change

1. Respond: "Our records show a change was made to your [SIP/SWP/STP] on [modified_at] from your account. SIP changes can only be made from the Coin app or web." (Per **A1** — all modifications initiated from client's device.)
2. Never expose internal IDs or raw field values.

### Rule 3 — No Modification Found

1. Respond: "Our records show no modifications, pauses, or cancellations were made to this [SIP/SWP/STP]."
2. If investigating SIP-not-triggered → route back to sip_report Rule 1 sequential diagnostic (per **A6**) to continue diagnosis (mandate, order status, etc.).
3. Do not infer a modification from any other field (per **A2**).

