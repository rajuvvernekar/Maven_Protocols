# Step 1 — Paste-ready tag description edits

Apply at https://beta-supporttools.zerodha.net/app/maven-interaction-tag/view/list — open each tag and replace the **Description** field with the block in the "NEW" code box. The old text is shown above for reference.

11 of 18 tags need edits. The other 7 (`account-closure`, `account`, `holdings`, `margins`, `reports`, `charges`, `demat`) stay as-is.

---

## 1. `funds`

> **Old:** Customer is adding money to or withdrawing money from their trading account. Includes: payin not credited, payment method failures (UPI/netbanking/NEFT/IMPS/RTGS/cheque), emandate setup and issues, money sent to wrong account, withdrawal status, payout rejection, quarterly settlement payout.

**NEW:**

```
Customer is adding money to or withdrawing money from their trading account. Includes: payin not credited, payment method failures (UPI/netbanking/NEFT/IMPS/RTGS/cheque), emandate setup and issues for cashier auto-debit into the Kite trading balance, money sent to wrong account, withdrawal status, payout rejection, quarterly settlement payout. Excludes MF SIP/ZSIP mandates — those go to `investments`.
```

---

## 2. `investments`

> **Old:** Customer has a query about mutual funds, NPS, fixed deposits, or government securities on Coin. Includes: MF purchase/redemption, SIP/ZSIP setup and issues, mandate creation and failures, allotment status, NAV updates, MF holdings, unit transfers, MF-specific login issues, Coin platform errors.

**NEW:**

```
Customer has a query about mutual funds, NPS, fixed deposits, or government securities on Coin. Includes: MF purchase/redemption, SIP/ZSIP setup and issues, mandate creation and failures, allotment status, NAV updates, MF holdings, unit transfers, MF-specific login issues, and Coin app errors that block an MF action (mandate creation, SIP placement, redemption). Generic platform/app crashes that aren't MF-specific go to `platform`.
```

---

## 3. `orders`

> **Old:** Customer is trying to place, modify, or cancel an order, or asking about order status. Includes: all order types (limit/market/SL/AMO/GTT/basket/iceberg), order rejection reasons, execution status, partial fills, bids, stock SIP.

**NEW:**

```
Customer is trying to place, modify, or cancel an order, or asking about order status. Includes: all order types (limit/market/SL/AMO/GTT/basket/iceberg), order rejection reasons, execution status, partial fills, bids, stock SIP (Kite equity SIP only — MF SIP/ZSIP goes to `investments`).
```

---

## 4. `corporate-actions`

> **Old:** Customer has a question about a corporate action on a stock they hold. Includes: dividends (not credited, TDS), bonus shares, stock splits, mergers, demergers, buyback, takeover, rights issue, delisting, OFS.

**NEW:**

```
Customer has a question about a corporate action on a stock they hold, OR about an order placed against a corporate action (buyback application, rights bid). Includes: dividends (not credited, TDS), bonus shares, stock splits, mergers, demergers, buyback, takeover, rights issue, delisting, OFS. A "buyback order rejected" query is `corporate-actions`, not `orders`.
```

---

## 5. `platform`

> **Old:** Customer has a problem using the platform itself, or cannot log in. Includes: login/password/2FA/TOTP/OTP issues, chart display problems, marketwatch issues, data feed delays, bugs, feature requests, API/Kite Connect queries, app crashes, UI glitches, funds page field explanations.

**NEW:**

```
Customer has a problem using the platform itself or cannot log in. Includes: login/password/2FA/TOTP/OTP issues, chart display problems, marketwatch issues, data feed delays, bugs, feature requests, API/Kite Connect queries, app crashes, and UI glitches that aren't tied to a specific business action. If the query is about a payin/payout/mandate/QS/MF/holdings/order operation that happens to be on a screen, use the relevant business tag, not `platform`. Use `platform` as the last resort when nothing else fits.
```

---

## 6. `nri`

> **Old:** Customer has an NRI-specific query. Includes: NRI account opening (NRE-PIS, NRO-PIS, NRO-NON-PIS), resident to NRO conversion, NRI trade settlement, NRI-specific charges, NRI fund transfers.

**NEW:**

```
Customer holds an NRE/NRO/NRI account, OR the query is about an NRI-specific operation. Includes: NRI account opening (NRE-PIS, NRO-PIS, NRO-NON-PIS), resident to NRO conversion, NRI trade settlement, NRI-specific charges (including NRI AMC), NRI fund transfers, PIS, repatriation. Resident-Indian customers whose payment happens to be from an NRO bank are NOT `nri`.
```

---

## 7. `non-individual`

> **Old:** Customer has a query specific to non-individual accounts (company, HUF, LLP, partnership). Includes: non-individual account opening, modifications, pricing.

**NEW:**

```
The Zerodha account itself must be a company/HUF/LLP/Partnership/Trust. Includes: non-individual account opening, modifications, pricing for non-individual accounts. Individual-account customers asking generic questions are NOT `non-individual`, even if the question superficially resembles a corporate one.
```

---

## 8. `ipo`

> **Old:** Customer is applying for an IPO, checking bid/allotment status, or has IPO fund blocking issues. Includes: how to apply, UPI mandate, bid deletion, allotment status, funds not released, IPO shares not in holdings.

**NEW:**

```
Customer is applying for a mainboard or SME equity IPO, checking bid/allotment status, or has IPO fund blocking issues. Includes: how to apply, UPI mandate for IPO, bid deletion, allotment status, funds not released after IPO, IPO shares not in holdings. Rights issue, FPO, OFS go to `corporate-actions`. MF NFO and MF refund/allotment go to `investments`.
```

---

## 9. `compliance`

> **Old:** Customer received an exchange/regulatory notice or has a legal query. Includes: ASM/GSM/ESM surveillance, SEBI circulars, exchange complaints, arbitration, PMLA, phishing/unauthorized trades, police complaints.

**NEW:**

```
Customer received an external notice (exchange surveillance, SEBI circular, legal/arbitration) or reports fraud/unauthorised activity. Includes: ASM/GSM/ESM surveillance, SEBI circulars, exchange complaints, arbitration, PMLA, phishing, unauthorized trades, police complaints. KYC/ReKYC issues are `account`. Brokerage/charge disputes are `charges`.
```

---

## 10. `general`

> **Old:** Customer has a general inquiry not tied to a specific problem. Includes: market timings, holidays, how futures/options work, tax questions, instrument info (liquidbees, SGB, US stocks), gift stocks, third-party products (Streak/Sensibull/Smallcase), Varsity, LAS queries.

**NEW:**

```
Customer has a general inquiry not tied to a specific problem and not covered by any other tag. Includes: market timings, holidays, how futures/options work, tax questions, instrument info (liquidbees, SGB, US stocks), gift stocks, third-party products (Streak/Sensibull/Smallcase), Varsity, LAS queries. Use `general` only when the query genuinely doesn't map to any other tag — do not use as a default.
```

---

## 11. `settlement`

> **Old:** Customer has a question about trade settlement. Includes: T+1/T+2 cycle, BTST, short delivery, auction trades, physical delivery, settlement holidays, sale credit not received.

**NEW:**

```
Customer has a question about exchange settlement. Includes: T+1/T+2 cycle, BTST, short delivery, auction trades, physical delivery, settlement holidays, sale credit not received. Quarterly settlement (QS) payout goes to `funds`. Payment-method failures (UPI/netbanking/IMPS/etc.) go to `funds`.
```

---

## Tags that stay unchanged (7)

`account-closure`, `account`, `holdings`, `margins`, `reports`, `charges`, `demat` — bad-rate ≤11% in the data, descriptions are clean, no edits needed.

## After applying

Watch tag-prediction accuracy for the 4 worst-rated tags over the next 24–48 hours:
- `nri` (was 32.4% bad)
- `non-individual` (was 36.8% bad)
- `ipo` (was 31.7% bad)
- `compliance` (was 24.4% bad)

Plus the over-applied catch-alls:
- `platform` (was 16.9% bad)
- `general` (was 16.1% bad)
- `settlement` (was 11.3% bad)

If those drop, Step 1 worked. Then we move to Step 2 (utility tools `always_include` audit).
