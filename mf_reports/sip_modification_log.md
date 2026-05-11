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

TAGS: investments

## Protocol

# SIP MODIFICATION LOG PROTOCOL

## Section A: Reference Data

### A1 — Fundamentals

- Requires `public_id` from sip_report as input (field here is `sip_id`, same value). If not available → invoke ‘sip_report’ first.
- All modifications are initiated from the client's device (no system pauses except AMC SIP auto-cancel).

### A2 — last_sip_at Distinction

`last_sip_at` in ‘sip_report’ is the date of the last SIP order execution — not the pause, modification, or deletion date. Never use `last_sip_at` as the pause/modify date.

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

### A4 — Modification Timing Impact

A modification within 1–2 days of the trigger date means the current instalment will not be placed. The SIP/SWP/STP starts from the next cycle date.

### A5 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |
|---|---|
| `type` | Translated per **A3** |
| `modified_at` | Date of change |

**Non-shareable:**

| Field | Interpretation |
|---|---|
| `sip_id` | Internal — same value as `public_id` from ‘sip_report’ |
| `client_id` | Internal client identifier |
| `status` | Always empty |
| `swp_status` | Always empty |
| `timestamp` | Internal |

## Section B: Decision Flow

### Routing

```
Route by scenario
   ├─ Instalment skipped, modification entry present near trigger date → Rule 1
   ├─ Client claims they didn't modify → Rule 2
   └─ Instalment skipped, no modification entries found → Rule 3
```

### Fallback

If no root cause found after completing all diagnostic steps → escalate to human agent.

## Section C: Rules

### Rule 1 — Modification Near Trigger Date

1. Translate `type` to plain language per **A3**.
2. Communicate the timing impact per **A4**.

### Rule 2 — Client Claims No Change

1. Records show a change was made on `modified_at` from the client's account. SIP changes can only be made from the Coin app or web per **A1**.

### Rule 3 — No Modification Found

1. Records show no modifications, pauses, or cancellations.
2. If investigating SIP-not-triggered → invoke ‘sip_report’ to continue diagnosis.
