# **Zerodha Support Ticket Taxonomy**

## **Design**

**18 tags.** Each tag is a domain — "what is this ticket about?" Nothing else. No product axis (Kite/Coin/Console comes from metadata). No sub-tags. Extracted metadata handles all granularity.

**What the tag answers:** "What kind of problem is happening, and is it happening more than usual?"

**What the tag does NOT encode:** Platform, payment method, segment, exchange, account type, sentiment, language, followup status. These are auto-extracted fields.

---

**Metabase dashboard:** 18 tiles. Each shows volume trend. Click a tile → see summaries, filter by metadata. Anomaly alerts trigger on volume deviation.

---

## **The 18 Tags**

| \# | Tag | % of tickets | What it covers |
| ----- | ----- | ----- | ----- |
| 1 | `account-closure` | 18.9% | Close account (full/demat/commodity), deactivation, cum-transfer |
| 2 | `account` | 15.7% | Account opening, KYC modification, personal detail changes, bank changes, nominee, segment enable/disable, dormant reactivation, ReKYC, POA/DDPI |
| 3 | `investments` | 10.5% | Mutual fund purchase/redemption/SIP/ZSIP/mandate, NPS, FD, Govt securities, Coin login, MF allotment, units transfer, MF reports |
| 4 | `funds` | 9.2% | Adding money (UPI/netbanking/NEFT/IMPS/RTGS/cheque/mandate), withdrawals, money not credited, wrong account, payout status/rejection, quarterly settlement |
| 5 | `platform` | 6.2% | Login/password/2FA/TOTP/OTP, charts, marketwatch, data feeds, UI bugs, feature requests, API/Kite Connect, downtime, funds page queries |
| 6 | `margins` | 5.1% | Margin requirements, pledge/unpledge, RMS auto-squareoff, margin penalties, MTF, collateral |
| 7 | `orders` | 5.0% | Order placement/types/modification/cancellation, GTT, rejection, execution status, bids, stock SIP |
| 8 | `holdings` | 3.7% | Holdings/positions display, buy average, discrepancy, P\&L display, conversions (MIS↔CNC), portfolio |
| 9 | `corporate-actions` | 3.2% | Dividends, bonus, stock splits, mergers, demergers, buyback, takeover, rights issue, delisting |
| 10 | `ipo` | 3.0% | IPO application, bid status, allotment, UPI mandate, fund blocking, IPO holdings |
| 11 | `reports` | 2.5% | Contract notes, P\&L reports, tax P\&L, ledger, tradebook, margin statement, AGS |
| 12 | `general` | 2.4% | Market timings, holidays, how trading works, tax queries, instrument info, gift stocks, third-party products (Streak/Sensibull/Smallcase), Varsity, Zerodha Capital/LAS |
| 13 | `demat` | 2.4% | CDSL/NSDL auth (TPIN, OTP, eASI), stock transfers in/out, DIS, freeze/unfreeze, transmission, demat statements |
| 14 | `settlement` | 1.8% | T+1/T+2 cycle, BTST, short delivery, auction, physical delivery, settlement holiday |
| 15 | `compliance` | 1.5% | Exchange notices, surveillance (ASM/GSM), SEBI circulars, legal/arbitration, PMLA, phishing, unauthorized trades |
| 16 | `nri` | 1.3% | NRI account opening/closure, NRE/NRO mapping, PIS, trade settlement, NRI-specific charges |
| 17 | `charges` | 1.3% | Brokerage, STT, stamp duty, DP charges, AMC, transaction charges, GST, charge reversals |
| 18 | `non-individual` | 0.5% | Company/HUF/LLP/Partnership account opening, modification, charges |

**Total coverage: 94.3%** of tickets. Remaining 5.7% are internal tracking, partner queue, and business queries — excluded from this taxonomy (see below).

---

## **Tag Definitions (for LLM classification prompt)**

These are the exact descriptions the LLM/ML model uses to classify:

```
account-closure: Customer wants to close, deactivate, or shut down their trading
account, demat account, or any part of their account. Includes full closure,
demat-only closure, cum-transfer, commodity closure, temporary deactivation.

account: Customer wants to open a new account, modify existing account details,
reactivate a dormant account, or complete KYC. Includes: signup issues, document
submission, activation, personal detail changes (name, DOB, email, mobile, address,
bank, nominee), segment enable/disable, ReKYC, POA/DDPI, income proof.

investments: Customer has a query about mutual funds, NPS, fixed deposits, or
government securities on Coin. Includes: MF purchase/redemption, SIP/ZSIP setup
and issues, mandate creation and failures, allotment status, NAV updates, MF
holdings, unit transfers, MF-specific login issues, Coin platform errors.

funds: Customer is adding money to or withdrawing money from their trading account.
Includes: payin not credited, payment method failures (UPI/netbanking/NEFT/IMPS/
RTGS/cheque), emandate setup and issues, money sent to wrong account, withdrawal
status, payout rejection, quarterly settlement payout.

platform: Customer has a problem using the platform itself, or can't log in.
Includes: login/password/2FA/TOTP/OTP issues, chart display problems, marketwatch
issues, data feed delays, bugs, feature requests, API/Kite Connect queries, app
crashes, UI glitches, funds page field explanations.

margins: Customer has a question about margin requirements, pledging, or got auto-
squared off. Includes: margin requirement queries, how to pledge/unpledge, margin
penalties, peak margin, RMS auto-squareoff, MTF, intraday leverage, collateral.

orders: Customer is trying to place, modify, or cancel an order, or asking about
order status. Includes: all order types (limit/market/SL/AMO/GTT/basket/iceberg),
order rejection reasons, execution status, partial fills, bids, stock SIP.

holdings: Customer has a question about their holdings or positions display.
Includes: buy average wrong, holdings discrepancy, positions P&L, investment value,
missing holdings, position conversion (MIS↔CNC), portfolio analytics.

corporate-actions: Customer has a question about a corporate action on a stock they
hold. Includes: dividends (not credited, TDS), bonus shares, stock splits, mergers,
demergers, buyback, takeover, rights issue, delisting, OFS.

ipo: Customer is applying for an IPO, checking bid/allotment status, or has IPO
fund blocking issues. Includes: how to apply, UPI mandate, bid deletion, allotment
status, funds not released, IPO shares not in holdings.

reports: Customer wants to access, download, or understand a report or statement.
Includes: contract notes, P&L report, tax P&L, ledger, tradebook, margin statement,
reconciliation, annual global statement.

general: Customer has a general inquiry not tied to a specific problem. Includes:
market timings, holidays, how futures/options work, tax questions, instrument info
(liquidbees, SGB, US stocks), gift stocks, third-party products, Varsity, LAS queries.

demat: Customer has a depository-related query. Includes: CDSL/NSDL authentication
(TPIN, OTP, eASI), stock transfer in/out, DIS slips, freeze/unfreeze, transmission,
demat statements, DP ID queries.

settlement: Customer has a question about trade settlement. Includes: T+1/T+2 cycle,
BTST, short delivery, auction trades, physical delivery, settlement holidays, sale
credit not received.

compliance: Customer received an exchange/regulatory notice or has a legal query.
Includes: ASM/GSM/ESM surveillance, SEBI circulars, exchange complaints, arbitration,
PMLA, phishing/unauthorized trades, police complaints.

nri: Customer has an NRI-specific query. Includes: NRI account opening (NRE-PIS,
NRO-PIS, NRO-NON-PIS), resident↔NRO conversion, NRI trade settlement, NRI-specific
charges, NRI fund transfers.

charges: Customer is asking about fees or charges. Includes: brokerage, STT, stamp
duty, DP charges, AMC, exchange transaction charges, GST, payment gateway charges,
call-and-trade charges, charge reversals.

non-individual: Customer has a query specific to non-individual accounts (company,
HUF, LLP, partnership). Includes: non-individual account opening, modifications,
pricing.
```

---

---

## **Excluded from Taxonomy**

These are NOT customer issue tags. They either belong in separate systems or are auto-detected.

| Category | What | How handled |
| ----- | ----- | ----- |
| Internal tracking | Followup, call transfer, call drop, irate, spam, third-party caller, language flags, duplicate, appreciation | Auto-detected metadata fields \+ ticket system states |
| Partner | AP onboarding, referral mapping, rewards, lead queries | Separate queue in LibreDesk |
| Business | HR/resume, Rainmatter, social media | Separate queue |
| Orbis | Migration tickets (temporary, trending to zero) | Separate queue, sunset when done |
| Escalation | Fraud, suicide threats, account block/unblock | Priority flags, not tags. Applied alongside any tag. |

---

## **Anomaly Detection Examples**

What each tag spike means and what to investigate:

| Tag spiking | Likely cause | Investigate |
| ----- | ----- | ----- |
| `account-closure` | Market downturn, fee increase, competitor promo | Check if new or from long-dormant accounts |
| `account` | ReKYC deadline, SEBI regulation change, bank merger (IFSC changes) | Filter summaries for keyword clusters |
| `investments` | BSEStARMF downtime, AMC-side rejection, SIP trigger failure | Filter by summary keywords: "payment failed" vs "order rejected" vs "SIP not triggered" |
| `funds` | Payment gateway down, bank-side outage, UPI infrastructure issue | Filter by `payment_method` metadata |
| `platform` | Bad deploy, exchange feed issue, CDSL TPIN system down | Filter by `platform` metadata to isolate Kite vs Console vs Coin |
| `margins` | Volatile market day, margin rule change, pledge system issue | Check if correlated with market movement |
| `orders` | Exchange rule change, RMS policy update, circuit limit changes | Filter summaries for "rejected" vs "stuck" vs "wrong price" |
| `ipo` | During IPO window \= normal. Outside \= stuck mandate or delayed refund | Check if concentrated on specific IPO |
| `compliance` | Exchange adding stocks to ASM/GSM, new SEBI circular | Usually resolves once circular is communicated |

---

## **Migration Rough idea can ignore**

### **Old → New mapping**

Every one of the existing 1,293 tags maps to exactly one of these 18 tags. The mapping follows this logic:

| Old tag prefix | New tag |
| ----- | ----- |
| `Account-closure-*`, `Account-closure-*` | `account-closure` |
| `Account-opening-*`, `Account-kyc-*`, `Account-operation-*`, `Console-modification-*`, `account-rekyc-*` | `account` |
| `Coin-MF-*`, `Coin-FD-*`, `Coin-NPS-*`, `Coin-Government*` | `investments` |
| `Funds-payin-*`, `Funds-payout-*`, `fund-payin-*`, `funds-payout-*`, `Funds-banktransfer-*` | `funds` |
| `Kite-login-*`, `Kite-charts-*`, `Kite-marketwatch-*`, `Kite-feeds-*`, `Kite-Pendingfix-*`, `Kite-connect-*`, `Kite-API-*`, `Kite-funds-page-*`, `Kite-feature-*`, `Kite-DNS-*`, `Kite-maintenance*`, `Kite-Demo*`, `Console-Intermittent-*`, `Console-how-to-login` | `platform` |
| `Trading-Margin-*`, `Trading-margin-*`, `Trading-RMS-*`, `trading-rms-*`, `Console-MTF-*`, `Kite-MTF-*` | `margins` |
| `Kite-orders-*`, `Kite-Order-*`, `kite-orders-*`, `kite-bids*` | `orders` |
| `Kite-holding*`, `Kite-position*`, `Console-holdings-*`, `Console-portfolio-*` | `holdings` |
| `Corporate-action-*`, `corporate-action-*` | `corporate-actions` |
| `IPO-*`, `ipo-*` | `ipo` |
| `Console-reports-*`, `Console-Reports-*`, `console-reports-*` | `reports` |
| `Trading-common-*`, `Products-*`, `Console-Gift-*`, `Console-gift-*`, `Zerodha-Capital-*`, `Zerodha-capital-*` | `general` |
| `Demat-*`, `demat-*` | `demat` |
| `Trading-settlement-*` | `settlement` |
| `Trading-compliance-*`, `Trading-Compliance-*`, `compliance-*`, `trading-compliance-*` | `compliance` |
| `NRI-*`, `nri-*` | `nri` |
| `Pricing-*`, `pricing-*` | `charges` |
| `Non-individual-*` | `non-individual` |
| `Tracking-*`, `tracking-*`, `Escalation-*`, `escalation-*`, `Partner-*`, `partner-*`, `Business-*`, `Orbis-*` | *(excluded from taxonomy)* |

### **Rewrite script**

The non-LLM ML model being trained on the CSV needs a new column. For each row in `tag_queries_final.csv`:

1. Map old tag → new tag using the prefix rules above  
2. Generate the row: `old_tag, new_tag, query`  
3. Train the ML model on `(query → new_tag)`

### **For the LLM auto-tagger**

The classification prompt is the tag definitions above. The LLM reads the customer message, picks one of 18 tags, writes a summary, and extracts metadata. Single API call, structured output.

---

## **Summary**

```
Before:  1,293 tags  →  no one looks at the data, too noisy to be useful
After:       18 tags  →  18 Metabase tiles, instant anomaly detection

Granularity:
  Tag        = which Metabase tile lights up (18 options)
  Summary    = what you read when you click the tile (free text)
  Metadata   = how you filter and slice (structured fields)

Classification accuracy:
  18-way classification → 95%+ accuracy (LLM or ML)
  1,293-way classification → unreliable (current state)
```

In future when we get info from meta data

## **Architecture**

```
Ticket comes in
    │
    ├── LLM classifies → 1 of 18 tags
    │
    ├── LLM generates → free-text summary (1-2 lines)
    │     e.g. "Customer's SIP order rejected for 3 MF schemes.
    │           Payment was debited but order shows failed."
    │
    ├── LLM extracts → structured metadata
    │     platform: Coin App
    │     payment_method: Mandate
    │     segment: MF
    │     sentiment: frustrated
    │
    └── System fills → account_type, is_followup, source_url
```

## 

## 

## **Auto-Extracted Metadata (not tags) Rough idea can ignore**

The same LLM that picks the tag also extracts these structured fields from the customer message:

| Field | Type | Values | How extracted |
| ----- | ----- | ----- | ----- |
| `platform` | enum | `kite-web`, `kite-app`, `console`, `coin-web`, `coin-app`, `api`, `unknown` | Source URL / user-agent (system) |
| `segment` | enum | `equity`, `fno`, `mcx`, `cds`, `mf`, `unknown` | LLM extracts from message |
| `payment_method` | enum | `upi`, `netbanking`, `neft`, `imps`, `rtgs`, `cheque`, `mandate`, `gateway`, `unknown` | LLM extracts from message |
| `account_type` | enum | `individual`, `joint`, `minor`, `nri-nre`, `nri-nro`, `huf`, `company`, `llp`, `partnership`, `trust` | CRM lookup |
| `sentiment` | enum | `calm`, `frustrated`, `angry`, `appreciative` | LLM detects from tone |
| `language` | enum | `english`, `hindi`, `hinglish`, `other` | LLM detects |
| `is_followup` | bool | `true`, `false` | Ticket system (reply chain) |
| `summary` | text | 1-2 line free-text summary | LLM generates |

**The `summary` field is the key to granularity.** When `funds` spikes on the dashboard, you click into it, and the summaries tell you: "12 tickets in last hour about UPI payin not credited after bank debit." That's your anomaly signal. You don't need a `funds-payin-upi-not-credited` tag for this — the summary does the work.

