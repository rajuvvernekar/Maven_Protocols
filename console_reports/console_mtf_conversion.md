# console_mtf_conversion

## Description

WHEN TO USE:

- Client asks about the status of their MTF-to-CNC conversion request
- Agent needs to verify if a conversion was actually processed or only appears processed
- Client reports conversion shows "Processed" but shares still under MTF
- Client asks about conversion cost or amount required to convert
- Client questions why conversion failed or was not processed
- Client asks about partial conversion (some qty converted, some not)
- Agent needs to check conversion history for a specific security

TRIGGER KEYWORDS: "MTF conversion", "MTF to CNC", "MTF to delivery", "convert MTF", "conversion status", "conversion processed", "conversion failed", "conversion request", "conversion cost", "convert to delivery"

## Protocol

# CONSOLE MTF CONVERSION PROTOCOL

## PROTOCOL

<knowledge_base>

<facts>
- This tool tracks MTF-to-CNC conversion requests — requested qty, converted qty, status, and remarks
- Required input: Client ID — returns all conversion requests
- Status values: Processed (system attempted conversion), Pending (awaiting processing)
- CRITICAL: status = Processed does NOT always mean conversion succeeded — check converted_quantity
- If converted_quantity = 0 and status = Processed → conversion FAILED due to insufficient margin (known display issue)
- Conversion requires full funded amount available as free cash in account — partial funds = full failure
- remarks field contains system-generated details: qty converted, trade date, total cost of conversion
- T+1 restriction: shares bought today under MTF cannot be converted until next trading day
- Conversions on ex-date of corporate actions are NOT processed — must retry after ex-date
- After successful conversion: shares move from MTF holdings to regular equity holdings; MTF interest stops on converted qty
- If stock removed from MTF approved list: existing MTF position NOT auto-converted — client must convert manually or continue holding
- Conversion cost = funded amount for those shares (Zerodha's contribution that client must now pay)
- Short-delivered MTF position auto-converted to CNC — interest should stop; if not, escalate for reversal
</facts>

<field_usage>
  <share>status | isin | trade_date | request_quantity | converted_quantity | remarks</share>
  <banned>client_id</banned>
</field_usage>

<status_values>
  <processed>System attempted conversion — check converted_quantity to confirm success</processed>
  <pending>Request awaiting processing — typically processed same day or next morning</pending>
</status_values>

<cross_reference>
  <console_mtf_holdings>Verify if shares still under MTF after conversion. Contains MTF-specific rules, interest, square-off details.</console_mtf_holdings>
  <console_eq_holdings>Verify if converted shares now appear in regular equity holdings.</console_eq_holdings>
</cross_reference>

<escalation_triggers>
  <display_bug>Status = Processed but converted_quantity = 0 AND client has re-tried with sufficient funds and still fails</display_bug>
  <shares_stuck>Conversion Processed with converted_quantity > 0 but shares still in MTF after 2+ trading days</shares_stuck>
  <interest_not_stopped>Conversion successful but MTF interest still being charged on converted qty</interest_not_stopped>
  <short_delivery_interest>Short-delivered MTF auto-converted to CNC but interest not reversed</short_delivery_interest>
</escalation_triggers>

</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
**NEVER expose:** `client_id`
**ALWAYS share when relevant:** `status`, `isin`, `trade_date`, `request_quantity`, `converted_quantity`, `remarks`

**CRITICAL display rule:** Never tell client the status field value alone — always cross-check with converted_quantity before communicating outcome.

### Rule 1: Conversion Status Verification
**if:** Client asks about conversion request status
**then:** Look up by Client ID, find matching ISIN/tradingsymbol.

Check converted_quantity vs request_quantity:
- If converted_quantity = request_quantity → "Your conversion of [request_quantity] shares has been successfully processed. These shares have moved from MTF to regular delivery holdings."
- If converted_quantity = 0 AND status = Processed → "Your conversion request was not processed due to insufficient funds in your account. The status shows 'Processed' but the actual conversion did not go through — this is a display issue. Please add the required funds (the funded amount for these shares) and place a new conversion request."
- If converted_quantity < request_quantity (partial) → "Only [converted_quantity] of your requested [request_quantity] shares were converted. The remaining shares are still under MTF. This may be due to insufficient funds for the full conversion."
- If status = Pending → "Your conversion request is pending processing. It will typically be processed by the next trading day."

### Rule 2: Conversion Cost Inquiry
**if:** Client asks how much is needed to convert MTF to delivery
**then:** "To convert your MTF position to regular delivery, you need to have the funded amount available as free cash in your account. The funded amount is the portion that Zerodha contributed when you purchased the shares under MTF.

You can check the funded amount in the remarks field of your conversion request, or calculate it as: total purchase value minus the initial margin you paid."

**if:** Client asks about MTM already paid → "The MTM (Mark-to-Market) margin you've paid covers daily price fluctuations. The conversion cost is the original funded amount, not the MTM."

### Rule 3: Conversion Failed — Common Reasons
**if:** Conversion did not go through (converted_quantity = 0)
**then:** Diagnose:
- Insufficient funds → "Your account did not have sufficient free cash to cover the funded amount of ₹[from remarks]. Please add the required funds and retry."
- T+1 → "Shares purchased today under MTF can only be converted from the next trading day."
- Ex-date → "Conversions on the ex-date of a corporate action are not processed. Please retry after the ex-date."
- If none of the above → escalate.

### Rule 4: Shares Still in MTF After Successful Conversion
**if:** converted_quantity > 0 but client says shares still appear under MTF
**then:** Check `console_mtf_holdings` for the stock.
- If stock still in MTF holdings → check if conversion was within last 1 trading day (may take overnight to reflect).
- If 2+ trading days since conversion and still in MTF → escalate as display bug or processing issue.

Also check `console_eq_holdings` — converted shares should now appear there.

### Rule 5: Interest After Conversion
**if:** Client says MTF interest still being charged after conversion
**then:** "After a successful conversion, MTF interest should stop accruing on the converted quantity from the next day. If interest is still being charged on the converted shares, we'll investigate and reverse any incorrect charges."

Verify conversion was successful (converted_quantity > 0). If yes and interest still charged → escalate.

### Rule 6: Stock Removed from MTF List — Conversion Not Required
**if:** Client asks if they must convert because stock was removed from MTF approved list
**then:** "If a stock is removed from the MTF approved list, your existing MTF position is NOT automatically converted or squared off. You can continue to hold the position under MTF. However, if you wish to convert to regular delivery to avoid ongoing MTF interest, you can place a conversion request provided you have sufficient funds."

### Rule 7: Remarks Field Interpretation
**if:** Agent needs to share conversion details
**then:** The `remarks` field contains system-generated text with: quantity converted, trade date, and total cost of conversion. Parse and share in client-friendly language:

"Your conversion details: [converted_quantity] shares converted from your MTF purchase on [trade_date]. The total conversion cost was ₹[cost from remarks]."

### Rule 8: Escalation Criteria
**if:** Any of the following:
- Converted_quantity > 0 but shares still in MTF after 2+ trading days (Rule 4)
- Conversion repeatedly fails despite sufficient funds (Rule 3)
- MTF interest charged on successfully converted shares (Rule 5)
- Short-delivered position auto-converted but interest not reversed (KB trigger)
**then:** Escalate with: client ID, tradingsymbol/ISIN, conversion date, request_quantity, converted_quantity, and specific issue.
