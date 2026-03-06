# corporate_action_orders

## Description

WHEN TO USE:

- Client asks about the status of a buyback, rights issue, or open offer order they placed
- Client asks whether their buyback/rights/open offer application was accepted or rejected
- Agent needs to verify if a corporate action order exists for a client
- Client questions allotment price or investment amount for a CA order
- Client asks about buyback proceeds or when shares will be debited/credited
- Client reports applying for a CA but order not showing
- Client asks about rights issue allotment status or payment details
- Client questions why CA order was rejected

TRIGGER KEYWORDS: "buyback order", "buyback status", "rights issue order", "rights issue applied", "open offer order", "tender status", "buyback applied", "buyback accepted", "buyback rejected", "allotment status", "CA order", "corporate action order", "rights allotment", "buyback proceeds", "tender offer"

## Protocol

# CORPORATE ACTION ORDERS PROTOCOL

## PROTOCOL

<knowledge_base>

<facts>
- This tool shows client orders placed for buybacks, rights issues, and open offers
- Required input: Client ID only — returns all CA orders for the client
- Status values: Placed (submitted), Processed (accepted by company/exchange), Rejected (not accepted)
- Allotment price defaults to 0.0 if not yet allotted — does not mean rejected
- Buyback: client tenders shares → if accepted, shares debited and proceeds credited to bank account by the company (not Zerodha)
- Buyback proceeds timeline: depends on company — typically 5-15 working days after acceptance
- Buyback accepted shares removed from holdings; remaining shares (if partial acceptance) stay in holdings
- Rights issue: client applies and pays → allotment credited to demat; unallotted amount refunded by registrar
- Rights issue shares may show as discrepant initially until listing — resolved after listing date
- Open offer: similar to buyback — client tenders, company accepts/rejects
- trade_type field identifies the CA type: Buyback, Rights Issue, Open Offer
- Buyback tax treatment changed from 1 Oct 2024 — buyback now treated as capital gain for shareholder (previously dividend distribution tax on company). Tax P&L may need manual editing by client for recent buybacks.
</facts>

<field_usage>
  <share>creation | trading_symbol | isin | price | quantity | status | allotment_price | investment_amount | trade_type</share>
  <banned>client_id | modified</banned>
</field_usage>

<status_values>
  <placed>Order submitted — pending processing by company/exchange</placed>
  <processed>Order accepted and executed — shares debited (buyback/open offer) or allotted (rights)</processed>
  <rejected>Order not accepted — shares returned, no debit</rejected>
</status_values>

<cross_reference>
  <console_eq_holdings>Check if tendered shares debited from holdings (buyback) or allotted shares credited (rights)</console_eq_holdings>
  <console_eq_external_trades>Buyback exit entries and rights issue allotment entries appear here</console_eq_external_trades>
  <console_eq_pnl>Buyback P&L reflected here — may need manual Tax P&L editing for post-Oct 2024 buybacks</console_eq_pnl>
</cross_reference>

<escalation_triggers>
  <order_missing>Client applied but no CA order record found in this tool</order_missing>
  <status_stuck>Order status remains "Placed" beyond the CA closure date + 5 working days</status_stuck>
  <wrong_allotment_price>Allotment price recorded differs from official CA circular price</wrong_allotment_price>
  <shares_not_debited>Buyback shows Processed but shares still in holdings</shares_not_debited>
  <rights_discrepancy>Rights allotment credited but showing as discrepant beyond listing date + 3 days</rights_discrepancy>
</escalation_triggers>

</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
**NEVER expose:** `client_id`, `modified`
**ALWAYS share when relevant:** `creation`, `trading_symbol`, `isin`, `price`, `quantity`, `status`, `allotment_price`, `investment_amount`, `trade_type`

### Rule 1: Order Status Verification
**if:** Client asks about their buyback/rights/open offer order status
**then:** Look up by Client ID and find matching trading_symbol.

"Your [trade_type] order for [trading_symbol]: [quantity] shares at ₹[price] per share, placed on [creation]. Current status: [status]."

- If status = Placed → "Your order has been submitted and is pending processing by the company. Processing timelines depend on the corporate action schedule."
- If status = Processed → "Your order has been accepted and processed." (See Rules 2-4 for type-specific details)
- If status = Rejected → "Your order was not accepted. Your shares have not been debited and no further action is needed from your side."

### Rule 2: Buyback Order — Processed
**if:** trade_type = Buyback AND status = Processed
**then:** "Your buyback tender of [quantity] shares of [trading_symbol] at ₹[allotment_price > 0 ? allotment_price : price] has been accepted. The tendered shares have been debited from your holdings. Buyback proceeds will be credited to your primary bank account by the company — this typically takes 5-15 working days after acceptance.

Note: If only part of your tendered shares were accepted (partial acceptance), the remaining shares will continue in your holdings."

**if:** Client says shares still showing in holdings despite status = Processed → check `console_eq_holdings`. If shares still there → escalate.

### Rule 3: Rights Issue — Not Available on This Tool
**if:** Client asks about rights issue application status
**then:** "Rights issue applications are submitted directly through your bank's ASBA facility or the company's registrar — they are not tracked in this tool. Please check with your bank for the ASBA application status, or with the company's RTA (Registrar and Transfer Agent) for allotment status."

Do NOT attempt to look up rights issue orders in this tool.

### Rule 4: Open Offer Order — Processed
**if:** trade_type = Open Offer AND status = Processed
**then:** "Your open offer tender of [quantity] shares of [trading_symbol] at ₹[allotment_price > 0 ? allotment_price : price] has been accepted. The tendered shares will be debited and proceeds credited to your bank account by the acquirer."

### Rule 5: Allotment Price = 0
**if:** allotment_price = 0 AND status = Placed or Processed
**then:** "The allotment price has not been updated yet. This does not mean your order was rejected — it will be updated once the company confirms the final allotment details."

Do NOT tell the client the allotment price is ₹0.

### Rule 6: Order Not Found
**if:** Client says they applied for a CA but no record found in this tool
**then:** "I don't see a [buyback/rights issue/open offer] order for [trading_symbol] in your account. This could mean:
- The application was not submitted successfully
- The application was placed from a different platform or process

Could you confirm how and when you placed the application? If you have a confirmation screenshot, that would help us investigate further." If client confirms they applied → escalate.

### Rule 7: Buyback Tax Treatment (Post Oct 2024)
**if:** Client asks about buyback tax treatment or buyback not showing correctly in Tax P&L
**then:** "From 1st October 2024, buyback proceeds are taxed as capital gains in the hands of the shareholder (previously the company paid dividend distribution tax). Your Tax P&L may need manual editing for buybacks processed after this date — you can edit the Tax P&L on Console (Reports → Tax P&L → Edit) to reflect the correct capital loss/gain."

If Tax P&L shows profit instead of expected loss for buyback → known issue for recent buybacks. Client can edit Tax P&L manually.

### Rule 8: Escalation Criteria
**if:** Any of the following:
- Client applied but no order record found after confirming application (Rule 6)
- Status stuck at "Placed" beyond CA closure + 5 working days (KB trigger)
- Allotment price differs from official circular price (KB trigger)
- Buyback Processed but shares not debited from holdings (Rule 2)
- Rights allotment discrepant beyond listing date + 3 days (KB trigger)
**then:** Escalate with: client ID, trading_symbol, trade_type, status, and specific issue.
