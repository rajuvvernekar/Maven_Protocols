# console_eq_external_trades

## Description

WHEN TO USE:

When clients:
- Have discrepancy in holdings and need to verify if a manual entry was posted
- Report they added discrepancy details but buy average still not updated
- Report wrong price/qty entered in discrepancy fix and want correction
- Report holdings show discrepant qty and need to trace the source (transfer, gift, ESOP, IPO, CA credit)
- Need verification of buyback, IPO allotment, or gift entries in the system
- Need to check if a reversal or exit entry was posted for transferred-out shares
- Need to check if external trade entries (discrepant, buyback, IPO, gift, ESOP, internal transfer, off-market) exist for a stock

TRIGGER KEYWORDS: "external trade", "discrepancy entry", "discrepant entry", "add trade", "fix discrepancy", "buyback entry", "IPO entry", "gift entry", "ESOP entry", "internal transfer entry", "off-market entry", "wrong discrepancy price", "wrong entry", "pending recalc", "external trade type"

## Protocol

#CONSOLE EQ EXTERNAL TRADES PROTOCOL

--

## Section A: Reference Data

---

### A1 — Tool Purpose & Fundamentals

This tool looks up external trade entries for a client. External trades are entries recorded outside normal exchange trading (manual or system-generated). They directly affect buy average and P&L via FIFO. Missing external trade entries are a primary cause of holdings and P&L discrepancies.

**Input:** Client ID + External Trade Type filter (discrepant, buyback, internal transfer, IPO, etc.)

---

### A2 — Field Usage Rules

**Shareable fields** (share when relevant):

`trade_date` | `tradingsymbol` | `isin` | `quantity` | `price` | `trade_type` | `external_trade_type` | `exchange` | `series` | `order_execution_time`

**Internal-only fields** (use for reasoning; communicate outcomes in plain language):

`pk` | `instrument_id` | `client_id` | `settlement_type` | `creation` | `pending_recalc`

`pending_recalc` is an internal processing flag — use it to diagnose recalculation state. Communicate the outcome to the client (e.g., "your entry is being processed") rather than the field name.

---

### A3 — External Trade Types & Client-Friendly Labels

| Raw `external_trade_type` | Client-Facing Label | Description |
|---|---|---|
| discrepant | manual entry | Client-added entry for transferred/gifted/ESOP/off-market shares with no matching tradebook record |
| buyback | buyback entry | System-posted SELL entry for accepted buyback quantities — `trade_type` always SELL, `order_id` = BUYBACK |
| devolved | physical settlement | System-posted BUY entry for shares received under physical delivery settlement — `exchange` = PHY, `series` = AF |
| ipo | IPO allotment | Entry for IPO allotment shares credited to demat — `tradingsymbol` may be temporary until listing, `exchange` may be UNKNOWN |
| internal_transfer | account transfer | Entry for shares moved between client's own demat accounts (primary ↔ secondary) |
| gift | gift transfer | Entry for shares received or sent as gift; entry price = closing price on transfer date by default |
| esop | ESOP entry | Entry for ESOP exercised shares; client enters exercise price |
| ofs | OFS allotment | Entry for trades related to Offer for Sale (OFS) transactions |
| reversal | short delivery reversal | System-posted reversal trade against short deliveries |
| rightsissue | rights allotment | Entry for shares allotted under a rights issue |
| takeover | open offer/takeover | Entry for shares tendered or received under an open offer/takeover |
| transferout | transfer out | System-posted gift-out and transfer-out entries when client provides transfer details via ticket or call |

Always translate the raw `external_trade_type` value to the client-facing label when communicating with the client.

---

### A4 — Cross-Reference Tools

| Tool | When to Use |
|---|---|
| `console_eq_holdings` | Check `discrepant` field — if > 0, external entry may be missing or pending. Discrepancy resolution steps are in that tool's protocol (Rule 5). |
| `console_eq_tradebook` | Regular exchange-executed trades. If trade not found there, check external trades. |
| `console_eq_holdings_breakdown` | Transaction-level view showing both tradebook and external entries combined. Use to verify if an external entry is reflected in the breakdown. |
| `console_eq_pnl` | P&L computed from all trades (tradebook + external). Missing external entries cause wrong P&L. |

---

### A5 — Key Timelines

| Event | Expected Timeline |
|---|---|
| `pending_recalc` = true → holdings/P&L update | Up to 24 hours |
| IPO allotment entry posting | Up to 3 trading days from listing date |
| Buyback entry posting | Posted on the day the "Net settlement for buyback with settlement number" entry appears in `ledger_report`; escalate if >5 trading days after confirmed acceptance |

---

### A6 — Discrepancy Self-Resolution Path

Clients add missing entries via: **Console → Portfolio → Holdings → View discrepancy → Add trade**

Once added and processed (`pending_recalc` = false), entries are locked and cannot be edited by the client. Wrong entries can only be corrected by the Console team (backend fix).

---

### A7 — Entry Price Defaults

| Share Source | Default Entry Price | Notes |
|---|---|---|
| Gift shares | Closing price on transfer date | Client may want actual acquisition cost instead; requires backend correction |
| ESOP shares | Exercise price (client-entered) | If ISIN not listed on exchange, entry cannot be added until listed |

---

### A8 — Escalation Data Template

When escalating, always include: **client ID, tradingsymbol, ISIN, specific issue description, and current entry details (if applicable).**

For wrong-entry corrections, also include: the correct values the client wants.

For gift price corrections, also include: the requested price.

---

### A9 — Response Templates

**R1 — Entry found (generic):**
Share: `trade_date`, `tradingsymbol`, `quantity`, `price`, `trade_type`. Use the client-facing label from **A3** instead of the raw `external_trade_type`.

**R2 — No entry found (generic):**
"No [client-facing label] entry exists for [tradingsymbol] in your account. This may be why the shares are showing as discrepant or the buy average is not available."

**R3 — Pending recalculation:**
"Your entry for [tradingsymbol] has been recorded and is being processed. The buy average will update within 24 hours."

**R4 — Locked entry (wrong details):**
"Once a discrepancy entry is processed, it cannot be edited from your end. We'll need to correct this on the backend."

**R5 — Gift shares price explanation:**
"Your gift shares of [tradingsymbol] were recorded at ₹[price] per share, which is the closing price on the transfer date ([trade_date]). This is the default entry price used for P&L tracking."

**R6 — Gift shares price change request:**
"The default price for gifted shares is the closing price on transfer date. If you need this updated to reflect the original acquisition cost for tax purposes, we can request a backend correction."

**R7 — ESOP not listed:**
"Your ESOP shares ([tradingsymbol]) are not yet listed on the exchange. Discrepancy entries can only be added once the ISIN is active on NSE or BSE. Please try again after the stock is listed."

**R8 — Buyback entry found:**
"Your [quantity] shares of [tradingsymbol] were tendered in the buyback at ₹[price] per share on [trade_date]. The buyback proceeds will be credited to your primary bank account by the company."

**R9 — Buyback entry not found:**
"The buyback entry has not been posted yet. Buyback entries are posted on the day the 'Net settlement for buyback with settlement number' entry appears in your ledger, after the company processes and confirms acceptance. If the buyback acceptance was confirmed more than 5 trading days ago, we'll investigate further."

**R10 — IPO entry found, avg pending:**
"Your IPO allotment of [quantity] shares of [tradingsymbol] at ₹[price] has been recorded. If the buy average still shows N/A, the entry may be pending processing (up to 24 hours)."

**R11 — IPO entry not found, within 3 days:**
"IPO allotment entries take up to 3 days to be posted in the system. Please check back after 3 trading days from the listing date."

**R12 — Internal transfer not found:**
"The transfer entry between your accounts has not been posted yet. We'll raise this for investigation."

**R13 — P&L wrong, missing external entry:**
"The P&L for [tradingsymbol] appears incorrect because there is no purchase entry in the system for the [discrepant] shares you hold. P&L is calculated using FIFO from all available trade entries. Without a buy entry, the system cannot compute the correct cost of acquisition.

To fix this, you need to add the purchase details via Console → Portfolio → Holdings → View discrepancy → Add trade. Once the entry is processed, the P&L will recalculate automatically."

---

**Escalation behavior:** When any rule in this protocol says **ESCALATE**, do not draft a customer-facing response. Instead, output only: **HUMAN AGENT ACTION REQUIRED** — followed by the reason from the rule. The human agent will handle the query manually.

## Section B: Decision Flow

---

### Preflight (run on every query)

```
1. Identify the stock (tradingsymbol / ISIN) and the client's concern
   (missing entry, wrong avg, wrong P&L, buyback status, etc.)

2. Determine the relevant external_trade_type to filter on
   └─ If unclear, check the client's description against A3 definitions

3. Look up entries using Client ID + external_trade_type filter
```

### Route

```
Intent / Condition                                            → Rule
──────────────────────────────────────────────────────────────────────
Verify if an external entry exists for a stock                → Rule 1
Entry added but buy average still wrong / N/A                 → Rule 2
Client entered wrong details in discrepancy fix               → Rule 3
Gift shares — price query or price change request             → Rule 4
ESOP shares — error adding discrepancy entry                  → Rule 5
Buyback — share status or entry verification                  → Rule 6
IPO allotment — shares discrepant, check entry                → Rule 7
Internal transfer — entry missing or wrong                    → Rule 8
No external entries but shares show discrepant                → Rule 9
P&L wrong, suspected missing external entry                   → Rule 10
```

### Scope

- Address the client's query about external trade entries and their impact on holdings/P&L.
- Translate raw field values to client-friendly language (per **A3**).
- Do not volunteer information about other external trade types unless relevant to the query.

### Fallback

If no route matches, use **A4** to cross-reference other tools (`console_eq_holdings`, `console_eq_tradebook`, `console_eq_holdings_breakdown`, `console_eq_pnl`) for additional context. If no root cause is found, **ESCALATE** per **A8**.

---

## Section C: Rules

---

### Rule 1 — Verify External Entry Exists

1. Filter by Client ID and appropriate `external_trade_type`.
2. If entry found → respond per **A9-R1** (share trade details, use client-facing label from **A3**).
3. If no entry found → respond per **A9-R2**.

---

### Rule 2 — Entry Added but Buy Average Not Updated

1. Check `pending_recalc` (internal use only per **A2**).
2. If `pending_recalc` = true → respond per **A9-R3**. Timeline per **A5**.
3. If `pending_recalc` = false AND buy average still wrong in `console_eq_holdings`:
   a. Verify the entry details (price, qty, date) are correct.
   b. If entry looks correct but average is still wrong → **ESCALATE** per **A8**.

---

### Rule 3 — Wrong Entry (Client Mistake)

1. Respond per **A9-R4**.
2. Entry is locked after processing (per **A6**).
3. **ESCALATE** per **A8** — include current wrong entry details from this tool and the correct values the client wants.

---

### Rule 4 — Gift Shares Entry Price

1. Filter by `external_trade_type` = gift.
2. If entry exists:
   a. Check `exchange` field: if `exchange` = "NSE", the entry was added by Zerodha (system-generated).
   b. If the client has also made a separate discrepant entry for the same stock → escalate (possible duplicate entries causing wrong buy average).
   c. Respond per **A9-R5**. Default price per **A7**.
3. If client wants actual acquisition cost instead → respond per **A9-R6**. **ESCALATE** per **A8** with requested price.

---

### Rule 5 — ESOP Shares (Cannot Add Entry)

**ESCALATE** — agent review needed.

---

### Rule 6 — Buyback Entry Verification

1. Filter by `external_trade_type` = buyback.
2. If sell entry found → respond per **A9-R8**.
3. If no entry found → respond per **A9-R9**. Timeline per **A5**.
4. Escalate if client confirms acceptance was completed and no entry exists after 5 trading days.

---

### Rule 7 — IPO Allotment Entry

1. Filter by `external_trade_type` = ipo.
2. If entry found → respond per **A9-R10**. Recalculation timeline per **A5**.
3. If no entry found AND IPO was within last 3 days → respond per **A9-R11**. Timeline per **A5**.
4. If no entry found AND IPO was more than 3 days ago → **ESCALATE** per **A8**.

---

### Rule 8 — Internal Transfer Entry

1. Filter by `external_trade_type` = internal_transfer.
2. If entry found → share details per **A9-R1**.
3. If no entry found → respond per **A9-R12**. **ESCALATE** per **A8**.

---

### Rule 9 — No External Entries but Shares Show Discrepant

1. Client needs to add the entry manually — direct them to the self-resolution path in **A6**.
2. If the shares were credited via corporate action (convertible debenture, rearrangement, unclaimed shares) and the source is not obvious to the client → **ESCALATE** per **A8** for Console team to investigate and post the correct entry.

---

### Rule 10 — P&L Wrong Due to Missing External Entry

1. Respond per **A9-R13** — explain FIFO dependency and direct client to self-resolution path in **A6**.

---

## Section D: General Notes

- Buyback entries have `trade_type` always SELL and `order_id` = BUYBACK.
- Devolved entries have `exchange` = PHY and `series` = AF.
- IPO entries may have a temporary `tradingsymbol` until listing and `exchange` may be UNKNOWN.
- For gift entries where `exchange` = "NSE", the entry was system-generated by Zerodha (not client-added).
- `transferout` entries are system-posted when the client provides transfer details via ticket or call.
