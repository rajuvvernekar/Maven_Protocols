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

TAGS: holdings, demat

## Protocol

# CONSOLE EQ EXTERNAL TRADES PROTOCOL

---

## Section A: Reference Data

### A1 — Fundamentals

- External trades directly affect buy average and P&L via FIFO.

---

### A2 — Field Usage Rules

**Shareable with client:**

| Field | Interpretation |
|---|---|
| `trade_date` | Date on which the trade was executed/purchased |
| `tradingsymbol` | Exchange trading symbol of the instrument |
| `isin` | ISIN code of the instrument |
| `quantity` | Number of shares in the entry |
| `price` | Entry price per share |
| `trade_type` | Buy or Sell |
| `order_execution_time` | Timestamp of the entry |

**Non-shareable:**

| Field | Interpretation |
|---|---|
| `pk` | Internal primary key identifier |
| `instrument_id` | Internal instrument mapping identifier |
| `client_id` | Internal client identifier |
| `settlement_type` | Internal settlement classification |
| `creation` | Internal record creation timestamp |
| `pending_recalc` | true = holdings/P&L recalculation still in progress; false = processed |
| `external_trade_type` | Category of external trade — use client-facing label from A3, not the raw value |
| `exchange` | Exchange associated with the entry (PHY for devolved; UNKNOWN for some IPO entries) |
| `series` | Series of the instrument (AF for devolved entries) |

---

### A3 — External Trade Types and Client-Facing Labels

| Raw `external_trade_type` | Client-Facing Label | Description |
|---|---|---|
| `discrepant` | manual entry | Client-added entry for transferred / gifted / ESOP / off-market shares with no matching tradebook record |
| `buyback` | buyback entry | System-posted SELL entry for accepted buyback quantities — `trade_type` always SELL; `order_id` = BUYBACK |
| `devolved` | physical settlement | System-posted BUY entry for shares received under physical delivery settlement — `exchange` = PHY; `series` = AF |
| `ipo` | IPO allotment | Entry for IPO allotment shares credited to demat — `tradingsymbol` may be temporary until listing; `exchange` may be UNKNOWN |
| `internal_transfer` | account transfer | Entry for shares moved between client's own demat accounts (primary ↔ secondary) |
| `gift` | gift transfer | Entry for shares received or sent as gift; entry price = closing price on transfer date by default |
| `esop` | ESOP entry | Entry for ESOP exercised shares; client enters the exercise price |
| `ofs` | OFS allotment | Entry for shares allotted under an Offer for Sale (OFS) transaction |
| `reversal` | short delivery reversal | System-posted reversal trade against short deliveries |
| `rightsissue` | rights allotment | Entry for shares allotted under a rights issue |
| `takeover` | open offer / takeover | Entry for shares tendered or received under an open offer or takeover |
| `transferout` | transfer out | System-posted gift-out and transfer-out entries when client provides transfer details via ticket or call |

---

### A4 — Key Timelines

| Event | Expected Timeline |
|---|---|
| `pending_recalc` = true → holdings / P&L update | Up to 24 hours |
| IPO allotment entry posting | Up to 3 trading days from listing date |
| Buyback entry posting | Posted on the day the "Net settlement for buyback with settlement number" entry appears in `ledger_report`; escalate to human agent if > 5 trading days after confirmed acceptance |

---

### A5 — Discrepancy Self-Resolution Path

- Clients add missing entries via: **Console → Portfolio → Holdings → View discrepancy → Add trade**

- Once added and processed (`pending_recalc` = false), entries are locked and cannot be edited by the client. Wrong entries can only be corrected by the Console team via backend fix.

---

### A6 — Entry Price Defaults and Constraints

| Share Source | Default Entry Price | Constraint |
|---|---|---|
| Gift shares | Closing price on transfer date | Client may want actual acquisition cost instead; requires backend correction |
| ESOP shares | Exercise price (client-entered) | If ISIN not yet listed on exchange, entry cannot be added until the stock is listed |

---

### A7 — Escalation Data

- Include when escalating to human agent: client ID, `tradingsymbol`, ISIN, specific issue description, and current entry details (if applicable).

---

## Section B: Decision Flow

### Routing

```
Route by scenario
   ├─ Verify if an external entry exists for a stock              → Rule 1
   ├─ Entry added but buy average still wrong / N/A               → Rule 2
   ├─ Client entered wrong details in discrepancy entry           → Rule 3
   ├─ Gift shares — price query or price change request           → Rule 4
   ├─ ESOP shares — error adding entry                            → Rule 5
   ├─ Buyback — share status or entry verification                → Rule 6
   ├─ IPO allotment — shares discrepant, check entry              → Rule 7
   ├─ Internal transfer — entry missing or wrong                  → Rule 8
   ├─ No external entries but shares show discrepant              → Rule 9
   ├─ P&L wrong, suspected missing external entry                 → Rule 10
   ├─ Devolved / physical settlement entry                        → Rule 11
   ├─ OFS allotment entry                                         → Rule 12
   ├─ Short delivery reversal entry                               → Rule 13
   ├─ Rights issue allotment entry                                → Rule 14
   ├─ Open offer / takeover entry                                 → Rule 15
   └─ Transfer out entry                                          → Rule 16
```

### Fallback

- If no route matches, invoke `console_eq_holdings`, `console_eq_tradebook`, `console_eq_holdings_breakdown`, or `console_eq_pnl` for additional context. If no root cause is found → escalate to human agent per A7.

---

## Section C: Rules

### Rule 1 — Verify External Entry Exists

1. Invoke this report with the appropriate `external_trade_type` per A3.
2. Entry found → share `trade_date`, `quantity`, `price`, `trade_type` using the client-facing label from A3.
3. No entry found → route to the applicable specific rule (Rule 4–16) based on share source.

---

### Rule 2 — Entry Added but Buy Average Not Updated

1. Check `pending_recalc` for this entry (per A2).
2. `pending_recalc` = true → entry is recorded and being processed; buy average will update within 24 hours (A4). Communicate the outcome to the client — do not mention the field name.
3. `pending_recalc` = false AND buy average still wrong in `console_eq_holdings`:
   a. Verify the entry details (price, qty, date) match the client's expected values.
   b. Entry details are correct but buy average remains wrong → escalate to human agent per A7. This is a backend recalculation failure.

---

### Rule 3 — Wrong Entry (Client Mistake)

1. Once a discrepancy entry is processed, it is locked and cannot be edited by the client (A5).
2. If entry details are wrong (client entered incorrect values) → entry is locked; backend correction needed.
3. Escalate to human agent per A7 — include the current (wrong) entry details from this tool and the correct values the client wants.

---

### Rule 4 — Gift Shares Entry Price

1. Invoke this report with `external_trade_type` = gift.
2. Entry exists:
   a. Check `exchange` field: `exchange` = "NSE" indicates the entry was system-generated by Zerodha.
   b. If client also has a separate discrepant entry for the same stock → escalate to human agent per A7 (possible duplicate entries causing wrong buy average).
   c. Entry price is the closing price on the transfer date — this is the default for all gift entries and is used for P&L tracking (A6).
3. Client wants actual acquisition cost instead of the default closing price → this requires a backend correction. Escalate to human agent per A7 with the requested price.

---

### Rule 5 — ESOP Shares

1. Invoke `console_eq_external_trades` with `external_trade_type` = esop.
2. Entry found → share entry details per Rule 1 using client-facing label "ESOP entry".
3. Client reports error when trying to add an ESOP discrepancy entry:
   - Verify whether the ISIN is currently listed on NSE or BSE.
   - ISIN not yet listed → entries cannot be added until the stock is active on the exchange (A6). Client should retry after listing.
4. Any other ESOP issue → escalate to human agent per A7.

---

### Rule 6 — Buyback Entry Verification

1. Invoke `console_eq_external_trades` with `external_trade_type` = buyback.
2. Entry found → `trade_type` will always be SELL. Share `trade_date`, `quantity`, `price`. Buyback proceeds are credited to the client's primary bank account directly by the company — not through Zerodha.
3. No entry found → invoke `ledger_report`; buyback entries are posted on the day the "Net settlement for buyback with settlement number" entry appears there, after the company processes and confirms acceptance (A4).
4. No entry AND client confirms acceptance was completed more than 5 trading days ago → escalate to human agent per A7.

---

### Rule 7 — IPO Allotment Entry

1. Invoke `console_eq_external_trades` with `external_trade_type` = ipo.
2. Entry found → share entry details per Rule 1 using client-facing label "IPO allotment". Note: `tradingsymbol` may be temporary until listing; `exchange` may show as UNKNOWN — both are expected. If buy average still shows N/A, `pending_recalc` may still be true; update within 24 hours (A4).
3. No entry found AND IPO listing was within the last 3 trading days → entries take up to 3 trading days to post (A4). Client should check back after 3 trading days from listing date.
4. No entry found AND IPO listing was more than 3 trading days ago → escalate to human agent per A7.

---

### Rule 8 — Internal Transfer Entry

1. Invoke `console_eq_external_trades` with `external_trade_type` = internal_transfer.
2. Entry found → share entry details per Rule 1 using client-facing label "account transfer" (transfer between client's own primary and secondary demat accounts).
3. No entry found → escalate to human agent per A7 to raise investigation.

---

### Rule 9 — No External Entries but Shares Show Discrepant

1. No entry exists and client has not added one → direct client to the self-resolution path (A5): Console → Portfolio → Holdings → View discrepancy → Add trade.
2. Shares credited via corporate action (convertible debenture, rearrangement, unclaimed shares) where the source is unclear → escalate to human agent per A7.

---

### Rule 10 — P&L Wrong Due to Missing External Entry

1. P&L is calculated using FIFO from all available trade entries (tradebook + external). Without a buy entry for the discrepant shares, the system cannot compute the correct cost of acquisition, resulting in incorrect P&L.
2. Direct client to the self-resolution path (A5): Console → Portfolio → Holdings → View discrepancy → Add trade. Once the entry is processed, P&L recalculates automatically.
3. Invoke `console_eq_pnl` to confirm the impact and verify once the entry is processed.

---

### Rule 11 — Devolved / Physical Settlement Entry

1. Invoke `console_eq_external_trades` with `external_trade_type` = devolved.
2. Entry found → `exchange` = PHY and `series` = AF are expected for devolved entries. Share `trade_date`, `quantity`, `price` using client-facing label "physical settlement".
3. No entry found → devolved entries are system-posted and should appear automatically. Escalate to human agent per A7 — include client ID, `tradingsymbol`, ISIN, and settlement date.

---

### Rule 12 — OFS Allotment Entry

1. Invoke `console_eq_external_trades` with `external_trade_type` = ofs.
2. Entry found → share entry details per Rule 1 using client-facing label "OFS allotment".
3. No entry found → OFS allotment entries are system-posted. Escalate to human agent per A7 — include client ID, `tradingsymbol`, ISIN, and OFS date.

---

### Rule 13 — Short Delivery Reversal Entry

1. Invoke `console_eq_external_trades` with `external_trade_type` = reversal.
2. Entry found → this is a system-posted reversal trade against a short delivery. Share `trade_date`, `quantity`, `price`, `trade_type` using client-facing label "short delivery reversal".
3. No entry found AND client reports an unresolved short delivery → escalate to human agent per A7 — include client ID, `tradingsymbol`, ISIN, and short delivery trade details. Cross-reference with `console_eq_holdings` protocol Rule 8 (Short delivery handling).

---

### Rule 14 — Rights Issue Allotment Entry

1. Invoke `console_eq_external_trades` with `external_trade_type` = rightsissue.
2. Entry found → share entry details per Rule 1 using client-facing label "rights allotment".
3. No entry found → rights issue entries are system-posted. Escalate to human agent per A7 — include client ID, `tradingsymbol`, ISIN, and rights issue record date.

---

### Rule 15 — Open Offer / Takeover Entry

1. Invoke `console_eq_external_trades` with `external_trade_type` = takeover.
2. Entry found → share `trade_date`, `quantity`, `price`, `trade_type` using client-facing label "open offer / takeover".
3. No entry found AND client confirms tendering was completed → escalate to human agent per A7 — include client ID, `tradingsymbol`, ISIN, and open offer / takeover details.

---

### Rule 16 — Transfer Out Entry

1. Invoke `console_eq_external_trades` with `external_trade_type` = transferout.
2. Entry found → share entry details per Rule 1 using client-facing label "transfer out". These entries are system-posted after the client provides transfer details via a ticket or call.
3. No entry found → escalate to human agent per A7.
